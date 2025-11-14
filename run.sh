#!/usr/bin/env bash
set -e

# Resolve the ShotMat root directory (where this script lives)
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 1. Core paths
export SHOTMAT_DATA="$HOME/ShotMatData"
export SHOTMAT_PROJECTS="$HOME/ShotMatProjects"
export SHOTMAT_PORT=8000

mkdir -p "$SHOTMAT_DATA" "$SHOTMAT_PROJECTS"

################################################################################
# 2. Start FastAPI in the background
################################################################################
echo "Starting FastAPI microservice..."

cd "$ROOT_DIR/api"

if [ ! -d ".venv" ]; then
  echo "No .venv in api/. Run setup first (python -m venv .venv && pip install -r requirements.txt)."
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

uvicorn shotmat_api.main:app \
  --host 127.0.0.1 \
  --port "$SHOTMAT_PORT" \
  --reload &
API_PID=$!

echo "FastAPI running on http://127.0.0.1:$SHOTMAT_PORT (PID: $API_PID)"

################################################################################
# 3. Run Flutter Web UI (foreground)
################################################################################
echo "Starting Flutter Web UI in Chrome..."

cd "$ROOT_DIR/ui_web"

# Enable web support (safe to run repeatedly)
flutter config --enable-web >/dev/null 2>&1

# This stays in the foreground so you see all output
flutter run -d chrome

################################################################################
# 4. Cleanup when Flutter exits
################################################################################
echo "Flutter exited, stopping FastAPI (PID: $API_PID)..."
kill "$API_PID" || true
