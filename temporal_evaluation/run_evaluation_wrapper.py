#!/usr/bin/env python3
import os
import sys
import subprocess

def run_evaluation():
    """Wrapper to run evaluation from correct directory"""
    
    # Get the project root (parent of temporal_evaluation)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    print(f"Current directory: {current_dir}")
    print(f"Project root: {project_root}")
    
    # Change to project root
    os.chdir(project_root)
    print(f"Changed to: {os.getcwd()}")
    
    # Run the evaluation script
    script_path = os.path.join('temporal_evaluation', 'sec_filings', 'run_evaluation.py')
    
    if os.path.exists(script_path):
        print(f"Running: python {script_path}")
        subprocess.run([sys.executable, script_path])
    else:
        print(f"❌ Script not found: {script_path}")

if __name__ == "__main__":
    run_evaluation()
