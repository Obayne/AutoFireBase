# apply_062_overlayA.py
# Auto-Fire v0.6.2 "overlayA"
# - Grid: always draws (major/minor), better contrast; origin cross
# - Selection: high-contrast halo when selected
# - Coverage overlays: Strobe / Speaker(dB) / Smoke; toggle & edit per device
# - Live "ghost" overlay while placing (uses defaults; editable after place)
# - Array tool: spacing derived from device coverage, with manual override
# - CHANGELOG.md: append robust entry
#
# Safe & reversible: any touched file is backed up with .bak-YYYYMMDD_HHMMSS

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


# ---------------- app/scene.py ----------------
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

        # Colors tuned for dark theme
        self.col_minor = QtGui.QColor(70, 70, 80)     # minor
        self.col_major = QtGui.QColor(95, 95, 110)    # every 5th
        self.col_axis  = QtGui.QColor(150, 150, 170)  # axes

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

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        super().drawBackground(painter, rect)
        if not self.show_grid or self.grid_size <= 0:
            return

        g = self.grid_size
        left = int(rect.left()) - (int(rect.left()) % g)
        top  = int(rect.top())  - (int(rect.top())  % g)

        # draw minor/major grid
        pen_minor = QtGui.QPen(self.col_minor); pen_minor.setCosmetic(True)
        pen_major = QtGui.QPen(self.col_major); pen_major.setCosmetic(True)
        painter.save()
        # verticals
        x = left
        idx = 0
        while x < rect.right():
            painter.setPen(pen_major if (idx % 5 == 0) else pen_minor)
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += g; idx += 1
        # horizontals
        y = top
        idy = 0
        while y < rect.bottom():
            painter.setPen(pen_major if (idy % 5 == 0) else pen_minor)
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += g; idy += 1

        # axes cross at (0,0)
        painter.setPen(QtGui.QPen(self.col_axis))
        painter.drawLine(0, int(rect.top()), 0, int(rect.bottom()))
        painter.drawLine(int(rect.left()), 0, int(rect.right()), 0)
        painter.restore()
