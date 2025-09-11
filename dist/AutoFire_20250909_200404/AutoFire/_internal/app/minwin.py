from PySide6 import QtWidgets, QtCore
from app.scene import GridScene

class MinimalMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto-Fire — Minimal Window (Fallback)")
        self.resize(1000, 700)
        view = QtWidgets.QGraphicsView(GridScene(20, 0,0,2000,1200))
        self.setCentralWidget(view)
        self.statusBar().showMessage("Fallback window loaded. If you see this, main UI didn't start.")

def run_minimal():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    win = MinimalMainWindow()
    win.show()
    app.exec()