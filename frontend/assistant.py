from PySide6 import QtWidgets

# UI strings here may intentionally be long for clarity; silence E501 for this file
# ruff: noqa: E501
# noqa: E501


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
        q = self.input.text().strip().lower()
        if not q:
            q = "(no prompt)"
        # Log the user input
        self.log.append(f"<b>You:</b> {q}")

        # Basic command parsing (safe simulation only - no actual changes)
        response = self._parse_command(q)
        self.log.append(f"Assistant: {response}")
        self.input.clear()

    def _parse_command(self, command):
        """Parse and simulate responses to safe commands. No actual modifications."""
        if "place" in command and "detector" in command:
            return "Simulation: Would place a detector device at the current cursor position or default location. (Use Device Palette to place manually for now.)"
        elif "draw" in command and "line" in command:
            return "Simulation: Would start the Draw Line tool. (Use Tools → Draw Line to draw manually.)"
        elif "grid" in command:
            return "Simulation: Would toggle grid visibility. (Use View → Grid to toggle manually.)"
        elif "array" in command or "spacing" in command:
            return "Simulation: Would create an array placement with specified spacing. (Array tool coming soon - use manual placement for now.)"
        elif "help" in command or "what" in command:
            return "I can simulate commands like 'place detector', 'draw line', 'toggle grid'. Try one! (Full AI manipulation coming in future updates.)"
        else:
            return "I understand your request but am in simulation mode. Try commands like 'place detector' or 'draw line' to see what I would do. (No actual changes made.)"