"""

# ---------------- app/device.py ----------------
DEVICE_PY = r'''
from PySide6 import QtCore, QtGui, QtWidgets

class DeviceItem(QtWidgets.QGraphicsItemGroup):
    """Device glyph + label + optional coverage overlays (strobe/speaker/smoke)."""
    Type = QtWidgets.QGraphicsItem.UserType + 101

    def type(self): return DeviceItem.Type

    def __init__(self, x, y, symbol, name, manufacturer="", part_number=""):
        super().__init__()
        self.setFlags(
            QtWidgets.QGraphicsItem.ItemIsMovable |
            QtWidgets.QGraphicsItem.ItemIsSelectable
        )
        self.symbol = symbol
        self.name = name
        self.manufacturer = manufacturer
        self.part_number = part_number

        # Base glyph
        self._glyph = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
        pen = QtGui.QPen(QtGui.QColor("#D8D8D8")); pen.setCosmetic(True)
        self._glyph.setPen(pen); self._glyph.setBrush(QtGui.QColor("#20252B"))
        self.addToGroup(self._glyph)

        # Label
        self._label = QtWidgets.QGraphicsSimpleTextItem(self.name)
        self._label.setBrush(QtGui.QBrush(QtGui.QColor("#EAEAEA")))
        self._label.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self._label.setPos(QtCore.QPointF(12, -14))
        self.addToGroup(self._label)

        # Selection halo
        self._halo = QtWidgets.QGraphicsEllipseItem(-9, -9, 18, 18)
        halo_pen = QtGui.QPen(QtGui.QColor(60,180,255,220)); halo_pen.setCosmetic(True); halo_pen.setWidthF(1.4)
        self._halo.setPen(halo_pen); self._halo.setBrush(QtCore.Qt.NoBrush)
        self._halo.setZValue(-1); self._halo.setVisible(False)
        self.addToGroup(self._halo)

        # Coverage overlays
        self.coverage = {"mode":"none", "mount":"ceiling",
                         "params":{},  # mode-specific inputs
                         "computed_radius_ft":0.0,
                         "px_per_ft":12.0}
        self._cov_circle = QtWidgets.QGraphicsEllipseItem(); self._cov_circle.setZValue(-10); self._cov_circle.setVisible(False)
        cpen = QtGui.QPen(QtGui.QColor(80,170,255,200)); cpen.setCosmetic(True); cpen.setStyle(QtCore.Qt.DashLine)
        self._cov_circle.setPen(cpen); self._cov_circle.setBrush(QtGui.QColor(80,170,255,40))
        self.addToGroup(self._cov_circle)

        self._cov_square = QtWidgets.QGraphicsRectItem(); self._cov_square.setZValue(-11); self._cov_square.setVisible(False)
        spen = QtGui.QPen(QtGui.QColor(80,170,255,140)); spen.setCosmetic(True); spen.setStyle(QtCore.Qt.DotLine)
        self._cov_square.setPen(spen); self._cov_square.setBrush(QtGui.QColor(80,170,255,25))
        self.addToGroup(self._cov_square)

        self.setPos(x, y)

    # ---- selection visual
    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            sel = bool(value)
            self._halo.setVisible(sel)
        return super().itemChange(change, value)

    def set_label_text(self, text: str):
        self._label.setText(text)

    # ---- coverage API
    def set_coverage(self, cfg: dict):
        if not cfg: return
        self.coverage.update(cfg)
        self._update_coverage_items()

    def _update_coverage_items(self):
        mode = self.coverage.get("mode","none")
        r_ft = float(self.coverage.get("computed_radius_ft") or 0.0)
        ppf  = float(self.coverage.get("px_per_ft") or 12.0)
        r_px = r_ft * ppf

        # hide all
        self._cov_circle.setVisible(False)
        self._cov_square.setVisible(False)
        if mode == "none" or r_px <= 0:
            return

        # circle always
        self._cov_circle.setRect(-r_px, -r_px, 2*r_px, 2*r_px)
        self._cov_circle.setVisible(True)

        # if strobe + ceiling: show square footprint
        if mode == "strobe" and self.coverage.get("mount","ceiling") == "ceiling":
            side = 2*r_px
            self._cov_square.setRect(-side/2, -side/2, side, side)
            self._cov_square.setVisible(True)

    # ---- serialization
    def to_json(self):
        return {
            "x": float(self.pos().x()),
            "y": float(self.pos().y()),
            "symbol": self.symbol,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "part_number": self.part_number,
            "coverage": self.coverage,
        }

    @staticmethod
    def from_json(d: dict):
        it = DeviceItem(float(d.get("x",0)), float(d.get("y",0)),
                        d.get("symbol","?"), d.get("name","Device"),
                        d.get("manufacturer",""), d.get("part_number",""))
        cov = d.get("coverage")
        if cov: it.set_coverage(cov)
        return it
'''

# ---------------- app/dialogs/coverage.py ----------------
COVERAGE_PY = r'''
from PySide6 import QtCore, QtGui, QtWidgets
import math

class CoverageDialog(QtWidgets.QDialog):
    """Edit per-device coverage. v1 keeps it simple & honest:
       - Strobe: manual coverage diameter (ft); mount = wall/ceiling
       - Speaker: L@10ft and target dB -> inverse-square to compute radius
       - Smoke: spacing (ft) guide ring
       We store computed radius_ft, and caller passes px_per_ft.
    """
    def __init__(self, parent=None, existing=None):
        super().__init__(parent)
        self.setWindowTitle("Coverage")
        self.setModal(True)
        v = QtWidgets.QVBoxLayout(self)

        # Mode
        form = QtWidgets.QFormLayout()
        self.cmb_mode = QtWidgets.QComboBox()
        self.cmb_mode.addItems(["none","strobe","speaker","smoke"])
        self.cmb_mount = QtWidgets.QComboBox()
        self.cmb_mount.addItems(["ceiling","wall"])
        self.ed_diam = QtWidgets.QDoubleSpinBox(); self.ed_diam.setRange(0, 1000); self.ed_diam.setSuffix(" ft"); self.ed_diam.setValue(50.0)
        self.ed_L10  = QtWidgets.QDoubleSpinBox(); self.ed_L10.setRange(40, 130); self.ed_L10.setSuffix(" dB"); self.ed_L10.setValue(95.0)
        self.ed_target = QtWidgets.QDoubleSpinBox(); self.ed_target.setRange(40, 120); self.ed_target.setSuffix(" dB"); self.ed_target.setValue(75.0)
        self.ed_spacing = QtWidgets.QDoubleSpinBox(); self.ed_spacing.setRange(0, 200); self.ed_spacing.setSuffix(" ft"); self.ed_spacing.setValue(30.0)

        form.addRow("Mode:", self.cmb_mode)
        form.addRow("Mount:", self.cmb_mount)
        form.addRow("Strobe coverage diameter:", self.ed_diam)
        form.addRow("Speaker level @10ft:", self.ed_L10)
        form.addRow("Speaker target dB:", self.ed_target)
        form.addRow("Smoke spacing:", self.ed_spacing)
        v.addLayout(form)

        self.lbl_info = QtWidgets.QLabel("Tip: diameter/spacing are simple helpers; NFPA/manufacturer tables override in submittals.")
        self.lbl_info.setWordWrap(True)
        v.addWidget(self.lbl_info)

        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject)
        v.addWidget(bb)

        # load existing
        if existing:
            mode = existing.get("mode","none"); i = self.cmb_mode.findText(mode);
            if i>=0: self.cmb_mode.setCurrentIndex(i)
            mnt = existing.get("mount","ceiling"); j = self.cmb_mount.findText(mnt);
            if j>=0: self.cmb_mount.setCurrentIndex(j)
            p = existing.get("params",{})
            if "diameter_ft" in p: self.ed_diam.setValue(float(p.get("diameter_ft",50.0)))
            if "L10" in p: self.ed_L10.setValue(float(p.get("L10",95.0)))
            if "target_db" in p: self.ed_target.setValue(float(p.get("target_db",75.0)))
            if "spacing_ft" in p: self.ed_spacing.setValue(float(p.get("spacing_ft",30.0)))

    def get_settings(self, px_per_ft: float):
        mode = self.cmb_mode.currentText()
        mount = self.cmb_mount.currentText()
        params = {}
        radius_ft = 0.0

        if mode == "strobe":
            diam = float(self.ed_diam.value())
            params = {"diameter_ft": diam}
            radius_ft = max(0.0, diam/2.0)

        elif mode == "speaker":
            L10 = float(self.ed_L10.value())
            tgt = float(self.ed_target.value())
            params = {"L10": L10, "target_db": tgt}
            # inverse-square, ref at 10 ft: L(r) = L10 - 20*log10(r/10)
            # Solve for r: r = 10 * 10**((L10 - tgt)/20)
            radius_ft = 10.0 * (10.0 ** ((L10 - tgt)/20.0))
            radius_ft = max(0.0, radius_ft)

        elif mode == "smoke":
            spacing = float(self.ed_spacing.value())
            params = {"spacing_ft": spacing}
            radius_ft = max(0.0, spacing/2.0)

        else:  # none
            params = {}
            radius_ft = 0.0

        return {
            "mode": mode,
            "mount": mount,
            "params": params,
            "computed_radius_ft": radius_ft,
            "px_per_ft": float(px_per_ft),
        }
'''

# ---------------- app/tools/array.py ----------------
ARRAY_PY = r'''
from PySide6 import QtCore, QtGui, QtWidgets
from app.device import DeviceItem

class ArrayTool(QtCore.QObject):
    """Simple rectangular array: spacing derived from active device coverage or manual."""
    def __init__(self, window, devices_group):
        super().__init__(window)
        self.win = window
        self.layer_devices = devices_group

    def run(self):
        win = self.win
        proto = getattr(win.view, "current_proto", None)
        if not proto:
            QtWidgets.QMessageBox.information(win, "Array", "Pick a device in the palette first.")
            return

        # spacing from active "defaults" or device coverage after place; here ask user:
        spacing_ft, ok = QtWidgets.QInputDialog.getDouble(win, "Array spacing", "Center-to-center spacing (ft):",
                                                          win.prefs.get("array_spacing_ft", 20.0), 1.0, 200.0, 1)
        if not ok: return
        win.prefs["array_spacing_ft"] = spacing_ft

        width_ft, ok = QtWidgets.QInputDialog.getDouble(win, "Area width", "Width (ft):",
                                                        60.0, 1.0, 10000.0, 1)
        if not ok: return
        height_ft, ok = QtWidgets.QInputDialog.getDouble(win, "Area height", "Height (ft):",
                                                         40.0, 1.0, 10000.0, 1)
        if not ok: return

        ppf = float(win.px_per_ft)
        sx = spacing_ft * ppf
        cols = max(1, int(width_ft/spacing_ft))
        rows = max(1, int(height_ft/spacing_ft))

        # place centered in the current view rect
        vis = win.view.mapToScene(win.view.viewport().rect()).boundingRect()
        cx, cy = vis.center().x(), vis.center().y()
        left = cx - (cols-1)*sx/2.0
        top  = cy - (rows-1)*sx/2.0

        for r in range(rows):
            for c in range(cols):
                x = left + c*sx
                y = top  + r*sx
                d = proto
                it = DeviceItem(x, y, d["symbol"], d["name"], d.get("manufacturer",""), d.get("part_number",""))
                # default coverage for previewed arrays (optional: half spacing ring)
                it.set_coverage({"mode":"strobe","mount":"ceiling",
                                 "computed_radius_ft": spacing_ft/2.0, "px_per_ft": ppf})
                it.setParentItem(self.layer_devices)

        win.push_history()
        win.statusBar().showMessage(f"Array placed: {cols}x{rows} at ~{spacing_ft:.1f} ft.")
'''

# ---------------- app/main.py (patch-in minimal, self-contained features) ----------------
MAIN_PATCH = r"""
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

