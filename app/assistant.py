from PySide6 import QtWidgets


class AssistantDock(QtWidgets.QDockWidget):
    """A lightweight in-app assistant scaffold (no network calls).
    - Left: simple prompt box + 'Suggest Layout' stub
    - Right: log view where future AI outputs could appear
    """

    def __init__(self, parent=None):
        super().__init__("Assistant (beta)", parent)
        self.setObjectName("AssistantDock")
        w = QtWidgets.QWidget()
        self.setWidget(w)
        lay = QtWidgets.QVBoxLayout(w)

        # Input row
        self.input = QtWidgets.QLineEdit()
        self.input.setPlaceholderText(
            "Ask: e.g., 'Place detectors along corridor at 30 ft spacing'"
        )
        self.btn_suggest = QtWidgets.QPushButton("Suggest Layout")
        row = QtWidgets.QHBoxLayout()
        row.addWidget(self.input)
        row.addWidget(self.btn_suggest)
        lay.addLayout(row)

        # Log/output
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Assistant output will appear here. (Stub — no external calls)")
        lay.addWidget(self.log)

        # Wire up stub behavior
        self.btn_suggest.clicked.connect(self._on_suggest)
        self.input.returnPressed.connect(self._on_suggest)

    def _on_suggest(self):
        q = self.input.text().strip()
        if not q:
            q = "(no prompt)"
        # Just echo for now; real logic will be added later
        self.log.append(f"<b>You:</b> {q}")
        self.log.append(
            "Assistant (stub): I would create a grid/line array based on your spacing and corridor length."
        )
        self.log.append("→ Try the upcoming Array tool under Tools (soon).")
        self.input.clear()
