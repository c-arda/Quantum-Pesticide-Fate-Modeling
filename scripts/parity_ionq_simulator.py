"""
Parity gate 2: IonQ hosted simulator vs. local default.mixed.
=============================================================
Same 5 baseline compounds as gate 1. Submits to ionq.simulator (free tier)
with backend="aria-1" so we get IonQ's own Aria noise model. Compares per-cell
expvals against backend.quantum_hardware.default.mixed output within 2σ.

Requires:
  - pennylane-ionq installed
  - IONQ_API_KEY env var set

Usage:
  IONQ_API_KEY=... python scripts/parity_ionq_simulator.py [--shots 8192]
"""

import argparse
import json
import os
import sys

import numpy as np
import pennylane as qml
from pennylane import numpy as pnp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import quantum_predictor as qp
from backend.spin_database import SUBSTANCES
from backend.quantum_hardware import (
    _build_circuit_body_noisy,
    make_noisy_qnodes,
    N_SHOTS_DEFAULT,
)
from backend.ionq_noisy_simulator import IonQNoisySimulator
from scripts.parity_smoke_test import INDICES, _shot_sigma  # reuse selection


def make_ionq_qnodes(shots, noise_model="aria-1"):
    dev_deg = IonQNoisySimulator(wires=qp.N_QUBITS_DEG, noise_model=noise_model, shots=shots)
    dev_koc = IonQNoisySimulator(wires=qp.N_QUBITS_KOC, noise_model=noise_model, shots=shots)

    @qml.qnode(dev_deg)
    def deg_qn(features, weights):
        # IonQ doesn't accept noise channels — submit the *clean* circuit and
        # let IonQ's hosted simulator apply its own Aria noise model.
        return qp._build_circuit_body(
            features, weights, qp.N_QUBITS_DEG, qp.N_LAYERS_DEG
        )

    @qml.qnode(dev_koc)
    def koc_qn(features, weights):
        return qp._build_circuit_body(
            features, weights, qp.N_QUBITS_KOC, qp.N_LAYERS_KOC
        )

    return deg_qn, koc_qn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shots", type=int, default=N_SHOTS_DEFAULT)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if not os.environ.get("IONQ_API_KEY"):
        print("ERROR: IONQ_API_KEY env var not set", file=sys.stderr)
        return 2

    np.random.seed(args.seed)

    w = qp._load_cached_weights_raw()
    if w is None:
        print("ERROR: cached weights missing", file=sys.stderr)
        return 2

    # Local mixed-state baseline
    deg_local, koc_local = make_noisy_qnodes(shots=args.shots, seed=args.seed)
    deg_ionq, koc_ionq   = make_ionq_qnodes(shots=args.shots)

    failures = []
    print(f"\n{'='*78}")
    print(f"Parity gate 2 — IonQ hosted sim vs default.mixed")
    print(f"{len(INDICES)} compounds, {args.shots} shots, seed={args.seed}")
    print(f"{'='*78}\n")

    for label, idx in INDICES.items():
        sub = SUBSTANCES[idx]
        feat_full = qp.extract_features(sub)
        feat_deg = feat_full[qp.QML_DEG_FEATURE_INDICES]

        b_deg = np.array([float(x) for x in deg_local(feat_deg, w["weights_deg"])])
        b_koc = np.array([float(x) for x in koc_local(feat_full, w["weights_koc"])])
        i_deg = np.array([float(x) for x in deg_ionq(feat_deg, w["weights_deg"])])
        i_koc = np.array([float(x) for x in koc_ionq(feat_full, w["weights_koc"])])

        print(f"--- {label}  idx={idx}  {sub['name']}")
        for tag, b_arr, i_arr in [("deg", b_deg, i_deg), ("koc", b_koc, i_koc)]:
            for q, (bv, iv) in enumerate(zip(b_arr, i_arr)):
                sigma = max(_shot_sigma(bv, args.shots), _shot_sigma(iv, args.shots))
                if abs(bv - iv) > 2 * sigma:
                    failures.append(f"{label} {tag} q{q}: |B-I|={abs(bv-iv):.4f} > 2σ={2*sigma:.4f}")
        print(f"  max |B-I|: deg={np.max(np.abs(b_deg-i_deg)):.4f}  koc={np.max(np.abs(b_koc-i_koc)):.4f}")

    print(f"\n{'='*78}")
    if failures:
        print(f"FAIL — {len(failures)} cell(s) failed:")
        for f_ in failures:
            print(f"  {f_}")
        return 1
    print("PASS — IonQ hosted sim matches default.mixed within 2σ on all cells")
    return 0


if __name__ == "__main__":
    sys.exit(main())
