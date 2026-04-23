#!/usr/bin/env python3
"""
QP-FATE Review Heavy Experiments — laptop32 runner
====================================================
Runs the compute-heavy experiments (~23 hours total):
  1. Seed ×5 architecture sweep (Variants A–D) (~15h)
  2. Leave-one-class-out grouped CV for RF/GB (~0.5h)
  3. Binary P/vP classification (pesticide-fate recommendation)

Run: ssh laptop32 'cd ~/Projects/Chemistry/Quantum\ Chemistry/Quantum\ Pesticide\ Fate\ Modeling && source .venv/bin/activate && nohup python3 scripts/run_heavy_experiments.py > heavy_experiments.log 2>&1 &'
"""
import sys
import os
import json
import time
import numpy as np

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
# Experiment 1: Seed ×5 architecture sweep (~15h)
# ═══════════════════════════════════════════════════════════════════
def exp1_seed_sweep():
    print("\n◈ Exp 1: Seed ×5 architecture sweep (Variants A–D)...")
    import pennylane as qml
    from pennylane import numpy as pnp
    from backend.quantum_predictor import (
        extract_features, QML_DEG_FEATURE_INDICES,
        _train_model, circuit_predict,
        N_QUBITS_DEG, N_QUBITS_KOC
    )
    from backend.spin_database import SUBSTANCES
    from sklearn.model_selection import KFold
    from sklearn.metrics import r2_score

    n = len(SUBSTANCES)
    all_features = [extract_features(s) for s in SUBSTANCES]
    all_features_deg = [f[QML_DEG_FEATURE_INDICES] for f in all_features]
    y_deg = np.array([np.log10(max(s["degT50_soil"], 0.1)) for s in SUBSTANCES])

    seeds = [0, 1, 7, 42, 2024]

    # Variant configs from EXPERIMENT_RESULTS.md
    variants = {
        "A_shallow_wide": {"n_qubits": 12, "n_layers": 3, "n_epochs": 80, "lr": 0.03,
                           "use_deg_features": False},
        "B_deep_narrow": {"n_qubits": 8, "n_layers": 12, "n_epochs": 100, "lr": 0.02,
                          "use_deg_features": True},
        "C_hw_efficient": {"n_qubits": 12, "n_layers": 5, "n_epochs": 60, "lr": 0.04,
                           "use_deg_features": False},
        "D_baseline_plus": {"n_qubits": 12, "n_layers": 8, "n_epochs": 120, "lr": 0.03,
                            "use_deg_features": False},
    }

    all_results = {}

    for var_name, config in variants.items():
        print(f"\n  ── Variant {var_name} ──")
        nq = config["n_qubits"]
        nl = config["n_layers"]

        # Create the circuit for this variant
        dev = qml.device("default.qubit", wires=nq)
        from backend.quantum_predictor import _build_circuit_body

        @qml.qnode(dev, interface="autograd")
        def var_circuit(features, weights):
            return _build_circuit_body(features, weights, nq, nl)

        seed_results = []
        for seed in seeds:
            t0 = time.time()
            print(f"    Seed {seed}...", end=" ", flush=True)

            # 5-fold CV
            kf = KFold(n_splits=5, shuffle=True, random_state=seed)
            preds = np.zeros(n)

            for fold_idx, (train_idx, test_idx) in enumerate(kf.split(range(n))):
                if config["use_deg_features"]:
                    train_feat = [all_features_deg[i] for i in train_idx]
                else:
                    train_feat = [all_features[i] for i in train_idx]

                train_targets = [pnp.array(y_deg[i], requires_grad=False) for i in train_idx]

                w, r, loss = _train_model(
                    train_feat, train_targets,
                    n_epochs=config["n_epochs"], lr=config["lr"],
                    n_qubits=nq, n_layers=nl,
                    circuit_fn=var_circuit, seed=seed
                )

                for i in test_idx:
                    feat = all_features_deg[i] if config["use_deg_features"] else all_features[i]
                    preds[i] = float(circuit_predict(feat, w, r, var_circuit, nq))

            r2 = round(float(r2_score(y_deg, preds)), 4)
            elapsed = round(time.time() - t0, 1)
            seed_results.append({"seed": seed, "r2": r2, "elapsed_s": elapsed})
            print(f"R²={r2:+.4f} ({elapsed}s)")

        r2_values = [sr["r2"] for sr in seed_results]
        all_results[var_name] = {
            "config": config,
            "seed_results": seed_results,
            "r2_mean": round(float(np.mean(r2_values)), 4),
            "r2_std": round(float(np.std(r2_values)), 4),
            "r2_min": round(float(np.min(r2_values)), 4),
            "r2_max": round(float(np.max(r2_values)), 4),
        }
        print(f"    → Mean R²={all_results[var_name]['r2_mean']:+.4f} ± {all_results[var_name]['r2_std']:.4f}")
        save_result(f"exp1_seed_sweep_{var_name}", all_results[var_name])

    save_result("exp1_seed_sweep_all", all_results)
    return all_results


