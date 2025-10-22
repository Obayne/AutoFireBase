# apply_067_cad_core_hotfix.py
# Fixes: real Space-hand pan (bypass placement), legible dark theme, clearer selection,
# lighter grid, keeps device placement working. Writes app/main.py, app/scene.py, app/device.py

import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STAMP = time.strftime("%Y%m%d_%H%M%S")


def backup_write(target: Path, text: str):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        bak = target.with_suffix(target.suffix + f".bak-{STAMP}")
        shutil.copy2(target, bak)
        import logging

        from app.logging_config import setup_logging

        setup_logging()
        logging.getLogger(__name__).info("[backup] %s", bak)
    target.write_text(text.strip() + "\n", encoding="utf-8")
    logging.getLogger(__name__).info("[write ] %s", target)


# ---------------- app/scene.py ----------------
SCENE = r"""
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

DEFAULT_GRID_SIZE = 48  # px per minor grid at default zoom

class GridScene(QtWidgets.QGraphicsScene):
    def __init__(self, grid_size=DEFAULT_GRID_SIZE, *rect):
        super().__init__(*rect)
        self.grid_size = int(grid_size)
        self.show_grid = True
        self.snap_enabled = True
        self.snap_step_px = 0.0   # 0 → snap to grid intersections only
        # visual style (overridable from preferences)
        self.grid_opacity = 0.20
        self.grid_width_px = 0.0   # cosmetic thin
        self.grid_major_every = 5  # every N minor lines

    # called by preferences dialog/slider
    def set_grid_style(self, opacity=None, width_px=None, major_every=None):
        if opacity is not None:
            self.grid_opacity = max(0.10, min(1.00, float(opacity)))
        if width_px is not None:
            self.grid_width_px = max(0.0, float(width_px))
        if major_every is not None:
            self.grid_major_every = max(1, int(major_every))
        self.update()

    def snap(self, p: QtCore.QPointF) -> QtCore.QPointF:
        if not self.snap_enabled:
            return p
        if self.snap_step_px and self.snap_step_px > 0:
            s = self.snap_step_px
            return QtCore.QPointF(round(p.x()/s)*s, round(p.y()/s)*s)
        # grid intersections
        g = float(self.grid_size)
        return QtCore.QPointF(round(p.x()/g)*g, round(p.y()/g)*g)

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        super().drawBackground(painter, rect)
        if not self.show_grid or self.grid_size <= 1:
            return

        left   = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top    = int(rect.top())  - (int(rect.top())  % self.grid_size)
        right  = int(rect.right())
        bottom = int(rect.bottom())

        # colors
        minor_col = QtGui.QColor(200, 200, 205)
        minor_col.setAlphaF(self.grid_opacity * 0.65)
        major_col = QtGui.QColor(170, 170, 175)
        major_col.setAlphaF(self.grid_opacity)

        pen_minor = QtGui.QPen(minor_col)
        pen_major = QtGui.QPen(major_col)
        pen_minor.setCosmetic(True)
        pen_major.setCosmetic(True)
        if self.grid_width_px > 0:
            pen_minor.setWidthF(self.grid_width_px)
            pen_major.setWidthF(max(1.0, self.grid_width_px+0.2))

        # verticals
        painter.setPen(pen_minor)
        x = left
        n = 0
        while x <= right:
            n += 1
            if (n % self.grid_major_every) == 0:
                painter.setPen(pen_major)
                painter.drawLine(x, top, x, bottom)
                painter.setPen(pen_minor)
            else:
                painter.drawLine(x, top, x, bottom)
            x += self.grid_size

        # horizontals
        y = top
        n = 0
        while y <= bottom:
            n += 1
            if (n % self.grid_major_every) == 0:
                painter.setPen(pen_major)
                painter.drawLine(left, y, right, y)
                painter.setPen(pen_minor)
            else:
                painter.drawLine(left, y, right, y)
            y += self.grid_size
"""

