# apply_063_overlayB.py
# Auto-Fire v0.6.3 "overlayB"
# - Overlay limited to device kinds: strobe / speaker / smoke (no more on pull stations)
# - Quick coverage tweaks: [ / ] (strobe diameter ±5 ft), Alt+[ / Alt+] (speaker target dB ±1)
# - Grid lighter, with a View → Grid Style… dialog (opacity & width, persistent)
# - Minimal, safe: backs up touched files with .bak-YYYYMMDD_HHMMSS

from pathlib import Path
import time, shutil

STAMP = time.strftime("%Y%m%d_%H%M%S")
ROOT = Path(__file__).resolve().parent


def backup_write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        bak = path.with_suffix(path.suffix + f".bak-{STAMP}")
        shutil.copy2(path, bak)
        print(f"[backup] {bak}")
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"[write ] {path}")


SCENE_PY = r"""
from PySide6 import QtCore, QtGui, QtWidgets

DEFAULT_GRID_SIZE = 24  # pixels between minor lines

class GridScene(QtWidgets.QGraphicsScene):
    def __init__(self, grid_size=DEFAULT_GRID_SIZE, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_size = max(2, int(grid_size))
        self.show_grid = True
        self.snap_enabled = True
        self.snap_step_px = 0.0  # if >0, overrides grid intersections

        # Style (preferences can override via setters)
        self.grid_opacity = 0.35     # 0..1
        self.grid_width   = 0.0      # 0 = hairline; otherwise widthF in px
        self.major_every  = 5

        # Base colors (dark theme)
        self.col_minor_rgb = QtGui.QColor(120, 130, 145)  # we apply alpha every frame
        self.col_major_rgb = QtGui.QColor(160, 170, 185)
        self.col_axis_rgb  = QtGui.QColor(180, 190, 205)

    def set_grid_style(self, opacity: float = None, width: float = None, major_every: int = None):
        if opacity is not None: self.grid_opacity = max(0.05, min(1.0, float(opacity)))
        if width   is not None: self.grid_width   = max(0.0, float(width))
        if major_every is not None: self.major_every = max(2, int(major_every))
        self.update()

    # simple grid snap
    def snap(self, pt: QtCore.QPointF) -> QtCore.QPointF:
        if not self.snap_enabled:
            return pt
        if self.snap_step_px and self.snap_step_px > 0:
            s = self.snap_step_px
            x = round(pt.x()/s)*s
            y = round(pt.y()/s)*s
            return QtCore.QPointF(x, y)
        # snap to grid intersections
        g = self.grid_size
        x = round(pt.x()/g)*g
        y = round(pt.y()/g)*g
        return QtCore.QPointF(x, y)

    def _pen(self, base_rgb: QtGui.QColor):
        c = QtGui.QColor(base_rgb)
        c.setAlphaF(self.grid_opacity)
        pen = QtGui.QPen(c)
        pen.setCosmetic(True)
        if self.grid_width > 0.0:
            pen.setWidthF(self.grid_width)
        return pen

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        super().drawBackground(painter, rect)
        if not self.show_grid or self.grid_size <= 0:
            return

        g = self.grid_size
        left = int(rect.left()) - (int(rect.left()) % g)
        top  = int(rect.top())  - (int(rect.top())  % g)

        pen_minor = self._pen(self.col_minor_rgb)
        pen_major = self._pen(self.col_major_rgb)
        major_every = self.major_every

        painter.save()
        # verticals
        x = left
        idx = 0
        while x < rect.right():
            painter.setPen(pen_major if (idx % major_every == 0) else pen_minor)
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += g; idx += 1
        # horizontals
        y = top
        idy = 0
        while y < rect.bottom():
            painter.setPen(pen_major if (idy % major_every == 0) else pen_minor)
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += g; idy += 1

        # axes cross at (0,0)
        axis_pen = self._pen(self.col_axis_rgb)
        painter.setPen(axis_pen)
        painter.drawLine(0, int(rect.top()), 0, int(rect.bottom()))
        painter.drawLine(int(rect.left()), 0, int(rect.right()), 0)
        painter.restore()
"""

