"""
Cirq density-matrix cross-check for the Phase 5a noisy harness.
===============================================================
Same circuit body and same noise channels as backend.quantum_hardware, but
executed via the Cirq mixed-state simulator through pennylane-cirq. This is
a cross-engine sanity check: if default.mixed and cirq.mixedsimulator agree
to within shot noise on the same compounds, the noise model is internally
consistent.

Requires: pennylane-cirq, cirq-core (see requirements.txt).
"""

import numpy as np
import pennylane as qml
from pennylane import numpy as pnp

from backend import quantum_predictor as qp
from backend.spin_database import SUBSTANCES
from backend.quantum_hardware import (
    _build_circuit_body_noisy,
    _noise_ops_cirq,
    N_SHOTS_DEFAULT,
)


def _make_dev_cirq(n_qubits, shots):
    """cirq.mixedsimulator via pennylane-cirq."""
    return qml.device("cirq.mixedsimulator", wires=n_qubits, shots=shots)


def make_cirq_qnodes(shots=N_SHOTS_DEFAULT, seed=42):
    """
    Build (deg, koc) noisy QNodes on the Cirq mixed-state simulator.
    Reuses _build_circuit_body_noisy from backend.quantum_hardware so that
    the *circuit and noise model are byte-identical* between engines.
    """
    if seed is not None:
        np.random.seed(seed)

    dev_deg = _make_dev_cirq(qp.N_QUBITS_DEG, shots)
    dev_koc = _make_dev_cirq(qp.N_QUBITS_KOC, shots)
    cirq_ops = _noise_ops_cirq()

    @qml.qnode(dev_deg, interface="autograd")
    def quantum_circuit_deg_cirq(features, weights):
        return _build_circuit_body_noisy(
            features, weights, qp.N_QUBITS_DEG, qp.N_LAYERS_DEG, noise_ops=cirq_ops
        )

    @qml.qnode(dev_koc, interface="autograd")
    def quantum_circuit_koc_cirq(features, weights):
        return _build_circuit_body_noisy(
            features, weights, qp.N_QUBITS_KOC, qp.N_LAYERS_KOC, noise_ops=cirq_ops
        )

    return quantum_circuit_deg_cirq, quantum_circuit_koc_cirq


def predict_cirq(substance, target="deg", n_shots=N_SHOTS_DEFAULT, seed=42):
    """Cirq-engine analogue of quantum_hardware.predict_noisy."""
    w = qp._load_cached_weights_raw()
    if w is None:
        raise RuntimeError("No cached weights — train via quantum_predictor first.")

    feat_full = qp.extract_features(substance)
    deg_qn, koc_qn = make_cirq_qnodes(shots=n_shots, seed=seed)

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
        "engine": "cirq.mixedsimulator",
        "n_shots": n_shots,
        "prediction_log10": pred,
        "prediction": float(10 ** pred),
        "expvals": [float(x) for x in exp],
    }


def smoke():
    return predict_cirq(SUBSTANCES[0], target="deg", n_shots=512)


if __name__ == "__main__":
    import json
    print(json.dumps(smoke(), indent=2))
