import os, json, zipfile
import sys
# Allow running as `python app\main.py` by fixing sys.path for absolute `app.*` imports
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QPointF, QSize
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QLineEdit, QLabel, QToolBar, QFileDialog,
    QGraphicsView, QGraphicsPathItem, QMenu, QDockWidget, QCheckBox, QSpinBox,
    QComboBox, QMessageBox, QDoubleSpinBox, QPushButton
)

from app.scene import GridScene, DEFAULT_GRID_SIZE
from app.layout import PageFrame, PAGE_SIZES, TitleBlock, ViewportItem
from app.device import DeviceItem
from app import catalog
from app.tools import draw as draw_tools
from app.tools.text_tool import TextTool, MTextTool
from app.tools.freehand import FreehandTool
from app.tools.scale_underlay import ScaleUnderlayRefTool, ScaleUnderlayDragTool, scale_underlay_by_factor
from app.tools.leader import LeaderTool
from app.tools.revision_cloud import RevisionCloudTool
from app.tools.trim_tool import TrimTool
from app.tools.extend_tool import ExtendTool
from app.tools.fillet_tool import FilletTool
from app.tools.measure_tool import MeasureTool
from app.tools.move_tool import MoveTool
from app.tools.fillet_radius_tool import FilletRadiusTool
from app.tools.rotate_tool import RotateTool
from app.tools.mirror_tool import MirrorTool
from app.tools.scale_tool import ScaleTool
from app.tools.chamfer_tool import ChamferTool
from app import dxf_import
try:
    from app.tools.dimension import DimensionTool
except Exception:
    class DimensionTool:
        def __init__(self, *a, **k): self.active=False
        def start(self): self.active=True
        def on_mouse_move(self, *a, **k): pass
        def on_click(self, *a, **k): self.active=False; return True
        def cancel(self): self.active=False

# Optional dialogs (present in recent patches); if missing, we degrade gracefully
try:
    from app.dialogs.coverage import CoverageDialog
except Exception:
    class CoverageDialog(QtWidgets.QDialog):
        def __init__(self, *a, existing=None, **k):
            super().__init__(*a, **k)
            self.setWindowTitle("Coverage")
            lay = QtWidgets.QVBoxLayout(self)
            self.mode = QComboBox(); self.mode.addItems(["none","strobe","speaker","smoke"])
            self.mount = QComboBox(); self.mount.addItems(["ceiling","wall"])
            self.size  = QDoubleSpinBox(); self.size.setRange(0,1000); self.size.setValue(50.0)
            lay.addWidget(QLabel("Mode")); lay.addWidget(self.mode)
            lay.addWidget(QLabel("Mount")); lay.addWidget(self.mount)
            lay.addWidget(QLabel("Size (ft)")); lay.addWidget(self.size)
            bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)
            bb.accepted.connect(self.accept); bb.rejected.connect(self.reject); lay.addWidget(bb)
        def get_settings(self, px_per_ft=12.0):
            m = self.mode.currentText(); mount=self.mount.currentText(); sz=float(self.size.value())
            cov={"mode":m,"mount":mount,"px_per_ft":px_per_ft}
            if m=="none": cov["computed_radius_ft"]=0.0
            elif m=="strobe": cov["computed_radius_ft"]=max(0.0, sz/2.0)
            elif m=="smoke": cov["params"]={"spacing_ft":max(0.0,sz)}; cov["computed_radius_ft"]=max(0.0,sz/2.0)
            else: cov["computed_radius_ft"]=max(0.0,sz)
            return cov
try:
    from app.dialogs.gridstyle import GridStyleDialog
except Exception:
    class GridStyleDialog(QtWidgets.QDialog):
        def __init__(self, *a, scene=None, prefs=None, **k):
            super().__init__(*a, **k); self.scene=scene; self.prefs=prefs or {}
            self.setWindowTitle("Grid Style")
            lay = QtWidgets.QFormLayout(self)
            self.op = QDoubleSpinBox(); self.op.setRange(0.1,1.0); self.op.setSingleStep(0.05); self.op.setValue(float(self.prefs.get("grid_opacity",0.25)))
            self.wd = QDoubleSpinBox(); self.wd.setRange(0.0,3.0); self.wd.setSingleStep(0.1); self.wd.setValue(float(self.prefs.get("grid_width_px",0.0)))
            self.mj = QSpinBox(); self.mj.setRange(1,50); self.mj.setValue(int(self.prefs.get("grid_major_every",5)))
            lay.addRow("Opacity", self.op); lay.addRow("Line width (px)", self.wd); lay.addRow("Major every", self.mj)
            bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)
            bb.accepted.connect(self.accept); bb.rejected.connect(self.reject); lay.addRow(bb)
        def apply(self):
            op=float(self.op.value()); wd=float(self.wd.value()); mj=int(self.mj.value())
            if self.scene: self.scene.set_grid_style(op, wd, mj)
            if self.prefs is not None:
                self.prefs["grid_opacity"]=op; self.prefs["grid_width_px"]=wd; self.prefs["grid_major_every"]=mj
            return op, wd, mj