GRIDSTYLE_PY = r"""
from PySide6 import QtCore, QtGui, QtWidgets

class GridStyleDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, scene=None, prefs:dict=None):
        super().__init__(parent)
        self.setWindowTitle("Grid Style")
        self.scene = scene
        self.prefs = prefs if isinstance(prefs, dict) else {}

        v = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.s_opacity = QtWidgets.QDoubleSpinBox(); self.s_opacity.setRange(0.05,1.0); self.s_opacity.setSingleStep(0.05)
        self.s_width   = QtWidgets.QDoubleSpinBox(); self.s_width.setRange(0.0, 2.0);  self.s_width.setSingleStep(0.1)
        self.s_major   = QtWidgets.QSpinBox();       self.s_major.setRange(2,12)

        # load from prefs or scene defaults
        op = float(self.prefs.get("grid_opacity", getattr(scene,"grid_opacity",0.35)))
        wd = float(self.prefs.get("grid_width_px", getattr(scene,"grid_width",0.0)))
        mj = int(self.prefs.get("grid_major_every", getattr(scene,"major_every",5)))
        self.s_opacity.setValue(op); self.s_width.setValue(wd); self.s_major.setValue(mj)

        form.addRow("Opacity:", self.s_opacity)
        form.addRow("Line width (px):", self.s_width)
        form.addRow("Major line every N:", self.s_major)
        v.addLayout(form)

        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject)
        v.addWidget(bb)

    def apply(self):
        op = float(self.s_opacity.value())
        wd = float(self.s_width.value())
        mj = int(self.s_major.value())
        if self.scene:
            self.scene.set_grid_style(op, wd, mj)
        if self.prefs is not None:
            self.prefs["grid_opacity"] = op
            self.prefs["grid_width_px"] = wd
            self.prefs["grid_major_every"] = mj
        return op, wd, mj
"""

