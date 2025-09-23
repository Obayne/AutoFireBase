import pytest
from PySide6.QtGui import QGuiApplication
import sys

def test_q_app_creation():
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv)
    assert app is not None
