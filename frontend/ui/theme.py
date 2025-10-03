from PySide6 import QtCore, QtGui


def apply_theme(app, name: str):
    name = (name or "Light").lower()
    pal = app.palette()

    if name == "dark":
        pal.setColor(pal.Window, QtGui.QColor(45, 45, 48))
        pal.setColor(pal.WindowText, QtCore.Qt.white)
        pal.setColor(pal.Base, QtGui.QColor(30, 30, 30))
        pal.setColor(pal.AlternateBase, QtGui.QColor(45, 45, 48))
        pal.setColor(pal.ToolTipBase, QtCore.Qt.white)
        pal.setColor(pal.ToolTipText, QtCore.Qt.white)
        pal.setColor(pal.Text, QtCore.Qt.white)
        pal.setColor(pal.Button, QtGui.QColor(45, 45, 48))
        pal.setColor(pal.ButtonText, QtCore.Qt.white)
        pal.setColor(pal.BrightText, QtCore.Qt.red)
        pal.setColor(pal.Highlight, QtGui.QColor(0, 120, 215))
        pal.setColor(pal.HighlightedText, QtCore.Qt.white)
        app.setPalette(pal)
        app.setStyleSheet("QToolBar { border: none; } QMenu { background:#2d2d30; color:white; }")
    elif name.startswith("high contrast"):
        pal.setColor(pal.Window, QtGui.QColor(0, 0, 0))
        pal.setColor(pal.WindowText, QtCore.Qt.white)
        pal.setColor(pal.Base, QtGui.QColor(0, 0, 0))
        pal.setColor(pal.AlternateBase, QtGui.QColor(30, 30, 30))
        pal.setColor(pal.ToolTipBase, QtCore.Qt.white)
        pal.setColor(pal.ToolTipText, QtCore.Qt.black)
        pal.setColor(pal.Text, QtCore.Qt.white)
        pal.setColor(pal.Button, QtGui.QColor(0, 0, 0))
        pal.setColor(pal.ButtonText, QtCore.Qt.white)
        pal.setColor(pal.BrightText, QtCore.Qt.yellow)
        pal.setColor(pal.Highlight, QtGui.QColor(255, 215, 0))
        pal.setColor(pal.HighlightedText, QtCore.Qt.black)
        app.setPalette(pal)
        app.setStyleSheet(
            "QToolBar { border: 1px solid #FFD700; } QMenu { background:#000; color:#fff; }"
        )
    else:
        # Light default
        app.setPalette(app.style().standardPalette())
        app.setStyleSheet("QToolBar { border: none; }")
