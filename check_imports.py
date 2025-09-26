import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

try:
    import PySide6

    print("PySide6 imported successfully")
except ImportError as e:
    print(f"PySide6 import error: {e}")

try:
    from PySide6 import QtWidgets

    print("PySide6.QtWidgets imported successfully")
except ImportError as e:
    print(f"PySide6.QtWidgets import error: {e}")

try:
    from app.main import MainWindow

    print("MainWindow imported successfully")
except ImportError as e:
    print(f"MainWindow import error: {e}")

try:
    from db import loader

    print("Database loader imported successfully")
except ImportError as e:
    print(f"Database loader import error: {e}")

print("Import check completed")
