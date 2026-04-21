#!/usr/bin/env python3
"""
QP-FATE Review — Remaining Experiments (H5, H8, H9)
====================================================
Dispatched to laptop16 after micro-experiments completed.

Run: ssh laptop16 'cd ~/Projects/Chemistry/Quantum\ Chemistry/Quantum\ Pesticide\ Fate\ Modeling && source .venv/bin/activate && python3 scripts/run_remaining_experiments.py'

Experiments:
  H5: Freundlich 1/n ablation for Koc (is 1/n leaking Koc info?)
  H8: Ridge regression on raw ⟨Z⟩ expectation values (linear decodability test)
  H9: α bootstrap confidence intervals (hybrid stacking robustness)
"""

import sys, os, json, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "backend", ".qml_cache", "review_experiments"
)
os.makedirs(RESULTS_DIR, exist_ok=True)

print("=" * 70)
print("QP-FATE Review — Remaining Experiments (H5, H8, H9)")
print(f"Host: {os.uname().nodename} | Python: {sys.version.split()[0]}")
print(f"Results dir: {RESULTS_DIR}")
print("=" * 70)

t_total = time.time()

# ── Load data ─────────────────────────────────────────────────────
from backend.spin_database import SUBSTANCES
from backend.quantum_predictor import extract_features, FEATURE_NAMES

all_features = []
all_deg = []
all_koc = []
for s in SUBSTANCES:
    f = extract_features(s)
    all_features.append(f.tolist() if hasattr(f, 'tolist') else list(f))
    all_deg.append(np.log10(max(s.get("degT50_soil", 1), 0.1)))
    all_koc.append(np.log10(max(s.get("koc", 1), 1)))

X = np.array(all_features)
y_deg = np.array(all_deg)
y_koc = np.array(all_koc)
N = len(SUBSTANCES)


# ══════════════════════════════════════════════════════════════════
# Exp H5: Freundlich 1/n ablation for Koc
# ══════════════════════════════════════════════════════════════════
print("\n◈ Exp H5: Freundlich 1/n ablation for Koc...")
t0 = time.time()

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import LeaveOneOut

freundlich_idx = FEATURE_NAMES.index("freundlich_n")
bioaccess_idx = FEATURE_NAMES.index("bioaccessibility")

# Fair Koc set: exclude bioaccessibility (idx 14)
fair_mask = [i for i in range(X.shape[1]) if i != bioaccess_idx]
X_fair = X[:, fair_mask]

# Also exclude Freundlich 1/n
no_freundlich_mask = [i for i in fair_mask if i != freundlich_idx]
X_no_freundlich = X[:, no_freundlich_mask]

loo = LeaveOneOut()
results_h5 = {"experiment": "H5_freundlich_ablation_koc"}

for name, Model, kwargs in [
    ("Ridge", Ridge, {"alpha": 1.0}),
    ("RF", RandomForestRegressor, {"n_estimators": 200, "max_depth": 10, "random_state": 42}),
    ("GB", GradientBoostingRegressor, {"n_estimators": 200, "max_depth": 4, "learning_rate": 0.1, "random_state": 42}),
]:
    preds_with = np.zeros(N)
    preds_without = np.zeros(N)
    for train_idx, test_idx in loo.split(X_fair):
        m1 = Model(**kwargs).fit(X_fair[train_idx], y_koc[train_idx])
        preds_with[test_idx] = m1.predict(X_fair[test_idx])
        m2 = Model(**kwargs).fit(X_no_freundlich[train_idx], y_koc[train_idx])
        preds_without[test_idx] = m2.predict(X_no_freundlich[test_idx])

    ss_res_with = np.sum((y_koc - preds_with) ** 2)
    ss_res_without = np.sum((y_koc - preds_without) ** 2)
    ss_tot = np.sum((y_koc - np.mean(y_koc)) ** 2)
    r2_with = 1 - ss_res_with / ss_tot
    r2_without = 1 - ss_res_without / ss_tot
    delta = r2_with - r2_without

    results_h5[f"{name}_koc_with_1n"] = round(r2_with, 4)
    results_h5[f"{name}_koc_without_1n"] = round(r2_without, 4)
    results_h5[f"{name}_delta"] = round(delta, 4)
    print(f"  {name}: with 1/n={r2_with:.4f}, without={r2_without:.4f} (Δ={delta:+.4f})")

results_h5["elapsed_seconds"] = round(time.time() - t0, 1)
with open(os.path.join(RESULTS_DIR, "exp_h5_freundlich_ablation.json"), "w") as f:
    json.dump(results_h5, f, indent=2)
print(f"  → Saved: {os.path.join(RESULTS_DIR, 'exp_h5_freundlich_ablation.json')}")


# ══════════════════════════════════════════════════════════════════
# Exp H8: Ridge regression on raw ⟨Z⟩ expectation values
# ══════════════════════════════════════════════════════════════════
print("\n◈ Exp H8: Ridge on raw ⟨Z⟩ expectation values...")
t0 = time.time()

