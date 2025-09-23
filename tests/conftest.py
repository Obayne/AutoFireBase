import pytest
from PySide6.QtGui import QGuiApplication
import sys

@pytest.fixture(scope='session')
def q_app():
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv)
    yield app
    app.quit()
