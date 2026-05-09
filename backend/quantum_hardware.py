"""
Quantum Hardware Mirror — PennyLane default.mixed with IonQ Aria noise model
============================================================================
Local noisy simulation harness for the Phase 5a circuits, intended to predict
what the IonQ Aria QPU will return *before* we spend any cloud budget.

Public API mirrors backend/quantum_predictor.py:
  - quantum_circuit_deg_noisy(features, weights)
  - quantum_circuit_koc_noisy(features, weights)
  - predict_noisy(substance, target, n_shots=N_SHOTS)

Reuses trained checkpoint via quantum_predictor._load_cached_weights_raw —
no retraining.

Noise parameters: IonQ Aria public spec sheet (verify before any hardware run).
Source: https://ionq.com/quantum-systems/aria  (accessed: 2026-05-01)
  - 1q gate error : ~5e-4   (1q fidelity ~99.95%)
  - 2q gate error : ~6e-3   (2q fidelity ~99.4%)
  - T1            : ~10 s   (electronic level)
  - T2            : ~1 s
  - 1q gate time  : ~135 us
  - 2q gate time  : ~600 us
  - SPAM error    : ~5e-3
Convert T1/T2 + gate-time to per-gate amplitude-damping / phase-damping gammas.

NOTE on duplication: _build_circuit_body in quantum_predictor.py is a
monolithic QNode body. Inserting per-layer noise channels mid-body without
modifying that file is impossible, so this module duplicates the circuit
structure. Keep them in sync; future refactor: thread an optional noise hook
through _build_circuit_body upstream.
"""

import os
import json
import numpy as np
import pennylane as qml
from pennylane import numpy as pnp

from backend import quantum_predictor as qp
from backend.spin_database import SUBSTANCES

# ── IonQ Aria noise parameters ──────────────────────────────────────
# Verify these against https://ionq.com/quantum-systems/aria at submit time.
P_1Q_DEPOL  = 5e-4    # 1q depolarizing error per gate
P_2Q_DEPOL  = 6e-3    # 2q depolarizing error per gate
P_READOUT   = 5e-3    # SPAM error per qubit
T1_S        = 10.0
T2_S        = 1.0
T_1Q_S      = 135e-6
T_2Q_S      = 600e-6

# Per-gate amplitude-damping gamma = 1 - exp(-t/T1)
GAMMA_AMP_1Q = 1.0 - np.exp(-T_1Q_S / T1_S)
GAMMA_AMP_2Q = 1.0 - np.exp(-T_2Q_S / T1_S)

N_SHOTS_DEFAULT = 8192

# ── Devices ─────────────────────────────────────────────────────────
def _make_dev(n_qubits, shots):
    return qml.device("default.mixed", wires=n_qubits, shots=shots)


# ── Noise channel sets (engine-specific names; same physics) ────────
# default.mixed uses standard PennyLane channel ops; cirq.mixedsimulator uses
# pennylane-cirq's wrappers (Depolarize, AmplitudeDamp, BitFlip). Channel
# parameters are identical — only the op classes differ.
NOISE_OPS_DEFAULT = {
    "depolarize": lambda p, w: qml.DepolarizingChannel(p, wires=w),
    "amp_damp":   lambda g, w: qml.AmplitudeDamping(g, wires=w),
    "bit_flip":   lambda p, w: qml.BitFlip(p, wires=w),
}

def _noise_ops_cirq():
    from pennylane_cirq import ops as cops
    return {
        "depolarize": lambda p, w: cops.Depolarize(p, wires=w),
        "amp_damp":   lambda g, w: cops.AmplitudeDamp(g, wires=w),
        "bit_flip":   lambda p, w: cops.BitFlip(p, wires=w),
    }


