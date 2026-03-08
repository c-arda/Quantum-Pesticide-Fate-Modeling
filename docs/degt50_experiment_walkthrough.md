# DegT50 Architecture Experiment — Walkthrough

## What was built

[run_degt50_experiment.py](file:///home/ardac/Projects/Chemistry/Quantum Chemistry/Quantum Pesticide Fate Modeling/run_degt50_experiment.py) — a self-contained script testing 4 quantum circuit architectures for DegT50 prediction.

## Circuit Variants

| Variant | Architecture | Hypothesis |
|---------|-------------|-----------|
| **A** Shallow-wide | 12q, 3L, all-to-all CZ, double re-upload | Barren plateaus from too many layers |
| **B** Deep-narrow | 8q, 12L, ring CNOT, triple re-upload | Too many qubits for 17 features |
| **C** Hardware-efficient | 12q, 5L, `StronglyEntanglingLayers` | Structured entanglement template |
| **D** Baseline+ | 12q, 8L, current arch, lr=0.03, 120ep | Just an optimization/convergence issue |

## Verification

All 4 circuits build and execute correctly:

```
A_shallow_wide:      12q, 3L, shape=(3,12,3),  output_len=12 ✓
B_deep_narrow:        8q, 12L, shape=(12,8,3),  output_len=8  ✓
C_hardware_efficient: 12q, 5L, shape=(5,12,3),  output_len=12 ✓
D_baseline_plus:      12q, 8L, shape=(8,12,3),  output_len=12 ✓
```

## How to deploy on laptop16

> [!IMPORTANT]
> Laptop16 is currently offline. Once it's back:

```bash
# On laptop16
cd /home/ca/qp-fate
git pull   # or scp the script from workstation

# Launch (nohup, backgrounded)
nohup /home/ca/qp-fate/.venv/bin/python -u run_degt50_experiment.py \
    > degt50_experiment.log 2>&1 &

# Monitor
tail -f degt50_experiment.log
```

Results will appear in `backend/.qml_cache/degt50_experiment_results.json`.

The script checkpoints after each variant — if laptop16 reboots mid-run, just re-launch and it picks up where it left off.
