#!/usr/bin/env python
import subprocess
import sys
import os

def main():
    """Run the WebSage application"""
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

if __name__ == "__main__":
    main() 