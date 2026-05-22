#!/bin/bash
# Setup script for backend

echo "Setting up MediMotion Backend..."

# Check if Python 3.11 is available
if command -v python3.11 &>/dev/null; then
    PYTHON=python3.11
elif command -v python3 &>/dev/null; then
    PYTHON=python3
    echo "Warning: Python 3.11 recommended, using $($PYTHON --version)"
else
    echo "Error: Python 3 not found"
    exit 1
fi

# Create virtual environment
$PYTHON -m venv venv

# Activate and install packages
source venv/bin/activate
pip install --upgrade pip
pip install mediapipe==0.10.7
pip install opencv-python
pip install numpy
pip install flask
pip install flask-cors

echo "✅ Backend setup complete!"
echo "Run: source venv/bin/activate && python app.py"
