#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# provision_cluster_node.sh — Set up QP-FATE on a cluster node
# Run via: ssh laptop16 'bash -s' < scripts/provision_cluster_node.sh
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

PROJ_DIR="$HOME/Projects/Chemistry/Quantum Chemistry/Quantum Pesticide Fate Modeling"
REPO_URL="https://github.com/c-arda/Quantum-Pesticide-Fate-Modeling.git"

echo "◈ $(hostname) — Provisioning QP-FATE environment"

# ── 1. Clone repo if not present ──────────────────────────────────
if [ ! -d "$PROJ_DIR" ]; then
    echo "  → Cloning repo..."
    mkdir -p "$(dirname "$PROJ_DIR")"
    git clone "$REPO_URL" "$PROJ_DIR"
else
    echo "  → Repo exists, pulling latest..."
    cd "$PROJ_DIR" && git pull --ff-only origin main || git pull --ff-only origin master || echo "    (pull skipped)"
fi

cd "$PROJ_DIR"

# ── 2. Create venv ────────────────────────────────────────────────
if [ ! -d ".venv" ]; then
    echo "  → Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
echo "  → Python: $(python3 --version)"

# ── 3. Install dependencies (pinned to GnoSys versions) ──────────
echo "  → Installing packages..."
pip install --upgrade pip > /dev/null 2>&1

pip install \
    "pennylane>=0.44,<0.46" \
    "scikit-learn>=1.8,<1.9" \
    "numpy>=2.4,<3.0" \
    "rdkit>=2025.3" \
    "flask>=3.1" \
    "scipy>=1.15" \
    2>&1 | tail -5

# ── 4. Verify ─────────────────────────────────────────────────────
echo "  → Verifying..."
python3 -c "
import pennylane, sklearn, rdkit, numpy
print(f'  PennyLane={pennylane.__version__}')
print(f'  scikit-learn={sklearn.__version__}')
print(f'  RDKit={rdkit.__version__}')
print(f'  NumPy={numpy.__version__}')
"

echo "◈ $(hostname) — Provisioning complete ✓"
