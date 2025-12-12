#!/usr/bin/env python3
import subprocess
import sys

if __name__ == "__main__":
    print("Starting FastAPI backend on port 8000...")
    subprocess.run([sys.executable, "app.py"])