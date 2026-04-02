#!/usr/bin/env python3
"""
Retrain Koc VQC WITHOUT bioaccessibility feature (B) — Fair Benchmark
=====================================================================
Reviewer fix 1B: The bioaccessibility feature (index 14) mathematically
leaks the Koc target. Classical models were evaluated without B, so the
VQC must also be evaluated without B for a fair comparison.

Uses diff_method="backprop" for ~10x speedup over parameter-shift rule.
Evaluates with 5-fold CV (same protocol as DegT50 evaluation).
"""

import sys
import os
import json
import time
import numpy as np
import pennylane as qml
import pennylane.numpy as pnp
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score, mean_squared_error

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.spin_database import SUBSTANCES
from backend.quantum_predictor import (
    extract_features, FEATURE_NAMES,
    N_QUBITS_KOC, N_LAYERS_KOC, EARLY_STOP_PATIENCE,
    _build_circuit_body
)

# ── Configuration ───────────────────────────────────────────────────
BIOACCESSIBILITY_INDEX = 14  # Feature to exclude
KOC_FAIR_FEATURE_INDICES = [i for i in range(21) if i != BIOACCESSIBILITY_INDEX]
N_FEATURES_FAIR = len(KOC_FAIR_FEATURE_INDICES)  # 20

N_QUBITS = N_QUBITS_KOC  # 12
N_LAYERS = N_LAYERS_KOC   # 8
N_EPOCHS = 80
LR = 0.04
N_FOLDS = 5
SEED = 42

print("=" * 70)
print("Koc VQC Retraining — WITHOUT Bioaccessibility Feature (Fair Benchmark)")
print("=" * 70)
print(f"  Features: {N_FEATURES_FAIR} (excluding '{FEATURE_NAMES[BIOACCESSIBILITY_INDEX]}')")
print(f"  Circuit:  {N_QUBITS}q × {N_LAYERS}L")
print(f"  Params:   {N_LAYERS * N_QUBITS * 3} variational + {N_QUBITS + 1} readout = {N_LAYERS * N_QUBITS * 3 + N_QUBITS + 1}")
print(f"  Epochs:   {N_EPOCHS}, LR: {LR}")
print(f"  CV:       {N_FOLDS}-fold")
print(f"  Method:   diff_method='backprop' (fast)")
print()

# ── Create backprop-compatible device and circuit ───────────────────
dev = qml.device("default.qubit", wires=N_QUBITS)

@qml.qnode(dev, diff_method="backprop", interface="autograd")
def circuit_koc_fair(features, weights):
    """12-qubit circuit for Koc with 20 features (no bioaccessibility)."""
    n_qubits = N_QUBITS
    n_layers = N_LAYERS
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

    return tuple(qml.expval(qml.PauliZ(i)) for i in range(n_qubits))


def predict(features, weights, readout_weights):
    """Linear readout on circuit outputs."""
    circuit_output = circuit_koc_fair(features, weights)
    expectations = pnp.array(list(circuit_output))
    return pnp.dot(readout_weights[:N_QUBITS], expectations) + readout_weights[N_QUBITS]


# ── Data preparation ───────────────────────────────────────────────
print("Loading data...")
features_all = []
targets_koc = []

for sub in SUBSTANCES:
    feat = extract_features(sub)
    # Take only the fair 20 features (exclude bioaccessibility)
    feat_fair = feat[KOC_FAIR_FEATURE_INDICES]
    features_all.append(pnp.array(feat_fair, requires_grad=False))
    targets_koc.append(np.log10(max(sub["koc"], 0.1)))

features_all = np.array([f.numpy() if hasattr(f, 'numpy') else np.array(f) for f in features_all])
targets_koc = np.array(targets_koc)

print(f"  Loaded {len(features_all)} substances")
print(f"  Koc range: {10**targets_koc.min():.0f} – {10**targets_koc.max():,.0f} mL/g")
print(f"  Feature shape: {features_all[0].shape}")
print()

