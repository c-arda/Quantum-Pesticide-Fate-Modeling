#!/usr/bin/env python3
"""
Compute confidence intervals for all R² values in the QP-FATE manuscript.

Methods:
  - 5-fold CV: per-fold R² → report mean ± std
  - LOO-CV: bootstrap resampling (1000 draws) → 95% CI
  - VQC 5-fold: per-fold R² from cached results

Run from project root:
  .venv/bin/python manuscript/compute_confidence_intervals.py
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import KFold, LeaveOneOut
from sklearn.metrics import r2_score

from backend.quantum_predictor import extract_features, FEATURE_NAMES
from backend.spin_database import SUBSTANCES

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "backend", ".qml_cache")
CI_CACHE = os.path.join(CACHE_DIR, "confidence_intervals.json")


def _prepare_data():
    X = np.array([extract_features(s) for s in SUBSTANCES])
    y_deg = np.array([np.log10(max(s["degT50_soil"], 0.1)) for s in SUBSTANCES])
    y_koc = np.array([np.log10(max(s["koc"], 0.1)) for s in SUBSTANCES])
    return X, y_deg, y_koc


def _r2(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - ss_res / max(ss_tot, 1e-10)


# ── 5-fold CV: per-fold R² ────────────────────────────────────────
def compute_5fold_ci(X, y_deg, y_koc):
    """Compute per-fold R² and report mean ± std for classical models."""
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    results = {}

    for name, Model, params in [
        ("RF", RandomForestRegressor, {"n_estimators": 200, "max_depth": 10, "random_state": 42}),
        ("GB", GradientBoostingRegressor, {"n_estimators": 200, "max_depth": 4, "learning_rate": 0.1, "random_state": 42}),
    ]:
        fold_r2_deg = []
        fold_r2_koc = []

        for train_idx, test_idx in kf.split(X):
            X_train, X_test = X[train_idx], X[test_idx]

            # DegT50
            model = Model(**params)
            model.fit(X_train, y_deg[train_idx])
            pred = model.predict(X_test)
            fold_r2_deg.append(_r2(y_deg[test_idx], pred))

            # Koc
            model = Model(**params)
            model.fit(X_train, y_koc[train_idx])
            pred = model.predict(X_test)
            fold_r2_koc.append(_r2(y_koc[test_idx], pred))

        results[name] = {
            "deg_fold_r2": [round(v, 4) for v in fold_r2_deg],
            "deg_mean": round(np.mean(fold_r2_deg), 4),
            "deg_std": round(np.std(fold_r2_deg), 4),
            "koc_fold_r2": [round(v, 4) for v in fold_r2_koc],
            "koc_mean": round(np.mean(fold_r2_koc), 4),
            "koc_std": round(np.std(fold_r2_koc), 4),
        }
        print(f"  {name} 5-fold: DegT50 R² = {results[name]['deg_mean']:.3f} ± {results[name]['deg_std']:.3f}")
        print(f"              Koc    R² = {results[name]['koc_mean']:.3f} ± {results[name]['koc_std']:.3f}")

    return results


# ── LOO-CV: bootstrap CI ─────────────────────────────────────────
def compute_loo_bootstrap_ci(X, y_deg, y_koc, n_bootstrap=1000):
    """Bootstrap 95% CI on LOO-CV R² from per-substance residuals."""
    results = {}

    for name, Model, params in [
        ("RF", RandomForestRegressor, {"n_estimators": 200, "max_depth": 10, "random_state": 42}),
        ("GB", GradientBoostingRegressor, {"n_estimators": 200, "max_depth": 4, "learning_rate": 0.1, "random_state": 42}),
    ]:
        loo = LeaveOneOut()
        n = len(y_deg)

        # Collect per-substance predictions
        pred_deg = np.zeros(n)
        pred_koc = np.zeros(n)

        for train_idx, test_idx in loo.split(X):
            i = test_idx[0]
            model = Model(**params)
            model.fit(X[train_idx], y_deg[train_idx])
            pred_deg[i] = model.predict(X[test_idx])[0]

            model = Model(**params)
            model.fit(X[train_idx], y_koc[train_idx])
            pred_koc[i] = model.predict(X[test_idx])[0]

        # Full R²
        full_r2_deg = _r2(y_deg, pred_deg)
        full_r2_koc = _r2(y_koc, pred_koc)

        # Bootstrap R²
        rng = np.random.RandomState(42)
        boot_r2_deg = []
        boot_r2_koc = []

        for _ in range(n_bootstrap):
            idx = rng.choice(n, n, replace=True)
            boot_r2_deg.append(_r2(y_deg[idx], pred_deg[idx]))
            boot_r2_koc.append(_r2(y_koc[idx], pred_koc[idx]))

        boot_r2_deg = np.array(boot_r2_deg)
        boot_r2_koc = np.array(boot_r2_koc)

        results[name] = {
            "deg_r2": round(full_r2_deg, 4),
            "deg_ci_lo": round(np.percentile(boot_r2_deg, 2.5), 4),
            "deg_ci_hi": round(np.percentile(boot_r2_deg, 97.5), 4),
            "koc_r2": round(full_r2_koc, 4),
            "koc_ci_lo": round(np.percentile(boot_r2_koc, 2.5), 4),
            "koc_ci_hi": round(np.percentile(boot_r2_koc, 97.5), 4),
        }
        print(f"  {name} LOO: DegT50 R² = {full_r2_deg:.3f} "
              f"[{results[name]['deg_ci_lo']:.3f}, {results[name]['deg_ci_hi']:.3f}]")
        print(f"            Koc    R² = {full_r2_koc:.3f} "
              f"[{results[name]['koc_ci_lo']:.3f}, {results[name]['koc_ci_hi']:.3f}]")

    return results


# ── VQC 5-fold: per-fold R² from cached results ──────────────────
def compute_vqc_5fold_ci():
    """Compute per-fold R² from cached VQC 5-fold CV results."""
    cv_file = os.path.join(CACHE_DIR, "cv_results_k5.json")
    if not os.path.exists(cv_file):
        print("  ⚠ No VQC 5-fold cache found — skipping")
        return None

    with open(cv_file) as f:
        cv = json.load(f)

    # Check if per-substance results are available
    if "results" not in cv and "folds" in cv:
        # Only summary data available — use overall R²
        print(f"  VQC 5-fold (summary only): DegT50 R² = {cv['deg_r2']:.3f}, "
              f"Koc R² = {cv['koc_r2']:.3f}")
        return {
            "deg_r2": cv["deg_r2"],
            "koc_r2": cv["koc_r2"],
            "note": "Per-fold breakdown not available in cached results"
        }

    # Per-substance results available — compute per-fold R²
    fold_data = {}
    for r in cv["results"]:
        fold = r["fold"]
        if fold not in fold_data:
            fold_data[fold] = {"deg_exp": [], "deg_pred": [], "koc_exp": [], "koc_pred": []}
        fold_data[fold]["deg_exp"].append(r["deg_exp"])
        fold_data[fold]["deg_pred"].append(r["deg_pred"])
        fold_data[fold]["koc_exp"].append(r["koc_exp"])
        fold_data[fold]["koc_pred"].append(r["koc_pred"])

    fold_r2_deg = []
    fold_r2_koc = []
    for fold in sorted(fold_data.keys()):
        fd = fold_data[fold]
        fold_r2_deg.append(_r2(np.array(fd["deg_exp"]), np.array(fd["deg_pred"])))
        fold_r2_koc.append(_r2(np.array(fd["koc_exp"]), np.array(fd["koc_pred"])))

    result = {
        "deg_fold_r2": [round(v, 4) for v in fold_r2_deg],
        "deg_mean": round(np.mean(fold_r2_deg), 4),
        "deg_std": round(np.std(fold_r2_deg), 4),
        "koc_fold_r2": [round(v, 4) for v in fold_r2_koc],
        "koc_mean": round(np.mean(fold_r2_koc), 4),
        "koc_std": round(np.std(fold_r2_koc), 4),
    }
    print(f"  VQC 5-fold: DegT50 R² = {result['deg_mean']:.3f} ± {result['deg_std']:.3f}")
    print(f"              Koc    R² = {result['koc_mean']:.3f} ± {result['koc_std']:.3f}")
    return result


# ── Main ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Computing confidence intervals for QP-FATE manuscript...\n")

    X, y_deg, y_koc = _prepare_data()
    print(f"Dataset: {len(SUBSTANCES)} substances, {len(FEATURE_NAMES)} features\n")

    print("── 5-fold CV (per-fold R²) ──")
    fivefold = compute_5fold_ci(X, y_deg, y_koc)

    print("\n── LOO-CV (bootstrap 95% CI, 1000 draws) ──")
    loo = compute_loo_bootstrap_ci(X, y_deg, y_koc)

    print("\n── VQC 5-fold ──")
    vqc = compute_vqc_5fold_ci()

    # Save all results
    output = {
        "fivefold_classical": fivefold,
        "loo_classical": loo,
        "vqc_5fold": vqc,
    }

    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(CI_CACHE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Saved to {CI_CACHE}")

    # Print LaTeX-ready table entries
    print("\n── LaTeX-ready values ──")
    for model_key, model_label in [("RF", "Random Forest"), ("GB", "Gradient Boosting")]:
        f5 = fivefold[model_key]
        lo = loo[model_key]
        print(f"\n{model_label}:")
        print(f"  DegT50 LOO:    {lo['deg_r2']:.3f} [{lo['deg_ci_lo']:.3f}, {lo['deg_ci_hi']:.3f}]")
        print(f"  DegT50 5-fold: {f5['deg_mean']:.3f} ± {f5['deg_std']:.3f}")
        print(f"  Koc    LOO:    {lo['koc_r2']:.3f} [{lo['koc_ci_lo']:.3f}, {lo['koc_ci_hi']:.3f}]")
        print(f"  Koc    5-fold: {f5['koc_mean']:.3f} ± {f5['koc_std']:.3f}")
