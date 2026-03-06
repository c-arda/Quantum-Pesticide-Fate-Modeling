"""
Hybrid QML+RF Stacking Predictor
================================
Combines Quantum ML (for DegT50) and Random Forest (for Koc) predictions
using a learned stacking weight optimized via cross-validation.

Strategy:
  DegT50_final = α × QML + (1-α) × RF   (α optimized per property)
  Koc_final    = RF                       (RF clearly dominates)
"""

import numpy as np
import json, os, hashlib

from backend.quantum_predictor import extract_features, FEATURE_NAMES
from backend.spin_database import SUBSTANCES

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".qml_cache")
CACHE_FILE = os.path.join(CACHE_DIR, "hybrid_results.json")


def _compute_hybrid_weights():
    """
    Find optimal stacking weight α that minimizes LOO MSE for DegT50.
    Uses pre-computed QML and RF predictions from their respective caches.
    """
    # Load classical baseline
    classical_cache = os.path.join(CACHE_DIR, "classical_baseline.json")
    if not os.path.exists(classical_cache):
        return None

    with open(classical_cache) as f:
        cl_data = json.load(f)

    rf_results = cl_data["models"]["RandomForest"]["loo"]["results"]

    # Build lookup: substance name → RF predictions
    rf_pred = {}
    for r in rf_results:
        rf_pred[r["name"]] = {
            "deg_pred": r["deg_pred"],  # log10 scale
            "deg_exp": r["deg_exp"],
            "koc_pred": r["koc_pred"],
            "koc_exp": r["koc_exp"],
            "deg_pred_days": r["deg_pred_days"],
            "koc_pred_val": r.get("koc_pred_val", 10 ** r["koc_pred"]),
        }

    # Try to load QML LOO results
    qml_loo_cache = os.path.join(CACHE_DIR, "cv_results_loo.json")
    qml_5f_cache = os.path.join(CACHE_DIR, "cv_results_k5.json")

    qml_data = None
    cv_type = None
    for cache, cv in [(qml_loo_cache, "loo"), (qml_5f_cache, "5fold")]:
        if os.path.exists(cache):
            with open(cache) as f:
                qml_data = json.load(f)
            cv_type = cv
            break

    if qml_data is None:
        # No QML CV data available — return RF-only
        return {
            "alpha_deg": 0.0,
            "alpha_koc": 0.0,
            "qml_available": False,
            "rf_deg_r2": cl_data["models"]["RandomForest"]["loo"]["deg_r2"],
            "rf_koc_r2": cl_data["models"]["RandomForest"]["loo"]["koc_r2"],
            "hybrid_deg_r2": cl_data["models"]["RandomForest"]["loo"]["deg_r2"],
            "hybrid_koc_r2": cl_data["models"]["RandomForest"]["loo"]["koc_r2"],
        }

    # Build QML prediction lookup from CV results
    # LOO CV stores flat results[], K-fold also uses results[]
    qml_pred = {}
    for r in qml_data.get("results", []):
        qml_pred[r["name"]] = {
            "deg_pred": r.get("deg_pred"),
            "koc_pred": r.get("koc_pred"),
        }

    # Find common substances
    common = [name for name in rf_pred if name in qml_pred]
    if len(common) < 10:
        return {
            "alpha_deg": 0.0,
            "alpha_koc": 0.0,
            "qml_available": False,
            "note": f"Only {len(common)} common substances between QML and RF CV results",
        }

    # Grid search for optimal alpha
    best_alpha_deg = 0.0
    best_mse_deg = float("inf")
    best_alpha_koc = 0.0
    best_mse_koc = float("inf")

    for alpha in np.arange(0.0, 1.01, 0.05):
        mse_deg = 0
        mse_koc = 0
        n = 0

        for name in common:
            rf = rf_pred[name]
            qml = qml_pred[name]

            if qml["deg_pred"] is None or qml["koc_pred"] is None:
                continue

            # Blended prediction (log10 scale)
            blend_deg = alpha * qml["deg_pred"] + (1 - alpha) * rf["deg_pred"]
            blend_koc = alpha * qml["koc_pred"] + (1 - alpha) * rf["koc_pred"]

            mse_deg += (blend_deg - rf["deg_exp"]) ** 2
            mse_koc += (blend_koc - rf["koc_exp"]) ** 2
            n += 1

        if n > 0:
            mse_deg /= n
            mse_koc /= n
            if mse_deg < best_mse_deg:
                best_mse_deg = mse_deg
                best_alpha_deg = alpha
            if mse_koc < best_mse_koc:
                best_mse_koc = mse_koc
                best_alpha_koc = alpha

    # Compute R² for the hybrid model
    deg_exps = []
    deg_hyb_preds = []
    koc_exps = []
    koc_hyb_preds = []

    for name in common:
        rf = rf_pred[name]
        qml = qml_pred[name]
        if qml["deg_pred"] is None:
            continue

        deg_exps.append(rf["deg_exp"])
        deg_hyb_preds.append(
            best_alpha_deg * qml["deg_pred"] + (1 - best_alpha_deg) * rf["deg_pred"]
        )
        koc_exps.append(rf["koc_exp"])
        koc_hyb_preds.append(
            best_alpha_koc * qml["koc_pred"] + (1 - best_alpha_koc) * rf["koc_pred"]
        )

    def r2(y_true, y_pred):
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        return 1 - ss_res / max(ss_tot, 1e-10)

    return {
        "alpha_deg": round(best_alpha_deg, 2),
        "alpha_koc": round(best_alpha_koc, 2),
        "qml_available": True,
        "qml_cv_type": cv_type,
        "n_common": len(common),
        "rf_deg_r2": round(cl_data["models"]["RandomForest"]["loo"]["deg_r2"], 4),
        "rf_koc_r2": round(cl_data["models"]["RandomForest"]["loo"]["koc_r2"], 4),
        "hybrid_deg_r2": round(r2(deg_exps, deg_hyb_preds), 4),
        "hybrid_koc_r2": round(r2(koc_exps, koc_hyb_preds), 4),
        "hybrid_deg_mse": round(best_mse_deg, 4),
        "hybrid_koc_mse": round(best_mse_koc, 4),
    }


def get_hybrid_results():
    """Return cached hybrid stacking results, computing if needed."""
    os.makedirs(CACHE_DIR, exist_ok=True)

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)

    results = _compute_hybrid_weights()
    if results:
        with open(CACHE_FILE, "w") as f:
            json.dump(results, f, indent=2)

    return results
