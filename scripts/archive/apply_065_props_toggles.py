# apply_065_props_toggles.py
# Restores a right-side "Layers & Properties" dock with layer toggles, grid size,
# and basic device properties editor. Keeps prior Tools menu + grid opacity slider.
import shutil
import time
from pathlib import Path

STAMP = time.strftime("%Y%m%d_%H%M%S")
ROOT = Path(__file__).resolve().parent
TGT = ROOT / "app" / "main.py"

NEW_MAIN = r"""
import os, json, zipfile
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QPointF, QSize
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QLineEdit, QLabel, QToolBar, QFileDialog,
    QGraphicsView, QGraphicsPathItem, QMenu, QDockWidget, QCheckBox, QSpinBox,
    QComboBox, QMessageBox, QDoubleSpinBox, QPushButton
)

from app.scene import GridScene, DEFAULT_GRID_SIZE
from app.device import DeviceItem
from app import catalog
from app.tools import draw as draw_tools
from app.tools.dimension import DimensionTool
from app.dialogs.coverage import CoverageDialog
from app.dialogs.gridstyle import GridStyleDialog

APP_VERSION = "0.6.5-layers-props"
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

def infer_device_kind(d: dict) -> str:
    t = (d.get("type","") or "").lower()
    n = (d.get("name","") or "").lower()
    s = (d.get("symbol","") or "").lower()
    text = " ".join([t,n,s])
    if any(k in text for k in ["strobe","av","nac-strobe","cd","candela"]):
        return "strobe"
    if any(k in text for k in ["speaker","spkr","voice"]):
        return "speaker"
    if any(k in text for k in ["smoke","sm","detector","heat"]):
        return "smoke"
    return "other"

class CanvasView(QGraphicsView):
    def __init__(self, scene, devices_group, wires_group, sketch_group, overlay_group, window_ref):
        super().__init__(scene)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setMouseTracking(True)
        self.devices_group = devices_group
        self.wires_group = wires_group
        self.sketch_group = sketch_group
        self.overlay_group = overlay_group
        self.ortho = False
        self.win = window_ref
        self.current_proto = None
        self.current_kind  = "other"
        self.ghost = None
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # crosshair
        self.cross_v = QtWidgets.QGraphicsLineItem(); self.cross_h = QtWidgets.QGraphicsLineItem()
        pen = QtGui.QPen(QtGui.QColor(150,150,160,150)); pen.setCosmetic(True); pen.setStyle(Qt.DashLine)
        self.cross_v.setPen(pen); self.cross_h.setPen(pen)
        self.cross_v.setParentItem(self.overlay_group); self.cross_h.setParentItem(self.overlay_group)
        self.show_crosshair = True

    def set_current_device(self, proto: dict):
        self.current_proto = proto
        self.current_kind  = infer_device_kind(proto)
        self._ensure_ghost()

    def _ensure_ghost(self):
        if not self.current_proto or self.current_kind not in ("strobe","speaker","smoke"):
            if self.ghost:
                self.scene().removeItem(self.ghost); self.ghost = None
            return
        if not self.ghost:
            d = self.current_proto
            self.ghost = DeviceItem(0, 0, d["symbol"], d["name"], d.get("manufacturer",""), d.get("part_number",""))
            self.ghost.setOpacity(0.65)
            self.ghost.setParentItem(self.overlay_group)
        # defaults
        ppf = float(self.win.px_per_ft)
        if self.current_kind == "strobe":
            diam_ft = float(self.win.prefs.get("default_strobe_diameter_ft", 50.0))
            self.ghost.set_coverage({"mode":"strobe","mount":"ceiling",
                                     "computed_radius_ft": max(0.0, diam_ft/2.0),
                                     "px_per_ft": ppf})
        elif self.current_kind == "speaker":
            # crude 20log drop preview
            self.ghost.set_coverage({"mode":"speaker","mount":"ceiling",
                                     "params":{"L10":95.0,"target_db":75.0},
                                     "computed_radius_ft": 10.0 * (10.0 ** ((95.0 - 75.0)/20.0)),
                                     "px_per_ft": ppf})
        elif self.current_kind == "smoke":
            spacing_ft = float(self.win.prefs.get("default_smoke_spacing_ft", 30.0))
            self.ghost.set_coverage({"mode":"smoke","mount":"ceiling",
                                     "params":{"spacing_ft":spacing_ft},
                                     "computed_radius_ft": spacing_ft/2.0,
                                     "px_per_ft": ppf})

    def _update_crosshair(self, sp: QPointF):
        if not self.show_crosshair: return
        rect = self.scene().sceneRect()
        self.cross_v.setLine(sp.x(), rect.top(), sp.x(), rect.bottom())
        self.cross_h.setLine(rect.left(), sp.y(), rect.right(), sp.y())
        dx_ft = sp.x()/self.win.px_per_ft
        dy_ft = sp.y()/self.win.px_per_ft
        self.win.statusBar().showMessage(f"x={dx_ft:.2f} ft   y={dy_ft:.2f} ft   scale={self.win.px_per_ft:.2f} px/ft  snap={self.win.snap_label}")

    def wheelEvent(self, e: QtGui.QWheelEvent):
        s = 1.15 if e.angleDelta().y() > 0 else 1/1.15
        self.scale(s, s)

    def keyPressEvent(self, e: QtGui.QKeyEvent):
        if e.key()==Qt.Key_Shift: self.ortho=True; e.accept(); return
        if e.key()==Qt.Key_C: self.show_crosshair = not self.show_crosshair; e.accept(); return
        if e.key()==Qt.Key_Escape and getattr(self.win, "draw", None):
            try:
                if self.win.draw.mode != 0:
                    self.win.draw.finish()
                    e.accept(); return
            except Exception:
                pass
        super().keyPressEvent(e)

    def keyReleaseEvent(self, e: QtGui.QKeyEvent):
        if e.key()==Qt.Key_Shift: self.ortho=False; e.accept(); return
        super().keyReleaseEvent(e)

    def mouseMoveEvent(self, e: QtGui.QMouseEvent):
        sp = self.mapToScene(e.position().toPoint())
        sp = self.scene().snap(sp)
        self._update_crosshair(sp)
        if getattr(self.win, "draw", None):
            try: self.win.draw.on_mouse_move(sp, shift_ortho=self.ortho)
            except Exception: pass
        if getattr(self.win, "dim_tool", None):
            try: self.win.dim_tool.on_mouse_move(sp)
            except Exception: pass
        if self.ghost:
            self.ghost.setPos(sp)
        super().mouseMoveEvent(e)

    def mousePressEvent(self, e: QtGui.QMouseEvent):
        win = self.win
        sp = self.scene().snap(self.mapToScene(e.position().toPoint()))
        if e.button()==Qt.LeftButton:
            if getattr(win, "draw", None) and getattr(win.draw, "mode", 0) != 0:
                try:
                    if win.draw.on_click(sp, shift_ortho=self.ortho):
                        win.push_history(); e.accept(); return
                except Exception:
                    pass
            if getattr(win, "dim_tool", None) and getattr(win.dim_tool, "active", False):
                try:
                    if win.dim_tool.on_click(sp):
                        e.accept(); return
                except Exception:
                    pass
            if self.current_proto:
                d = self.current_proto
                it = DeviceItem(sp.x(), sp.y(), d["symbol"], d["name"], d.get("manufacturer",""), d.get("part_number",""))
                if self.ghost and self.current_kind in ("strobe","speaker","smoke"):
                    it.set_coverage(self.ghost.coverage)
                it.setParentItem(self.devices_group)
                win.push_history(); e.accept(); return
        elif e.button()==Qt.RightButton:
            win.canvas_menu(e.globalPosition().toPoint()); e.accept(); return
        super().mousePressEvent(e)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1400, 900)
        self.prefs = load_prefs()
        self.px_per_ft = float(self.prefs.get("px_per_ft", 12.0))
        self.snap_label = self.prefs.get("snap_label", "grid")
        self.snap_step_in = float(self.prefs.get("snap_step_in", 0.0))
        self.prefs.setdefault("default_strobe_diameter_ft", 50.0)
        self.prefs.setdefault("default_smoke_spacing_ft", 30.0)
        self.prefs.setdefault("grid_opacity", 0.25)
        self.prefs.setdefault("grid_width_px", 0.0)
        self.prefs.setdefault("grid_major_every", 5)
        save_prefs(self.prefs)

        self.devices_all = catalog.load_catalog()

        self.scene = GridScene(int(self.prefs.get("grid", DEFAULT_GRID_SIZE)), 0,0,15000,10000)
        self.scene.snap_enabled = bool(self.prefs.get("snap", True))
        self.scene.set_grid_style(float(self.prefs.get("grid_opacity",0.25)),
                                  float(self.prefs.get("grid_width_px",0.0)),
                                  int(self.prefs.get("grid_major_every",5)))
        self._apply_snap_step_from_inches(self.snap_step_in)

        self.layer_underlay = QtWidgets.QGraphicsItemGroup(); self.layer_underlay.setZValue(-50); self.scene.addItem(self.layer_underlay)
        self.layer_sketch   = QtWidgets.QGraphicsItemGroup(); self.layer_sketch.setZValue(40);   self.scene.addItem(self.layer_sketch)
        self.layer_wires    = QtWidgets.QGraphicsItemGroup(); self.layer_wires.setZValue(60);    self.scene.addItem(self.layer_wires)
        self.layer_devices  = QtWidgets.QGraphicsItemGroup(); self.layer_devices.setZValue(100);  self.scene.addItem(self.layer_devices)
        self.layer_overlay  = QtWidgets.QGraphicsItemGroup(); self.layer_overlay.setZValue(200);  self.scene.addItem(self.layer_overlay)

        self.view = CanvasView(self.scene, self.layer_devices, self.layer_wires, self.layer_sketch, self.layer_overlay, self)

        # CAD tools
        self.draw = draw_tools.DrawController(self, self.layer_sketch)
        self.dim_tool = DimensionTool(self, self.layer_overlay)

        # Menus
        menubar = self.menuBar()
        m_file = menubar.addMenu("&File")
        m_file.addAction("New", self.new_project, QtGui.QKeySequence.New)
        m_file.addAction("Open…", self.open_project, QtGui.QKeySequence.Open)
        m_file.addAction("Save As…", self.save_project_as, QtGui.QKeySequence.SaveAs)
        m_file.addSeparator()
        m_file.addAction("Quit", self.close, QtGui.QKeySequence.Quit)

        m_tools = menubar.addMenu("&Tools")
        def add_tool(name, cb):
            act = QtGui.QAction(name, self); act.triggered.connect(cb); m_tools.addAction(act); return act
        self.act_draw_line    = add_tool("Draw Line",    lambda: self.draw.set_mode(draw_tools.DrawMode.LINE))
        self.act_draw_rect    = add_tool("Draw Rect",    lambda: self.draw.set_mode(draw_tools.DrawMode.RECT))
        self.act_draw_circle  = add_tool("Draw Circle",  lambda: self.draw.set_mode(draw_tools.DrawMode.CIRCLE))
        self.act_draw_poly    = add_tool("Draw Polyline",lambda: self.draw.set_mode(draw_tools.DrawMode.POLYLINE))
        m_tools.addSeparator()
        m_tools.addAction("Dimension (D)", self.start_dimension)

        m_view = menubar.addMenu("&View")
        self.act_view_grid = QtGui.QAction("Grid", self, checkable=True); self.act_view_grid.setChecked(True); self.act_view_grid.toggled.connect(self.toggle_grid); m_view.addAction(self.act_view_grid)
        self.act_view_snap = QtGui.QAction("Snap", self, checkable=True); self.act_view_snap.setChecked(self.scene.snap_enabled); self.act_view_snap.toggled.connect(self.toggle_snap); m_view.addAction(self.act_view_snap)
        self.act_view_cross = QtGui.QAction("Crosshair (C)", self, checkable=True); self.act_view_cross.setChecked(True); self.act_view_cross.toggled.connect(self.toggle_crosshair); m_view.addAction(self.act_view_cross)
        m_view.addSeparator()
        act_scale = QtGui.QAction("Set Pixels per Foot…", self); act_scale.triggered.connect(self.set_px_per_ft); m_view.addAction(act_scale)
        act_gridstyle = QtGui.QAction("Grid Style…", self); act_gridstyle.triggered.connect(self.grid_style_dialog); m_view.addAction(act_gridstyle)

        # Toolbar minimal
        tb = QToolBar("Main"); tb.setIconSize(QSize(16,16)); self.addToolBar(tb)
        tb.addAction(self.act_view_grid); tb.addAction(self.act_view_snap); tb.addAction(self.act_view_cross)

        # Status bar Grid opacity slider
        sb = self.statusBar()
        wrap = QWidget(); lay = QHBoxLayout(wrap); lay.setContentsMargins(6,0,6,0); lay.setSpacing(6)
        lay.addWidget(QLabel("Grid"))
        self.slider_grid = QtWidgets.QSlider(Qt.Horizontal); self.slider_grid.setMinimum(10); self.slider_grid.setMaximum(100)
        self.slider_grid.setFixedWidth(120)
        cur_op = float(self.prefs.get("grid_opacity", 0.25))
        self.slider_grid.setValue(int(max(10, min(100, round(cur_op*100)))))
        self.lbl_gridp = QLabel(f"{int(self.slider_grid.value())}%")
        lay.addWidget(self.slider_grid); lay.addWidget(self.lbl_gridp)
        sb.addPermanentWidget(wrap)
        def _apply_grid_op(val:int):
            op = max(0.10, min(1.00, val/100.0))
            self.scene.set_grid_style(opacity=op)
            self.prefs["grid_opacity"] = op
            save_prefs(self.prefs)
            self.lbl_gridp.setText(f"{int(val)}%")
        self.slider_grid.valueChanged.connect(_apply_grid_op)

        # Left panel (device palette)
        self._build_left_panel()

        # Right dock: Layers & Properties
        self._build_layers_and_props_dock()

        # Shortcuts
        QtGui.QShortcut(QtGui.QKeySequence("D"), self, activated=self.start_dimension)
        QtGui.QShortcut(QtGui.QKeySequence("Esc"), self, activated=lambda: getattr(self.draw,"finish",lambda:None)())

        # Selection change → update Properties
        self.scene.selectionChanged.connect(self._on_selection_changed)

        self.history = []; self.history_index = -1
        self.push_history()

    # ---------- UI building ----------
    def _build_left_panel(self):
        left = QWidget(); ll = QVBoxLayout(left)
        ll.addWidget(QLabel("Device Palette"))
        self.search = QLineEdit(); self.search.setPlaceholderText("Search name / part number…")
        self.cmb_mfr = QComboBox(); self.cmb_type = QComboBox()
        ll_top = QHBoxLayout(); ll_top.addWidget(QLabel("Manufacturer:")); ll_top.addWidget(self.cmb_mfr)
        ll_typ = QHBoxLayout(); ll_typ.addWidget(QLabel("Type:")); ll_typ.addWidget(self.cmb_type)
        self.list = QListWidget()
        ll.addLayout(ll_top); ll.addLayout(ll_typ); ll.addWidget(self.search); ll.addWidget(self.list)

        self._populate_filters()

        splitter = QtWidgets.QSplitter(); splitter.addWidget(left); splitter.addWidget(self.view); splitter.setStretchFactor(1,1)
        container = QWidget(); lay = QHBoxLayout(container); lay.addWidget(splitter); self.setCentralWidget(container)

        self.search.textChanged.connect(self._refresh_device_list)
        self.cmb_mfr.currentIndexChanged.connect(self._refresh_device_list)
        self.cmb_type.currentIndexChanged.connect(self._refresh_device_list)
        self.list.itemClicked.connect(self.choose_device)
        self._refresh_device_list()

    def _build_layers_and_props_dock(self):
        dock = QDockWidget("Layers & Properties", self)
        panel = QWidget(); form = QVBoxLayout(panel); form.setContentsMargins(8,8,8,8); form.setSpacing(6)

        # layer toggles
        form.addWidget(QLabel("Layers"))
        self.chk_underlay = QCheckBox("Underlay"); self.chk_underlay.setChecked(True); self.chk_underlay.toggled.connect(lambda v: self.layer_underlay.setVisible(v)); form.addWidget(self.chk_underlay)
        self.chk_sketch   = QCheckBox("Sketch"); self.chk_sketch.setChecked(True);   self.chk_sketch.toggled.connect(lambda v: self.layer_sketch.setVisible(v));     form.addWidget(self.chk_sketch)
        self.chk_wires    = QCheckBox("Wiring"); self.chk_wires.setChecked(True);    self.chk_wires.toggled.connect(lambda v: self.layer_wires.setVisible(v));       form.addWidget(self.chk_wires)
        self.chk_devices  = QCheckBox("Devices"); self.chk_devices.setChecked(True); self.chk_devices.toggled.connect(lambda v: self.layer_devices.setVisible(v));   form.addWidget(self.chk_devices)

        # grid size
        form.addSpacing(6); form.addWidget(QLabel("Grid Size"))
        self.spin_grid = QSpinBox(); self.spin_grid.setRange(2, 500); self.spin_grid.setValue(self.scene.grid_size)
        self.spin_grid.valueChanged.connect(self.change_grid_size)
        form.addWidget(self.spin_grid)

        # properties
        form.addSpacing(10); lblp = QLabel("Device Properties"); lblp.setStyleSheet("font-weight:600;"); form.addWidget(lblp)

        grid = QtWidgets.QGridLayout(); grid.setHorizontalSpacing(8); grid.setVerticalSpacing(4)
        r = 0
        grid.addWidget(QLabel("Label"), r, 0); self.prop_label = QLineEdit(); grid.addWidget(self.prop_label, r, 1); r+=1
        grid.addWidget(QLabel("Offset X (ft)"), r, 0); self.prop_offx = QDoubleSpinBox(); self.prop_offx.setRange(-500,500); self.prop_offx.setDecimals(2); grid.addWidget(self.prop_offx, r, 1); r+=1
        grid.addWidget(QLabel("Offset Y (ft)"), r, 0); self.prop_offy = QDoubleSpinBox(); self.prop_offy.setRange(-500,500); self.prop_offy.setDecimals(2); grid.addWidget(self.prop_offy, r, 1); r+=1
        grid.addWidget(QLabel("Mount"), r, 0); self.prop_mount = QComboBox(); self.prop_mount.addItems(["ceiling","wall"]); grid.addWidget(self.prop_mount, r, 1); r+=1
        grid.addWidget(QLabel("Coverage Mode"), r, 0); self.prop_mode = QComboBox(); self.prop_mode.addItems(["none","strobe","speaker","smoke"]); grid.addWidget(self.prop_mode, r, 1); r+=1
        grid.addWidget(QLabel("Size (ft)"), r, 0); self.prop_size = QDoubleSpinBox(); self.prop_size.setRange(0,1000); self.prop_size.setDecimals(2); self.prop_size.setSingleStep(1.0); grid.addWidget(self.prop_size, r, 1); r+=1

        form.addLayout(grid)
        self.btn_apply_props = QPushButton("Apply"); form.addWidget(self.btn_apply_props)

        # disable until selection
        self._enable_props(False)

        self.btn_apply_props.clicked.connect(self._apply_props_clicked)
        self.prop_label.editingFinished.connect(self._apply_label_offset_live)
        self.prop_offx.valueChanged.connect(self._apply_label_offset_live)
        self.prop_offy.valueChanged.connect(self._apply_label_offset_live)

        panel.setLayout(form); dock.setWidget(panel); self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def _enable_props(self, on: bool):
        for w in (self.prop_label, self.prop_offx, self.prop_offy, self.prop_mount, self.prop_mode, self.prop_size, self.btn_apply_props):
            w.setEnabled(on)

    # ---------- palette ----------
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
        d = it.data(Qt.UserRole)
        self.view.set_current_device(d)
        kind = infer_device_kind(d)
        self.statusBar().showMessage(f"Selected: {d['name']} [{kind}]")

    # ---------- view toggles ----------
    def toggle_grid(self, on: bool): self.scene.show_grid = bool(on); self.scene.update()
    def toggle_snap(self, on: bool): self.scene.snap_enabled = bool(on)
    def toggle_crosshair(self, on: bool): self.view.show_crosshair = bool(on)

    def grid_style_dialog(self):
        dlg = GridStyleDialog(self, scene=self.scene, prefs=self.prefs)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            op, wd, mj = dlg.apply()
            save_prefs(self.prefs)
            self.slider_grid.setValue(int(round(op*100)))
            self.statusBar().showMessage(f"Grid updated (opacity={op:.2f}, width={wd:.1f}, major_every={mj})")

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
            self.scene.snap_step_px = ft * self.px_per_ft
            self.snap_label = f'{int(inches)}"'
        self.prefs["snap_step_in"] = inches
        self.prefs["snap_label"] = self.snap_label
        save_prefs(self.prefs)

    def set_snap_inches(self, inches: float):
        self._apply_snap_step_from_inches(inches)

    # ---------- scene menu ----------
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
                dlg = CoverageDialog(self, existing=d.coverage)
                if dlg.exec() == QtWidgets.QDialog.Accepted:
                    d.set_coverage(dlg.get_settings(self.px_per_ft)); self.push_history()
            elif act == act_tog:
                if d.coverage.get("mode","none")=="none":
                    diam_ft = float(self.prefs.get("default_strobe_diameter_ft", 50.0))
                    d.set_coverage({"mode":"strobe","mount":"ceiling",
                                    "computed_radius_ft": max(0.0, diam_ft/2.0),
                                    "px_per_ft": self.px_per_ft})
                else:
                    d.set_coverage({"mode":"none","computed_radius_ft":0.0,"px_per_ft":self.px_per_ft})
                self.push_history()
            elif act == act_lbl:
                txt, ok = QtWidgets.QInputDialog.getText(self, "Device Label", "Text:", text=d.name)
                if ok: d.set_label_text(txt)
        else:
            menu.addAction("Clear Underlay", self.clear_underlay)
            menu.exec(global_pos)

    # ---------- history / serialize ----------
    def serialize_state(self):
        devs = []
        for it in self.layer_devices.childItems():
            if isinstance(it, DeviceItem): devs.append(it.to_json())
        return {"grid":int(self.scene.grid_size), "snap":bool(self.scene.snap_enabled),
                "px_per_ft": float(self.px_per_ft),
                "snap_step_in": float(self.snap_step_in),
                "grid_opacity": float(self.prefs.get("grid_opacity",0.25)),
                "grid_width_px": float(self.prefs.get("grid_width_px",0.0)),
                "grid_major_every": int(self.prefs.get("grid_major_every",5)),
                "devices":devs,"wires":[]}

    def load_state(self, data):
        for it in list(self.layer_devices.childItems()): it.scene().removeItem(it)
        for it in list(self.layer_wires.childItems()): it.scene().removeItem(it)
        self.scene.snap_enabled = bool(data.get("snap", True)); self.act_view_snap.setChecked(self.scene.snap_enabled)
        self.scene.grid_size = int(data.get("grid", DEFAULT_GRID_SIZE));
        if hasattr(self, "spin_grid"): self.spin_grid.setValue(self.scene.grid_size)
        self.px_per_ft = float(data.get("px_per_ft", self.px_per_ft))
        self.snap_step_in = float(data.get("snap_step_in", self.snap_step_in))
        self.prefs["grid_opacity"] = float(data.get("grid_opacity", self.prefs.get("grid_opacity",0.25)))
        self.prefs["grid_width_px"] = float(data.get("grid_width_px", self.prefs.get("grid_width_px",0.0)))
        self.prefs["grid_major_every"] = int(data.get("grid_major_every", self.prefs.get("grid_major_every",5)))
        self.scene.set_grid_style(self.prefs["grid_opacity"], self.prefs["grid_width_px"], self.prefs["grid_major_every"])
        self._apply_snap_step_from_inches(self.snap_step_in)
        for d in data.get("devices", []):
            it = DeviceItem.from_json(d); it.setParentItem(self.layer_devices)

    def push_history(self):
        if self.history_index < len(self.history)-1: self.history = self.history[:self.history_index+1]
        self.history.append(self.serialize_state()); self.history_index += 1

    def undo(self):
        if self.history_index>0:
            self.history_index-=1; self.load_state(self.history[self.history_index]); self.statusBar().showMessage("Undo")

    def redo(self):
        if self.history_index < len(self.history)-1:
            self.history_index+=1; self.load_state(self.history[self.history_index]); self.statusBar().showMessage("Redo")

    # ---------- right-dock props logic ----------
    def _get_selected_device(self):
        for it in self.scene.selectedItems():
            if isinstance(it, DeviceItem):
                return it
        return None

    def _on_selection_changed(self):
        d = self._get_selected_device()
        if not d:
            self._enable_props(False);
            return
        self._enable_props(True)
        # label + offset in ft
        self.prop_label.setText(d._label.text())
        offx = d.label_offset.x()/self.px_per_ft
        offy = d.label_offset.y()/self.px_per_ft
        self.prop_offx.blockSignals(True); self.prop_offy.blockSignals(True)
        self.prop_offx.setValue(offx); self.prop_offy.setValue(offy)
        self.prop_offx.blockSignals(False); self.prop_offy.blockSignals(False)
        # coverage
        cov = d.coverage or {}
        self.prop_mount.setCurrentText(cov.get("mount","ceiling"))
        mode = cov.get("mode","none")
        if mode not in ("none","strobe","speaker","smoke"): mode="none"
        self.prop_mode.setCurrentText(mode)
        # size proxy (ft): strobe uses diameter/2 -> radius; smoke uses spacing/2; speaker we just show computed radius if present
        size_ft = float(cov.get("computed_radius_ft",0.0))*2.0 if mode=="strobe" else (
                  float(cov.get("params",{}).get("spacing_ft",0.0)) if mode=="smoke" else
                  float(cov.get("computed_radius_ft",0.0)))
        self.prop_size.setValue(max(0.0, size_ft))

    def _apply_label_offset_live(self):
        d = self._get_selected_device()
        if not d: return
        d.set_label_text(self.prop_label.text())
        dx_ft = float(self.prop_offx.value()); dy_ft = float(self.prop_offy.value())
        d.set_label_offset(dx_ft*self.px_per_ft, dy_ft*self.px_per_ft)
        self.scene.update()

    def _apply_props_clicked(self):
        d = self._get_selected_device()
        if not d: return
        # label + offset already handled live
        mode = self.prop_mode.currentText()
        mount = self.prop_mount.currentText()
        sz = float(self.prop_size.value())
        cov = {"mode":mode, "mount":mount, "px_per_ft": self.px_per_ft}
        if mode == "none":
            cov["computed_radius_ft"] = 0.0
        elif mode == "strobe":
            # interpret "size ft" as DIAMETER in ft for strobe (easy visual)
            diam_ft = max(0.0, sz)
            cov["computed_radius_ft"] = diam_ft/2.0
        elif mode == "smoke":
            spacing_ft = max(0.0, sz)
            cov["params"] = {"spacing_ft": spacing_ft}
            cov["computed_radius_ft"] = spacing_ft/2.0
        elif mode == "speaker":
            # interpret "size ft" as desired radius directly for now (quick placeholder)
            cov["computed_radius_ft"] = max(0.0, sz)
        d.set_coverage(cov)
        self.push_history()
        self.scene.update()

    # ---------- underlay / file ops ----------
    def clear_underlay(self):
        for it in list(self.layer_underlay.childItems()): it.scene().removeItem(it)

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
        self.scene.grid_size = max(2, int(v)); self.scene.update()

    def start_dimension(self):
        try:
            self.dim_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Dimension Tool Error", str(ex))

    def fit_view_to_content(self):
        rect=self.scene.itemsBoundingRect().adjusted(-100,-100,100,100)
        if rect.isNull(): rect=QtCore.QRectF(0,0,1000,800)
        self.view.fitInView(rect, Qt.KeepAspectRatio)

# factory for boot.py
def create_window():
    return MainWindow()

def main():
    app = QApplication([])
    win = create_window()
    win.show()
    app.exec()

if __name__ == "__main__":
    main()
"""


def main():
    if TGT.exists():
        bak = TGT.with_suffix(TGT.suffix + f".bak-{STAMP}")
        shutil.copy2(TGT, bak)
        import logging

        from app.logging_config import setup_logging

        setup_logging()
        logging.getLogger(__name__).info("[backup] %s", bak)
    TGT.parent.mkdir(parents=True, exist_ok=True)
    TGT.write_text(NEW_MAIN.strip() + "\n", encoding="utf-8")
    logging.getLogger(__name__).info(
        "[write ] %s\n\nDone. Launch with:\n  py -3 -m app.boot",
        TGT,
    )


if __name__ == "__main__":
    main()
