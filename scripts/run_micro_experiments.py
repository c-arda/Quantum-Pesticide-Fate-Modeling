#!/usr/bin/env python3
"""
QP-FATE Review Micro-Experiments — laptop16 runner
====================================================
Runs the fast experiments identified by the review (~1 hour total):
  1. Regenerate classical_baseline.json (B2 fix)
  2. 17-feature RF baseline (H2)
  3. Bioaccessibility ablation for DegT50 (H3)
  4. 8-4 MLP baseline (M2)
  5. Sabljic null model for Koc (pesticide-fate recommendation)
  6. Gradient variance at VQC init (H7)

Run: ssh laptop16 'cd ~/Projects/Chemistry/Quantum\ Chemistry/Quantum\ Pesticide\ Fate\ Modeling && source .venv/bin/activate && python3 scripts/run_micro_experiments.py'
"""
import sys
import os
import json
import time
import numpy as np

# Ensure backend is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "backend", ".qml_cache", "review_experiments")
os.makedirs(RESULTS_DIR, exist_ok=True)

def save_result(name, data):
    path = os.path.join(RESULTS_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  → Saved: {path}")

# ═══════════════════════════════════════════════════════════════════
# Experiment 1: Regenerate classical_baseline.json (B2)
# ═══════════════════════════════════════════════════════════════════
def exp1_regenerate_classical_baseline():
    print("\n◈ Exp 1: Regenerating classical_baseline.json (B2 fix)...")
    t0 = time.time()

    # Delete cached file to force regeneration
    from backend.classical_predictor import CL_CACHE_FILE, train_classical_baseline
    if os.path.exists(CL_CACHE_FILE):
        os.remove(CL_CACHE_FILE)
        print("  Deleted stale cache")

    result = train_classical_baseline()
    elapsed = time.time() - t0

    # Extract headline numbers for verification
    summary = {
        "experiment": "B2_regenerate_classical_baseline",
        "elapsed_seconds": round(elapsed, 1),
        "n_substances": result["n_substances"],
        "n_features": result["n_features"],
        "db_hash": result["db_hash"],
    }
    for model in ["Ridge", "Lasso", "RandomForest", "GradientBoosting"]:
        for cv in ["loo", "5fold"]:
            m = result["models"][model][cv]
            summary[f"{model}_{cv}_deg_r2"] = m["deg_r2"]
            summary[f"{model}_{cv}_koc_r2"] = m["koc_r2"]
    # Fair Koc (no bioaccessibility)
    for model in ["Ridge", "Lasso", "RandomForest", "GradientBoosting"]:
        for cv in ["loo", "5fold"]:
            m = result["koc_no_bioaccessibility"][model][cv]
            summary[f"{model}_{cv}_koc_fair_r2"] = m["koc_r2"]

    save_result("exp1_classical_baseline_summary", summary)
    print(f"  Done in {elapsed:.1f}s. RF LOO DegT50 R²={summary['RandomForest_loo_deg_r2']}, "
          f"Koc R²={summary['RandomForest_loo_koc_r2']} (fair: {summary['RandomForest_loo_koc_fair_r2']})")
    return summary


# ═══════════════════════════════════════════════════════════════════
# Experiment 2: 17-feature RF baseline (H2)
# ═══════════════════════════════════════════════════════════════════
def exp2_17feature_baseline():
    print("\n◈ Exp 2: 17-feature RF/GB baseline (H2)...")
    t0 = time.time()

    from backend.quantum_predictor import extract_features, QML_DEG_FEATURE_INDICES, FEATURE_NAMES
    from backend.spin_database import SUBSTANCES
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import cross_val_predict, LeaveOneOut
    from sklearn.metrics import r2_score, mean_absolute_error

    X_full = np.array([extract_features(s) for s in SUBSTANCES])
    X_17 = X_full[:, QML_DEG_FEATURE_INDICES]
    y_deg = np.array([np.log10(max(s["degT50_soil"], 0.1)) for s in SUBSTANCES])
    y_koc = np.array([np.log10(max(s["koc"], 0.1)) for s in SUBSTANCES])

    loo = LeaveOneOut()
    results = {"experiment": "H2_17feature_baseline", "n_features_17": len(QML_DEG_FEATURE_INDICES),
               "n_features_21": len(FEATURE_NAMES)}

    for name, Cls, params in [
        ("Ridge", Ridge, {"alpha": 1.0}),
        ("RF", RandomForestRegressor, {"n_estimators": 200, "max_depth": 10, "random_state": 42}),
        ("GB", GradientBoostingRegressor, {"n_estimators": 200, "max_depth": 4, "learning_rate": 0.1, "random_state": 42}),
    ]:
        # 17-feature
        pred_deg_17 = cross_val_predict(Cls(**params), X_17, y_deg, cv=loo)
        pred_koc_17 = cross_val_predict(Cls(**params), X_17, y_koc, cv=loo)
        # 21-feature
        pred_deg_21 = cross_val_predict(Cls(**params), X_full, y_deg, cv=loo)
        pred_koc_21 = cross_val_predict(Cls(**params), X_full, y_koc, cv=loo)

        results[f"{name}_17f_deg_r2"] = round(float(r2_score(y_deg, pred_deg_17)), 4)
        results[f"{name}_17f_koc_r2"] = round(float(r2_score(y_koc, pred_koc_17)), 4)
        results[f"{name}_21f_deg_r2"] = round(float(r2_score(y_deg, pred_deg_21)), 4)
        results[f"{name}_21f_koc_r2"] = round(float(r2_score(y_koc, pred_koc_21)), 4)
        results[f"{name}_delta_deg"] = round(results[f"{name}_21f_deg_r2"] - results[f"{name}_17f_deg_r2"], 4)
        results[f"{name}_delta_koc"] = round(results[f"{name}_21f_koc_r2"] - results[f"{name}_17f_koc_r2"], 4)

        print(f"  {name}: DegT50 17f={results[f'{name}_17f_deg_r2']:.3f} → 21f={results[f'{name}_21f_deg_r2']:.3f} "
              f"(Δ={results[f'{name}_delta_deg']:+.3f})")

    results["elapsed_seconds"] = round(time.time() - t0, 1)
    save_result("exp2_17feature_baseline", results)
    return results


# ═══════════════════════════════════════════════════════════════════
# Experiment 3: Bioaccessibility ablation for DegT50 (H3)
# ═══════════════════════════════════════════════════════════════════
def exp3_bioaccessibility_ablation():
    print("\n◈ Exp 3: Bioaccessibility ablation for DegT50 (H3)...")
    t0 = time.time()

    from backend.quantum_predictor import extract_features, FEATURE_NAMES
    from backend.spin_database import SUBSTANCES
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import cross_val_predict, LeaveOneOut
    from sklearn.metrics import r2_score

    X = np.array([extract_features(s) for s in SUBSTANCES])
    y_deg = np.array([np.log10(max(s["degT50_soil"], 0.1)) for s in SUBSTANCES])

    bio_idx = FEATURE_NAMES.index("bioaccessibility")
    mask_no_bio = [i for i in range(len(FEATURE_NAMES)) if i != bio_idx]
    X_no_bio = X[:, mask_no_bio]

    loo = LeaveOneOut()
    rf_params = {"n_estimators": 200, "max_depth": 10, "random_state": 42}

    pred_with = cross_val_predict(RandomForestRegressor(**rf_params), X, y_deg, cv=loo)
    pred_without = cross_val_predict(RandomForestRegressor(**rf_params), X_no_bio, y_deg, cv=loo)

    r2_with = round(float(r2_score(y_deg, pred_with)), 4)
    r2_without = round(float(r2_score(y_deg, pred_without)), 4)

    results = {
        "experiment": "H3_bioaccessibility_ablation_degtl50",
        "RF_deg_r2_with_bioaccessibility": r2_with,
        "RF_deg_r2_without_bioaccessibility": r2_without,
        "delta_r2": round(r2_with - r2_without, 4),
        "bioaccessibility_index": bio_idx,
        "elapsed_seconds": round(time.time() - t0, 1),
    }
    save_result("exp3_bioaccessibility_ablation", results)
    print(f"  RF DegT50: with B={r2_with:.3f}, without B={r2_without:.3f} (Δ={r2_with-r2_without:+.3f})")
    return results


# ═══════════════════════════════════════════════════════════════════
# Experiment 4: 8-4 MLP baseline (M2)
# ═══════════════════════════════════════════════════════════════════
def exp4_mlp_baseline():
    print("\n◈ Exp 4: 8-4 MLP vs 64-32 MLP baseline (M2)...")
    t0 = time.time()

    from backend.quantum_predictor import extract_features
    from backend.spin_database import SUBSTANCES
    from sklearn.neural_network import MLPRegressor
    from sklearn.model_selection import cross_val_predict, LeaveOneOut
    from sklearn.metrics import r2_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline

    X = np.array([extract_features(s) for s in SUBSTANCES])
    y_deg = np.array([np.log10(max(s["degT50_soil"], 0.1)) for s in SUBSTANCES])
    y_koc = np.array([np.log10(max(s["koc"], 0.1)) for s in SUBSTANCES])

    loo = LeaveOneOut()
    results = {"experiment": "M2_mlp_capacity_comparison"}

    for arch_name, hidden in [("MLP_8_4", (8, 4)), ("MLP_64_32", (64, 32))]:
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("mlp", MLPRegressor(hidden_layer_sizes=hidden, max_iter=2000,
                                 random_state=42, early_stopping=True,
                                 validation_fraction=0.15, n_iter_no_change=20))
        ])
        pred_deg = cross_val_predict(pipe, X, y_deg, cv=loo)
        pred_koc = cross_val_predict(pipe, X, y_koc, cv=loo)

        results[f"{arch_name}_deg_r2"] = round(float(r2_score(y_deg, pred_deg)), 4)
        results[f"{arch_name}_koc_r2"] = round(float(r2_score(y_koc, pred_koc)), 4)
        n_params = X.shape[1] * hidden[0] + hidden[0] + hidden[0] * hidden[1] + hidden[1] + hidden[1] + 1
        results[f"{arch_name}_params"] = n_params
        results[f"{arch_name}_params_per_sample"] = round(n_params / len(SUBSTANCES), 2)

        print(f"  {arch_name} ({n_params} params): DegT50 R²={results[f'{arch_name}_deg_r2']:.3f}, "
              f"Koc R²={results[f'{arch_name}_koc_r2']:.3f}")

    results["elapsed_seconds"] = round(time.time() - t0, 1)
    save_result("exp4_mlp_baseline", results)
    return results


