# apply_cad_step1_064.py
# CAD Step 1: hand-pan, duplicate, rotate, nudge, align-to-grid, selection count.
# Writes: app/tools/transform.py, app/main.py  (creates .bak-<timestamp> backups)

from pathlib import Path
import time

ROOT = Path(".").resolve()
STAMP = time.strftime("%Y%m%d_%H%M%S")

FILES = {}

FILES[
    "app/tools/transform.py"
] = r'''
from PySide6 import QtCore, QtGui, QtWidgets
from app.device import DeviceItem

def _clone_item(it: QtWidgets.QGraphicsItem) -> QtWidgets.QGraphicsItem | None:
    # Support DeviceItem and generic QGraphicsPathItem; ignore others for now
    if isinstance(it, DeviceItem):
        d = it.to_json()
        clone = DeviceItem(float(d["x"]), float(d["y"]), d["symbol"], d["name"],
                           d.get("manufacturer",""), d.get("part_number",""))
        # label offset / coverage already in to_json
        if d.get("coverage"): clone.set_coverage(d["coverage"])
        if "label_offset" in d:
            off = d["label_offset"]
            if isinstance(off, (list, tuple)) and len(off)==2:
                clone.set_label_offset(float(off[0]), float(off[1]))
        return clone
    elif isinstance(it, QtWidgets.QGraphicsPathItem):
        c = QtWidgets.QGraphicsPathItem()
        c.setPath(it.path())
        c.setPen(it.pen())
        c.setBrush(it.brush())
        c.setZValue(it.zValue())
        c.setTransform(it.transform())
        return c
    else:
        return None

def duplicate_selected(scene: QtWidgets.QGraphicsScene, parent_group: QtWidgets.QGraphicsItem, dx_px: float = 12.0, dy_px: float = 12.0):
    sel = scene.selectedItems()
    if not sel:
        return 0
    count = 0
    for it in sel:
        clone = _clone_item(it)
        if clone is None:
            continue
        # position clone near original
        clone.setPos(it.pos() + QtCore.QPointF(dx_px, dy_px))
        clone.setParentItem(parent_group)
        count += 1
    return count

def rotate_selected(scene: QtWidgets.QGraphicsScene, angle_deg: float):
    sel = scene.selectedItems()
    if not sel:
        return 0
    for it in sel:
        it.setRotation(it.rotation() + angle_deg)
    return len(sel)

def nudge_selected(scene: QtWidgets.QGraphicsScene, dx_px: float, dy_px: float):
    sel = scene.selectedItems()
    if not sel:
        return 0
    for it in sel:
        it.setPos(it.pos() + QtCore.QPointF(dx_px, dy_px))
    return len(sel)

def align_selected_to_grid(scene, px_per_ft: float, snap_step_px: float, grid_size: int):
    """
    If snap_step_px > 0, snap to that interval in pixels.
    Otherwise snap to the grid intersections (grid_size pixels).
    """
    sel = scene.selectedItems()
    if not sel:
        return 0
    step = float(snap_step_px) if (snap_step_px and snap_step_px > 0) else float(grid_size)
    if step <= 0:
        step = float(grid_size) if grid_size > 0 else 12.0
    def _snap(v: float) -> float:
        return round(v / step) * step
    for it in sel:
        p = it.pos()
        it.setPos(QtCore.QPointF(_snap(p.x()), _snap(p.y())))
    return len(sel)
'''