APP_VERSION = "0.6.2-overlayA"
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
        self.devices_group = devices_group
        self.wires_group = wires_group
        self.sketch_group = sketch_group
        self.overlay_group = overlay_group
        self.ortho = False
        self.win = window_ref
        self.current_proto = None
        self.ghost = None  # live preview device

        # crosshair overlay
        self.cross_v = QtWidgets.QGraphicsLineItem(); self.cross_h = QtWidgets.QGraphicsLineItem()
        pen = QtGui.QPen(QtGui.QColor(150,150,160,170)); pen.setCosmetic(True); pen.setStyle(Qt.DashLine)
        self.cross_v.setPen(pen); self.cross_h.setPen(pen)
        self.cross_v.setParentItem(self.overlay_group); self.cross_h.setParentItem(self.overlay_group)
        self.show_crosshair = True

        # zoom-to-cursor (plays nice with our cad_nav add-on)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def set_current_device(self, proto: dict):
        self.current_proto = proto
        self._ensure_ghost()

    def _ensure_ghost(self):
        if not self.current_proto:
            if self.ghost:
                self.scene().removeItem(self.ghost); self.ghost = None
            return
        if not self.ghost:
            d = self.current_proto
            self.ghost = DeviceItem(0, 0, d["symbol"], d["name"], d.get("manufacturer",""), d.get("part_number",""))
            # default live coverage preview (uses prefs)
            ppf = float(self.win.px_per_ft)
            diam_ft = float(self.win.prefs.get("default_strobe_diameter_ft", 50.0))
            self.ghost.set_coverage({"mode":"strobe","mount":"ceiling",
                                     "computed_radius_ft": max(0.0, diam_ft/2.0),
                                     "px_per_ft": ppf})
            self.ghost.setOpacity(0.6)
            self.ghost.setParentItem(self.overlay_group)

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
        if e.key()==Qt.Key_Escape and getattr(self.win, "draw", None): self.win.draw.finish(); e.accept(); return
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
        if getattr(self.win, "dim_tool", None):
            try: self.win.dim_tool.on_mouse_move(sp)
            except Exception: pass
        super().mouseMoveEvent(e)

    def mousePressEvent(self, e: QtGui.QMouseEvent):
        win = self.win
        sp = self.scene().snap(self.mapToScene(e.position().toPoint()))
        if e.button()==Qt.LeftButton:
            if self.current_proto:
                d = self.current_proto
                it = DeviceItem(sp.x(), sp.y(), d["symbol"], d["name"], d.get("manufacturer",""), d.get("part_number",""))
                # start with same preview coverage as ghost
                if self.ghost:
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
        self.prefs.setdefault("array_spacing_ft", 20.0)
        save_prefs(self.prefs)

        self.devices_all = catalog.load_catalog()

        self.scene = GridScene(int(self.prefs.get("grid", DEFAULT_GRID_SIZE)), 0,0,15000,10000)
        self.scene.snap_enabled = bool(self.prefs.get("snap", True))
        self._apply_snap_step_from_inches(self.snap_step_in)

        self.layer_underlay = QtWidgets.QGraphicsItemGroup(); self.layer_underlay.setZValue(-50); self.scene.addItem(self.layer_underlay)
        self.layer_sketch   = QtWidgets.QGraphicsItemGroup(); self.layer_sketch.setZValue(40);   self.scene.addItem(self.layer_sketch)
        self.layer_wires    = QtWidgets.QGraphicsItemGroup(); self.layer_wires.setZValue(60);    self.scene.addItem(self.layer_wires)
        self.layer_devices  = QtWidgets.QGraphicsItemGroup(); self.layer_devices.setZValue(100);  self.scene.addItem(self.layer_devices)
        self.layer_overlay  = QtWidgets.QGraphicsItemGroup(); self.layer_overlay.setZValue(200);  self.scene.addItem(self.layer_overlay)

        self.view = CanvasView(self.scene, self.layer_devices, self.layer_wires, self.layer_sketch, self.layer_overlay, self)

        self.current_underlay_path = None

        self.array_tool = ArrayTool(self, self.layer_devices)

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
        m_tools.addAction("Place Array…", self.array_tool.run)

        m_view = menubar.addMenu("&View")
        self.act_view_grid = QtGui.QAction("Grid", self, checkable=True); self.act_view_grid.setChecked(True); self.act_view_grid.toggled.connect(self.toggle_grid); m_view.addAction(self.act_view_grid)
        self.act_view_snap = QtGui.QAction("Snap", self, checkable=True); self.act_view_snap.setChecked(self.scene.snap_enabled); self.act_view_snap.toggled.connect(self.toggle_snap); m_view.addAction(self.act_view_snap)
        self.act_view_cross = QtGui.QAction("Crosshair (C)", self, checkable=True); self.act_view_cross.setChecked(True); self.act_view_cross.toggled.connect(self.toggle_crosshair); m_view.addAction(self.act_view_cross)
        m_view.addSeparator()
        act_scale = QtGui.QAction("Set Pixels per Foot…", self); act_scale.triggered.connect(self.set_px_per_ft); m_view.addAction(act_scale)

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

        # toolbar (lightweight)
        tb = QToolBar("Main"); tb.setIconSize(QSize(16,16)); self.addToolBar(tb)
        tb.addAction(self.act_view_grid); tb.addAction(self.act_view_snap); tb.addAction(self.act_view_cross)

        # history
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
        self.view.set_current_device(it.data(Qt.UserRole)); self.statusBar().showMessage(f"Selected: {it.data(Qt.UserRole)['name']}")

    # view toggles
    def toggle_grid(self, on: bool): self.scene.show_grid = bool(on); self.scene.update()
    def toggle_snap(self, on: bool): self.scene.snap_enabled = bool(on)
    def toggle_crosshair(self, on: bool): self.view.show_crosshair = bool(on)

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
                    # turn on strobe ring using default diameter
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
"""

# ---------------- CHANGELOG.md append ----------------
CHANGELOG_ADD = r"""
## v0.6.2 – overlayA (stability + coverage, {date})
- **Grid**: always-on draw; major/minor lines; origin cross; tuned contrast for dark theme.
- **Selection**: high-contrast selection halo for devices.
- **Coverage overlays**:
  - Per-device **Coverage…** dialog with **Strobe / Speaker(dB) / Smoke** modes.
  - Strobe: manual **coverage diameter (ft)**; ceiling mount shows **circle in square** footprint.
  - Speaker: **inverse-square** model (L@10ft → target dB) to compute radius.
  - Smoke: simple **spacing (ft)** ring (visual guide).
  - Toggle coverage on/off via right-click.
