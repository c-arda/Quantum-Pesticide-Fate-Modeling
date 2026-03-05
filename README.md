# QP-FATE: Quantum Pesticide Fate Modeling

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![PennyLane](https://img.shields.io/badge/PennyLane-0.39+-purple.svg)](https://pennylane.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Quantum machine learning for predicting pesticide environmental fate properties** — a 12-qubit variational quantum circuit that predicts soil degradation half-life (DegT50) and organic carbon adsorption (Koc) from molecular structure, integrated with FOCUS regulatory fate models.

## Highlights

- **12-qubit VQC** with data re-uploading and IQP-style entanglement (301 variational parameters)
- **17 molecular descriptors** including microbial degradation proxies and photolability features
- **111 pesticide substances** from the EU SPIN database with validated SMILES
- **Classical baselines** (Random Forest + Gradient Boosting) for head-to-head comparison
- **Hybrid QML+RF stacking** — uses QML for DegT50 (quantum advantage) and RF for Koc
- **Field validation** against published groundwater monitoring data (8 substances)
- **Web UI** with 7 interactive panels: dashboard, substances, FOCUS scenarios, quantum status, validation, QML vs classical comparison, and simulation

## Architecture

```
SMILES → RDKit descriptors → 17 features → [0, π] scaling
                                              ↓
                              12-qubit VQC (PennyLane)
                              ├─ Hadamard + RZ encoding
                              ├─ IQP ZZ entanglement
                              ├─ RY cross-rotation (features 13-17)
                              ├─ Data re-uploading
                              └─ 5 variational layers (Rot + CNOT)
                                              ↓
                              ⟨Z₀⟩...⟨Z₁₁⟩ → Linear readout
                                              ↓
                              log₁₀(DegT50), log₁₀(Koc)
                                              ↓
                              FOCUS fate model (PEARL/GEM)
                                              ↓
                              PEC groundwater (µg/L)
```

## Molecular Features (17)

| # | Feature | Type | Purpose |
|---|---------|------|---------|
| 1-5 | MW, logP, n_heavy, HBD, HBA | Structural | Basic molecular properties |
| 6-7 | n_rings, n_rotatable | Topological | Molecular flexibility |
| 8-9 | log(solubility), log(vapor_pressure) | Physicochemical | Phase partitioning |
| 10 | freundlich_n | Sorption | Non-linear adsorption |
| 11-12 | TPSA, aromatic_ring_frac | Electronic | Polar surface / aromaticity |
| 13 | n_hydrolyzable | Microbial proxy | Enzymatic attack sites |
| 14 | n_halogens | Microbial proxy | Biodegradation resistance |
| 15 | bioaccessibility | Microbial proxy | Microbial availability |
| 16 | charge_state | Blind-spot fix | pKa-based cationic correction |
| 17 | conjugated_pi_size | Blind-spot fix | Photolability proxy |

## Quick Start

```bash
# Clone and set up
git clone https://github.com/unearthlyimprint/Quantum-Pesticide-Fate-Modeling.git
cd Quantum-Pesticide-Fate-Modeling
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start the backend (trains QML model on first run, ~15-20 min)
python backend/server.py

# Open the web UI
python3 -m http.server 8765
# Navigate to http://localhost:8765
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Backend health check |
| GET | `/api/substances` | List all 111 substances |
| GET | `/api/quantum/status` | QML model info (qubits, params, gate count) |
| GET | `/api/quantum/predict/<name>` | Predict DegT50/Koc for a substance |
| GET | `/api/classical-baseline` | RF + GBM cross-validation results |
| GET | `/api/error-analysis` | Prediction errors by chemical class |
| GET | `/api/hybrid-results` | Hybrid QML+RF stacking results |
| POST | `/api/run` | Run full FOCUS fate simulation |

## Cross-Validation Results

*Results with 60-epoch training on 111 substances, 17 features — CV in progress.*

| Model | DegT50 R² | Koc R² |
|-------|-----------|--------|
| QML 12-Qubit | *pending* | *pending* |
| Random Forest (LOO) | 0.194 | 0.766 |
| Gradient Boosting (LOO) | 0.223 | 0.779 |

## Project Structure

```
qp-fate/
├── index.html              # Web UI (SPA)
├── app.js                  # Frontend logic
├── styles.css              # UI styling
├── requirements.txt        # Python dependencies
├── backend/
│   ├── server.py           # Flask API server
│   ├── quantum_predictor.py # 12-qubit VQC (PennyLane)
│   ├── classical_predictor.py # RF + GBM baselines
│   ├── hybrid_predictor.py # QML+RF stacking
│   ├── spin_database.py    # 111 substances with properties
│   ├── fate_model.py       # FOCUS PEARL/GEM fate model
│   ├── field_data.py       # Field validation data
│   └── focus_scenarios.py  # 9 FOCUS groundwater scenarios
```

## References

- [PennyLane](https://pennylane.ai) — Quantum ML framework
- [FOCUS](https://focus.jrc.ec.europa.eu) — Forum for Co-ordination of pesticide fate models
- [pesticidemodels.eu](https://pesticidemodels.eu) — EU pesticide fate model hub
- [SPIN 4.4](https://pesticidemodels.eu/spin/) — Substances Plug-IN database

## License

MIT — see [LICENSE](LICENSE)
