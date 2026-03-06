"""
AOP-Informed Mechanism Features
================================
Maps pesticide chemical classes to adverse outcome pathway (AOP)
mechanism-of-action categories derived from AOP Wiki data.

Provides binary feature encoding for 6 MoA pathway categories:
  1. AChE inhibition (organophosphates, carbamates)
  2. GABA / ion channel disruption (pyrethroids, phenylpyrazoles, cyclohexanediones)
  3. Mitochondrial respiration disruption (SDHI, strobilurins, rotenoids)
  4. Nicotinic acetylcholine receptor (neonicotinoids, spinosyns, sulfoximines)
  5. Endocrine disruption (triazines, phenoxyacetic acids, chloroacetamides)
  6. Cell division / tubulin disruption (benzimidazoles, dinitroanilines, benzoylureas)

These features encode biological *mechanism* rather than chemical *structure*,
potentially capturing degradation-relevant information not in molecular
descriptors (e.g., AChE inhibitors tend to hydrolyze faster because their
labile phosphoester/carbamate bonds are also targets for soil enzymes).
"""

import numpy as np

# ── MoA pathway mapping: chemical class → pathway categories ────────
# Based on AOP Wiki MIE analysis (AOP:3,4,10,16,17,19,23,25,26,29)
# and established pesticide toxicology (IRAC/FRAC/HRAC mode-of-action)

MOA_PATHWAYS = {
    "ache_inhibitor": {
        "description": "AChE inhibition (AOP:16) — phosphoester/carbamate hydrolysis-prone",
        "classes": {
            "Organophosphate", "Carbamate", "Phenylcarbamate", "Phosphonate",
        },
    },
    "gaba_ion_channel": {
        "description": "GABA-gated chloride channel / sodium channel (AOP:10)",
        "classes": {
            "Pyrethroid", "Phenylpyrazole", "Cyclohexanedione", "Oxadiazine",
            "Avermectin",
        },
    },
    "mitochondrial": {
        "description": "Mitochondrial respiration disruption (AOP:3,26)",
        "classes": {
            "SDHI", "Strobilurin", "Rotenoid",
        },
    },
    "nachr_agonist": {
        "description": "Nicotinic AChR agonist/modulator",
        "classes": {
            "Neonicotinoid", "Spinosyn", "Sulfoximine", "Butenolide",
        },
    },
    "endocrine_disruptor": {
        "description": "Endocrine disruption — estrogen/androgen/thyroid (AOP:7,19,23,25,29)",
        "classes": {
            "Triazine", "Triazinone", "Phenoxyacetic acid", "Phenoxypropionic acid",
            "Phenoxyalkanoic", "Chloroacetamide", "Morpholine",
        },
    },
    "cell_division": {
        "description": "Tubulin / cell division disruption",
        "classes": {
            "Benzimidazole", "Dinitroaniline", "Benzoylurea",
        },
    },
}

# All pathway names in fixed order for consistent feature vectors
PATHWAY_NAMES = sorted(MOA_PATHWAYS.keys())


def get_moa_features(substance):
    """
    Return binary MoA feature vector for a substance.

    Parameters
    ----------
    substance : dict
        Substance record from spin_database (must have 'cls' field).

    Returns
    -------
    np.ndarray of shape (6,)
        Binary features: 1 if substance class maps to that pathway, 0 otherwise.
    """
    cls = substance.get("cls", "")
    features = np.zeros(len(PATHWAY_NAMES), dtype=float)

    for i, pathway in enumerate(PATHWAY_NAMES):
        if cls in MOA_PATHWAYS[pathway]["classes"]:
            features[i] = 1.0

    return features


def get_moa_feature_names():
    """Return list of MoA feature names in canonical order."""
    return [f"moa_{p}" for p in PATHWAY_NAMES]


def assess_coverage():
    """
    Assess MoA feature coverage across all substances.

    Returns
    -------
    dict with coverage statistics and per-pathway counts.
    """
    from backend.spin_database import SUBSTANCES

    n = len(SUBSTANCES)
    has_any_moa = 0
    pathway_counts = {p: 0 for p in PATHWAY_NAMES}
    unmapped = []

    for sub in SUBSTANCES:
        feats = get_moa_features(sub)
        if feats.sum() > 0:
            has_any_moa += 1
        else:
            unmapped.append(sub["name"])

        for i, p in enumerate(PATHWAY_NAMES):
            if feats[i] > 0:
                pathway_counts[p] += 1

    return {
        "n_substances": n,
        "n_mapped": has_any_moa,
        "coverage_pct": round(100 * has_any_moa / n, 1),
        "pathway_counts": pathway_counts,
        "unmapped_substances": unmapped,
        "n_unmapped": len(unmapped),
    }