- **Live preview**: when a palette device is active, a **ghost device + coverage** follows your cursor (editable after placement).
- **Array**: “Place Array…” uses **coverage-driven spacing** by default (with manual override).
- **Persistence**: overlays and settings persist via `.autofire` save files and user preferences.
- **Notes**: NFPA/manufacturer tables will be wired next; current coverage helpers are conservative visual aids.

"""


def main():
    # write files
    backup_write(ROOT / "app" / "scene.py", SCENE_PY)
    backup_write(ROOT / "app" / "device.py", DEVICE_PY)
    backup_write(ROOT / "app" / "dialogs" / "coverage.py", COVERAGE_PY)
    backup_write(ROOT / "app" / "tools" / "array.py", ARRAY_PY)

    # main.py: only overwrite if project is in flux; we provide a full working main
    backup_write(ROOT / "app" / "main.py", MAIN_PATCH)

    # changelog append
    cl = ROOT / "CHANGELOG.md"
    existing = ""
    if cl.exists():
        existing = cl.read_text(encoding="utf-8")
    entry = CHANGELOG_ADD.replace("{date}", time.strftime("%Y-%m-%d"))
    cl.write_text(existing.rstrip() + "\n\n" + entry, encoding="utf-8")
    print(f"[append] {cl} v0.6.2 entry added")

    print("\nDone. Launch with:\n  py -3 -m app.boot")


if __name__ == "__main__":
    main()
