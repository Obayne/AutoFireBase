from PySide6 import QtWidgets


class MinimalWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto-Fire — Minimal Window")
        lab = QtWidgets.QLabel(
            "Fallback UI (minimal). If you see this, app.main.create_window() was not found."
        )
        lab.setMargin(16)
        self.setCentralWidget(lab)
        self.resize(900, 600)