# ── Training function ──────────────────────────────────────────────
def train_fold(X_train, y_train, seed=42):
    """Train VQC on one fold with backprop."""
    np.random.seed(seed)
    weights = pnp.array(
        np.random.uniform(-0.5, 0.5, (N_LAYERS, N_QUBITS, 3)),
        requires_grad=True
    )
    readout_weights = pnp.array(
        np.random.uniform(-0.5, 0.5, N_QUBITS + 1),
        requires_grad=True
    )

    opt = qml.AdamOptimizer(stepsize=LR)

    # Convert training data to PennyLane arrays
    X_pnp = [pnp.array(x, requires_grad=False) for x in X_train]
    y_pnp = [pnp.array(y, requires_grad=False) for y in y_train]

    def cost_fn(weights, readout_weights):
        total_loss = pnp.array(0.0)
        for feat, target in zip(X_pnp, y_pnp):
            pred = predict(feat, weights, readout_weights)
            total_loss = total_loss + (pred - target) ** 2
        return total_loss / len(X_pnp)

    best_loss = float('inf')
    best_weights = weights.copy()
    best_readout = readout_weights.copy()
    patience_counter = 0

    for epoch in range(N_EPOCHS):
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

        if epoch % 20 == 0 or epoch == N_EPOCHS - 1:
            print(f"      Epoch {epoch:3d}/{N_EPOCHS}: MSE = {loss_val:.4f}")

        if patience_counter >= EARLY_STOP_PATIENCE:
            print(f"      Early stopping at epoch {epoch} (patience={EARLY_STOP_PATIENCE})")
            break

    return best_weights, best_readout, best_loss


# ── 5-Fold Cross-Validation ─────────────────────────────────────────
print(f"Starting {N_FOLDS}-fold Cross-Validation...")
t_start = time.time()

kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
all_preds = np.zeros(len(targets_koc))
fold_results = []

for fold_idx, (train_idx, test_idx) in enumerate(kf.split(features_all)):
    print(f"\n  ── Fold {fold_idx + 1}/{N_FOLDS} ──")
    print(f"    Train: {len(train_idx)}, Test: {len(test_idx)}")

    X_train = features_all[train_idx]
    y_train = targets_koc[train_idx]
    X_test = features_all[test_idx]
    y_test = targets_koc[test_idx]

    t_fold = time.time()
    weights, readout, train_mse = train_fold(X_train, y_train, seed=SEED + fold_idx)
    fold_time = time.time() - t_fold

    # Predict on test set
    test_preds = []
    for x in X_test:
        x_pnp = pnp.array(x, requires_grad=False)
        pred = float(predict(x_pnp, weights, readout))
        test_preds.append(pred)

    test_preds = np.array(test_preds)
    all_preds[test_idx] = test_preds

    fold_r2 = r2_score(y_test, test_preds)
    fold_mse = mean_squared_error(y_test, test_preds)

    fold_results.append({
        "fold": fold_idx + 1,
        "train_mse": float(train_mse),
        "test_r2": float(fold_r2),
        "test_mse": float(fold_mse),
        "time_seconds": fold_time
    })

    print(f"    Train MSE: {train_mse:.4f}")
    print(f"    Test R²:   {fold_r2:.3f}")
    print(f"    Test MSE:  {fold_mse:.4f}")
    print(f"    Time:      {fold_time:.1f}s")

total_time = time.time() - t_start

# ── Overall Results ──────────────────────────────────────────────────
overall_r2 = r2_score(targets_koc, all_preds)
overall_mse = mean_squared_error(targets_koc, all_preds)

print("\n" + "=" * 70)
print("RESULTS: Koc VQC WITHOUT Bioaccessibility (Fair 20-Feature Model)")
print("=" * 70)
print(f"  Overall R²:  {overall_r2:.3f}")
print(f"  Overall MSE: {overall_mse:.4f}")
print(f"  Total time:  {total_time:.1f}s ({total_time/60:.1f} min)")
print()
print("  Per-fold results:")
for r in fold_results:
    print(f"    Fold {r['fold']}: R² = {r['test_r2']:.3f}, MSE = {r['test_mse']:.4f}, time = {r['time_seconds']:.0f}s")
print()

# ── Save Results ─────────────────────────────────────────────────────
results = {
    "experiment": "koc_vqc_fair_20features",
    "description": "Koc VQC retrained without bioaccessibility feature B (reviewer fix 1B)",
    "n_features": N_FEATURES_FAIR,
    "excluded_feature": FEATURE_NAMES[BIOACCESSIBILITY_INDEX],
    "n_qubits": N_QUBITS,
    "n_layers": N_LAYERS,
    "n_params": N_LAYERS * N_QUBITS * 3 + N_QUBITS + 1,
    "n_substances": len(SUBSTANCES),
    "n_folds": N_FOLDS,
    "overall_r2": float(overall_r2),
    "overall_mse": float(overall_mse),
    "total_time_seconds": total_time,
    "diff_method": "backprop",
    "fold_results": fold_results,
    "feature_names_used": [FEATURE_NAMES[i] for i in KOC_FAIR_FEATURE_INDICES],
}

output_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "backend", ".qml_cache", "koc_fair_20features_results.json"
)
output_path = os.path.abspath(output_path)

with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"Results saved to: {output_path}")