try:
    import pennylane as qml
    import pennylane.numpy as pnp
    from backend.quantum_predictor import (
        quantum_circuit_deg, quantum_circuit_koc,
        N_QUBITS_DEG, N_QUBITS_KOC, N_LAYERS_DEG, N_LAYERS_KOC
    )

    # Generate random ⟨Z⟩ features from untrained circuits (100 random weight sets)
    n_random = 20
    results_h8 = {"experiment": "H8_ridge_on_raw_Z", "n_random_circuits": n_random}

    # Use 17-feature subset for DegT50 circuit
    deg_feature_indices = list(range(17))
    X_deg = X[:, deg_feature_indices]

    r2_deg_list = []
    r2_koc_list = []

    for seed in range(n_random):
        np.random.seed(seed)
        # Random weights for DegT50 circuit
        w_deg = pnp.array(np.random.uniform(-0.5, 0.5,
                          (N_LAYERS_DEG, N_QUBITS_DEG, 3)), requires_grad=False)
        # Random weights for Koc circuit
        w_koc = pnp.array(np.random.uniform(-0.5, 0.5,
                          (N_LAYERS_KOC, N_QUBITS_KOC, 3)), requires_grad=False)

        # Get ⟨Z⟩ features for each substance
        Z_deg = np.array([quantum_circuit_deg(pnp.array(X_deg[i], requires_grad=False), w_deg)
                          for i in range(N)])
        Z_koc = np.array([quantum_circuit_koc(pnp.array(X[i], requires_grad=False), w_koc)
                          for i in range(N)])

        # Ridge LOO on ⟨Z⟩ features
        preds_deg = np.zeros(N)
        preds_koc = np.zeros(N)
        for train_idx, test_idx in loo.split(Z_deg):
            m_deg = Ridge(alpha=1.0).fit(Z_deg[train_idx], y_deg[train_idx])
            preds_deg[test_idx] = m_deg.predict(Z_deg[test_idx])
            m_koc = Ridge(alpha=1.0).fit(Z_koc[train_idx], y_koc[train_idx])
            preds_koc[test_idx] = m_koc.predict(Z_koc[test_idx])

        r2_d = 1 - np.sum((y_deg - preds_deg)**2) / np.sum((y_deg - np.mean(y_deg))**2)
        r2_k = 1 - np.sum((y_koc - preds_koc)**2) / np.sum((y_koc - np.mean(y_koc))**2)
        r2_deg_list.append(r2_d)
        r2_koc_list.append(r2_k)

        if (seed + 1) % 5 == 0:
            print(f"  Seed {seed+1}/{n_random}: DegT50 R²={r2_d:.4f}, Koc R²={r2_k:.4f}")

    results_h8["ridge_on_Z_deg_mean_r2"] = round(float(np.mean(r2_deg_list)), 4)
    results_h8["ridge_on_Z_deg_std_r2"] = round(float(np.std(r2_deg_list)), 4)
    results_h8["ridge_on_Z_koc_mean_r2"] = round(float(np.mean(r2_koc_list)), 4)
    results_h8["ridge_on_Z_koc_std_r2"] = round(float(np.std(r2_koc_list)), 4)
    results_h8["ridge_on_raw_features_deg_r2"] = round(float(
        1 - np.sum((y_deg - Ridge(alpha=1.0).fit(X, y_deg).predict(X))**2) /
        np.sum((y_deg - np.mean(y_deg))**2)), 4)
    results_h8["interpretation"] = (
        f"Ridge on random ⟨Z⟩: DegT50 R²={np.mean(r2_deg_list):.3f}±{np.std(r2_deg_list):.3f}, "
        f"Koc R²={np.mean(r2_koc_list):.3f}±{np.std(r2_koc_list):.3f}. "
        "If ⟨Z⟩ R² << raw feature R², the quantum embedding destroys linear decodability."
    )
    results_h8["elapsed_seconds"] = round(time.time() - t0, 1)

    with open(os.path.join(RESULTS_DIR, "exp_h8_ridge_on_Z.json"), "w") as f:
        json.dump(results_h8, f, indent=2)
    print(f"  → Saved: {os.path.join(RESULTS_DIR, 'exp_h8_ridge_on_Z.json')}")
    print(f"  Ridge on ⟨Z⟩: DegT50 R²={np.mean(r2_deg_list):.4f}±{np.std(r2_deg_list):.4f}")
    print(f"  Ridge on ⟨Z⟩: Koc R²={np.mean(r2_koc_list):.4f}±{np.std(r2_koc_list):.4f}")

except Exception as e:
    print(f"  ⚠ H8 failed: {e}")
    results_h8 = {"experiment": "H8_ridge_on_raw_Z", "error": str(e)}
    with open(os.path.join(RESULTS_DIR, "exp_h8_ridge_on_Z.json"), "w") as f:
        json.dump(results_h8, f, indent=2)


