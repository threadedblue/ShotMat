#!/bin/bash

# Save the directory this script was run from
START_DIR="$(pwd)"

# Target directory where requirements.txt is located
API_DIR="$HOME/ShotMat.Wk/shotmat/api"
REQ_FILE="$API_DIR/requirements.txt"

# Check directory exists
if [ ! -d "$API_DIR" ]; then
  echo "Error: API directory does not exist: $API_DIR"
  exit 1
fi

# Check requirements file exists
if [ ! -f "$REQ_FILE" ]; then
  echo "Error: requirements.txt not found at $REQ_FILE"
  exit 1
fi

echo "Changing to: $API_DIR"
cd "$API_DIR" || exit 1

# If you want to auto-activate a venv, uncomment these lines:
# if [ -d "$API_DIR/.venv" ]; then
#   echo "Activating virtual environment..."
#   source "$API_DIR/.venv/bin/activate"
# fi

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Done."

# Return to the original directory
cd "$START_DIR" || exit 1
