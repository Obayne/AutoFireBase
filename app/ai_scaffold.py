
from PySide6 import QtCore, QtGui, QtWidgets

class AssistantDock(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Assistant (stub)", parent)
        w = QtWidgets.QWidget(self)
        self.setWidget(w)
        layout = QtWidgets.QVBoxLayout(w)

        self.txt_history = QtWidgets.QTextEdit(self); self.txt_history.setReadOnly(True)
        self.txt_prompt = QtWidgets.QPlainTextEdit(self); self.txt_prompt.setPlaceholderText("Ask a question about this drawing… (offline stub)")
        btns = QtWidgets.QHBoxLayout()
        self.btn_respond = QtWidgets.QPushButton("Respond (Stub)")
        self.btn_clear = QtWidgets.QPushButton("Clear")
        btns.addWidget(self.btn_respond); btns.addWidget(self.btn_clear); btns.addStretch(1)

        layout.addWidget(self.txt_history)
        layout.addWidget(self.txt_prompt, 1)
        layout.addLayout(btns)

        self.btn_respond.clicked.connect(self._respond)
        self.btn_clear.clicked.connect(lambda: (self.txt_history.clear(), self.txt_prompt.clear()))

    def _respond(self):
        q = self.txt_prompt.toPlainText().strip()
        if not q:
            QtWidgets.QMessageBox.information(self, "Assistant", "Type a prompt first.")
            return
        # Offline canned response. Later, can route to a local or remote model.
        reply = (
            "Assistant (stub): I can't call external AI from here yet.\n"
            "But I can: \n"
            "• summarize counts (BOM),\n"
            "• list selected items,\n"
            "• show keyboard shortcuts.\n"
            "Future: connect to a local service for AI drafting/checks.\n"
        )
        self.txt_history.append(f"<b>You:</b> {QtGui.QTextDocument().toHtmlEscaped(q)}")
        self.txt_history.append(reply.replace("\n", "<br>"))
        self.txt_prompt.clear()
