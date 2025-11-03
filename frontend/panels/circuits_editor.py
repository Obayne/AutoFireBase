from __future__ import annotations

from typing import Any, Dict, List

from PySide6 import QtWidgets
from backend.preferences import load_preferences, update_preferences
from typing import cast

from backend.circuits import summarize_panel_circuits


class CircuitsEditor(QtWidgets.QWidget):
    """Lightweight Circuits Editor MVP.

    - Displays a simple, editable table of circuits with a filter row
    - Columns: Circuit, Cable, EOL, T‑Tap, Hidden, Locked, Start Addr
    - Actions: Update Wire Labels (stub), Recompute Calcs (rebuilds circuits list)
    """

    COL_CIRCUIT = 0
    COL_CABLE = 1
    COL_EOL = 2
    COL_TTAP = 3
    COL_HIDDEN = 4
    COL_LOCKED = 5
    COL_START_ADDR = 6

    EOL_OPTIONS = ["Resistor", "Capacitor", "Diode", "None"]

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._device_items: list[Any] = []
        self._wire_items: list[Any] = []
        # In-memory row model keyed by circuit_id
        self._rows: List[Dict[str, Any]] = []
        self._overrides: Dict[str, Dict[str, Any]] = {}

        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        # Top actions bar
        top_bar = QtWidgets.QHBoxLayout()
        self.filter_edit = QtWidgets.QLineEdit()
        self.filter_edit.setPlaceholderText("Filter circuits (id or cable)…")
        self.filter_edit.textChanged.connect(self._apply_filter)
        top_bar.addWidget(QtWidgets.QLabel("Filter:"))
        top_bar.addWidget(self.filter_edit, 1)

        self.btn_update_labels = QtWidgets.QPushButton("Update Wire Labels")
        self.btn_update_labels.clicked.connect(self._update_wire_labels)
        top_bar.addWidget(self.btn_update_labels)

        self.btn_recompute = QtWidgets.QPushButton("Recompute Calcs")
        self.btn_recompute.clicked.connect(self.recompute)
        top_bar.addWidget(self.btn_recompute)

        layout.addLayout(top_bar)

        # Editable table
        self.table = QtWidgets.QTableWidget(0, 7, self)
        self.table.setHorizontalHeaderLabels(
            [
                "Circuit",
                "Cable",
                "EOL",
                "T‑Tap",
                "Hidden",
                "Locked",
                "Start Addr",
            ]
        )
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setDefaultSectionSize(120)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def set_data(self, device_items: list[Any], wire_items: list[Any]) -> None:
        self._device_items = device_items or []
        self._wire_items = wire_items or []
        self.recompute()

    def recompute(self) -> None:
        """Recompute circuits list and merge with existing edits."""
        # Load persisted overrides once per recompute
        self._overrides = self._load_overrides()
        summary_rows = summarize_panel_circuits(self._device_items, self._wire_items)
        # Build a map of existing edits by circuit_id
        existing: Dict[str, Dict[str, Any]] = {
            str(r.get("circuit_id", "")): r for r in self._rows if r.get("circuit_id")
        }
        new_rows: List[Dict[str, Any]] = []
        for s in summary_rows:
            cid = str(s.circuit_id)
            base: Dict[str, Any] = {
                "circuit_id": cid,
                "cable": "",
                "eol": "Resistor",
                "ttap": False,
                "hidden": False,
                "locked": False,
                "start_addr": 1,
            }
            if cid in existing:
                # Preserve user edits
                base.update({k: existing[cid][k] for k in base.keys() if k in existing[cid]})
            # Merge persisted overrides
            if cid in self._overrides:
                base.update(
                    {k: self._overrides[cid][k] for k in base.keys() if k in self._overrides[cid]}
                )
            new_rows.append(base)
        self._rows = new_rows
        self._refresh_table()

    def _refresh_table(self) -> None:
        self.table.setRowCount(len(self._rows))
        for r, row in enumerate(self._rows):
            # Circuit (read‑only) as a read-only line edit to avoid enum flag usage
            cid_le = QtWidgets.QLineEdit(str(row["circuit_id"]))
            cid_le.setReadOnly(True)
            self.table.setCellWidget(r, self.COL_CIRCUIT, cid_le)

            # Cable (editable line edit)
            le = QtWidgets.QLineEdit(str(row.get("cable", "")))
            le.textChanged.connect(lambda val, rr=r: self._set_row_val(rr, "cable", val))
            self.table.setCellWidget(r, self.COL_CABLE, le)

            # EOL (combo)
            cb = QtWidgets.QComboBox()
            cb.addItems(self.EOL_OPTIONS)
            idx = max(
                0,
                (
                    self.EOL_OPTIONS.index(str(row.get("eol", "Resistor")))
                    if str(row.get("eol", "Resistor")) in self.EOL_OPTIONS
                    else 0
                ),
            )
            cb.setCurrentIndex(idx)
            cb.currentTextChanged.connect(lambda val, rr=r: self._set_row_val(rr, "eol", val))
            self.table.setCellWidget(r, self.COL_EOL, cb)

            # T‑Tap (checkbox)
            tt = QtWidgets.QCheckBox()
            tt.setChecked(bool(row.get("ttap", False)))
            tt.toggled.connect(lambda val, rr=r: self._set_row_val(rr, "ttap", bool(val)))
            self.table.setCellWidget(r, self.COL_TTAP, tt)

            # Hidden (checkbox)
            hd = QtWidgets.QCheckBox()
            hd.setChecked(bool(row.get("hidden", False)))
            hd.toggled.connect(lambda val, rr=r: self._set_row_val(rr, "hidden", bool(val)))
            self.table.setCellWidget(r, self.COL_HIDDEN, hd)

            # Locked (checkbox)
            lk = QtWidgets.QCheckBox()
            lk.setChecked(bool(row.get("locked", False)))
            lk.toggled.connect(lambda val, rr=r: self._set_row_val(rr, "locked", bool(val)))
            self.table.setCellWidget(r, self.COL_LOCKED, lk)

            # Start Addr (spin)
            sp = QtWidgets.QSpinBox()
            sp.setRange(1, 9999)
            sp.setValue(int(row.get("start_addr", 1)))
            sp.valueChanged.connect(lambda val, rr=r: self._set_row_val(rr, "start_addr", int(val)))
            self.table.setCellWidget(r, self.COL_START_ADDR, sp)

        # Re-apply current filter after refresh
        self._apply_filter(self.filter_edit.text())

    def _set_row_val(self, row_index: int, key: str, value: Any) -> None:
        if 0 <= row_index < len(self._rows):
            self._rows[row_index][key] = value
            # Persist after each change (MVP; a future version can debounce)
            try:
                self._save_overrides()
            except Exception:
                pass

    def _apply_filter(self, text: str) -> None:
        q = (text or "").strip().lower()
        for r in range(self.table.rowCount()):
            circuit_widget = self.table.cellWidget(r, self.COL_CIRCUIT)
            circuit_id = (
                circuit_widget.text().lower()
                if isinstance(circuit_widget, QtWidgets.QLineEdit)
                else ""
            )
            cable_widget = self.table.cellWidget(r, self.COL_CABLE)
            cable = (
                cable_widget.text().lower() if isinstance(cable_widget, QtWidgets.QLineEdit) else ""
            )
            match = (q in circuit_id) or (q in cable)
            self.table.setRowHidden(r, not match)

    def _update_wire_labels(self) -> None:
        # Invoke the containing window's label refresh if available
        mw = self.parent()
        # Walk up at most two levels to find a window method
        for _ in range(2):
            if mw is None:
                break
            if hasattr(mw, "update_wire_labels_overlay"):
                try:
                    mw.update_wire_labels_overlay()
                    QtWidgets.QMessageBox.information(
                        self,
                        "Update Wire Labels",
                        "Updated wire labels based on current preferences.",
                    )
                    return
                except Exception:
                    break
            mw = mw.parent()
        # Fallback info
        QtWidgets.QMessageBox.information(
            self,
            "Update Wire Labels",
            "Unable to reach the main window. Simulation: would update wire labels.",
        )

    # --- persistence helpers ---
    def _load_overrides(self) -> Dict[str, Dict[str, Any]]:
        try:
            prefs = load_preferences()
            co = prefs.get("circuits_overrides", {})
            return cast(Dict[str, Dict[str, Any]], co) if isinstance(co, dict) else {}
        except Exception:
            return {}

    def _save_overrides(self) -> None:
        # Persist only keys we own for each circuit
        allowed = {"cable", "eol", "ttap", "hidden", "locked", "start_addr"}
        mapping: Dict[str, Dict[str, Any]] = {}
        for row in self._rows:
            cid = str(row.get("circuit_id", ""))
            if not cid:
                continue
            mapping[cid] = {k: row[k] for k in allowed if k in row}
        update_preferences({"circuits_overrides": mapping})