# ═══════════════════════════════════════════════════════════════════
# Experiment 5: Sabljic null model for Koc
# ═══════════════════════════════════════════════════════════════════
def exp5_sabljic_null_model():
    print("\n◈ Exp 5: Sabljic null model — log Koc = 0.81 log Kow + 0.10...")
    t0 = time.time()

    from backend.quantum_predictor import extract_features, FEATURE_NAMES
    from backend.spin_database import SUBSTANCES
    from sklearn.metrics import r2_score, mean_absolute_error

    logP_idx = FEATURE_NAMES.index("logP")

    y_koc = np.array([np.log10(max(s["koc"], 0.1)) for s in SUBSTANCES])
    X = np.array([extract_features(s) for s in SUBSTANCES])
    logP_values = X[:, logP_idx]

    # Sabljic (1995): log Koc = 0.81 * log Kow + 0.10
    pred_koc_sabljic = 0.81 * logP_values + 0.10

    r2 = round(float(r2_score(y_koc, pred_koc_sabljic)), 4)
    mae = round(float(mean_absolute_error(y_koc, pred_koc_sabljic)), 4)

    results = {
        "experiment": "sabljic_null_model_koc",
        "formula": "log_Koc = 0.81 * log_Kow + 0.10",
        "reference": "Sabljic et al. 1995, Chemosphere 31:4489",
        "r2_koc": r2,
        "mae_koc": mae,
        "n_substances": len(SUBSTANCES),
        "elapsed_seconds": round(time.time() - t0, 1),
    }
    save_result("exp5_sabljic_null_model", results)
    print(f"  Sabljic Koc R²={r2:.3f}, MAE={mae:.3f} (log10 scale)")
    return results