APP_VERSION = "0.6.8-cad-base"
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
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setMouseTracking(True)
        self.devices_group = devices_group
        self.wires_group   = wires_group
        self.sketch_group  = sketch_group
        self.overlay_group = overlay_group
        self.ortho = False
        self.win   = window_ref
        self.current_proto = None
        self.current_kind  = "other"
        self.ghost = None
        self._mmb_panning = False
        self._mmb_last = QtCore.QPointF()
        # OSNAP toggles (read from prefs via window later)
        self.osnap_end = True
        self.osnap_mid = True
        self.osnap_center = True
        self.osnap_intersect = True
        self.osnap_perp = False
        self.osnap_marker = QtWidgets.QGraphicsEllipseItem(-3, -3, 6, 6)
        pen = QtGui.QPen(QtGui.QColor('#ffd166')); pen.setCosmetic(True)
        brush = QtGui.QBrush(QtGui.QColor('#ffd166'))
        self.osnap_marker.setPen(pen); self.osnap_marker.setBrush(brush)
        self.osnap_marker.setZValue(250)
        self.osnap_marker.setVisible(False)
        self.osnap_marker.setParentItem(self.overlay_group)
        self.osnap_marker.setAcceptedMouseButtons(Qt.NoButton)
        self.osnap_marker.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.osnap_marker.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        # crosshair
        self.cross_v = QtWidgets.QGraphicsLineItem()
        self.cross_h = QtWidgets.QGraphicsLineItem()
        pen_ch = QtGui.QPen(QtGui.QColor(150,150,160,150))
        pen_ch.setCosmetic(True); pen_ch.setStyle(Qt.DashLine)
        self.cross_v.setPen(pen_ch); self.cross_h.setPen(pen_ch)
        self.cross_v.setParentItem(self.overlay_group); self.cross_h.setParentItem(self.overlay_group)
        self.cross_v.setAcceptedMouseButtons(Qt.NoButton)
        self.cross_h.setAcceptedMouseButtons(Qt.NoButton)
        self.cross_v.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.cross_h.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.cross_v.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self.cross_h.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self.show_crosshair = True
        # snap cycling state
        self._snap_candidates = []
        self._snap_index = 0

    def _px_to_scene(self, px: float) -> float:
        a = self.mapToScene(QtCore.QPoint(0, 0))
        b = self.mapToScene(QtCore.QPoint(int(px), int(px)))
        return QtCore.QLineF(a, b).length()

    def _compute_osnap(self, p: QPointF) -> QtCore.QPointF | None:
        # Search nearby items and return nearest enabled snap point
        try:
            thr_scene = self._px_to_scene(12)
            box = QtCore.QRectF(p.x() - thr_scene, p.y() - thr_scene, thr_scene * 2, thr_scene * 2)
            best = None; best_d = 1e18
            items = list(self.scene().items(box))
            # First pass: endpoint/mid/center
            cand = []
            for it in items:
                # skip overlay helpers
                if it is self.osnap_marker:
                    continue
                pts = []
                if isinstance(it, QtWidgets.QGraphicsLineItem):
                    l = it.line()
                    if self.osnap_end:
                        pts += [QtCore.QPointF(l.x1(), l.y1()), QtCore.QPointF(l.x2(), l.y2())]
                    if self.osnap_mid:
                        pts += [QtCore.QPointF((l.x1() + l.x2()) / 2.0, (l.y1() + l.y2()) / 2.0)]
                elif isinstance(it, QtWidgets.QGraphicsRectItem):
                    if self.osnap_center:
                        r = it.rect(); pts = [QtCore.QPointF(r.center())]
                elif isinstance(it, QtWidgets.QGraphicsEllipseItem):
                    if self.osnap_center:
                        r = it.rect(); pts = [QtCore.QPointF(r.center())]
                elif isinstance(it, QtWidgets.QGraphicsPathItem):
                    pth = it.path(); n = pth.elementCount()
                    if n >= 1 and (self.osnap_end or self.osnap_mid):
                        e0 = pth.elementAt(0); eN = pth.elementAt(n - 1)
                        if self.osnap_end:
                            pts += [QtCore.QPointF(e0.x, e0.y), QtCore.QPointF(eN.x, eN.y)]
                        if self.osnap_mid and n >= 2:
                            e1 = pth.elementAt(1)
                            pts += [QtCore.QPointF((e0.x + e1.x) / 2.0, (e0.y + e1.y) / 2.0)]
                for q in pts:
                    d = QtCore.QLineF(p, q).length()
                    if d <= thr_scene:
                        cand.append((d, q))
            # Intersection snaps between nearby lines
            if self.osnap_intersect:
                lines = [it for it in items if isinstance(it, QtWidgets.QGraphicsLineItem)]
                n = len(lines)
                for i in range(n):
                    li = QtCore.QLineF(lines[i].line())
                    for j in range(i+1, n):
                        lj = QtCore.QLineF(lines[j].line())
                        ip = QtCore.QPointF()
                        if li.intersect(lj, ip) != QtCore.QLineF.NoIntersection:
                            d = QtCore.QLineF(p, ip).length()
                            if d <= thr_scene:
                                cand.append((d, ip))
            # Perpendicular from point to line
            if self.osnap_perp:
                for it in items:
                    if not isinstance(it, QtWidgets.QGraphicsLineItem):
                        continue
                    l = QtCore.QLineF(it.line())
                    # project point onto line segment
                    ax, ay, bx, by = l.x1(), l.y1(), l.x2(), l.y2()
                    vx, vy = bx-ax, by-ay
                    wx, wy = p.x()-ax, p.y()-ay
                    denom = vx*vx + vy*vy
                    if denom <= 1e-6:
                        continue
                    t = (wx*vx + wy*vy) / denom
                    if 0.0 <= t <= 1.0:
                        qx, qy = ax + t*vx, ay + t*vy
                        qpt = QtCore.QPointF(qx, qy)
                        d = QtCore.QLineF(p, qpt).length()
                        if d <= thr_scene:
                            cand.append((d, qpt))
            # Sort candidates by distance and deduplicate
            cand.sort(key=lambda x: x[0])
            uniq = []
            seen = set()
            for _, q in cand:
                key = (round(q.x(),2), round(q.y(),2))
                if key in seen: continue
                seen.add(key); uniq.append(q)
            self._snap_candidates = uniq
            self._snap_index = 0
            return uniq[0] if uniq else None
        except Exception:
            return None

    def _apply_osnap(self, p: QPointF) -> QtCore.QPointF:
        sp = QtCore.QPointF(p)
        q = None
        # In paper space, skip object snaps and grid snap entirely
        try:
            if getattr(self.win, 'in_paper_space', False):
                self.osnap_marker.setVisible(False)
                return sp
        except Exception:
            pass
        if self.osnap_end or self.osnap_mid or self.osnap_center:
            q = self._compute_osnap(sp)
        if q is None:
            # Use scene snap only if available (GridScene in model space)
            try:
                sc = self.scene()
                if hasattr(sc, 'snap') and callable(getattr(sc, 'snap')):
                    sp = sc.snap(sp)
            except Exception:
                pass
            self.osnap_marker.setVisible(False)
            return sp
        else:
            self.osnap_marker.setPos(q)
            self.osnap_marker.setVisible(True)
            return q

        

    def set_current_device(self, proto: dict):
        self.current_proto = proto
        self.current_kind  = infer_device_kind(proto)
        self._ensure_ghost()

    def _ensure_ghost(self):
        # clear if not a coverage-driven type
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
            self.ghost.set_coverage({"mode":"speaker","mount":"ceiling",
                                     "computed_radius_ft": 30.0, "px_per_ft": ppf})
        elif self.current_kind == "smoke":
            spacing_ft = float(self.win.prefs.get("default_smoke_spacing_ft", 30.0))
            self.ghost.set_coverage({"mode":"smoke","mount":"ceiling",
                                     "params":{"spacing_ft":spacing_ft},
                                     "computed_radius_ft": spacing_ft/2.0,
                                     "px_per_ft": ppf})
        # placement coverage toggle
        self.ghost.set_coverage_enabled(bool(self.win.prefs.get('show_placement_coverage', True)))

    def _update_crosshair(self, sp: QPointF):
        if not getattr(self, 'show_crosshair', True):
            return
        rect = self.scene().sceneRect()
        self.cross_v.setLine(sp.x(), rect.top(), sp.x(), rect.bottom())
        self.cross_h.setLine(rect.left(), sp.y(), rect.right(), sp.y())
        dx_ft = sp.x()/self.win.px_per_ft
        dy_ft = sp.y()/self.win.px_per_ft
        # Append draw info if applicable
        draw_info = ""
        try:
            if getattr(self.win, 'draw', None) and getattr(self.win.draw, 'points', None):
                pts = self.win.draw.points
                if pts:
                    p0 = pts[-1]
                    vec = QtCore.QLineF(p0, sp)
                    length_ft = vec.length()/self.win.px_per_ft
                    ang = vec.angle()  # 0 to 360 CCW from +x in Qt
                    draw_info = f"  len={length_ft:.2f} ft  ang={ang:.1f}Â°"
        except Exception:
            pass
        self.win.statusBar().showMessage(f"x={dx_ft:.2f} ft   y={dy_ft:.2f} ft   scale={self.win.px_per_ft:.2f} px/ft  snap={self.win.snap_label}{draw_info}")

    def wheelEvent(self, e: QtGui.QWheelEvent):
        s = 1.15 if e.angleDelta().y() > 0 else 1/1.15
        self.scale(s, s)

    def keyPressEvent(self, e: QtGui.QKeyEvent):
        k = e.key()
        if k==Qt.Key_Space:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setCursor(Qt.OpenHandCursor); e.accept(); return
        if k==Qt.Key_Shift: self.ortho=True; e.accept(); return
        # Crosshair toggle moved to 'X' (keyboard shortcut handled in MainWindow too)
        if k==Qt.Key_Escape:
            self.win.cancel_active_tool()
            e.accept(); return
        if k==Qt.Key_Tab:
            # cycle snap candidates
            if getattr(self, '_snap_candidates', None):
                self._snap_index = (self._snap_index + 1) % len(self._snap_candidates)
                q = self._snap_candidates[self._snap_index]
                self.osnap_marker.setPos(q); self.osnap_marker.setVisible(True)
                e.accept(); return
        super().keyPressEvent(e)

    def keyReleaseEvent(self, e: QtGui.QKeyEvent):
        k = e.key()
        if k==Qt.Key_Space:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.unsetCursor(); e.accept(); return
        if k==Qt.Key_Shift: self.ortho=False; e.accept(); return
        super().keyReleaseEvent(e)

    def mouseMoveEvent(self, e: QtGui.QMouseEvent):
        # Middle-mouse panning (standard CAD feel)
        if self._mmb_panning:
            dx = e.position().x() - self._mmb_last.x()
            dy = e.position().y() - self._mmb_last.y()
            self._mmb_last = e.position()
            h = self.horizontalScrollBar(); v = self.verticalScrollBar()
            h.setValue(h.value() - int(dx))
            v.setValue(v.value() - int(dy))
            e.accept(); return

        sp = self.mapToScene(e.position().toPoint())
        sp = self._apply_osnap(sp)
        self.last_scene_pos = sp
        self._update_crosshair(sp)
        if getattr(self.win, "draw", None):
            try: self.win.draw.on_mouse_move(sp, shift_ortho=self.ortho)
            except Exception: pass
        if getattr(self.win, "dim_tool", None):
            try: self.win.dim_tool.on_mouse_move(sp)
            except Exception: pass
        if getattr(self.win, "text_tool", None):
            try: self.win.text_tool.on_mouse_move(sp)
            except Exception: pass
        if getattr(self.win, "mtext_tool", None) and getattr(self.win.mtext_tool, "active", False):
            try: self.win.mtext_tool.on_mouse_move(sp)
            except Exception: pass
        if getattr(self.win, "freehand_tool", None) and getattr(self.win.freehand_tool, "active", False):
            try: self.win.freehand_tool.on_mouse_move(sp)
            except Exception: pass
        if getattr(self.win, "measure_tool", None) and getattr(self.win.measure_tool, "active", False):
            try: self.win.measure_tool.on_mouse_move(sp)
            except Exception: pass
        if getattr(self.win, "leader_tool", None) and getattr(self.win.leader_tool, "active", False):
            try: self.win.leader_tool.on_mouse_move(sp)
            except Exception: pass
        if getattr(self.win, "cloud_tool", None) and getattr(self.win.cloud_tool, "active", False):
            try: self.win.cloud_tool.on_mouse_move(sp)
            except Exception: pass
        if getattr(self.win, "trim_tool", None) and getattr(self.win.trim_tool, "active", False):
            try: self.win.trim_tool.on_mouse_move(sp)
            except Exception: pass
        if getattr(self.win, "extend_tool", None) and getattr(self.win.extend_tool, "active", False):
            try: self.win.extend_tool.on_mouse_move(sp)
            except Exception: pass
        if getattr(self.win, "fillet_tool", None) and getattr(self.win.fillet_tool, "active", False):
            try: self.win.fillet_tool.on_mouse_move(sp)
            except Exception: pass
        if getattr(self.win, "fillet_radius_tool", None) and getattr(self.win.fillet_radius_tool, "active", False):
            try: self.win.fillet_radius_tool.on_mouse_move(sp)
            except Exception: pass
        if getattr(self.win, "move_tool", None) and getattr(self.win.move_tool, "active", False):
            try: self.win.move_tool.on_mouse_move(sp)
            except Exception: pass
        if getattr(self.win, "underlay_drag_tool", None) and getattr(self.win.underlay_drag_tool, "active", False):
            try: self.win.underlay_drag_tool.on_mouse_move(sp)
            except Exception: pass
        if getattr(self.win, "rotate_tool", None) and getattr(self.win.rotate_tool, "active", False):
            try: self.win.rotate_tool.on_mouse_move(sp)
            except Exception: pass
        if getattr(self.win, "mirror_tool", None) and getattr(self.win.mirror_tool, "active", False):
            try: self.win.mirror_tool.on_mouse_move(sp)
            except Exception: pass
        if getattr(self.win, "scale_tool", None) and getattr(self.win.scale_tool, "active", False):
            try: self.win.scale_tool.on_mouse_move(sp)
            except Exception: pass
        if self.ghost:
            self.ghost.setPos(sp)
        super().mouseMoveEvent(e)

    def mousePressEvent(self, e: QtGui.QMouseEvent):
        win = self.win
        sp = self._apply_osnap(self.mapToScene(e.position().toPoint()))
        # If we're in hand-drag mode (Space held), defer to QGraphicsView to pan
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            return super().mousePressEvent(e)
        # Middle mouse starts panning regardless of mode
        if e.button() == Qt.MiddleButton:
            self._mmb_panning = True
            self._mmb_last = e.position()
            self.setCursor(Qt.ClosedHandCursor)
            e.accept(); return
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
            if getattr(win, "text_tool", None) and getattr(win.text_tool, "active", False):
                try:
                    if win.text_tool.on_click(sp):
                        win.push_history(); e.accept(); return
                except Exception:
                    pass
            if getattr(win, "mtext_tool", None) and getattr(win.mtext_tool, "active", False):
                try:
                    if win.mtext_tool.on_click(sp):
                        win.push_history(); e.accept(); return
                except Exception:
                    pass
            if getattr(win, "freehand_tool", None) and getattr(win.freehand_tool, "active", False):
                try:
                    # freehand starts on press; release will commit
                    if win.freehand_tool.on_press(sp):
                        win.push_history(); e.accept(); return
                except Exception:
                    pass
            if getattr(win, "leader_tool", None) and getattr(win.leader_tool, "active", False):
                try:
                    if win.leader_tool.on_click(sp):
                        win.push_history(); e.accept(); return
                except Exception:
                    pass
            if getattr(win, "cloud_tool", None) and getattr(win.cloud_tool, "active", False):
                try:
                    if win.cloud_tool.on_click(sp):
                        e.accept(); return
                except Exception:
                    pass
            if getattr(win, "measure_tool", None) and getattr(win.measure_tool, "active", False):
                try:
                    if win.measure_tool.on_click(sp):
                        e.accept(); return
                except Exception:
                    pass
            if getattr(win, "trim_tool", None) and getattr(win.trim_tool, "active", False):
                try:
                    if win.trim_tool.on_click(sp):
                        win.push_history(); e.accept(); return
                except Exception:
                    pass
            if getattr(win, "extend_tool", None) and getattr(win.extend_tool, "active", False):
                try:
                    if win.extend_tool.on_click(sp):
                        win.push_history(); e.accept(); return
                except Exception:
                    pass
            if getattr(win, "fillet_tool", None) and getattr(win.fillet_tool, "active", False):
                try:
                    if win.fillet_tool.on_click(sp):
                        win.push_history(); e.accept(); return
                except Exception:
                    pass
            if getattr(win, "move_tool", None) and getattr(win.move_tool, "active", False):
                try:
                    if win.move_tool.on_click(sp):
                        win.push_history(); e.accept(); return
                except Exception:
                    pass
            if getattr(win, "rotate_tool", None) and getattr(win.rotate_tool, "active", False):
                try:
                    if win.rotate_tool.on_click(sp):
                        win.push_history(); e.accept(); return
                except Exception:
                    pass
            if getattr(win, "mirror_tool", None) and getattr(win.mirror_tool, "active", False):
                try:
                    if win.mirror_tool.on_click(sp):
                        win.push_history(); e.accept(); return
                except Exception:
                    pass
            if getattr(win, "scale_tool", None) and getattr(win.scale_tool, "active", False):
                try:
                    if win.scale_tool.on_click(sp):
                        win.push_history(); e.accept(); return
                except Exception:
                    pass
            if getattr(win, "chamfer_tool", None) and getattr(win.chamfer_tool, "active", False):
                try:
                    if win.chamfer_tool.on_click(sp):
                        win.push_history(); e.accept(); return
                except Exception:
                    pass
            if getattr(win, "underlay_drag_tool", None) and getattr(win.underlay_drag_tool, "active", False):
                try:
                    if win.underlay_drag_tool.on_click(sp):
                        win.push_history(); e.accept(); return
                except Exception:
                    pass
            if getattr(win, "fillet_radius_tool", None) and getattr(win.fillet_radius_tool, "active", False):
                try:
                    if win.fillet_radius_tool.on_click(sp):
                        win.push_history(); e.accept(); return
                except Exception:
                    pass
            # Prefer selection when clicking over existing selectable content
            try:
                under_items = self.items(e.position().toPoint())
                for it in under_items:
                    if it in (self.cross_v, self.cross_h, self.osnap_marker):
                        continue
                    if isinstance(it, QtWidgets.QGraphicsItem) and (it.flags() & QtWidgets.QGraphicsItem.ItemIsSelectable):
                        return super().mousePressEvent(e)
            except Exception:
                pass
            if self.current_proto:
                d = self.current_proto
                it = DeviceItem(sp.x(), sp.y(), d["symbol"], d["name"], d.get("manufacturer",""), d.get("part_number",""))
                if self.ghost and self.current_kind in ("strobe","speaker","smoke"):
                    it.set_coverage(self.ghost.coverage)
                # Respect global overlay toggle on placement
                try: it.set_coverage_enabled(bool(self.win.show_coverage))
                except Exception: pass
                it.setParentItem(self.devices_group)
                win.push_history(); e.accept(); return
            else:
                # Clear selection when clicking empty space with no active tool
                self.scene().clearSelection()
        elif e.button()==Qt.RightButton:
            win.canvas_menu(e.globalPosition().toPoint()); e.accept(); return
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.MiddleButton and self._mmb_panning:
            self._mmb_panning = False
            self.unsetCursor()
            e.accept(); return
        # If hand-drag mode (Space), let base handle release
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            return super().mouseReleaseEvent(e)
        if e.button() == Qt.LeftButton:
            if getattr(self.win, "freehand_tool", None) and getattr(self.win.freehand_tool, "active", False):
                try:
                    if self.win.freehand_tool.on_release(self.last_scene_pos):
                        self.win.push_history(); e.accept(); return
                except Exception:
                    pass
            if getattr(self.win, "cloud_tool", None) and getattr(self.win.cloud_tool, "active", False):
                try:
                    if self.win.cloud_tool.finish():
                        self.win.push_history(); e.accept(); return
                except Exception:
                    pass
        super().mouseReleaseEvent(e)

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
        self.prefs.setdefault("print_in_per_ft", 0.125)
        self.prefs.setdefault("print_dpi", 300)
        self.prefs.setdefault("page_size", "Letter")
        self.prefs.setdefault("page_orient", "Landscape")
        self.prefs.setdefault("page_margin_in", 0.5)
        self.prefs.setdefault("show_placement_coverage", True)
        save_prefs(self.prefs)

        # Theme
        self.set_theme(self.prefs.get("theme", "dark"))   # apply early

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
        # Allow child items to receive mouse events for selection and dragging
        for grp in (self.layer_underlay, self.layer_sketch, self.layer_wires, self.layer_devices, self.layer_overlay):
            try:
                grp.setHandlesChildEvents(False)
            except Exception:
                pass

        self.view = CanvasView(self.scene, self.layer_devices, self.layer_wires, self.layer_sketch, self.layer_overlay, self)
        # Distinguish model space visually
        try: self.view.setBackgroundBrush(QtGui.QColor(20, 22, 26))
        except Exception: pass
        self.page_frame = None
        self.title_block = None
        # Sheet manager: list of {name, scene}; paper_scene points to current sheet
        self.sheets = []
        self.paper_scene = None
        self.in_paper_space = False
        # Auto-add a default page frame on first run (can be removed via Layout menu)
        if bool(self.prefs.setdefault('auto_page_frame', True)):
            try:
                pf = PageFrame(self.px_per_ft, size_name=self.prefs.get('page_size','Letter'), orientation=self.prefs.get('page_orient','Landscape'), margin_in=self.prefs.get('page_margin_in',0.5))
                pf.setParentItem(self.layer_underlay)
                self.page_frame = pf
            except Exception:
                pass

        # CAD tools
        self.draw = draw_tools.DrawController(self, self.layer_sketch)
        self.dim_tool = DimensionTool(self, self.layer_overlay)
        self.text_tool = TextTool(self, self.layer_sketch)
        self.mtext_tool = MTextTool(self, self.layer_sketch)
        self.freehand_tool = FreehandTool(self, self.layer_sketch)
        self.underlay_ref_tool = ScaleUnderlayRefTool(self, self.layer_underlay)
        self.underlay_drag_tool = ScaleUnderlayDragTool(self, self.layer_underlay)
        self.leader_tool = LeaderTool(self, self.layer_overlay)
        self.cloud_tool = RevisionCloudTool(self, self.layer_overlay)
        self.trim_tool = TrimTool(self)
        self.extend_tool = ExtendTool(self)
        self.fillet_tool = FilletTool(self)
        self.measure_tool = MeasureTool(self, self.layer_overlay)
        self.move_tool = MoveTool(self)
        self.rotate_tool = RotateTool(self)
        self.mirror_tool = MirrorTool(self)
        self.scale_tool = ScaleTool(self)
        self.chamfer_tool = ChamferTool(self)
        self.fillet_radius_tool = FilletRadiusTool(self, self.layer_sketch)

        # Menus
        menubar = self.menuBar()
        m_file = menubar.addMenu("&File")
        m_file.addAction("New", self.new_project, QtGui.QKeySequence.New)
        m_file.addAction("Openâ€¦", self.open_project, QtGui.QKeySequence.Open)
        m_file.addAction("Save Asâ€¦", self.save_project_as, QtGui.QKeySequence.SaveAs)
        m_file.addSeparator()
        imp = m_file.addMenu("Import")
        imp.addAction("DXF Underlayâ€¦", self.import_dxf_underlay)
        imp.addAction("PDF Underlayâ€¦", self.import_pdf_underlay)
        exp = m_file.addMenu("Export")
        exp.addAction("PNGâ€¦", self.export_png)
        exp.addAction("PDFâ€¦", self.export_pdf)
        exp.addAction("Device Schedule (CSV)â€¦", self.export_device_schedule_csv)
        exp.addAction("Place Symbol Legend", self.place_symbol_legend)
        # Settings submenu (moved under File)
        m_settings = m_file.addMenu("Settings")
        theme = m_settings.addMenu("Theme")
        theme.addAction("Dark", lambda: self.set_theme("dark"))
        theme.addAction("Light", lambda: self.set_theme("light"))
        theme.addAction("High Contrast (Dark)", lambda: self.set_theme("high_contrast"))
        m_file.addSeparator()
        m_file.addAction("Quit", self.close, QtGui.QKeySequence.Quit)

        # Edit menu
        m_edit = menubar.addMenu("&Edit")
        act_undo = QtGui.QAction("Undo", self); act_undo.setShortcut(QtGui.QKeySequence.Undo); act_undo.triggered.connect(self.undo); m_edit.addAction(act_undo)
        act_redo = QtGui.QAction("Redo", self); act_redo.setShortcut(QtGui.QKeySequence.Redo); act_redo.triggered.connect(self.redo); m_edit.addAction(act_redo)
        m_edit.addSeparator()
        act_del  = QtGui.QAction("Delete", self); act_del.setShortcut(Qt.Key_Delete); act_del.triggered.connect(self.delete_selection); m_edit.addAction(act_del)

        m_tools = menubar.addMenu("&Tools")
        def add_tool(name, cb):
            act = QtGui.QAction(name, self); act.triggered.connect(cb); m_tools.addAction(act); return act
        self.act_draw_line    = add_tool("Draw Line",    lambda: (setattr(self.draw, 'layer', self.layer_sketch), self.draw.set_mode(draw_tools.DrawMode.LINE)))
        self.act_draw_rect    = add_tool("Draw Rect",    lambda: (setattr(self.draw, 'layer', self.layer_sketch), self.draw.set_mode(draw_tools.DrawMode.RECT)))
        self.act_draw_circle  = add_tool("Draw Circle",  lambda: (setattr(self.draw, 'layer', self.layer_sketch), self.draw.set_mode(draw_tools.DrawMode.CIRCLE)))
        self.act_draw_poly    = add_tool("Draw Polyline",lambda: (setattr(self.draw, 'layer', self.layer_sketch), self.draw.set_mode(draw_tools.DrawMode.POLYLINE)))
        self.act_draw_arc3    = add_tool("Draw Arc (3-Point)", lambda: (setattr(self.draw, 'layer', self.layer_sketch), self.draw.set_mode(draw_tools.DrawMode.ARC3)))
        self.act_draw_wire    = add_tool("Draw Wire",   lambda: self._set_wire_mode())
        self.act_text         = add_tool("Text",        self.start_text)
        self.act_mtext        = add_tool("MText",       self.start_mtext)
        self.act_freehand     = add_tool("Freehand",    self.start_freehand)
        self.act_leader       = add_tool("Leader",      self.start_leader)
        self.act_cloud        = add_tool("Revision Cloud", self.start_cloud)
        m_tools.addSeparator()
        m_tools.addAction("Dimension (D)", self.start_dimension)
        m_tools.addAction("Measure (M)", self.start_measure)
        
        # (Settings moved under File)

        # Layout / Paper Space
        m_layout = menubar.addMenu("&Layout")
        m_layout.addAction("Add Page Frameâ€¦", self.add_page_frame)
        m_layout.addAction("Remove Page Frame", self.remove_page_frame)
        m_layout.addAction("Add/Update Title Blockâ€¦", self.add_or_update_title_block)
        m_layout.addAction("Page Setupâ€¦", self.page_setup_dialog)
        m_layout.addAction("Add Viewport", self.add_viewport)
        m_layout.addSeparator()
        m_layout.addAction("Switch to Paper Space", lambda: self.toggle_paper_space(True))
        m_layout.addAction("Switch to Model Space", lambda: self.toggle_paper_space(False))
        scale_menu = m_layout.addMenu("Print Scale")
        def add_scale(label, inches_per_ft):
            act = QtGui.QAction(label, self)
            act.triggered.connect(lambda v=inches_per_ft: self.set_print_scale(v))
            scale_menu.addAction(act)
        for lbl, v in [("1/16\" = 1'", 1.0/16.0), ("3/32\" = 1'", 3.0/32.0), ("1/8\" = 1'", 1.0/8.0), ("3/16\" = 1'", 3.0/16.0), ("1/4\" = 1'", 0.25), ("3/8\" = 1'", 0.375), ("1/2\" = 1'", 0.5), ("1\" = 1'", 1.0)]:
            add_scale(lbl, v)
        scale_menu.addAction("Customâ€¦", self.set_print_scale_custom)
        # Space badge in status bar (right side)
        # Add scale badge after space badge
        self.scale_badge = QtWidgets.QLabel("")
        self.scale_badge.setStyleSheet("QLabel { color: #c0c0c0; }")
        self.statusBar().addPermanentWidget(self.scale_badge)
        self.space_badge = QtWidgets.QLabel("MODEL SPACE")
        self.space_badge.setStyleSheet("QLabel { color: #7dcfff; font-weight: bold; }")
        self.statusBar().addPermanentWidget(self.space_badge)
        # Sheet Manager dock and export
        self._init_sheet_manager()
        m_layout.addAction("Export Sheets to PDF...", self.export_sheets_pdf)
        # Underlay tools
        m_underlay = m_tools.addMenu("Underlay")
        m_underlay.addAction("Scale by Referenceâ€¦", self.start_underlay_scale_ref)
        m_underlay.addAction("Scale by Factorâ€¦", self.underlay_scale_factor)
        m_underlay.addAction("Scale by Dragâ€¦", self.start_underlay_scale_drag)
        m_underlay.addAction("Center Underlay In View", self.center_underlay_in_view)
        m_underlay.addAction("Move Underlay To Origin", self.move_underlay_to_origin)
        m_underlay.addAction("Reset Underlay Transform", self.reset_underlay_transform)

        # Modify menu
        m_modify = menubar.addMenu("&Modify")
        m_modify.addAction("Offset Selectedâ€¦", self.offset_selected_dialog)
        m_modify.addAction("Trim Lines", self.start_trim)
        m_modify.addAction("Finish Trim", self.finish_trim)
        m_modify.addAction("Extend Lines", self.start_extend)
        m_modify.addAction("Fillet (Corner)", self.start_fillet)
        m_modify.addAction("Fillet (Radius)â€¦", self.start_fillet_radius)
        m_modify.addAction("Move", self.start_move)
        m_modify.addAction("Copy", self.start_copy)
        m_modify.addAction("Rotate", self.start_rotate)
        m_modify.addAction("Mirror", self.start_mirror)
        m_modify.addAction("Scale", self.start_scale)
        m_modify.addAction("Chamferâ€¦", self.start_chamfer)

        # Help menu
        m_help = menubar.addMenu("&Help")
        m_help.addAction("User Guide", self.show_user_guide)
        m_help.addAction("Keyboard Shortcuts", self.show_shortcuts)
        m_help.addSeparator()
        m_help.addAction("About Auto-Fire", self.show_about)

        m_view = menubar.addMenu("&View")
        self.act_view_grid = QtGui.QAction("Grid", self, checkable=True); self.act_view_grid.setChecked(True); self.act_view_grid.toggled.connect(self.toggle_grid); m_view.addAction(self.act_view_grid)
        self.act_view_snap = QtGui.QAction("Snap", self, checkable=True); self.act_view_snap.setChecked(self.scene.snap_enabled); self.act_view_snap.toggled.connect(self.toggle_snap); m_view.addAction(self.act_view_snap)
        self.act_view_cross = QtGui.QAction("Crosshair (X)", self, checkable=True); self.act_view_cross.setChecked(True); self.act_view_cross.toggled.connect(self.toggle_crosshair); m_view.addAction(self.act_view_cross)
        self.act_paperspace = QtGui.QAction("Paper Space Mode", self, checkable=True); self.act_paperspace.setChecked(False); self.act_paperspace.toggled.connect(self.toggle_paper_space); m_view.addAction(self.act_paperspace)
        self.show_coverage = bool(self.prefs.get('show_coverage', True))
        self.act_view_cov = QtGui.QAction("Show Device Coverage", self, checkable=True); self.act_view_cov.setChecked(self.show_coverage); self.act_view_cov.toggled.connect(self.toggle_coverage); m_view.addAction(self.act_view_cov)
        self.act_view_place_cov = QtGui.QAction("Show Coverage During Placement", self, checkable=True)
        self.act_view_place_cov.setChecked(bool(self.prefs.get('show_placement_coverage', True)))
        self.act_view_place_cov.toggled.connect(self.toggle_placement_coverage)
        m_view.addAction(self.act_view_place_cov)
        m_view.addSeparator()
        act_scale = QtGui.QAction("Set Pixels per Footâ€¦", self); act_scale.triggered.connect(self.set_px_per_ft); m_view.addAction(act_scale)
        act_gridstyle = QtGui.QAction("Grid Styleâ€¦", self); act_gridstyle.triggered.connect(self.grid_style_dialog); m_view.addAction(act_gridstyle)
        # Quick snap step presets (guardrail: snap to fixed inch steps or grid)
        snap_menu = m_view.addMenu("Snap Step")
        def add_snap(label, inches):
            act = QtGui.QAction(label, self)
            act.triggered.connect(lambda v=inches: self.set_snap_inches(v))
            snap_menu.addAction(act)
        add_snap("Grid (default)", 0.0)
        add_snap("3 inches", 3.0)
        add_snap("6 inches", 6.0)
        add_snap("12 inches", 12.0)
        add_snap("24 inches", 24.0)

        # Object Snaps (OSNAP) toggles in View menu
        m_view.addSeparator()
        m_osnap = m_view.addMenu("Object Snaps")
        self.act_os_end = QtGui.QAction("Endpoint", self, checkable=True)
        self.act_os_mid = QtGui.QAction("Midpoint", self, checkable=True)
        self.act_os_cen = QtGui.QAction("Center", self, checkable=True)
        self.act_os_int = QtGui.QAction("Intersection", self, checkable=True)
        self.act_os_perp = QtGui.QAction("Perpendicular", self, checkable=True)
        self.act_os_end.setChecked(bool(self.prefs.get('osnap_end', True)))
        self.act_os_mid.setChecked(bool(self.prefs.get('osnap_mid', True)))
        self.act_os_cen.setChecked(bool(self.prefs.get('osnap_center', True)))
        self.act_os_int.setChecked(bool(self.prefs.get('osnap_intersect', True)))
        self.act_os_perp.setChecked(bool(self.prefs.get('osnap_perp', False)))
        self.act_os_end.toggled.connect(lambda v: self._set_osnap('end', v))
        self.act_os_mid.toggled.connect(lambda v: self._set_osnap('mid', v))
        self.act_os_cen.toggled.connect(lambda v: self._set_osnap('center', v))
        self.act_os_int.toggled.connect(lambda v: self._set_osnap('intersect', v))
        self.act_os_perp.toggled.connect(lambda v: self._set_osnap('perp', v))
        m_osnap.addAction(self.act_os_end)
        m_osnap.addAction(self.act_os_mid)
        m_osnap.addAction(self.act_os_cen)
        m_osnap.addAction(self.act_os_int)
        m_osnap.addAction(self.act_os_perp)
        # apply initial states to view
        self._set_osnap('end', self.act_os_end.isChecked())
        self._set_osnap('mid', self.act_os_mid.isChecked())
        self._set_osnap('center', self.act_os_cen.isChecked())
        self._set_osnap('intersect', self.act_os_int.isChecked())
        self._set_osnap('perp', self.act_os_perp.isChecked())

        # No toolbars for base feel; reserve top bar for AutoFire items later

        # Status bar Grid controls
        sb = self.statusBar()
        wrap = QWidget(); lay = QHBoxLayout(wrap); lay.setContentsMargins(6,0,6,0); lay.setSpacing(10)
        # Grid opacity control
        lay.addWidget(QLabel("Grid"))
        self.slider_grid = QtWidgets.QSlider(Qt.Horizontal); self.slider_grid.setMinimum(10); self.slider_grid.setMaximum(100)
        self.slider_grid.setFixedWidth(110)
        cur_op = float(self.prefs.get("grid_opacity", 0.25))
        self.slider_grid.setValue(int(max(10, min(100, round(cur_op*100)))))
        self.lbl_gridp = QLabel(f"{int(self.slider_grid.value())}%")
        lay.addWidget(self.slider_grid); lay.addWidget(self.lbl_gridp)
        # Grid size control
        lay.addWidget(QLabel("Size"))
        self.spin_grid_status = QSpinBox(); self.spin_grid_status.setRange(2, 500); self.spin_grid_status.setValue(self.scene.grid_size)
        self.spin_grid_status.setFixedWidth(70)
        lay.addWidget(self.spin_grid_status)
        sb.addPermanentWidget(wrap)
        def _apply_grid_op(val:int):
            op = max(0.10, min(1.00, val/100.0))
            self.scene.set_grid_style(opacity=op)
            self.prefs["grid_opacity"] = op
            save_prefs(self.prefs)
            self.lbl_gridp.setText(f"{int(val)}%")
        self.slider_grid.valueChanged.connect(_apply_grid_op)
        self.spin_grid_status.valueChanged.connect(self.change_grid_size)

        # Command bar
        cmd_wrap = QWidget(); cmd_l = QHBoxLayout(cmd_wrap); cmd_l.setContentsMargins(6,0,6,0); cmd_l.setSpacing(6)
        cmd_l.addWidget(QLabel("Cmd:"))
        self.cmd = QLineEdit(); self.cmd.setPlaceholderText("Type command (e.g., L, RECT, MOVE)â€¦")
        self.cmd.returnPressed.connect(self._run_command)
        cmd_l.addWidget(self.cmd)
        sb.addPermanentWidget(cmd_wrap, 1)

        # Toolbars removed: keeping top bar clean for AutoFire-specific UI later

        # Left panel (device palette)
        self._build_left_panel()

        # Right dock: Layers & Properties
        self._build_layers_and_props_dock()
        # DXF Layers dock
        self._dxf_layers = {}
        self._build_dxf_layers_dock()

        # Shortcuts
        QtGui.QShortcut(QtGui.QKeySequence("D"), self, activated=self.start_dimension)
        QtGui.QShortcut(QtGui.QKeySequence("Esc"), self, activated=self.cancel_active_tool)
        QtGui.QShortcut(QtGui.QKeySequence("F2"), self, activated=self.fit_view_to_content)

        # Selection change â†’ update Properties
        self.scene.selectionChanged.connect(self._on_selection_changed)

        self.history = []; self.history_index = -1
        self.push_history()
        # Fit view after UI ready
        try:
            QtCore.QTimer.singleShot(0, self.fit_view_to_content)
        except Exception:
            pass

    # ---------- Theme ----------
    def apply_dark_theme(self):
        app = QtWidgets.QApplication.instance()
        pal = app.palette()
        bg   = QtGui.QColor(25,26,28)
        base = QtGui.QColor(32,33,36)
        text = QtGui.QColor(220,220,225)
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
        self._apply_menu_stylesheet(contrast_boost=False)

    def apply_light_theme(self):
        app = QtWidgets.QApplication.instance()
        pal = app.palette()
        bg   = QtGui.QColor(245,246,248)
        base = QtGui.QColor(255,255,255)
        text = QtGui.QColor(20,20,25)
        pal.setColor(QtGui.QPalette.ColorRole.Window, bg)
        pal.setColor(QtGui.QPalette.ColorRole.Base, base)
        pal.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(240,240,245))
        pal.setColor(QtGui.QPalette.ColorRole.Text, text)
        pal.setColor(QtGui.QPalette.ColorRole.WindowText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Button, base)
        pal.setColor(QtGui.QPalette.ColorRole.ButtonText, text)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipBase, base)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(33,99,255))
        pal.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(255,255,255))
        app.setPalette(pal)
        self._apply_menu_stylesheet(contrast_boost=False)

    def apply_high_contrast_theme(self):
        app = QtWidgets.QApplication.instance()
        pal = app.palette()
        bg   = QtGui.QColor(18,18,18)
        base = QtGui.QColor(10,10,12)
        text = QtGui.QColor(245,245,245)
        pal.setColor(QtGui.QPalette.ColorRole.Window, bg)
        pal.setColor(QtGui.QPalette.ColorRole.Base, base)
        pal.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(28,28,32))
        pal.setColor(QtGui.QPalette.ColorRole.Text, text)
        pal.setColor(QtGui.QPalette.ColorRole.WindowText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(26,26,30))
        pal.setColor(QtGui.QPalette.ColorRole.ButtonText, text)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor(30,30,30))
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor(255,255,255))
        pal.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(90,160,255))
        pal.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(0,0,0))
        app.setPalette(pal)
        self._apply_menu_stylesheet(contrast_boost=True)

    def set_theme(self, name: str):
        name = (name or "dark").lower()
        if name == "light": self.apply_light_theme()
        elif name in ("hc","high","high_contrast","high-contrast"): self.apply_high_contrast_theme()
        else: self.apply_dark_theme()
        self.prefs["theme"] = name
        save_prefs(self.prefs)

    def _apply_menu_stylesheet(self, contrast_boost: bool):
        if contrast_boost:
            ss = """
            QMenuBar { background: #0f1113; color: #eaeaea; }
            QMenuBar::item:selected { background: #2f61ff; color: #ffffff; }
            QMenu { background: #14161a; color: #f0f0f0; border: 1px solid #364049; }
            QMenu::item:selected { background: #2f61ff; color: #ffffff; }
            QToolBar { background: #0f1113; border-bottom: 1px solid #364049; }
            QStatusBar { background: #0f1113; color: #cfd8e3; }
            """
        else:
            ss = """
            QMenuBar { background: transparent; }
            QMenu { border: 1px solid rgba(0,0,0,40); }
            """
        self.setStyleSheet(ss)

    # ---------- UI building ----------
    def _build_left_panel(self):
        # Device Palette as dockable panel
        left = QWidget(); ll = QVBoxLayout(left)
        self.search = QLineEdit(); self.search.setPlaceholderText("Search name / part numberâ€¦")
        self.cmb_mfr = QComboBox(); self.cmb_type = QComboBox()
        ll_top = QHBoxLayout(); ll_top.addWidget(QLabel("Manufacturer:")); ll_top.addWidget(self.cmb_mfr)
        ll_typ = QHBoxLayout(); ll_typ.addWidget(QLabel("Type:")); ll_typ.addWidget(self.cmb_type)
        self.list = QListWidget()
        ll.addLayout(ll_top); ll.addLayout(ll_typ); ll.addWidget(self.search); ll.addWidget(self.list)

        self._populate_filters()

        dock = QDockWidget("Device Palette", self)
        dock.setWidget(left)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        # Ensure central widget is just the view
        self.setCentralWidget(self.view)

        self.search.textChanged.connect(self._refresh_device_list)
        self.cmb_mfr.currentIndexChanged.connect(self._refresh_device_list)
        self.cmb_type.currentIndexChanged.connect(self._refresh_device_list)
        self.list.itemClicked.connect(self.choose_device)
        self._refresh_device_list()

        # OSNAP initial states are wired in View â†’ Object Snaps

        # CAD-style shortcuts
        QtGui.QShortcut(QtGui.QKeySequence("L"), self, activated=lambda: (setattr(self.draw,'layer', self.layer_sketch), self.draw.set_mode(draw_tools.DrawMode.LINE)))
        QtGui.QShortcut(QtGui.QKeySequence("R"), self, activated=lambda: (setattr(self.draw,'layer', self.layer_sketch), self.draw.set_mode(draw_tools.DrawMode.RECT)))
        QtGui.QShortcut(QtGui.QKeySequence("P"), self, activated=lambda: (setattr(self.draw,'layer', self.layer_sketch), self.draw.set_mode(draw_tools.DrawMode.POLYLINE)))
        QtGui.QShortcut(QtGui.QKeySequence("A"), self, activated=lambda: (setattr(self.draw,'layer', self.layer_sketch), self.draw.set_mode(draw_tools.DrawMode.ARC3)))
        QtGui.QShortcut(QtGui.QKeySequence("C"), self, activated=lambda: (setattr(self.draw,'layer', self.layer_sketch), self.draw.set_mode(draw_tools.DrawMode.CIRCLE)))
        QtGui.QShortcut(QtGui.QKeySequence("W"), self, activated=self._set_wire_mode)
        QtGui.QShortcut(QtGui.QKeySequence("T"), self, activated=self.start_text)
        QtGui.QShortcut(QtGui.QKeySequence("M"), self, activated=self.start_measure)
        QtGui.QShortcut(QtGui.QKeySequence("O"), self, activated=self.offset_selected_dialog)
        # Crosshair toggle moved to X to free C for Circle
        QtGui.QShortcut(QtGui.QKeySequence("X"), self, activated=lambda: self.toggle_crosshair(not self.view.show_crosshair))

    def _build_layers_and_props_dock(self):
        dock = QDockWidget("Properties", self)
        panel = QWidget(); form = QVBoxLayout(panel); form.setContentsMargins(8,8,8,8); form.setSpacing(6)

        # layer toggles (visibility)
        form.addWidget(QLabel("Layers"))
        self.chk_underlay = QCheckBox("Underlay"); self.chk_underlay.setChecked(True); self.chk_underlay.toggled.connect(lambda v: self.layer_underlay.setVisible(v)); form.addWidget(self.chk_underlay)
        self.chk_sketch   = QCheckBox("Sketch"); self.chk_sketch.setChecked(True);   self.chk_sketch.toggled.connect(lambda v: self.layer_sketch.setVisible(v));     form.addWidget(self.chk_sketch)
        self.chk_wires    = QCheckBox("Wiring"); self.chk_wires.setChecked(True);    self.chk_wires.toggled.connect(lambda v: self.layer_wires.setVisible(v));       form.addWidget(self.chk_wires)
        self.chk_devices  = QCheckBox("Devices"); self.chk_devices.setChecked(True); self.chk_devices.toggled.connect(lambda v: self.layer_devices.setVisible(v));   form.addWidget(self.chk_devices)

        # properties
        form.addSpacing(10); lblp = QLabel("Device Properties"); lblp.setStyleSheet("font-weight:600;"); form.addWidget(lblp)

        grid = QtWidgets.QGridLayout(); grid.setHorizontalSpacing(8); grid.setVerticalSpacing(4)
        r = 0
        grid.addWidget(QLabel("Label"), r, 0); self.prop_label = QLineEdit(); grid.addWidget(self.prop_label, r, 1); r+=1
        grid.addWidget(QLabel("Show Coverage"), r, 0); self.prop_showcov = QCheckBox(); self.prop_showcov.setChecked(True); grid.addWidget(self.prop_showcov, r, 1); r+=1
        grid.addWidget(QLabel("Offset X (ft)"), r, 0); self.prop_offx = QDoubleSpinBox(); self.prop_offx.setRange(-500,500); self.prop_offx.setDecimals(2); grid.addWidget(self.prop_offx, r, 1); r+=1
        grid.addWidget(QLabel("Offset Y (ft)"), r, 0); self.prop_offy = QDoubleSpinBox(); self.prop_offy.setRange(-500,500); self.prop_offy.setDecimals(2); grid.addWidget(self.prop_offy, r, 1); r+=1
        grid.addWidget(QLabel("Mount"), r, 0); self.prop_mount = QComboBox(); self.prop_mount.addItems(["ceiling","wall"]); grid.addWidget(self.prop_mount, r, 1); r+=1
        grid.addWidget(QLabel("Coverage Mode"), r, 0); self.prop_mode = QComboBox(); self.prop_mode.addItems(["none","strobe","speaker","smoke"]); grid.addWidget(self.prop_mode, r, 1); r+=1
        grid.addWidget(QLabel("Candela (strobe)"), r, 0); self.prop_candela = QComboBox(); self.prop_candela.addItems(["(custom)","15","30","75","95","110","135","185"]); grid.addWidget(self.prop_candela, r, 1); r+=1
        grid.addWidget(QLabel("Size (ft)"), r, 0); self.prop_size = QDoubleSpinBox(); self.prop_size.setRange(0,1000); self.prop_size.setDecimals(2); self.prop_size.setSingleStep(1.0); grid.addWidget(self.prop_size, r, 1); r+=1

        form.addLayout(grid)
        self.btn_apply_props = QPushButton("Apply"); form.addWidget(self.btn_apply_props)

        # disable until selection
        self._enable_props(False)

        self.btn_apply_props.clicked.connect(self._apply_props_clicked)
        self.prop_label.editingFinished.connect(self._apply_label_offset_live)
        self.prop_offx.valueChanged.connect(self._apply_label_offset_live)
        self.prop_offy.valueChanged.connect(self._apply_label_offset_live)
        self.prop_mode.currentTextChanged.connect(self._on_mode_changed_props)

        panel.setLayout(form); dock.setWidget(panel); self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.dock_layers_props = dock

    def _enable_props(self, on: bool):
        for w in (self.prop_label, self.prop_offx, self.prop_offy, self.prop_mount, self.prop_mode, self.prop_size, self.btn_apply_props):
            w.setEnabled(on)

    # ---------- DXF layers dock ----------
    def _build_dxf_layers_dock(self):
        dock = QDockWidget("DXF Layers", self)
        self.dxf_panel = QWidget(); v = QVBoxLayout(self.dxf_panel); v.setContentsMargins(8,8,8,8); v.setSpacing(6)
        self.lst_dxf = QtWidgets.QListWidget()
        self.lst_dxf.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        v.addWidget(self.lst_dxf)
        # Controls row
        row1 = QHBoxLayout();
        self.btn_dxf_color = QPushButton("Set Colorâ€¦"); self.btn_dxf_reset = QPushButton("Reset Color")
        row1.addWidget(self.btn_dxf_color); row1.addWidget(self.btn_dxf_reset)
        wrap1 = QWidget(); wrap1.setLayout(row1); v.addWidget(wrap1)
        # Flags row
        row2 = QHBoxLayout();
        self.chk_dxf_lock = QCheckBox("Lock Selected"); self.chk_dxf_print = QCheckBox("Print Selected")
        self.chk_dxf_print.setChecked(True)
        row2.addWidget(self.chk_dxf_lock); row2.addWidget(self.chk_dxf_print)
        wrap2 = QWidget(); wrap2.setLayout(row2); v.addWidget(wrap2)
        dock.setWidget(self.dxf_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.dock_dxf_layers = dock
        self.btn_dxf_color.clicked.connect(self._pick_dxf_color)
        self.btn_dxf_reset.clicked.connect(self._reset_dxf_color)
        self.lst_dxf.itemChanged.connect(self._toggle_dxf_layer)
        self.chk_dxf_lock.toggled.connect(self._lock_dxf_layer)
        self.chk_dxf_print.toggled.connect(self._print_dxf_layer)
        self._refresh_dxf_layers_dock()
        # Tabify with properties dock if available
        if hasattr(self, 'dock_layers_props'):
            try:
                self.tabifyDockWidget(self.dock_layers_props, self.dock_dxf_layers)
            except Exception:
                pass

    def _refresh_dxf_layers_dock(self):
        if not hasattr(self, 'lst_dxf'): return
        self.lst_dxf.blockSignals(True)
        self.lst_dxf.clear()
        for name, grp in sorted((self._dxf_layers or {}).items()):
            it = QListWidgetItem(name)
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
            it.setCheckState(Qt.Checked if grp.isVisible() else Qt.Unchecked)
            self.lst_dxf.addItem(it)
        self.lst_dxf.blockSignals(False)

    def _get_dxf_group(self, name: str):
        return (self._dxf_layers or {}).get(name)

    def _toggle_dxf_layer(self, item: QListWidgetItem):
        name = item.text(); grp = self._get_dxf_group(name)
        if grp is None: return
        grp.setVisible(item.checkState()==Qt.Checked)

    def _pick_dxf_color(self):
        it = self.lst_dxf.currentItem()
        if not it: return
        color = QtWidgets.QColorDialog.getColor(parent=self)
        if not color.isValid(): return
        grp = self._get_dxf_group(it.text())
        if grp is None: return
        pen = QtGui.QPen(color); pen.setCosmetic(True)
        for ch in grp.childItems():
            try:
                if hasattr(ch,'setPen'): ch.setPen(pen)
            except Exception: pass

    def _reset_dxf_color(self):
        it = self.lst_dxf.currentItem()
        if not it: return
        grp = self._get_dxf_group(it.text())
        if grp is None: return
        # Reset to original DXF color if stored
        orig = grp.data(2002)
        col = QtGui.QColor(orig) if orig else QtGui.QColor('#C0C0C0')
        pen = QtGui.QPen(col); pen.setCosmetic(True)
        for ch in grp.childItems():
            try:
                if hasattr(ch,'setPen'): ch.setPen(pen)
            except Exception: pass

    def _current_dxf_group(self):
        it = self.lst_dxf.currentItem()
        return self._get_dxf_group(it.text()) if it else None

    def _lock_dxf_layer(self, on: bool):
        grp = self._current_dxf_group()
        if grp is None: return
        # toggle selectable/movable flags on children
        for ch in grp.childItems():
            try:
                if on:
                    ch.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
                    ch.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
                else:
                    ch.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
                    ch.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
            except Exception:
                pass
        # also toggle on the group
        try:
            grp.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, not on)
            grp.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, not on)
        except Exception:
            pass
        grp.setData(2004, bool(on))

    def _print_dxf_layer(self, on: bool):
        grp = self._current_dxf_group()
        if grp is None: return
        grp.setData(2003, bool(on))

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

    # ---------- view toggles ----------
    def toggle_grid(self, on: bool): self.scene.show_grid = bool(on); self.scene.update()
    def toggle_snap(self, on: bool): self.scene.snap_enabled = bool(on)
    def toggle_crosshair(self, on: bool): self.view.show_crosshair = bool(on)

    def toggle_coverage(self, on: bool):
        self.show_coverage = bool(on)
        for it in self.layer_devices.childItems():
            if isinstance(it, DeviceItem):
                try: it.set_coverage_enabled(self.show_coverage)
                except Exception: pass
        self.prefs['show_coverage'] = self.show_coverage; save_prefs(self.prefs)

    def toggle_placement_coverage(self, on: bool):
        self.prefs['show_placement_coverage'] = bool(on); save_prefs(self.prefs)

    # ---------- command bar ----------
    def _run_command(self):
        txt = (self.cmd.text() or '').strip().lower()
        self.cmd.clear()
        def set_draw(mode):
            setattr(self.draw, 'layer', self.layer_sketch)
            self.draw.set_mode(mode)
        m = {
            'l': lambda: set_draw(draw_tools.DrawMode.LINE), 'line': lambda: set_draw(draw_tools.DrawMode.LINE),
            'r': lambda: set_draw(draw_tools.DrawMode.RECT), 'rect': lambda: set_draw(draw_tools.DrawMode.RECT), 'rectangle': lambda: set_draw(draw_tools.DrawMode.RECT),
            'c': lambda: set_draw(draw_tools.DrawMode.CIRCLE), 'circle': lambda: set_draw(draw_tools.DrawMode.CIRCLE),
            'p': lambda: set_draw(draw_tools.DrawMode.POLYLINE), 'pl': lambda: set_draw(draw_tools.DrawMode.POLYLINE), 'polyline': lambda: set_draw(draw_tools.DrawMode.POLYLINE),
            'a': lambda: set_draw(draw_tools.DrawMode.ARC3), 'arc': lambda: set_draw(draw_tools.DrawMode.ARC3),
            'w': self._set_wire_mode, 'wire': self._set_wire_mode,
            'dim': self.start_dimension, 'd': self.start_dimension,
            'meas': self.start_measure, 'm': self.start_measure,
            'off': self.offset_selected_dialog, 'offset': self.offset_selected_dialog, 'o': self.offset_selected_dialog,
            'tr': self.start_trim, 'trim': self.start_trim,
            'ex': self.start_extend, 'extend': self.start_extend,
            'fi': self.start_fillet, 'fillet': self.start_fillet,
            'mo': self.start_move, 'move': self.start_move,
            'co': self.start_copy, 'copy': self.start_copy,
            'ro': self.start_rotate, 'rotate': self.start_rotate,
            'mi': self.start_mirror, 'mirror': self.start_mirror,
            'sc': self.start_scale, 'scale': self.start_scale,
            'ch': self.start_chamfer, 'chamfer': self.start_chamfer,
        }
        try:
            # If a draw tool is active, try to parse coordinate input
            if getattr(self.draw, 'mode', 0) != 0 and txt:
                pt = self._parse_coord_input(txt)
                if pt is not None:
                    if self.draw.add_point_command(pt):
                        self.push_history()
                    return
            fn = m.get(txt)
            if fn:
                fn()
            else:
                self.statusBar().showMessage(f"Unknown command: {txt}")
        except Exception as ex:
            QMessageBox.critical(self, "Command Error", str(ex))

    def _parse_coord_input(self, s: str) -> QtCore.QPointF | None:
        # Supports: x,y (abs ft), @dx,dy (rel ft), r<ang or @r<ang (polar, ft/deg)
        s = (s or '').strip().lower()
        try:
            base = None
            if self.draw.points:
                base = QtCore.QPointF(self.draw.points[-1])
            else:
                base = QtCore.QPointF(self.view.last_scene_pos)
            ppf = float(self.px_per_ft)
            if s.startswith('@') and '<' in s:
                # relative polar: @r<ang
                r, ang = s[1:].split('<',1); r = float(r); ang=float(ang)
                dx = r*ppf*math.cos(math.radians(ang))
                dy = r*ppf*math.sin(math.radians(ang))
                return QtCore.QPointF(base.x()+dx, base.y()+dy)
            if '<' in s:
                # absolute polar: r<ang from origin (0,0)
                r, ang = s.split('<',1); r=float(r); ang=float(ang)
                dx = r*ppf*math.cos(math.radians(ang))
                dy = r*ppf*math.sin(math.radians(ang))
                return QtCore.QPointF(dx, dy)
            if s.startswith('@') and ',' in s:
                dx, dy = s[1:].split(',',1); dx=float(dx)*ppf; dy=float(dy)*ppf
                return QtCore.QPointF(base.x()+dx, base.y()+dy)
            if ',' in s:
                x, y = s.split(',',1); x=float(x)*ppf; y=float(y)*ppf
                return QtCore.QPointF(x, y)
        except Exception:
            return None
        return None

    # ---------- OSNAP ----------
    def _set_osnap(self, which: str, val: bool):
        if which == 'end': self.view.osnap_end = bool(val)
        elif which == 'mid': self.view.osnap_mid = bool(val)
        elif which == 'center': self.view.osnap_center = bool(val)
        elif which == 'intersect': self.view.osnap_intersect = bool(val)
        elif which == 'perp': self.view.osnap_perp = bool(val)
        # reflect in prefs
        self.prefs[f'osnap_{which}'] = bool(val)
        save_prefs(self.prefs)

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

    # ---------- cancel / esc ----------
    def cancel_active_tool(self):
        # cancel draw tool
        if getattr(self, "draw", None):
            try:
                committing_poly = (getattr(self.draw, "mode", 0) == draw_tools.DrawMode.POLYLINE and len(getattr(self.draw, "points", [])) >= 2)
            except Exception:
                committing_poly = False
            try: self.draw.finish()
            except Exception: pass
            if committing_poly:
                self.push_history()
        # cancel dimension tool
        if getattr(self, "dim_tool", None):
            try:
                if hasattr(self.dim_tool, "cancel"): self.dim_tool.cancel()
                else: self.dim_tool.active=False
            except Exception: pass
        # cancel text tool
        if getattr(self, "text_tool", None):
            try: self.text_tool.cancel()
            except Exception: pass
        # cancel trim tool
        if getattr(self, "trim_tool", None):
            try: self.trim_tool.cancel()
            except Exception: pass
        # cancel extend tool
        if getattr(self, "extend_tool", None):
            try: self.extend_tool.cancel()
            except Exception: pass
        # cancel fillet tool
        if getattr(self, "fillet_tool", None):
            try: self.fillet_tool.cancel()
            except Exception: pass
        # clear device placement
        self.view.current_proto = None
        if self.view.ghost:
            try: self.scene.removeItem(self.view.ghost)
            except Exception: pass
            self.view.ghost = None
        self.statusBar().showMessage("Cancelled")

    # ---------- scene menu ----------
    def canvas_menu(self, global_pos):
        menu = QMenu(self)
        # Determine item under cursor
        view_pt = self.view.mapFromGlobal(global_pos)
        try:
            scene_pt = self.view.mapToScene(view_pt)
        except Exception:
            scene_pt = None
        item_under = None
        if scene_pt is not None:
            try:
                item_under = self.scene.itemAt(scene_pt, self.view.transform())
            except Exception:
                item_under = None

        # Selection actions
        act_sel = None; act_sim = None
        if item_under is not None and (not isinstance(item_under, QtWidgets.QGraphicsItemGroup) or isinstance(item_under, DeviceItem)):
            act_sel = menu.addAction("Select")
            act_sim = menu.addAction("Select Similar")
        act_all = menu.addAction("Select All")
        act_none = menu.addAction("Clear Selection")
        if self.scene.selectedItems():
            menu.addAction("Delete Selection", self.delete_selection)

        # Device-specific when a device is selected
        dev_sel = [it for it in self.scene.selectedItems() if isinstance(it, DeviceItem)]
        if dev_sel:
            menu.addSeparator()
            d = dev_sel[0]
            act_cov = menu.addAction("Coverageâ€¦")
            act_tog = menu.addAction("Toggle Coverage On/Off")
            act_lbl = menu.addAction("Edit Labelâ€¦")

        # Scene actions
        menu.addSeparator()
        act_clear_underlay = menu.addAction("Clear Underlay")

        act = menu.exec(global_pos)
        if act is None:
            return
        if act == act_sel and item_under is not None:
            try: item_under.setSelected(True)
            except Exception: pass
            return
        if act == act_sim and item_under is not None:
            self._select_similar_from(item_under)
            return
        if act == act_all:
            self.scene.clearSelection()
            for it in self.scene.items():
                try:
                    if not isinstance(it, QtWidgets.QGraphicsItemGroup): it.setSelected(True)
                except Exception: pass
            return
        if act == act_none:
            self.scene.clearSelection(); return
        if dev_sel and act in (act_cov, act_tog, act_lbl):
            d = dev_sel[0]
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
            return
        if act == act_clear_underlay:
            self.clear_underlay(); return

    # ---------- history / serialize ----------
    def serialize_state(self):
        devs = []
        for it in self.layer_devices.childItems():
            if isinstance(it, DeviceItem): devs.append(it.to_json())
        # underlay transform
        ut = self.layer_underlay.transform()
        underlay = {
            "m11": ut.m11(), "m12": ut.m12(), "m13": ut.m13(),
            "m21": ut.m21(), "m22": ut.m22(), "m23": ut.m23(),
            "m31": ut.m31(), "m32": ut.m32(), "m33": ut.m33(),
        }
        # DXF layer states
        dxf_layers = {}
        for name, grp in (self._dxf_layers or {}).items():
            # get first child pen color
            color_hex = None
            for ch in grp.childItems():
                try:
                    if hasattr(ch,'pen'):
                        color_hex = ch.pen().color().name()
                        break
                except Exception:
                    pass
            dxf_layers[name] = {
                'visible': bool(grp.isVisible()),
                'locked': bool(grp.data(2004) or False),
                'print': False if grp.data(2003) is False else True,
                'color': color_hex,
                'orig_color': grp.data(2002)
            }
        # sketch geometry
        def _line_json(it: QtWidgets.QGraphicsLineItem):
            l = it.line(); return {"type":"line","x1":l.x1(),"y1":l.y1(),"x2":l.x2(),"y2":l.y2()}
        def _rect_json(it: QtWidgets.QGraphicsRectItem):
            r = it.rect(); return {"type":"rect","x":r.x(),"y":r.y(),"w":r.width(),"h":r.height()}
        def _ellipse_json(it: QtWidgets.QGraphicsEllipseItem):
            r = it.rect(); return {"type":"circle","x":r.center().x(),"y":r.center().y(),"r":r.width()/2.0}
        def _path_json(it: QtWidgets.QGraphicsPathItem):
            p = it.path(); pts=[]
            for i in range(p.elementCount()):
                e = p.elementAt(i); pts.append({"x":e.x, "y":e.y})
            return {"type":"poly","pts":pts}
        def _text_json(it: QtWidgets.QGraphicsSimpleTextItem):
            p = it.pos(); return {"type":"text","x":p.x(),"y":p.y(),"text":it.text()}
        sketch=[]
        for it in self.layer_sketch.childItems():
            if isinstance(it, QtWidgets.QGraphicsLineItem): sketch.append(_line_json(it))
            elif isinstance(it, QtWidgets.QGraphicsRectItem): sketch.append(_rect_json(it))
            elif isinstance(it, QtWidgets.QGraphicsEllipseItem): sketch.append(_ellipse_json(it))
            elif isinstance(it, QtWidgets.QGraphicsPathItem): sketch.append(_path_json(it))
            elif isinstance(it, QtWidgets.QGraphicsSimpleTextItem): sketch.append(_text_json(it))
        # wires
        wires=[]
        for it in self.layer_wires.childItems():
            if isinstance(it, QtWidgets.QGraphicsPathItem):
                p=it.path();
                if p.elementCount()>=2:
                    a=p.elementAt(0); b=p.elementAt(1)
                    wires.append({"ax":a.x, "ay":a.y, "bx":b.x, "by":b.y})
        return {"grid":int(self.scene.grid_size), "snap":bool(self.scene.snap_enabled),
                "px_per_ft": float(self.px_per_ft),
                "snap_step_in": float(self.snap_step_in),
                "grid_opacity": float(self.prefs.get("grid_opacity",0.25)),
                "grid_width_px": float(self.prefs.get("grid_width_px",0.0)),
                "grid_major_every": int(self.prefs.get("grid_major_every",5)),
                "devices":devs,
                "underlay_transform": underlay,
                "dxf_layers": dxf_layers,
                "sketch":sketch,
                "wires":wires}

    def load_state(self, data):
        for it in list(self.layer_devices.childItems()): it.scene().removeItem(it)
        for it in list(self.layer_wires.childItems()): it.scene().removeItem(it)
        for it in list(self.layer_sketch.childItems()): it.scene().removeItem(it)
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
        # underlay transform
        ut = data.get("underlay_transform")
        if ut:
            tr = QtGui.QTransform(ut.get("m11",1), ut.get("m12",0), ut.get("m13",0),
                                  ut.get("m21",0), ut.get("m22",1), ut.get("m23",0),
                                  ut.get("m31",0), ut.get("m32",0), ut.get("m33",1))
            self.layer_underlay.setTransform(tr)
        # restore sketch
        from PySide6 import QtGui
        for s in data.get("sketch", []):
            t = s.get("type")
            if t == "line":
                it = QtWidgets.QGraphicsLineItem(s["x1"], s["y1"], s["x2"], s["y2"])
            elif t == "rect":
                it = QtWidgets.QGraphicsRectItem(s["x"], s["y"], s["w"], s["h"])
            elif t == "circle":
                r = float(s.get("r",0.0)); cx=float(s.get("x",0.0)); cy=float(s.get("y",0.0))
                it = QtWidgets.QGraphicsEllipseItem(cx-r, cy-r, 2*r, 2*r)
            elif t == "poly":
                pts = [QtCore.QPointF(p["x"], p["y"]) for p in s.get("pts", [])]
                if len(pts) < 2: continue
                path = QtGui.QPainterPath(pts[0])
                for p in pts[1:]: path.lineTo(p)
                it = QtWidgets.QGraphicsPathItem(path)
            elif t == "text":
                it = QtWidgets.QGraphicsSimpleTextItem(s.get("text",""))
                it.setPos(float(s.get("x",0.0)), float(s.get("y",0.0)))
                it.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
            else:
                continue
            pen = QtGui.QPen(QtGui.QColor("#e0e0e0")); pen.setCosmetic(True)
            if hasattr(it, 'setPen'):
                it.setPen(pen)
            it.setZValue(20); it.setParentItem(self.layer_sketch)
            it.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
            it.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        # restore wires
        for w in data.get("wires", []):
            a = QtCore.QPointF(float(w.get("ax",0.0)), float(w.get("ay",0.0)))
            b = QtCore.QPointF(float(w.get("bx",0.0)), float(w.get("by",0.0)))
            path = QtGui.QPainterPath(a); path.lineTo(b)
            wi = QtWidgets.QGraphicsPathItem(path)
            pen = QtGui.QPen(QtGui.QColor("#2aa36b")); pen.setCosmetic(True); pen.setWidth(2)
            wi.setPen(pen); wi.setZValue(60); wi.setParentItem(self.layer_wires)
            wi.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
            wi.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)

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
        # Update device properties panel if a device is selected
        d = self._get_selected_device()
        if not d:
            self._enable_props(False)
        else:
            self._enable_props(True)
            # label + offset in ft
            self.prop_label.setText(d._label.text())
            self.prop_showcov.setChecked(bool(getattr(d, 'coverage_enabled', True)))
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
            # strobe candela
            cand = str(cov.get('params',{}).get('candela',''))
            if cand in {"15","30","75","95","110","135","185"}:
                self.prop_candela.setCurrentText(cand)
            else:
                self.prop_candela.setCurrentText("(custom)")
            size_ft = float(cov.get("computed_radius_ft",0.0))*2.0 if mode=="strobe" else (
                      float(cov.get("params",{}).get("spacing_ft",0.0)) if mode=="smoke" else
                      float(cov.get("computed_radius_ft",0.0)))
            self.prop_size.setValue(max(0.0, size_ft))
        # Always update selection highlight for geometry
        self._update_selection_visuals()

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
        d.set_coverage_enabled(bool(self.prop_showcov.isChecked()))
        mode = self.prop_mode.currentText()
        mount = self.prop_mount.currentText()
        sz = float(self.prop_size.value())
        cov = {"mode":mode, "mount":mount, "px_per_ft": self.px_per_ft}
        if mode == "none":
            cov["computed_radius_ft"] = 0.0
        elif mode == "strobe":
            cand_txt = self.prop_candela.currentText()
            if cand_txt != "(custom)":
                try:
                    cand = int(cand_txt)
                    cov.setdefault('params',{})['candela']=cand
                    cov["computed_radius_ft"] = self._strobe_radius_from_candela(cand)
                except Exception:
                    cov["computed_radius_ft"] = max(0.0, sz/2.0)
            else:
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

    def _on_mode_changed_props(self, mode: str):
        # Show candela chooser only for strobe
        want = (mode == 'strobe')
        self.prop_candela.setEnabled(want)

    # ---------- underlay / file ops ----------
    def clear_underlay(self):
        for it in list(self.layer_underlay.childItems()): it.scene().removeItem(it)

    # ---------- selection helpers ----------
    def _select_similar_from(self, base_item: QtWidgets.QGraphicsItem):
        try:
            # Device similarity: match symbol or name
            if isinstance(base_item, DeviceItem):
                sym = getattr(base_item, 'symbol', None)
                name = getattr(base_item, 'name', None)
                for it in self.layer_devices.childItems():
                    if isinstance(it, DeviceItem):
                        if (sym and getattr(it, 'symbol', None) == sym) or (name and getattr(it, 'name', None) == name):
                            it.setSelected(True)
                self._update_selection_visuals()
                return
            # Geometry similarity: same class within the same top-level group under the scene
            top = base_item.parentItem()
            last = base_item
            while top is not None and top.parentItem() is not None:
                last = top
                top = top.parentItem()
            group = last if isinstance(last, QtWidgets.QGraphicsItemGroup) else top
            if group is not None and isinstance(group, QtWidgets.QGraphicsItemGroup):
                items = list(group.childItems())
            else:
                items = [it for it in self.scene.items() if not isinstance(it, QtWidgets.QGraphicsItemGroup)]
            t = type(base_item)
            try:
                base_item.setSelected(True)
            except Exception:
                pass
            for it in items:
                try:
                    if isinstance(it, t):
                        it.setSelected(True)
                except Exception:
                    pass
            self._update_selection_visuals()
        except Exception:
            pass

    # ---------- selection visuals ----------
    def _update_selection_visuals(self):
        hi_pen = QtGui.QPen(QtGui.QColor(66, 160, 255))
        hi_pen.setCosmetic(True); hi_pen.setWidthF(2.0)
        def apply(item, on: bool):
            try:
                if hasattr(item, 'setPen'):
                    if on:
                        if item.data(1001) is None:
                            # store original pen
                            try: item.setData(1001, item.pen())
                            except Exception: item.setData(1001, None)
                        item.setPen(hi_pen)
                    else:
                        op = item.data(1001)
                        if op is not None:
                            try: item.setPen(op)
                            except Exception: pass
                            item.setData(1001, None)
            except Exception:
                pass
        # clear highlights on non-selected geometry
        for layer in (self.layer_sketch, self.layer_wires):
            for it in layer.childItems():
                apply(it, it.isSelected())

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

    # ---------- underlay import ----------
    def import_dxf_underlay(self):
        p, _ = QFileDialog.getOpenFileName(self, "Import DXF Underlay", "", "DXF Files (*.dxf)")
        if not p:
            return
        try:
            bounds, layer_groups = dxf_import.import_dxf_into_group(p, self.layer_underlay, self.px_per_ft)
            if bounds and not bounds.isNull():
                # Expand scene rect to include underlay, then fit
                self.scene.setSceneRect(self.scene.sceneRect().united(bounds.adjusted(-200,-200,200,200)))
                self.view.fitInView(bounds.adjusted(-100,-100,100,100), Qt.KeepAspectRatio)
            self.statusBar().showMessage(f"Imported underlay: {os.path.basename(p)}")
            self._dxf_layers = layer_groups
            self._refresh_dxf_layers_dock()
        except Exception as ex:
            QMessageBox.critical(self, "DXF Import Error", str(ex))

    def import_pdf_underlay(self):
        p,_ = QFileDialog.getOpenFileName(self, "Import PDF Underlay", "", "PDF Files (*.pdf)")
        if not p:
            return
        try:
            from PySide6 import QtPdf, QtPdfWidgets  # type: ignore
        except Exception as ex:
            QMessageBox.critical(self, "PDF Import Error", "QtPdf module not available.\n\nInstall PySide6 with QtPdf support.")
            return
        try:
            doc = QtPdf.QPdfDocument(self)
            st = doc.load(p)
            if st != QtPdf.QPdfDocument.NoError:
                raise RuntimeError("Failed to load PDF")
            page = 0
            sz = doc.pagePointSize(page)
            # Render at a reasonable DPI (96) and then scale via px_per_ft
            dpi = 96.0
            img = QtGui.QImage(int(sz.width()/72.0*dpi), int(sz.height()/72.0*dpi), QtGui.QImage.Format_ARGB32_Premultiplied)
            img.fill(QtGui.QColor(255,255,255))
            painter = QtGui.QPainter(img)
            r = QtCore.QRectF(0,0,img.width(), img.height())
            QtPdf.QPdfDocumentRenderOptions()
            doc.render(painter, page, r)
            painter.end()
            pix = QtGui.QPixmap.fromImage(img)
            item = QtWidgets.QGraphicsPixmapItem(pix)
            item.setOpacity(0.9)
            item.setTransformationMode(Qt.SmoothTransformation)
            item.setParentItem(self.layer_underlay)
            self.statusBar().showMessage(f"Imported PDF underlay: {os.path.basename(p)} (page 1)")
        except Exception as ex:
            QMessageBox.critical(self, "PDF Import Error", str(ex))

    # ---------- edit helpers ----------
    def delete_selection(self):
        sel = self.scene.selectedItems()
        if not sel: return
        for it in sel:
            if isinstance(it, QtWidgets.QGraphicsItemGroup):
                continue
            sc = it.scene()
            if sc: sc.removeItem(it)
        self.push_history()

    # ---------- text / wire ----------
    def start_text(self):
        try:
            self.text_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Text Tool Error", str(ex))

    def _set_wire_mode(self):
        # temporarily direct draw controller to wires layer for wire mode
        self.draw.layer = self.layer_wires
        self.draw.set_mode(draw_tools.DrawMode.WIRE)

    def start_mtext(self):
        try:
            self.mtext_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "MText Tool Error", str(ex))

    def start_freehand(self):
        try:
            self.freehand_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Freehand Tool Error", str(ex))

    def start_leader(self):
        try:
            self.leader_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Leader Tool Error", str(ex))

    def start_cloud(self):
        try:
            self.cloud_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Revision Cloud Error", str(ex))

    # ---------- underlay scaling ----------
    def start_underlay_scale_ref(self):
        try:
            self.underlay_ref_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Underlay Scale (Ref) Error", str(ex))

    def underlay_scale_factor(self):
        val, ok = QtWidgets.QInputDialog.getDouble(self, "Underlay Scale", "Factor", 1.0, 0.001, 1000.0, 4)
        if not ok:
            return
        try:
            scale_underlay_by_factor(self.layer_underlay, float(val), QtCore.QPointF(0,0))
            self.push_history()
            self.statusBar().showMessage(f"Underlay scaled by factor {float(val):.4f}")
        except Exception as ex:
            QMessageBox.critical(self, "Underlay Scale Error", str(ex))

    def start_underlay_scale_drag(self):
        try:
            self.underlay_drag_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Underlay Scale (Drag) Error", str(ex))

    def center_underlay_in_view(self):
        try:
            bounds = self.layer_underlay.childrenBoundingRect()
            if bounds.isNull():
                return
            vc = self.view.mapToScene(self.view.viewport().rect().center())
            # current center of underlay in scene coords
            cur_center = bounds.center() + self.layer_underlay.pos()
            delta = vc - cur_center
            self.layer_underlay.setPos(self.layer_underlay.pos() + delta)
            # ensure sceneRect includes new underlay pos
            ub = self.layer_underlay.mapRectToScene(self.layer_underlay.childrenBoundingRect())
            self.scene.setSceneRect(self.scene.sceneRect().united(ub.adjusted(-200,-200,200,200)))
            self.push_history(); self.statusBar().showMessage("Underlay centered in view")
        except Exception as ex:
            QMessageBox.critical(self, "Center Underlay Error", str(ex))

    def move_underlay_to_origin(self):
        try:
            self.layer_underlay.setPos(0,0)
            ub = self.layer_underlay.mapRectToScene(self.layer_underlay.childrenBoundingRect())
            self.scene.setSceneRect(self.scene.sceneRect().united(ub.adjusted(-200,-200,200,200)))
            self.push_history(); self.statusBar().showMessage("Underlay moved to origin")
        except Exception as ex:
            QMessageBox.critical(self, "Move Underlay Error", str(ex))

    def reset_underlay_transform(self):
        try:
            self.layer_underlay.setTransform(QtGui.QTransform())
            self.layer_underlay.setPos(0,0)
            ub = self.layer_underlay.mapRectToScene(self.layer_underlay.childrenBoundingRect())
            self.scene.setSceneRect(self.scene.sceneRect().united(ub.adjusted(-200,-200,200,200)))
            self.push_history(); self.statusBar().showMessage("Underlay transform reset")
        except Exception as ex:
            QMessageBox.critical(self, "Reset Underlay Error", str(ex))

    def start_measure(self):
        try:
            self.measure_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Measure Tool Error", str(ex))

    # ---------- modify: trim ----------
    def start_trim(self):
        try:
            self.trim_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Trim Tool Error", str(ex))

    def finish_trim(self):
        try:
            self.trim_tool.cancel()
        except Exception:
            pass
    def start_extend(self):
        try:
            self.extend_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Extend Tool Error", str(ex))
    def start_fillet(self):
        try:
            self.fillet_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Fillet Tool Error", str(ex))
    def start_move(self):
        try:
            self.move_tool.start(copy=False)
        except Exception as ex:
            QMessageBox.critical(self, "Move Tool Error", str(ex))
    def start_copy(self):
        try:
            self.move_tool.start(copy=True)
        except Exception as ex:
            QMessageBox.critical(self, "Copy Tool Error", str(ex))
    def start_rotate(self):
        try:
            self.rotate_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Rotate Tool Error", str(ex))
    def start_mirror(self):
        try:
            self.mirror_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Mirror Tool Error", str(ex))
    def start_scale(self):
        try:
            self.scale_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Scale Tool Error", str(ex))
    def start_chamfer(self):
        try:
            self.chamfer_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Chamfer Tool Error", str(ex))
    def start_fillet_radius(self):
        try:
            self.fillet_radius_tool.start()
        except Exception as ex:
            QMessageBox.critical(self, "Fillet (Radius) Error", str(ex))

    # ---------- modify: offset ----------
    def offset_selected_dialog(self):
        dlg = QtWidgets.QDialog(self); dlg.setWindowTitle("Offset Selected")
        form = QtWidgets.QFormLayout(dlg)
        spin = QDoubleSpinBox(); spin.setRange(-1000, 1000); spin.setDecimals(3); spin.setValue(1.0)
        side = QComboBox(); side.addItems(["Right","Left"])  # relative to first segment direction
        dup  = QCheckBox("Create copy (do not modify original)"); dup.setChecked(True)
        units = QLabel("feet")
        wrap = QtWidgets.QHBoxLayout(); wrap.addWidget(spin); wrap.addWidget(units)
        field = QWidget(); field.setLayout(wrap)
        form.addRow("Distance:", field)
        form.addRow("Side:", side)
        form.addRow(dup)
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)
        form.addRow(bb)
        bb.accepted.connect(dlg.accept); bb.rejected.connect(dlg.reject)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return
        dist_ft = float(spin.value()); right = (side.currentText()=="Right"); make_copy = bool(dup.isChecked())
        self._apply_offset_selected(dist_ft, right, make_copy)
        self.push_history()

    def _apply_offset_selected(self, dist_ft: float, right: bool, make_copy: bool):
        import math
        sel = [it for it in self.scene.selectedItems() if isinstance(it, (QtWidgets.QGraphicsLineItem, QtWidgets.QGraphicsRectItem, QtWidgets.QGraphicsEllipseItem, QtWidgets.QGraphicsPathItem))]
        if not sel:
            return
        dpx = dist_ft * self.px_per_ft
        sign = 1.0 if right else -1.0
        def add_flags(it):
            it.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
            it.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
            return it
        for it in sel:
            layer = it.parentItem() or self.layer_sketch
            if isinstance(it, QtWidgets.QGraphicsLineItem):
                l = it.line(); dx = l.x2()-l.x1(); dy=l.y2()-l.y1()
                ln = math.hypot(dx,dy) or 1.0
                nx, ny = sign*(-dy/ln)*dpx, sign*(dx/ln)*dpx
                nl = QtCore.QLineF(l.x1()+nx, l.y1()+ny, l.x2()+nx, l.y2()+ny)
                tgt = QtWidgets.QGraphicsLineItem(nl) if make_copy else it
                if make_copy:
                    tgt.setParentItem(layer)
                pen = tgt.pen() if hasattr(tgt,'pen') else QtGui.QPen(QtGui.QColor("#e0e0e0"))
                pen.setCosmetic(True); tgt.setPen(pen); tgt.setZValue(20); add_flags(tgt)
            elif isinstance(it, QtWidgets.QGraphicsRectItem):
                r = it.rect(); g = sign*dpx
                nr = QtCore.QRectF(r.x()-g, r.y()-g, r.width()+2*g, r.height()+2*g)
                tgt = QtWidgets.QGraphicsRectItem(nr) if make_copy else it
                if make_copy:
                    tgt.setParentItem(layer)
                pen = QtGui.QPen(QtGui.QColor("#e0e0e0")); pen.setCosmetic(True); tgt.setPen(pen); tgt.setZValue(20); add_flags(tgt)
            elif isinstance(it, QtWidgets.QGraphicsEllipseItem):
                r = it.rect(); g = sign*dpx
                nr = QtCore.QRectF(r.x()-g, r.y()-g, r.width()+2*g, r.height()+2*g)
                tgt = QtWidgets.QGraphicsEllipseItem(nr) if make_copy else it
                if make_copy:
                    tgt.setParentItem(layer)
                pen = QtGui.QPen(QtGui.QColor("#e0e0e0")); pen.setCosmetic(True); tgt.setPen(pen); tgt.setZValue(20); add_flags(tgt)
            elif isinstance(it, QtWidgets.QGraphicsPathItem):
                p = it.path();
                if p.elementCount() < 2: continue
                e0 = p.elementAt(0); e1 = p.elementAt(1)
                dx, dy = (e1.x - e0.x), (e1.y - e0.y)
                ln = math.hypot(dx,dy) or 1.0
                nx, ny = sign*(-dy/ln)*dpx, sign*(dx/ln)*dpx
                path = QtGui.QPainterPath()
                for i in range(p.elementCount()):
                    e = p.elementAt(i)
                    if i == 0:
                        path.moveTo(e.x+nx, e.y+ny)
                    else:
                        path.lineTo(e.x+nx, e.y+ny)
                tgt = QtWidgets.QGraphicsPathItem(path) if make_copy else it
                if make_copy:
                    tgt.setParentItem(layer)
                pen = QtGui.QPen(QtGui.QColor("#e0e0e0")); pen.setCosmetic(True); tgt.setPen(pen); tgt.setZValue(20); add_flags(tgt)

    # ---------- export ----------
    def export_png(self):
        p,_ = QFileDialog.getSaveFileName(self, "Export PNG", "", "PNG Image (*.png)")
        if not p:
            return
        if not p.lower().endswith('.png'):
            p += '.png'
        # If a page frame exists, render to exact paper size using print scale
        if self.page_frame and self.page_frame.scene():
            size_name = self.prefs.get('page_size','Letter'); dpi=int(self.prefs.get('print_dpi',300))
            w_in, h_in = PAGE_SIZES.get(size_name, PAGE_SIZES['Letter'])
            if (self.prefs.get('page_orient','Landscape')).lower().startswith('land'):
                w_in, h_in = h_in, w_in
            img = QtGui.QImage(int(w_in*dpi), int(h_in*dpi), QtGui.QImage.Format_ARGB32_Premultiplied)
            img.fill(QtGui.QColor(255,255,255))
            painter = QtGui.QPainter(img)
            painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            rect = self.page_frame.childrenBoundingRect()
            # Temporarily hide DXF layers flagged as non-print
            hidden = []
            for grp in (self._dxf_layers or {}).values():
                if grp.data(2003) is False:
                    hidden.append(grp); grp.setVisible(False)
            s = (dpi*float(self.prefs.get('print_in_per_ft',0.125))) / float(self.px_per_ft)
            # center
            page_rect = QtCore.QRectF(0,0, w_in*dpi, h_in*dpi)
            tx = (page_rect.width() - rect.width()*s)/2
            ty = (page_rect.height() - rect.height()*s)/2
            painter.translate(tx, ty)
            painter.scale(s, s)
            painter.translate(-rect.topLeft())
            self.scene.render(painter, QtCore.QRectF(0,0,rect.width(),rect.height()), rect)
            painter.end()
            for grp in hidden:
                grp.setVisible(True)
            img.save(p)
            self.statusBar().showMessage(f"Exported PNG: {os.path.basename(p)}")
            return
        rect = self.scene.itemsBoundingRect().adjusted(-20,-20,20,20)
        if rect.isNull():
            rect = QtCore.QRectF(0,0,1000,800)
        scale = 2.0
        img = QtGui.QImage(int(rect.width()*scale), int(rect.height()*scale), QtGui.QImage.Format_ARGB32_Premultiplied)
        img.fill(QtGui.QColor(25,26,28))
        painter = QtGui.QPainter(img)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.scale(scale, scale)
        painter.translate(-rect.topLeft())
        self.scene.render(painter, QtCore.QRectF(0,0,rect.width(),rect.height()), rect)
        painter.end()
        img.save(p)
        self.statusBar().showMessage(f"Exported PNG: {os.path.basename(p)}")

    def export_pdf(self):
        p,_ = QFileDialog.getSaveFileName(self, "Export PDF", "", "PDF Document (*.pdf)")
        if not p:
            return
        if not p.lower().endswith('.pdf'):
            p += '.pdf'
        writer = QtGui.QPdfWriter(p)
        dpi = int(self.prefs.get('print_dpi', 300))
        writer.setResolution(dpi)
        # Page setup
        size_name = self.prefs.get('page_size', 'Letter')
        orient = self.prefs.get('page_orient', 'Landscape')
        qsize_map = {
            'Letter': QtGui.QPageSize.Letter,
            'Tabloid': QtGui.QPageSize.Tabloid,
            'A3': QtGui.QPageSize.A3,
            'A2': QtGui.QPageSize.A2,
            'A1': QtGui.QPageSize.A1,
            'A0': QtGui.QPageSize.A0,
            'Arch A': QtGui.QPageSize.ArchA,
            'Arch B': QtGui.QPageSize.ArchB,
            'Arch C': QtGui.QPageSize.ArchC,
            'Arch D': QtGui.QPageSize.ArchD,
            'Arch E': QtGui.QPageSize.ArchE,
        }
        writer.setPageSize(QtGui.QPageSize(qsize_map.get(size_name, QtGui.QPageSize.Letter)))
        writer.setPageOrientation(QtGui.QPageLayout.Landscape if orient.lower().startswith('land') else QtGui.QPageLayout.Portrait)
        painter = QtGui.QPainter(writer)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        if self.page_frame and self.page_frame.scene():
            rect = self.page_frame.childrenBoundingRect()
            hidden = []
            for grp in (self._dxf_layers or {}).values():
                if grp.data(2003) is False:
                    hidden.append(grp); grp.setVisible(False)
            s = (dpi*float(self.prefs.get('print_in_per_ft',0.125))) / float(self.px_per_ft)
            page_rect = writer.pageLayout().paintRectPixels(dpi)
            tx = (page_rect.width() - rect.width()*s)/2
            ty = (page_rect.height() - rect.height()*s)/2
            painter.translate(tx, ty)
            painter.scale(s, s)
            painter.translate(-rect.topLeft())
            self.scene.render(painter, QtCore.QRectF(0,0,rect.width(),rect.height()), rect)
            for grp in hidden:
                grp.setVisible(True)
        else:
            rect = self.scene.itemsBoundingRect().adjusted(-20,-20,20,20)
            if rect.isNull(): rect = QtCore.QRectF(0,0,1000,800)
            page_rect = writer.pageLayout().paintRectPixels(dpi)
            sx = page_rect.width() / rect.width(); sy = page_rect.height() / rect.height(); s = min(sx, sy)
            tx = (page_rect.width() - rect.width()*s)/2; ty = (page_rect.height() - rect.height()*s)/2
            painter.translate(tx, ty)
            painter.scale(s, s)
            painter.translate(-rect.topLeft())
            self.scene.render(painter, QtCore.QRectF(0,0,rect.width(),rect.height()), rect)
        painter.end()
        self.statusBar().showMessage(f"Exported PDF: {os.path.basename(p)}")

    # coverage helpers
    def _strobe_radius_from_candela(self, cand: int) -> float:
        # Try DB first
        try:
            from db import loader as db_loader
            con = db_loader.connect()
            db_loader.ensure_schema(con)
            r = db_loader.strobe_radius_for_candela(con, int(cand))
            con.close()
            if r is not None:
                return float(r)
        except Exception:
            pass
        # Fallback mapping
        table = {15:15.0,30:20.0,75:30.0,95:35.0,110:38.0,135:43.0,185:50.0}
        return float(table.get(int(cand), 25.0))

    # ---------- layout / paperspace ----------
    def add_page_frame(self):
        dlg = QtWidgets.QDialog(self); dlg.setWindowTitle("Add Page Frame")
        form = QtWidgets.QFormLayout(dlg)
        cmb = QComboBox(); cmb.addItems(list(PAGE_SIZES.keys())); cmb.setCurrentText(self.prefs.get('page_size','Letter'))
        ori = QComboBox(); ori.addItems(["Portrait","Landscape"]); ori.setCurrentText(self.prefs.get('page_orient','Landscape'))
        spm = QDoubleSpinBox(); spm.setRange(0.0, 2.0); spm.setSingleStep(0.1); spm.setValue(float(self.prefs.get('page_margin_in',0.5)))
        form.addRow("Size:", cmb); form.addRow("Orientation:", ori); form.addRow("Margin (in):", spm)
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel); form.addRow(bb)
        bb.accepted.connect(dlg.accept); bb.rejected.connect(dlg.reject)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return
        self.prefs['page_size'] = cmb.currentText(); self.prefs['page_orient']=ori.currentText(); self.prefs['page_margin_in']=float(spm.value()); save_prefs(self.prefs)
        if self.page_frame and self.page_frame.scene():
            try: self.scene.removeItem(self.page_frame)
            except Exception: pass
            self.page_frame = None
        pf = PageFrame(self.px_per_ft, size_name=self.prefs['page_size'], orientation=self.prefs['page_orient'], margin_in=self.prefs['page_margin_in'])
        pf.setParentItem(self.layer_underlay)  # keep frame below content
        self.page_frame = pf
        self.statusBar().showMessage("Page frame added")

    def add_or_update_title_block(self):
        # Project metadata dialog
        dlg = QtWidgets.QDialog(self); dlg.setWindowTitle("Title Block")
        form = QtWidgets.QFormLayout(dlg)
        ed_project = QLineEdit(self.prefs.get('proj_project',''))
        ed_address = QLineEdit(self.prefs.get('proj_address',''))
        ed_sheet   = QLineEdit(self.prefs.get('proj_sheet',''))
        ed_date    = QLineEdit(self.prefs.get('proj_date',''))
        ed_by      = QLineEdit(self.prefs.get('proj_by',''))
        form.addRow("Project", ed_project)
        form.addRow("Address", ed_address)
        form.addRow("Sheet", ed_sheet)
        form.addRow("Date", ed_date)
        form.addRow("By", ed_by)
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)
        form.addRow(bb); bb.accepted.connect(dlg.accept); bb.rejected.connect(dlg.reject)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return
        meta = {
            'project': ed_project.text(), 'address': ed_address.text(), 'sheet': ed_sheet.text(), 'date': ed_date.text(), 'by': ed_by.text()
        }
        self.prefs.update({ 'proj_'+k:v for k,v in meta.items() }); save_prefs(self.prefs)
        # Add or update
        if self.title_block and self.title_block.scene():
            self.title_block.set_meta(meta)
        else:
            tb = TitleBlock(self.px_per_ft, size_name=self.prefs.get('page_size','Letter'), orientation=self.prefs.get('page_orient','Landscape'), meta=meta)
            tb.setParentItem(self.layer_underlay)
            self.title_block = tb
        self.statusBar().showMessage("Title block updated")

    def page_setup_dialog(self):
        dlg = QtWidgets.QDialog(self); dlg.setWindowTitle("Page Setup")
        form = QtWidgets.QFormLayout(dlg)
        size = QComboBox(); size.addItems(list(PAGE_SIZES.keys())); size.setCurrentText(self.prefs.get('page_size','Letter'))
        orient = QComboBox(); orient.addItems(["Portrait","Landscape"]); orient.setCurrentText(self.prefs.get('page_orient','Landscape'))
        margin = QDoubleSpinBox(); margin.setRange(0.0, 2.0); margin.setDecimals(2); margin.setSingleStep(0.1); margin.setValue(float(self.prefs.get('page_margin_in',0.5)))
        form.addRow("Size:", size); form.addRow("Orientation:", orient); form.addRow("Margin (in):", margin)
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel); form.addRow(bb)
        bb.accepted.connect(dlg.accept); bb.rejected.connect(dlg.reject)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return
        self.prefs['page_size'] = size.currentText()
        self.prefs['page_orient'] = orient.currentText()
        self.prefs['page_margin_in'] = float(margin.value())
        save_prefs(self.prefs)
        # refresh frame and title block
        if self.page_frame and self.page_frame.scene():
            try:
                self.page_frame.set_params(size_name=self.prefs['page_size'], orientation=self.prefs['page_orient'], margin_in=self.prefs['page_margin_in'], px_per_ft=self.px_per_ft)
            except Exception:
                pass
        if self.title_block and self.title_block.scene():
            try:
                self.layer_underlay.removeFromGroup(self.title_block)
            except Exception:
                pass
            # rebuild title block with same meta
            meta = {
                'project': self.prefs.get('proj_project',''), 'address': self.prefs.get('proj_address',''),
                'sheet': self.prefs.get('proj_sheet',''), 'date': self.prefs.get('proj_date',''), 'by': self.prefs.get('proj_by','')
            }
            tb = TitleBlock(self.px_per_ft, size_name=self.prefs['page_size'], orientation=self.prefs['page_orient'], meta=meta)
            tb.setParentItem(self.layer_underlay)
            self.title_block = tb
        self.statusBar().showMessage("Page setup updated")

    # ---------- paper space / viewports ----------
    def _ensure_paper_scene(self):
        if getattr(self, 'paper_scene', None):
            return
        sc = QtWidgets.QGraphicsScene()
        sc.setBackgroundBrush(QtGui.QColor(250, 250, 250))
        # page frame and title block (reuse prefs)
        pf = PageFrame(self.px_per_ft, size_name=self.prefs.get('page_size','Letter'), orientation=self.prefs.get('page_orient','Landscape'), margin_in=self.prefs.get('page_margin_in',0.5))
        sc.addItem(pf)
        inner = pf._inner.rect()
        vp = ViewportItem(self.scene, inner.adjusted(10, 10, -10, -10), self)
        try:
            mbr = self.scene.itemsBoundingRect()
            if mbr.width() > 0 and mbr.height() > 0 and inner.width() > 0 and inner.height() > 0:
                fx = (mbr.width() / inner.width()) * 1.1
                fy = (mbr.height() / inner.height()) * 1.1
                vp.scale_factor = max(fx, fy)
                vp.src_center = mbr.center()
        except Exception:
            pass
        sc.addItem(vp)
        meta = {
            'project': self.prefs.get('proj_project',''), 'address': self.prefs.get('proj_address',''),
            'sheet': self.prefs.get('proj_sheet',''), 'date': self.prefs.get('proj_date',''), 'by': self.prefs.get('proj_by','')
        }
        tb = TitleBlock(self.px_per_ft, size_name=self.prefs.get('page_size','Letter'), orientation=self.prefs.get('page_orient','Landscape'), meta=meta)
        sc.addItem(tb)
        # Register first sheet if none exists
        if not self.sheets:
            self.sheets.append({"name": "Sheet 1", "scene": sc})
        self.paper_scene = sc
        self._refresh_sheets_list()

    def add_viewport(self):
        if not self.in_paper_space:
            self.toggle_paper_space(True)
        if not self.paper_scene:
            self._ensure_paper_scene()
        # add a new viewport in the center
        rect = QtCore.QRectF(100, 100, 600, 400)
        vp = ViewportItem(self.scene, rect, self)
        try:
            mbr = self.scene.itemsBoundingRect()
            if mbr.width() > 0 and mbr.height() > 0 and rect.width() > 0 and rect.height() > 0:
                fx = (mbr.width() / rect.width()) * 1.1
                fy = (mbr.height() / rect.height()) * 1.1
                vp.scale_factor = max(fx, fy)
                vp.src_center = mbr.center()
        except Exception:
            pass
        self.paper_scene.addItem(vp)
        self.statusBar().showMessage("Viewport added")

    def toggle_paper_space(self, on: bool):
        self.in_paper_space = bool(on)
        if self.in_paper_space:
            self._ensure_paper_scene()
            self.view.setScene(self.paper_scene)
            # Update badges and background
            try:
                if hasattr(self, 'space_badge'):
                    self.space_badge.setText("PAPER SPACE")
                    self.space_badge.setStyleSheet("QLabel { color: #e0af68; font-weight: bold; }")
                if hasattr(self, 'scale_badge'):
                    val = float(self.prefs.get('print_in_per_ft', 0.125))
                    self.scale_badge.setText(f"Scale: {val}\" = 1'")
                self.view.setBackgroundBrush(QtGui.QColor(250, 250, 250))
            except Exception:
                pass
            # Update sheet list selection to current scene
            try:
                self._refresh_sheets_list()
            except Exception:
                pass
        else:
            self.view.setScene(self.scene)
            # Update badges and background
            try:
                if hasattr(self, 'space_badge'):
                    self.space_badge.setText("MODEL SPACE")
                    self.space_badge.setStyleSheet("QLabel { color: #7dcfff; font-weight: bold; }")
                if hasattr(self, 'scale_badge'):
                    self.scale_badge.setText("")
                self.view.setBackgroundBrush(QtGui.QColor(20, 22, 26))
            except Exception:
                pass
        self.fit_view_to_content()

    # ---------- sheet manager ----------
    def _init_sheet_manager(self):
        dock = QtWidgets.QDockWidget("Sheets", self)
        w = QtWidgets.QWidget(); lay = QtWidgets.QVBoxLayout(w)
        self.lst_sheets = QtWidgets.QListWidget()
        btns = QtWidgets.QHBoxLayout()
        b_add = QtWidgets.QPushButton("Add")
        b_ren = QtWidgets.QPushButton("Rename")
        b_del = QtWidgets.QPushButton("Delete")
        b_up  = QtWidgets.QPushButton("Up")
        b_dn  = QtWidgets.QPushButton("Down")
        btns.addWidget(b_add); btns.addWidget(b_ren); btns.addWidget(b_del); btns.addWidget(b_up); btns.addWidget(b_dn)
        lay.addWidget(self.lst_sheets); lay.addLayout(btns)
        dock.setWidget(w)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        # Wire
        b_add.clicked.connect(self.sheet_add)
        b_ren.clicked.connect(self.sheet_rename)
        b_del.clicked.connect(self.sheet_delete)
        b_up.clicked.connect(lambda: self.sheet_move(-1))
        b_dn.clicked.connect(lambda: self.sheet_move(+1))
        self.lst_sheets.currentRowChanged.connect(self.sheet_switch)
        self._refresh_sheets_list()

    def _refresh_sheets_list(self):
        if not hasattr(self, 'lst_sheets'):
            return
        self.lst_sheets.clear()
        for s in self.sheets:
            self.lst_sheets.addItem(s.get("name", "Sheet"))
        if self.paper_scene:
            try:
                idx = next((i for i,s in enumerate(self.sheets) if s.get("scene") is self.paper_scene), 0)
                self.lst_sheets.setCurrentRow(idx)
            except Exception:
                pass

    def sheet_add(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "New Sheet", "Sheet name", text=f"Sheet {len(self.sheets)+1}")
        if not ok:
            return
        sc = QtWidgets.QGraphicsScene(); sc.setBackgroundBrush(QtGui.QColor(250,250,250))
        pf = PageFrame(self.px_per_ft, size_name=self.prefs.get('page_size','Letter'), orientation=self.prefs.get('page_orient','Landscape'), margin_in=self.prefs.get('page_margin_in',0.5))
        sc.addItem(pf)
        tb = TitleBlock(self.px_per_ft, size_name=self.prefs.get('page_size','Letter'), orientation=self.prefs.get('page_orient','Landscape'), meta={})
        sc.addItem(tb)
        self.sheets.append({"name": name or "Sheet", "scene": sc})
        self._refresh_sheets_list()

    def sheet_rename(self):
        idx = self.lst_sheets.currentRow()
        if idx < 0 or idx >= len(self.sheets):
            return
        cur = self.sheets[idx]["name"]
        name, ok = QtWidgets.QInputDialog.getText(self, "Rename Sheet", "New name", text=cur)
        if ok and name:
            self.sheets[idx]["name"] = name
            self._refresh_sheets_list()

    def sheet_delete(self):
        idx = self.lst_sheets.currentRow()
        if idx < 0 or idx >= len(self.sheets):
            return
        if len(self.sheets) <= 1:
            QtWidgets.QMessageBox.warning(self, "Sheets", "At least one sheet is required.")
            return
        del self.sheets[idx]
        if idx >= len(self.sheets):
            idx = len(self.sheets)-1
        self.paper_scene = self.sheets[idx]["scene"]
        if self.in_paper_space:
            self.view.setScene(self.paper_scene)
        self._refresh_sheets_list()

    def sheet_move(self, delta: int):
        idx = self.lst_sheets.currentRow()
        j = idx + int(delta)
        if idx < 0 or j < 0 or j >= len(self.sheets):
            return
        self.sheets[idx], self.sheets[j] = self.sheets[j], self.sheets[idx]
        self._refresh_sheets_list()
        self.lst_sheets.setCurrentRow(j)

    def sheet_switch(self, idx: int):
        if idx < 0 or idx >= len(self.sheets):
            return
        self.paper_scene = self.sheets[idx]["scene"]
        if self.in_paper_space:
            self.view.setScene(self.paper_scene)

    def export_sheets_pdf(self):
        if not self.sheets:
            QtWidgets.QMessageBox.information(self, "Export", "No sheets to export.")
            return
        p, _ = QFileDialog.getSaveFileName(self, "Export Sheets to PDF", "", "PDF Files (*.pdf)")
        if not p:
            return
        try:
            # Prepare writer
            writer = QtGui.QPdfWriter(p)
            writer.setResolution(int(self.prefs.get('print_dpi', 300)))
            painter = QtGui.QPainter(writer)
            first = True
            for sheet in self.sheets:
                sc = sheet["scene"]
                # Set page size from prefs
                size_in = PAGE_SIZES.get(self.prefs.get('page_size','Letter'), PAGE_SIZES['Letter'])
                orient = self.prefs.get('page_orient','Landscape')
                if (orient or 'Landscape').lower().startswith('land'):
                    w_in, h_in = size_in[1], size_in[0]
                else:
                    w_in, h_in = size_in
                w_mm = w_in * 25.4; h_mm = h_in * 25.4
                page_size = QtGui.QPageSize(QtCore.QSizeF(w_mm, h_mm), QtGui.QPageSize.Millimeter)
                writer.setPageSize(page_size)
                if not first:
                    writer.newPage()
                first = False
                target = QtCore.QRectF(0, 0, writer.width(), writer.height())
                sc.render(painter, target, sc.itemsBoundingRect())
            painter.end()
            self.statusBar().showMessage(f"Exported {len(self.sheets)} sheet(s) to PDF")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Export", f"Failed to export PDF: {e}")

    def remove_page_frame(self):
        if self.page_frame and self.page_frame.scene():
            try: self.scene.removeItem(self.page_frame)
            except Exception: pass
            self.page_frame = None
            self.statusBar().showMessage("Page frame removed")

    def set_print_scale(self, inches_per_ft: float):
        self.prefs['print_in_per_ft'] = float(inches_per_ft); save_prefs(self.prefs)
        self.statusBar().showMessage(f"Print scale set: {inches_per_ft}\" = 1'-0\"")
        # Update scale badge in paper space
        try:
            if self.in_paper_space and hasattr(self, 'scale_badge'):
                self.scale_badge.setText(f"Scale: {inches_per_ft}\" = 1'")
        except Exception:
            pass

    def set_print_scale_custom(self):
        val, ok = QtWidgets.QInputDialog.getDouble(self, "Custom Print Scale", "Inches per foot", float(self.prefs.get('print_in_per_ft',0.125)), 0.01, 12.0, 3)
        if ok:
            self.set_print_scale(val)

    # ---------- help / about ----------
    def show_user_guide(self):
        self._show_text_dialog("User Guide", _USER_GUIDE_TEXT)

    def show_shortcuts(self):
        self._show_text_dialog("Keyboard Shortcuts", _SHORTCUTS_TEXT)

    def show_about(self):
        txt = f"Auto-Fire CAD Base\nVersion: {APP_VERSION}\n\nA lightweight CAD base inspired by LibreCAD, with paper space and DXF/PDF underlays."
        self._show_text_dialog("About Auto-Fire", txt)

    def _show_text_dialog(self, title: str, text: str):
        dlg = QtWidgets.QDialog(self); dlg.setWindowTitle(title); dlg.resize(720, 480)
        lay = QtWidgets.QVBoxLayout(dlg)
        edit = QtWidgets.QTextEdit(); edit.setReadOnly(True); edit.setPlainText(text)
        lay.addWidget(edit)
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        bb.rejected.connect(dlg.reject); bb.accepted.connect(dlg.accept)
        lay.addWidget(bb)
        dlg.exec()

    def export_device_schedule_csv(self):
        p,_ = QFileDialog.getSaveFileName(self, "Export Device Schedule", "", "CSV Files (*.csv)")
        if not p:
            return
        if not p.lower().endswith('.csv'):
            p += '.csv'
        import csv
        # Count devices by model/name/symbol
        rows = []
        counts = {}
        for it in self.layer_devices.childItems():
            if isinstance(it, DeviceItem):
                key = (it.name, it.symbol, getattr(it, 'manufacturer',''), getattr(it, 'part_number',''))
                counts[key] = counts.get(key, 0) + 1
        try:
            with open(p, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['Name','Symbol','Manufacturer','Model','Qty'])
                for (name, sym, mfr, model), qty in sorted(counts.items()):
                    w.writerow([name, sym, mfr, model, qty])
            self.statusBar().showMessage(f"Exported schedule: {os.path.basename(p)}")
        except Exception as ex:
            QMessageBox.critical(self, "Export CSV Error", str(ex))

    def place_symbol_legend(self):
        # Counts by name/symbol and places a simple table on overlay
        counts = {}
        for it in self.layer_devices.childItems():
            if isinstance(it, DeviceItem):
                key = (it.name, it.symbol)
                counts[key] = counts.get(key, 0) + 1
        if not counts:
            QMessageBox.information(self, "Legend", "No devices to list.")
            return
        # Place near current view center
        try:
            vc = self.view.mapToScene(self.view.viewport().rect().center())
            x0, y0 = vc.x() - 150, vc.y() - 100
        except Exception:
            x0, y0 = 50, 50
        row_h = 18
        header = QtWidgets.QGraphicsSimpleTextItem("Legend: Device Counts")
        header.setBrush(QtGui.QBrush(QtGui.QColor("#e0e0e0")))
        header.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        header.setPos(x0, y0)
        header.setParentItem(self.layer_overlay)
        i = 1
        for (name, sym), qty in sorted(counts.items()):
            t = QtWidgets.QGraphicsSimpleTextItem(f"{sym}  {name}  x {qty}")
            t.setBrush(QtGui.QBrush(QtGui.QColor("#e0e0e0")))
            t.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
            t.setPos(x0, y0 + i*row_h)
            t.setParentItem(self.layer_overlay)
            i += 1
        self.statusBar().showMessage("Placed symbol legend")

