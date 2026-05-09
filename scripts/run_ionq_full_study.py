"""
Full Aria-1 hosted-sim study: 110 compounds × {deg, koc} = 220 jobs.
====================================================================
Resume-friendly: skips any compound whose result is already cached.
Logs progress per compound. Aggregates a single index file at the end.

Usage:
  IONQ_API_KEY=$(cat ~/.ionq_api_key) python scripts/run_ionq_full_study.py
  IONQ_API_KEY=$(cat ~/.ionq_api_key) python scripts/run_ionq_full_study.py --shots 1024 --noise aria-1
  IONQ_API_KEY=$(cat ~/.ionq_api_key) python scripts/run_ionq_full_study.py --only chlorpyrifos --target deg

Cache layout:
  backend/.qml_cache/ionq_runs/<noise_model>/<slug>__<target>__<shots>sh__w<sha8>.json
  backend/.qml_cache/ionq_runs/<noise_model>/_index.json   ← summary table
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import quantum_predictor as qp
from backend.spin_database import SUBSTANCES
from backend.ionq_engine import (
    predict_via_ionq,
    DEFAULT_SHOTS, DEFAULT_NOISE_MODEL, CACHE_ROOT,
    weights_sha256_cached, _slug,
)


def _index_path(noise_model):
    return os.path.join(CACHE_ROOT, _slug(noise_model), "_index.json")


def _write_index(noise_model, rows, started, finished, n_cached, n_submitted, n_failed):
    path = _index_path(noise_model)
    payload = {
        "noise_model": noise_model,
        "weights_sha256": weights_sha256_cached(),
        "started_utc": started,
        "finished_utc": finished,
        "n_compounds": len({r["name"] for r in rows}),
        "n_predictions": len(rows),
        "n_cached_hits": n_cached,
        "n_submitted": n_submitted,
        "n_failed": n_failed,
        "rows": rows,
    }
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shots", type=int, default=DEFAULT_SHOTS)
    parser.add_argument("--noise", default=DEFAULT_NOISE_MODEL)
    parser.add_argument("--only", default=None,
                        help="filter compounds by case-insensitive name substring")
    parser.add_argument("--target", choices=["deg", "koc", "both"], default="both")
    parser.add_argument("--max-compounds", type=int, default=None)
    args = parser.parse_args()

    if not os.environ.get("IONQ_API_KEY"):
        print("ERROR: IONQ_API_KEY env var not set", file=sys.stderr)
        return 2

    # Compound selection
    subs = list(SUBSTANCES)
    if args.only:
        needle = args.only.lower()
        subs = [s for s in subs if needle in (s.get("name") or "").lower()]
    if args.max_compounds:
        subs = subs[: args.max_compounds]

    targets = ["deg", "koc"] if args.target == "both" else [args.target]
    total = len(subs) * len(targets)

    started = datetime.now(timezone.utc).isoformat()
    print(f"\n{'='*78}")
    print(f"IonQ Aria-1 hosted-sim full study")
    print(f"  noise_model: {args.noise}")
    print(f"  shots:       {args.shots}")
    print(f"  compounds:   {len(subs)}")
    print(f"  targets:     {targets}")
    print(f"  total jobs:  {total}")
    print(f"  started:     {started}")
    print(f"{'='*78}\n")

    rows = []
    n_cached = 0
    n_submitted = 0
    n_failed = 0
    t_start = time.time()

    for i, sub in enumerate(subs):
        for target in targets:
            try:
                r = predict_via_ionq(
                    sub, target=target,
                    shots=args.shots, noise_model=args.noise,
                )
                if r["cached"]:
                    n_cached += 1
                    tag = "cache"
                else:
                    n_submitted += 1
                    tag = f"new {r['elapsed_s']:.1f}s"
            except Exception as e:
                n_failed += 1
                tag = f"FAIL {type(e).__name__}: {e}"
                r = {
                    "name": sub.get("name"),
                    "cas": sub.get("cas"),
                    "target": target,
                    "error": str(e),
                }

            rows.append(r)
            done = i * len(targets) + targets.index(target) + 1
            elapsed = time.time() - t_start
            rate = done / elapsed if elapsed > 0 else 0
            eta = (total - done) / rate if rate > 0 else 0
            print(f"[{done:3d}/{total}] {sub['name']:35s} {target} -> {tag}"
                  f"   rate={rate:.2f}/s  ETA={eta/60:.1f}min")

            # Save index periodically (every 10 jobs)
            if done % 10 == 0:
                _write_index(args.noise, rows, started,
                             datetime.now(timezone.utc).isoformat(),
                             n_cached, n_submitted, n_failed)

    finished = datetime.now(timezone.utc).isoformat()
    _write_index(args.noise, rows, started, finished, n_cached, n_submitted, n_failed)

    print(f"\n{'='*78}")
    print(f"Complete. cached={n_cached}  submitted={n_submitted}  failed={n_failed}")
    print(f"Index: {_index_path(args.noise)}")
    return 0 if n_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
