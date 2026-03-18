"""
Quantum ML Predictor — PennyLane QML Circuit (v3)
====================================================
Per-target variational quantum circuits for predicting pesticide
environmental fate properties (DegT50 and Koc) from molecular descriptors.

v3 Upgrades (Phase 5a):
  - Per-target circuits: 6-qubit for DegT50, 12-qubit for Koc
  - Early stopping with patience to prevent overtraining
  - Reduced DegT50 overfitting (params/data: 2.7 → 0.87)

v2 Upgrades:
  - 12 qubits (was 6) → larger Hilbert space
  - 8 variational layers (was 4) → more expressivity
  - Gradient-based Adam optimizer (was stochastic perturbation)
  - Improved feature encoding with IQP-style entangling
  - Log-space prediction for better dynamic range coverage

Architecture:
  - DegT50: 6 qubits × 5 layers = 97 params (regularized)
  - Koc:   12 qubits × 8 layers = 301 params (expressive)
  - IQP-style feature-entangled encoding (ZZ interactions)
  - Measurement: PauliZ expectations → linear readout
"""

import numpy as np
import pennylane as qml
from pennylane import numpy as pnp

# ── Circuit configurations ──────────────────────────────────────────
# DegT50: smaller circuit to reduce overfitting (97 params / 111 samples = 0.87)
N_QUBITS_DEG = 6
N_LAYERS_DEG = 5
dev_deg = qml.device("default.qubit", wires=N_QUBITS_DEG)

# Koc: larger circuit — already showing R²=0.412, benefits from expressivity
N_QUBITS_KOC = 12
N_LAYERS_KOC = 8
dev_koc = qml.device("default.qubit", wires=N_QUBITS_KOC)

# Backward-compat aliases (used by cache system, server.py references)
N_QUBITS = N_QUBITS_KOC
N_LAYERS = N_LAYERS_KOC

EARLY_STOP_PATIENCE = 10  # stop if no improvement for this many epochs


# ── Feature engineering ─────────────────────────────────────────────
FEATURE_NAMES = [
    "mw", "logP", "n_heavy", "hbd", "hba",
    "n_rings", "n_rotatable", "solubility_log",
    "vapor_pressure_log", "freundlich_n",
    "tpsa_approx", "aromatic_ring_frac",
    # Phase 4a: microbial degradation proxies
    "n_hydrolyzable", "n_halogens", "bioaccessibility",
    # Phase 4b: blind-spot corrections
    "charge_state", "conjugated_pi_size",
    # Phase 5c: DegT50-targeted features
    "heteroatom_ratio", "sp3_fraction",
    "henry_volatility", "oxidation_susceptibility",
]
N_FEATURES = len(FEATURE_NAMES)  # 21