MAIN_PATCH = r'''
import os, json, zipfile
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QPointF, QSize
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QLineEdit, QLabel, QToolBar, QFileDialog,
    QGraphicsView, QGraphicsPathItem, QMenu, QDockWidget, QCheckBox, QSpinBox, QComboBox, QMessageBox
)

from app.scene import GridScene, DEFAULT_GRID_SIZE
from app.device import DeviceItem
from app import catalog
from app.tools.array import ArrayTool
from app.dialogs.coverage import CoverageDialog
from app.dialogs.gridstyle import GridStyleDialog

APP_VERSION = "0.6.3-overlayB"
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
    """Rough mapping: returns 'strobe' | 'speaker' | 'smoke' | 'other'."""
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
        self.ghost = None  # live preview device
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # crosshair overlay
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
        # remove ghost if no overlay for this kind
        if not self.current_proto or self.current_kind not in ("strobe","speaker","smoke"):
            if self.ghost:
                self.scene().removeItem(self.ghost); self.ghost = None
            return
        if not self.ghost:
            d = self.current_proto
            self.ghost = DeviceItem(0, 0, d["symbol"], d["name"], d.get("manufacturer",""), d.get("part_number",""))
            self.ghost.setOpacity(0.65)
            self.ghost.setParentItem(self.overlay_group)
        # update ghost coverage defaults by kind
        ppf = float(self.win.px_per_ft)
        if self.current_kind == "strobe":
            diam_ft = float(self.win.prefs.get("default_strobe_diameter_ft", 50.0))
            self.ghost.set_coverage({"mode":"strobe","mount":"ceiling",
                                     "computed_radius_ft": max(0.0, diam_ft/2.0),
                                     "px_per_ft": ppf})
        elif self.current_kind == "speaker":
            # show ~target dB 75 by default using L10 95
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
        super().keyPressEvent(e)

    def keyReleaseEvent(self, e: QtGui.QKeyEvent):
        if e.key()==Qt.Key_Shift: self.ortho=False; e.accept(); return
        super().keyReleaseEvent(e)

    def mouseMoveEvent(self, e: QtGui.QMouseEvent):
        sp = self.mapToScene(e.position().toPoint())
        sp = self.scene().snap(sp)
        self._update_crosshair(sp)
        if self.ghost:
            self.ghost.setPos(sp)
        super().mouseMoveEvent(e)

    def mousePressEvent(self, e: QtGui.QMouseEvent):
        win = self.win
        sp = self.scene().snap(self.mapToScene(e.position().toPoint()))
        if e.button()==Qt.LeftButton:
            if self.current_proto:
                d = self.current_proto
                it = DeviceItem(sp.x(), sp.y(), d["symbol"], d["name"], d.get("manufacturer",""), d.get("part_number",""))
                # copy ghost coverage only when kind supports overlay
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
        # sane defaults
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
        # apply grid style from prefs
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
        self.array_tool = ArrayTool(self, self.layer_devices)

        menubar = self.menuBar()
        m_file = menubar.addMenu("&File")
        m_file.addAction("New", self.new_project, QtGui.QKeySequence.New)
        m_file.addAction("Open…", self.open_project, QtGui.QKeySequence.Open)
        m_file.addAction("Save As…", self.save_project_as, QtGui.QKeySequence.SaveAs)
        m_file.addSeparator()
        m_file.addAction("Quit", self.close, QtGui.QKeySequence.Quit)

        m_tools = menubar.addMenu("&Tools")
        m_tools.addAction("Place Array…", self.array_tool.run)

        m_view = menubar.addMenu("&View")
        self.act_view_grid = QtGui.QAction("Grid", self, checkable=True); self.act_view_grid.setChecked(True); self.act_view_grid.toggled.connect(self.toggle_grid); m_view.addAction(self.act_view_grid)
        self.act_view_snap = QtGui.QAction("Snap", self, checkable=True); self.act_view_snap.setChecked(self.scene.snap_enabled); self.act_view_snap.toggled.connect(self.toggle_snap); m_view.addAction(self.act_view_snap)
        self.act_view_cross = QtGui.QAction("Crosshair (C)", self, checkable=True); self.act_view_cross.setChecked(True); self.act_view_cross.toggled.connect(self.toggle_crosshair); m_view.addAction(self.act_view_cross)
        m_view.addSeparator()
        act_scale = QtGui.QAction("Set Pixels per Foot…", self); act_scale.triggered.connect(self.set_px_per_ft); m_view.addAction(act_scale)
        act_gridstyle = QtGui.QAction("Grid Style…", self); act_gridstyle.triggered.connect(self.grid_style_dialog); m_view.addAction(act_gridstyle)

        # palette panel
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

        dock = QDockWidget("Layers / Controls", self); panel = QWidget(); form = QVBoxLayout(panel)
        self.chk_underlay = QCheckBox("Underlay"); self.chk_underlay.setChecked(True); self.chk_underlay.toggled.connect(lambda v: self.layer_underlay.setVisible(v)); form.addWidget(self.chk_underlay)
        self.chk_sketch = QCheckBox("Sketch"); self.chk_sketch.setChecked(True); self.chk_sketch.toggled.connect(lambda v: self.layer_sketch.setVisible(v)); form.addWidget(self.chk_sketch)
        self.chk_wires = QCheckBox("Wiring"); self.chk_wires.setChecked(True); self.chk_wires.toggled.connect(lambda v: self.layer_wires.setVisible(v)); form.addWidget(self.chk_wires)
        self.chk_devices = QCheckBox("Devices"); self.chk_devices.setChecked(True); self.chk_devices.toggled.connect(lambda v: self.layer_devices.setVisible(v)); form.addWidget(self.chk_devices)
        form.addWidget(QLabel("Grid Size"))
        self.spin_grid = QSpinBox(); self.spin_grid.setRange(2, 500); self.spin_grid.setValue(self.scene.grid_size); self.spin_grid.valueChanged.connect(self.change_grid_size); form.addWidget(self.spin_grid)
        panel.setLayout(form); dock.setWidget(panel); self.addDockWidget(Qt.RightDockWidgetArea, dock)

        tb = QToolBar("Main"); tb.setIconSize(QSize(16,16)); self.addToolBar(tb)
        tb.addAction(self.act_view_grid); tb.addAction(self.act_view_snap); tb.addAction(self.act_view_cross)

        # Quick coverage shortcuts
        QtGui.QShortcut(QtGui.QKeySequence("["), self, activated=lambda: self.nudge_coverage(strobe_delta= -5.0))
        QtGui.QShortcut(QtGui.QKeySequence("]"), self, activated=lambda: self.nudge_coverage(strobe_delta= +5.0))
        QtGui.QShortcut(QtGui.QKeySequence("Alt+["), self, activated=lambda: self.nudge_coverage(speaker_db_delta= -1.0))
        QtGui.QShortcut(QtGui.QKeySequence("Alt+]"), self, activated=lambda: self.nudge_coverage(speaker_db_delta= +1.0))

        self.history = []; self.history_index = -1
        self.push_history()

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
        d = it.data(Qt.UserRole)
        self.view.set_current_device(d)
        kind = infer_device_kind(d)
        self.statusBar().showMessage(f"Selected: {d['name']} [{kind}]")

    # view toggles
    def toggle_grid(self, on: bool): self.scene.show_grid = bool(on); self.scene.update()
    def toggle_snap(self, on: bool): self.scene.snap_enabled = bool(on)
    def toggle_crosshair(self, on: bool): self.view.show_crosshair = bool(on)

    def grid_style_dialog(self):
        dlg = GridStyleDialog(self, scene=self.scene, prefs=self.prefs)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            op, wd, mj = dlg.apply()
            save_prefs(self.prefs)
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

    # scene menu
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
                    # default = strobe with configured diameter
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

    # quick coverage nudges for selected device or ghost (strobe/speaker)
    def nudge_coverage(self, strobe_delta: float = 0.0, speaker_db_delta: float = 0.0):
        target = None
        # prefer selected device
        sel = [it for it in self.scene.selectedItems() if isinstance(it, DeviceItem)]
        if sel: target = sel[0]
        # else ghost
        if not target and self.view.ghost: target = self.view.ghost
        if not target: return

        cov = dict(target.coverage)
        mode = cov.get("mode","none")
        if strobe_delta and mode == "strobe":
            # change diameter
            diam = float(cov.get("params",{}).get("diameter_ft", 2*cov.get("computed_radius_ft", 25.0)))
            diam = max(5.0, diam + strobe_delta)
            cov.setdefault("params",{})["diameter_ft"] = diam
            cov["computed_radius_ft"] = diam/2.0
            target.set_coverage(cov)
            self.statusBar().showMessage(f"Strobe diameter: {diam:.1f} ft")
        if speaker_db_delta and mode == "speaker":
            p = cov.setdefault("params",{})
            tgt = float(p.get("target_db", 75.0)) + speaker_db_delta
            p["target_db"] = max(50.0, min(110.0, tgt))
            L10 = float(p.get("L10",95.0))
            cov["computed_radius_ft"] = 10.0 * (10.0 ** ((L10 - p["target_db"])/20.0))
            target.set_coverage(cov)
            self.statusBar().showMessage(f"Speaker target: {p['target_db']:.1f} dB")

    # serialize
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
        self.scene.grid_size = int(data.get("grid", DEFAULT_GRID_SIZE)); self.spin_grid.setValue(self.scene.grid_size)
        self.px_per_ft = float(data.get("px_per_ft", self.px_per_ft))
        self.snap_step_in = float(data.get("snap_step_in", self.snap_step_in))
        # grid style from file if present
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

    # underlay (placeholder clear)
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
'''