# ═══════════════════════════════════════════════════════════════════
# Experiment 2: Leave-one-class-out grouped CV (~30 min)
# ═══════════════════════════════════════════════════════════════════
def exp2_grouped_cv():
    print("\n◈ Exp 2: Leave-one-class-out grouped CV for RF/GB (H10)...")
    t0 = time.time()

    from backend.quantum_predictor import extract_features
    from backend.spin_database import SUBSTANCES
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.metrics import r2_score
    from collections import defaultdict

    X = np.array([extract_features(s) for s in SUBSTANCES])
    y_deg = np.array([np.log10(max(s["degT50_soil"], 0.1)) for s in SUBSTANCES])
    y_koc = np.array([np.log10(max(s["koc"], 0.1)) for s in SUBSTANCES])

    # Build class groups
    class_to_indices = defaultdict(list)
    for i, s in enumerate(SUBSTANCES):
        cls = s.get("cls", s.get("chemical_class", s.get("class", "unknown")))
        class_to_indices[cls].append(i)

    classes = sorted(class_to_indices.keys())
    print(f"  {len(classes)} chemical classes, {len(SUBSTANCES)} substances")

    results = {"experiment": "H10_leave_one_class_out_CV", "n_classes": len(classes)}
    per_class = []

    for model_name, Cls, params in [
        ("RF", RandomForestRegressor, {"n_estimators": 200, "max_depth": 10, "random_state": 42}),
        ("GB", GradientBoostingRegressor, {"n_estimators": 200, "max_depth": 4, "learning_rate": 0.1,
                                            "random_state": 42}),
    ]:
        preds_deg = np.zeros(len(SUBSTANCES))
        preds_koc = np.zeros(len(SUBSTANCES))

        for cls_name in classes:
            test_idx = class_to_indices[cls_name]
            train_idx = [i for i in range(len(SUBSTANCES)) if i not in test_idx]

            if len(train_idx) < 5:
                # Skip tiny classes — assign mean as prediction
                preds_deg[test_idx] = np.mean(y_deg[train_idx]) if train_idx else np.mean(y_deg)
                preds_koc[test_idx] = np.mean(y_koc[train_idx]) if train_idx else np.mean(y_koc)
                continue

            model_deg = Cls(**params)
            model_deg.fit(X[train_idx], y_deg[train_idx])
            preds_deg[test_idx] = model_deg.predict(X[test_idx])

            model_koc = Cls(**params)
            model_koc.fit(X[train_idx], y_koc[train_idx])
            preds_koc[test_idx] = model_koc.predict(X[test_idx])

        r2_deg = round(float(r2_score(y_deg, preds_deg)), 4)
        r2_koc = round(float(r2_score(y_koc, preds_koc)), 4)

        results[f"{model_name}_grouped_deg_r2"] = r2_deg
        results[f"{model_name}_grouped_koc_r2"] = r2_koc
        print(f"  {model_name} grouped-CV: DegT50 R²={r2_deg:.3f}, Koc R²={r2_koc:.3f}")

    # Compare with standard LOO
    from sklearn.model_selection import cross_val_predict, LeaveOneOut
    loo = LeaveOneOut()
    rf = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
    pred_deg_loo = cross_val_predict(rf, X, y_deg, cv=loo)
    pred_koc_loo = cross_val_predict(rf, X, y_koc, cv=loo)
    results["RF_loo_deg_r2"] = round(float(r2_score(y_deg, pred_deg_loo)), 4)
    results["RF_loo_koc_r2"] = round(float(r2_score(y_koc, pred_koc_loo)), 4)
    results["RF_deg_drop"] = round(results["RF_loo_deg_r2"] - results["RF_grouped_deg_r2"], 4)
    results["RF_koc_drop"] = round(results["RF_loo_koc_r2"] - results["RF_grouped_koc_r2"], 4)
    results["elapsed_seconds"] = round(time.time() - t0, 1)
    results["class_sizes"] = {k: len(v) for k, v in sorted(class_to_indices.items())}

    save_result("exp2_grouped_cv", results)
    print(f"  RF drop LOO→grouped: DegT50 Δ={results['RF_deg_drop']:+.3f}, Koc Δ={results['RF_koc_drop']:+.3f}")
    return results