def extract_features(substance):
    """
    Extract and normalize 17 molecular descriptor features.
    Returns PennyLane-compatible numpy array of length 17.
    Includes microbial degradation proxies (Phase 4a) and
    blind-spot corrections (Phase 4b: charge_state, conjugated_pi_size).
    """
    sol = substance.get("solubility", 1.0)
    vp  = substance.get("vapor_pressure", 1e-6)
    n_heavy = substance.get("n_heavy", 18)
    hbd = substance.get("hbd", 1)
    hba = substance.get("hba", 4)
    n_rings = substance.get("n_rings", 1)
    koc = substance.get("koc", 100)

    # Approximate TPSA from HBD/HBA (Ertl method approximation)
    tpsa_approx = hbd * 23.0 + hba * 9.23
    # Aromatic ring fraction
    aromatic_frac = n_rings / max(n_heavy, 1) * 10.0

    # ── Phase 4: Microbial degradation proxies ──
    # 1. Count hydrolyzable bonds (esters, amides, carbamates) from SMILES
    n_hydrolyzable = 0
    smiles = substance.get("smiles", "")
    if smiles:
        try:
            from rdkit import Chem
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                # SMARTS patterns for enzymatically-cleavable bonds
                patterns = [
                    Chem.MolFromSmarts("[C](=O)[O][C,c]"),    # ester
                    Chem.MolFromSmarts("[C](=O)[NH]"),         # amide
                    Chem.MolFromSmarts("[NH]C(=O)O"),          # carbamate
                    Chem.MolFromSmarts("[P](=O)(O)(O)"),       # phosphoester
                    Chem.MolFromSmarts("[C](=O)S"),            # thioester
                ]
                for pat in patterns:
                    if pat:
                        n_hydrolyzable += len(mol.GetSubstructMatches(pat))
        except Exception:
            pass

    # 2. Halogen count (resistance to biodegradation)
    n_halogens = 0
    if smiles:
        try:
            from rdkit import Chem
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                for atom in mol.GetAtoms():
                    if atom.GetSymbol() in ('Cl', 'Br', 'F', 'I'):
                        n_halogens += 1
        except Exception:
            pass

    # 3. Bioaccessibility: log10(solubility / koc) — microbial availability
    bioaccessibility = np.log10(max(sol, 1e-6) / max(koc, 1))

    # ── Phase 4b: Blind-spot corrections ──
    # 4. Charge state — pKa-based cationic correction
    #    Permanently charged molecules (Diquat, Paraquat) bind irreversibly
    #    to clay minerals → effective bioaccessibility ≈ 0
    pka = substance.get("pka", None)
    if pka is None:
        # Neutral molecule — no charge correction
        charge_state = 0.0
    elif pka > 10:
        # Strong base → fully protonated at soil pH → cationic binding
        charge_state = 1.0
    elif pka < 2:
        # Strong acid → anionic at soil pH → mobile
        charge_state = -0.5
    else:
        # Weak acid/base — partial correction
        charge_state = max(0, (pka - 5.0) / 5.0)  # 0 at pH5, 1.0 at pH10

    # 5. Conjugated pi system size — photolability proxy
    #    Large conjugated systems (rotenone, pyrethrins) absorb UV/vis
    #    and undergo rapid photodegradation
    conjugated_pi_size = 0
    if smiles:
        try:
            from rdkit import Chem
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                # Count aromatic atoms as proxy for conjugated system extent
                aromatic_atoms = sum(1 for a in mol.GetAtoms() if a.GetIsAromatic())
                # Also count non-aromatic double bonds (extended conjugation)
                conj_double = 0
                for bond in mol.GetBonds():
                    if bond.GetBondTypeAsDouble() == 2.0 and not bond.GetIsAromatic():
                        conj_double += 1
                conjugated_pi_size = aromatic_atoms + conj_double * 2
        except Exception:
            pass

    # ── Phase 5c: DegT50-targeted features ──
    # 6. Heteroatom ratio — N,O,S density drives microbial targeting
    #    High ratio → more enzymatic attack sites → faster degradation
    #    (Neonicotinoids have high N count but are persistent due to molecular rigidity)
    heteroatom_ratio = 0.0
    if smiles:
        try:
            from rdkit import Chem
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                heteroatoms = sum(1 for a in mol.GetAtoms() if a.GetSymbol() in ('N', 'O', 'S', 'P'))
                total = mol.GetNumHeavyAtoms()
                heteroatom_ratio = heteroatoms / max(total, 1)
        except Exception:
            pass

    # 7. sp3 fraction — molecular shape and flexibility
    #    High sp3 → flexible, exposed → easier degradation
    #    Low sp3 → planar, aromatic → persistent
    sp3_fraction = 0.5  # default
    if smiles:
        try:
            from rdkit import Chem
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                sp3_atoms = sum(1 for a in mol.GetAtoms()
                              if a.GetHybridization() == Chem.rdchem.HybridizationType.SP3)
                sp3_fraction = sp3_atoms / max(mol.GetNumHeavyAtoms(), 1)
        except Exception:
            pass

    # 8. Henry-to-solubility ratio — volatilization as degradation pathway
    #    High Henry const + low solubility → volatile loss from soil
    henry = substance.get("henry_const", 1e-5)
    henry_volatility = np.log10(max(henry, 1e-15)) - np.log10(max(sol, 1e-6))

    # 9. Oxidation susceptibility — electron-rich sites for cytochrome P450
    #    Tertiary C, allylic/benzylic, thioethers → metabolic lability
    oxidation_susceptibility = 0
    if smiles:
        try:
            from rdkit import Chem
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                ox_patterns = [
                    Chem.MolFromSmarts("[CH0]([C])([C])[C]"),  # tertiary C-H
                    Chem.MolFromSmarts("[CH2]c"),               # benzylic
                    Chem.MolFromSmarts("[CH2]C=C"),             # allylic
                    Chem.MolFromSmarts("[#16X2]"),              # thioether
                    Chem.MolFromSmarts("[NH]"),                 # secondary amine
                ]
                for pat in ox_patterns:
                    if pat:
                        oxidation_susceptibility += len(mol.GetSubstructMatches(pat))
        except Exception:
            pass

    raw = pnp.array([
        substance.get("mw", 300),
        substance.get("logP", 2.0),
        n_heavy,
        hbd,
        hba,
        n_rings,
        substance.get("n_rotatable", 3),
        np.log10(max(sol, 1e-6)),
        np.log10(max(vp, 1e-15)),
        substance.get("freundlich_n", 0.9),
        tpsa_approx,
        aromatic_frac,
        # Phase 4a proxies
        n_hydrolyzable,
        n_halogens,
        bioaccessibility,
        # Phase 4b blind-spot corrections
        charge_state,
        conjugated_pi_size,
        # Phase 5c DegT50-targeted
        heteroatom_ratio,
        sp3_fraction,
        henry_volatility,
        oxidation_susceptibility,
    ], dtype=float, requires_grad=False)

    # Min-max scaling to [0, π] based on dataset statistics
    mins = pnp.array([
        150.8, -4.6, 6, 0, 2, 0, 0, -3.7, -12.0, 0.80,
        0.0, 0.0, 0, 0, -8.0, -0.5, 0,
        0.0, 0.0, -15.0, 0,  # Phase 5c
    ], dtype=float, requires_grad=False)
    maxs = pnp.array([
        731.9, 7.0, 52, 4, 10, 5, 10, 6.1, -1.0, 1.00,
        150.0, 3.0, 5, 6, 2.0, 1.0, 30,
        0.7, 1.0, 5.0, 10,  # Phase 5c
    ], dtype=float, requires_grad=False)

    scaled = (raw - mins) / (maxs - mins + 1e-8)
    scaled = pnp.clip(scaled, 0.0, 1.0) * np.pi

    return scaled


# ── Quantum circuits ────────────────────────────────────────────────
# Two circuit sizes: 6-qubit (DegT50) and 12-qubit (Koc)

def _build_circuit_body(features, weights, n_qubits, n_layers):
    """Shared circuit body: IQP encoding + variational layers."""
    n_feat = len(features)
    # Layer 1: Angle encoding
    for i in range(n_qubits):
        qml.Hadamard(wires=i)
        qml.RZ(features[i % n_feat], wires=i)

    # Layer 2: IQP-style feature entanglement (ZZ gates)
    for i in range(n_qubits - 1):
        qml.CNOT(wires=[i, i + 1])
        qml.RZ(features[i % n_feat] * features[(i + 1) % n_feat], wires=i + 1)
        qml.CNOT(wires=[i, i + 1])

    # Layer 2b: Encode remaining features (>n_qubits) via cross-rotation
    for j in range(n_qubits, n_feat):
        wire = j % n_qubits
        qml.RY(features[j], wires=wire)

    # Layer 3: Second angle encoding for re-uploading
    for i in range(n_qubits):
        qml.RY(features[i % n_feat], wires=i)

    # Variational layers
    for layer in range(n_layers):
        for i in range(n_qubits):
            qml.Rot(weights[layer, i, 0],
                     weights[layer, i, 1],
                     weights[layer, i, 2], wires=i)
        for i in range(0, n_qubits - 1, 2):
            qml.CNOT(wires=[i, i + 1])
        if layer % 2 == 0:
            for i in range(1, n_qubits - 1, 2):
                qml.CNOT(wires=[i, i + 1])
            qml.CNOT(wires=[n_qubits - 1, 0])

    return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]


