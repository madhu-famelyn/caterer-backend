#!/bin/bash
# CaterHub Backend – quick start script
cd "$(dirname "$0")"

echo "🚀 Starting CaterHub Backend on http://127.0.0.1:8000 ..."
echo "   Swagger docs: http://127.0.0.1:8000/docs"
echo ""

# Activate the macOS virtual environment and start uvicorn with hot-reload
venv_mac/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --reload
