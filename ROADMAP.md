# QP-FATE Roadmap

## Completed ✅

### Phase 1: Data & Infrastructure
- Web UI with 7 panels (dashboard, substances, scenarios, quantum, validation, comparison, run)
- SPIN database: 111 substances with validated SMILES
- FOCUS scenario integration (9 groundwater scenarios)
- Flask API with 8+ endpoints

### Phase 2: Quantum ML
- 12-qubit VQC with data re-uploading (301 parameters)
- Incremental learning with Tanimoto novelty gate
- Lazy initialization for instant server startup
- LOO and k-fold cross-validation framework

### Phase 3: Classical Baseline & Validation
- Random Forest + Gradient Boosting baselines
- Field validation against 8 monitoring substances
- Feature importance analysis
- Git repository initialized

### Phase 4: Feature Engineering
- 17 molecular descriptors (was 12)
- Microbial proxies: n_hydrolyzable, n_halogens, bioaccessibility
- Blind-spot fixes: charge_state (pKa-based), conjugated_pi_size (photolability)
- 6 photolabile substances added (famoxadone, pyrimethanil, abamectin, etc.)
- Error-by-class analysis (45 chemical classes)
- Hybrid QML+RF stacking model (ready, awaiting QML CV)
- RF DegT50 R² improved +43% from feature engineering

---

## In Progress 🔄

### Phase 4b: Validation (60-epoch CV running)
- [ ] 5-fold CV with 60 epochs, 17 features, 111 substances (laptop16)
- [ ] LOO CV with 60 epochs (laptop32)
- [ ] Activate hybrid stacking once QML CV available
- [ ] Push validated results to GitHub

---

## Planned 📋

### Phase 5: Model Optimization
- [ ] Hyperparameter sweep (learning rate, n_layers, n_epochs)
- [ ] Uncertainty quantification via ensemble of 5 circuits
- [ ] Neural network baseline (MLPRegressor) for 3-way comparison
- [ ] Expand to 150+ substances

### Phase 6: Hardware Deployment
- [ ] Deploy to IBM Quantum via PennyLane qiskit plugin
- [ ] Noise-aware training with depolarizing channel
- [ ] Benchmark simulator vs real quantum hardware

### Phase 7: Publication
- [ ] Write results section (DegT50 quantum advantage analysis)
- [ ] Generate publication-quality figures
- [ ] EU regulatory submission template (Tier 1 FOCUS assessment)

### Phase 8: Production
- [ ] Active learning loop (suggest next substance to measure)
- [ ] REST API for regulatory submission tools
- [ ] Integration with FOCUS PEARL/PELMO models
- [ ] Scale to 500+ substances
