# QP-FATE Heavy Experiments — Final Report

> **Host:** laptop32 (32 GB RAM, DCCM worker node)
> **Script:** `scripts/run_heavy_experiments.py`
> **Run time:** 2026-04-21 05:55 → 2026-04-22 21:20 CEST (**39.4 hours**)
> **Status:** ✅ **COMPLETE** — all results pulled to gnosys, laptop32 safe to shut down.

---

## Results Summary

### Exp 1: Seed ×5 Architecture Sweep (QML Variants)

| Variant | Qubits | Layers | Epochs | R² mean ± std | R² range | Time/seed |
|---------|--------|--------|--------|---------------|----------|-----------|
| **A — Shallow Wide** | 12 | 3 | 80 | **+0.051 ± 0.121** | −0.12 to +0.23 | ~1.0h |
| B — Deep Narrow | 8 | 12 | 100 | −0.412 ± 0.079 | −0.54 to −0.29 | ~2.4h |
| C — HW Efficient | 12 | 5 | 60 | −0.111 ± 0.093 | −0.23 to +0.02 | ~1.1h |
| D — Baseline Plus | 12 | 8 | 120 | −0.264 ± 0.178 | −0.57 to −0.06 | ~3.4h |

**Key finding:** All QML variants are worse than random, except Variant A which is marginally above zero but with high variance. More layers/depth = worse performance (barren plateau is not the cause — see Exp 6 below).

### Exp 2: Leave-One-Class-Out Grouped CV (re-run 2026-04-22 on gnosys — key-lookup fix)

> Prior run on laptop32 reported `n_classes = 1` because the runner looked for
> `chemical_class`/`class`, but the DB field is named `cls`. Fixed in
> `scripts/run_heavy_experiments.py:150` and re-run locally.

- **Classes × substances:** 50 × 110
- **RF:** DegT50 R² = 0.134, Koc R² = 0.724
- **GB:** DegT50 R² = 0.042, Koc R² = 0.717
- **Drop vs LOO:** RF DegT50 Δ = +0.153, RF Koc Δ = +0.035
- Koc generalizes across chemical classes; DegT50 does not. Written up as a
  new §3.5 "Domain Applicability" subsection in `main.tex` / `main_rsc.tex`.
- Source of truth: `backend/.qml_cache/review_experiments/exp2_grouped_cv.json`.

### Exp 3: Binary P/vP Classification (re-run 2026-06-11 on gnosys — N=110 fix)

> The original laptop32 run used a stale 111-substance snapshot (its class
> counts summed to 111: 10 vP vs 101 non-vP). The live `substances.db` holds
> 110 unique substances — the 111th was a duplicate `Difenoconazole` that the
> SQLite migration deduped via `INSERT OR REPLACE` on a UNIQUE name. Re-run on
> N=110; the numbers below are canonical and match `tab:binary` in `main.tex`.

| Model | P (>60d) BA | P MCC | vP (>180d) BA | vP MCC |
|-------|------------|-------|---------------|--------|
| RF | 0.660 | 0.432 | 0.500 | 0.000 |
| **GB** | **0.791** | **0.623** | **0.670** | **0.340** |

- Class counts: $n_P$ = 28/82, $n_{vP}$ = 10/100.
- GB is clearly better for regulatory classification.
- RF completely fails on vP (predicts all non-vP — class imbalance issue: 10 vP vs 100 non-vP).
- GB gets 4/10 vP correct with 6 false positives — usable for screening.
- Source of truth: `backend/.qml_cache/review_experiments/exp3_binary_classification.json`.

---

## Earlier Experiments (already on laptop32)

| File | Key Result |
|------|-----------|
| `exp2_17feature_baseline.json` | Dropping the 4 DegT50-targeted descriptors costs RF 0.112 and GB 0.153 on DegT50 (RF 0.290→0.178, GB 0.285→0.132); Koc is unaffected (Δ ≤ 0.009). The earlier "17f ≈ 21f" summary here was wrong — it quoted the 21f value as if it were the 17f result. |
| `exp3_bioaccessibility_ablation.json` | Removing bioaccessibility drops R² by only 0.013 — negligible |
| `exp4_mlp_baseline.json` | MLP(8,4) R²=−0.28; MLP(64,32) R²=0.07 — still poor for DegT50 |
| `exp5_sabljic_null_model.json` | Koc R²=−0.97 — Sabljic formula fails on this dataset |
| `exp6_gradient_variance.json` | Var[‖∇L‖]=0.40 ≫ 10⁻³ — **no barren plateau** at 8q/6L |

---

## Action Items

### Manuscript Updates

- [x] Update Table 3 with final seed-sweep means and ± std
- [x] Add Exp 3 binary classification results to manuscript (new §3.6)
- [x] Add Exp 2 LOCO domain-applicability results to manuscript (new §3.5)
- [ ] Mention Exp 6 gradient variance in the "why QML underperforms" discussion
- [ ] Reference the Sabljic null-model failure as evidence that simple physics-based Koc models don't transfer to this dataset

### Housekeeping

- [x] All results pulled to gnosys (`backend/.qml_cache/review_experiments/`)
- [x] Full log saved locally (`heavy_experiments.log`)
- [ ] Clean up laptop32: remove the `.venv`, log, and cache after confirming gnosys copy is complete
- [ ] Commit result JSONs to the QP-FATE repo
- [ ] laptop32 can be shut down now

---

## Monitoring Commands (for future runs)

```bash
ssh laptop32 'ps aux | grep run_heavy_experiments | grep -v grep'
ssh laptop32 'tail -f ~/Projects/Chemistry/Quantum\ Chemistry/Quantum\ Pesticide\ Fate\ Modeling/heavy_experiments.log'
```
