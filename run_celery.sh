#!/usr/bin/env bash
# Script to launch Celery worker for Trekking Management Application
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/backend"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "=========================================================="
echo " Starting Celery Worker for Batch Jobs (MAD-II)"
echo " Student Roll No: 23f2000278"
echo "=========================================================="
celery -A tasks.celery_app.celery_app worker --loglevel=info
