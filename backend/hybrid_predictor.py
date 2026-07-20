"""
Hybrid QML+RF Stacking Predictor
================================
Blends Quantum ML and Random Forest predictions with a stacking weight α:

    pred_final = α × QML + (1-α) × RF     (α optimized per target)

α is optimized by NESTED leave-one-out CV: for each held-out substance i,
α is chosen by grid search (step 0.05) on the remaining N-1 substances, and
i is then predicted with that fold-specific α. This keeps the stacking
weight from ever seeing the held-out target.

The naive alternative (optimizing α on the same predictions used to score
R²) leaks the target into the weight and inflates R². Both are computed
here: the manuscript reports the nested result as the headline and the
naive one only as a cautionary comparator (§3.7, "Comparison with naive
α optimization").

Canonical artifact: .qml_cache/honest_hybrid_results.json
"""

import numpy as np
import json, os

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".qml_cache")
CACHE_FILE = os.path.join(CACHE_DIR, "honest_hybrid_results.json")

# Grid searched for α, in both the nested and the naive procedure.
ALPHA_GRID = np.arange(0.0, 1.01, 0.05)


def _r2(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - ss_res / max(ss_tot, 1e-10)


# ── Prediction loading ────────────────────────────────────────────

def _load_predictions():
    """
    Load the cached RF (LOO) and QML (CV) predictions and align them on
    substance name. Returns (arrays_by_target, n_common, qml_cv_type,
    rf_baselines) or None if the classical baseline is missing.
    """
    classical_cache = os.path.join(CACHE_DIR, "classical_baseline.json")
    if not os.path.exists(classical_cache):
        return None

    with open(classical_cache) as f:
        cl_data = json.load(f)

    rf_loo = cl_data["models"]["RandomForest"]["loo"]
    rf_pred = {r["name"]: r for r in rf_loo["results"]}

    qml_data, cv_type = None, None
    for fname, cv in [("cv_results_loo.json", "loo"), ("cv_results_k5.json", "5fold")]:
        path = os.path.join(CACHE_DIR, fname)
        if os.path.exists(path):
            with open(path) as f:
                qml_data = json.load(f)
            cv_type = cv
            break

    if qml_data is None:
        return None

    qml_pred = {r["name"]: r for r in qml_data.get("results", [])}

    common = [
        n for n in rf_pred
        if n in qml_pred
        and qml_pred[n].get("deg_pred") is not None
        and qml_pred[n].get("koc_pred") is not None
    ]
    if len(common) < 10:
        return None

    arrays = {}
    for key in ("deg", "koc"):
        arrays[key] = (
            np.array([qml_pred[n][f"{key}_pred"] for n in common], dtype=float),
            np.array([rf_pred[n][f"{key}_pred"] for n in common], dtype=float),
            np.array([rf_pred[n][f"{key}_exp"] for n in common], dtype=float),
        )

    baselines = {
        "rf_21feat_loo_deg_r2": round(rf_loo["deg_r2"], 4),
        "rf_21feat_loo_koc_r2": round(rf_loo["koc_r2"], 4),
    }
    return arrays, len(common), cv_type, baselines


def _best_alpha(q, r, y, mask=None):
    """Grid-search the α minimizing blended MSE over the (masked) set."""
    if mask is not None:
        q, r, y = q[mask], r[mask], y[mask]
    best_alpha, best_mse = 0.0, float("inf")
    for alpha in ALPHA_GRID:
        mse = np.mean((alpha * q + (1 - alpha) * r - y) ** 2)
        if mse < best_mse:
            best_mse, best_alpha = mse, alpha
    return best_alpha


# ── The two α-optimization procedures ─────────────────────────────

def _naive_alpha(q, r, y):
    """
    LEAKY: pick α on the full set, then score R² on that same set. Reported
    in the manuscript only to quantify how much the leak inflates R².
    """
    alpha = _best_alpha(q, r, y)
    return alpha, _r2(y, alpha * q + (1 - alpha) * r)


def _nested_loo_alpha(q, r, y):
    """
    HONEST: for each held-out i, choose α on the other N-1 substances and
    predict i with it. Returns (per-fold α array, R² of the nested preds).
    """
    n = len(y)
    alphas = np.empty(n)
    preds = np.empty(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        a = _best_alpha(q, r, y, mask=mask)
        alphas[i] = a
        preds[i] = a * q[i] + (1 - a) * r[i]
    return alphas, _r2(y, preds)


def _fold_distribution(alphas):
    """Per-fold α counts, e.g. {"0.2": 101, ...}. Backs the manuscript's
    fold-stability claim without a re-run."""
    vals, counts = np.unique(np.round(alphas, 2), return_counts=True)
    return {f"{v:.2f}": int(c) for v, c in zip(vals, counts)}


# ── Public API ────────────────────────────────────────────────────

def compute_honest_hybrid():
    """Run both procedures and return the canonical result dict."""
    loaded = _load_predictions()
    if loaded is None:
        return None
    arrays, n_common, cv_type, baselines = loaded

    leaky, honest, folds = {}, {}, {}
    for key in ("deg", "koc"):
        q, r, y = arrays[key]

        alpha, r2_leaky = _naive_alpha(q, r, y)
        leaky[f"alpha_{key}"] = float(alpha)
        leaky[f"hybrid_{key}_r2"] = float(r2_leaky)

        alphas, r2_honest = _nested_loo_alpha(q, r, y)
        honest[f"alpha_{key}_mean"] = float(alphas.mean())
        honest[f"alpha_{key}_std"] = float(alphas.std())
        honest[f"hybrid_{key}_r2"] = float(r2_honest)
        folds[f"alpha_{key}_folds"] = _fold_distribution(alphas)

    delta_deg = honest["hybrid_deg_r2"] - baselines["rf_21feat_loo_deg_r2"]
    delta_koc = honest["hybrid_koc_r2"] - baselines["rf_21feat_loo_koc_r2"]

    return {
        "method": "nested_loo_cv_alpha",
        "n_common": n_common,
        "qml_cv_type": cv_type,
        "alpha_grid_step": 0.05,
        "leaky": leaky,
        "honest": honest,
        "fold_distribution": folds,
        "baselines": baselines,
        "delta_vs_rf": {
            "deg_r2": round(delta_deg, 4),
            "koc_r2": round(delta_koc, 4),
        },
        # The nested DegT50 gain over RF is +0.001 and the Koc blend is a net
        # loss, so neither target supports a hybrid advantage. See tab:baselines
        # and the bootstrap CIs in confidence_intervals.json.
        "conclusion": "hybrid_within_run_to_run_noise_of_rf",
    }


def get_hybrid_results():
    """
    Return the cached hybrid results, computing them if absent. Headline
    numbers are the NESTED (honest) ones; the naive values are exposed
    under naive_* purely as the leakage comparator.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            results = json.load(f)
    else:
        results = compute_honest_hybrid()
        if results is None:
            return None
        with open(CACHE_FILE, "w") as f:
            json.dump(results, f, indent=2)

    honest, leaky = results["honest"], results["leaky"]
    return {
        "method": results["method"],
        "qml_available": True,
        "qml_cv_type": results.get("qml_cv_type"),
        "n_common": results["n_common"],
        "alpha_deg": round(honest["alpha_deg_mean"], 2),
        "alpha_deg_std": round(honest["alpha_deg_std"], 3),
        "alpha_koc": round(honest["alpha_koc_mean"], 2),
        "alpha_koc_std": round(honest["alpha_koc_std"], 3),
        "hybrid_deg_r2": round(honest["hybrid_deg_r2"], 4),
        "hybrid_koc_r2": round(honest["hybrid_koc_r2"], 4),
        "rf_deg_r2": results["baselines"]["rf_21feat_loo_deg_r2"],
        "rf_koc_r2": results["baselines"]["rf_21feat_loo_koc_r2"],
        "naive_alpha_deg": round(leaky["alpha_deg"], 2),
        "naive_hybrid_deg_r2": round(leaky["hybrid_deg_r2"], 4),
        "naive_hybrid_koc_r2": round(leaky["hybrid_koc_r2"], 4),
        "delta_vs_rf": results["delta_vs_rf"],
        "conclusion": results["conclusion"],
    }


if __name__ == "__main__":
    import pprint

    res = compute_honest_hybrid()
    if res is None:
        raise SystemExit("Missing classical_baseline.json or QML CV cache.")
    with open(CACHE_FILE, "w") as f:
        json.dump(res, f, indent=2)
    print(f"Wrote {CACHE_FILE}")
    pprint.pprint(res)
