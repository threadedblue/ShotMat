#!/bin/bash

# This script launches the ShotMat application components.
#
# Usage:
#   ./run.sh [mode]
#
# Modes:
#   all (default): Launches both the API and the Flutter UI.
#   api:           Launches only the FastAPI backend.

# Function to kill background processes on exit
cleanup() {
    echo "Shutting down background processes..."
    if [ -n "$API_PID" ]; then
        kill $API_PID
        echo "API server stopped."
    fi
    exit 0
}

# Trap Ctrl+C (INT) and termination (TERM) signals to run cleanup
trap cleanup INT TERM

# Default to 'all' mode if no argument is provided
MODE=${1:-all}

if [[ "$MODE" == "api" || "$MODE" == "all" ]]; then
    echo "Starting API server..."
    (cd api && uvicorn shotmat_api.main:app --reload) &
    API_PID=$!
fi

if [[ "$MODE" == "all" ]]; then
    echo "Starting Flutter UI..."
    (cd ui_web && flutter run)
    # When flutter run exits, cleanup will be called by the trap
    cleanup
fi

if [[ "$MODE" == "api" ]]; then
    echo "API server is running with PID $API_PID."
    echo "Press Ctrl+C to stop the server."
    wait $API_PID
fi