# DegT50 Architecture Experiment — Standalone Runner for laptop16

## Background

The current QML circuit (12 qubits, 8 layers, IQP encoding, nearest-neighbor CNOTs) produces:
- **Koc R² = 0.412** (5-fold, 60 epochs) — decent, the circuit *can* learn
- **DegT50 R² = −0.141** — worse than mean-prediction; the architecture is not suited for degradation half-life

The LOO run on laptop32 uses the **same** architecture. We want to explore architectural changes specifically for DegT50 on laptop16 in parallel, without touching the main codebase or the laptop32 run.

## Proposed Changes

### [NEW] [run_degt50_experiment.py](file:///home/ardac/Projects/Chemistry/Quantum Chemistry/Quantum Pesticide Fate Modeling/run_degt50_experiment.py)

A self-contained experiment script that:

1. **Imports only** `extract_features` and `SUBSTANCES` from the existing codebase (no circuit dependency)
2. **Trains DegT50 only** (no Koc) — halves the compute per fold
3. **Tests 4 architecture variants** via 5-fold CV (fast, ~2 h each on laptop16):

| Variant | Qubits | Layers | Entanglement | Encoding | LR | Epochs |
|---------|--------|--------|-------------|----------|------|--------|
| A: **Shallow-wide** | 12 | 3 | All-to-all CZ | IQP + re-upload ×2 | 0.03 | 80 |
| B: **Deep-narrow** | 8 | 12 | Ring CNOT | IQP + re-upload ×3 | 0.02 | 100 |
| C: **Hardware-efficient** | 12 | 5 | StronglyEntanglingLayers | Amplitude + angle | 0.04 | 60 |
| D: **Baseline+ (more epochs)** | 12 | 8 | Nearest-neighbor (current) | Current | 0.03 | 120 |

Key architectural hypotheses:
- **A**: Maybe DegT50 needs more entanglement (all-to-all) but fewer layers to avoid barren plateaus
- **B**: Maybe 12 qubits is too many for 17 features — 8 qubits with deeper circuit might learn better
- **C**: PennyLane's built-in `StronglyEntanglingLayers` template as a structured alternative
- **D**: Same architecture but lower LR + more epochs — test if it's just an optimization issue

4. **Outputs** a JSON comparison file and prints a summary table
5. **Checkpoints** each variant (resume-safe for laptop16 reboots)
6. **Uses `nohup`-friendly** design (all output to stdout with `flush=True`)

### Deployment to laptop16

The script is designed to run standalone from the existing `qp-fate` clone:
```bash
cd /home/ca/qp-fate
nohup python -u run_degt50_experiment.py > degt50_experiment.log 2>&1 &
```

> [!IMPORTANT]
> Laptop16 is currently offline (`No route to host`). The script will be ready to deploy when it comes back up. You'll need to `git pull` on laptop16 or `scp` the script.

## Verification Plan

### Automated (local dry-run)
```bash
cd /home/ardac/Projects/Chemistry/Quantum\ Chemistry/Quantum\ Pesticide\ Fate\ Modeling
python -c "
import run_degt50_experiment as exp
# Verify all 4 circuits build and run forward pass
for name, cfg in exp.VARIANTS.items():
    circuit = cfg['circuit_fn']
    print(f'{name}: circuit built OK')
print('All variants valid')
"
```

### On laptop16 (once online)
1. `scp` or `git pull` the script
2. Run with `nohup python -u run_degt50_experiment.py > degt50_experiment.log 2>&1 &`
3. Monitor: `tail -f degt50_experiment.log`
4. Results appear in `backend/.qml_cache/degt50_experiment_results.json`