FILES[
    "app/main.py"
] = r"""
import os, json, zipfile
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QPointF, QSize
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QLineEdit, QLabel, QToolBar, QFileDialog,
    QGraphicsView, QGraphicsPathItem, QMenu, QDockWidget, QCheckBox, QSpinBox, QComboBox, QMessageBox)

from app.scene import GridScene, DEFAULT_GRID_SIZE
from app.device import DeviceItem
from app import catalog
from app.tools import draw as draw_tools
from app.tools.array import ArrayTool
from app.tools.dimension import DimensionTool
from app.tools import transform
from app.dialogs.coverage import CoverageDialog
from app import units

APP_VERSION = "0.6.4-cadstep1"
APP_TITLE = f"Auto-Fire {APP_VERSION}"
PREF_DIR = os.path.join(os.path.expanduser("~"), "AutoFire")
PREF_PATH = os.path.join(PREF_DIR, "preferences.json")
LOG_DIR = os.path.join(PREF_DIR, "logs")

def ensure_pref_dir():
    try:
        os.makedirs(PREF_DIR, exist_ok=True); os.makedirs(LOG_DIR, exist_ok=True)
    except Exception:
        pass

def load_prefs():
    ensure_pref_dir()
    if os.path.exists(PREF_PATH):
        try:
            with open(PREF_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_prefs(p):
    ensure_pref_dir()
    try:
        with open(PREF_PATH, "w", encoding="utf-8") as f:
            json.dump(p, f, indent=2)
    except Exception:
        pass

class CanvasView(QGraphicsView):
    def __init__(self, scene, devices_group, wires_group, sketch_group, overlay_group, window_ref):
        super().__init__(scene)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setMouseTracking(True)
        self.current_proto = None
        self.devices_group = devices_group
        self.wires_group = wires_group
        self.sketch_group = sketch_group
        self.overlay_group = overlay_group
        self.ortho = False
        self.win = window_ref

        # crosshair
        self.cross_v = QtWidgets.QGraphicsLineItem(); self.cross_h = QtWidgets.QGraphicsLineItem()
        pen = QtGui.QPen(QtGui.QColor(130,130,130,160)); pen.setCosmetic(True); pen.setStyle(Qt.DashLine)
        self.cross_v.setPen(pen); self.cross_h.setPen(pen)
        self.cross_v.setParentItem(self.overlay_group); self.cross_h.setParentItem(self.overlay_group)
        self.show_crosshair = True

        self._hand_pan = False  # spacebar pressed?

    def set_current_device(self, proto: dict):
        self.current_proto = proto
        self.win.current_proto = proto
        self.win.statusBar().showMessage(f"Selected: {proto.get('name','?')}")

    def _update_crosshair(self, sp: QPointF):
        if not self.show_crosshair: return
        rect = self.scene().sceneRect()
        self.cross_v.setLine(sp.x(), rect.top(), sp.x(), rect.bottom())
        self.cross_h.setLine(rect.left(), sp.y(), rect.right(), sp.y())
        dx_ft = units.px_to_ft(sp.x(), self.win.px_per_ft)
        dy_ft = units.px_to_ft(sp.y(), self.win.px_per_ft)
        self.win.statusBar().showMessage(f"sel={self.win.selection_count}  x={units.fmt_ft_inches(dx_ft)}   y={units.fmt_ft_inches(dy_ft)}   scale={self.win.px_per_ft:.2f} px/ft  snap={self.win.snap_label}")

    def wheelEvent(self, e: QtGui.QWheelEvent):
        s = 1.15 if e.angleDelta().y() > 0 else 1/1.15
        self.scale(s, s)

    def mousePressEvent(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._hand_pan = True
            self.viewport().setCursor(Qt.OpenHandCursor)
        win = self.win
        sp = self.scene().snap(self.mapToScene(e.position().toPoint()))
        if e.button()==Qt.LeftButton:
            # array tool
            if getattr(win, "array_tool", None) and win.array_tool.pending:
                if win.array_tool.on_click(sp): win.push_history(); e.accept(); return
            # drawing tool
            if getattr(win, "draw", None) and win.draw.mode != draw_tools.DrawMode.NONE:
                if win.draw.on_click(sp, shift_ortho=self.ortho): win.push_history(); e.accept(); return
            # dimension tool
            if getattr(win, "dim_tool", None) and win.dim_tool.active:
                if win.dim_tool.on_click(sp): e.accept(); return
            # device placement
            if self.current_proto:
                d = self.current_proto
                it = DeviceItem(sp.x(), sp.y(), d["symbol"], d["name"], d.get("manufacturer",""), d.get("part_number",""))
                it.setParentItem(self.devices_group); win.push_history(); e.accept(); return
        elif e.button()==Qt.RightButton:
            win.canvas_menu(e.globalPosition().toPoint()); e.accept(); return
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e: QtGui.QMouseEvent):
        sp = self.mapToScene(e.position().toPoint())
        self._update_crosshair(sp)
        if getattr(self.win, "draw", None): self.win.draw.on_mouse_move(sp, shift_ortho=self.ortho)
        if getattr(self.win, "dim_tool", None): self.win.dim_tool.on_mouse_move(sp)
        if getattr(self.win, "array_tool", None): self.win.array_tool.on_mouse_move(sp)
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.MiddleButton and self._hand_pan:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.viewport().unsetCursor()
            self._hand_pan = False
        super().mouseReleaseEvent(e)

    def keyPressEvent(self, e: QtGui.QKeyEvent):
        if e.key()==Qt.Key_Shift:
            self.ortho=True; e.accept(); return
        if e.key()==Qt.Key_C:
            self.show_crosshair = not self.show_crosshair; e.accept(); return
        if e.key()==Qt.Key_Space and not self._hand_pan:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.viewport().setCursor(Qt.OpenHandCursor)
            self._hand_pan = True
            e.accept(); return
        if e.key()==Qt.Key_Escape:
            if getattr(self.win, "draw", None) and self.win.draw.mode != draw_tools.DrawMode.NONE:
                self.win.draw.finish(); e.accept(); return
            if getattr(self.win, "array_tool", None) and self.win.array_tool.pending:
                self.win.array_tool.cancel(); e.accept(); return
        super().keyPressEvent(e)

    def keyReleaseEvent(self, e: QtGui.QKeyEvent):
        if e.key()==Qt.Key_Shift:
            self.ortho=False; e.accept(); return
        if e.key()==Qt.Key_Space and self._hand_pan:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.viewport().unsetCursor()
            self._hand_pan = False
            e.accept(); return
        super().keyReleaseEvent(e)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1400, 900)
        self.prefs = load_prefs()
        self.px_per_ft = float(self.prefs.get("px_per_ft", 12.0))
        self.snap_label = self.prefs.get("snap_label", "grid")
        self.snap_step_in = float(self.prefs.get("snap_step_in", 0.0))  # inches
        self.current_proto = None
        self.selection_count = 0

        # dark theme
        pal = self.palette()
        pal.setColor(QtGui.QPalette.Window, QtGui.QColor(32,32,36))
        pal.setColor(QtGui.QPalette.Base,   QtGui.QColor(26,26,28))
        pal.setColor(QtGui.QPalette.Text,   QtCore.Qt.white)
        pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        pal.setColor(QtGui.QPalette.Button, QtGui.QColor(48,48,52))
        pal.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        self.setPalette(pal)

        self.devices_all = catalog.load_catalog()

        self.scene = GridScene(int(self.prefs.get("grid", DEFAULT_GRID_SIZE)), 0,0,12000,9000)
        self.scene.snap_enabled = bool(self.prefs.get("snap", True))
        self._apply_snap_step_from_inches(self.snap_step_in)
        self.scene.setSceneRect(0,0,12000,9000)

        # layers
        self.layer_underlay = QtWidgets.QGraphicsItemGroup(); self.layer_underlay.setZValue(-10); self.scene.addItem(self.layer_underlay)
        self.layer_sketch   = QtWidgets.QGraphicsItemGroup(); self.layer_sketch.setZValue(40);   self.scene.addItem(self.layer_sketch)
        self.layer_wires    = QtWidgets.QGraphicsItemGroup(); self.layer_wires.setZValue(60);    self.scene.addItem(self.layer_wires)
        self.layer_devices  = QtWidgets.QGraphicsItemGroup(); self.layer_devices.setZValue(100);  self.scene.addItem(self.layer_devices)
        self.layer_overlay  = QtWidgets.QGraphicsItemGroup(); self.layer_overlay.setZValue(200);  self.scene.addItem(self.layer_overlay)

        self.view = CanvasView(self.scene, self.layer_devices, self.layer_wires, self.layer_sketch, self.layer_overlay, self)

        self.current_underlay_path = None
        self.draw = draw_tools.DrawController(self, self.layer_sketch)
        self.array_tool = ArrayTool(self, self.layer_devices)
        self.dim_tool = DimensionTool(self, self.layer_overlay)

        # menus
        menubar = self.menuBar()
        m_file = menubar.addMenu("&File")
        m_file.addAction("New", self.new_project, QtGui.QKeySequence.New)
        m_file.addAction("Open…", self.open_project, QtGui.QKeySequence.Open)
        m_file.addAction("Save As…", self.save_project_as, QtGui.QKeySequence.SaveAs)
        m_file.addSeparator()
        m_file.addAction("Import DXF Underlay…", self.import_dxf_underlay)
        m_file.addAction("Export PNG…", self.export_png)
        m_file.addSeparator()
        m_file.addAction("Quit", self.close, QtGui.QKeySequence.Quit)

        m_edit = menubar.addMenu("&Edit")
        act_dup = QtGui.QAction("Duplicate (Ctrl+D)", self, triggered=self.dup_selected); act_dup.setShortcut(QtGui.QKeySequence("Ctrl+D")); m_edit.addAction(act_dup)
        m_edit.addSeparator()
        m_edit.addAction("Rotate Left 90° (Q)", lambda: self.rotate_selected(-90))
        m_edit.addAction("Rotate Right 90° (E)", lambda: self.rotate_selected(+90))
        m_edit.addAction("Rotate… (R)", self.rotate_prompt)
        m_edit.addSeparator()
        m_edit.addAction("Align to Grid (G)", self.align_to_grid)

        m_tools = menubar.addMenu("&Tools")
        def add_tool(name, cb):
            act = QtGui.QAction(name, self); act.triggered.connect(cb); m_tools.addAction(act); return act
        self.act_draw_line    = add_tool("Draw Line",    lambda: self.draw.set_mode(draw_tools.DrawMode.LINE))
        self.act_draw_rect    = add_tool("Draw Rect",    lambda: self.draw.set_mode(draw_tools.DrawMode.RECT))
        self.act_draw_circle  = add_tool("Draw Circle",  lambda: self.draw.set_mode(draw_tools.DrawMode.CIRCLE))
        self.act_draw_poly    = add_tool("Draw Polyline",lambda: self.draw.set_mode(draw_tools.DrawMode.POLYLINE))
        m_tools.addSeparator()
        m_tools.addAction("Place Array…", self.array_tool.run)
        m_tools.addAction("Dimension (D)", self.start_dimension)

        m_view = menubar.addMenu("&View")
        self.act_view_grid = QtGui.QAction("Grid", self, checkable=True); self.act_view_grid.setChecked(True); self.act_view_grid.toggled.connect(self.toggle_grid); m_view.addAction(self.act_view_grid)
        self.act_view_snap = QtGui.QAction("Snap", self, checkable=True); self.act_view_snap.setChecked(self.scene.snap_enabled); self.act_view_snap.toggled.connect(self.toggle_snap); m_view.addAction(self.act_view_snap)
        self.act_view_cross = QtGui.QAction("Crosshair (C)", self, checkable=True); self.act_view_cross.setChecked(True); self.act_view_cross.toggled.connect(self.toggle_crosshair); m_view.addAction(self.act_view_cross)
        m_view.addSeparator()
        act_scale = QtGui.QAction("Set Pixels per Foot…", self); act_scale.triggered.connect(self.set_px_per_ft); m_view.addAction(act_scale)
        m_snap = m_view.addMenu("Snap step")
        self.grp_snap = QtGui.QActionGroup(self, exclusive=True)
        def add_snap(name, inches):
            a = QtGui.QAction(name, self, checkable=True)
            if (inches==0 and self.snap_step_in<=0) or (inches>0 and abs(self.snap_step_in-inches)<1e-6): a.setChecked(True)
            a.triggered.connect(lambda _=False, inc=inches: self.set_snap_inches(inc))
            self.grp_snap.addAction(a); m_snap.addAction(a)
        add_snap("Grid intersections (default)", 0.0)
        add_snap('6"', 6.0); add_snap('12"', 12.0); add_snap('24"', 24.0)

        m_help = menubar.addMenu("&Help")
        m_help.addAction("About AutoFire…", self.show_about)

        # toolbar (minimal)
        tb = QToolBar("Main"); tb.setIconSize(QSize(16,16)); self.addToolBar(tb)
        tb.addAction(self.act_view_grid); tb.addAction(self.act_view_snap); tb.addAction(self.act_view_cross)
        tb.addSeparator()
        tb.addAction("Array", self.array_tool.run); tb.addAction("Dimension", self.start_dimension)
        tb.addSeparator()
        act_fit = QtGui.QAction("Fit (F2)", self, triggered=self.fit_view_to_content); tb.addAction(act_fit)
        QtGui.QShortcut(QtGui.QKeySequence("F2"), self, activated=self.fit_view_to_content)
        QtGui.QShortcut(QtGui.QKeySequence("D"), self, activated=self.start_dimension)

        # Delete/Backspace to remove selection
        QtGui.QShortcut(QtGui.QKeySequence(Qt.Key_Delete), self, activated=self.delete_selected)
        QtGui.QShortcut(QtGui.QKeySequence(Qt.Key_Backspace), self, activated=self.delete_selected)

        # selection helpers
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+A"), self, activated=self.select_all)

        # duplicate / rotate shortcuts
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+D"), self, activated=self.dup_selected)
        QtGui.QShortcut(QtGui.QKeySequence("Q"), self, activated=lambda: self.rotate_selected(-90))
        QtGui.QShortcut(QtGui.QKeySequence("E"), self, activated=lambda: self.rotate_selected(+90))
        QtGui.QShortcut(QtGui.QKeySequence("R"), self, activated=self.rotate_prompt)
        QtGui.QShortcut(QtGui.QKeySequence("G"), self, activated=self.align_to_grid)

        # nudge with arrows (uses snap step or 6")
        QtGui.QShortcut(QtGui.QKeySequence(Qt.Key_Up), self, activated=lambda: self.nudge(0, -1, fast=False))
        QtGui.QShortcut(QtGui.QKeySequence(Qt.Key_Down), self, activated=lambda: self.nudge(0, +1, fast=False))
        QtGui.QShortcut(QtGui.QKeySequence(Qt.Key_Left), self, activated=lambda: self.nudge(-1, 0, fast=False))
        QtGui.QShortcut(QtGui.QKeySequence(Qt.Key_Right), self, activated=lambda: self.nudge(+1, 0, fast=False))
        QtGui.QShortcut(QtGui.QKeySequence("Shift+Up"), self, activated=lambda: self.nudge(0, -1, fast=True))
        QtGui.QShortcut(QtGui.QKeySequence("Shift+Down"), self, activated=lambda: self.nudge(0, +1, fast=True))
        QtGui.QShortcut(QtGui.QKeySequence("Shift+Left"), self, activated=lambda: self.nudge(-1, 0, fast=True))
        QtGui.QShortcut(QtGui.QKeySequence("Shift+Right"), self, activated=lambda: self.nudge(+1, 0, fast=True))

        # left palette
        left = QWidget(); ll = QVBoxLayout(left)
        ll.addWidget(QLabel("Device Palette"))
        self.search = QLineEdit(); self.search.setPlaceholderText("Search name / part number…")
        self.cmb_mfr = QComboBox(); self.cmb_type = QComboBox()
        ll_top = QHBoxLayout(); ll_top.addWidget(QLabel("Manufacturer:")); ll_top.addWidget(self.cmb_mfr)
        ll_typ = QHBoxLayout(); ll_typ.addWidget(QLabel("Type:")); ll_typ.addWidget(self.cmb_type)
        self.list = QListWidget()
        ll.addLayout(ll_top); ll.addLayout(ll_typ); ll.addWidget(self.search); ll.addWidget(self.list)
        self._populate_filters(); self._refresh_device_list()
        self.search.textChanged.connect(self._refresh_device_list)
        self.cmb_mfr.currentIndexChanged.connect(self._refresh_device_list)
        self.cmb_type.currentIndexChanged.connect(self._refresh_device_list)
        self.list.itemClicked.connect(self.choose_device)

        splitter = QtWidgets.QSplitter(); splitter.addWidget(left); splitter.addWidget(self.view); splitter.setStretchFactor(1,1)
        container = QWidget(); lay = QHBoxLayout(container); lay.addWidget(splitter); self.setCentralWidget(container)

        # right dock — grid/snap controls
        dock = QDockWidget("Layers / Controls", self); panel = QWidget(); form = QVBoxLayout(panel)
        self.chk_underlay = QCheckBox("Underlay"); self.chk_underlay.setChecked(True); self.chk_underlay.toggled.connect(lambda v: self.layer_underlay.setVisible(v)); form.addWidget(self.chk_underlay)
        self.chk_sketch = QCheckBox("Sketch"); self.chk_sketch.setChecked(True); self.chk_sketch.toggled.connect(lambda v: self.layer_sketch.setVisible(v)); form.addWidget(self.chk_sketch)
        self.chk_wires = QCheckBox("Wiring"); self.chk_wires.setChecked(True); self.chk_wires.toggled.connect(lambda v: self.layer_wires.setVisible(v)); form.addWidget(self.chk_wires)
        self.chk_devices = QCheckBox("Devices"); self.chk_devices.setChecked(True); self.chk_devices.toggled.connect(lambda v: self.layer_devices.setVisible(v)); form.addWidget(self.chk_devices)
        form.addWidget(QLabel("Grid Size"))
        self.spin_grid = QSpinBox(); self.spin_grid.setRange(2, 500); self.spin_grid.setValue(self.scene.grid_size); self.spin_grid.valueChanged.connect(self.change_grid_size); form.addWidget(self.spin_grid)
        panel.setLayout(form); dock.setWidget(panel); self.addDockWidget(Qt.RightDockWidgetArea, dock)

        # selection changed → update status count
        self.scene.selectionChanged.connect(self._on_selection_changed)

        self.history = []; self.history_index = -1
        self.push_history()
        self.statusBar().showMessage("Ready")

    # palette
    def _populate_filters(self):
        mfrs = catalog.list_manufacturers(self.devices_all)
        types = catalog.list_types(self.devices_all)
        self.cmb_mfr.clear(); self.cmb_mfr.addItems(mfrs)
        self.cmb_type.clear(); self.cmb_type.addItems(types)

    def _refresh_device_list(self):
        q = self.search.text().lower().strip()
        want_mfr = self.cmb_mfr.currentText()
        want_type = self.cmb_type.currentText()
        self.list.clear()
        for d in self.devices_all:
            if want_mfr and want_mfr != "(Any)" and d.get("manufacturer") != want_mfr: continue
            if want_type and want_type != "(Any)" and d.get("type") != want_type: continue
            txt = f"{d['name']} ({d['symbol']})"
            if q and q not in txt.lower() and q not in (d.get('part_number','').lower()): continue
            it = QListWidgetItem(txt); it.setData(Qt.UserRole, d); self.list.addItem(it)

    def choose_device(self, it: QListWidgetItem):
        self.view.set_current_device(it.data(Qt.UserRole))

    # toggles
    def toggle_grid(self, on: bool): self.scene.show_grid = bool(on); self.scene.update()
    def toggle_snap(self, on: bool): self.scene.snap_enabled = bool(on)
    def toggle_crosshair(self, on: bool): self.view.show_crosshair = bool(on)

    # scale/snap
    def set_px_per_ft(self):
        val, ok = QtWidgets.QInputDialog.getDouble(self, "Scale", "Pixels per foot", self.px_per_ft, 1.0, 1000.0, 2)
        if ok:
            self.px_per_ft = float(val)
            self.prefs["px_per_ft"] = self.px_per_ft
            save_prefs(self.prefs)
            self._apply_snap_step_from_inches(self.snap_step_in)

    def _apply_snap_step_from_inches(self, inches: float):
        if inches <= 0:
            self.scene.snap_step_px = 0.0
            self.snap_label = "grid"
        else:
            ft = inches / 12.0
            self.scene.snap_step_px = units.ft_to_px(ft, self.px_per_ft)
            self.snap_label = f'{int(inches)}"'
        self.prefs["snap_step_in"] = inches
        self.prefs["snap_label"] = self.snap_label
        save_prefs(self.prefs)

    def set_snap_inches(self, inches: float):
        self.snap_step_in = float(inches)
        self._apply_snap_step_from_inches(self.snap_step_in)

    # context menu
    def canvas_menu(self, global_pos):
        menu = QMenu(self)
        sel = [it for it in self.scene.selectedItems() if isinstance(it, DeviceItem)]
        if sel:
            d = sel[0]
            act_cov = menu.addAction("Coverage…")
            act_tog = menu.addAction("Toggle Coverage On/Off")
            act_lbl = menu.addAction("Edit Label…")
            act = menu.exec(global_pos)
            if act == act_cov:
                dlg = CoverageDialog(self, existing=d.coverage, px_per_ft=self.px_per_ft)
                if dlg.exec() == QtWidgets.QDialog.Accepted:
                    d.set_coverage(dlg.get_settings()); self.push_history()
            elif act == act_tog:
                if d.coverage.get("mode","none")=="none":
                    d.set_coverage({"mode":"manual","radius_ft":25.0,"px_per_ft":self.px_per_ft,"computed_radius_px":25.0*self.px_per_ft})
                else:
                    d.set_coverage({"mode":"none","computed_radius_px":0.0})
                self.push_history()
            elif act == act_lbl:
                txt, ok = QtWidgets.QInputDialog.getText(self, "Device Label", "Text:", text=d.name)
                if ok: d.set_label_text(txt)
        else:
            menu.addAction("Fit View (F2)", self.fit_view_to_content)
            menu.addSeparator()
            menu.addAction("Draw Line",    lambda: self.draw.set_mode(draw_tools.DrawMode.LINE))
            menu.addAction("Draw Rect",    lambda: self.draw.set_mode(draw_tools.DrawMode.RECT))
            menu.addAction("Draw Circle",  lambda: self.draw.set_mode(draw_tools.DrawMode.CIRCLE))
            menu.addAction("Draw Polyline",lambda: self.draw.set_mode(draw_tools.DrawMode.POLYLINE))
            menu.addSeparator()
            menu.addAction("Place Array…", self.array_tool.run)
            menu.addAction("Dimension", self.start_dimension)
            menu.exec(global_pos)

    # serialize
    def serialize_state(self):
        devs = []
        for it in self.layer_devices.childItems():
            if isinstance(it, DeviceItem): devs.append(it.to_json())
        return {"grid":int(self.scene.grid_size), "snap":bool(self.scene.snap_enabled),
                "px_per_ft": float(self.px_per_ft),
                "snap_step_in": float(self.snap_step_in),
                "devices":devs,"wires":[]}

    def load_state(self, data):
        for it in list(self.layer_devices.childItems()): it.scene().removeItem(it)
        for it in list(self.layer_wires.childItems()): it.scene().removeItem(it)
        self.scene.snap_enabled = bool(data.get("snap", True)); self.act_view_snap.setChecked(self.scene.snap_enabled)
        self.scene.grid_size = int(data.get("grid", DEFAULT_GRID_SIZE)); self.spin_grid.setValue(self.scene.grid_size)
        self.px_per_ft = float(data.get("px_per_ft", self.px_per_ft))
        self.snap_step_in = float(data.get("snap_step_in", self.snap_step_in))
        self._apply_snap_step_from_inches(self.snap_step_in)
        for d in data.get("devices", []):
            it = DeviceItem.from_json(d); it.setParentItem(self.layer_devices)

    # history
    def push_history(self):
        if self.history_index < len(self.history)-1: self.history = self.history[:self.history_index+1]
        self.history.append(self.serialize_state()); self.history_index += 1

    def undo(self):
        if self.history_index>0:
            self.history_index-=1; self.load_state(self.history[self.history_index]); self.statusBar().showMessage("Undo")

    def redo(self):
        if self.history_index < len(self.history)-1:
            self.history_index+=1; self.load_state(self.history[self.history_index]); self.statusBar().showMessage("Redo")

    def delete_selected(self):
        sel = self.scene.selectedItems()
        if not sel: return
        for it in sel:
            it.scene().removeItem(it)
        self.push_history()
        self.statusBar().showMessage(f"Deleted {len(sel)} item(s)")

    def select_all(self):
        for it in self.scene.items():
            it.setSelected(True)
        self._on_selection_changed()

    # edit ops
    def dup_selected(self):
        dx_px = units.ft_to_px(0.5, self.px_per_ft)  # 6 inches default offset
        n = transform.duplicate_selected(self.scene, self.layer_devices, dx_px, dx_px)
        if n:
            self.push_history()
            self.statusBar().showMessage(f"Duplicated {n} item(s)")

    def rotate_selected(self, angle_deg: float):
        n = transform.rotate_selected(self.scene, angle_deg)
        if n:
            self.push_history()
            self.statusBar().showMessage(f"Rotated {n} item(s) by {angle_deg:.1f}°")

    def rotate_prompt(self):
        val, ok = QtWidgets.QInputDialog.getDouble(self, "Rotate", "Degrees (+CW / −CCW):", 15.0, -360.0, 360.0, 1)
        if ok:
            self.rotate_selected(val)

    def nudge(self, sx: int, sy: int, fast: bool):
        # step = snap_step if set, else 6 inches; Shift doubles it
        if self.scene.snap_step_px and self.scene.snap_step_px > 0:
            step = float(self.scene.snap_step_px)
        else:
            step = float(units.ft_to_px(0.5, self.px_per_ft))
        if fast:
            step *= 2.0
        dx = sx * step
        dy = sy * step
        n = transform.nudge_selected(self.scene, dx, dy)
        if n:
            self.push_history()
            self.statusBar().showMessage(f"Moved {n} item(s)")

    def align_to_grid(self):
        n = transform.align_selected_to_grid(self.scene, self.px_per_ft, self.scene.snap_step_px, self.scene.grid_size)
        if n:
            self.push_history()
            self.statusBar().showMessage(f"Aligned {n} item(s) to grid")

    # underlay
    def _build_underlay_path(self, msp):
        path = QtGui.QPainterPath()
        for e in msp:
            t = e.dxftype()
            if t=="LINE":
                sx,sy,_=e.dxf.start; ex,ey,_=e.dxf.end
                path.moveTo(float(sx),float(sy)); path.lineTo(float(ex),float(ey))
            elif t=="CIRCLE":
                cx,cy,_=e.dxf.center; r=float(e.dxf.radius); rect=QtCore.QRectF(cx-r, cy-r, 2*r, 2*r); path.addEllipse(rect)
            elif t=="ARC":
                cx,cy,_=e.dxf.center; r=float(e.dxf.radius)
                start=float(e.dxf.start_angle); end=float(e.dxf.end_angle); rect=QtCore.QRectF(cx-r, cy-r, 2*r, 2*r)
                path.arcMoveTo(rect, start); path.arcTo(rect, start, end-start)
        return path

    def _apply_underlay_path(self, path):
        for it in list(self.layer_underlay.childItems()): it.scene().removeItem(it)
        pen=QtGui.QPen(QtGui.QColor("#808080")); pen.setCosmetic(True); pen.setWidthF(0)
        item=QGraphicsPathItem(path); item.setPen(pen); item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False); item.setParentItem(self.layer_underlay)

    def _load_underlay(self, path):
        try:
            import ezdxf
        except Exception as ex:
            QMessageBox.critical(self,"DXF Import Error","DXF support (ezdxf) not available.\n\nInstall: pip install ezdxf\n\n"+str(ex))
            return
        try:
            doc = ezdxf.readfile(path); msp = doc.modelspace(); p = self._build_underlay_path(msp); self._apply_underlay_path(p)
        except Exception as ex:
            QMessageBox.critical(self,"DXF Import Error", str(ex))

    def import_dxf_underlay(self):
        p,_ = QFileDialog.getOpenFileName(self,"Import DXF Underlay","","DXF Files (*.dxf)")
        if not p: return
        self._load_underlay(p)

    def export_png(self):
        p,_=QFileDialog.getSaveFileName(self,"Export PNG","","PNG Image (*.png)")
        if not p: return
        if not p.lower().endswith(".png"): p += ".png"
        rect = self.scene.itemsBoundingRect().adjusted(-50,-50,50,50)
        if rect.isNull(): rect = QtCore.QRectF(0,0,1200,900)
        img = QtGui.QImage(int(rect.width()), int(rect.height()), QtGui.QImage.Format_ARGB32)
        img.fill(QtGui.QColor(30,30,34))
        painter = QtGui.QPainter(img)
        painter.translate(-rect.topLeft())
        self.scene.render(painter, QtCore.QRectF(0,0,rect.width(),rect.height()), rect)
        painter.end()
        ok = img.save(p)
        if ok: self.statusBar().showMessage(f"Exported: {os.path.basename(p)}")
        else:  QMessageBox.critical(self, "Export PNG", "Failed to save image")

    def new_project(self):
        self.clear_underlay()
        for it in list(self.layer_devices.childItems()): it.scene().removeItem(it)
        for it in list(self.layer_wires.childItems()): it.scene().removeItem(it)
        self.push_history(); self.statusBar().showMessage("New project")

    def save_project_as(self):
        p,_=QFileDialog.getSaveFileName(self,"Save Project As","","AutoFire Bundle (*.autofire)")
        if not p: return
        if not p.lower().endswith(".autofire"): p += ".autofire"
        try:
            data=self.serialize_state()
            with zipfile.ZipFile(p,"w",compression=zipfile.ZIP_DEFLATED) as z:
                z.writestr("project.json", json.dumps(data, indent=2))
            self.statusBar().showMessage(f"Saved: {os.path.basename(p)}")
        except Exception as ex:
            QMessageBox.critical(self,"Save Project Error", str(ex))

    def open_project(self):
        p,_=QFileDialog.getOpenFileName(self,"Open Project","","AutoFire Bundle (*.autofire)")
        if not p: return
        try:
            with zipfile.ZipFile(p,"r") as z:
                data=json.loads(z.read("project.json").decode("utf-8"))
            self.load_state(data); self.push_history(); self.statusBar().showMessage(f"Opened: {os.path.basename(p)}")
        except Exception as ex:
            QMessageBox.critical(self,"Open Project Error", str(ex))

    def change_grid_size(self, v: int):
        self.scene.grid_size = int(v); self.scene.update()

    def fit_view_to_content(self):
        rect=self.scene.itemsBoundingRect().adjusted(-100,-100,100,100)
        if rect.isNull(): rect=QtCore.QRectF(0,0,2000,1500)
        self.view.fitInView(rect, Qt.KeepAspectRatio)

    def start_dimension(self):
        self.dim_tool.start()

    def clear_underlay(self):
        for it in list(self.layer_underlay.childItems()): it.scene().removeItem(it)

    def show_about(self):
        QtWidgets.QMessageBox.information(self,"About", f"Auto-Fire\nVersion {APP_VERSION}")

    # selection status
    def _on_selection_changed(self):
        self.selection_count = len(self.scene.selectedItems())
        # statusBar updated from CanvasView whenever mouse moves

def create_window():
    return MainWindow()

def main():
    app = QApplication([])
    win = create_window()
    win.show()
    app.exec()
"""


def write_file(rel, content):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        bak = path.with_suffix(path.suffix + f".bak-{STAMP}")
        bak.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"backup -> {bak}")
    path.write_text(content.lstrip("\n"), encoding="utf-8")
    print(f"wrote   -> {path}")


def main():
    print("== Auto-Fire CAD Step 1 (0.6.4) ==")
    for rel, content in FILES.items():
        write_file(rel, content)
    print("Done. Launch with:  py -3 -m app.boot")


if __name__ == "__main__":
    main()
