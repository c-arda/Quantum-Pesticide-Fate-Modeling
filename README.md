# QP-FATE: Quantum Pesticide Fate Modeling

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![PennyLane](https://img.shields.io/badge/PennyLane-0.39+-6C2DC7.svg)](https://pennylane.ai)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![RDKit](https://img.shields.io/badge/RDKit-Cheminformatics-3CA5D8.svg)](https://www.rdkit.org)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E.svg?logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![HTML5](https://img.shields.io/badge/HTML5-CSS3-E34F26.svg?logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![EC 1107/2009](https://img.shields.io/badge/EU-EC%201107%2F2009-003399.svg?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiI+PGNpcmNsZSBjeD0iOCIgY3k9IjgiIHI9IjYiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ZmZCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz48L3N2Zz4=)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A32009R1107)
[![ChemRxiv](https://img.shields.io/badge/ChemRxiv-10.26434/chemrxiv.15000799-B31B1B.svg)](https://chemrxiv.org/doi/full/10.26434/chemrxiv.15000799/v1)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Per-target variational quantum circuits vs. classical ML for predicting pesticide environmental fate properties** — a 6-qubit circuit for DegT50 and a 12-qubit circuit for Koc, trained on 110 substances with 21 molecular descriptors from the EU SPIN database, benchmarked against Random Forest and Gradient Boosting, integrated with FOCUS regulatory fate models.

## Highlights

- **Per-target VQCs** — 6-qubit/5-layer for DegT50 (97 params) + 12-qubit/8-layer for Koc (301 params)
- **Early stopping** with patience=10 epochs to prevent overtraining
- **17 curated molecular descriptors** including microbial degradation proxies and photolability features
- **110 pesticide substances** from the EU SPIN database (SQLite-backed, validated SMILES)
- **Classical baselines** (Random Forest + Gradient Boosting) for systematic comparison
- **Hybrid QML+RF stacking** — learned blending weight α per property, optimized via LOO-CV
- **FOCUS regulatory pipeline** — feeds predictions into PEARL/GEM groundwater models → PEC (µg/L)
- **Field validation** against published groundwater monitoring data (8 substances)
- **Web dashboard** with 7 interactive panels

## Architecture

```
SMILES → RDKit descriptors → 17 features → [0, π] scaling
                                              ↓
                    ┌─────────────── Per-target VQC (PennyLane) ──────────────┐
                    │                                                         │
                    │  DegT50 circuit (6q/5L)      Koc circuit (12q/8L)      │
                    │  ├─ Hadamard + RZ encoding   ├─ Hadamard + RZ encoding │
                    │  ├─ IQP ZZ entanglement      ├─ IQP ZZ entanglement   │
                    │  ├─ Data re-uploading         ├─ RY cross-rotation     │
                    │  └─ 5 variational layers      ├─ Data re-uploading     │
                    │                               └─ 8 variational layers  │
                    │  ⟨Z₀⟩...⟨Z₅⟩ → readout       ⟨Z₀⟩...⟨Z₁₁⟩ → readout │
                    └─────────────────────────────────────────────────────────┘
                                              ↓
                              log₁₀(DegT50), log₁₀(Koc)
                                              ↓
                              FOCUS fate model (PEARL/GEM)
                                              ↓
                              PEC groundwater (µg/L)
```

## Molecular Features (21)

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
| 18 | heteroatom_ratio | DegT50-targeted | N/O/S/P density → microbial targeting |
| 19 | sp3_fraction | DegT50-targeted | Molecular shape → soil binding |
| 20 | henry_volatility | DegT50-targeted | Volatilization pathway proxy |
| 21 | oxidation_susceptibility | DegT50-targeted | P450 metabolic lability sites |

## Quick Start

```bash
# Clone and set up
git clone https://github.com/c-arda/Quantum-Pesticide-Fate-Modeling.git
cd Quantum-Pesticide-Fate-Modeling
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start the backend (trains per-target QML models on first run, ~40 min)
python backend/server.py

# Open the web UI
python3 -m http.server 8765
# Navigate to http://localhost:8765
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Backend health check |
| GET | `/api/substances` | List all 110 substances |
| GET | `/api/quantum/status` | Per-target circuit info (8q DegT50, 12q Koc) |
| GET | `/api/quantum/predict/<name>` | Predict DegT50/Koc for a substance |
| GET | `/api/classical-baseline` | RF + GBM cross-validation results |
| GET | `/api/error-analysis` | Prediction errors by chemical class |
| GET | `/api/hybrid-results` | Hybrid QML+RF stacking results |
| POST | `/api/run` | Run full FOCUS fate simulation |

## Cross-Validation Results

*Results with 60-epoch training on 110 unique substances, 21 features.*

| Model | DegT50 R² | Koc R² | Notes |
|-------|-----------|--------|-------|
| Random Forest (LOO) | **0.287** | **0.759** | 200 trees, 21 features |
| Gradient Boosting (LOO) | 0.283 | 0.752 | 200 estimators, 21 features |
| Hybrid QML+RF (nested CV) | 0.288 | 0.750 | α=0.20±0.02, ΔR²=+0.001 |
| MLP Neural Network (LOO) | 0.075 | 0.497 | 64-32 hidden, 21 features |
| QML 8q+12q (5-fold) | −0.028 | 0.269 | Per-target, 17+21 features |
| QML 12q (Phase 4d) | −0.141 | 0.412 | Overfitting baseline |

**Key finding:** The VQC does not outperform properly feature-engineered Random Forest. The hybrid adds ΔR²=+0.001 — negligible and not statistically significant.

## Project Structure

```
qp-fate/
├── index.html              # Web UI (SPA)
├── app.js                  # Frontend logic
├── styles.css              # UI styling
├── requirements.txt        # Python dependencies
├── backend/
│   ├── server.py           # Flask API server
│   ├── quantum_predictor.py # Per-target VQC (6q DegT50 + 12q Koc)
│   ├── classical_predictor.py # RF + GBM baselines
│   ├── hybrid_predictor.py # QML+RF stacking
│   ├── spin_database.py    # SQLite loader (110 substances)
│   ├── substances.db       # SQLite database
│   ├── migrate_to_sqlite.py # Dict → SQLite migration
│   ├── fate_model.py       # FOCUS PEARL/GEM fate model
│   ├── field_data.py       # Field validation data
│   ├── aop_features.py     # AOP-Wiki MoA pathway mapping
│   └── focus_scenarios.py  # 9 FOCUS groundwater scenarios
├── manuscript/
│   ├── main.tex            # LaTeX manuscript
│   ├── references.bib      # 22 references
│   ├── generate_figures.py # Publication figure generation
│   └── figures/            # 8 figures (PDF + PNG)
```

## References

- [PennyLane](https://pennylane.ai) — Quantum ML framework
- [FOCUS](https://focus.jrc.ec.europa.eu) — Forum for Co-ordination of pesticide fate models
- [pesticidemodels.eu](https://pesticidemodels.eu) — EU pesticide fate model hub
- [SPIN 4.4](https://pesticidemodels.eu/spin/) — Substances Plug-IN database

## Author

Celal Arda — [ORCID 0009-0006-4563-8325](https://orcid.org/0009-0006-4563-8325)

## License

MIT — see [LICENSE](LICENSE)