# ---------------- app/device.py ----------------
DEVICE = r"""
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

class DeviceItem(QtWidgets.QGraphicsItemGroup):
    def __init__(self, x: float, y: float, symbol: str, name: str, manufacturer: str = "", part_number: str = ""):
        super().__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.symbol = symbol
        self.name = name
        self.manufacturer = manufacturer
        self.part_number = part_number

        # Base glyph (type color comes from symbol/name heuristics)
        col = self._color_for_symbol(symbol, name)
        self._glyph = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
        p = QtGui.QPen(Qt.black); p.setCosmetic(True)
        self._glyph.setPen(p)
        self._glyph.setBrush(QtGui.QBrush(col))
        self.addToGroup(self._glyph)

        # Label
        self.label_offset = QtCore.QPointF(12, -14)
        self._label = QtWidgets.QGraphicsSimpleTextItem(self.name)
        self._label.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self._label.setPos(self.label_offset)
        self.addToGroup(self._label)

        # Selection ring (clearer selection)
        self._sel_ring = QtWidgets.QGraphicsEllipseItem(-9,-9,18,18)
        sel_pen = QtGui.QPen(QtGui.QColor(66,133,244)); sel_pen.setCosmetic(True); sel_pen.setWidthF(1.2)
        self._sel_ring.setPen(sel_pen)
        self._sel_ring.setBrush(QtGui.QColor(66,133,244,40))
        self._sel_ring.setZValue(-4)
        self._sel_ring.setVisible(False)
        self.addToGroup(self._sel_ring)

        # Coverage overlay
        self.coverage = {"mode":"none","mount":"ceiling","radius_ft":0.0,"px_per_ft":12.0,
                         "speaker":{"model":"physics (20log)","db_ref":95.0,"target_db":75.0,"loss10":6.0},
                         "strobe":{"candela":177.0,"target_lux":0.2},
                         "computed_radius_px": 0.0,
                         "computed_radius_ft": 0.0}
        self._cov_circle = None
        self._cov_square = None
        self._cov_rect = None

        self.setPos(x, y)

    # -------- type color ----------
    def _color_for_symbol(self, symbol: str, name: str) -> QtGui.QColor:
        s = (symbol or "").lower() + " " + (name or "").lower()
        if any(k in s for k in ("strobe","av","candela")):   return QtGui.QColor(240, 85, 85)   # red-ish
        if any(k in s for k in ("speaker","spkr","voice")):  return QtGui.QColor(255, 165, 44)  # amber
        if any(k in s for k in ("smoke","heat","detector")): return QtGui.QColor(117, 200, 117) # green
        return QtGui.QColor(210, 210, 230)                   # neutral

    def set_label_text(self, text: str):
        self._label.setText(text)

    def set_label_offset(self, dx: float, dy: float):
        self.label_offset = QtCore.QPointF(dx, dy)
        self._label.setPos(self.label_offset)

    # -------- selection feedback ----------
    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedHasChanged:
            self._sel_ring.setVisible(bool(value))
        return super().itemChange(change, value)

    # -------- coverage drawing ----------
    def set_coverage(self, settings: dict):
        if not settings: return
        self.coverage.update(settings)
        # compute px if only ft provided
        r_ft = float(self.coverage.get("computed_radius_ft") or 0.0)
        ppf  = float(self.coverage.get("px_per_ft") or 12.0)
        if r_ft > 0:
            self.coverage["computed_radius_px"] = r_ft * ppf
        self._update_coverage_items()

    def _ensure_cov_items(self):
        if self._cov_circle is None:
            self._cov_circle = QtWidgets.QGraphicsEllipseItem(); self._cov_circle.setParentItem(self); self._cov_circle.setZValue(-5)
            pen = QtGui.QPen(QtGui.QColor(50,120,255,200)); pen.setStyle(Qt.DashLine); pen.setCosmetic(True)
            self._cov_circle.setPen(pen); self._cov_circle.setBrush(QtGui.QColor(50,120,255,60))
        if self._cov_square is None:
            self._cov_square = QtWidgets.QGraphicsRectItem(); self._cov_square.setParentItem(self); self._cov_square.setZValue(-6)
            pen = QtGui.QPen(QtGui.QColor(50,120,255,120)); pen.setStyle(Qt.DotLine); pen.setCosmetic(True)
            self._cov_square.setPen(pen); self._cov_square.setBrush(QtGui.QColor(50,120,255,30))
        if self._cov_rect is None:
            self._cov_rect = QtWidgets.QGraphicsRectItem(); self._cov_rect.setParentItem(self); self._cov_rect.setZValue(-6)
            pen = QtGui.QPen(QtGui.QColor(50,120,255,120)); pen.setStyle(Qt.DotLine); pen.setCosmetic(True)
            self._cov_rect.setPen(pen); self._cov_rect.setBrush(QtGui.QColor(50,120,255,30))

    def _update_coverage_items(self):
        mode = self.coverage.get("mode","none")
        mount = self.coverage.get("mount","ceiling")
        r_px = float(self.coverage.get("computed_radius_px") or 0.0)

        for it in (self._cov_circle, self._cov_square, self._cov_rect):
            if it: it.setVisible(False)

        if mode=="none" or r_px <= 0:
            return

        self._ensure_cov_items()
        self._cov_circle.setRect(-r_px, -r_px, 2*r_px, 2*r_px); self._cov_circle.setVisible(True)

        if mount=="ceiling" and mode=="strobe":
            side = 2*r_px
            self._cov_square.setRect(-side/2, -side/2, side, side); self._cov_square.setVisible(True)
        elif mount=="wall" and mode in ("strobe","speaker"):
            self._cov_rect.setRect(0, -r_px, r_px*2.0, r_px*2.0); self._cov_rect.setVisible(True)

    # -------- serialization ----------
    def to_json(self):
        return {
            "x": float(self.pos().x()),
            "y": float(self.pos().y()),
            "symbol": self.symbol,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "part_number": self.part_number,
            "label_offset": [self.label_offset.x(), self.label_offset.y()],
            "coverage": self.coverage,
        }

    @staticmethod
    def from_json(d: dict):
        it = DeviceItem(float(d.get("x",0)), float(d.get("y",0)),
                        d.get("symbol","?"), d.get("name","Device"),
                        d.get("manufacturer",""), d.get("part_number",""))
        off = d.get("label_offset")
        if isinstance(off,(list,tuple)) and len(off)==2:
            it.set_label_offset(float(off[0]), float(off[1]))
        cov = d.get("coverage")
        if cov: it.set_coverage(cov)
        return it
"""

