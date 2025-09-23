#!/usr/bin/env python3
"""Test script to verify the main application can start."""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from main import MainWindow
    from PySide6.QtWidgets import QApplication
    print("Successfully imported main application components")
except Exception as e:
    print(f"Error importing: {e}")
    import traceback
    traceback.print_exc()