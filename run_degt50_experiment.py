#!/usr/bin/env python3
"""
DegT50 Architecture Experiment — Standalone Runner
====================================================
Tests 4 quantum circuit variants for DegT50 prediction via 5-fold CV.
Designed to run independently on laptop16 while the main LOO CV runs on laptop32.

Usage:
    cd /home/ca/qp-fate
    nohup python -u run_degt50_experiment.py > degt50_experiment.log 2>&1 &

Results saved to: backend/.qml_cache/degt50_experiment_results.json
"""

import sys
import os
import json
import time
from datetime import datetime

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pennylane as qml
from pennylane import numpy as pnp

from backend.quantum_predictor import extract_features, N_FEATURES, FEATURE_NAMES
from backend.spin_database import SUBSTANCES

# ── Output paths ─────────────────────────────────────────────────────
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", ".qml_cache")
RESULTS_FILE = os.path.join(CACHE_DIR, "degt50_experiment_results.json")
CHECKPOINT_FILE = os.path.join(CACHE_DIR, "degt50_experiment_checkpoint.json")


# ═══════════════════════════════════════════════════════════════════════
#  VARIANT A: Shallow-Wide (12 qubits, 3 layers, all-to-all CZ)
# ═══════════════════════════════════════════════════════════════════════

def make_variant_a():
    """Shallow-wide: more entanglement, fewer layers to avoid barren plateaus."""
    n_qubits = 12
    n_layers = 3
    dev = qml.device("default.qubit", wires=n_qubits)

    @qml.qnode(dev, interface="autograd")
    def circuit(features, weights):
        n_feat = len(features)

        # Double data re-uploading for richer encoding
        for rep in range(2):
            for i in range(n_qubits):
                qml.Hadamard(wires=i)
                qml.RZ(features[i % n_feat], wires=i)
                qml.RY(features[(i + rep * 3) % n_feat], wires=i)

            # IQP-style ZZ interactions
            for i in range(n_qubits - 1):
                qml.CNOT(wires=[i, i + 1])
                qml.RZ(features[i % n_feat] * features[(i + 1) % n_feat], wires=i + 1)
                qml.CNOT(wires=[i, i + 1])

        # Variational layers with ALL-TO-ALL CZ entanglement
        for layer in range(n_layers):
            for i in range(n_qubits):
                qml.Rot(weights[layer, i, 0],
                        weights[layer, i, 1],
                        weights[layer, i, 2], wires=i)

            # All-to-all CZ gates (much richer entanglement)
            for i in range(n_qubits):
                for j in range(i + 1, n_qubits):
                    qml.CZ(wires=[i, j])

        return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]

    return {
        "name": "A_shallow_wide",
        "description": "12q, 3L, all-to-all CZ, double re-upload",
        "n_qubits": n_qubits,
        "n_layers": n_layers,
        "circuit": circuit,
        "lr": 0.03,
        "epochs": 80,
        "weight_shape": (n_layers, n_qubits, 3),
    }


# ═══════════════════════════════════════════════════════════════════════
#  VARIANT B: Deep-Narrow (8 qubits, 12 layers, ring CNOT)
# ═══════════════════════════════════════════════════════════════════════

def make_variant_b():
    """Deep-narrow: fewer qubits, more layers, ring entanglement."""
    n_qubits = 8
    n_layers = 12
    dev = qml.device("default.qubit", wires=n_qubits)

    @qml.qnode(dev, interface="autograd")
    def circuit(features, weights):
        n_feat = len(features)

        # Triple data re-uploading
        for rep in range(3):
            for i in range(n_qubits):
                qml.RX(features[(i + rep * n_qubits) % n_feat], wires=i)
                qml.RZ(features[(i + rep * n_qubits + 1) % n_feat], wires=i)

            # ZZ entanglement
            for i in range(n_qubits - 1):
                qml.CNOT(wires=[i, i + 1])
                qml.RZ(features[i % n_feat] * features[(i + 1) % n_feat], wires=i + 1)
                qml.CNOT(wires=[i, i + 1])

        # Variational layers with RING CNOT connectivity
        for layer in range(n_layers):
            for i in range(n_qubits):
                qml.Rot(weights[layer, i, 0],
                        weights[layer, i, 1],
                        weights[layer, i, 2], wires=i)

            # Ring: nearest-neighbor + wrap-around
            for i in range(n_qubits):
                qml.CNOT(wires=[i, (i + 1) % n_qubits])

        return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]

    return {
        "name": "B_deep_narrow",
        "description": "8q, 12L, ring CNOT, triple re-upload",
        "n_qubits": n_qubits,
        "n_layers": n_layers,
        "circuit": circuit,
        "lr": 0.02,
        "epochs": 100,
        "weight_shape": (n_layers, n_qubits, 3),
    }


