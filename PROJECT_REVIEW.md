# PROJECT REVIEW — Quantum Pesticide Fate Modeling (QP-FATE)

> **Reviewed**: 2026-03-21 | **Status**: ◉ MATURE — JCIM submission active
> **Path**: `/home/ardac/Projects/Chemistry/Quantum Chemistry/Quantum Pesticide Fate Modeling/`

## Health Score: 8/10

## Structure
- `backend/` — Flask server, quantum/classical/hybrid predictors, SQLite DB (110 substances)
- `manuscript/` — LaTeX paper (main.tex, figures/, references.bib)
- `index.html` + `app.js` + `styles.css` — Web dashboard (7 panels)
- Full CI: requirements.txt, start script, API endpoints

## Issues

### ◆ HIGH — Uncommitted experiment results
```
?? EXPERIMENT_RESULTS.md             ← Overnight VQC architecture experiment
 M manuscript/manuscript.zip         ← Modified zip
```
**Fix**: `git add EXPERIMENT_RESULTS.md backend/.qml_cache/degt50_experiment* && git commit -m "feat: VQC architecture experiment — B_deep_narrow R²=0.066"`

### ◆ HIGH — Manuscript Table 3 needs updating
The overnight experiment found Variant B (8q/12L) achieves R²=0.066, a +0.207 improvement over the published baseline (−0.141). This is the best VQC result on this dataset.
**Fix**: Update Table 3 in `manuscript/main.tex` with Variant B results. Add architecture comparison figure.

### ◆ MEDIUM — Flask server running for 4 days
PID 348763 consuming 4.6 GB RAM, started Mar 17.
**Fix**: Consider stopping when not needed: `kill 348763`

### ◆ LOW — requirements.txt missing pennylane version pin
`pennylane>=0.39` but overnight ran on 0.44.0. Pin to tested version.
**Fix**: Update to `pennylane>=0.44`

## Action Plan
1. Commit experiment results and update manuscript
2. Add Variant B findings to Discussion section (depth > width insight)
3. Stop long-running Flask server if not needed
4. Consider rerunning Variant B with more epochs or LOO-CV for final numbers
