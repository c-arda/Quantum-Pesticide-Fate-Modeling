#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  QP-FATE — Quantum Pesticide Fate Modeling UI
#  Starts Flask backend (port 5000) + serves index.html
# ═══════════════════════════════════════════════════════════════
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly SCRIPT_DIR
readonly CONDA_ENV="fbond-env"
readonly CONDA_PATH="/home/ardac/miniconda3"
readonly PORT=5000

# ── Colors ───────────────────────────────────────────────────
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

cleanup() {
    local exit_code=$?
    printf '\n%bShutting down QP-FATE...%b\n' "$CYAN" "$NC"
    [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null && printf '%b  ◎ Backend stopped%b\n' "$GREEN" "$NC"
    exit "$exit_code"
}

trap cleanup EXIT INT TERM HUP

printf '%b═══ QP-FATE — Quantum Pesticide Fate Modeling ═══%b\n' "$GREEN" "$NC"

# 1. Activate conda environment
if command -v conda &>/dev/null; then
    eval "$(conda shell.bash hook)"
elif [[ -f "${CONDA_PATH}/etc/profile.d/conda.sh" ]]; then
    source "${CONDA_PATH}/etc/profile.d/conda.sh"
fi
conda activate "$CONDA_ENV" 2>/dev/null || {
    printf '%b  ◆ Failed to activate conda env %s%b\n' "$RED" "$CONDA_ENV" "$NC"
    exit 1
}
printf '%b  ◎ Conda environment: %s%b\n' "$GREEN" "$CONDA_ENV" "$NC"

# 2. Check dependencies
cd "$SCRIPT_DIR"
if ! python3 -c "import flask, flask_cors" &>/dev/null; then
    printf '%b  ◆ Installing missing dependencies...%b\n' "$YELLOW" "$NC"
    pip install -r requirements.txt
fi

# 3. Start Flask backend
printf '%b  ◎ Starting Flask backend on port %s...%b\n' "$GREEN" "$PORT" "$NC"
pkill -f "python3 backend/server.py" 2>/dev/null || true
sleep 0.5
python3 backend/server.py &
BACKEND_PID=$!

# 4. Wait for health
sleep 2
if curl -sf "http://localhost:${PORT}/api/health" >/dev/null 2>&1; then
    printf '%b═══ QP-FATE is LIVE ◎ ═══%b\n' "$GREEN" "$NC"
    printf '   ▸ Dashboard: http://localhost:%s\n' "$PORT"
    printf '   ▸ API:       http://localhost:%s/api/health\n' "$PORT"
else
    printf '%b  ◆ Backend may still be starting — check http://localhost:%s%b\n' "$YELLOW" "$PORT" "$NC"
fi

# 5. Open browser
if command -v xdg-open &>/dev/null; then
    xdg-open "http://localhost:${PORT}/index.html" 2>/dev/null &
fi

printf "\nPress Ctrl+C to stop...\n"
wait