@qml.qnode(dev_deg, interface="autograd")
def quantum_circuit_deg(features, weights):
    """6-qubit circuit for DegT50 prediction (97 params, reduced overfitting)."""
    return _build_circuit_body(features, weights, N_QUBITS_DEG, N_LAYERS_DEG)


@qml.qnode(dev_koc, interface="autograd")
def quantum_circuit_koc(features, weights):
    """12-qubit circuit for Koc prediction (301 params, more expressive)."""
    return _build_circuit_body(features, weights, N_QUBITS_KOC, N_LAYERS_KOC)


# Backward-compat alias — existing code referencing quantum_circuit uses 12q
quantum_circuit = quantum_circuit_koc


# ── Linear readout ──────────────────────────────────────────────────

def circuit_predict(features, weights, readout_weights, circuit_fn=None, n_q=None):
    """
    Get prediction from circuit output.
    readout_weights: array(n_q + 1,) — linear weights + bias
    circuit_fn: which circuit to use (default: 12-qubit)
    """
    if circuit_fn is None:
        circuit_fn = quantum_circuit_koc
    if n_q is None:
        n_q = N_QUBITS_KOC
    expvals = pnp.array(circuit_fn(features, weights))
    pred = pnp.dot(readout_weights[:n_q], expvals) + readout_weights[n_q]
    return pred


# ── Training ────────────────────────────────────────────────────────

def _train_model(features_list, targets, n_epochs=80, lr=0.05,
                 n_qubits=None, n_layers=None, circuit_fn=None, seed=42):
    """
    Train a quantum circuit + linear readout using Adam optimizer
    with early stopping.

    Parameters
    ----------
    features_list : list of arrays
        Feature vectors for each substance.
    targets : array
        Log10-transformed target values.
    n_epochs : int
        Maximum number of training epochs.
    lr : float
        Learning rate.
    n_qubits : int
        Number of qubits (default: N_QUBITS_KOC=12).
    n_layers : int
        Number of variational layers (default: N_LAYERS_KOC=8).
    circuit_fn : callable
        QNode to use (default: quantum_circuit_koc).
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    weights, readout_weights, final_loss
    """
    if n_qubits is None:
        n_qubits = N_QUBITS_KOC
    if n_layers is None:
        n_layers = N_LAYERS_KOC
    if circuit_fn is None:
        circuit_fn = quantum_circuit_koc

    # Initialize parameters
    np.random.seed(seed)
    weights = pnp.array(
        np.random.uniform(-0.5, 0.5, (n_layers, n_qubits, 3)),
        requires_grad=True
    )
    readout_weights = pnp.array(
        np.random.uniform(-0.5, 0.5, n_qubits + 1),
        requires_grad=True
    )

    opt = qml.AdamOptimizer(stepsize=lr)

    def cost_fn(weights, readout_weights):
        total_loss = pnp.array(0.0)
        for feat, target in zip(features_list, targets):
            pred = circuit_predict(feat, weights, readout_weights, circuit_fn, n_qubits)
            total_loss = total_loss + (pred - target) ** 2
        return total_loss / len(features_list)

    best_loss = float('inf')
    best_weights = weights.copy()
    best_readout = readout_weights.copy()
    patience_counter = 0

    for epoch in range(n_epochs):
        (weights, readout_weights), loss = opt.step_and_cost(
            cost_fn, weights, readout_weights
        )

        loss_val = float(loss)
        if loss_val < best_loss:
            best_loss = loss_val
            best_weights = weights.copy()
            best_readout = readout_weights.copy()
            patience_counter = 0
        else:
            patience_counter += 1

        if epoch % 20 == 0 or epoch == n_epochs - 1:
            print(f"    Epoch {epoch:3d}/{n_epochs}: MSE = {loss_val:.4f}")

        # Early stopping
        if patience_counter >= EARLY_STOP_PATIENCE:
            print(f"    Early stopping at epoch {epoch} (no improvement for {EARLY_STOP_PATIENCE} epochs)")
            break

    return best_weights, best_readout, best_loss