CHANGELOG_ADD = r"""
## v0.6.3 – overlayB ({date})
- **Overlays** now show **only** for strobe / speaker / smoke device types (no coverage on pull stations).
- **Quick coverage adjust**:
  - **[ / ]** → strobe coverage **diameter −/+ 5 ft**
  - **Alt+[ / Alt+]** → speaker **target dB −/+ 1 dB**
- **Grid** is lighter by default; added **View → Grid Style…** for opacity, line width, and major-line interval (saved in prefs).
- Persisted grid style in project saves; status bar messages clarify current adjustments.
"""


def main():
    # write files
    backup_write(ROOT / "app" / "scene.py", SCENE_PY)
    backup_write(ROOT / "app" / "dialogs" / "gridstyle.py", GRIDSTYLE_PY)
    backup_write(ROOT / "app" / "main.py", MAIN_PATCH)

    # changelog append
    cl = ROOT / "CHANGELOG.md"
    existing = ""
    if cl.exists():
        existing = cl.read_text(encoding="utf-8")
    entry = CHANGELOG_ADD.replace("{date}", time.strftime("%Y-%m-%d"))
    cl.write_text(existing.rstrip() + "\n\n" + entry, encoding="utf-8")
    print(f"[append] {cl} v0.6.3 entry added")

    print("\nDone. Launch with:\n  py -3 -m app.boot\n")


if __name__ == "__main__":
    main()
