"""
App Controller - Central coordinator for multi-window AutoFire application
"""

import json
import os
import sys
import zipfile
from typing import TYPE_CHECKING, Any

# Allow running as `python app\main.py` by fixing sys.path for absolute `app.*` imports
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
)

from app import catalog
from app.logging_config import setup_logging

if TYPE_CHECKING:
    from app.model_space_window import ModelSpaceWindow
    from app.paperspace_window import PaperspaceWindow

    # from app.summary_window import SummaryWindow  # Not yet implemented

# Preferences and logging paths
PREF_DIR = os.path.join(os.path.expanduser("~"), "AutoFire")
PREF_PATH = os.path.join(PREF_DIR, "preferences.json")
LOG_DIR = os.path.join(PREF_DIR, "logs")


def ensure_pref_dir():
    """Ensure preference and log directories exist."""
    try:
        os.makedirs(PREF_DIR, exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)
    except Exception:
        pass


def load_prefs():
    """Load user preferences from disk."""
    ensure_pref_dir()
    if os.path.exists(PREF_PATH):
        try:
            with open(PREF_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_prefs(p):
    """Save user preferences to disk."""
    ensure_pref_dir()
    try:
        with open(PREF_PATH, "w", encoding="utf-8") as f:
            json.dump(p, f, indent=2)
    except Exception:
        pass


# Ensure logging is configured early
setup_logging()
import logging

_logger = logging.getLogger(__name__)


class AppController(QMainWindow):
    """
    Central application controller for multi-window AutoFire.
    Acts as a dummy main window for boot.py compatibility while managing multiple windows.
    """

    # Signals for inter-window communication
    model_space_changed = QtCore.Signal(dict)  # Emitted when model space content changes
    paperspace_changed = QtCore.Signal(dict)  # Emitted when paperspace content changes
    project_changed = QtCore.Signal(str)  # Emitted when project state changes

    def __init__(self):
        # Get Qt application instance (should already exist from main.py)
        self.app = QApplication.instance()
        if self.app is None:
            raise RuntimeError("QApplication must be created before AppController")

        self.app.setApplicationName("AutoFire")
        self.app.setApplicationVersion("0.6.0")

        # Initialize as QMainWindow - this IS the main window now
        super().__init__()
        self.setWindowTitle("AutoFire")
        self.resize(1400, 900)

        # Initialize preferences
        self.prefs = self._load_prefs()

        # Initialize global database connection for coverage calculations
        from db import connection

        connection.initialize_database(in_memory=True)

        # Load device catalog
        self.devices_all = catalog.load_catalog()

        # Window management - these are now child windows
        self.model_space_window: ModelSpaceWindow | None = None
        self.paperspace_window: PaperspaceWindow | None = None
        self.summary_window: Any | None = None  # SummaryWindow not yet implemented

        # Application state
        self.current_project_path: str | None = None
        self.is_modified = False

        # Setup the main UI
        self._setup_main_ui()

        # Setup global menus
        self._setup_global_menus()

        # Show the actual application windows
        self._initialize_windows()

        # Connect layer controls after windows are created
        self._connect_layer_controls()

    def _setup_main_ui(self):
        """Setup the main UI components - tabbed interface for space switching."""
        # Set theme
        self._apply_theme()

        # Create tab widget for space switching
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setMovable(False)

        # Create placeholders for space views
        self.model_space_tab = QtWidgets.QWidget()
        self.paperspace_tab = QtWidgets.QWidget()

        # Setup tab layouts
        model_layout = QtWidgets.QVBoxLayout(self.model_space_tab)
        model_layout.addWidget(QtWidgets.QLabel("Model Space - Loading..."))
        self.tab_widget.addTab(self.model_space_tab, "Model Space")

        paper_layout = QtWidgets.QVBoxLayout(self.paperspace_tab)
        paper_layout.addWidget(QtWidgets.QLabel("Paper Space - Loading..."))
        self.tab_widget.addTab(self.paperspace_tab, "Paper Space")

        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        self.setCentralWidget(self.tab_widget)

        # Setup menus
        self._setup_global_menus()

        # Build docks
        self._build_left_panel()
        self._build_layers_and_props_dock()

    def _on_tab_changed(self, index):
        """Handle tab changes to notify space windows."""
        tab_text = self.tab_widget.tabText(index)
        if tab_text == "Model Space":
            self.model_space_changed.emit()
        elif tab_text == "Paper Space":
            self.paperspace_changed.emit()

    def _setup_status_bar(self):
        """Setup the status bar with space selector and badges."""
        # Space selector combo box
        self.space_combo = QtWidgets.QComboBox()
        self.space_combo.addItems(["Model Space", "Paper Space"])
        self.space_combo.setCurrentIndex(0)

        # Space lock button
        self.space_lock = QtWidgets.QToolButton()
        self.space_lock.setCheckable(True)
        self.space_lock.setText("Lock")

        # Add to status bar
        self.statusBar().addWidget(QtWidgets.QLabel("Space:"))
        self.statusBar().addWidget(self.space_combo)
        self.statusBar().addWidget(self.space_lock)

        # Connect space combo changes
        self.space_combo.currentIndexChanged.connect(self._on_space_combo_changed)

        # Right badges
        self.scale_badge = QtWidgets.QLabel("")
        self.scale_badge.setStyleSheet("QLabel { color: #c0c0c0; }")
        self.statusBar().addPermanentWidget(self.scale_badge)

        self.space_badge = QtWidgets.QLabel("MODEL SPACE")
        self.space_badge.setStyleSheet("QLabel { color: #7dcfff; font-weight: bold; }")
        self.statusBar().addPermanentWidget(self.space_badge)

    def _get_active_space_window(self):
        """Get the currently active space window."""
        # For now, return model space window as primary
        # TODO: Track which space is actually active
        return self.model_space_window

    def _connect_layer_controls(self):
        """Connect layer visibility controls to the active space window."""
        active_window = self._get_active_space_window()
        if active_window:
            self.chk_underlay.toggled.connect(lambda v: active_window.layer_underlay.setVisible(v))
            self.chk_sketch.toggled.connect(lambda v: active_window.layer_sketch.setVisible(v))
            self.chk_wires.toggled.connect(lambda v: active_window.layer_wires.setVisible(v))
            self.chk_devices.toggled.connect(lambda v: active_window.layer_devices.setVisible(v))

            # Sync initial states
            self.chk_underlay.setChecked(active_window.layer_underlay.isVisible())
            self.chk_sketch.setChecked(active_window.layer_sketch.isVisible())
            self.chk_wires.setChecked(active_window.layer_wires.isVisible())
            self.chk_devices.setChecked(active_window.layer_devices.isVisible())

    def _build_left_panel(self):
        """Build the left device palette panel."""
        from PySide6.QtWidgets import QGroupBox, QPushButton, QVBoxLayout, QWidget

        # Device Palette as dockable panel
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setSpacing(5)
        ll.setContentsMargins(5, 5, 5, 5)

        # System Configuration Section
        system_group = QGroupBox("System")
        system_group.setCheckable(True)
        system_layout = QVBoxLayout(system_group)

        facp_btn = QPushButton("System Configuration Wizard")
        facp_btn.setStyleSheet(
            "QPushButton { font-weight: bold; padding: 15px; background-color: #0078d7; color: white; border: none; border-radius: 4px; font-size: 11pt; margin-top: 15px; } QPushButton:hover { background-color: #005a9e; } QPushButton:pressed { background-color: #004578; }"
        )
        # TODO: Connect to actual handler
        # facp_btn.clicked.connect(self.place_facp_panel)
        system_layout.addWidget(facp_btn)

        wire_spool_btn = QPushButton("Wire Spool")
        wire_spool_btn.setStyleSheet(
            "QPushButton { font-weight: bold; padding: 15px; background-color: #555; color: white; border: none; border-radius: 4px; font-size: 11pt; margin-top: 15px; } QPushButton:hover { background-color: #666; } QPushButton:pressed { background-color: #777; }"
        )
        # TODO: Connect to actual handler
        # wire_spool_btn.clicked.connect(self.open_wire_spool)
        system_layout.addWidget(wire_spool_btn)

        ll.addWidget(system_group)

        # Create dock widget
        dock = QtWidgets.QDockWidget("System & Device Palette", self)
        dock.setWidget(left)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def _build_layers_and_props_dock(self):
        """Build the layers and properties dock."""
        from PySide6.QtWidgets import (
            QCheckBox,
            QComboBox,
            QDoubleSpinBox,
            QLabel,
            QLineEdit,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )

        dock = QtWidgets.QDockWidget("Properties", self)
        panel = QWidget()
        form = QVBoxLayout(panel)
        form.setContentsMargins(8, 8, 8, 8)
        form.setSpacing(6)

        # Layer toggles (visibility)
        form.addWidget(QLabel("Layers"))
        self.chk_underlay = QCheckBox("Underlay")
        self.chk_underlay.setChecked(True)
        # TODO: Connect to actual layer visibility
        # self.chk_underlay.toggled.connect(lambda v: self.layer_underlay.setVisible(v))
        form.addWidget(self.chk_underlay)

        self.chk_sketch = QCheckBox("Sketch")
        self.chk_sketch.setChecked(True)
        # TODO: Connect to actual layer visibility
        # self.chk_sketch.toggled.connect(lambda v: self.layer_sketch.setVisible(v))
        form.addWidget(self.chk_sketch)

        self.chk_wires = QCheckBox("Wiring")
        self.chk_wires.setChecked(True)
        # TODO: Connect to actual layer visibility
        # self.chk_wires.toggled.connect(lambda v: self.layer_wires.setVisible(v))
        form.addWidget(self.chk_wires)

        self.chk_devices = QCheckBox("Devices")
        self.chk_devices.setChecked(True)
        # TODO: Connect to actual layer visibility
        # self.chk_devices.toggled.connect(lambda v: self.layer_devices.setVisible(v))
        form.addWidget(self.chk_devices)

        self.btn_layer_manager = QPushButton("Layer Manager")
        # TODO: Connect to actual handler
        # self.btn_layer_manager.clicked.connect(self.open_layer_manager)
        form.addWidget(self.btn_layer_manager)

        # Properties
        form.addSpacing(10)
        lblp = QLabel("Device Properties")
        lblp.setStyleSheet("font-weight:600;")
        form.addWidget(lblp)

        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(4)
        r = 0
        grid.addWidget(QLabel("Label"), r, 0)
        self.prop_label = QLineEdit()
        grid.addWidget(self.prop_label, r, 1)
        r += 1
        grid.addWidget(QLabel("Show Coverage"), r, 0)
        self.prop_showcov = QCheckBox()
        self.prop_showcov.setChecked(True)
        grid.addWidget(self.prop_showcov, r, 1)
        r += 1
        grid.addWidget(QLabel("Offset X (ft)"), r, 0)
        self.prop_offx = QDoubleSpinBox()
        self.prop_offx.setRange(-500, 500)
        self.prop_offx.setDecimals(2)
        grid.addWidget(self.prop_offx, r, 1)
        r += 1
        grid.addWidget(QLabel("Offset Y (ft)"), r, 0)
        self.prop_offy = QDoubleSpinBox()
        self.prop_offy.setRange(-500, 500)
        self.prop_offy.setDecimals(2)
        grid.addWidget(self.prop_offy, r, 1)
        r += 1
        grid.addWidget(QLabel("Mount"), r, 0)
        self.prop_mount = QComboBox()
        self.prop_mount.addItems(["ceiling", "wall"])
        grid.addWidget(self.prop_mount, r, 1)
        r += 1
        grid.addWidget(QLabel("Coverage Mode"), r, 0)
        self.prop_mode = QComboBox()
        self.prop_mode.addItems(["none", "strobe", "speaker", "smoke"])
        grid.addWidget(self.prop_mode, r, 1)
        r += 1
        grid.addWidget(QLabel("Candela (strobe)"), r, 0)
        self.prop_candela = QComboBox()
        self.prop_candela.addItems(["(custom)", "15", "30", "75", "95", "110", "135", "185"])
        grid.addWidget(self.prop_candela, r, 1)
        r += 1
        grid.addWidget(QLabel("Size (ft)"), r, 0)
        self.prop_size = QDoubleSpinBox()
        self.prop_size.setRange(0, 1000)
        self.prop_size.setDecimals(2)
        self.prop_size.setSingleStep(1.0)
        grid.addWidget(self.prop_size, r, 1)
        r += 1

        form.addLayout(grid)
        self.btn_apply_props = QPushButton("Apply")
        form.addWidget(self.btn_apply_props)

        # Disable until selection
        self._enable_props(False)

        # Connect property controls
        self.btn_apply_props.clicked.connect(self._apply_props_clicked)
        self.prop_label.editingFinished.connect(self._apply_label_offset_live)
        self.prop_offx.valueChanged.connect(self._apply_label_offset_live)
        self.prop_offy.valueChanged.connect(self._apply_label_offset_live)
        self.prop_mode.currentTextChanged.connect(self._on_mode_changed_props)

        panel.setLayout(form)
        dock.setWidget(panel)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.sheets_dock = dock
        dock.setVisible(False)
        self.dock_layers_props = dock

    def _apply_props_clicked(self):
        """Apply properties to selected device."""
        active_window = self._get_active_space_window()
        if active_window and hasattr(active_window, "_apply_props_clicked"):
            active_window._apply_props_clicked()

    def _apply_label_offset_live(self):
        """Apply label offset changes live."""
        active_window = self._get_active_space_window()
        if active_window and hasattr(active_window, "_apply_label_offset_live"):
            active_window._apply_label_offset_live()

    def _on_mode_changed_props(self, mode: str):
        """Handle coverage mode changes."""
        active_window = self._get_active_space_window()
        if active_window and hasattr(active_window, "_on_mode_changed_props"):
            active_window._on_mode_changed_props(mode)

    def _enable_props(self, on: bool):
        """Enable or disable property controls."""
        for w in (
            self.prop_label,
            self.prop_offx,
            self.prop_offy,
            self.prop_mount,
            self.prop_mode,
            self.prop_candela,
            self.prop_size,
            self.btn_apply_props,
        ):
            w.setEnabled(on)

    def _build_dxf_layers_dock(self):
        """Build the DXF layers dock."""
        from PySide6.QtWidgets import (
            QCheckBox,
            QHBoxLayout,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )

        dock = QtWidgets.QDockWidget("DXF Layers", self)
        self.dxf_panel = QWidget()
        v = QVBoxLayout(self.dxf_panel)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(6)
        self.lst_dxf = QtWidgets.QListWidget()
        self.lst_dxf.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        v.addWidget(self.lst_dxf)

        # Controls row
        row1 = QHBoxLayout()
        self.btn_dxf_color = QPushButton("Set Color...")
        self.btn_dxf_reset = QPushButton("Reset Color")
        row1.addWidget(self.btn_dxf_color)
        row1.addWidget(self.btn_dxf_reset)
        wrap1 = QWidget()
        wrap1.setLayout(row1)
        v.addWidget(wrap1)

        # Flags row
        row2 = QHBoxLayout()
        self.chk_dxf_lock = QCheckBox("Lock Selected")
        self.chk_dxf_print = QCheckBox("Print Selected")
        self.chk_dxf_print.setChecked(True)
        row2.addWidget(self.chk_dxf_lock)
        row2.addWidget(self.chk_dxf_print)
        wrap2 = QWidget()
        wrap2.setLayout(row2)
        v.addWidget(wrap2)

        dock.setWidget(self.dxf_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.dock_dxf_layers = dock

        # TODO: Connect to actual handlers
        # self.btn_dxf_color.clicked.connect(self._pick_dxf_color)
        # self.btn_dxf_reset.clicked.connect(self._reset_dxf_color)
        # self.lst_dxf.itemChanged.connect(self._toggle_dxf_layer)
        # self.chk_dxf_lock.toggled.connect(self._lock_dxf_layer)
        # self.chk_dxf_print.toggled.connect(self._print_dxf_layer)

        # self._refresh_dxf_layers_dock()

        # Tabify with properties dock if available
        if hasattr(self, "dock_layers_props"):
            try:
                self.tabifyDockWidget(self.dock_layers_props, self.dock_dxf_layers)
            except Exception:
                pass

    def _setup_global_menus(self):
        """Setup global menu actions that work across windows."""
        # File menu actions
        self.action_new_project = QtGui.QAction("New Project", self)
        self.action_new_project.setShortcut(QtGui.QKeySequence.StandardKey.New)
        self.action_new_project.triggered.connect(self.new_project)

        self.action_open_project = QtGui.QAction("Open Project...", self)
        self.action_open_project.setShortcut(QtGui.QKeySequence.StandardKey.Open)
        self.action_open_project.triggered.connect(self.open_project)

        self.action_save_project = QtGui.QAction("Save Project", self)
        self.action_save_project.setShortcut(QtGui.QKeySequence.StandardKey.Save)
        self.action_save_project.triggered.connect(self.save_project)

        self.action_save_project_as = QtGui.QAction("Save Project As...", self)
        self.action_save_project_as.setShortcut(QtGui.QKeySequence.StandardKey.SaveAs)
        self.action_save_project_as.triggered.connect(self.save_project_as)

        # Import/Export actions
        self.action_import_dxf = QtGui.QAction("Import DXF Underlay...", self)
        self.action_import_dxf.triggered.connect(self.import_dxf_underlay)

        self.action_import_pdf = QtGui.QAction("Import PDF Underlay...", self)
        self.action_import_pdf.triggered.connect(self.import_pdf_underlay)

        self.action_export_png = QtGui.QAction("Export PNG...", self)
        self.action_export_png.triggered.connect(self.export_png)

        self.action_export_pdf = QtGui.QAction("Export PDF...", self)
        self.action_export_pdf.triggered.connect(self.export_pdf)

        self.action_export_device_schedule = QtGui.QAction("Export Device Schedule CSV...", self)
        self.action_export_device_schedule.triggered.connect(self.export_device_schedule_csv)

        # Edit menu actions
        self.action_undo = QtGui.QAction("Undo", self)
        self.action_undo.setShortcut(QtGui.QKeySequence.StandardKey.Undo)
        self.action_undo.triggered.connect(self.undo)

        self.action_redo = QtGui.QAction("Redo", self)
        self.action_redo.setShortcut(QtGui.QKeySequence.StandardKey.Redo)
        self.action_redo.triggered.connect(self.redo)

        self.action_delete_selection = QtGui.QAction("Delete", self)
        self.action_delete_selection.setShortcut(QtGui.QKeySequence.StandardKey.Delete)
        self.action_delete_selection.triggered.connect(self.delete_selection)

        self.action_select_all = QtGui.QAction("Select All", self)
        self.action_select_all.setShortcut(QtGui.QKeySequence.StandardKey.SelectAll)
        self.action_select_all.triggered.connect(self.select_all_items)

        # View menu actions
        self.action_zoom_in = QtGui.QAction("Zoom In", self)
        self.action_zoom_in.setShortcut(QtGui.QKeySequence.StandardKey.ZoomIn)
        self.action_zoom_in.triggered.connect(self.zoom_in)

        self.action_zoom_out = QtGui.QAction("Zoom Out", self)
        self.action_zoom_out.setShortcut(QtGui.QKeySequence.StandardKey.ZoomOut)
        self.action_zoom_out.triggered.connect(self.zoom_out)

        self.action_zoom_to_selection = QtGui.QAction("Zoom to Selection", self)
        self.action_zoom_to_selection.triggered.connect(self.zoom_to_selection)

        self.action_fit_view = QtGui.QAction("Fit View to Content", self)
        self.action_fit_view.setShortcut("F2")
        self.action_fit_view.triggered.connect(self.fit_view_to_content)

        self.action_toggle_grid = QtGui.QAction("Grid", self)
        self.action_toggle_grid.setCheckable(True)
        self.action_toggle_grid.setChecked(True)
        self.action_toggle_grid.triggered.connect(self.toggle_grid)

        self.action_toggle_snap = QtGui.QAction("Snap", self)
        self.action_toggle_snap.setCheckable(True)
        self.action_toggle_snap.setChecked(True)
        self.action_toggle_snap.triggered.connect(self.toggle_snap)

        self.action_toggle_crosshair = QtGui.QAction("Crosshair", self)
        self.action_toggle_crosshair.setShortcut("X")
        self.action_toggle_crosshair.setCheckable(True)
        self.action_toggle_crosshair.setChecked(True)
        self.action_toggle_crosshair.triggered.connect(self.toggle_crosshair)

        self.action_toggle_coverage = QtGui.QAction("Coverage Overlays", self)
        self.action_toggle_coverage.setCheckable(True)
        self.action_toggle_coverage.setChecked(True)
        self.action_toggle_coverage.triggered.connect(self.toggle_coverage)

        self.action_toggle_placement_coverage = QtGui.QAction("Placement Coverage", self)
        self.action_toggle_placement_coverage.setCheckable(True)
        self.action_toggle_placement_coverage.setChecked(True)
        self.action_toggle_placement_coverage.triggered.connect(self.toggle_placement_coverage)

        self.action_grid_style = QtGui.QAction("Grid Style...", self)
        self.action_grid_style.triggered.connect(self.grid_style_dialog)

        # Draw menu actions
        self.action_draw_line = QtGui.QAction("Line", self)
        self.action_draw_line.setShortcut("L")
        self.action_draw_line.triggered.connect(lambda: self.start_draw_tool("line"))

        self.action_draw_rectangle = QtGui.QAction("Rectangle", self)
        self.action_draw_rectangle.setShortcut("R")
        self.action_draw_rectangle.triggered.connect(lambda: self.start_draw_tool("rectangle"))

        self.action_draw_circle = QtGui.QAction("Circle", self)
        self.action_draw_circle.setShortcut("C")
        self.action_draw_circle.triggered.connect(lambda: self.start_draw_tool("circle"))

        self.action_draw_polyline = QtGui.QAction("Polyline", self)
        self.action_draw_polyline.setShortcut("P")
        self.action_draw_polyline.triggered.connect(lambda: self.start_draw_tool("polyline"))

        self.action_draw_arc = QtGui.QAction("Arc (3-Point)", self)
        self.action_draw_arc.setShortcut("A")
        self.action_draw_arc.triggered.connect(lambda: self.start_draw_tool("arc"))

        self.action_draw_wire = QtGui.QAction("Wire", self)
        self.action_draw_wire.setShortcut("W")
        self.action_draw_wire.triggered.connect(self.start_wiring)

        self.action_text = QtGui.QAction("Text", self)
        self.action_text.setShortcut("T")
        self.action_text.triggered.connect(self.start_text)

        self.action_mtext = QtGui.QAction("Multi-line Text", self)
        self.action_mtext.triggered.connect(self.start_mtext)

        self.action_freehand = QtGui.QAction("Freehand", self)
        self.action_freehand.triggered.connect(self.start_freehand)

        self.action_leader = QtGui.QAction("Leader", self)
        self.action_leader.triggered.connect(self.start_leader)

        self.action_cloud = QtGui.QAction("Revision Cloud", self)
        self.action_cloud.triggered.connect(self.start_cloud)

        # Modify menu actions
        self.action_trim = QtGui.QAction("Trim", self)
        self.action_trim.setShortcut("Tr")
        self.action_trim.triggered.connect(self.start_trim)

        self.action_extend = QtGui.QAction("Extend", self)
        self.action_extend.setShortcut("Ex")
        self.action_extend.triggered.connect(self.start_extend)

        self.action_fillet = QtGui.QAction("Fillet", self)
        self.action_fillet.setShortcut("Fi")
        self.action_fillet.triggered.connect(self.start_fillet)

        self.action_move = QtGui.QAction("Move", self)
        self.action_move.setShortcut("Mo")
        self.action_move.triggered.connect(self.start_move)

        self.action_copy = QtGui.QAction("Copy", self)
        self.action_copy.setShortcut("Co")
        self.action_copy.triggered.connect(self.start_copy)

        self.action_rotate = QtGui.QAction("Rotate", self)
        self.action_rotate.setShortcut("Ro")
        self.action_rotate.triggered.connect(self.start_rotate)

        self.action_mirror = QtGui.QAction("Mirror", self)
        self.action_mirror.setShortcut("Mi")
        self.action_mirror.triggered.connect(self.start_mirror)

        self.action_scale = QtGui.QAction("Scale", self)
        self.action_scale.setShortcut("Sc")
        self.action_scale.triggered.connect(self.start_scale)

        self.action_chamfer = QtGui.QAction("Chamfer", self)
        self.action_chamfer.setShortcut("Ch")
        self.action_chamfer.triggered.connect(self.start_chamfer)

        self.action_offset = QtGui.QAction("Offset", self)
        self.action_offset.setShortcut("O")
        self.action_offset.triggered.connect(self.offset_selected_dialog)

        # Tools menu actions
        self.action_measure = QtGui.QAction("Measure", self)
        self.action_measure.setShortcut("M")
        self.action_measure.triggered.connect(self.start_measure)

        self.action_dimension = QtGui.QAction("Dimension", self)
        self.action_dimension.setShortcut("D")
        self.action_dimension.triggered.connect(self.start_dimension)

        self.action_place_facp = QtGui.QAction("System Configuration Wizard...", self)
        self.action_place_facp.triggered.connect(self.place_facp_panel)

        self.action_wire_spool = QtGui.QAction("Wire Spool...", self)
        self.action_wire_spool.triggered.connect(self.open_wire_spool)

        self.action_system_builder = QtGui.QAction("System Builder...", self)
        self.action_system_builder.triggered.connect(self.open_system_builder)

        self.action_device_manager = QtGui.QAction("Device Manager...", self)
        self.action_device_manager.triggered.connect(self.open_device_manager)

        self.action_parts_warehouse = QtGui.QAction("Parts Warehouse...", self)
        self.action_parts_warehouse.triggered.connect(self.open_parts_warehouse)

        self.action_layer_manager = QtGui.QAction("Layer Manager...", self)
        self.action_layer_manager.triggered.connect(self.open_layer_manager)

        self.action_settings = QtGui.QAction("Settings...", self)
        self.action_settings.triggered.connect(self.open_settings)

        self.action_token_selector = QtGui.QAction("Place Token...", self)
        self.action_token_selector.triggered.connect(self.place_token)

        # Reports menu actions
        self.action_calculations = QtGui.QAction("Calculations...", self)
        self.action_calculations.triggered.connect(self.show_calculations)

        self.action_bom_report = QtGui.QAction("Bill of Materials...", self)
        self.action_bom_report.triggered.connect(self.show_bom_report)

        self.action_device_schedule = QtGui.QAction("Device Schedule...", self)
        self.action_device_schedule.triggered.connect(self.show_device_schedule_report)

        self.action_riser_diagram = QtGui.QAction("Riser Diagram...", self)
        self.action_riser_diagram.triggered.connect(self.generate_riser_diagram)

        self.action_circuit_properties = QtGui.QAction("Circuit Properties...", self)
        self.action_circuit_properties.triggered.connect(self.show_circuit_properties)

        self.action_job_info = QtGui.QAction("Job Information...", self)
        self.action_job_info.triggered.connect(self.show_job_info_dialog)

        self.action_symbol_legend = QtGui.QAction("Place Symbol Legend", self)
        self.action_symbol_legend.triggered.connect(self.place_symbol_legend)

        # Layout menu actions
        self.action_page_frame = QtGui.QAction("Add Page Frame", self)
        self.action_page_frame.triggered.connect(self.add_page_frame)

        self.action_remove_page_frame = QtGui.QAction("Remove Page Frame", self)
        self.action_remove_page_frame.triggered.connect(self.remove_page_frame)

        self.action_title_block = QtGui.QAction("Add/Update Title Block", self)
        self.action_title_block.triggered.connect(self.add_or_update_title_block)

        self.action_page_setup = QtGui.QAction("Page Setup...", self)
        self.action_page_setup.triggered.connect(self.page_setup_dialog)

        self.action_add_viewport = QtGui.QAction("Add Viewport", self)
        self.action_add_viewport.triggered.connect(self.add_viewport)

        # Help menu actions
        self.action_user_guide = QtGui.QAction("User Guide", self)
        self.action_user_guide.triggered.connect(self.show_user_guide)

        self.action_shortcuts = QtGui.QAction("Keyboard Shortcuts", self)
        self.action_shortcuts.triggered.connect(self.show_shortcuts)

        self.action_about = QtGui.QAction("About Auto-Fire", self)
        self.action_about.triggered.connect(self.show_about)

        # Window menu actions
        self.action_show_model_space = QtGui.QAction("Model Space", self)
        self.action_show_model_space.triggered.connect(self.show_model_space)

        self.action_show_paperspace = QtGui.QAction("Paperspace", self)
        self.action_show_paperspace.triggered.connect(self.show_paperspace)

        self.action_show_summary = QtGui.QAction("Summary", self)
        self.action_show_summary.triggered.connect(self.show_summary_window)

        self.action_arrange_windows = QtGui.QAction("Arrange Windows", self)
        self.action_arrange_windows.triggered.connect(self.arrange_windows)

    def create_global_menu_bar(self, parent_window):
        """Create a standardized menu bar for a window."""
        menubar = parent_window.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.action_new_project)
        file_menu.addAction(self.action_open_project)
        file_menu.addSeparator()
        file_menu.addAction(self.action_save_project)
        file_menu.addAction(self.action_save_project_as)
        file_menu.addSeparator()
        import_menu = file_menu.addMenu("Import")
        import_menu.addAction(self.action_import_dxf)
        import_menu.addAction(self.action_import_pdf)
        export_menu = file_menu.addMenu("Export")
        export_menu.addAction(self.action_export_png)
        export_menu.addAction(self.action_export_pdf)
        export_menu.addAction(self.action_export_device_schedule)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.action_undo)
        edit_menu.addAction(self.action_redo)
        edit_menu.addSeparator()
        edit_menu.addAction(self.action_delete_selection)
        edit_menu.addAction(self.action_select_all)

        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.action_zoom_in)
        view_menu.addAction(self.action_zoom_out)
        view_menu.addAction(self.action_zoom_to_selection)
        view_menu.addAction(self.action_fit_view)
        view_menu.addSeparator()
        view_menu.addAction(self.action_toggle_grid)
        view_menu.addAction(self.action_toggle_snap)
        view_menu.addAction(self.action_toggle_crosshair)
        view_menu.addAction(self.action_toggle_coverage)
        view_menu.addAction(self.action_toggle_placement_coverage)
        view_menu.addSeparator()
        view_menu.addAction(self.action_grid_style)

        # Draw menu
        draw_menu = menubar.addMenu("&Draw")
        draw_menu.addAction(self.action_draw_line)
        draw_menu.addAction(self.action_draw_rectangle)
        draw_menu.addAction(self.action_draw_circle)
        draw_menu.addAction(self.action_draw_polyline)
        draw_menu.addAction(self.action_draw_arc)
        draw_menu.addSeparator()
        draw_menu.addAction(self.action_draw_wire)
        draw_menu.addSeparator()
        draw_menu.addAction(self.action_text)
        draw_menu.addAction(self.action_mtext)
        draw_menu.addAction(self.action_freehand)
        draw_menu.addAction(self.action_leader)
        draw_menu.addAction(self.action_cloud)

        # Modify menu
        modify_menu = menubar.addMenu("&Modify")
        modify_menu.addAction(self.action_trim)
        modify_menu.addAction(self.action_extend)
        modify_menu.addAction(self.action_fillet)
        modify_menu.addSeparator()
        modify_menu.addAction(self.action_move)
        modify_menu.addAction(self.action_copy)
        modify_menu.addAction(self.action_rotate)
        modify_menu.addAction(self.action_mirror)
        modify_menu.addAction(self.action_scale)
        modify_menu.addAction(self.action_chamfer)
        modify_menu.addSeparator()
        modify_menu.addAction(self.action_offset)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction(self.action_measure)
        tools_menu.addAction(self.action_dimension)
        tools_menu.addSeparator()
        tools_menu.addAction(self.action_place_facp)
        tools_menu.addAction(self.action_wire_spool)
        tools_menu.addAction(self.action_system_builder)
        tools_menu.addAction(self.action_device_manager)
        tools_menu.addAction(self.action_parts_warehouse)
        tools_menu.addSeparator()
        tools_menu.addAction(self.action_layer_manager)
        tools_menu.addAction(self.action_settings)
        tools_menu.addAction(self.action_token_selector)

        # Reports menu
        reports_menu = menubar.addMenu("&Reports")
        reports_menu.addAction(self.action_calculations)
        reports_menu.addAction(self.action_bom_report)
        reports_menu.addAction(self.action_device_schedule)
        reports_menu.addAction(self.action_riser_diagram)
        reports_menu.addSeparator()
        reports_menu.addAction(self.action_circuit_properties)
        reports_menu.addAction(self.action_job_info)
        reports_menu.addSeparator()
        reports_menu.addAction(self.action_symbol_legend)

        # Layout menu
        layout_menu = menubar.addMenu("&Layout")
        layout_menu.addAction(self.action_page_frame)
        layout_menu.addAction(self.action_remove_page_frame)
        layout_menu.addAction(self.action_title_block)
        layout_menu.addSeparator()
        layout_menu.addAction(self.action_page_setup)
        layout_menu.addAction(self.action_add_viewport)

        # Window menu
        window_menu = menubar.addMenu("&Window")
        window_menu.addAction(self.action_show_model_space)
        window_menu.addAction(self.action_show_paperspace)
        window_menu.addAction(self.action_show_summary)
        window_menu.addSeparator()
        window_menu.addAction(self.action_arrange_windows)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.action_user_guide)
        help_menu.addAction(self.action_shortcuts)
        help_menu.addSeparator()
        help_menu.addAction(self.action_about)

        return menubar

    def _initialize_windows(self):
        """Initialize and show the main application windows."""
        # Show initial windows
        self.show_model_space()
        self.show_paperspace()

        if self.prefs.get("show_summary_window", False):
            self.show_summary_window()

        # Don't auto-arrange windows to avoid geometry conflicts
        # Qt will position them automatically in a reasonable way

    def _load_prefs(self):
        """Load user preferences."""
        prefs = load_prefs()
        if not prefs:
            prefs = self._get_default_prefs()
        return prefs

    def _get_default_prefs(self):
        """Get default preferences."""
        return {
            "px_per_ft": 12.0,
            "grid": 12,
            "snap": True,
            "show_coverage": True,
            "page_size": "Letter",
            "page_orient": "Landscape",
            "page_margin_in": 0.5,
            "grid_opacity": 0.25,
            "grid_width_px": 0.0,
            "grid_major_every": 5,
            "print_in_per_ft": 0.125,
            "print_dpi": 300,
            "theme": "dark",
            # Project metadata
            "proj_project": "",
            "proj_address": "",
            "proj_sheet": "",
            "proj_date": "",
            "proj_by": "",
            # Multi-window settings
            "multiview_enabled": True,
            "show_summary_window": False,
            "window_positions": {},
        }

    def save_prefs(self):
        """Save user preferences."""
        save_prefs(self.prefs)

    def show_model_space(self):
        """Show or create the model space window."""
        if self.model_space_window is None:
            from app.model_space_window import ModelSpaceWindow

            self.model_space_window = ModelSpaceWindow(self)
            # Reapply theme to ensure new window gets proper styling
            self._apply_theme()
            self.model_space_window.show()
        else:
            self.model_space_window.raise_()
            self.model_space_window.activateWindow()

    def show_paperspace(self):
        """Show or create the paperspace window."""
        if self.paperspace_window is None:
            from app.paperspace_window import PaperspaceWindow

            # Pass the model space scene to paperspace
            model_scene = self.model_space_window.scene if self.model_space_window else None
            self.paperspace_window = PaperspaceWindow(self, model_scene)
            self.paperspace_window.show()
        else:
            self.paperspace_window.raise_()
            self.paperspace_window.activateWindow()

    def show_summary_window(self):
        """Show or create the summary window."""
        if not self.prefs.get("show_summary_window", False):
            return

        if self.summary_window is None:
            # SummaryWindow will be implemented later
            _logger.info("Summary window not yet implemented")
        else:
            self.summary_window.raise_()
            self.summary_window.activateWindow()

    def arrange_windows(self):
        """Arrange windows for optimal multi-monitor workflow."""
        screens = QApplication.screens()
        if len(screens) >= 2:
            # Multi-monitor setup
            primary = screens[0].geometry()
            secondary = screens[1].geometry()

            # Model space on primary monitor
            if self.model_space_window:
                self.model_space_window.setGeometry(primary)

            # Paperspace on secondary monitor
            if self.paperspace_window:
                self.paperspace_window.setGeometry(secondary)

            # Summary window overlay if enabled
            if self.summary_window:
                # Position summary window on secondary monitor
                summary_geom = QtCore.QRect(secondary.x() + 50, secondary.y() + 50, 400, 600)
                self.summary_window.setGeometry(summary_geom)
        else:
            # Single monitor - tile windows
            screen = screens[0].geometry()
            width = screen.width()
            height = screen.height()

            # Model space - left half
            if self.model_space_window:
                self.model_space_window.setGeometry(0, 0, width // 2, height)

            # Paperspace - right half, top
            if self.paperspace_window:
                self.paperspace_window.setGeometry(width // 2, 0, width // 2, height // 2)

            # Summary - right half, bottom
            if self.summary_window:
                self.summary_window.setGeometry(width // 2, height // 2, width // 2, height // 2)

    def new_project(self):
        """Create a new project."""
        # Close existing project
        self.close_project()

        # Reset windows
        if self.model_space_window:
            self.model_space_window._initialize_tools()
        if self.paperspace_window:
            # Reset paperspace to single sheet
            self.paperspace_window.sheets = []
            self.paperspace_window._create_new_sheet()

        self.current_project_path = None
        self.is_modified = False
        self._update_window_titles()

    def open_project(self):
        """Open an existing project."""
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            None, "Open Project", "", "AutoFire Bundle (*.autofire)"
        )

        if not file_path:
            return

        try:
            with zipfile.ZipFile(file_path, "r") as z:
                data = json.loads(z.read("project.json").decode("utf-8"))

            self.load_project_state(data)
            self.current_project_path = file_path
            self.is_modified = False
            self._update_window_titles()

        except Exception as e:
            QMessageBox.critical(None, "Open Project Error", str(e))

    def save_project(self):
        """Save the current project."""
        if not self.current_project_path:
            self.save_project_as()
            return

        try:
            data = self.serialize_project_state()
            with zipfile.ZipFile(
                self.current_project_path, "w", compression=zipfile.ZIP_DEFLATED
            ) as z:
                z.writestr("project.json", json.dumps(data, indent=2))

            self.is_modified = False
            self._update_window_titles()

        except Exception as e:
            QMessageBox.critical(None, "Save Project Error", str(e))

    def save_project_as(self):
        """Save project with a new filename."""
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save Project As", "", "AutoFire Bundle (*.autofire)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".autofire"):
            file_path += ".autofire"

        self.current_project_path = file_path
        self.save_project()

    def serialize_project_state(self):
        """Serialize the complete project state."""
        data = {
            "version": "1.0",
            "metadata": {
                "created": QtCore.QDateTime.currentDateTime().toString(),
                "app_version": self.app.applicationVersion(),
            },
            "preferences": self.prefs.copy(),
        }

        # Get model space state
        if self.model_space_window:
            data["model_space"] = self.model_space_window.get_scene_state()

        # Get paperspace state
        if self.paperspace_window:
            data["paperspace"] = self.paperspace_window.get_sheets_state()

        return data

    def load_project_state(self, data):
        """Load project state from serialized data."""
        # Load preferences
        if "preferences" in data:
            self.prefs.update(data["preferences"])
            self.save_prefs()

        # Load model space
        if "model_space" in data and self.model_space_window:
            self.model_space_window.load_scene_state(data["model_space"])

        # Load paperspace
        if "paperspace" in data and self.paperspace_window:
            self.paperspace_window.load_sheets_state(data["paperspace"])

    def close_project(self):
        """Close the current project."""
        # Clear model space
        if self.model_space_window:
            # Clear devices, wires, sketch
            for item in self.model_space_window.devices_group.childItems():
                item.scene().removeItem(item)
            for item in self.model_space_window.layer_wires.childItems():
                item.scene().removeItem(item)
            for item in self.model_space_window.layer_sketch.childItems():
                item.scene().removeItem(item)

        # Reset paperspace
        if self.paperspace_window:
            self.paperspace_window.sheets = []
            self.paperspace_window._create_new_sheet()

    def _update_window_titles(self):
        """Update window titles with project information."""
        project_name = "Untitled"
        if self.current_project_path:
            project_name = os.path.splitext(os.path.basename(self.current_project_path))[0]

        modified_indicator = " *" if self.is_modified else ""

        if self.model_space_window:
            self.model_space_window.setWindowTitle(
                f"AutoFire - Model Space - {project_name}{modified_indicator}"
            )

        if self.paperspace_window:
            self.paperspace_window.setWindowTitle(
                f"AutoFire - Paperspace - {project_name}{modified_indicator}"
            )

    def on_model_space_closed(self):
        """Handle model space window closure."""
        self.model_space_window = None
        # If both main windows are closed, exit app
        if self.paperspace_window is None:
            self.app.quit()

    def on_paperspace_closed(self):
        """Handle paperspace window closure."""
        self.paperspace_window = None
        # If both main windows are closed, exit app
        if self.model_space_window is None:
            self.app.quit()

    def notify_model_space_changed(self, change_type="general", data=None):
        """Notify all windows that model space has changed."""
        change_data = {
            "type": change_type,
            "data": data or {},
            "timestamp": QtCore.QDateTime.currentDateTime().toString(),
        }
        self.model_space_changed.emit(change_data)

    def notify_paperspace_changed(self, change_type="general", data=None):
        """Notify all windows that paperspace has changed."""
        change_data = {
            "type": change_type,
            "data": data or {},
            "timestamp": QtCore.QDateTime.currentDateTime().toString(),
        }
        self.paperspace_changed.emit(change_data)

    def notify_project_changed(self, change_type="general", data=None):
        """Notify all windows that project state has changed."""
        change_data = {
            "type": change_type,
            "data": data or {},
            "timestamp": QtCore.QDateTime.currentDateTime().toString(),
        }
        self.project_changed.emit(change_data)

    # ---------- Menu action implementations ----------
    # File operations
    def import_dxf_underlay(self):
        """Import DXF file as underlay."""
        if self.model_space_window:
            self.model_space_window.import_dxf_underlay()

    def import_pdf_underlay(self):
        """Import PDF file as underlay."""
        if self.model_space_window:
            self.model_space_window.import_pdf_underlay()

    def export_png(self):
        """Export current view as PNG."""
        if self.model_space_window:
            self.model_space_window.export_png()

    def export_pdf(self):
        """Export current view as PDF."""
        if self.model_space_window:
            self.model_space_window.export_pdf()

    def export_device_schedule_csv(self):
        """Export device schedule as CSV."""
        if self.model_space_window:
            self.model_space_window.export_device_schedule_csv()

    # Edit operations
    def undo(self):
        """Undo the last action."""
        if self.model_space_window:
            self.model_space_window.undo()

    def redo(self):
        """Redo the last undone action."""
        if self.model_space_window:
            self.model_space_window.redo()

    def delete_selection(self):
        """Delete selected items."""
        if self.model_space_window:
            self.model_space_window.delete_selection()

    def select_all_items(self):
        """Select all items in the current view."""
        if self.model_space_window:
            self.model_space_window.select_all_items()

    # View operations
    def zoom_in(self):
        """Zoom in."""
        if self.model_space_window:
            self.model_space_window.zoom_in()

    def zoom_out(self):
        """Zoom out."""
        if self.model_space_window:
            self.model_space_window.zoom_out()

    def zoom_to_selection(self):
        """Zoom to selected items."""
        if self.model_space_window:
            self.model_space_window.zoom_to_selection()

    def fit_view_to_content(self):
        """Fit view to show all content."""
        if self.model_space_window:
            self.model_space_window.fit_view_to_content()

    def toggle_grid(self, on: bool):
        """Toggle grid visibility."""
        if self.model_space_window:
            self.model_space_window.toggle_grid(on)

    def toggle_snap(self, on: bool):
        """Toggle snap functionality."""
        if self.model_space_window:
            self.model_space_window.toggle_snap(on)

    def toggle_crosshair(self, on: bool):
        """Toggle crosshair visibility."""
        if self.model_space_window:
            self.model_space_window.toggle_crosshair(on)

    def toggle_coverage(self, on: bool):
        """Toggle coverage overlays."""
        if self.model_space_window:
            self.model_space_window.toggle_coverage(on)

    def toggle_placement_coverage(self, on: bool):
        """Toggle placement coverage."""
        if self.model_space_window:
            self.model_space_window.toggle_placement_coverage(on)

    def grid_style_dialog(self):
        """Show grid style dialog."""
        if self.model_space_window:
            self.model_space_window.grid_style_dialog()

    # Draw operations
    def start_draw_tool(self, tool_type: str):
        """Start a drawing tool."""
        if self.model_space_window:
            self.model_space_window.start_draw_tool(tool_type)

    def start_wiring(self):
        """Start wiring tool."""
        if self.model_space_window:
            self.model_space_window.start_wiring()

    def start_text(self):
        """Start text tool."""
        if self.model_space_window:
            self.model_space_window.start_text()

    def start_mtext(self):
        """Start multi-line text tool."""
        if self.model_space_window:
            self.model_space_window.start_mtext()

    def start_freehand(self):
        """Start freehand drawing tool."""
        if self.model_space_window:
            self.model_space_window.start_freehand()

    def start_leader(self):
        """Start leader tool."""
        if self.model_space_window:
            self.model_space_window.start_leader()

    def start_cloud(self):
        """Start revision cloud tool."""
        if self.model_space_window:
            self.model_space_window.start_cloud()

    # Modify operations
    def start_trim(self):
        """Start trim tool."""
        if self.model_space_window:
            self.model_space_window.start_trim()

    def start_extend(self):
        """Start extend tool."""
        if self.model_space_window:
            self.model_space_window.start_extend()

    def start_fillet(self):
        """Start fillet tool."""
        if self.model_space_window:
            self.model_space_window.start_fillet()

    def start_move(self):
        """Start move tool."""
        if self.model_space_window:
            self.model_space_window.start_move()

    def start_copy(self):
        """Start copy tool."""
        if self.model_space_window:
            self.model_space_window.start_copy()

    def start_rotate(self):
        """Start rotate tool."""
        if self.model_space_window:
            self.model_space_window.start_rotate()

    def start_mirror(self):
        """Start mirror tool."""
        if self.model_space_window:
            self.model_space_window.start_mirror()

    def start_scale(self):
        """Start scale tool."""
        if self.model_space_window:
            self.model_space_window.start_scale()

    def start_chamfer(self):
        """Start chamfer tool."""
        if self.model_space_window:
            self.model_space_window.start_chamfer()

    def offset_selected_dialog(self):
        """Show offset dialog for selected items."""
        if self.model_space_window:
            self.model_space_window.offset_selected_dialog()

    # Tools operations
    def start_measure(self):
        """Start measure tool."""
        if self.model_space_window:
            self.model_space_window.start_measure()

    def start_dimension(self):
        """Start dimension tool."""
        if self.model_space_window:
            self.model_space_window.start_dimension()

    def place_facp_panel(self):
        """Place FACP panel using wizard."""
        if self.model_space_window:
            self.model_space_window.place_facp_panel()

    def open_wire_spool(self):
        """Open wire spool dialog."""
        if self.model_space_window:
            self.model_space_window.open_wire_spool()

    def open_system_builder(self):
        """Open system builder dialog."""
        if self.model_space_window:
            self.model_space_window.open_system_builder()

    def open_device_manager(self):
        """Open device manager dialog."""
        if self.model_space_window:
            self.model_space_window.open_device_manager()

    def open_parts_warehouse(self):
        """Open parts warehouse dialog."""
        if self.model_space_window:
            self.model_space_window.open_parts_warehouse()
        if self.model_space_window:
            self.model_space_window.open_parts_warehouse()

    def open_layer_manager(self):
        """Open layer manager dialog."""
        if self.model_space_window:
            self.model_space_window.open_layer_manager()

    def open_settings(self):
        """Open settings dialog."""
        if self.model_space_window:
            self.model_space_window.open_settings()

    def place_token(self):
        """Place token on selected device."""
        if self.model_space_window:
            self.model_space_window.place_token()

    # Reports operations
    def show_calculations(self):
        """Show calculations dialog."""
        if self.model_space_window:
            self.model_space_window.show_calculations()

    def show_bom_report(self):
        """Show bill of materials report."""
        if self.model_space_window:
            self.model_space_window.show_bom_report()

    def show_device_schedule_report(self):
        """Show device schedule report."""
        if self.model_space_window:
            self.model_space_window.show_device_schedule_report()

    def generate_riser_diagram(self):
        """Generate riser diagram."""
        if self.model_space_window:
            self.model_space_window.generate_riser_diagram()

    def show_circuit_properties(self):
        """Show circuit properties dialog."""
        if self.model_space_window:
            self.model_space_window.show_circuit_properties()

    def show_job_info_dialog(self):
        """Show job information dialog."""
        if self.model_space_window:
            self.model_space_window.show_job_info_dialog()

    def place_symbol_legend(self):
        """Place symbol legend on drawing."""
        if self.model_space_window:
            self.model_space_window.place_symbol_legend()

    # Layout operations
    def add_page_frame(self):
        """Add page frame to layout."""
        if self.model_space_window:
            self.model_space_window.add_page_frame()

    def remove_page_frame(self):
        """Remove page frame from layout."""
        if self.model_space_window:
            self.model_space_window.remove_page_frame()

    def add_or_update_title_block(self):
        """Add or update title block."""
        if self.model_space_window:
            self.model_space_window.add_or_update_title_block()

    def page_setup_dialog(self):
        """Show page setup dialog."""
        if self.model_space_window:
            self.model_space_window.page_setup_dialog()

    def add_viewport(self):
        """Add viewport to paperspace."""
        if self.paperspace_window:
            self.paperspace_window.add_viewport()

    # Help operations
    def show_user_guide(self):
        """Show user guide."""
        QtWidgets.QMessageBox.information(
            None, "User Guide", "User guide functionality would be implemented here."
        )

    def show_shortcuts(self):
        """Show keyboard shortcuts in a formatted dialog."""
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Keyboard Shortcuts")
        dialog.setModal(True)
        dialog.resize(500, 600)

        layout = QtWidgets.QVBoxLayout(dialog)

        # Title
        title = QtWidgets.QLabel("AutoFire Keyboard Shortcuts")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Create tab widget for organized shortcuts
        tab_widget = QtWidgets.QTabWidget()

        # Drawing shortcuts
        drawing_tab = QtWidgets.QWidget()
        drawing_layout = QtWidgets.QVBoxLayout(drawing_tab)

        drawing_text = QtWidgets.QTextEdit()
        drawing_text.setReadOnly(True)
        drawing_text.setPlainText(
            """Drawing Tools:
L          - Draw Line
R          - Draw Rectangle
C          - Draw Circle
P          - Draw Polyline
A          - Draw Arc (3-Point)
W          - Draw Wire

Text & Annotations:
T          - Text Tool
M          - Measure Tool
D          - Dimension Tool

Modify Tools:
Mo         - Move
Co         - Copy
Ro         - Rotate
Sc         - Scale
Mi         - Mirror
Tr         - Trim
Ex         - Extend
Fi         - Fillet
Ch         - Chamfer
O          - Offset"""
        )
        drawing_layout.addWidget(drawing_text)
        tab_widget.addTab(drawing_tab, "Drawing & Modify")

        # View shortcuts
        view_tab = QtWidgets.QWidget()
        view_layout = QtWidgets.QVBoxLayout(view_tab)

        view_text = QtWidgets.QTextEdit()
        view_text.setReadOnly(True)
        view_text.setPlainText(
            """View Controls:
F2         - Fit View to Content
+ / -      - Zoom In/Out
Ctrl+Mouse - Pan View
Space      - Pan Mode

Display Toggles:
G          - Toggle Grid
S          - Toggle Snap
X          - Toggle Crosshair
V          - Toggle Coverage Overlays

Window Management:
Ctrl+N     - New Project
Ctrl+O     - Open Project
Ctrl+S     - Save Project
Ctrl+P     - Export PNG"""
        )
        view_layout.addWidget(view_text)
        tab_widget.addTab(view_tab, "View & Windows")

        # Selection shortcuts
        selection_tab = QtWidgets.QWidget()
        selection_layout = QtWidgets.QVBoxLayout(selection_tab)

        selection_text = QtWidgets.QTextEdit()
        selection_text.setReadOnly(True)
        selection_text.setPlainText(
            """Selection:
Esc        - Cancel Active Tool
Delete     - Delete Selection
Ctrl+A     - Select All
Ctrl+D     - Clear Selection

Device Operations:
Right-click - Context menu for device operations
Double-click - Quick place device

Special Modes:
Shift      - Orthogonal mode (ortho)
Ctrl       - Constrain proportions"""
        )
        selection_layout.addWidget(selection_text)
        tab_widget.addTab(selection_tab, "Selection & Special")

        layout.addWidget(tab_widget)

        # Close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def show_about(self):
        """Show about dialog."""
        QtWidgets.QMessageBox.about(
            None, "About Auto-Fire", "Auto-Fire CAD Application\nVersion: 0.6.0"
        )

    # ---------- Theme Support ----------
    def _apply_theme(self):
        """Apply the current theme."""
        name = self.prefs.get("theme", "dark")
        primary_color = self.prefs.get("primary_color", "#0078d7")
        if name == "light":
            self.apply_light_theme(primary_color)
        elif name in ("hc", "high", "high_contrast", "high-contrast"):
            self.apply_high_contrast_theme(primary_color)
        elif name == "blue":
            self.apply_blue_theme()
        elif name == "green":
            self.apply_green_theme()
        else:
            self.apply_dark_theme(primary_color)

    def set_theme(self, name: str):
        """Set the application theme."""
        name = (name or "dark").lower()
        self.prefs["theme"] = name
        self._apply_theme()
        self.save_prefs()

    def apply_dark_theme(self, primary_color):
        """Apply dark theme."""
        app = QtWidgets.QApplication.instance()
        if app is None:
            return
        pal = app.palette()
        bg = QtGui.QColor(25, 26, 28)
        base = QtGui.QColor(32, 33, 36)
        text = QtGui.QColor(220, 220, 225)
        pal.setColor(QtGui.QPalette.ColorRole.Window, bg)
        pal.setColor(QtGui.QPalette.ColorRole.Base, base)
        pal.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(38, 39, 43))
        pal.setColor(QtGui.QPalette.ColorRole.Text, text)
        pal.setColor(QtGui.QPalette.ColorRole.WindowText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Button, base)
        pal.setColor(QtGui.QPalette.ColorRole.ButtonText, text)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipBase, base)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(primary_color))
        pal.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(255, 255, 255))
        app.setPalette(pal)
        self._apply_menu_stylesheet(contrast_boost=False)

    def apply_light_theme(self, primary_color):
        """Apply light theme."""
        app = QtWidgets.QApplication.instance()
        if app is None:
            return
        pal = app.palette()
        bg = QtGui.QColor(245, 246, 248)
        base = QtGui.QColor(255, 255, 255)
        text = QtGui.QColor(20, 20, 25)
        pal.setColor(QtGui.QPalette.ColorRole.Window, bg)
        pal.setColor(QtGui.QPalette.ColorRole.Base, base)
        pal.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(240, 240, 245))
        pal.setColor(QtGui.QPalette.ColorRole.Text, text)
        pal.setColor(QtGui.QPalette.ColorRole.WindowText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Button, base)
        pal.setColor(QtGui.QPalette.ColorRole.ButtonText, text)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipBase, base)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(primary_color))
        pal.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(255, 255, 255))
        app.setPalette(pal)
        self._apply_menu_stylesheet(contrast_boost=False)

    def apply_high_contrast_theme(self, primary_color):
        """Apply high contrast theme."""
        app = QtWidgets.QApplication.instance()
        if app is None:
            return
        pal = app.palette()
        bg = QtGui.QColor(18, 18, 18)
        base = QtGui.QColor(10, 10, 12)
        text = QtGui.QColor(245, 245, 245)
        pal.setColor(QtGui.QPalette.ColorRole.Window, bg)
        pal.setColor(QtGui.QPalette.ColorRole.Base, base)
        pal.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(28, 28, 32))
        pal.setColor(QtGui.QPalette.ColorRole.Text, text)
        pal.setColor(QtGui.QPalette.ColorRole.WindowText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Button, base)
        pal.setColor(QtGui.QPalette.ColorRole.ButtonText, text)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipBase, base)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(primary_color))
        pal.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(255, 255, 255))
        app.setPalette(pal)
        self._apply_menu_stylesheet(contrast_boost=True)

    def apply_blue_theme(self):
        """Apply blue theme."""
        app = QtWidgets.QApplication.instance()
        if app is None:
            return
        pal = app.palette()
        bg = QtGui.QColor(15, 20, 30)
        base = QtGui.QColor(25, 30, 40)
        text = QtGui.QColor(200, 210, 220)
        pal.setColor(QtGui.QPalette.ColorRole.Window, bg)
        pal.setColor(QtGui.QPalette.ColorRole.Base, base)
        pal.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(35, 40, 50))
        pal.setColor(QtGui.QPalette.ColorRole.Text, text)
        pal.setColor(QtGui.QPalette.ColorRole.WindowText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Button, base)
        pal.setColor(QtGui.QPalette.ColorRole.ButtonText, text)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipBase, base)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(0, 120, 215))
        pal.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(255, 255, 255))
        app.setPalette(pal)
        self._apply_menu_stylesheet(contrast_boost=False)

    def apply_green_theme(self):
        """Apply green theme."""
        app = QtWidgets.QApplication.instance()
        if app is None:
            return
        pal = app.palette()
        bg = QtGui.QColor(15, 25, 15)
        base = QtGui.QColor(25, 35, 25)
        text = QtGui.QColor(200, 220, 200)
        pal.setColor(QtGui.QPalette.ColorRole.Window, bg)
        pal.setColor(QtGui.QPalette.ColorRole.Base, base)
        pal.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(30, 40, 30))
        pal.setColor(QtGui.QPalette.ColorRole.Text, text)
        pal.setColor(QtGui.QPalette.ColorRole.WindowText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Button, base)
        pal.setColor(QtGui.QPalette.ColorRole.ButtonText, text)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipBase, base)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(0, 150, 0))
        pal.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(255, 255, 255))
        app.setPalette(pal)
        self._apply_menu_stylesheet(contrast_boost=False)

    def _apply_menu_stylesheet(self, contrast_boost=False):
        """Apply menu stylesheet for better visibility to all windows."""
        if contrast_boost:
            style = """
            QMenuBar { background-color: #1a1a1a; color: #ffffff; }
            QMenuBar::item { background-color: transparent; color: #ffffff; padding: 4px 8px; }
            QMenuBar::item:selected { background-color: #0078d7; color: #ffffff; }
            QMenu { background-color: #1a1a1a; color: #ffffff; border: 1px solid #333; }
            QMenu::item { background-color: transparent; color: #ffffff; padding: 4px 20px; }
            QMenu::item:selected { background-color: #0078d7; color: #ffffff; }
            QMainWindow { background-color: #1a1a1a; color: #ffffff; }
            QMainWindow::title { background-color: #1a1a1a; color: #ffffff; }
            """
        else:
            style = """
            QMenuBar { background-color: #2a2a2a; color: #e0e0e0; }
            QMenuBar::item { background-color: transparent; color: #e0e0e0; padding: 4px 8px; }
            QMenuBar::item:selected { background-color: #0078d7; color: #ffffff; }
            QMenu { background-color: #2a2a2a; color: #e0e0e0; border: 1px solid #444; }
            QMenu::item { background-color: transparent; color: #e0e0e0; padding: 4px 20px; }
            QMenu::item:selected { background-color: #0078d7; color: #ffffff; }
            QMainWindow { background-color: #2a2a2a; color: #e0e0e0; }
            QMainWindow::title { background-color: #2a2a2a; color: #e0e0e0; }
            """

        # Apply stylesheet to all windows
        windows_to_style = [self]
        if self.model_space_window:
            windows_to_style.append(self.model_space_window)
        if self.paperspace_window:
            windows_to_style.append(self.paperspace_window)

        for window in windows_to_style:
            window.setStyleSheet(style)

    def run(self):
        """Start the application (called by boot.py)."""
        # The boot.py will call app.exec(), so we just return self
        return self


def main():
    """Main application entry point."""
    controller = AppController()
    return controller.run()


if __name__ == "__main__":
    main()
