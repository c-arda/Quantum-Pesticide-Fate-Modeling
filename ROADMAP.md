# QP-FATE Roadmap

> Quantum-enhanced QSAR for pesticide environmental fate modeling under EC 1107/2009

---

## Completed

### Phase 1: Data Infrastructure ✓
*Milestone: First API response — substance lookup + FOCUS scenarios*

- Flask API server with 8+ REST endpoints
- SPIN database: **111 pesticide substances** with validated SMILES
- 9 FOCUS groundwater scenarios (Châteaudun → Porto)
- 1D fate model (PEARL/GEM-style convection-dispersion solver)
- Web UI (SPA) with 7 interactive panels

### Phase 2: Quantum ML Core ✓
*Milestone: First QML prediction — DegT50 and Koc from quantum circuit*

- 12-qubit variational quantum circuit (PennyLane `default.qubit`)
- 301 variational parameters, 5 rotation layers
- IQP-style ZZ entanglement + data re-uploading
- Incremental learning with Tanimoto novelty gate
- Lazy initialization for instant server startup (<1s)
- LOO and k-fold cross-validation framework

### Phase 3: Classical Baselines & Validation ✓
*Milestone: First head-to-head — QML vs RF vs GBM*

- Random Forest + Gradient Boosting baselines (scikit-learn)
- LOO and 5-fold CV for both classical and QML
- Field validation against 8 published groundwater monitoring substances
- Feature importance analysis (RF permutation importance)
- Git repository initialized, `.gitignore` configured

### Phase 4: Feature Engineering ✓
*Milestone: DegT50 RF R² improved +43% from new features alone*

**Phase 4a — Microbial degradation proxies:**
- `n_hydrolyzable` — enzymatic attack sites (ester, amide, etc.)
- `n_halogens` — biodegradation resistance
- `bioaccessibility` — log₁₀(solubility/koc), microbial availability
- Feature count: 12 → 15

**Phase 4b — Blind-spot corrections:**
- `charge_state` — pKa-based cationic correction (Diquat fix)
- `conjugated_pi_size` — photolability proxy (Rotenone fix)
- 6 photolabile substances added (Famoxadone, Pyrimethanil, Abamectin, Fenhexamid, Prothioconazole, Difenoconazole)
- Feature count: 15 → 17, substances: 105 → 111
- Prothioconazole SMILES corrected (dithiazolethione form)

**Phase 4c — UI & documentation polish:**
- Professional README with architecture diagram, API docs, feature table
- MIT LICENSE, ROADMAP.md
- UI redesign: IBM Plex typography, noise texture, staggered animations
- All emoji icons → unicode geometric symbols (◈ ◎ ◉ ◆ ▣ ⬡)
- Dynamic `/api/quantum/cv-results` endpoint (replaces hardcoded values)
- Error-by-class analysis (45 chemical classes)
- Hybrid QML+RF stacking model (α-weighted, ready for QML CV)

---

## In Progress 🔄

### Phase 4d: 60-Epoch QML Validation
*Milestone: Confirmed QML convergence with 17 features*

- [ ] 5-fold CV with 60 epochs — laptop16 (est. ~12:30 today)
- [ ] LOO CV with 60 epochs — laptop32 (est. ~tomorrow morning)
- [ ] Compare QML R² vs classical baselines with new features
- [ ] Activate hybrid stacking (optimize α weight)
- [ ] Push validated results to GitHub

---

## Planned

### Phase 5: Model Optimization
*Goal: Maximize DegT50 R² and establish quantum advantage*

- [ ] Hyperparameter sweep (learning rate: 0.01–0.1, layers: 3–8, epochs: 40–100)
- [ ] Uncertainty quantification via ensemble of 5 independently seeded circuits
- [ ] Neural network baseline (MLPRegressor) for 3-way comparison
- [ ] Expand database to 150+ substances (add organophosphates, pyrethroids)
- [ ] Residual analysis: cluster errors by chemical class, identify new blind spots

