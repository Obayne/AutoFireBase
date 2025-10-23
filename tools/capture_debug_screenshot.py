import os
import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

app = QApplication.instance()
if not app:
    print("No running QApplication instance found")
    sys.exit(1)

found = False
for w in app.topLevelWidgets():
    print("Top-level:", w, w.windowTitle())
    if "AutoFire - Debug Visible" in w.windowTitle() or "AutoFire" in w.windowTitle():
        screen = QGuiApplication.primaryScreen()
        pix = screen.grabWindow(int(w.winId()))
        out = r"C:\Dev\pwsh-diagnostics\autofire-window-screenshot.png"
        os.makedirs(os.path.dirname(out), exist_ok=True)
        pix.save(out)
        print("Saved screenshot to", out)
        found = True
        break

if not found:
    print("No matching window found")