# ═══════════════════════════════════════════════════════════════════════
#  VARIANT C: Hardware-Efficient (PennyLane StronglyEntanglingLayers)
# ═══════════════════════════════════════════════════════════════════════

def make_variant_c():
    """Hardware-efficient: PennyLane's optimized entangling template."""
    n_qubits = 12
    n_layers = 5
    dev = qml.device("default.qubit", wires=n_qubits)

    @qml.qnode(dev, interface="autograd")
    def circuit(features, weights):
        n_feat = len(features)

        # Amplitude-inspired encoding via RY + angle encoding via RZ
        for i in range(n_qubits):
            qml.RY(features[i % n_feat], wires=i)
            qml.RZ(features[(i + 4) % n_feat], wires=i)

        # Data re-upload with RX
        for i in range(n_qubits):
            qml.RX(features[(i + 8) % n_feat], wires=i)

        # PennyLane's StronglyEntanglingLayers template
        qml.StronglyEntanglingLayers(weights, wires=range(n_qubits))

        return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]

    return {
        "name": "C_hardware_efficient",
        "description": "12q, 5L, StronglyEntanglingLayers, mixed encoding",
        "n_qubits": n_qubits,
        "n_layers": n_layers,
        "circuit": circuit,
        "lr": 0.04,
        "epochs": 60,
        "weight_shape": qml.StronglyEntanglingLayers.shape(n_layers=n_layers, n_wires=n_qubits),
    }


# ═══════════════════════════════════════════════════════════════════════
#  VARIANT D: Baseline+ (same arch, lower LR, more epochs)
# ═══════════════════════════════════════════════════════════════════════

def make_variant_d():
    """Baseline+: current architecture with slower optimization — is it just training?"""
    n_qubits = 12
    n_layers = 8
    dev = qml.device("default.qubit", wires=n_qubits)

    @qml.qnode(dev, interface="autograd")
    def circuit(features, weights):
        n_feat = len(features)

        # Identical to current quantum_predictor.py circuit
        for i in range(n_qubits):
            qml.Hadamard(wires=i)
            qml.RZ(features[i % n_feat], wires=i)

        for i in range(n_qubits - 1):
            qml.CNOT(wires=[i, i + 1])
            qml.RZ(features[i % n_feat] * features[(i + 1) % n_feat], wires=i + 1)
            qml.CNOT(wires=[i, i + 1])

        for j in range(n_qubits, n_feat):
            wire = j % n_qubits
            qml.RY(features[j], wires=wire)

        for i in range(n_qubits):
            qml.RY(features[i % n_feat], wires=i)

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

    return {
        "name": "D_baseline_plus",
        "description": "12q, 8L, current arch, lr=0.03, 120 epochs",
        "n_qubits": n_qubits,
        "n_layers": n_layers,
        "circuit": circuit,
        "lr": 0.03,
        "epochs": 120,
        "weight_shape": (n_layers, n_qubits, 3),
    }


# ═══════════════════════════════════════════════════════════════════════
#  TRAINING + CV HARNESS
# ═══════════════════════════════════════════════════════════════════════