# ═══════════════════════════════════════════════════════════════════
# Experiment 3: Binary P/vP classification
# ═══════════════════════════════════════════════════════════════════
def exp3_binary_classification():
    print("\n◈ Exp 3: Binary P/vP persistence classification...")
    t0 = time.time()

    from backend.quantum_predictor import extract_features
    from backend.spin_database import SUBSTANCES
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import cross_val_predict, LeaveOneOut
    from sklearn.metrics import balanced_accuracy_score, matthews_corrcoef, confusion_matrix

    X = np.array([extract_features(s) for s in SUBSTANCES])
    degt50 = np.array([s["degT50_soil"] for s in SUBSTANCES])

    # P threshold (REACH Annex XIII): DT50 > 60 days
    y_P = (degt50 > 60).astype(int)
    # vP threshold: DT50 > 180 days
    y_vP = (degt50 > 180).astype(int)

    loo = LeaveOneOut()
    results = {
        "experiment": "binary_persistence_classification",
        "P_threshold_days": 60,
        "vP_threshold_days": 180,
        "n_P": int(y_P.sum()),
        "n_non_P": int((1 - y_P).sum()),
        "n_vP": int(y_vP.sum()),
        "n_non_vP": int((1 - y_vP).sum()),
    }

    for target_name, y_true in [("P_60d", y_P), ("vP_180d", y_vP)]:
        for model_name, Cls, params in [
            ("RF", RandomForestClassifier, {"n_estimators": 200, "max_depth": 10, "random_state": 42}),
            ("GB", GradientBoostingClassifier, {"n_estimators": 200, "max_depth": 4,
                                                 "learning_rate": 0.1, "random_state": 42}),
        ]:
            pred = cross_val_predict(Cls(**params), X, y_true, cv=loo)
            ba = round(float(balanced_accuracy_score(y_true, pred)), 4)
            mcc = round(float(matthews_corrcoef(y_true, pred)), 4)
            cm = confusion_matrix(y_true, pred).tolist()

            results[f"{model_name}_{target_name}_balanced_acc"] = ba
            results[f"{model_name}_{target_name}_mcc"] = mcc
            results[f"{model_name}_{target_name}_confusion"] = cm
            print(f"  {model_name} {target_name}: BA={ba:.3f}, MCC={mcc:.3f}")

    results["elapsed_seconds"] = round(time.time() - t0, 1)
    save_result("exp3_binary_classification", results)
    return results


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 70)
    print("QP-FATE Review Heavy Experiments")
    print(f"Host: {os.uname().nodename} | Python: {sys.version.split()[0]}")
    print(f"Results dir: {RESULTS_DIR}")
    print("=" * 70)

    t_start = time.time()

    # Run fast experiments first
    try:
        exp2_grouped_cv()
    except Exception as e:
        print(f"  ✗ Grouped CV failed: {e}")
        import traceback; traceback.print_exc()

    try:
        exp3_binary_classification()
    except Exception as e:
        print(f"  ✗ Binary classification failed: {e}")
        import traceback; traceback.print_exc()

    # Run the expensive one last
    try:
        exp1_seed_sweep()
    except Exception as e:
        print(f"  ✗ Seed sweep failed: {e}")
        import traceback; traceback.print_exc()

    total = time.time() - t_start
    print(f"\n{'=' * 70}")
    print(f"All heavy experiments complete in {total:.1f}s ({total/3600:.1f}h)")
    save_result("all_heavy_experiments", {
        "total_seconds": round(total, 1),
        "host": os.uname().nodename,
    })
