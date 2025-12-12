#!/usr/bin/env python3
import subprocess
import time
import sys
import os
import signal
import atexit

def cleanup(fastapi_process, streamlit_process):
    """Clean up processes on exit"""
    if fastapi_process:
        fastapi_process.terminate()
    if streamlit_process:
        streamlit_process.terminate()

def main():
    print("Starting Network Security Phishing Detection App...")
    
    # Start FastAPI backend
    print("Starting FastAPI backend on port 8000...")
    fastapi_process = subprocess.Popen([sys.executable, "app.py"])
    
    # Wait for FastAPI to start
    time.sleep(5)
    
    # Start Streamlit frontend
    print("Starting Streamlit frontend...")
    streamlit_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.headless", "true"])
    
    # Register cleanup function
    atexit.register(cleanup, fastapi_process, streamlit_process)
    
    try:
        print("\nBoth servers are running!")
        print("FastAPI: http://localhost:8000")
        print("Streamlit: http://localhost:8501")
        print("Press Ctrl+C to stop both servers")
        
        # Wait for processes
        while True:
            if fastapi_process.poll() is not None or streamlit_process.poll() is not None:
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        cleanup(fastapi_process, streamlit_process)

if __name__ == "__main__":
    main()