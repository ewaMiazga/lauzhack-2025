#!/usr/bin/env python3
"""
Quick test script for wildlife backend
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Wildlife Backend Setup Check")
print("=" * 60)

# Check Python version
print(f"\n✓ Python version: {sys.version}")

# Check dependencies
try:
    import cv2
    print(f"✓ OpenCV version: {cv2.__version__}")
except ImportError as e:
    print(f"✗ OpenCV not installed: {e}")
    print("  Install with: pip install opencv-python")

try:
    from together import Together
    print("✓ Together AI SDK installed")
except ImportError as e:
    print(f"✗ Together AI SDK not installed: {e}")
    print("  Install with: pip install together")

try:
    from flask import Flask
    from flask_cors import CORS
    print("✓ Flask and CORS installed")
except ImportError as e:
    print(f"✗ Flask/CORS not installed: {e}")
    print("  Install with: pip install flask flask-cors")

# Check API key
api_key = os.getenv("TOGETHER_API_KEY")
if api_key:
    print(f"✓ Together API key found (length: {len(api_key)})")
else:
    print("✗ TOGETHER_API_KEY not found in environment")
    print("  Add it to your .env file")

# Check directories
upload_dir = os.path.join(os.path.dirname(__file__), "uploaded_videos")
frames_dir = os.path.join(os.path.dirname(__file__), "video_frames")

if os.path.exists(upload_dir):
    print(f"✓ Upload directory exists: {upload_dir}")
else:
    print(f"⚠ Upload directory will be created: {upload_dir}")

if os.path.exists(frames_dir):
    print(f"✓ Frames directory exists: {frames_dir}")
else:
    print(f"⚠ Frames directory will be created: {frames_dir}")

print("\n" + "=" * 60)
print("Ready to start the wildlife backend!")
print("Run: python wildlife_backend.py")
print("=" * 60)