# Inline help content (can be moved to a file later)
_USER_GUIDE_TEXT = """
Auto-Fire CAD Base â€” User Guide (Quick)

â€¢ Pan: Hold Space + Left Drag, or Middle-mouse Drag
â€¢ Zoom: Mouse wheel
â€¢ Select: Click items, or Drag a box in empty space
â€¢ Delete: Del key or Edit â†’ Delete

Draw (Tools menu): Line, Rect, Circle, Polyline, Arc (3â€‘Point), Wire, Text

Modify (Modify menu): Offset, Trim, Extend, Fillet (Corner), Move, Copy, Rotate, Mirror, Scale, Chamfer

Measure/Dimension: Tools â†’ Measure, Dimension (D)

Snaps: View â†’ Object Snaps (Endpoint, Midpoint, Center)

Underlays: File â†’ Import â†’ DXF/PDF Underlay

Paper Space: Layout â†’ Add Page Frame, Print Scale presets, Export PNG/PDF

Settings: File â†’ Settings â†’ Theme
"""

_SHORTCUTS_TEXT = """
Keyboard Shortcuts

â€¢ L Line
â€¢ R Rect
â€¢ C Circle
â€¢ P Polyline
â€¢ A Arc (3â€‘Point)
â€¢ W Wire
â€¢ T Text
â€¢ M Measure
â€¢ O Offset
â€¢ D Dimension
â€¢ X Toggle Crosshair
â€¢ Esc Cancel/Finish
â€¢ F2 Fit View
"""

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



