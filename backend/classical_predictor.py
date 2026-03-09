"""
Classical ML Baseline — Random Forest & Gradient Boosting
==========================================================
Provides a classical machine learning baseline for direct comparison
with the quantum ML predictions. Uses the exact same 12 molecular
descriptor features as the quantum circuit.

This module trains instantly (<1 sec) and serves as the benchmark
that the quantum model must beat to claim quantum advantage.
"""

import numpy as np
import json
import os
import hashlib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import cross_val_predict, LeaveOneOut, KFold
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# Reuse the same feature extractor as the quantum model
from backend.quantum_predictor import extract_features, FEATURE_NAMES, N_QUBITS
from backend.spin_database import SUBSTANCES

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".qml_cache")
CL_CACHE_FILE = os.path.join(CACHE_DIR, "classical_baseline.json")


def _compute_db_hash():
    """Same hash as quantum predictor for cache consistency."""
    data_str = json.dumps(
        [{k: v for k, v in s.items() if k != "smiles"} for s in SUBSTANCES],
        sort_keys=True, default=str
    )
    return hashlib.sha256(data_str.encode()).hexdigest()[:16]


def _prepare_data():
    """Extract features and targets for all substances."""
    X = np.array([extract_features(s) for s in SUBSTANCES])
    y_deg = np.array([np.log10(max(s["degT50_soil"], 0.1)) for s in SUBSTANCES])
    y_koc = np.array([np.log10(max(s["koc"], 0.1)) for s in SUBSTANCES])
    names = [s["name"] for s in SUBSTANCES]
    return X, y_deg, y_koc, names


