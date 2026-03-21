# QP-FATE VQC Architecture Experiment — Results

> **Date**: 2026-03-21 (overnight run, 20:58 → 09:03)
> **Dataset**: 110 pesticide substances, 21 molecular descriptors, EU SPIN database
> **Evaluation**: 5-fold cross-validation on DegT50 prediction
> **Baseline (previous)**: 12q, 60ep, lr=0.05 → R² = −0.141

## Summary Table

| Variant | Architecture | Qubits | Layers | Epochs | LR | R² | MAE | RMSE | Train MSE | Time |
|---------|-------------|--------|--------|--------|-----|------|------|------|-----------|------|
| A: Shallow-Wide | All-to-all CZ, double re-upload | 12 | 3 | 80 | 0.03 | −0.129 | 0.596 | 0.724 | 0.179 | 0.7h |
| **B: Deep-Narrow** | **Ring CNOT, triple re-upload** | **8** | **12** | **100** | **0.02** | **+0.066** | **0.512** | **0.658** | **0.003** | **1.1h** |
| C: HW-Efficient | StronglyEntanglingLayers, mixed | 12 | 5 | 60 | 0.04 | +0.014 | 0.518 | 0.677 | 0.134 | 0.5h |
| D: Baseline-Plus | Current arch, extended training | 12 | 8 | 120 | 0.03 | −0.269 | 0.619 | 0.768 | 0.006 | 9.8h |

**Winner**: B_deep_narrow (R² = +0.066, improvement of +0.207 over baseline)

## Classical Baselines (for context)

| Model | DegT50 R² | Koc R² |
|-------|-----------|--------|
| Random Forest (LOO) | **0.287** | **0.759** |
| Gradient Boosting (LOO) | 0.283 | 0.752 |
| Hybrid QML+RF (nested CV) | 0.288 | 0.750 |

## Key Findings

1. **Depth > Width**: 8 qubits with 12 layers (B) outperforms all 12-qubit variants
2. **Overfitting pattern**: B achieves train MSE=0.003 but test R²=0.066 — extreme overfitting, yet still best test performance among VQC variants
3. **Extended training hurts**: D (120 epochs) has the worst R² despite lowest train MSE, confirming overfitting
4. **Honest negative result confirmed**: Best VQC (R²=0.066) still far below Random Forest (R²=0.287)
5. **Ring CNOT + triple re-upload** is the most effective entanglement/encoding strategy for this dataset size

## Manuscript Implications

- Update Table 3 in `manuscript/main.tex` with Variant B results
- The depth-over-width finding strengthens the "barren plateau avoidance" argument
- Variant B's R²=0.066 is now the best-reported VQC result for DegT50 on this dataset
- Consider adding a figure comparing architecture variants (A–D)

## Data Files

- Full results JSON: `backend/.qml_cache/degt50_experiment_results.json` (94 KB)
- Per-substance predictions with fold assignments included in JSON
- Training log: `degt50_retrain.log`
- Checkpoint: `backend/.qml_cache/degt50_experiment_checkpoint.json`