# ═══════════════════════════════════════════════════════════════════
# Experiment 6: Gradient variance at VQC init (H7)
# ═══════════════════════════════════════════════════════════════════
def exp6_gradient_variance():
    print("\n◈ Exp 6: Gradient variance at random init (H7 — barren plateau test)...")
    t0 = time.time()

    import pennylane as qml
    from pennylane import numpy as pnp
    from backend.quantum_predictor import (
        extract_features, QML_DEG_FEATURE_INDICES,
        N_QUBITS_DEG, N_LAYERS_DEG, quantum_circuit_deg, circuit_predict
    )
    from backend.spin_database import SUBSTANCES

    # Prepare features
    features_deg = [extract_features(s)[QML_DEG_FEATURE_INDICES] for s in SUBSTANCES]
    targets_deg = [pnp.array(np.log10(max(s["degT50_soil"], 0.1)), requires_grad=False) for s in SUBSTANCES]

    n_seeds = 100
    gradient_norms = []

    for seed in range(n_seeds):
        np.random.seed(seed)
        weights = pnp.array(
            np.random.uniform(-0.5, 0.5, (N_LAYERS_DEG, N_QUBITS_DEG, 3)),
            requires_grad=True
        )
        readout = pnp.array(
            np.random.uniform(-0.5, 0.5, N_QUBITS_DEG + 1),
            requires_grad=True
        )

        # Compute cost on a small subset (first 10 substances for speed)
        def cost(w, r):
            total = pnp.array(0.0)
            for feat, target in zip(features_deg[:10], targets_deg[:10]):
                pred = circuit_predict(feat, w, r, quantum_circuit_deg, N_QUBITS_DEG)
                total = total + (pred - target) ** 2
            return total / 10

        grad_fn = qml.grad(cost, argnum=[0, 1])
        grads = grad_fn(weights, readout)
        grad_norm = float(np.sqrt(sum(np.sum(np.array(g) ** 2) for g in grads)))
        gradient_norms.append(grad_norm)

        if (seed + 1) % 20 == 0:
            print(f"  Seed {seed+1}/{n_seeds}, grad_norm={grad_norm:.4f}")

    grad_array = np.array(gradient_norms)
    results = {
        "experiment": "H7_gradient_variance_at_init",
        "n_seeds": n_seeds,
        "n_qubits": N_QUBITS_DEG,
        "n_layers": N_LAYERS_DEG,
        "n_substances_sampled": 10,
        "grad_norm_mean": round(float(np.mean(grad_array)), 6),
        "grad_norm_std": round(float(np.std(grad_array)), 6),
        "grad_norm_min": round(float(np.min(grad_array)), 6),
        "grad_norm_max": round(float(np.max(grad_array)), 6),
        "grad_norm_median": round(float(np.median(grad_array)), 6),
        "variance": round(float(np.var(grad_array)), 8),
        "barren_plateau_likely": bool(np.var(grad_array) < 1e-3),
        "interpretation": "",
        "elapsed_seconds": round(time.time() - t0, 1),
    }

    if results["variance"] > 1e-3:
        results["interpretation"] = (
            f"Var[||∇L||] = {results['variance']:.6f} > 10⁻³ → "
            "barren plateau is NOT the bottleneck at this circuit size. "
            "The VQC's poor performance is likely due to data/feature limitations, not trainability."
        )
    else:
        results["interpretation"] = (
            f"Var[||∇L||] = {results['variance']:.6f} < 10⁻³ → "
            "gradient variance is low, consistent with a barren plateau. "
            "Circuit expressivity may be limited."
        )

    save_result("exp6_gradient_variance", results)
    print(f"  Grad variance: {results['variance']:.6f} — {results['interpretation'][:80]}")
    return results


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 70)
    print("QP-FATE Review Micro-Experiments")
    print(f"Host: {os.uname().nodename} | Python: {sys.version.split()[0]}")
    print(f"Results dir: {RESULTS_DIR}")
    print("=" * 70)

    t_start = time.time()

    results_all = {}
    try:
        results_all["exp1"] = exp1_regenerate_classical_baseline()
    except Exception as e:
        print(f"  ✗ Exp 1 failed: {e}")

    try:
        results_all["exp2"] = exp2_17feature_baseline()
    except Exception as e:
        print(f"  ✗ Exp 2 failed: {e}")

    try:
        results_all["exp3"] = exp3_bioaccessibility_ablation()
    except Exception as e:
        print(f"  ✗ Exp 3 failed: {e}")

    try:
        results_all["exp4"] = exp4_mlp_baseline()
    except Exception as e:
        print(f"  ✗ Exp 4 failed: {e}")

    try:
        results_all["exp5"] = exp5_sabljic_null_model()
    except Exception as e:
        print(f"  ✗ Exp 5 failed: {e}")

    try:
        results_all["exp6"] = exp6_gradient_variance()
    except Exception as e:
        print(f"  ✗ Exp 6 failed: {e}")

    total = time.time() - t_start
    print(f"\n{'=' * 70}")
    print(f"All micro-experiments complete in {total:.1f}s ({total/60:.1f} min)")
    save_result("all_micro_experiments", {
        "total_seconds": round(total, 1),
        "experiments": list(results_all.keys()),
        "host": os.uname().nodename,
    })
