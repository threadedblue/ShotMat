#!/usr/bin/env bash
set -e

# 1. Core paths
export SHOTMAT_DATA="$HOME/ShotMatData"
export SHOTMAT_PROJECTS="$HOME/ShotMatProjects"
export SHOTMAT_PORT=8000
export SHOTMAT_UI_URL="http://127.0.0.1:5173"

mkdir -p "$SHOTMAT_DATA" "$SHOTMAT_PROJECTS"

### 2. Start FastAPI
cd "$(dirname "$0")/../api"

if [ ! -d ".venv" ]; then
  echo "No .venv in api/. Run scripts/setup_api.sh first."
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

uvicorn shotmat_api.main:app --host 127.0.0.1 --port "$SHOTMAT_PORT" &
API_PID=$!

### 3. Start frontend (Vite dev)
cd ../ui-web/shotmat-ui
npm run dev &
UI_PID=$!

### 4. Launch Chrome in app-mode with its own profile
CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SHOTMAT_CHROME_PROFILE="$HOME/.shotmat/chrome-profile"
mkdir -p "$SHOTMAT_CHROME_PROFILE"

"$CHROME_BIN" \
  --user-data-dir="$SHOTMAT_CHROME_PROFILE" \
  --app="$SHOTMAT_UI_URL" \
  >/dev/null 2>&1 &

echo "FastAPI PID: $API_PID"
echo "UI PID:      $UI_PID"
echo "ShotMat UI opened in Chrome app window."

wait $API_PID
wait $UI_PID

