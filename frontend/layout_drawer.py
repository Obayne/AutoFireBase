from __future__ import annotations

from PySide6 import QtCore, QtWidgets

ARCH_PAPER = [
    "Letter",
    "Tabloid",
    "Arch A",
    "Arch B",
    "Arch C",
    "Arch D",
    "Arch E",
    "A3",
    "A2",
    "A1",
    "A0",
]

ORIENTATIONS = ["Portrait", "Landscape"]

ARCH_SCALES = [
    "1/8\" = 1'",
    "3/16\" = 1'",
    "1/4\" = 1'",
    "3/8\" = 1'",
    "1/2\" = 1'",
    "3/4\" = 1'",
    "1\" = 1'",
    "1 1/2\" = 1'",
    "3\" = 1'",
]

ENG_SCALES = ["1\" = 10'", "1\" = 20'", "1\" = 30'", "1\" = 40'", "1\" = 50'", "1\" = 60'"]


class LayoutDrawer(QtWidgets.QDockWidget):
    """Minimal slide-out drawer for PaperSpace layout controls.

    This is a non-invasive shell with placeholders. Hookups to actual actions
    can be added incrementally.
    """

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__("Layout", parent)
        self.setObjectName("LayoutDrawer")
        self.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | QtCore.Qt.LeftDockWidgetArea)
        self._build()

    def _build(self) -> None:
        w = QtWidgets.QWidget(self)
        self.setWidget(w)
        lay = QtWidgets.QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)

        # Sheet group
        grp_sheet = QtWidgets.QGroupBox("Sheet")
        f_sheet = QtWidgets.QFormLayout(grp_sheet)
        self.cmb_size = QtWidgets.QComboBox()
        self.cmb_size.addItems(ARCH_PAPER)
        self.cmb_orient = QtWidgets.QComboBox()
        self.cmb_orient.addItems(ORIENTATIONS)
        self.spn_margin = QtWidgets.QDoubleSpinBox()
        self.spn_margin.setRange(0.0, 3.0)
        self.spn_margin.setSingleStep(0.1)
        self.spn_margin.setSuffix(" in")
        self.spn_margin.setValue(0.5)
        f_sheet.addRow("Size", self.cmb_size)
        f_sheet.addRow("Orientation", self.cmb_orient)
        f_sheet.addRow("Margins", self.spn_margin)

        # Windows group
        grp_win = QtWidgets.QGroupBox("Windows")
        v_win = QtWidgets.QVBoxLayout(grp_win)
        self.lst_windows = QtWidgets.QListWidget()
        self.lst_windows.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        v_win.addWidget(self.lst_windows, 1)
        h_win = QtWidgets.QHBoxLayout()
        self.btn_add_window = QtWidgets.QPushButton("Add")
        self.btn_fit = QtWidgets.QPushButton("Fit")
        self.btn_center = QtWidgets.QPushButton("Center")
        h_win.addWidget(self.btn_add_window)
        h_win.addWidget(self.btn_fit)
        h_win.addWidget(self.btn_center)
        v_win.addLayout(h_win)
        # Scale presets
        h_scale = QtWidgets.QHBoxLayout()
        self.cmb_scale_arch = QtWidgets.QComboBox()
        self.cmb_scale_arch.addItems(["(Architectural)"] + ARCH_SCALES)
        self.cmb_scale_eng = QtWidgets.QComboBox()
        self.cmb_scale_eng.addItems(["(Engineering)"] + ENG_SCALES)
        h_scale.addWidget(self.cmb_scale_arch, 1)
        h_scale.addWidget(self.cmb_scale_eng, 1)
        v_win.addLayout(h_scale)

        # Export group
        grp_exp = QtWidgets.QGroupBox("Export")
        h_exp = QtWidgets.QHBoxLayout(grp_exp)
        self.chk_flatten = QtWidgets.QCheckBox("Flatten layers")
        self.btn_pdf = QtWidgets.QPushButton("PDF")
        self.btn_dxf = QtWidgets.QPushButton("DXF")
        self.btn_png = QtWidgets.QPushButton("PNG")
        h_exp.addWidget(self.chk_flatten)
        h_exp.addStretch(1)
        h_exp.addWidget(self.btn_pdf)
        h_exp.addWidget(self.btn_dxf)
        h_exp.addWidget(self.btn_png)

        lay.addWidget(grp_sheet)
        lay.addWidget(grp_win, 1)
        lay.addWidget(grp_exp)


def create_layout_drawer(main_window: QtWidgets.QMainWindow) -> LayoutDrawer:
    dock = LayoutDrawer(main_window)
    main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
    dock.hide()
    return dock


__all__ = ["LayoutDrawer", "create_layout_drawer", "ARCH_PAPER", "ARCH_SCALES", "ENG_SCALES"]
