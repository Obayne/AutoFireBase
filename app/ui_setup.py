"""UI setup utilities for MainWindow.

Extracted from main.py to reduce file size and improve maintainability.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.main import MainWindow


def setup_main_window_ui(window: MainWindow) -> None:
    """Set up the main UI components for MainWindow."""
    # This will contain the UI setup code from MainWindow.__init__
    # For now, placeholder - will move code here
    pass


def setup_menus(window: MainWindow) -> None:
    """Set up the menu bar and actions for MainWindow."""
    from PySide6 import QtCore, QtGui, QtWidgets

    from app.tools import draw as draw_tools

    menubar = window.menuBar()
    m_file = menubar.addMenu("&File")
    m_file.addAction("New", window.new_project, QtGui.QKeySequence.StandardKey.New)
    m_file.addAction("Open…", window.open_project, QtGui.QKeySequence.StandardKey.Open)
    m_file.addAction("Save As…", window.save_project_as, QtGui.QKeySequence.StandardKey.SaveAs)
    m_file.addSeparator()
    imp = m_file.addMenu("Import")
    imp.addAction("DXF Underlay…", window.import_dxf_underlay)
    imp.addAction("PDF Underlay…", window.import_pdf_underlay)
    exp = m_file.addMenu("Export")
    exp.addAction("PNG…", window.export_png)
    exp.addAction("PDF…", window.export_pdf)
    exp.addAction("Device Schedule (CSV)…", window.export_device_schedule_csv)
    exp.addAction("Place Symbol Legend", window.place_symbol_legend)
    # Settings submenu (moved under File)
    m_settings = m_file.addMenu("Settings")
    theme = m_settings.addMenu("Theme")
    theme.addAction("Dark", lambda: window.set_theme("dark"))
    theme.addAction("Light", lambda: window.set_theme("light"))
    theme.addAction("High Contrast (Dark)", lambda: window.set_theme("high_contrast"))
    m_file.addSeparator()
    m_file.addAction("Quit", window.close, QtGui.QKeySequence.StandardKey.Quit)

    # Edit menu
    m_edit = menubar.addMenu("&Edit")
    act_undo = QtGui.QAction("Undo", window)
    act_undo.setShortcut(QtGui.QKeySequence.StandardKey.Undo)
    act_undo.triggered.connect(window.undo)
    m_edit.addAction(act_undo)
    act_redo = QtGui.QAction("Redo", window)
    act_redo.setShortcut(QtGui.QKeySequence.StandardKey.Redo)
    act_redo.triggered.connect(window.redo)
    m_edit.addAction(act_redo)
    m_edit.addSeparator()
    act_del = QtGui.QAction("Delete", window)
    act_del.setShortcut(QtCore.Qt.Key.Key_Delete)
    act_del.triggered.connect(window.delete_selection)
    m_edit.addAction(act_del)

    m_tools = menubar.addMenu("&Tools")

    def add_tool(name: str, cb: Any) -> QtGui.QAction:
        act = QtGui.QAction(name, window)
        act.triggered.connect(cb)
        m_tools.addAction(act)
        return act

    window.act_draw_line = add_tool(
        "Draw Line",
        lambda: (
            setattr(window.draw, "layer", window.layer_sketch),
            window.draw.set_mode(draw_tools.DrawMode.LINE),
        ),
    )
    window.act_draw_rect = add_tool(
        "Draw Rect",
        lambda: (
            setattr(window.draw, "layer", window.layer_sketch),
            window.draw.set_mode(draw_tools.DrawMode.RECT),
        ),
    )
    window.act_draw_circle = add_tool(
        "Draw Circle",
        lambda: (
            setattr(window.draw, "layer", window.layer_sketch),
            window.draw.set_mode(draw_tools.DrawMode.CIRCLE),
        ),
    )
    window.act_draw_poly = add_tool(
        "Draw Polyline",
        lambda: (
            setattr(window.draw, "layer", window.layer_sketch),
            window.draw.set_mode(draw_tools.DrawMode.POLYLINE),
        ),
    )
    window.act_draw_arc3 = add_tool(
        "Draw Arc (3-Point)",
        lambda: (
            setattr(window.draw, "layer", window.layer_sketch),
            window.draw.set_mode(draw_tools.DrawMode.ARC3),
        ),
    )
    window.act_draw_wire = add_tool("Draw Wire", lambda: window._set_wire_mode())
    window.act_text = add_tool("Text", window.start_text)
    window.act_mtext = add_tool("MText", window.start_mtext)
    window.act_freehand = add_tool("Freehand", window.start_freehand)
    window.act_leader = add_tool("Leader", window.start_leader)
    window.act_cloud = add_tool("Revision Cloud", window.start_cloud)
    m_tools.addSeparator()
    m_tools.addAction("Dimension (D)", window.start_dimension)
    m_tools.addAction("Measure (M)", window.start_measure)

    # Layout / Paper Space
    m_layout = menubar.addMenu("&Layout")
    m_layout.addAction("Add Page Frame…", window.add_page_frame)
    m_layout.addAction("Remove Page Frame", window.remove_page_frame)
    m_layout.addAction("Add/Update Title Block…", window.add_or_update_title_block)
    m_layout.addAction("Page Setup…", window.page_setup_dialog)
    m_layout.addAction("Add Viewport", window.add_viewport)
    m_layout.addSeparator()
    m_layout.addAction("Switch to Paper Space", lambda: window.toggle_paper_space(True))
    m_layout.addAction("Switch to Model Space", lambda: window.toggle_paper_space(False))
    scale_menu = m_layout.addMenu("Print Scale")

    def add_scale(label: str, inches_per_ft: float) -> None:
        act = QtGui.QAction(label, window)
        act.triggered.connect(lambda v=inches_per_ft: window.set_print_scale(v))
        scale_menu.addAction(act)

    for lbl, v in [
        ("1/16\" = 1'", 1.0 / 16.0),
        ("3/32\" = 1'", 3.0 / 32.0),
        ("1/8\" = 1'", 1.0 / 8.0),
        ("3/16\" = 1'", 3.0 / 16.0),
        ("1/4\" = 1'", 0.25),
        ("3/8\" = 1'", 0.375),
        ("1/2\" = 1'", 0.5),
        ("1\" = 1'", 1.0),
    ]:
        add_scale(lbl, v)
    scale_menu.addAction("Custom…", window.set_print_scale_custom)

    # Modify menu
    m_modify = menubar.addMenu("&Modify")
    m_modify.addAction("Offset Selected…", window.offset_selected_dialog)
    m_modify.addAction("Trim Lines", window.start_trim)
    m_modify.addAction("Finish Trim", window.finish_trim)
    m_modify.addAction("Extend Lines", window.start_extend)
    m_modify.addAction("Fillet (Corner)", window.start_fillet)
    m_modify.addAction("Fillet (Radius)…", window.start_fillet_radius)
    m_modify.addAction("Move", window.start_move)
    m_modify.addAction("Copy", window.start_copy)
    m_modify.addAction("Rotate", window.start_rotate)
    m_modify.addAction("Mirror", window.start_mirror)
    m_modify.addAction("Scale", window.start_scale)
    m_modify.addAction("Chamfer…", window.start_chamfer)

    # Help menu
    m_help = menubar.addMenu("&Help")
    m_help.addAction("User Guide", window.show_user_guide)
    m_help.addAction("Keyboard Shortcuts", window.show_shortcuts)
    m_help.addSeparator()
    m_help.addAction("About", window.show_about)

    # View menu
    m_view = menubar.addMenu("&View")
    window.act_view_grid = QtGui.QAction("Grid", window, checkable=True)
    window.act_view_grid.setChecked(True)
    window.act_view_grid.toggled.connect(window.toggle_grid)
    m_view.addAction(window.act_view_grid)
    window.act_view_snap = QtGui.QAction("Snap", window, checkable=True)
    window.act_view_snap.setChecked(window.scene.snap_enabled)
    window.act_view_snap.toggled.connect(window.toggle_snap)
    m_view.addAction(window.act_view_snap)
    window.act_view_cross = QtGui.QAction("Crosshair (X)", window, checkable=True)
    window.act_view_cross.setChecked(True)
    window.act_view_cross.toggled.connect(window.toggle_crosshair)
    m_view.addAction(window.act_view_cross)
    window.act_paperspace = QtGui.QAction("Paper Space Mode", window, checkable=True)
    window.act_paperspace.setChecked(False)
    window.act_paperspace.toggled.connect(window.toggle_paper_space)
    m_view.addAction(window.act_paperspace)
    window.show_coverage = bool(window.prefs.get("show_coverage", True))
    window.act_view_cov = QtGui.QAction("Show Device Coverage", window, checkable=True)
    window.act_view_cov.setChecked(window.show_coverage)
    window.act_view_cov.toggled.connect(window.toggle_coverage)
    m_view.addAction(window.act_view_cov)
    window.act_view_place_cov = QtGui.QAction(
        "Show Coverage During Placement", window, checkable=True
    )
    window.act_view_place_cov.setChecked(bool(window.prefs.get("show_placement_coverage", True)))
    window.act_view_place_cov.toggled.connect(window.toggle_placement_coverage)
    m_view.addAction(window.act_view_place_cov)
    m_view.addSeparator()
    act_scale = QtGui.QAction("Set Pixels per Foot…", window)
    act_scale.triggered.connect(window.set_px_per_ft)
    m_view.addAction(act_scale)
    act_gridstyle = QtGui.QAction("Grid Style…", window)
    act_gridstyle.triggered.connect(window.grid_style_dialog)
    m_view.addAction(act_gridstyle)
    # Quick snap step presets (guardrail: snap to fixed inch steps or grid)
    snap_menu = m_view.addMenu("Snap Step")
    for lbl, v in [
        ('1"', 12.0),
        ('1/2"', 6.0),
        ('1/4"', 3.0),
        ('1/8"', 1.5),
        ('1/16"', 0.75),
        ('1/32"', 0.375),
        ("Grid", 0.0),
    ]:
        act = QtGui.QAction(lbl, window)
        act.triggered.connect(lambda checked=False, val=v: window.set_snap_step(val))
        snap_menu.addAction(act)

    # Status bar: left space selector/lock; right badges
    window.space_combo = QtWidgets.QComboBox()
    window.space_combo.addItems(["Model", "Paper"])
    window.space_combo.setCurrentIndex(0)
    window.space_lock = QtWidgets.QToolButton()
    window.space_lock.setCheckable(True)
    window.space_lock.setText("Lock")
    window.statusBar().addWidget(QtWidgets.QLabel("Space:"))
    window.statusBar().addWidget(window.space_combo)
    window.statusBar().addWidget(window.space_lock)
    window.space_combo.currentIndexChanged.connect(window._on_space_combo_changed)
    # Right badges
    window.scale_badge = QtWidgets.QLabel("")
    window.scale_badge.setStyleSheet("QLabel { color: #c0c0c0; }")
    window.statusBar().addPermanentWidget(window.scale_badge)
    window.space_badge = QtWidgets.QLabel("MODEL SPACE")
    window.space_badge.setStyleSheet("QLabel { color: #7dcfff; font-weight: bold; }")
    window.statusBar().addPermanentWidget(window.space_badge)
    window._init_sheet_manager()


def setup_toolbar(window: MainWindow) -> None:
    """Set up the main toolbar with drawing and view tools."""
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap

    def create_text_icon(text: str, color: str = "#ffffff") -> QIcon:
        """Create a simple text-based icon."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        painter = QPainter(pixmap)
        painter.setPen(QColor(color))
        painter.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, text)
        painter.end()
        return QIcon(pixmap)

    # Create main toolbar
    tb = QtWidgets.QToolBar("Main")
    tb.setIconSize(QSize(16, 16))
    tb.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
    window.addToolBar(tb)

    # Add view controls with icons
    window.act_view_grid.setIcon(create_text_icon("⊞", "#888888"))
    window.act_view_snap.setIcon(create_text_icon("⊡", "#888888"))
    window.act_view_cross.setIcon(create_text_icon("✛", "#888888"))
    tb.addAction(window.act_view_grid)
    tb.addAction(window.act_view_snap)
    tb.addAction(window.act_view_cross)
    tb.addSeparator()

    # Add drawing tools with icons
    window.act_draw_line.setIcon(create_text_icon("/", "#00ff00"))
    window.act_draw_rect.setIcon(create_text_icon("□", "#00ff00"))
    window.act_draw_circle.setIcon(create_text_icon("○", "#00ff00"))
    window.act_draw_poly.setIcon(create_text_icon("△", "#00ff00"))
    window.act_draw_arc3.setIcon(create_text_icon("⌒", "#00ff00"))
    tb.addAction(window.act_draw_line)
    tb.addAction(window.act_draw_rect)
    tb.addAction(window.act_draw_circle)
    tb.addAction(window.act_draw_poly)
    tb.addAction(window.act_draw_arc3)
    tb.addSeparator()

    # Add other tools with icons
    window.act_draw_wire.setIcon(create_text_icon("⚡", "#ffff00"))
    window.act_text.setIcon(create_text_icon("T", "#ffffff"))
    tb.addAction(window.act_draw_wire)
    tb.addAction(window.act_text)
