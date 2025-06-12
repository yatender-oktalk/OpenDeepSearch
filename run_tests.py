#!/usr/bin/env python3
"""
Simple test runner for temporal KG tool
"""
import subprocess
import sys
import importlib.util

def check_pytest_installed():
    """Check if pytest is installed"""
    spec = importlib.util.find_spec("pytest")
    return spec is not None

def install_pytest():
    """Install pytest"""
    print("Installing pytest...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"], check=True)
        print("✓ pytest installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install pytest")
        return False

def run_tests():
    """Run all tests"""
    print("Running Temporal KG Tool Tests")
    print("=" * 40)
    
    # Check and install pytest if needed
    if not check_pytest_installed():
        print("pytest not found. Attempting to install...")
        if not install_pytest():
            print("Running example tests only...")
            subprocess.run([sys.executable, "tests/test_prompt_examples.py"])
            return
    
    try:
        # Run unit tests
        print("\n1. Running Unit Tests...")
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_temporal_kg_tool.py", 
            "-v"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Unit tests passed")
            print(result.stdout)
        else:
            print("✗ Unit tests failed")
            print(result.stdout)
            print(result.stderr)
        
        # Run example tests
        print("\n2. Running Example Query Tests...")
        result = subprocess.run([
            sys.executable, "tests/test_prompt_examples.py"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
            
    except Exception as e:
        print(f"Error running tests: {e}")
        print("Running example tests only...")
        subprocess.run([sys.executable, "tests/test_prompt_examples.py"])

if __name__ == "__main__":
    run_tests() 