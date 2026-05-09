# QPFate DegT50 Quantum Circuit Training Results
**Date**: 2026-05-03  
**Backend**: PennyLane lightning.qubit (C++ accelerated)  
**Data**: 80 synthetic samples (12 features → DegT50 in days)  
**Training**: 60 epochs, 5-fold CV, 12 qubits, 6 layers

## Variant Results (5-fold CV)

| Variant | Architecture | R² | RMSE | MAE | Time |
|---------|-------------|-----|------|-----|------|
| A_shallow_wide | All-to-all CZ, 12 qubits | -0.5508 | 36.10 | 30.76 | 667s |
| B_deep_narrow | Ring CNOT, 6 qubits | -1.5660 | 46.44 | 38.35 | 579s |
| C_hardware_efficient | StronglyEntanglingLayers, 12 qubits | -1.7796 | 48.33 | 43.88 | 753s |
| D_baseline_plus | Linear CNOT, 6 qubits | -1.1871 | 42.87 | 37.71 | 585s |

## Notes
- Negative R² = worse than mean prediction → expected on synthetic random data
- **Action needed**: Replace synthetic data with real pesticide DegT50 features
- Best architecture: A (shallow-wide, all-to-all CZ) — likely best for real data too
- Total training time: 43 min on RTX 5070 Ti
