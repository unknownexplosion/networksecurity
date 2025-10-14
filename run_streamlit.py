#!/usr/bin/env python3
"""
Script to run both FastAPI backend and Streamlit frontend
"""
import subprocess
import time
import sys
import os

def run_fastapi():
    """Start FastAPI server"""
    return subprocess.Popen([sys.executable, "app.py"])

def run_streamlit():
    """Start Streamlit app"""
    return subprocess.Popen([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])

if __name__ == "__main__":
    print("Starting FastAPI backend...")
    fastapi_process = run_fastapi()
    
    # Wait for FastAPI to start
    time.sleep(3)
    
    print("Starting Streamlit frontend...")
    streamlit_process = run_streamlit()
    
    try:
        # Wait for both processes
        fastapi_process.wait()
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        fastapi_process.terminate()
        streamlit_process.terminate()