def train_degt50(circuit_fn, features_list, targets, weight_shape,
                 n_epochs=60, lr=0.05, seed=42):
    """
    Train a quantum circuit for DegT50 only.
    Returns (weights, readout_weights, best_loss, loss_history).
    """
    np.random.seed(seed)
    n_qubits = len(circuit_fn(features_list[0],
                               pnp.array(np.random.uniform(-0.5, 0.5, weight_shape),
                                         requires_grad=False)))

    weights = pnp.array(np.random.uniform(-0.5, 0.5, weight_shape), requires_grad=True)
    readout = pnp.array(np.random.uniform(-0.5, 0.5, n_qubits + 1), requires_grad=True)

    opt = qml.AdamOptimizer(stepsize=lr)

    def cost_fn(weights, readout):
        total_loss = pnp.array(0.0)
        for feat, target in zip(features_list, targets):
            expvals = pnp.array(circuit_fn(feat, weights))
            pred = pnp.dot(readout[:n_qubits], expvals) + readout[n_qubits]
            total_loss = total_loss + (pred - target) ** 2
        return total_loss / len(features_list)

    best_loss = float('inf')
    best_weights = weights.copy()
    best_readout = readout.copy()
    loss_history = []

    for epoch in range(n_epochs):
        (weights, readout), loss = opt.step_and_cost(cost_fn, weights, readout)
        loss_val = float(loss)
        loss_history.append(loss_val)

        if loss_val < best_loss:
            best_loss = loss_val
            best_weights = weights.copy()
            best_readout = readout.copy()

        if epoch % 20 == 0 or epoch == n_epochs - 1:
            print(f"      Epoch {epoch:3d}/{n_epochs}: MSE = {loss_val:.4f}", flush=True)

    return best_weights, best_readout, best_loss, loss_history


def calc_r2(exp_list, pred_list):
    """Calculate R² (coefficient of determination)."""
    mean_exp = sum(exp_list) / len(exp_list)
    ss_res = sum((e - p) ** 2 for e, p in zip(exp_list, pred_list))
    ss_tot = sum((e - mean_exp) ** 2 for e in exp_list)
    return 1 - ss_res / max(ss_tot, 1e-10)


def run_5fold_cv(variant, all_features, all_targets, k=5):
    """Run k-fold CV for a single variant. Returns dict with metrics."""
    n = len(all_features)
    circuit_fn = variant["circuit"]
    n_qubits = variant["n_qubits"]

    # Reproducible shuffle
    indices = list(range(n))
    np.random.seed(42)
    np.random.shuffle(indices)

    fold_size = n // k
    folds = []
    for f in range(k):
        start = f * fold_size
        end = start + fold_size if f < k - 1 else n
        folds.append(indices[start:end])

    results = []
    fold_losses = []

    for fold_idx, test_indices in enumerate(folds):
        print(f"    Fold {fold_idx + 1}/{k} ({len(test_indices)} test)...", flush=True)
        train_indices = [i for i in indices if i not in test_indices]

        train_feat = [all_features[i] for i in train_indices]
        train_targets = [all_targets[i] for i in train_indices]

        w, r, loss, history = train_degt50(
            circuit_fn, train_feat, train_targets,
            variant["weight_shape"],
            n_epochs=variant["epochs"],
            lr=variant["lr"],
        )
        fold_losses.append(loss)

        # Predict on test set
        for i in test_indices:
            feat = all_features[i]
            expvals = pnp.array(circuit_fn(feat, w))
            pred = float(pnp.dot(pnp.array(r[:n_qubits]), expvals) + r[n_qubits])
            results.append({
                "name": SUBSTANCES[i]["name"],
                "fold": fold_idx + 1,
                "deg_exp": float(all_targets[i]),
                "deg_pred": round(pred, 3),
                "deg_pred_days": round(10 ** pred, 1),
                "deg_exp_days": SUBSTANCES[i]["degT50_soil"],
            })

        print(f"    Fold {fold_idx + 1}/{k} complete — train MSE: {loss:.4f}", flush=True)

    # Aggregate metrics
    r2 = calc_r2([r["deg_exp"] for r in results], [r["deg_pred"] for r in results])
    mae = sum(abs(r["deg_exp"] - r["deg_pred"]) for r in results) / len(results)
    rmse = (sum((r["deg_exp"] - r["deg_pred"]) ** 2 for r in results) / len(results)) ** 0.5

    return {
        "variant": variant["name"],
        "description": variant["description"],
        "n_qubits": variant["n_qubits"],
        "n_layers": variant["n_layers"],
        "lr": variant["lr"],
        "epochs": variant["epochs"],
        "deg_r2": round(r2, 4),
        "deg_mae": round(mae, 4),
        "deg_rmse": round(rmse, 4),
        "mean_train_mse": round(sum(fold_losses) / len(fold_losses), 4),
        "results": results,
    }


