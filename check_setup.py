"""
Quick Start Script for SATUK VLM
===================================
This script helps you get started quickly by checking your setup.
"""

import os
import sys
from dotenv import load_dotenv

def check_setup():
    """Check if the project is properly configured."""

    print("\n" + "="*60)
    print("🔥 SATUK VLM - Setup Checker")
    print("="*60 + "\n")

    issues = []

    # Check 1: .env file exists
    print("1️⃣  Checking for .env file...")
    if os.path.exists('.env'):
        print("   ✅ .env file found")
    else:
        print("   ⚠️  .env file not found")
        issues.append("Create a .env file with your TOGETHER_API_KEY")

    # Check 2: API key is set
    print("\n2️⃣  Checking API key...")
    load_dotenv()
    api_key = os.getenv("TOGETHER_API_KEY")
    if api_key:
        print(f"   ✅ API key configured (starts with: {api_key[:10]}...)")
    else:
        print("   ❌ TOGETHER_API_KEY not found in .env")
        issues.append("Add TOGETHER_API_KEY=your_key to .env file")

    # Check 3: Directories exist
    print("\n3️⃣  Checking directories...")
    dirs = {
        'satellite_data': 'Satellite imagery storage',
        'images': 'Test images'
    }
    for dirname, desc in dirs.items():
        if os.path.exists(dirname):
            print(f"   ✅ {dirname}/ exists ({desc})")
        else:
            print(f"   ⚠️  {dirname}/ not found, creating...")
            os.makedirs(dirname, exist_ok=True)
            print(f"   ✅ Created {dirname}/")

    # Check 4: Sample images
    print("\n4️⃣  Checking for images...")
    satellite_images = [f for f in os.listdir('satellite_data')
                       if f.endswith(('.jpg', '.jpeg', '.png'))]
    if satellite_images:
        print(f"   ✅ Found {len(satellite_images)} satellite image(s):")
        for img in satellite_images[:3]:
            print(f"      - {img}")
    else:
        print("   ⚠️  No satellite images found in satellite_data/")
        issues.append("Add satellite images (JPEG/PNG) to satellite_data/ directory")

    if os.path.exists('images/car.jpg'):
        print(f"   ✅ Test image (car.jpg) found")
    else:
        print(f"   ⚠️  Test image (car.jpg) not found")
        issues.append("Add car.jpg to images/ directory for testing")

    # Check 5: Python packages
    print("\n5️⃣  Checking Python packages...")
    required_packages = ['flask', 'flask_cors', 'together', 'dotenv']
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} installed")
        except ImportError:
            print(f"   ❌ {package} not installed")
            missing_packages.append(package)

    if missing_packages:
        issues.append(f"Run: pip install {' '.join(missing_packages)}")

    # Summary
    print("\n" + "="*60)
    if issues:
        print("⚠️  ISSUES FOUND:")
        print("="*60)
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        print("\n" + "="*60)
        print("\nPlease fix the issues above before starting the server.")
    else:
        print("✅ ALL CHECKS PASSED!")
        print("="*60)
        print("\n🚀 You're ready to go!")
        print("\nNext steps:")
        print("1. Run: python backend.py")
        print("2. Open: http://localhost:5000")
        print("3. Start analyzing satellite imagery!")

    print("\n")
    return len(issues) == 0

if __name__ == '__main__':
    check_setup()

