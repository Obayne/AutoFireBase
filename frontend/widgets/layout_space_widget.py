from __future__ import annotations

try:
    from PySide6 import QtWidgets, QtCore
except Exception as e:  # pragma: no cover - optional at import time in CI
    QtWidgets = None  # type: ignore
    QtCore = None  # type: ignore

from frontend.layout_space import LayoutSpaceState


class LayoutSpaceWidget(QtWidgets.QWidget):  # type: ignore[misc]
    """Minimal Qt widget that binds to LayoutSpaceState.

    Notes:
    - Keeps logic thin; state changes live in LayoutSpaceState.
    - Safe to import without Qt present (class is defined only if PySide6 is available).
    """

    def __init__(self, state: LayoutSpaceState, parent=None) -> None:
        super().__init__(parent)
        self.state = state

        root = QtWidgets.QVBoxLayout(self)

        # Top bar: sheets toggle, layout selector, lock toggle
        bar = QtWidgets.QHBoxLayout()
        self.btn_sheets = QtWidgets.QPushButton("Show Sheets")
        self.cmb_layout = QtWidgets.QComboBox()
        self.btn_lock = QtWidgets.QPushButton("Lock")
        self.btn_lock.setCheckable(True)

        bar.addWidget(self.btn_sheets)
        bar.addWidget(QtWidgets.QLabel("Layout:"))
        bar.addWidget(self.cmb_layout, 1)
        bar.addWidget(self.btn_lock)
        root.addLayout(bar)

        # Command bar
        cmd_row = QtWidgets.QHBoxLayout()
        self.ed_cmd = QtWidgets.QLineEdit()
        self.ed_cmd.setPlaceholderText("Enter command…")
        self.btn_run = QtWidgets.QPushButton("Run")
        cmd_row.addWidget(self.ed_cmd, 1)
        cmd_row.addWidget(self.btn_run)
        root.addLayout(cmd_row)

        # Wire UI → state
        self.btn_sheets.clicked.connect(self.state.toggle_sheets_dock)
        self.btn_lock.toggled.connect(self.state.set_lock)
        self.cmb_layout.currentTextChanged.connect(self.state.select_layout)
        self.btn_run.clicked.connect(self._emit_command)
        self.ed_cmd.returnPressed.connect(self._emit_command)

        # Wire state → UI
        self.state.on("toggle_sheets", self._on_toggle_sheets)
        self.state.on("select_layout", self._on_select_layout)
        self.state.on("lock", self._on_lock)

        # Initialize visuals from current state
        self._refresh_from_state()

    # ---- slots
    def _emit_command(self) -> None:
        text = self.ed_cmd.text().strip()
        if text:
            self.state.submit_command(text)
            self.ed_cmd.clear()

    def _on_toggle_sheets(self, visible: bool) -> None:
        self.btn_sheets.setText("Hide Sheets" if visible else "Show Sheets")

    def _on_select_layout(self, name: str) -> None:
        idx = self.cmb_layout.findText(name)
        if idx < 0:
            self.cmb_layout.addItem(name)
            idx = self.cmb_layout.findText(name)
        if idx >= 0:
            self.cmb_layout.setCurrentIndex(idx)

    def _on_lock(self, locked: bool) -> None:
        self.btn_lock.setChecked(locked)
        self.btn_lock.setText("Locked" if locked else "Lock")

    def _refresh_from_state(self) -> None:
        # Sheets button text
        self._on_toggle_sheets(self.state.sheets_visible)
        # Layouts combo
        self.cmb_layout.clear()
        for name in self.state.layouts:
            self.cmb_layout.addItem(name)
        if self.state.selected_layout:
            self._on_select_layout(self.state.selected_layout)
        # Lock button
        self._on_lock(self.state.locked)


__all__ = ["LayoutSpaceWidget"]

