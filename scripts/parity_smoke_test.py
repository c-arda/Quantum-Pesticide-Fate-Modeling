"""
Parity gate 1: 3-way comparison on 5 baseline compounds.
========================================================
Compares per-qubit PauliZ expectation values across:
  (A) noiseless default.qubit  (existing quantum_predictor.quantum_circuit_*)
  (B) noisy   default.mixed    (backend.quantum_hardware)
  (C) noisy   cirq.mixedsim    (backend.quantum_hardware_cirq)

Pass criteria (all must hold):
  - (A) matches saved baseline_5cmp.json to within 1e-6
  - For each (compound, qubit) cell, (B) and (C) agree within 2σ shot noise
    where σ = sqrt((1 - <Z>²) / N_SHOTS)

Exits non-zero on any failure.

Usage:
  python scripts/parity_smoke_test.py [--shots 8192]
"""

import argparse
import json
import os
import sys

import numpy as np
import pennylane as qml
from pennylane import numpy as pnp

# Make backend importable when run from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import quantum_predictor as qp
from backend.spin_database import SUBSTANCES
from backend.quantum_hardware import make_noisy_qnodes, N_SHOTS_DEFAULT

# Hard-coded indices — see plan / baseline_5cmp.json
INDICES = {
    "deg_fast":  29,   # Ferric phosphate, degT50_soil = 0.5 d
    "deg_mid":   92,   # Phenmedipham,    degT50_soil = 25.0 d
    "deg_slow":  52,   # Flutriafol,      degT50_soil = 1389 d
    "koc_low":   66,   # Oxamyl,          koc = 25
    "koc_high":  42,   # Diquat,          koc = 1_000_000
}

NOISELESS_TOL = 1e-6


def _shot_sigma(z, n_shots):
    var = max(0.0, 1.0 - z * z)
    return float(np.sqrt(var / n_shots))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shots", type=int, default=N_SHOTS_DEFAULT)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-cirq", action="store_true",
                        help="Skip Cirq cross-check (use if pennylane-cirq unavailable)")
    args = parser.parse_args()

    np.random.seed(args.seed)

    baseline_path = os.path.join(qp.CACHE_DIR, "review_experiments", "baseline_5cmp.json")
    with open(baseline_path) as f:
        baseline = json.load(f)

    w = qp._load_cached_weights_raw()
    if w is None:
        print("ERROR: cached weights missing", file=sys.stderr)
        return 2

    deg_noisy, koc_noisy = make_noisy_qnodes(shots=args.shots, seed=args.seed)

    if not args.skip_cirq:
        try:
            from backend.quantum_hardware_cirq import make_cirq_qnodes
            deg_cirq, koc_cirq = make_cirq_qnodes(shots=args.shots, seed=args.seed)
        except Exception as e:
            print(f"ERROR: Cirq unavailable ({e}). Re-run with --skip-cirq to bypass.", file=sys.stderr)
            return 3

    failures = []
    print(f"\n{'='*78}")
    print(f"Parity gate 1 — {len(INDICES)} compounds, {args.shots} shots, seed={args.seed}")
    print(f"{'='*78}\n")

    for label, idx in INDICES.items():
        sub = SUBSTANCES[idx]
        feat_full = qp.extract_features(sub)
        feat_deg = feat_full[qp.QML_DEG_FEATURE_INDICES]

        # (A) noiseless reference
        a_deg = np.array([float(x) for x in qp.quantum_circuit_deg(feat_deg, w["weights_deg"])])
        a_koc = np.array([float(x) for x in qp.quantum_circuit_koc(feat_full, w["weights_koc"])])

        # Compare against saved baseline
        saved = baseline["compounds"][label]
        delta_a_deg = np.max(np.abs(a_deg - np.array(saved["expvals_deg"])))
        delta_a_koc = np.max(np.abs(a_koc - np.array(saved["expvals_koc"])))
        if delta_a_deg > NOISELESS_TOL or delta_a_koc > NOISELESS_TOL:
            failures.append(f"{label}: noiseless drift deg={delta_a_deg:.2e} koc={delta_a_koc:.2e}")

        # (B) default.mixed noisy
        b_deg = np.array([float(x) for x in deg_noisy(feat_deg, w["weights_deg"])])
        b_koc = np.array([float(x) for x in koc_noisy(feat_full, w["weights_koc"])])

        if not args.skip_cirq:
            # (C) Cirq mixed-state
            c_deg = np.array([float(x) for x in deg_cirq(feat_deg, w["weights_deg"])])
            c_koc = np.array([float(x) for x in koc_cirq(feat_full, w["weights_koc"])])
        else:
            c_deg = np.full_like(b_deg, np.nan)
            c_koc = np.full_like(b_koc, np.nan)

        print(f"--- {label}  idx={idx}  {sub['name']}")
        print(f"  noiseless drift: deg={delta_a_deg:.2e}  koc={delta_a_koc:.2e}  (tol {NOISELESS_TOL:.0e})")

        # Per-cell B vs C check (skipped if Cirq absent)
        if not args.skip_cirq:
            for tag, b_arr, c_arr in [("deg", b_deg, c_deg), ("koc", b_koc, c_koc)]:
                for q, (bv, cv) in enumerate(zip(b_arr, c_arr)):
                    sigma = max(_shot_sigma(bv, args.shots), _shot_sigma(cv, args.shots))
                    if abs(bv - cv) > 2 * sigma:
                        failures.append(
                            f"{label} {tag} q{q}: |B-C|={abs(bv-cv):.4f} > 2σ={2*sigma:.4f}"
                        )
            print(f"  noisy max |B-C|: deg={np.max(np.abs(b_deg-c_deg)):.4f}  koc={np.max(np.abs(b_koc-c_koc)):.4f}")
        else:
            print(f"  Cirq skipped")

    print(f"\n{'='*78}")
    if failures:
        print(f"FAIL — {len(failures)} cell(s) failed:")
        for f_ in failures:
            print(f"  {f_}")
        return 1
    print("PASS — all noiseless within tol; all noisy cells agree within 2σ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