# ── Noisy circuit body (mirrors quantum_predictor._build_circuit_body) ──
def _build_circuit_body_noisy(features, weights, n_qubits, n_layers, noise_ops=None):
    """
    Mirror of quantum_predictor._build_circuit_body with IonQ Aria noise.

    noise_ops: dict of channel constructors {"depolarize", "amp_damp", "bit_flip"}.
      Defaults to NOISE_OPS_DEFAULT (default.mixed). For cirq.mixedsimulator,
      pass _noise_ops_cirq().

    Noise insertion strategy:
      - After every 1q gate: depolarize(P_1Q_DEPOL) + amp_damp(GAMMA_AMP_1Q)
      - After every 2q gate (CNOT): depolarize(P_2Q_DEPOL) + amp_damp(GAMMA_AMP_2Q) on both wires
      - Before measurement: bit_flip(P_READOUT) per wire (readout/SPAM)
    Returns the same list of PauliZ expvals as the noiseless version.
    """
    if noise_ops is None:
        noise_ops = NOISE_OPS_DEFAULT
    n_feat = len(features)

    def noise_1q(w):
        noise_ops["depolarize"](P_1Q_DEPOL, w)
        noise_ops["amp_damp"](GAMMA_AMP_1Q, w)

    def noise_2q(w0, w1):
        noise_ops["depolarize"](P_2Q_DEPOL, w0)
        noise_ops["depolarize"](P_2Q_DEPOL, w1)
        noise_ops["amp_damp"](GAMMA_AMP_2Q, w0)
        noise_ops["amp_damp"](GAMMA_AMP_2Q, w1)

    # Layer 1: Hadamard + RZ encoding
    for i in range(n_qubits):
        qml.Hadamard(wires=i)
        noise_1q(i)
        qml.RZ(features[i % n_feat], wires=i)
        noise_1q(i)

    # Layer 2: IQP-style ZZ entanglement
    for i in range(n_qubits - 1):
        qml.CNOT(wires=[i, i + 1])
        noise_2q(i, i + 1)
        qml.RZ(features[i % n_feat] * features[(i + 1) % n_feat], wires=i + 1)
        noise_1q(i + 1)
        qml.CNOT(wires=[i, i + 1])
        noise_2q(i, i + 1)

    # Layer 2b: cross-rotation for features beyond n_qubits
    for j in range(n_qubits, n_feat):
        wire = j % n_qubits
        qml.RY(features[j], wires=wire)
        noise_1q(wire)

    # Layer 3: re-uploading
    for i in range(n_qubits):
        qml.RY(features[i % n_feat], wires=i)
        noise_1q(i)

    # Variational layers
    for layer in range(n_layers):
        for i in range(n_qubits):
            qml.Rot(weights[layer, i, 0],
                    weights[layer, i, 1],
                    weights[layer, i, 2], wires=i)
            noise_1q(i)
        for i in range(0, n_qubits - 1, 2):
            qml.CNOT(wires=[i, i + 1])
            noise_2q(i, i + 1)
        if layer % 2 == 0:
            for i in range(1, n_qubits - 1, 2):
                qml.CNOT(wires=[i, i + 1])
                noise_2q(i, i + 1)
            qml.CNOT(wires=[n_qubits - 1, 0])
            noise_2q(n_qubits - 1, 0)

    # Readout / SPAM noise
    for i in range(n_qubits):
        noise_ops["bit_flip"](P_READOUT, i)

    return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]


# ── Noisy QNodes (factory because devices depend on shots) ──────────
def make_noisy_qnodes(shots=N_SHOTS_DEFAULT, seed=42):
    """
    Return (quantum_circuit_deg_noisy, quantum_circuit_koc_noisy) bound to
    fresh default.mixed devices with the requested shot count.
    """
    if seed is not None:
        np.random.seed(seed)

    dev_deg = _make_dev(qp.N_QUBITS_DEG, shots)
    dev_koc = _make_dev(qp.N_QUBITS_KOC, shots)

    @qml.qnode(dev_deg, interface="autograd")
    def quantum_circuit_deg_noisy(features, weights):
        return _build_circuit_body_noisy(
            features, weights, qp.N_QUBITS_DEG, qp.N_LAYERS_DEG
        )

    @qml.qnode(dev_koc, interface="autograd")
    def quantum_circuit_koc_noisy(features, weights):
        return _build_circuit_body_noisy(
            features, weights, qp.N_QUBITS_KOC, qp.N_LAYERS_KOC
        )

    return quantum_circuit_deg_noisy, quantum_circuit_koc_noisy


# Module-level convenience instances at default shot count
quantum_circuit_deg_noisy, quantum_circuit_koc_noisy = make_noisy_qnodes()


# ── Prediction entrypoint ───────────────────────────────────────────
def predict_noisy(substance, target="deg", n_shots=N_SHOTS_DEFAULT, seed=42):
    """
    Run the noisy circuit on a substance dict, apply the cached linear
    readout, and return the prediction in log10 space.
    target: 'deg' or 'koc'
    """
    w = qp._load_cached_weights_raw()
    if w is None:
        raise RuntimeError(
            "No cached weights — train via quantum_predictor first "
            "(weights_v2.npz missing)."
        )

    feat_full = qp.extract_features(substance)
    deg_qn, koc_qn = make_noisy_qnodes(shots=n_shots, seed=seed)

    if target == "deg":
        feat = feat_full[qp.QML_DEG_FEATURE_INDICES]
        exp = pnp.array(deg_qn(feat, w["weights_deg"]))
        readout = w["readout_deg"]
        n_q = qp.N_QUBITS_DEG
    elif target == "koc":
        feat = feat_full
        exp = pnp.array(koc_qn(feat, w["weights_koc"]))
        readout = w["readout_koc"]
        n_q = qp.N_QUBITS_KOC
    else:
        raise ValueError(f"target must be 'deg' or 'koc', got {target!r}")

    pred = float(pnp.dot(readout[:n_q], exp) + readout[n_q])
    return {
        "name": substance.get("name"),
        "target": target,
        "n_shots": n_shots,
        "prediction_log10": pred,
        "prediction": float(10 ** pred),
        "expvals": [float(x) for x in exp],
    }


def smoke():
    """One-compound smoke test: verify the module loads and runs."""
    sub = SUBSTANCES[0]
    return predict_noisy(sub, target="deg", n_shots=512)


if __name__ == "__main__":
    print(json.dumps(smoke(), indent=2))
