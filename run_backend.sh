#!/usr/bin/env bash
# Script to launch Trekking Management Application Flask API
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/backend"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

export PORT=5001
echo "=========================================================="
echo " Starting Trekking Management Application - V2 (MAD-II)"
echo " Student Roll No: 23f2000278"
echo " Backend running at: http://127.0.0.1:5001"
echo "=========================================================="
python app.py
