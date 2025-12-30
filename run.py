# -*- coding: utf-8 -*-
"""
Script to run Streamlit app with configuration from .env
"""
import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get config from .env
address = os.getenv("SERVER_ADDRESS", "0.0.0.0")
port = os.getenv("SERVER_PORT", "8501")

# Build command
cmd = [
    sys.executable, "-m", "streamlit", "run", "app.py",
    "--server.address", address,
    "--server.port", port,
    "--server.headless", "true"
]

print(f"Starting Streamlit on {address}:{port}")
subprocess.run(cmd)