# ---------------- app/main.py ----------------
MAIN = r"""
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
try:
    from app.tools.dimension import DimensionTool
except Exception:
    class DimensionTool:
        def __init__(self, *a, **k): self.active=False
        def start(self): self.active=True
        def on_mouse_move(self, *a, **k): pass
        def on_click(self, *a, **k): self.active=False; return True
        def cancel(self): self.active=False

APP_VERSION = "0.6.7-cad-core"
APP_TITLE   = f"Auto-Fire {APP_VERSION}"
PREF_DIR    = os.path.join(os.path.expanduser("~"), "AutoFire")
PREF_PATH   = os.path.join(PREF_DIR, "preferences.json")
LOG_DIR     = os.path.join(PREF_DIR, "logs")

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
    if any(k in text for k in ["strobe","av","nac-strobe","cd","candela"]): return "strobe"
    if any(k in text for k in ["speaker","spkr","voice"]): return "speaker"
    if any(k in text for k in ["smoke","detector","heat"]): return "smoke"
    return "other"

class CanvasView(QGraphicsView):
    def __init__(self, scene, devices_group, wires_group, sketch_group, overlay_group, window_ref):
        super().__init__(scene)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)
        self.setMouseTracking(True)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.devices_group = devices_group
        self.wires_group   = wires_group
        self.sketch_group  = sketch_group
        self.overlay_group = overlay_group
        self.ortho = False
        self.win   = window_ref
        self.current_proto = None
        self.current_kind  = "other"
        self.ghost = None

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
        # only show coverage ghost for relevant types
        if not self.current_proto or self.current_kind not in ("strobe","speaker","smoke"):
            if self.ghost:
                self.scene().removeItem(self.ghost); self.ghost = None
            return
        if not self.ghost:
            d = self.current_proto
            self.ghost = DeviceItem(0, 0, d["symbol"], d["name"], d.get("manufacturer",""), d.get("part_number",""))
            self.ghost.setOpacity(0.65)
            self.ghost.setParentItem(self.overlay_group)
        ppf = float(self.win.px_per_ft)
        if self.current_kind == "strobe":
            diam_ft = float(self.win.prefs.get("default_strobe_diameter_ft", 50.0))
            self.ghost.set_coverage({"mode":"strobe","mount":"ceiling",
                                     "computed_radius_ft": max(0.0, diam_ft/2.0),
                                     "px_per_ft": ppf})
        elif self.current_kind == "speaker":
            self.ghost.set_coverage({"mode":"speaker","mount":"ceiling",
                                     "computed_radius_ft": 30.0, "px_per_ft": ppf})
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
        self.win.statusBar().showMessage(f"x={dx_ft:.2f} ft   y={dy_ft:.2f} ft   scale={self.win.px_per_ft:.2f} px/ft")

    def wheelEvent(self, e: QtGui.QWheelEvent):
        s = 1.15 if e.angleDelta().y() > 0 else 1/1.15
        self.scale(s, s)

    def keyPressEvent(self, e: QtGui.QKeyEvent):
        k = e.key()
        if k==Qt.Key_Space:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setCursor(Qt.OpenHandCursor); e.accept(); return
        if k==Qt.Key_Shift: self.ortho=True; e.accept(); return
        if k==Qt.Key_C: self.show_crosshair = not self.show_crosshair; e.accept(); return
        if k==Qt.Key_Escape:
            self.win.cancel_active_tool(); e.accept(); return
        super().keyPressEvent(e)

    def keyReleaseEvent(self, e: QtGui.QKeyEvent):
        k = e.key()
        if k==Qt.Key_Space:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.unsetCursor(); e.accept(); return
        if k==Qt.Key_Shift: self.ortho=False; e.accept(); return
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
        # If space-hand mode, let QGraphicsView do the panning and don't place anything
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            return super().mousePressEvent(e)

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
        self.prefs.setdefault("grid_opacity", 0.20)
        self.prefs.setdefault("grid_width_px", 0.0)
        self.prefs.setdefault("grid_major_every", 5)
        save_prefs(self.prefs)

        self.apply_dark_theme()

        self.devices_all = catalog.load_catalog()

        self.scene = GridScene(int(self.prefs.get("grid", DEFAULT_GRID_SIZE)), 0,0,15000,10000)
        self.scene.snap_enabled = bool(self.prefs.get("snap", True))
        self.scene.set_grid_style(float(self.prefs.get("grid_opacity",0.20)),
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

        # Toolbar minimal
        tb = QToolBar("Main"); tb.setIconSize(QSize(16,16)); self.addToolBar(tb)
        tb.addAction(self.act_view_grid); tb.addAction(self.act_view_snap); tb.addAction(self.act_view_cross)

        # Status bar Grid opacity slider
        sb = self.statusBar()
        wrap = QWidget(); lay = QHBoxLayout(wrap); lay.setContentsMargins(6,0,6,0); lay.setSpacing(6)
        lay.addWidget(QLabel("Grid"))
        self.slider_grid = QtWidgets.QSlider(Qt.Horizontal); self.slider_grid.setMinimum(10); self.slider_grid.setMaximum(100)
        self.slider_grid.setFixedWidth(120)
        cur_op = float(self.prefs.get("grid_opacity", 0.20))
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

        # Right dock: Layers & (basic) Properties
        self._build_layers_and_props_dock()

        # Shortcuts
        QtGui.QShortcut(QtGui.QKeySequence("D"), self, activated=self.start_dimension)
        QtGui.QShortcut(QtGui.QKeySequence("Esc"), self, activated=self.cancel_active_tool)
        QtGui.QShortcut(QtGui.QKeySequence("F2"), self, activated=self.fit_view_to_content)

        # Selection → update Properties
        self.scene.selectionChanged.connect(self._on_selection_changed)

        self.history = []; self.history_index = -1
        self.push_history()

    # ---------- Theme (legible dark) ----------
    def apply_dark_theme(self):
        app = QtWidgets.QApplication.instance()
        app.setStyle("Fusion")
        pal = QtGui.QPalette()
        bg   = QtGui.QColor(25,26,28)
        base = QtGui.QColor(32,33,36)
        text = QtGui.QColor(230,230,235)
        pal.setColor(QtGui.QPalette.ColorRole.Window, bg)
        pal.setColor(QtGui.QPalette.ColorRole.Base, base)
        pal.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(38,39,43))
        pal.setColor(QtGui.QPalette.ColorRole.Text, text)
        pal.setColor(QtGui.QPalette.ColorRole.WindowText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Button, base)
        pal.setColor(QtGui.QPalette.ColorRole.ButtonText, text)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipBase, base)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(66,133,244))
        pal.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(255,255,255))
        app.setPalette(pal)
        # Ensure menu/toolbar read well
        # Use triple-single-quotes here to avoid terminating the outer
        # triple-double-quoted MAIN string that contains this block.
        app.setStyleSheet('''
            QMenuBar, QToolBar { background: #2a2b2f; color:#e6e6eb; }
            QMenuBar::item:selected { background:#3a3b40; }
            QMenu { background:#2a2b2f; color:#e6e6eb; }
            QMenu::item:selected { background:#3a3b40; }
            QStatusBar { background:#222326; color:#d7d7dc; }
        ''')

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

        form.addWidget(QLabel("Layers"))
        self.chk_underlay = QCheckBox("Underlay"); self.chk_underlay.setChecked(True); self.chk_underlay.toggled.connect(lambda v: self.layer_underlay.setVisible(v)); form.addWidget(self.chk_underlay)
        self.chk_sketch   = QCheckBox("Sketch"); self.chk_sketch.setChecked(True);   self.chk_sketch.toggled.connect(lambda v: self.layer_sketch.setVisible(v));     form.addWidget(self.chk_sketch)
        self.chk_wires    = QCheckBox("Wiring"); self.chk_wires.setChecked(True);    self.chk_wires.toggled.connect(lambda v: self.layer_wires.setVisible(v));       form.addWidget(self.chk_wires)
        self.chk_devices  = QCheckBox("Devices"); self.chk_devices.setChecked(True); self.chk_devices.toggled.connect(lambda v: self.layer_devices.setVisible(v));   form.addWidget(self.chk_devices)

        form.addSpacing(6); form.addWidget(QLabel("Grid Size"))
        self.spin_grid = QSpinBox(); self.spin_grid.setRange(2, 500); self.spin_grid.setValue(self.scene.grid_size)
        self.spin_grid.valueChanged.connect(self.change_grid_size)
        form.addWidget(self.spin_grid)

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
        self.statusBar().showMessage(f"Selected: {d['name']}")

    # ---------- toggles ----------
    def toggle_grid(self, on: bool): self.scene.show_grid = bool(on); self.scene.update()
    def toggle_snap(self, on: bool): self.scene.snap_enabled = bool(on)
    def toggle_crosshair(self, on: bool):
        self.view.show_crosshair = bool(on)
        self.scene.update()

    # ---------- scale/snap ----------
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

    # ---------- esc / cancel ----------
    def cancel_active_tool(self):
        if getattr(self, "draw", None):
            try: self.draw.finish()
            except Exception: pass
        if getattr(self, "dim_tool", None):
            try:
                if hasattr(self.dim_tool, "cancel"): self.dim_tool.cancel()
                else: self.dim_tool.active=False
            except Exception: pass
        self.view.current_proto = None
        if self.view.ghost:
            try: self.scene.removeItem(self.view.ghost)
            except Exception: pass
            self.view.ghost = None
        self.statusBar().showMessage("Cancelled")

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
                # minimal: open size dialog-like not included here (kept simple)
                sz, ok = QtWidgets.QInputDialog.getDouble(self, "Coverage size", "Diameter/Radius(ft)", 50.0, 0, 1000, 1)
                if ok:
                    d.set_coverage({"mode":"strobe","mount":"ceiling",
                                    "computed_radius_ft": max(0.0, sz/2.0),
                                    "px_per_ft": self.px_per_ft})
                    self.push_history()
            elif act == act_tog:
                if d.coverage.get("mode","none")=="none":
                    d.set_coverage({"mode":"strobe","mount":"ceiling",
                                    "computed_radius_ft": 25.0,
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
                "grid_opacity": float(self.prefs.get("grid_opacity",0.20)),
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
        self.prefs["grid_opacity"] = float(data.get("grid_opacity", self.prefs.get("grid_opacity",0.20)))
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

    # ---------- right-dock props ----------
    def _get_selected_device(self):
        for it in self.scene.selectedItems():
            if isinstance(it, DeviceItem): return it
        return None

    def _on_selection_changed(self):
        d = self._get_selected_device()
        if not d:
            self._enable_props(False);
            return
        self._enable_props(True)
        self.prop_label.setText(d._label.text())
        offx = d.label_offset.x()/self.px_per_ft
        offy = d.label_offset.y()/self.px_per_ft
        self.prop_offx.blockSignals(True); self.prop_offy.blockSignals(True)
        self.prop_offx.setValue(offx); self.prop_offy.setValue(offy)
        self.prop_offx.blockSignals(False); self.prop_offy.blockSignals(False)
        cov = d.coverage or {}
        self.prop_mount.setCurrentText(cov.get("mount","ceiling"))
        mode = cov.get("mode","none")
        if mode not in ("none","strobe","speaker","smoke"): mode="none"
        self.prop_mode.setCurrentText(mode)
        size_ft = float(cov.get("computed_radius_ft",0.0))*2.0 if mode=="strobe" else (
                  float(cov.get("params",{}).get("spacing_ft",0.0)) if mode=="smoke" else
                  float(cov.get("computed_radius_ft",0.0)))
        self.prop_size.setValue(max(0.0, size_ft))

    def _enable_props(self, on: bool):
        for w in (self.prop_label, self.prop_offx, self.prop_offy, self.prop_mount, self.prop_mode, self.prop_size, self.btn_apply_props):
            w.setEnabled(on)

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
        mode = self.prop_mode.currentText()
        mount = self.prop_mount.currentText()
        sz = float(self.prop_size.value())
        cov = {"mode":mode, "mount":mount, "px_per_ft": self.px_per_ft}
        if mode == "none":
            cov["computed_radius_ft"] = 0.0
        elif mode == "strobe":
            cov["computed_radius_ft"] = max(0.0, sz/2.0)
        elif mode == "smoke":
            spacing_ft = max(0.0, sz)
            cov["params"] = {"spacing_ft": spacing_ft}
            cov["computed_radius_ft"] = spacing_ft/2.0
        elif mode == "speaker":
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
    backup_write(ROOT / "app" / "scene.py", SCENE)
    backup_write(ROOT / "app" / "device.py", DEVICE)
    backup_write(ROOT / "app" / "main.py", MAIN)
    print("\nDone. Launch with:\n  py -3 -m app.boot\n")


if __name__ == "__main__":
    main()
