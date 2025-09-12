# apply_corecad_060.py
# Writes a minimal, stable CAD core for Auto-Fire (v0.6.0-corecad)
# Safe to run multiple times; backs up any existing target files to *.bak-YYYYmmdd_HHMMSS

import os, sys, time
from pathlib import Path

STAMP = time.strftime("%Y%m%d_%H%M%S")
ROOT = Path(".").resolve()

FILES = {
    # ---------------- app package ----------------
    "app/__init__.py": '''
# Auto-Fire app package marker
''',

    "app/minwin.py": r'''
from PySide6 import QtWidgets

class MinimalWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto-Fire — Minimal Window")
        lab = QtWidgets.QLabel("Fallback UI (minimal). If you see this, app.main.create_window() was not found.")
        lab.setMargin(16)
        self.setCentralWidget(lab)
        self.resize(900, 600)
''',

    "app/boot.py": r'''
# Robust loader that works when run as a module (-m app.boot) or as a script (py app\boot.py)
import sys, importlib, importlib.util, types
from pathlib import Path
from PySide6 import QtWidgets
from core.error_hook import install as install_error_hook, write_crash_log

install_error_hook()

def _import_app_main():
    # Try normal import first
    try:
        return importlib.import_module("app.main")
    except Exception:
        pass

    # Running from source as a script: create synthetic 'app' package and load app/main.py
    here = Path(__file__).resolve().parent
    direct = here / "main.py"
    if direct.exists():
        if "app" not in sys.modules:
            pkg = types.ModuleType("app")
            pkg.__path__ = [str(here)]
            pkg.__package__ = "app"
            sys.modules["app"] = pkg
        spec = importlib.util.spec_from_file_location("app.main", str(direct))
        mod  = importlib.util.module_from_spec(spec)  # type: ignore
        assert spec and spec.loader
        spec.loader.exec_module(mod)                  # type: ignore[attr-defined]
        sys.modules["app.main"] = mod
        return mod

    raise ModuleNotFoundError("app.main")

def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    try:
        m = _import_app_main()
        create_window = getattr(m, "create_window", None)
        if callable(create_window):
            w = create_window()
            w.show()
            app.exec()
            return
        from app.minwin import MinimalWindow
        w = MinimalWindow()
        w.show()
        app.exec()
    except Exception:
        import traceback
        tb = traceback.format_exc()
        p = write_crash_log(tb)
        try:
            QtWidgets.QMessageBox.critical(None, "Startup Error", f"{tb}\n\nSaved: {p}")
        except Exception:
            pass

if __name__ == "__main__":
    main()
''',

    "app/scene.py": r'''
from PySide6 import QtCore, QtGui, QtWidgets

DEFAULT_GRID_SIZE = 24  # pixels

class GridScene(QtWidgets.QGraphicsScene):
    def __init__(self, grid=DEFAULT_GRID_SIZE, *a):
        super().__init__(*a)
        self.grid_size    = int(grid)
        self.snap_enabled = True
        self.snap_step_px = 0.0
        self.show_grid    = True

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        if not self.show_grid:
            return
        s = max(2, int(self.grid_size))
        pen_major = QtGui.QPen(QtGui.QColor(70,70,75))
        pen_minor = QtGui.QPen(QtGui.QColor(45,45,50))
        left = int(rect.left()) - (int(rect.left()) % s)
        top  = int(rect.top())  - (int(rect.top())  % s)

        painter.setPen(pen_minor)
        for x in range(left, int(rect.right())+s, s):
            painter.drawLine(x, rect.top(), x, rect.bottom())
        for y in range(top, int(rect.bottom())+s, s):
            painter.drawLine(rect.left(), y, rect.right(), y)

        painter.setPen(pen_major)
        painter.drawLine(0, rect.top(), 0, rect.bottom())
        painter.drawLine(rect.left(), 0, rect.right(), 0)

    def snap(self, p: QtCore.QPointF) -> QtCore.QPointF:
        if not self.snap_enabled:
            return p
        s = self.snap_step_px if self.snap_step_px > 0 else self.grid_size
        return QtCore.QPointF(round(p.x()/s)*s, round(p.y()/s)*s)
''',

    # ---------------- tools ----------------
    "app/tools/__init__.py": '''
# tools package
''',

    "app/tools/draw.py": r'''
from enum import IntEnum
from PySide6 import QtCore, QtGui, QtWidgets

class DrawMode(IntEnum):
    NONE = 0
    LINE = 1
    RECT = 2
    CIRCLE = 3
    POLYLINE = 4

class DrawController:
    def __init__(self, window, layer):
        self.win = window
        self.layer = layer
        self.mode = DrawMode.NONE
               # temp preview item while drawing
        self.temp_item = None
        self.points = []

    def set_mode(self, mode: DrawMode):
        self.finish()
        self.mode = mode
        self.win.statusBar().showMessage(f"Draw: {mode.name.title()} — click to start, Esc to finish")

    def finish(self):
        if self.temp_item and self.temp_item.scene():
            self.temp_item.scene().removeItem(self.temp_item)
        self.temp_item = None
        self.points = []
        self.mode = DrawMode.NONE

    def on_mouse_move(self, pt_scene: QtCore.QPointF, shift_ortho=False):
        if not self.points:
            return
        p0 = self.points[0]
        p1 = pt_scene
        if shift_ortho:
            dx = abs(p1.x() - p0.x())
            dy = abs(p1.y() - p0.y())
            if dx > dy:
                p1.setY(p0.y())
            else:
                p1.setX(p0.x())

        if self.mode == DrawMode.LINE:
            if self.temp_item is None:
                self.temp_item = QtWidgets.QGraphicsLineItem()
                pen = QtGui.QPen(QtGui.QColor("#7aa2f7")); pen.setCosmetic(True)
                self.temp_item.setPen(pen); self.temp_item.setParentItem(self.layer)
            self.temp_item.setLine(p0.x(), p0.y(), p1.x(), p1.y())

        elif self.mode == DrawMode.RECT:
            if self.temp_item is None:
                self.temp_item = QtWidgets.QGraphicsRectItem()
                pen = QtGui.QPen(QtGui.QColor("#7dcfff")); pen.setCosmetic(True)
                self.temp_item.setPen(pen); self.temp_item.setParentItem(self.layer)
            rect = QtCore.QRectF(p0, p1).normalized()
            self.temp_item.setRect(rect)

        elif self.mode == DrawMode.CIRCLE:
            if self.temp_item is None:
                self.temp_item = QtWidgets.QGraphicsEllipseItem()
                pen = QtGui.QPen(QtGui.QColor("#bb9af7")); pen.setCosmetic(True)
                self.temp_item.setPen(pen); self.temp_item.setParentItem(self.layer)
            r = QtCore.QLineF(p0, p1).length()
            self.temp_item.setRect(p0.x()-r, p0.y()-r, 2*r, 2*r)

        elif self.mode == DrawMode.POLYLINE:
            if self.temp_item is None:
                self.temp_item = QtWidgets.QGraphicsPathItem()
                pen = QtGui.QPen(QtGui.QColor("#9ece6a")); pen.setCosmetic(True)
                self.temp_item.setPen(pen); self.temp_item.setParentItem(self.layer)
            path = QtGui.QPainterPath(self.points[0])
            for pt in self.points[1:]:
                path.lineTo(pt)
            path.lineTo(p1)
            self.temp_item.setPath(path)

    def on_click(self, pt_scene: QtCore.QPointF, shift_ortho=False):
        if self.mode == DrawMode.NONE:
            return False  # not handled
        if not self.points:
            self.points = [pt_scene]
            return False
        # finalize shapes on second click (except polyline: continue until Esc)
        if self.mode in (DrawMode.LINE, DrawMode.RECT, DrawMode.CIRCLE):
            p0 = self.points[0]
            p1 = pt_scene
            if shift_ortho:
                dx = abs(p1.x() - p0.x()); dy = abs(p1.y() - p0.y())
                if dx > dy: p1.setY(p0.y())
                else: p1.setX(p0.x())
            item = None
            if self.mode == DrawMode.LINE:
                item = QtWidgets.QGraphicsLineItem(p0.x(), p0.y(), p1.x(), p1.y())
            elif self.mode == DrawMode.RECT:
                rect = QtCore.QRectF(p0, p1).normalized()
                item = QtWidgets.QGraphicsRectItem(rect)
            elif self.mode == DrawMode.CIRCLE:
                r = QtCore.QLineF(p0, p1).length()
                item = QtWidgets.QGraphicsEllipseItem(p0.x()-r, p0.y()-r, 2*r, 2*r)
            pen = QtGui.QPen(QtGui.QColor("#e0e0e0")); pen.setCosmetic(True)
            item.setPen(pen); item.setZValue(20); item.setParentItem(self.layer)
            self.finish()
            return True
        elif self.mode == DrawMode.POLYLINE:
            if len(self.points) >= 1:
                self.points.append(pt_scene)
                return False
        return False
''',

    "app/tools/dimension.py": r'''
from PySide6 import QtCore, QtGui, QtWidgets

def fmt_ft_inches(px: float, px_per_ft: float) -> str:
    ft = px / px_per_ft if px_per_ft > 0 else 0.0
    sign = '-' if ft < 0 else ''
    ft = abs(ft)
    whole = int(ft)
    inches = (ft - whole) * 12.0
    return f"{sign}{whole}'-{inches:.1f}\""

class LinearDimension(QtWidgets.QGraphicsItemGroup):
    def __init__(self, p0: QtCore.QPointF, p1: QtCore.QPointF, px_per_ft: float):
        super().__init__()
        self.p0 = QtCore.QPointF(p0); self.p1 = QtCore.QPointF(p1)
        self.px_per_ft = px_per_ft
        pen = QtGui.QPen(QtGui.QColor("#e0e0e0")); pen.setCosmetic(True)
        self.line = QtWidgets.QGraphicsLineItem(self.p0.x(), self.p0.y(), self.p1.x(), self.p1.y())
        self.line.setPen(pen); self.addToGroup(self.line)
        mid = (self.p0 + self.p1) / 2
        txt = fmt_ft_inches(QtCore.QLineF(self.p0, self.p1).length(), self.px_per_ft)
        self.label = QtWidgets.QGraphicsSimpleTextItem(txt)
        self.label.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self.label.setBrush(QtGui.QBrush(QtGui.QColor("#c0caf5")))
        self.label.setPos(mid + QtCore.QPointF(8, -8))
        self.addToGroup(self.label)

class DimensionTool:
    def __init__(self, window, overlay_layer):
        self.win = window
        self.layer = overlay_layer
        self.active = False
        self.start_pt = None

    def start(self):
        self.active = True
        self.start_pt = None
        self.win.statusBar().showMessage("Dimension: click first point, then second point")

    def on_mouse_move(self, p: QtCore.QPointF):
        pass

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        if self.start_pt is None:
            self.start_pt = p
            return False
        dim = LinearDimension(self.start_pt, p, self.win.px_per_ft)
        dim.setParentItem(self.layer)
        self.active = False
        self.start_pt = None
        self.win.statusBar().showMessage("Dimension placed")
        return True
''',

    "app/main.py": r'''
import json
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QPointF, QSize
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QToolBar, QGraphicsView, QMenu, QCheckBox)

from app.scene import GridScene, DEFAULT_GRID_SIZE
from app.tools import draw as draw_tools
from app.tools.dimension import DimensionTool

APP_VERSION = "0.6.0-corecad"
APP_TITLE   = f"Auto-Fire {APP_VERSION}"

def ft_to_px(ft: float, px_per_ft: float) -> float: return ft*px_per_ft
def px_to_ft(px: float, px_per_ft: float) -> float: return px/px_per_ft
def fmt_ft_inches(ft: float) -> str:
    sign = '-' if ft < 0 else ''
    ft = abs(ft); whole = int(ft); inches = (ft - whole)*12.0
    return f"{sign}{whole}'-{inches:.1f}\""

class CanvasView(QGraphicsView):
    def __init__(self, scene, sketch_group, overlay_group, window_ref):
        super().__init__(scene)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setMouseTracking(True)
        self.sketch_group = sketch_group
        self.overlay_group = overlay_group
        self.ortho = False
        self.win = window_ref

        # crosshair
        self.cross_v = QtWidgets.QGraphicsLineItem(); self.cross_h = QtWidgets.QGraphicsLineItem()
        pen = QtGui.QPen(QtGui.QColor(130,130,130,160)); pen.setCosmetic(True); pen.setStyle(Qt.DashLine)
        for ln in (self.cross_v,self.cross_h): ln.setPen(pen); ln.setZValue(500); scene.addItem(ln)
        self.show_crosshair = True

    def _update_cross(self, sp: QPointF):
        if not self.show_crosshair: return
        r = self.scene().sceneRect()
        self.cross_v.setLine(sp.x(), r.top(), sp.x(), r.bottom())
        self.cross_h.setLine(r.left(), sp.y(), r.right(), sp.y())
        xft = px_to_ft(sp.x(), self.win.px_per_ft); yft = px_to_ft(sp.y(), self.win.px_per_ft)
        self.win.statusBar().showMessage(f"x={fmt_ft_inches(xft)}  y={fmt_ft_inches(yft)}  scale={self.win.px_per_ft:.2f} px/ft  snap={self.win.snap_label}")

    def wheelEvent(self, e: QtGui.QWheelEvent):
        s = 1.15 if e.angleDelta().y()>0 else 1/1.15
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
        self._update_cross(sp)
        if getattr(self.win, "draw", None): self.win.draw.on_mouse_move(sp, shift_ortho=self.ortho)
        if getattr(self.win, "dim_tool", None): self.win.dim_tool.on_mouse_move(sp)
        super().mouseMoveEvent(e)

    def mousePressEvent(self, e: QtGui.QMouseEvent):
        sp = self.scene().snap(self.mapToScene(e.position().toPoint()))
        if e.button()==Qt.LeftButton:
            if getattr(self.win, "draw", None) and self.win.draw.mode != draw_tools.DrawMode.NONE:
                if self.win.draw.on_click(sp, shift_ortho=self.ortho): self.win.push_history(); e.accept(); return
            if getattr(self.win, "dim_tool", None) and self.win.dim_tool.active:
                if self.win.dim_tool.on_click(sp): e.accept(); return
        elif e.button()==Qt.RightButton:
            self.win.canvas_menu(e.globalPosition().toPoint()); e.accept(); return
        super().mousePressEvent(e)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE); self.resize(1400, 900)
        self.px_per_ft = 12.0
        self.snap_label = "grid"

        # dark theme
        pal = self.palette()
        pal.setColor(pal.Window, QtGui.QColor(32,32,36))
        pal.setColor(pal.Base,   QtGui.QColor(26,26,28))
        pal.setColor(pal.Text,   QtCore.Qt.white); pal.setColor(pal.WindowText, QtCore.Qt.white)
        pal.setColor(pal.Button, QtGui.QColor(48,48,52)); pal.setColor(pal.ButtonText, QtCore.Qt.white)
        self.setPalette(pal)

        self.scene = GridScene(DEFAULT_GRID_SIZE, 0,0,12000,9000)
        self.scene.snap_enabled = True
        self.scene.setSceneRect(0,0,12000,9000)

        # layers
        self.layer_underlay = QtWidgets.QGraphicsItemGroup(); self.layer_underlay.setZValue(-10); self.scene.addItem(self.layer_underlay)
        self.layer_sketch   = QtWidgets.QGraphicsItemGroup(); self.layer_sketch.setZValue(40);   self.scene.addItem(self.layer_sketch)
        self.layer_overlay  = QtWidgets.QGraphicsItemGroup(); self.layer_overlay.setZValue(200); self.scene.addItem(self.layer_overlay)

        self.view = CanvasView(self.scene, self.layer_sketch, self.layer_overlay, self)

        # controllers
        self.draw = draw_tools.DrawController(self, self.layer_sketch)
        self.dim_tool = DimensionTool(self, self.layer_overlay)

        # UI — toolbar
        tb = QToolBar("Main"); tb.setIconSize(QSize(16,16)); self.addToolBar(tb)
        act_line   = QtGui.QAction("Line", self, triggered=lambda: self.draw.set_mode(draw_tools.DrawMode.LINE))
        act_rect   = QtGui.QAction("Rect", self, triggered=lambda: self.draw.set_mode(draw_tools.DrawMode.RECT))
        act_circle = QtGui.QAction("Circle", self, triggered=lambda: self.draw.set_mode(draw_tools.DrawMode.CIRCLE))
        act_poly   = QtGui.QAction("Polyline", self, triggered=lambda: self.draw.set_mode(draw_tools.DrawMode.POLYLINE))
        act_dim    = QtGui.QAction("Dimension", self, triggered=self.start_dimension)
        act_fit    = QtGui.QAction("Fit (F2)", self, triggered=self.fit_view_to_content)
        tb.addActions([act_line, act_rect, act_circle, act_poly]); tb.addSeparator(); tb.addAction(act_dim); tb.addSeparator(); tb.addAction(act_fit)

        # grid/snap panel
        pnl = QWidget(); pv = QHBoxLayout(pnl)
        pv.addWidget(QLabel("Grid(px):"))
        self.chk_grid = QCheckBox("Show Grid"); self.chk_grid.setChecked(True); self.chk_grid.toggled.connect(self.toggle_grid); pv.addWidget(self.chk_grid)
        self.chk_snap = QCheckBox("Snap"); self.chk_snap.setChecked(self.scene.snap_enabled); self.chk_snap.toggled.connect(self.toggle_snap); pv.addWidget(self.chk_snap)
        self.lbl_scale = QLabel("px/ft: 12.0"); pv.addWidget(self.lbl_scale)
        tb.addWidget(pnl)

        # menu
        menubar = self.menuBar()
        m_view = menubar.addMenu("&View")
        m_view.addAction("Set Pixels per Foot…", self.set_px_per_ft)
        m_snap = m_view.addMenu("Snap step")
        for name, inches in [("Grid intersections (default)", 0.0), ('6\"', 6.0), ('12\"',12.0), ('24\"',24.0)]:
            a = QtGui.QAction(name, self, checkable=True)
            a.triggered.connect(lambda _=False, inc=inches: self.set_snap_inches(inc))
            m_snap.addAction(a)
        QtGui.QShortcut(QtGui.QKeySequence("F2"), self, activated=self.fit_view_to_content)

        # layout
        container = QWidget(); lay = QHBoxLayout(container); lay.addWidget(self.view); self.setCentralWidget(container)
        self.statusBar().showMessage("Ready")
        self.history = []; self.history_index = -1
        self.push_history()

    # view toggles
    def toggle_grid(self, on: bool): self.scene.show_grid = bool(on); self.scene.update()
    def toggle_snap(self, on: bool): self.scene.snap_enabled = bool(on)

    def set_px_per_ft(self):
        val, ok = QtWidgets.QInputDialog.getDouble(self, "Scale", "Pixels per foot", self.px_per_ft, 1.0, 1000.0, 2)
        if ok:
            self.px_per_ft = float(val); self.lbl_scale.setText(f"px/ft: {self.px_per_ft:.2f}")
            self._apply_snap_step_from_inches(getattr(self, "snap_step_in", 0.0))

    def _apply_snap_step_from_inches(self, inches: float):
        self.snap_step_in = inches
        if inches <= 0:
            self.scene.snap_step_px = 0.0; self.snap_label = "grid"
        else:
            ft = inches / 12.0
            self.scene.snap_step_px = ft_to_px(ft, self.px_per_ft)
            self.snap_label = f'{int(inches)}"'
        self.statusBar().showMessage(f"Snap: {self.snap_label}")

    def set_snap_inches(self, inches: float):
        self._apply_snap_step_from_inches(inches)

    def change_grid_size(self, v: int):
        self.scene.grid_size = int(v); self.scene.update()

    # history (basic for future undo/redo wiring)
    def serialize_state(self):
        return {"grid":int(self.scene.grid_size), "snap":bool(self.scene.snap_enabled),
                "px_per_ft": float(self.px_per_ft)}

    def push_history(self):
        if self.history_index < len(self.history)-1: self.history = self.history[:self.history_index+1]
        self.history.append(self.serialize_state()); self.history_index += 1

    def start_dimension(self):
        self.dim_tool.start()

    def fit_view_to_content(self):
        rect=self.scene.itemsBoundingRect().adjusted(-100,-100,100,100)
        if rect.isNull(): rect=QtCore.QRectF(0,0,2000,1500)
        self.view.fitInView(rect, Qt.KeepAspectRatio)

    # context menu
    def canvas_menu(self, global_pos):
        m = QMenu(self)
        m.addAction("Fit View (F2)", self.fit_view_to_content)
        m.addSeparator()
        m.addAction("Draw Line", lambda: self.draw.set_mode(draw_tools.DrawMode.LINE))
        m.addAction("Draw Rect", lambda: self.draw.set_mode(draw_tools.DrawMode.RECT))
        m.addAction("Draw Circle", lambda: self.draw.set_mode(draw_tools.DrawMode.CIRCLE))
        m.addAction("Draw Polyline", lambda: self.draw.set_mode(draw_tools.DrawMode.POLYLINE))
        m.addSeparator()
        m.addAction("Dimension", self.start_dimension)
        m.exec(global_pos)

def create_window(): return MainWindow()

def main():
    app = QApplication([])
    w = create_window(); w.show(); app.exec()
''',

    # ---------------- core package ----------------
    "core/__init__.py": '''
# Auto-Fire core package
''',

    "core/logger.py": r'''
import logging
from pathlib import Path

def get_logger(name="autofire"):
    base = Path.home() / "AutoFire" / "logs"
    base.mkdir(parents=True, exist_ok=True)
    log_path = base / "autofire.log"
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(str(log_path), encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger
''',

    "core/error_hook.py": r'''
import sys, traceback, datetime
from pathlib import Path
from PySide6 import QtWidgets

def write_crash_log(tb_text: str) -> str:
    base = Path.home() / "AutoFire" / "logs"
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"startup_error_{datetime.datetime.now():%Y%m%d_%H%M%S}.log"
    try:
        path.write_text(tb_text, encoding="utf-8")
    except Exception:
        pass
    return str(path)

def excepthook(exctype, value, tb):
    tb_text = "".join(traceback.format_exception(exctype, value, tb))
    p = write_crash_log(tb_text)
    try:
        QtWidgets.QMessageBox.critical(None, "Auto-Fire Error", f"{tb_text}\n\nSaved: {p}")
    except Exception:
        pass

def install():
    sys.excepthook = excepthook
''',
}

def write_file(rel_path: str, content: str):
    dst = ROOT / rel_path
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        bak = dst.with_suffix(dst.suffix + f".bak-{STAMP}")
        try:
            dst.replace(bak)
            print(f"backup -> {bak}")
        except Exception as ex:
            print(f"[warn] could not backup {dst}: {ex}")
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(content.lstrip("\n"))
    print(f"wrote   -> {dst}")

def main():
    print("== Auto-Fire v0.6.0-corecad — apply core CAD files ==")
    for p, c in FILES.items():
        write_file(p, c)
    print("\nDone.\nNext:")
    print("  py -3 -m app.boot")
    print("  # or")
    print("  py -3 app\\boot.py")

if __name__ == "__main__":
    main()
