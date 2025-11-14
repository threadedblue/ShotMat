#!/usr/bin/env bash

# Build Flutter Web & let FastAPI serve it
# This is what you’ll want in production, because it serves Flutter from FastAPI itself.

set -e

# 1. Environment
export SHOTMAT_DATA="$HOME/ShotMatData"
export SHOTMAT_PROJECTS="$HOME/ShotMatProjects"
export SHOTMAT_PORT=8000
SHOTMAT_URL="http://127.0.0.1:$SHOTMAT_PORT"

mkdir -p "$SHOTMAT_DATA" "$SHOTMAT_PROJECTS"

################################################################################
# 2. Build Flutter Web
################################################################################
echo "Building Flutter Web UI..."
cd "$(dirname "$0")/../web_ui"

flutter config --enable-web >/dev/null 2>&1
flutter build web --release

echo "Flutter build completed."

################################################################################
# 3. Start FastAPI
################################################################################
echo "Starting FastAPI microservice..."

cd ../api

if [ ! -d ".venv" ]; then
  echo "No .venv in api/. Run scripts/setup_api.sh first."
  exit 1
fi

source .venv/bin/activate

uvicorn shotmat_api.main:app \
  --host 127.0.0.1 \
  --port "$SHOTMAT_PORT" \
  --reload &
API_PID=$!

echo "FastAPI running (PID: $API_PID)"

################################################################################
# 4. Launch Chrome
################################################################################
CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SHOTMAT_CHROME_PROFILE="$HOME/.shotmat/chrome-profile"
mkdir -p "$SHOTMAT_CHROME_PROFILE"

echo "Launching ShotMat Web UI in Chrome..."
"$CHROME_BIN" --user-data-dir="$SHOTMAT_CHROME_PROFILE" --app="$SHOTMAT_URL" >/dev/null 2>&1 &

################################################################################
# 5. Wait for FastAPI
################################################################################
trap "kill $API_PID" EXIT
wait $API_PID