### Phase 6: Hardware Deployment
*Goal: Real quantum hardware benchmark*

- [ ] Deploy to IBM Quantum via `pennylane-qiskit` plugin
- [ ] Noise-aware training with depolarizing + readout error channels
- [ ] Benchmark: simulator vs IBM Brisbane/Osaka (127-qubit)
- [ ] Explore PennyLane Lightning GPU for faster simulation

### Phase 7: Publication & Regulatory
*Goal: Peer-reviewed paper + EU regulatory proof-of-concept*

- [ ] Write results paper: "Quantum QSAR for Pesticide Environmental Fate"
- [ ] Generate publication-quality figures (R² plots, circuit diagrams, feature importance)
- [ ] Tier 1 FOCUS assessment template using QML-predicted parameters
- [ ] Compare against EFSA/OECD accepted QSAR approaches

### Phase 8: Ecotoxicology & 3R (Bf3R Integration)
*Goal: Reduce animal testing in pesticide registration*

Inspired by [Bf3R — Ersatzmethoden](https://www.bf3r.de/angebote/ersatzmethoden/) and the 3R principle (Replace, Reduce, Refine).

- [ ] Add ecotoxicological endpoints: LC50 (fish/daphnia), LD50 (bees/rats), NOAEL
- [ ] Source training data from EPA ECOTOX, OECD eChemPortal, ECHA REACH dossiers
- [ ] Train 12-qubit VQC on toxicity endpoints using same molecular descriptor framework
- [ ] Support **read-across** — quantitative structural similarity via QML features
- [ ] Submit validated methods to EURL ECVAM / Bf3R for regulatory acceptance
- [ ] Target: in silico replacement of acute oral toxicity (OECD TG 423) for new pesticides

### Phase 9: Production Scale
*Goal: Operational tool for regulatory submissions*

- [ ] Active learning loop (suggest next substance to measure experimentally)
- [ ] REST API for integration with regulatory submission software
- [ ] Direct integration with FOCUS PEARL/PELMO/MACRO models
- [ ] Scale database to 500+ substances
- [ ] Multi-endpoint prediction (DegT50 + Koc + GUS + PEC in one run)

---

## Key Metrics Tracker

| Metric | Phase 2 | Phase 3 | Phase 4 | Phase 4d (pending) |
|--------|---------|---------|---------|---------------------|
| Substances | 50 | 50 | 111 | 111 |
| Features | 8 | 12 | 17 | 17 |
| Qubits | 6 | 12 | 12 | 12 |
| RF DegT50 R² (LOO) | — | 0.191 | 0.194 | pending |
| GBM DegT50 R² (LOO) | — | 0.211 | 0.223 | pending |
| QML DegT50 R² (5-fold) | 0.258 | 0.258 | *25ep: 0.015* | *60ep: pending* |
| RF Koc R² (LOO) | — | 0.766 | 0.766 | pending |
| QML Koc R² (5-fold) | 0.321 | 0.321 | *25ep: 0.155* | *60ep: pending* |
| CV Epochs | 25 | 25 | 25 | **60** |

---

## Timeline

```
2026-03 ████████████░░░░░░░░░░░░ Phase 1-4 ✓
2026-03 ░░░░░░░░░░░░████░░░░░░░░ Phase 4d (this week)
2026-04 ░░░░░░░░░░░░░░░░████░░░░ Phase 5 (optimization)
2026-Q2 ░░░░░░░░░░░░░░░░░░░░████ Phase 6 (hardware)
2026-Q3 ░░░░░░░░░░░░░░░░░░░░░░██ Phase 7 (publication)
2027    ░░░░░░░░░░░░░░░░░░░░░░░█ Phase 8 (3R / Bf3R)
2027+   ░░░░░░░░░░░░░░░░░░░░░░░░ Phase 9 (production)
```