def test_feature_impact():
    """
    Quick test: does adding MoA features improve RF DegT50 LOO R²?

    Compares:
      - RF with 17 molecular descriptors only
      - RF with 17 descriptors + 6 MoA features (23 total)

    Returns dict with R² comparison.
    """
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import cross_val_predict, LeaveOneOut
    from sklearn.metrics import r2_score

    from backend.quantum_predictor import extract_features
    from backend.spin_database import SUBSTANCES

    # Base features (17 molecular descriptors)
    X_base = np.array([extract_features(s) for s in SUBSTANCES])
    y_deg = np.array([np.log10(max(s["degT50_soil"], 0.1)) for s in SUBSTANCES])
    y_koc = np.array([np.log10(max(s["koc"], 0.1)) for s in SUBSTANCES])

    # Extended features (17 + 6 MoA = 23)
    moa_feats = np.array([get_moa_features(s) for s in SUBSTANCES])
    X_extended = np.hstack([X_base, moa_feats])

    rf_params = {"n_estimators": 200, "max_depth": 10, "random_state": 42}
    loo = LeaveOneOut()

    # Baseline RF (17 features)
    pred_deg_base = cross_val_predict(
        RandomForestRegressor(**rf_params), X_base, y_deg, cv=loo
    )
    pred_koc_base = cross_val_predict(
        RandomForestRegressor(**rf_params), X_base, y_koc, cv=loo
    )

    # Extended RF (23 features)
    pred_deg_ext = cross_val_predict(
        RandomForestRegressor(**rf_params), X_extended, y_deg, cv=loo
    )
    pred_koc_ext = cross_val_predict(
        RandomForestRegressor(**rf_params), X_extended, y_koc, cv=loo
    )

    return {
        "n_base_features": X_base.shape[1],
        "n_extended_features": X_extended.shape[1],
        "n_moa_features": moa_feats.shape[1],
        "base_deg_r2": round(float(r2_score(y_deg, pred_deg_base)), 4),
        "extended_deg_r2": round(float(r2_score(y_deg, pred_deg_ext)), 4),
        "deg_r2_delta": round(float(r2_score(y_deg, pred_deg_ext) - r2_score(y_deg, pred_deg_base)), 4),
        "base_koc_r2": round(float(r2_score(y_koc, pred_koc_base)), 4),
        "extended_koc_r2": round(float(r2_score(y_koc, pred_koc_ext)), 4),
        "koc_r2_delta": round(float(r2_score(y_koc, pred_koc_ext) - r2_score(y_koc, pred_koc_base)), 4),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("AOP-Informed MoA Feature Assessment")
    print("=" * 60)

    # Coverage analysis
    cov = assess_coverage()
    print(f"\nCoverage: {cov['n_mapped']}/{cov['n_substances']} "
          f"substances mapped ({cov['coverage_pct']}%)")
    print(f"\nPathway counts:")
    for p, count in sorted(cov["pathway_counts"].items(), key=lambda x: -x[1]):
        desc = MOA_PATHWAYS[p]["description"]
        print(f"  {p:22s} {count:3d} substances — {desc}")

    print(f"\nUnmapped ({cov['n_unmapped']}): {', '.join(cov['unmapped_substances'][:10])}...")

    # Feature impact test
    print(f"\n{'=' * 60}")
    print("Testing RF DegT50/Koc R² with and without MoA features...")
    print("(LOO CV with RandomForest, n_estimators=200)")
    print("=" * 60)

    impact = test_feature_impact()
    print(f"\nDegT50 R²: {impact['base_deg_r2']:.4f} → {impact['extended_deg_r2']:.4f} "
          f"(Δ = {impact['deg_r2_delta']:+.4f})")
    print(f"Koc    R²: {impact['base_koc_r2']:.4f} → {impact['extended_koc_r2']:.4f} "
          f"(Δ = {impact['koc_r2_delta']:+.4f})")

    verdict = "IMPROVES" if impact["deg_r2_delta"] > 0 else "NO IMPROVEMENT"
    print(f"\nVerdict: MoA features {verdict} DegT50 prediction")
