import sys, traceback, datetime
from pathlib import Path
from PySide6 import QtWidgets

def write_crash_log(tb_text: str) -> str:
    base = Path.home() / "AutoFire" / "logs"
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"startup_error_{datetime.datetime.now():%Y%m%d_%H%M%S}.log"
    try:
        path.write_text(tb_text, encoding="utf-8")
    except Exception:
        pass
    return str(path)

def excepthook(exctype, value, tb):
    tb_text = "".join(traceback.format_exception(exctype, value, tb))
    p = write_crash_log(tb_text)
    try:
        QtWidgets.QMessageBox.critical(None, "Auto-Fire Error", f"{tb_text}\n\nSaved: {p}")
    except Exception:
        pass

def install():
    sys.excepthook = excepthook
