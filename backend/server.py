"""
Flask API Server — Quantum Pesticide Fate Modeling
====================================================
Serves the backend API at localhost:5000 with endpoints for:
  - Substance lookup (SPIN database)
  - FOCUS scenario data
  - Quantum ML predictions
  - Fate model simulations
"""

import sys
import os
import json
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.spin_database import (
    get_all_substances, get_substance_by_name,
    search_substances, get_substance_classes, get_molecular_descriptors
)
from backend.focus_scenarios import (
    get_all_scenarios, get_scenario_by_name, get_scenario_summary
)
from backend.fate_model import run_comparison
from backend.quantum_predictor import (
    predict_all, batch_predict, get_circuit_info,
    run_cross_validation
)

app = Flask(__name__)
CORS(app)


# ── Health check ────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "qp-fate-backend"})


# ── Substances ──────────────────────────────────────────────────────

@app.route("/api/substances")
def api_substances():
    """List all substances, optionally filtered by query and class."""
    query = request.args.get("q", "")
    cls_filter = request.args.get("cls", None)
    substances = search_substances(query, cls_filter)
    return jsonify({
        "count": len(substances),
        "substances": substances,
        "classes": get_substance_classes(),
    })


@app.route("/api/substances/<name>")
def api_substance_detail(name):
    """Get a single substance by name."""
    sub = get_substance_by_name(name)
    if not sub:
        return jsonify({"error": f"Substance '{name}' not found"}), 404
    descriptors = get_molecular_descriptors(sub)
    return jsonify({"substance": sub, "descriptors": descriptors})


# ── Scenarios ───────────────────────────────────────────────────────

@app.route("/api/scenarios")
def api_scenarios():
    """List all FOCUS scenarios."""
    scenarios = get_all_scenarios()
    summaries = [get_scenario_summary(s) for s in scenarios]
    return jsonify({
        "count": len(summaries),
        "scenarios": summaries,
    })


@app.route("/api/scenarios/<name>")
def api_scenario_detail(name):
    """Get full scenario detail including soil profile."""
    scenario = get_scenario_by_name(name)
    if not scenario:
        return jsonify({"error": f"Scenario '{name}' not found"}), 404
    return jsonify({"scenario": scenario})


# ── Quantum predictions ────────────────────────────────────────────

@app.route("/api/quantum/status")
def api_quantum_status():
    """Return quantum circuit info and training status."""
    try:
        info = get_circuit_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/api/quantum/predict/<name>")
def api_quantum_predict(name):
    """Predict DegT50 and Koc for a substance using QML."""
    sub = get_substance_by_name(name)
    if not sub:
        return jsonify({"error": f"Substance '{name}' not found"}), 404
    try:
        result = predict_all(sub)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/api/quantum/predict-all")
def api_quantum_predict_all():
    """Batch predict DegT50 and Koc for all substances."""
    try:
        substances = get_all_substances()
        results = batch_predict(substances)
        return jsonify({
            "count": len(results),
            "predictions": results,
        })
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/api/quantum/cross-validation")
def api_quantum_cv():
    """Run or return cached leave-one-out cross-validation results."""
    try:
        results = run_cross_validation()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


# ── Field Validation ───────────────────────────────────────────────

from backend.field_data import (
    get_all_field_data, get_field_data, compare_model_vs_field,
    get_validation_substances
)


@app.route("/api/validation")
def api_validation():
    """Run model for all validation substances and compare against field data."""
    try:
        all_field = get_all_field_data()
        comparisons = []
        quantum_available = False

        # Check if quantum weights are cached (don't trigger training)
        from backend.quantum_predictor import _cached_weights
        quantum_available = _cached_weights is not None

        for sub_name, field in all_field.items():
            sub = get_substance_by_name(sub_name)
            if not sub:
                continue
            scn = get_scenario_by_name(field["scenario"])
            if not scn:
                continue

            # Get quantum predictions only if model is already trained
            quantum_params = None
            if quantum_available:
                try:
                    qpred = predict_all(sub)
                    quantum_params = {
                        "degT50_soil": qpred["degtl50"]["predicted_days"],
                        "koc": qpred["koc"]["predicted_ml_g"],
                    }
                except Exception:
                    quantum_params = None

            # Run simulation (classical always, quantum if available)
            result = run_comparison(sub, scn, 20, quantum_params)

            # Compare with field data
            comparison = compare_model_vs_field(
                model_pec_classical=result["classical"]["pec_80th"],
                model_pec_quantum=result["quantum"]["pec_80th"] if result.get("quantum") else None,
                model_leached_classical=result["classical"]["total_leached"],
                model_leached_quantum=result["quantum"]["total_leached"] if result.get("quantum") else None,
                field_data=field,
            )
            if quantum_params:
                comparison["quantum_predictions"] = {
                    "degT50_predicted": quantum_params["degT50_soil"],
                    "degT50_experimental": sub["degT50_soil"],
                    "koc_predicted": quantum_params["koc"],
                    "koc_experimental": sub["koc"],
                }
            comparisons.append(comparison)

        return jsonify({
            "count": len(comparisons),
            "quantum_available": quantum_available,
            "validation_substances": get_validation_substances(),
            "comparisons": comparisons,
        })
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