# ═══════════════════════════════════════════════════════════════════════
#  MAIN: Run all variants
# ═══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70, flush=True)
    print("  DegT50 Architecture Experiment", flush=True)
    print(f"  {len(SUBSTANCES)} substances, {N_FEATURES} features, 5-fold CV", flush=True)
    print(f"  Started: {datetime.now().isoformat()}", flush=True)
    print("=" * 70, flush=True)

    # Prepare data (DegT50 only)
    all_features = [extract_features(sub) for sub in SUBSTANCES]
    all_targets = [
        pnp.array(np.log10(max(s["degT50_soil"], 0.1)), requires_grad=False)
        for s in SUBSTANCES
    ]

    variants = [make_variant_a(), make_variant_b(), make_variant_c(), make_variant_d()]

    # Load checkpoint (resume from where we left off)
    completed = {}
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                completed = json.load(f)
            print(f"\n  Resuming from checkpoint: {len(completed)} variants complete", flush=True)
        except Exception:
            completed = {}

    all_results = {}

    for variant in variants:
        name = variant["name"]

        if name in completed:
            print(f"\n{'─' * 70}", flush=True)
            print(f"  SKIP {name} — already completed (R² = {completed[name]['deg_r2']})", flush=True)
            all_results[name] = completed[name]
            continue

        print(f"\n{'─' * 70}", flush=True)
        print(f"  VARIANT: {name}", flush=True)
        print(f"  {variant['description']}", flush=True)
        print(f"  Config: lr={variant['lr']}, epochs={variant['epochs']}", flush=True)
        t0 = time.time()

        result = run_5fold_cv(variant, all_features, all_targets)
        elapsed = time.time() - t0
        result["elapsed_seconds"] = round(elapsed, 1)
        result["elapsed_human"] = f"{elapsed / 3600:.1f} h"

        print(f"\n  → DegT50 R² = {result['deg_r2']:.4f}  (MAE={result['deg_mae']:.4f}, "
              f"RMSE={result['deg_rmse']:.4f})", flush=True)
        print(f"  → Time: {result['elapsed_human']}", flush=True)

        all_results[name] = result

        # Checkpoint after each variant
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(CHECKPOINT_FILE, "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"  → Checkpointed ({len(all_results)}/{len(variants)} variants)", flush=True)

    # ── Final summary ─────────────────────────────────────────────
    print(f"\n{'═' * 70}", flush=True)
    print("  RESULTS SUMMARY — DegT50 5-Fold CV", flush=True)
    print(f"{'═' * 70}", flush=True)
    print(f"  {'Variant':<25} {'R²':>8} {'MAE':>8} {'RMSE':>8} {'Time':>10}", flush=True)
    print(f"  {'─' * 25} {'─' * 8} {'─' * 8} {'─' * 8} {'─' * 10}", flush=True)

    for name in [v["name"] for v in variants]:
        r = all_results[name]
        r2_str = f"{r['deg_r2']:>8.4f}"
        # Color-code R² in the log
        marker = "★" if r["deg_r2"] > 0 else "✗"
        print(f"  {marker} {r['description']:<23} {r2_str} {r['deg_mae']:>8.4f} "
              f"{r['deg_rmse']:>8.4f} {r.get('elapsed_human', '?'):>10}", flush=True)

    # Current baseline for reference
    print(f"  ─ {'Current (60ep, lr=0.05)':<23} {'−0.1410':>8} {'—':>8} {'—':>8} {'—':>10}", flush=True)

    # Save final results (without per-fold details for cleaner file)
    summary = {
        "experiment": "DegT50 Architecture Search",
        "timestamp": datetime.now().isoformat(),
        "n_substances": len(SUBSTANCES),
        "n_features": N_FEATURES,
        "cv_folds": 5,
        "baseline_r2": -0.141,
        "variants": {
            name: {k: v for k, v in r.items() if k != "results"}
            for name, r in all_results.items()
        },
        "full_results": all_results,
    }
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  Results saved to: {RESULTS_FILE}", flush=True)

    # Find best
    best_name = max(all_results, key=lambda k: all_results[k]["deg_r2"])
    best = all_results[best_name]
    print(f"\n  ◈ Best variant: {best_name} — R² = {best['deg_r2']:.4f}", flush=True)

    if best["deg_r2"] > -0.141:
        improvement = best["deg_r2"] - (-0.141)
        print(f"  ◈ Improvement over baseline: {improvement:+.4f}", flush=True)
    else:
        print(f"  ◈ No improvement over baseline — consider feature engineering or target transformation", flush=True)

    print(f"\n  Finished: {datetime.now().isoformat()}", flush=True)


if __name__ == "__main__":
    main()
