# Quantum-Enhanced Pesticide Fate Modeling

**Project:** Investigating how quantum computing can accelerate European pesticide environmental fate modeling (FOCUS/EFM framework).

## Background

This project explores opportunities to leverage quantum computing to speed up the currently slow, computationally intensive process of pesticide exposure assessment that underpins EU regulatory decisions under Regulation (EC) 1107/2009.

## Key Tools & Data Sources

| Resource | Description |
|----------|-------------|
| [pesticidemodels.eu](https://pesticidemodels.eu) | Hub for EU pesticide fate models (Wageningen UR / RIVM) |
| [ESDAC](https://esdac.jrc.ec.europa.eu) | European Soil Data Centre (JRC) — soil data, FOCUS scenarios |
| GEM 4.4.2 | Greenhouse Emission Model — simulates pesticide movement in soil |
| SPIN 4.4 | Substances Plug-IN — substance property database for GEM/PEARL/SWASH/TOXSWA |
| FOCUS framework | Standardized scenarios for PEC calculations (groundwater + surface water) |

## Project Goals

1. **Research** — Map the computational bottlenecks in EU pesticide fate modeling
2. **Feasibility** — Identify where quantum algorithms (VQE, QAOA, HHL) provide genuine speedup
3. **Prototype** — Build proof-of-concept quantum circuits for key sub-problems
4. **Tool** — Create a modern data-integration layer over ESDAC/SPIN/GEM data

## Status

- [x] Initial research and landscape survey
- [x] Web interface dashboard (substance lookup, FOCUS scenarios, quantum status, run config)
- [ ] Detailed computational bottleneck analysis
- [ ] Quantum algorithm mapping
- [ ] Prototype development

## Running the Web Interface

```bash
cd "Quantum Pesticide Fate Modeling"
python3 -m http.server 8765
# Open http://localhost:8765 in your browser
```