def _init_pretrained_weights():
    """
    Train per-target models on the substance database.
    DegT50 → 6-qubit circuit (reduced overfitting)
    Koc    → 12-qubit circuit (more expressive)
    """
    from backend.spin_database import SUBSTANCES

    features_list = []
    targets_deg = []
    targets_koc = []

    for sub in SUBSTANCES:
        feat = extract_features(sub)
        features_list.append(feat)
        targets_deg.append(pnp.array(np.log10(max(sub["degT50_soil"], 0.1)), requires_grad=False))
        targets_koc.append(pnp.array(np.log10(max(sub["koc"], 0.1)), requires_grad=False))

    n_var_deg = N_LAYERS_DEG * N_QUBITS_DEG * 3
    n_var_koc = N_LAYERS_KOC * N_QUBITS_KOC * 3
    print(f"  Training on {len(SUBSTANCES)} substances")
    print(f"  DegT50 circuit: {N_QUBITS_DEG}q × {N_LAYERS_DEG}L = {n_var_deg} var params (ratio: {(n_var_deg + N_QUBITS_DEG + 1) / len(SUBSTANCES):.2f})")
    print(f"  Koc circuit:    {N_QUBITS_KOC}q × {N_LAYERS_KOC}L = {n_var_koc} var params (ratio: {(n_var_koc + N_QUBITS_KOC + 1) / len(SUBSTANCES):.2f})")
    print(f"  DegT50 range: {min(s['degT50_soil'] for s in SUBSTANCES):.1f} – {max(s['degT50_soil'] for s in SUBSTANCES):.0f} days")
    print(f"  Koc range:    {min(s['koc'] for s in SUBSTANCES):.0f} – {max(s['koc'] for s in SUBSTANCES):,.0f} mL/g")

    print(f"\n  Training DegT50 model ({N_QUBITS_DEG}-qubit circuit)...")
    w_deg, r_deg, l_deg = _train_model(
        features_list, targets_deg, n_epochs=80, lr=0.04,
        n_qubits=N_QUBITS_DEG, n_layers=N_LAYERS_DEG,
        circuit_fn=quantum_circuit_deg
    )

    print(f"\n  Training Koc model ({N_QUBITS_KOC}-qubit circuit)...")
    w_koc, r_koc, l_koc = _train_model(
        features_list, targets_koc, n_epochs=80, lr=0.04,
        n_qubits=N_QUBITS_KOC, n_layers=N_LAYERS_KOC,
        circuit_fn=quantum_circuit_koc
    )

    return w_deg, r_deg, w_koc, r_koc, l_deg, l_koc


# ── Persistent weight cache with incremental learning ───────────────
import hashlib
import json
import os

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".qml_cache")
CACHE_FILE = os.path.join(CACHE_DIR, "weights_v2.npz")
HASH_FILE = os.path.join(CACHE_DIR, "db_hash.json")

_cached_weights = None

INCREMENTAL_THRESHOLD = 5  # fine-tune readout if ≤ this many substances changed
SIMILARITY_THRESHOLD = 0.3  # Tanimoto cutoff; below = structurally novel → full retrain
DESCRIPTOR_NOVELTY_THRESHOLD = 3.0  # Euclidean distance in feature space; above = novel


def _check_chemical_novelty(new_substances, existing_substances):
    """
    Chemical-space guardrail: detect if any new substance is structurally
    isolated from the existing training set.

    Returns (is_novel: bool, reason: str).

    Strategy:
    1. Try RDKit Tanimoto similarity on Morgan fingerprints (best)
    2. Fall back to Euclidean distance in normalized descriptor space
    """
    # ── Try RDKit first
    try:
        from rdkit import Chem, RDLogger
        from rdkit.Chem import rdFingerprintGenerator
        from rdkit import DataStructs

        # Suppress noisy RDKit warnings
        RDLogger.DisableLog('rdApp.*')

        gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)

        existing_fps = []
        for s in existing_substances:
            mol = Chem.MolFromSmiles(s.get("smiles", ""))
            if mol:
                existing_fps.append(gen.GetFingerprint(mol))

        if existing_fps:
            for ns in new_substances:
                mol = Chem.MolFromSmiles(ns.get("smiles", ""))
                if not mol:
                    continue
                new_fp = gen.GetFingerprint(mol)
                max_sim = max(DataStructs.TanimotoSimilarity(new_fp, fp) for fp in existing_fps)
                if max_sim < SIMILARITY_THRESHOLD:
                    return True, (
                        f"{ns['name']} Tanimoto similarity = {max_sim:.3f} "
                        f"(< {SIMILARITY_THRESHOLD}) — structurally novel"
                    )
            return False, "all new substances have Tanimoto ≥ threshold"

    except ImportError:
        pass  # RDKit not available, fall back to descriptor distance

    # ── Fallback: Euclidean distance in normalized descriptor space
    existing_feats = [extract_features(s) for s in existing_substances]
    for ns in new_substances:
        new_feat = extract_features(ns)
        min_dist = min(
            float(np.sqrt(np.sum((new_feat - ef) ** 2)))
            for ef in existing_feats
        )
        if min_dist > DESCRIPTOR_NOVELTY_THRESHOLD:
            return True, (
                f"{ns['name']} descriptor distance = {min_dist:.2f} "
                f"(> {DESCRIPTOR_NOVELTY_THRESHOLD}) — novel in feature space"
            )

    return False, "all new substances within descriptor-space threshold"


def _compute_db_hash():
    """Compute a hash of the substance database to detect changes."""
    from backend.spin_database import SUBSTANCES
    data_str = json.dumps(
        [{k: v for k, v in s.items() if k != "smiles"} for s in SUBSTANCES],
        sort_keys=True, default=str
    )
    return hashlib.sha256(data_str.encode()).hexdigest()[:16]


def _save_weights(weights_dict, db_hash, n_substances):
    """Save trained weights to disk with metadata."""
    from backend.spin_database import SUBSTANCES as ALL_SUBS
    os.makedirs(CACHE_DIR, exist_ok=True)
    np.savez(
        CACHE_FILE,
        weights_deg=np.array(weights_dict["weights_deg"]),
        readout_deg=np.array(weights_dict["readout_deg"]),
        weights_koc=np.array(weights_dict["weights_koc"]),
        readout_koc=np.array(weights_dict["readout_koc"]),
        loss_deg=np.array(weights_dict["loss_deg"]),
        loss_koc=np.array(weights_dict["loss_koc"]),
    )
    with open(HASH_FILE, "w") as f:
        json.dump({
            "hash": db_hash,
            "n_substances": n_substances,
            "n_qubits": N_QUBITS,
            "substance_names": [s["name"] for s in ALL_SUBS],
        }, f)
    print(f"  Weights saved to {CACHE_FILE}")


