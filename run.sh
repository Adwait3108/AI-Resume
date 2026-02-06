#!/bin/bash

# AI Resume Analyzer - Run Script
# This script ensures the app runs with the correct Python and environment

cd "$(dirname "$0")"

echo "=========================================="
echo "AI Resume Analyzer - Starting..."
echo "=========================================="

# Check Python version
echo "Checking Python..."
PYTHON_CMD=$(which python3)
if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: python3 not found!"
    exit 1
fi

echo "Using: $PYTHON_CMD"
$PYTHON_CMD --version

# Set API key
export GEMINI_API_KEY=''

# Test imports first
echo ""
echo "Testing imports..."
$PYTHON_CMD -c "import flask; import flask_cors; import google.generativeai; print('✓ All imports OK')" 2>&1 | grep -v "FutureWarning\|NotOpenSSLWarning" || {
    echo "ERROR: Missing required packages!"
    echo "Installing dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt --user
}

# Run the app
echo ""
echo "Starting Flask application..."
echo "Open http://localhost:5000 in your browser"
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

$PYTHON_CMD app.py
