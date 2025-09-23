#!/usr/bin/env python3
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.main import main
    print("SUCCESS: Main module imported successfully")
except Exception as e:
    print(f"ERROR: Failed to import main module: {e}")
    sys.exit(1)