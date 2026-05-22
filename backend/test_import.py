
try:
    from flask import Flask
    import cv2
    import mediapipe as mp
    import numpy as np
    print("All modules imported successfully!")
except ImportError as e:
    print(f"Import error: {e}")
    exit(1)
