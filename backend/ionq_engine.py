"""
IonQ Hosted-Sim Engine — primary scientific backend (Phase 6, Option B).
========================================================================
Submits the trained Phase 5a circuits to an IonQ hosted noisy simulator
(IonQ's own hardware-derived noise model) and caches per-compound results.

Default backend: forte-1 (Aria-1 deprecated on GCP marketplace, Amendment 3).
Other accepted IonQ noise_model identifiers (probed 2026-05-01):
  ideal, harmony, harmony-1, harmony-2, aria-1, aria-2, forte-1,
  forte-enterprise-1, ideal-sampled.

Design rationale (gate-2 parity test): local default.mixed and IonQ's hosted
noisy sims disagree by 2–4× the shot-noise floor. Rather than fit our local
noise model to IonQ's, use IonQ's directly — it's free (hosted sim is
unbilled), faster than local 12q density-matrix sim, and is the most credible
benchmark for what the matching QPU (qpu.forte-1) will return.

Cache key: (compound_cas_or_name, target, noise_model, shots, weights_sha256).
Cached results live in:
  backend/.qml_cache/ionq_runs/<noise_model>/<key>.json
A cache hit means zero new submissions / zero new queue time.

Public API:
  predict_via_ionq(substance, target, shots=1024, noise_model="forte-1",
                   force_resubmit=False) -> dict
"""

import hashlib
import json
import os
import re
import time

import numpy as np
import pennylane as qml
from pennylane import numpy as pnp

from backend import quantum_predictor as qp
from backend.ionq_noisy_simulator import IonQNoisySimulator

CIRCUIT_VERSION = "phase5a_v1"   # bump if _build_circuit_body changes
DEFAULT_SHOTS = 1024
DEFAULT_NOISE_MODEL = "forte-1"  # Amendment 3: aria-1 deprecated

CACHE_ROOT = os.path.join(qp.CACHE_DIR, "ionq_runs")


def _weights_sha256():
    """SHA-256 of the trained weights checkpoint — invalidates cache on retrain."""
    path = os.path.join(qp.CACHE_DIR, "weights_v2.npz")
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


_WEIGHTS_SHA_CACHE = None
def weights_sha256_cached():
    global _WEIGHTS_SHA_CACHE
    if _WEIGHTS_SHA_CACHE is None:
        _WEIGHTS_SHA_CACHE = _weights_sha256()
    return _WEIGHTS_SHA_CACHE


def _slug(s):
    """Filesystem-safe slug from substance name / CAS."""
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", s).strip("_")


def _cache_path(substance, target, noise_model, shots):
    key_base = substance.get("cas") or substance.get("name") or "unknown"
    sha8 = weights_sha256_cached()[:8]
    fname = f"{_slug(key_base)}__{target}__{shots}sh__w{sha8}.json"
    cache_dir = os.path.join(CACHE_ROOT, _slug(noise_model))
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, fname)


def _load_cached(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def _build_qnode(n_qubits, n_layers, shots, noise_model):
    dev = IonQNoisySimulator(
        wires=n_qubits, noise_model=noise_model, shots=shots
    )
    @qml.qnode(dev)
    def qn(features, weights):
        return qp._build_circuit_body(features, weights, n_qubits, n_layers)
    return qn


def predict_via_ionq(substance, target="deg",
                     shots=DEFAULT_SHOTS,
                     noise_model=DEFAULT_NOISE_MODEL,
                     force_resubmit=False):
    """
    Run substance through trained Phase 5a circuit on IonQ Aria-1 hosted
    noisy simulator. Cached per (substance, target, shots, noise_model,
    weights_sha).

    Returns dict with keys: name, cas, target, noise_model, shots,
    weights_sha256, circuit_version, expvals, prediction_log10, prediction,
    cached (bool), elapsed_s.
    """
    if target not in ("deg", "koc"):
        raise ValueError(f"target must be 'deg' or 'koc', got {target!r}")

    cache_path = _cache_path(substance, target, noise_model, shots)
    if not force_resubmit:
        cached = _load_cached(cache_path)
        if cached is not None:
            cached["cached"] = True
            return cached

    w = qp._load_cached_weights_raw()
    if w is None:
        raise RuntimeError("Cached weights missing")

    feat_full = qp.extract_features(substance)
    if target == "deg":
        feat = feat_full[qp.QML_DEG_FEATURE_INDICES]
        n_q, n_l = qp.N_QUBITS_DEG, qp.N_LAYERS_DEG
        weights = w["weights_deg"]
        readout = w["readout_deg"]
    else:
        feat = feat_full
        n_q, n_l = qp.N_QUBITS_KOC, qp.N_LAYERS_KOC
        weights = w["weights_koc"]
        readout = w["readout_koc"]

    qn = _build_qnode(n_q, n_l, shots, noise_model)

    t0 = time.time()
    expvals = [float(x) for x in qn(feat, weights)]
    elapsed = time.time() - t0

    pred_log = float(np.dot(np.array(readout[:n_q]), np.array(expvals)) + readout[n_q])

    result = {
        "name": substance.get("name"),
        "cas": substance.get("cas"),
        "target": target,
        "noise_model": noise_model,
        "shots": shots,
        "weights_sha256": weights_sha256_cached(),
        "circuit_version": CIRCUIT_VERSION,
        "n_qubits": n_q,
        "n_layers": n_l,
        "expvals": expvals,
        "prediction_log10": pred_log,
        "prediction": float(10 ** pred_log),
        "cached": False,
        "elapsed_s": round(elapsed, 2),
    }

    # Atomic write
    tmp = cache_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(result, f, indent=2)
    os.replace(tmp, cache_path)

    return result
