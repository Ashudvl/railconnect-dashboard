#!/bin/bash
set -e

PORT="${PORT:-8000}"
echo "========================================================"
echo " Starting RailConnect 2.0 Multi-WAN Control Platform"
echo " Port: $PORT"
echo "========================================================"

# Build frontend if dist is missing
if [ ! -d "frontend/dist" ]; then
    echo "Building frontend assets..."
    (cd frontend && npm run build)
fi

# Detect Python binary
if [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
elif [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
else
    PYTHON="python3"
fi

exec "$PYTHON" -m uvicorn backend.app.main:app --host 0.0.0.0 --port "$PORT"