def train_classical_baseline():
    """
    Train RandomForest + GradientBoosting baselines and run
    leave-one-out and 5-fold cross-validation.

    Returns dict with R², MAE, RMSE for both models and both properties.
    Also computes Koc results WITHOUT the bioaccessibility feature (index 14)
    to address circularity: B = log10(S/Koc) uses measured Koc as input.
    Cached to disk — trains in <2 seconds.
    """
    # Check cache
    if os.path.exists(CL_CACHE_FILE):
        with open(CL_CACHE_FILE, "r") as f:
            cached = json.load(f)
        if cached.get("db_hash") == _compute_db_hash() and "koc_no_bioaccessibility" in cached:
            print("[Classical ML] Loaded cached baseline results")
            return cached

    print("[Classical ML] Training classical baselines...")
    X, y_deg, y_koc, names = _prepare_data()
    n = len(SUBSTANCES)

    # Feature set without bioaccessibility (index 14) for fair Koc evaluation
    BIOACCESSIBILITY_IDX = FEATURE_NAMES.index("bioaccessibility")
    feature_mask_no_B = [i for i in range(len(FEATURE_NAMES)) if i != BIOACCESSIBILITY_IDX]
    X_no_B = X[:, feature_mask_no_B]
    feature_names_no_B = [FEATURE_NAMES[i] for i in feature_mask_no_B]
    print(f"  Bioaccessibility feature at index {BIOACCESSIBILITY_IDX} — "
          f"excluded for Koc circularity fix ({len(feature_names_no_B)} features)")

    results = {}
    koc_no_B_results = {}

    for model_name, ModelClass, params in [
        ("Ridge", Ridge, {"alpha": 1.0}),
        ("Lasso", Lasso, {"alpha": 0.1, "max_iter": 10000}),
        ("RandomForest", RandomForestRegressor, {"n_estimators": 200, "max_depth": 10, "random_state": 42}),
        ("GradientBoosting", GradientBoostingRegressor, {"n_estimators": 200, "max_depth": 4, "learning_rate": 0.1, "random_state": 42}),
    ]:
        model_results = {}
        model_koc_no_B = {}

        for cv_name, cv_obj in [("loo", LeaveOneOut()), ("5fold", KFold(n_splits=5, shuffle=True, random_state=42))]:
            # DegT50 (all 17 features — no circularity)
            model_deg = ModelClass(**params)
            pred_deg = cross_val_predict(model_deg, X, y_deg, cv=cv_obj)

            # Koc WITH bioaccessibility (original, for comparison)
            model_koc = ModelClass(**params)
            pred_koc = cross_val_predict(model_koc, X, y_koc, cv=cv_obj)

            # Koc WITHOUT bioaccessibility (fair evaluation)
            model_koc_fair = ModelClass(**params)
            pred_koc_fair = cross_val_predict(model_koc_fair, X_no_B, y_koc, cv=cv_obj)

            # Per-substance results (with original Koc)
            substance_results = []
            for i in range(n):
                substance_results.append({
                    "name": names[i],
                    "deg_exp": round(float(y_deg[i]), 3),
                    "deg_pred": round(float(pred_deg[i]), 3),
                    "deg_exp_days": SUBSTANCES[i]["degT50_soil"],
                    "deg_pred_days": round(float(10 ** pred_deg[i]), 1),
                    "koc_exp": round(float(y_koc[i]), 3),
                    "koc_pred": round(float(pred_koc[i]), 3),
                    "koc_pred_no_B": round(float(pred_koc_fair[i]), 3),
                    "koc_exp_val": SUBSTANCES[i]["koc"],
                    "koc_pred_val": round(float(10 ** pred_koc[i]), 1),
                    "koc_pred_val_no_B": round(float(10 ** pred_koc_fair[i]), 1),
                })

            model_results[cv_name] = {
                "cv_type": "leave-one-out" if cv_name == "loo" else "5-fold",
                "n_folds": n if cv_name == "loo" else 5,
                "results": substance_results,
                "deg_r2": round(float(r2_score(y_deg, pred_deg)), 4),
                "deg_mae": round(float(mean_absolute_error(y_deg, pred_deg)), 4),
                "deg_rmse": round(float(np.sqrt(mean_squared_error(y_deg, pred_deg))), 4),
                "koc_r2": round(float(r2_score(y_koc, pred_koc)), 4),
                "koc_mae": round(float(mean_absolute_error(y_koc, pred_koc)), 4),
                "koc_rmse": round(float(np.sqrt(mean_squared_error(y_koc, pred_koc))), 4),
            }

            # Koc without B metrics
            model_koc_no_B[cv_name] = {
                "cv_type": "leave-one-out" if cv_name == "loo" else "5-fold",
                "koc_r2": round(float(r2_score(y_koc, pred_koc_fair)), 4),
                "koc_mae": round(float(mean_absolute_error(y_koc, pred_koc_fair)), 4),
                "koc_rmse": round(float(np.sqrt(mean_squared_error(y_koc, pred_koc_fair))), 4),
            }

            print(f"  {model_name} ({cv_name}): DegT50 R²={model_results[cv_name]['deg_r2']:.3f}, "
                  f"Koc R²={model_results[cv_name]['koc_r2']:.3f} "
                  f"(no B: {model_koc_no_B[cv_name]['koc_r2']:.3f})")

        results[model_name] = model_results
        koc_no_B_results[model_name] = model_koc_no_B

    # Feature importances from full-data RF
    rf_full = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
    rf_full.fit(X, y_deg)
    deg_importances = {FEATURE_NAMES[i]: round(float(v), 4)
                       for i, v in enumerate(rf_full.feature_importances_)}

    rf_full.fit(X, y_koc)
    koc_importances = {FEATURE_NAMES[i]: round(float(v), 4)
                       for i, v in enumerate(rf_full.feature_importances_)}

    # Feature importances for Koc WITHOUT bioaccessibility
    rf_no_B = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
    rf_no_B.fit(X_no_B, y_koc)
    koc_importances_no_B = {feature_names_no_B[i]: round(float(v), 4)
                            for i, v in enumerate(rf_no_B.feature_importances_)}

    output = {
        "n_substances": n,
        "n_features": len(FEATURE_NAMES),
        "feature_names": FEATURE_NAMES,
        "models": results,
        "koc_no_bioaccessibility": koc_no_B_results,
        "feature_importances": {
            "deg": deg_importances,
            "koc": koc_importances,
            "koc_no_B": koc_importances_no_B,
        },
        "db_hash": _compute_db_hash(),
    }

    # Cache
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(CL_CACHE_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print("[Classical ML] Baseline complete and cached!")

    return output
