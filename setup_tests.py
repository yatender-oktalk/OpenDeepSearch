#!/usr/bin/env python3
"""
Setup script for testing environment
"""
import subprocess
import sys

def install_dependencies():
    """Install required testing dependencies"""
    dependencies = [
        "pytest",
        "neo4j",
        "litellm"
    ]
    
    print("Installing test dependencies...")
    for dep in dependencies:
        print(f"Installing {dep}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True, capture_output=True)
            print(f"✓ {dep} installed")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {dep}: {e}")

if __name__ == "__main__":
    install_dependencies()
    print("\nSetup complete! Run 'python run_tests.py' to test.") 