def _load_cached_meta():
    """Load cached metadata (hash, substance count). Returns dict or None."""
    if not os.path.exists(HASH_FILE):
        return None
    try:
        with open(HASH_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def _load_cached_weights_raw():
    """Load raw weight arrays from disk. Returns dict or None."""
    if not os.path.exists(CACHE_FILE):
        return None
    data = np.load(CACHE_FILE)
    return {
        "weights_deg": pnp.array(data["weights_deg"], requires_grad=False),
        "readout_deg": pnp.array(data["readout_deg"], requires_grad=False),
        "weights_koc": pnp.array(data["weights_koc"], requires_grad=False),
        "readout_koc": pnp.array(data["readout_koc"], requires_grad=False),
        "loss_deg": float(data["loss_deg"]),
        "loss_koc": float(data["loss_koc"]),
    }


def _fine_tune_readout(old_weights, features_list, targets_deg, targets_koc,
                       n_epochs=15, lr=0.05):
    """Fine-tune only the readout (linear) layer — variational weights frozen."""
    print("  Fine-tuning readout layer only (variational weights frozen)...")

    # Frozen variational weights
    w_deg_frozen = pnp.array(old_weights["weights_deg"], requires_grad=False)
    w_koc_frozen = pnp.array(old_weights["weights_koc"], requires_grad=False)

    # Trainable readout weights — warm-start from old values
    r_deg = pnp.array(old_weights["readout_deg"], requires_grad=True)
    r_koc = pnp.array(old_weights["readout_koc"], requires_grad=True)

    # Pre-compute all quantum circuit outputs (forward pass only, no gradient through circuit)
    print("    Pre-computing quantum circuit outputs...")
    deg_expectations = [pnp.array(quantum_circuit(f, w_deg_frozen), requires_grad=False)
                        for f in features_list]
    koc_expectations = [pnp.array(quantum_circuit(f, w_koc_frozen), requires_grad=False)
                        for f in features_list]

    # Train readout on DegT50
    opt_deg = qml.AdamOptimizer(stepsize=lr)

    def loss_deg(readout):
        total = 0.0
        for exp_vals, target in zip(deg_expectations, targets_deg):
            pred = pnp.dot(readout[:N_QUBITS], exp_vals) + readout[N_QUBITS]
            total = total + (pred - target) ** 2
        return total / len(targets_deg)

    for epoch in range(n_epochs):
        r_deg, cost = opt_deg.step_and_cost(loss_deg, r_deg)
        if epoch % 5 == 0 or epoch == n_epochs - 1:
            print(f"    DegT50 readout epoch {epoch:3d}/{n_epochs}: MSE = {float(cost):.4f}")
    l_deg = float(loss_deg(r_deg))

    # Train readout on Koc
    opt_koc = qml.AdamOptimizer(stepsize=lr)

    def loss_koc(readout):
        total = 0.0
        for exp_vals, target in zip(koc_expectations, targets_koc):
            pred = pnp.dot(readout[:N_QUBITS], exp_vals) + readout[N_QUBITS]
            total = total + (pred - target) ** 2
        return total / len(targets_koc)

    for epoch in range(n_epochs):
        r_koc, cost = opt_koc.step_and_cost(loss_koc, r_koc)
        if epoch % 5 == 0 or epoch == n_epochs - 1:
            print(f"    Koc readout epoch {epoch:3d}/{n_epochs}: MSE = {float(cost):.4f}")
    l_koc = float(loss_koc(r_koc))

    return w_deg_frozen, r_deg, w_koc_frozen, r_koc, l_deg, l_koc


def _get_weights():
    global _cached_weights
    if _cached_weights is None:
        _ensure_initialized()
    return _cached_weights


def _train_weights():
    global _cached_weights
    from backend.spin_database import SUBSTANCES

    n_var_deg = N_LAYERS_DEG * N_QUBITS_DEG * 3
    n_var_koc = N_LAYERS_KOC * N_QUBITS_KOC * 3
    print(f"[QML v3] Initializing quantum ML predictor (per-target circuits)...")
    print(f"  DegT50: {N_QUBITS_DEG}q × {N_LAYERS_DEG}L = {n_var_deg + N_QUBITS_DEG + 1} params")
    print(f"  Koc:    {N_QUBITS_KOC}q × {N_LAYERS_KOC}L = {n_var_koc + N_QUBITS_KOC + 1} params")

    current_hash = _compute_db_hash()
    current_n = len(SUBSTANCES)
    meta = _load_cached_meta()

    # ── Case 1: Cache matches exactly → instant load
    if meta and meta.get("hash") == current_hash and meta.get("n_qubits") == N_QUBITS:
        cached = _load_cached_weights_raw()
        if cached:
            _cached_weights = cached
            print(f"  Loaded cached weights ({meta['n_substances']} substances)")
            print(f"  DegT50 MSE={cached['loss_deg']:.4f}, Koc MSE={cached['loss_koc']:.4f}")
            print("[QML v3] Ready! (loaded from cache, no training needed)\n")
            return

    # ── Case 2: Hash differs — check if incremental or full retrain
    old_weights = _load_cached_weights_raw()
    old_n = meta.get("n_substances", 0) if meta else 0
    old_qubits = meta.get("n_qubits", 0) if meta else 0
    n_diff = abs(current_n - old_n)

    if old_weights and old_qubits == N_QUBITS and n_diff <= INCREMENTAL_THRESHOLD:
        # Count-based check passed — now check chemical-space novelty
        print(f"  Database changed: {old_n} → {current_n} substances ({n_diff} changed)")

        # Identify new substances (those not in old set by name)
        old_names = set(meta.get("substance_names", [])) if meta else set()
        new_subs = [s for s in SUBSTANCES if s["name"] not in old_names] if old_names else []
        existing_subs = [s for s in SUBSTANCES if s["name"] in old_names] if old_names else SUBSTANCES

        if new_subs and existing_subs:
            is_novel, novelty_reason = _check_chemical_novelty(new_subs, existing_subs)
            if is_novel:
                print(f"  ⚠️  Chemical novelty detected: {novelty_reason}")
                print(f"  Escalating to full retrain (frozen feature map may not represent this compound)")
                # Fall through to Case 3
            else:
                print(f"  ✓ Novelty check passed: {novelty_reason}")
        else:
            is_novel = False

        if not is_novel:
            # ── Incremental: fine-tune readout only
            print(f"  ≤{INCREMENTAL_THRESHOLD} changes → incremental fine-tune (readout only)")
            print(f"  Training on {current_n} substances, {N_QUBITS} qubits, {N_LAYERS} layers")

            features_list = [extract_features(sub) for sub in SUBSTANCES]
            targets_deg = [pnp.array(np.log10(max(s["degT50_soil"], 0.1)), requires_grad=False) for s in SUBSTANCES]
            targets_koc = [pnp.array(np.log10(max(s["koc"], 0.1)), requires_grad=False) for s in SUBSTANCES]

            w_deg, r_deg, w_koc, r_koc, l_deg, l_koc = _fine_tune_readout(
                old_weights, features_list, targets_deg, targets_koc
            )

            _cached_weights = {
                "weights_deg": w_deg, "readout_deg": r_deg,
                "weights_koc": w_koc, "readout_koc": r_koc,
                "loss_deg": l_deg, "loss_koc": l_koc,
            }
            _save_weights(_cached_weights, current_hash, current_n)
            print(f"\n[QML v3] Incremental training complete!")
            print(f"  Final MSE — DegT50: {l_deg:.4f}, Koc: {l_koc:.4f}")
            return

    # ── Case 3: Full retrain (no cache, architecture change, big DB change, or novel compound)
    reason = "no cache" if not old_weights else f"{n_diff} substance changes (>{INCREMENTAL_THRESHOLD})"
    if old_qubits and old_qubits != N_QUBITS:
        reason = f"qubit count changed ({old_qubits}→{N_QUBITS})"
    print(f"  Full retrain needed: {reason}")
    print(f"  Training from scratch...")

    w_deg, r_deg, w_koc, r_koc, l_deg, l_koc = _init_pretrained_weights()
    _cached_weights = {
        "weights_deg": w_deg, "readout_deg": r_deg,
        "weights_koc": w_koc, "readout_koc": r_koc,
        "loss_deg": l_deg, "loss_koc": l_koc,
    }
    _save_weights(_cached_weights, current_hash, current_n)

    print(f"\n[QML v3] Training complete!")
    print(f"  Final MSE — DegT50: {l_deg:.4f}, Koc: {l_koc:.4f}")
    print(f"  (MSE is on log10 scale: 0.5 ≈ factor-of-3 error, 0.1 ≈ 25% error)")


# Lazy initialization — only train when predictions are needed
_initialized = False


def _ensure_initialized():
    """Initialize quantum predictor on first predict call (not on import)."""
    global _initialized
    if not _initialized:
        _train_weights()
        _initialized = True


# ── Prediction functions ────────────────────────────────────────────

def predict_degtl50(substance):
    """Predict DegT50 (soil half-life in days) using the 6-qubit circuit."""
    weights = _get_weights()
    features = extract_features(substance)

    expvals = quantum_circuit_deg(features, weights["weights_deg"])
    expvals_arr = pnp.array(expvals)
    log_pred = float(pnp.dot(weights["readout_deg"][:N_QUBITS_DEG], expvals_arr) + weights["readout_deg"][N_QUBITS_DEG])

    predicted = 10 ** log_pred
    experimental = substance["degT50_soil"]

    return {
        "substance": substance["name"],
        "property": "DegT50_soil",
        "predicted_days": round(predicted, 1),
        "experimental_days": experimental,
        "error_pct": round(abs(predicted - experimental) / max(experimental, 0.1) * 100, 1),
        "log10_predicted": round(log_pred, 3),
        "log10_experimental": round(np.log10(max(experimental, 0.1)), 3),
        "n_qubits": N_QUBITS_DEG,
        "n_layers": N_LAYERS_DEG,
        "circuit_depth": N_LAYERS_DEG * 3 + 4,
        "expectation_values": [float(e) for e in expvals],
    }


def predict_koc(substance):
    """Predict Koc (organic carbon adsorption coefficient) using the 12-qubit circuit."""
    weights = _get_weights()
    features = extract_features(substance)

    expvals = quantum_circuit_koc(features, weights["weights_koc"])
    expvals_arr = pnp.array(expvals)
    log_pred = float(pnp.dot(weights["readout_koc"][:N_QUBITS_KOC], expvals_arr) + weights["readout_koc"][N_QUBITS_KOC])

    predicted = 10 ** log_pred
    experimental = substance["koc"]

    return {
        "substance": substance["name"],
        "property": "Koc",
        "predicted_ml_g": round(predicted, 1),
        "experimental_ml_g": experimental,
        "error_pct": round(abs(predicted - experimental) / max(experimental, 0.1) * 100, 1),
        "log10_predicted": round(log_pred, 3),
        "log10_experimental": round(np.log10(max(experimental, 0.1)), 3),
        "n_qubits": N_QUBITS_KOC,
        "n_layers": N_LAYERS_KOC,
        "circuit_depth": N_LAYERS_KOC * 3 + 4,
        "expectation_values": [float(e) for e in expvals],
    }


def predict_all(substance):
    """Predict both DegT50 and Koc for a substance."""
    return {
        "degtl50": predict_degtl50(substance),
        "koc": predict_koc(substance),
    }


def batch_predict(substances):
    """Predict DegT50 and Koc for a list of substances."""
    results = []
    for sub in substances:
        try:
            pred = predict_all(sub)
            results.append({
                "name": sub["name"],
                "cas": sub["cas"],
                "degtl50_exp": sub["degT50_soil"],
                "degtl50_pred": pred["degtl50"]["predicted_days"],
                "degtl50_err_pct": pred["degtl50"]["error_pct"],
                "koc_exp": sub["koc"],
                "koc_pred": pred["koc"]["predicted_ml_g"],
                "koc_err_pct": pred["koc"]["error_pct"],
            })
        except Exception as e:
            results.append({
                "name": sub["name"],
                "cas": sub["cas"],
                "error": str(e),
            })
    return results


def get_circuit_info():
    """Return information about both per-target quantum circuit architectures."""
    weights = _get_weights()
    n_var_deg = N_LAYERS_DEG * N_QUBITS_DEG * 3
    n_var_koc = N_LAYERS_KOC * N_QUBITS_KOC * 3
    return {
        # Per-target circuit info
        "degt50_circuit": {
            "n_qubits": N_QUBITS_DEG,
            "n_layers": N_LAYERS_DEG,
            "variational_params": n_var_deg,
            "readout_params": N_QUBITS_DEG + 1,
            "total_params": n_var_deg + N_QUBITS_DEG + 1,
            "params_per_sample": round((n_var_deg + N_QUBITS_DEG + 1) / 111, 2),
        },
        "koc_circuit": {
            "n_qubits": N_QUBITS_KOC,
            "n_layers": N_LAYERS_KOC,
            "variational_params": n_var_koc,
            "readout_params": N_QUBITS_KOC + 1,
            "total_params": n_var_koc + N_QUBITS_KOC + 1,
            "params_per_sample": round((n_var_koc + N_QUBITS_KOC + 1) / 111, 2),
        },
        # Backward compat (aggregate)
        "n_qubits": N_QUBITS_KOC,
        "n_layers": N_LAYERS_KOC,
        "variational_params": n_var_koc,
        "readout_params": N_QUBITS_KOC + 1,
        "total_params": n_var_koc + N_QUBITS_KOC + 1,
        "n_parameters": n_var_koc + N_QUBITS_KOC + 1,
        "gate_count": N_QUBITS_KOC * 3 + (N_QUBITS_KOC - 1) * 3 + N_QUBITS_KOC + N_LAYERS_KOC * (N_QUBITS_KOC * 3 + N_QUBITS_KOC),
        "circuit_depth": N_LAYERS_KOC * 3 + 4,
        "feature_count": len(FEATURE_NAMES),
        "feature_names": FEATURE_NAMES,
        "training_loss_degtl50": float(weights["loss_deg"]),
        "training_loss_koc": float(weights["loss_koc"]),
        "encoding": "IQP-style angle + ZZ entangling + data re-uploading",
        "optimizer": "Adam (gradient-based, parameter-shift rule)",
        "early_stopping": f"patience={EARLY_STOP_PATIENCE}",
        "device": "default.qubit (statevector simulator)",
        "framework": f"PennyLane {qml.__version__}",
        "architecture": "Per-target: 6q/5L (DegT50) + 12q/8L (Koc)",
    }


# ── Cross-validation ────────────────────────────────────────────────

CV_CACHE_FILE = os.path.join(CACHE_DIR, "cv_results.json")


def run_cross_validation(n_epochs_cv=60, lr_cv=0.05, k_folds=None):
    """
    Cross-validation for the QML model.

    Args:
        n_epochs_cv: Training epochs per fold (default 25)
        lr_cv: Learning rate per fold (default 0.05)
        k_folds: Number of folds. None = leave-one-out (N folds).
                 Set to e.g. 5 for 5-fold CV (faster, ~20× less time).
    """
    from backend.spin_database import SUBSTANCES

    n = len(SUBSTANCES)
    actual_folds = k_folds if k_folds else n
    cv_type = f"{k_folds}-fold" if k_folds else "leave-one-out"

    # Per-type cache file
    cache_suffix = f"_k{k_folds}" if k_folds else "_loo"
    cv_cache = os.path.join(CACHE_DIR, f"cv_results{cache_suffix}.json")

    # Check cache
    if os.path.exists(cv_cache):
        with open(cv_cache, "r") as f:
            cached = json.load(f)
        current_hash = _compute_db_hash()
        if cached.get("db_hash") == current_hash:
            print(f"[CV] Loaded cached {cv_type} CV results ({len(cached['results'])} folds)")
            return cached

    print(f"[CV] Running {cv_type} cross-validation ({actual_folds} folds, {n} substances)...")
    all_features = [extract_features(sub) for sub in SUBSTANCES]
    all_deg = [pnp.array(np.log10(max(s["degT50_soil"], 0.1)), requires_grad=False) for s in SUBSTANCES]
    all_koc = [pnp.array(np.log10(max(s["koc"], 0.1)), requires_grad=False) for s in SUBSTANCES]

    results = []

    if k_folds:
        # ── K-fold: shuffle and split into k groups
        indices = list(range(n))
        np.random.seed(42)  # reproducible splits
        np.random.shuffle(indices)
        fold_size = n // k_folds
        folds = []
        for f in range(k_folds):
            start = f * fold_size
            end = start + fold_size if f < k_folds - 1 else n
            folds.append(indices[start:end])

        for fold_idx, test_indices in enumerate(folds):
            train_indices = [i for i in indices if i not in test_indices]

            train_feat = [all_features[i] for i in train_indices]
            train_deg = [all_deg[i] for i in train_indices]
            train_koc = [all_koc[i] for i in train_indices]

            w_deg, r_deg, _ = _train_model(train_feat, train_deg, n_epochs=n_epochs_cv, lr=lr_cv)
            w_koc, r_koc, _ = _train_model(train_feat, train_koc, n_epochs=n_epochs_cv, lr=lr_cv)

            for i in test_indices:
                feat = all_features[i]
                exp_deg = quantum_circuit(feat, w_deg)
                exp_koc = quantum_circuit(feat, w_koc)
                pred_deg = float(pnp.dot(pnp.array(r_deg[:N_QUBITS]), pnp.array(exp_deg)) + r_deg[N_QUBITS])
                pred_koc = float(pnp.dot(pnp.array(r_koc[:N_QUBITS]), pnp.array(exp_koc)) + r_koc[N_QUBITS])

                sub = SUBSTANCES[i]
                results.append({
                    "name": sub["name"],
                    "fold": fold_idx + 1,
                    "deg_exp": float(all_deg[i]),
                    "deg_pred": round(pred_deg, 3),
                    "deg_pred_days": round(10 ** pred_deg, 1),
                    "deg_exp_days": sub["degT50_soil"],
                    "koc_exp": float(all_koc[i]),
                    "koc_pred": round(pred_koc, 3),
                    "koc_pred_val": round(10 ** pred_koc, 1),
                    "koc_exp_val": sub["koc"],
                })

            print(f"  Fold {fold_idx + 1}/{k_folds} complete ({len(test_indices)} test substances)")
    else:
        # ── Leave-one-out (with fold-level checkpointing)
        checkpoint_file = os.path.join(CACHE_DIR, "loo_checkpoint.json")

        # Resume from checkpoint if available
        completed_results = {}
        if os.path.exists(checkpoint_file):
            try:
                with open(checkpoint_file, "r") as f:
                    checkpoint = json.load(f)
                for r in checkpoint.get("results", []):
                    completed_results[r["name"]] = r
                print(f"  Resuming from checkpoint: {len(completed_results)}/{n} folds complete")
            except Exception:
                pass

        for i in range(n):
            sub = SUBSTANCES[i]
            # Skip already-completed folds
            if sub["name"] in completed_results:
                results.append(completed_results[sub["name"]])
                continue

            train_feat = [f for j, f in enumerate(all_features) if j != i]
            train_deg = [t for j, t in enumerate(all_deg) if j != i]
            train_koc = [t for j, t in enumerate(all_koc) if j != i]

            w_deg, r_deg, _ = _train_model(train_feat, train_deg, n_epochs=n_epochs_cv, lr=lr_cv)
            w_koc, r_koc, _ = _train_model(train_feat, train_koc, n_epochs=n_epochs_cv, lr=lr_cv)

            feat = all_features[i]
            exp_deg = quantum_circuit(feat, w_deg)
            exp_koc = quantum_circuit(feat, w_koc)
            pred_deg = float(pnp.dot(pnp.array(r_deg[:N_QUBITS]), pnp.array(exp_deg)) + r_deg[N_QUBITS])
            pred_koc = float(pnp.dot(pnp.array(r_koc[:N_QUBITS]), pnp.array(exp_koc)) + r_koc[N_QUBITS])

            fold_result = {
                "name": sub["name"],
                "fold": i + 1,
                "deg_exp": float(all_deg[i]),
                "deg_pred": round(pred_deg, 3),
                "deg_pred_days": round(10 ** pred_deg, 1),
                "deg_exp_days": sub["degT50_soil"],
                "koc_exp": float(all_koc[i]),
                "koc_pred": round(pred_koc, 3),
                "koc_pred_val": round(10 ** pred_koc, 1),
                "koc_exp_val": sub["koc"],
            }
            results.append(fold_result)

            # Save checkpoint after every fold
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(checkpoint_file, "w") as f:
                json.dump({"results": results, "completed": len(results)}, f)

            if (i + 1) % 5 == 0 or i == n - 1:
                print(f"  Fold {i + 1}/{n} complete (checkpointed)")


    # Calculate overall stats
    deg_errors = [abs(r["deg_exp"] - r["deg_pred"]) for r in results]
    koc_errors = [abs(r["koc_exp"] - r["koc_pred"]) for r in results]

    def calc_r2(exp_list, pred_list):
        mean_exp = sum(exp_list) / len(exp_list)
        ss_res = sum((e - p) ** 2 for e, p in zip(exp_list, pred_list))
        ss_tot = sum((e - mean_exp) ** 2 for e in exp_list)
        return 1 - ss_res / max(ss_tot, 1e-10)

    output = {
        "cv_type": cv_type,
        "n_folds": actual_folds,
        "n_substances": n,
        "n_qubits": N_QUBITS,
        "n_layers": N_LAYERS,
        "cv_epochs": n_epochs_cv,
        "results": results,
        "deg_r2": round(calc_r2([r["deg_exp"] for r in results], [r["deg_pred"] for r in results]), 4),
        "deg_mae": round(sum(deg_errors) / len(deg_errors), 4),
        "deg_rmse": round((sum(e ** 2 for e in deg_errors) / len(deg_errors)) ** 0.5, 4),
        "koc_r2": round(calc_r2([r["koc_exp"] for r in results], [r["koc_pred"] for r in results]), 4),
        "koc_mae": round(sum(koc_errors) / len(koc_errors), 4),
        "koc_rmse": round((sum(e ** 2 for e in koc_errors) / len(koc_errors)) ** 0.5, 4),
        "db_hash": _compute_db_hash(),
    }

    # Cache results
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cv_cache, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[CV] {cv_type} complete! DegT50 R²={output['deg_r2']:.3f}, Koc R²={output['koc_r2']:.3f}")

    return output