# ── Classical ML Baseline ──────────────────────────────────────────

from backend.classical_predictor import train_classical_baseline


@app.route("/api/classical-baseline")
def api_classical_baseline():
    """Return classical ML baseline results (RF + GBM with LOO and 5-fold CV)."""
    try:
        results = train_classical_baseline()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


# ── Hybrid QML+RF Stacking ────────────────────────────────────────

from backend.hybrid_predictor import get_hybrid_results


@app.route("/api/hybrid-results")
def api_hybrid_results():
    """Return hybrid stacking model results."""
    try:
        results = get_hybrid_results()
        return jsonify(results or {"error": "No data available"})
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


# ── Error Analysis by Chemical Class ──────────────────────────────

@app.route("/api/error-analysis")
def api_error_analysis():
    """Return prediction errors grouped by chemical class."""
    try:
        cl_data = train_classical_baseline()
        rf_results = cl_data["models"]["RandomForest"]["loo"]["results"]

        cls_map = {s["name"]: s["cls"] for s in get_all_substances()}

        from collections import defaultdict
        deg_by_cls = defaultdict(list)
        koc_by_cls = defaultdict(list)

        for r in rf_results:
            cls = cls_map.get(r["name"], "Unknown")
            deg_by_cls[cls].append({
                "name": r["name"],
                "error": abs(r["deg_exp"] - r["deg_pred"]),
                "pred_days": r["deg_pred_days"],
                "exp_days": r["deg_exp_days"],
            })
            koc_by_cls[cls].append({
                "name": r["name"],
                "error": abs(r["koc_exp"] - r["koc_pred"]),
                "pred_ml_g": r.get("koc_pred_val", 10 ** r["koc_pred"]),
                "exp_ml_g": r.get("koc_exp_val", 10 ** r["koc_exp"]),
            })

        def summarize(cls_dict):
            import numpy as np
            summary = []
            for cls, items in sorted(cls_dict.items(), key=lambda x: -np.mean([i["error"] for i in x[1]])):
                errs = [i["error"] for i in items]
                summary.append({
                    "cls": cls,
                    "n": len(items),
                    "mean_error": round(np.mean(errs), 3),
                    "max_error": round(np.max(errs), 3),
                    "substances": items,
                })
            return summary

        return jsonify({
            "deg_by_class": summarize(deg_by_cls),
            "koc_by_class": summarize(koc_by_cls),
        })
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


# ── Simulation ──────────────────────────────────────────────────────

@app.route("/api/run", methods=["POST"])
def api_run_simulation():
    """
    Run a pesticide fate simulation.

    POST body (JSON):
        substance: str — substance name
        scenario: str — FOCUS scenario name
        years: int (default 20)
        quantum: bool (default true) — whether to include quantum predictions
    """
    data = request.get_json() or {}
    sub_name = data.get("substance", "")
    scn_name = data.get("scenario", "")
    years    = int(data.get("years", 20))
    use_quantum = data.get("quantum", True)

    sub = get_substance_by_name(sub_name)
    if not sub:
        return jsonify({"error": f"Substance '{sub_name}' not found"}), 404

    scn = get_scenario_by_name(scn_name)
    if not scn:
        return jsonify({"error": f"Scenario '{scn_name}' not found"}), 404

    try:
        quantum_params = None
        if use_quantum:
            # Get quantum-predicted properties
            qpred = predict_all(sub)
            quantum_params = {
                "degT50_soil": qpred["degtl50"]["predicted_days"],
                "koc": qpred["koc"]["predicted_ml_g"],
            }

        result = run_comparison(sub, scn, years, quantum_params)

        # Include quantum prediction metadata if used
        if use_quantum and quantum_params:
            result["quantum_predictions"] = {
                "degT50_predicted": quantum_params["degT50_soil"],
                "degT50_experimental": sub["degT50_soil"],
                "koc_predicted": quantum_params["koc"],
                "koc_experimental": sub["koc"],
            }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


# ── Main ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  QP-FATE Backend — Quantum Pesticide Fate Modeling")
    print("  API running at http://localhost:5000")
    print("=" * 60)
    print()
    print("Endpoints:")
    print("  GET  /api/health")
    print("  GET  /api/substances          ?q=...&cls=...")
    print("  GET  /api/substances/<name>")
    print("  GET  /api/scenarios")
    print("  GET  /api/scenarios/<name>")
    print("  GET  /api/quantum/status")
    print("  GET  /api/quantum/predict/<name>")
    print("  GET  /api/quantum/predict-all")
    print("  POST /api/run                 {substance, scenario, years, quantum}")
    print()

    app.run(host="0.0.0.0", port=5000, debug=False)