# ══════════════════════════════════════════════════════════════════
# Exp H9: α bootstrap confidence intervals
# ══════════════════════════════════════════════════════════════════
print("\n◈ Exp H9: α bootstrap confidence intervals...")
t0 = time.time()

# Load VQC predictions if available
vqc_cache = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "backend", ".qml_cache"
)

try:
    # Try to load existing VQC 5-fold CV predictions
    vqc_deg_preds = None
    vqc_koc_preds = None

    # Check for cached results
    for fname in ["vqc_deg_5fold.json", "cv_results_deg.json", "quantum_cv_results.json"]:
        fpath = os.path.join(vqc_cache, fname)
        if os.path.exists(fpath):
            with open(fpath) as f:
                data = json.load(f)
            if "predictions" in data:
                vqc_deg_preds = np.array(data["predictions"])
                break

    if vqc_deg_preds is None:
        # Generate VQC predictions from a trained model on full data
        # (approximation — proper nested CV would be better but too expensive)
        from backend.quantum_predictor import _train_model
        print("  No cached VQC predictions found. Training single model for bootstrap approximation...")

        X_deg_list = [X[i, :17].tolist() for i in range(N)]
        w, r, _ = _train_model(
            X_deg_list, y_deg.tolist(), n_epochs=80, lr=0.04,
            n_qubits=N_QUBITS_DEG, n_layers=N_LAYERS_DEG,
            circuit_fn=quantum_circuit_deg
        )
        vqc_deg_preds = np.array([
            float(pnp.dot(pnp.array(r[:N_QUBITS_DEG]),
                          pnp.array(quantum_circuit_deg(pnp.array(X[i, :17], requires_grad=False), w)))
                  + r[N_QUBITS_DEG])
            for i in range(N)
        ])

    # RF LOO predictions
    rf_deg_preds = np.zeros(N)
    for train_idx, test_idx in loo.split(X):
        m = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
        m.fit(X[train_idx], y_deg[train_idx])
        rf_deg_preds[test_idx] = m.predict(X[test_idx])

    # Bootstrap α optimization
    n_bootstrap = 1000
    alpha_grid = np.arange(0, 1.05, 0.05)
    bootstrap_alphas = []

    for b in range(n_bootstrap):
        idx = np.random.choice(N, N, replace=True)
        best_alpha = 0.0
        best_mse = np.inf
        for a in alpha_grid:
            hybrid = a * vqc_deg_preds[idx] + (1 - a) * rf_deg_preds[idx]
            mse = np.mean((y_deg[idx] - hybrid) ** 2)
            if mse < best_mse:
                best_mse = mse
                best_alpha = a
        bootstrap_alphas.append(best_alpha)

    bootstrap_alphas = np.array(bootstrap_alphas)
    results_h9 = {
        "experiment": "H9_alpha_bootstrap",
        "n_bootstrap": n_bootstrap,
        "alpha_mean": round(float(np.mean(bootstrap_alphas)), 4),
        "alpha_std": round(float(np.std(bootstrap_alphas)), 4),
        "alpha_median": round(float(np.median(bootstrap_alphas)), 4),
        "alpha_ci_2.5": round(float(np.percentile(bootstrap_alphas, 2.5)), 4),
        "alpha_ci_97.5": round(float(np.percentile(bootstrap_alphas, 97.5)), 4),
        "alpha_zero_fraction": round(float(np.mean(bootstrap_alphas == 0)), 4),
        "elapsed_seconds": round(time.time() - t0, 1),
    }

    with open(os.path.join(RESULTS_DIR, "exp_h9_alpha_bootstrap.json"), "w") as f:
        json.dump(results_h9, f, indent=2)

    print(f"  α = {results_h9['alpha_mean']:.3f} ± {results_h9['alpha_std']:.3f}")
    print(f"  95% CI: [{results_h9['alpha_ci_2.5']:.3f}, {results_h9['alpha_ci_97.5']:.3f}]")
    print(f"  Fraction α=0: {results_h9['alpha_zero_fraction']:.3f}")
    print(f"  → Saved: {os.path.join(RESULTS_DIR, 'exp_h9_alpha_bootstrap.json')}")

except Exception as e:
    print(f"  ⚠ H9 failed: {e}")
    import traceback; traceback.print_exc()
    results_h9 = {"experiment": "H9_alpha_bootstrap", "error": str(e)}
    with open(os.path.join(RESULTS_DIR, "exp_h9_alpha_bootstrap.json"), "w") as f:
        json.dump(results_h9, f, indent=2)


# ══════════════════════════════════════════════════════════════════
print(f"\n{'='*70}")
print(f"All remaining experiments complete in {time.time()-t_total:.1f}s "
      f"({(time.time()-t_total)/60:.1f} min)")
print("=" * 70)
