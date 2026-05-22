#!/usr/bin/env python3
"""
MediMotion Backend Setup and Runner
Run this script to automatically set up and start the server
"""

import subprocess
import sys
import os
import platform

def run_command(command, shell=True):
    """Run a command and print output"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=shell, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def check_python():
    """Check Python version"""
    python_cmd = "python3" if platform.system() == "Darwin" else "python"
    result = subprocess.run(f"{python_cmd} --version", shell=True, capture_output=True, text=True)
    print(f"Using {result.stdout.strip()}")
    return python_cmd

def install_packages(python_cmd):
    """Install required packages"""
    packages = [
        "flask==2.3.3",
        "flask-cors==4.0.0",
        "opencv-python==4.8.1.78",
        "mediapipe==0.10.7",
        "numpy==1.24.3",
        "reportlab==4.0.4",
        "pandas==2.0.3",
        "openpyxl==3.1.2",
        "python-dotenv==1.0.0",
        "pyjwt==2.8.0"
    ]
    
    print("\nInstalling required packages...")
    for package in packages:
        print(f"Installing {package}...")
        if not run_command(f"{python_cmd} -m pip install --user {package}"):
            print(f"Warning: Could not install {package}, trying without --user...")
            run_command(f"{python_cmd} -m pip install {package}")
    
    return True

def verify_installation(python_cmd):
    """Verify Flask is installed"""
    print("\nVerifying installations...")
    test_code = """
try:
    from flask import Flask
    import cv2
    import mediapipe as mp
    import numpy as np
    print("All modules imported successfully!")
except ImportError as e:
    print(f"Import error: {e}")
    exit(1)
"""
    with open("test_import.py", "w") as f:
        f.write(test_code)
    
    result = subprocess.run(f"{python_cmd} test_import.py", shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return False
    
    os.remove("test_import.py")
    return True

def create_requirements_file():
    """Create requirements.txt file"""
    requirements = """flask==2.3.3
flask-cors==4.0.0
opencv-python==4.8.1.78
mediapipe==0.10.7
numpy==1.24.3
reportlab==4.0.4
pandas==2.0.3
openpyxl==3.1.2
python-dotenv==1.0.0
pyjwt==2.8.0
"""
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    print("Created requirements.txt")

def main():
    print("=" * 50)
    print("MediMotion Backend Setup")
    print("=" * 50)
    
    # Check Python
    python_cmd = check_python()
    
    # Create requirements file
    create_requirements_file()
    
    # Install packages
    install_packages(python_cmd)
    
    # Verify installation
    if not verify_installation(python_cmd):
        print("\n❌ Verification failed. Trying alternative installation...")
        print("\nPlease run these commands manually:")
        print(f"{python_cmd} -m pip install --upgrade pip")
        print(f"{python_cmd} -m pip install flask flask-cors opencv-python mediapipe numpy reportlab pandas openpyxl python-dotenv pyjwt")
        return
    
    print("\n✅ Setup complete!")
    print("\nStarting the server...")
    
    # Run the app
    if platform.system() == "Windows":
        subprocess.run(f"{python_cmd} app.py", shell=True)
    else:
        subprocess.run(f"{python_cmd} app.py", shell=True)

if __name__ == "__main__":
    main()