import csv
import json
import math
import os
import sys

# Allow running as `python app\main.py` by fixing sys.path for absolute `app.*` imports
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QPointF, QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDockWidget,
    QDoubleSpinBox,
    QFileDialog,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from app import catalog, dxf_import
from app.device import DeviceItem
from app.layout import PageFrame, TitleBlock, ViewportItem
from app.scene import DEFAULT_GRID_SIZE, GridScene
from app.tools import draw as draw_tools
from app.tools.chamfer_tool import ChamferTool
from app.tools.extend_tool import ExtendTool
from app.tools.fillet_radius_tool import FilletRadiusTool
from app.tools.fillet_tool import FilletTool
from app.tools.freehand import FreehandTool
from app.tools.leader import LeaderTool
from app.tools.measure_tool import MeasureTool
from app.tools.mirror_tool import MirrorTool
from app.tools.move_tool import MoveTool
from app.tools.revision_cloud import RevisionCloudTool
from app.tools.rotate_tool import RotateTool
from app.tools.scale_tool import ScaleTool
from app.tools.scale_underlay import (
    ScaleUnderlayDragTool,
    ScaleUnderlayRefTool,
    scale_underlay_by_factor,
)
from app.tools.text_tool import MTextTool, TextTool
from app.tools.trim_tool import TrimTool
from app.tools.wire_tool import WireTool
from db import loader as db_loader

# Optional dialogs (present in recent patches); if missing, we degrade gracefully
try:
    from app.tools.dimension import DimensionTool
except Exception:

    class DimensionTool:
        def __init__(self, *a, **k):
            self.active = False

        def start(self):
            self.active = True

        def on_mouse_move(self, *a, **k):
            pass

        def on_click(self, *a, **k):
            self.active = False
            return True

        def cancel(self):
            self.active = False


# Optional dialogs (present in recent patches); if missing, we degrade gracefully
try:
    from app.dialogs.coverage import CoverageDialog
except Exception:

    class CoverageDialog(QtWidgets.QDialog):
        def __init__(self, *a, existing=None, **k):
            super().__init__(*a, **k)
            self.setWindowTitle("Coverage")
            lay = QtWidgets.QVBoxLayout(self)
            self.mode = QComboBox()
            self.mode.addItems(["none", "strobe", "speaker", "smoke"])
            self.mount = QComboBox()
            self.mount.addItems(["ceiling", "wall"])
            self.size_spin = QDoubleSpinBox()
            self.size_spin.setRange(0, 1000)
            self.size_spin.setValue(50.0)
            lay.addWidget(QLabel("Mode"))
            lay.addWidget(self.mode)
            lay.addWidget(QLabel("Mount"))
            lay.addWidget(self.mount)
            lay.addWidget(QLabel("Size (ft)"))
            lay.addWidget(self.size_spin)
            bb = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok
                | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            bb.accepted.connect(self.accept)
            bb.rejected.connect(self.reject)
            lay.addWidget(bb)

        def get_settings(self, px_per_ft=12.0):
            m = self.mode.currentText()
            mount = self.mount.currentText()
            sz = float(self.size_spin.value())
            cov = {"mode": m, "mount": mount, "px_per_ft": px_per_ft}
            if m == "none":
                cov["computed_radius_ft"] = 0.0
            elif m == "strobe":
                cov["computed_radius_ft"] = max(0.0, sz / 2.0)
            elif m == "smoke":
                cov["params"] = {"spacing_ft": max(0.0, sz)}
                cov["computed_radius_ft"] = max(0.0, sz / 2.0)
            else:
                cov["computed_radius_ft"] = max(0.0, sz)
            return cov


try:
    from app.dialogs.gridstyle import GridStyleDialog
except Exception:

    class GridStyleDialog(QtWidgets.QDialog):
        def __init__(self, *a, scene=None, prefs=None, **k):
            super().__init__(*a, **k)
            self.scene = scene
            self.prefs = prefs or {}
            self.setWindowTitle("Grid Style")
            lay = QtWidgets.QFormLayout(self)
            self.op = QDoubleSpinBox()
            self.op.setRange(0.1, 1.0)
            self.op.setSingleStep(0.05)
            self.op.setValue(float(self.prefs.get("grid_opacity", 0.25)))
            self.wd = QDoubleSpinBox()
            self.wd.setRange(0.0, 3.0)
            self.wd.setSingleStep(0.1)
            self.wd.setValue(float(self.prefs.get("grid_width_px", 0.0)))
            self.mj = QSpinBox()
            self.mj.setRange(1, 50)
            self.mj.setValue(int(self.prefs.get("grid_major_every", 5)))
            lay.addRow("Opacity", self.op)
            lay.addRow("Line width (px)", self.wd)
            lay.addRow("Major every", self.mj)
            bb = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok
                | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            bb.accepted.connect(self.accept)
            bb.rejected.connect(self.reject)
            lay.addRow(bb)

        def apply(self):
            op = float(self.op.value())
            wd = float(self.wd.value())
            mj = int(self.mj.value())
            if self.scene:
                self.scene.set_grid_style(op, wd, mj)
            if self.prefs is not None:
                self.prefs["grid_opacity"] = op
                self.prefs["grid_width_px"] = wd
                self.prefs["grid_major_every"] = mj
            return op, wd, mj


# FACP Wizard Dialog
try:
    from app.dialogs.facp_wizard import FACPWizardDialog
except Exception:

    class FACPWizardDialog:
        def __init__(self, *args, **kwargs):
            pass

        def exec(self):
            return False


try:
    from app.dialogs.wire_spool import WireSpoolDialog
except Exception:

    class WireSpoolDialog(QtWidgets.QDialog):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.setWindowTitle("Wire Spool")
            lay = QtWidgets.QVBoxLayout(self)
            lay.addWidget(QtWidgets.QLabel("Wire selection will be implemented here."))
            bb = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok
                | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            bb.accepted.connect(self.accept)
            bb.rejected.connect(self.reject)
            lay.addWidget(bb)


try:
    from app.dialogs.connections_tree import ConnectionsTree
except Exception:

    class ConnectionsTree(QtWidgets.QDockWidget):
        def __init__(self, *a, **k):
            super().__init__("Connections", *a, **k)
            self.setWidget(QtWidgets.QLabel("Connections tree will be implemented here."))

        def get_connections(self):
            # Return empty connections data for fallback implementation
            return []


try:
    from app.dialogs.settings_dialog import SettingsDialog
except Exception:

    class SettingsDialog(QtWidgets.QDialog):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.setWindowTitle("Settings")
            lay = QtWidgets.QVBoxLayout(self)
            lay.addWidget(QtWidgets.QLabel("Settings will be implemented here."))
            bb = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok
                | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            bb.accepted.connect(self.accept)
            bb.rejected.connect(self.reject)
            lay.addWidget(bb)


try:
    from app.dialogs.layer_manager import LayerManagerDialog
except Exception:

    class LayerManagerDialog(QtWidgets.QDialog):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.setWindowTitle("Layer Manager")
            lay = QtWidgets.QVBoxLayout(self)
            lay.addWidget(QtWidgets.QLabel("Layer Manager will be implemented here."))
            bb = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok
                | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            bb.accepted.connect(self.accept)
            bb.rejected.connect(self.reject)
            lay.addWidget(bb)


try:
    from app.dialogs.token_selector import TokenSelectorDialog
    from app.token_item import TokenItem
except Exception:

    class TokenSelectorDialog(QtWidgets.QDialog):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.setWindowTitle("Select Token")
            lay = QtWidgets.QVBoxLayout(self)
            lay.addWidget(QtWidgets.QLabel("Token selector will be implemented here."))
            bb = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok
                | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            bb.accepted.connect(self.accept)
            bb.rejected.connect(self.reject)
            lay.addWidget(bb)


try:
    from app.dialogs.circuit_properties import CircuitPropertiesDialog
except Exception:

    class CircuitPropertiesDialog(QtWidgets.QDialog):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.setWindowTitle("Circuit Properties")
            lay = QtWidgets.QVBoxLayout(self)
            lay.addWidget(QtWidgets.QLabel("Circuit properties will be implemented here."))
            bb = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok
                | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            bb.accepted.connect(self.accept)
            bb.rejected.connect(self.reject)
            lay.addWidget(bb)


try:
    from app.dialogs.calculations_dialog import CalculationsDialog
except Exception:

    class CalculationsDialog(QtWidgets.QDialog):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.setWindowTitle("Calculations")
            lay = QtWidgets.QVBoxLayout(self)
            lay.addWidget(QtWidgets.QLabel("Calculations will be implemented here."))
            bb = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok
                | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            bb.accepted.connect(self.accept)
            bb.rejected.connect(self.reject)
            lay.addWidget(bb)


try:
    from app.dialogs.bom_report import BomReportDialog
except Exception:

    class BomReportDialog(QtWidgets.QDialog):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.setWindowTitle("Bill of Materials Report")
            lay = QtWidgets.QVBoxLayout(self)
            lay.addWidget(QtWidgets.QLabel("BOM report will be implemented here."))
            bb = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok
                | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            bb.accepted.connect(self.accept)
            bb.rejected.connect(self.reject)
            lay.addWidget(bb)


try:
    from app.dialogs.device_schedule_report import DeviceScheduleReportDialog
except Exception:

    class DeviceScheduleReportDialog(QtWidgets.QDialog):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.setWindowTitle("Device Schedule Report")
            lay = QtWidgets.QVBoxLayout(self)
            lay.addWidget(QtWidgets.QLabel("Device schedule report will be implemented here."))
            bb = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok
                | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            bb.accepted.connect(self.accept)
            bb.rejected.connect(self.reject)
            lay.addWidget(bb)


try:
    from app.dialogs.riser_diagram import RiserDiagramDialog
except Exception:

    class RiserDiagramDialog(QtWidgets.QDialog):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.setWindowTitle("Riser Diagram")
            lay = QtWidgets.QVBoxLayout(self)
            lay.addWidget(QtWidgets.QLabel("Riser diagram will be implemented here."))
            bb = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok
                | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            bb.accepted.connect(self.accept)
            bb.rejected.connect(self.reject)
            lay.addWidget(bb)


try:
    from app.dialogs.job_info_dialog import JobInfoDialog
except Exception:

    class JobInfoDialog(QtWidgets.QDialog):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.setWindowTitle("Job Information")
            lay = QtWidgets.QVBoxLayout(self)
            lay.addWidget(QtWidgets.QLabel("Job information will be implemented here."))
            bb = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok
                | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            bb.accepted.connect(self.accept)
            bb.rejected.connect(self.reject)
            lay.addWidget(bb)


APP_VERSION = "0.6.8-cad-base"
APP_TITLE = f"Auto-Fire {APP_VERSION}"
PREF_DIR = os.path.join(os.path.expanduser("~"), "AutoFire")
PREF_PATH = os.path.join(PREF_DIR, "preferences.json")
LOG_DIR = os.path.join(PREF_DIR, "logs")


def ensure_pref_dir():
    try:
        os.makedirs(PREF_DIR, exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)
    except Exception:
        pass


def load_prefs():
    ensure_pref_dir()
    if os.path.exists(PREF_PATH):
        try:
            with open(PREF_PATH, encoding="utf-8") as f:
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
    t = (d.get("type", "") or "").lower()
    n = (d.get("name", "") or "").lower()
    s = (d.get("symbol", "") or "").lower()
    text = " ".join([t, n, s])
    if any(k in text for k in ["strobe", "av", "nac-strobe", "cd", "candela"]):
        return "strobe"
    if any(k in text for k in ["speaker", "spkr", "voice"]):
        return "speaker"
    if any(k in text for k in ["smoke", "detector", "heat"]):
        return "smoke"
    return "other"
    return "other"


class CanvasView(QGraphicsView):
    def __init__(self, scene, devices_group, wires_group, sketch_group, overlay_group, window_ref):
        super().__init__(scene)
        self.setRenderHints(
            QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.TextAntialiasing
        )
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setMouseTracking(True)
        self.devices_group = devices_group
        self.wires_group = wires_group
        self.sketch_group = sketch_group
        self.overlay_group = overlay_group
        self.ortho = False
        self.win = window_ref
        self.current_proto = None
        self.current_kind = "other"
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
        pen = QtGui.QPen(QtGui.QColor("#ffd166"))
        pen.setCosmetic(True)
        brush = QtGui.QBrush(QtGui.QColor("#ffd166"))
        self.osnap_marker.setPen(pen)
        self.osnap_marker.setBrush(brush)
        self.osnap_marker.setZValue(250)
        self.osnap_marker.setVisible(False)
        self.osnap_marker.setParentItem(self.overlay_group)
        self.osnap_marker.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.osnap_marker.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.osnap_marker.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # crosshair
        self.cross_v = QtWidgets.QGraphicsLineItem()
        self.cross_h = QtWidgets.QGraphicsLineItem()
        pen_ch = QtGui.QPen(QtGui.QColor(150, 150, 160, 150))
        pen_ch.setCosmetic(True)
        pen_ch.setStyle(Qt.PenStyle.DashLine)
        self.cross_v.setPen(pen_ch)
        self.cross_h.setPen(pen_ch)
        self.cross_v.setParentItem(self.overlay_group)
        self.cross_h.setParentItem(self.overlay_group)
        self.cross_v.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.cross_h.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.cross_v.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.cross_h.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.cross_v.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.cross_h.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
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
            best = None
            best_d = 1e18
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
                        r = it.rect()
                        pts = [QtCore.QPointF(r.center())]
                elif isinstance(it, QtWidgets.QGraphicsEllipseItem):
                    if self.osnap_center:
                        r = it.rect()
                        pts = [QtCore.QPointF(r.center())]
                elif isinstance(it, QtWidgets.QGraphicsPathItem):
                    pth = it.path()
                    n = pth.elementCount()
                    if n >= 1 and (self.osnap_end or self.osnap_mid):
                        e0 = pth.elementAt(0)
                        eN = pth.elementAt(n - 1)
                        if self.osnap_end:
                            # Check if elements have x,y attributes before accessing
                            if (
                                hasattr(e0, "x")
                                and hasattr(e0, "y")
                                and hasattr(eN, "x")
                                and hasattr(eN, "y")
                            ):
                                pts += [
                                    QtCore.QPointF(float(e0.x), float(e0.y)),
                                    QtCore.QPointF(float(eN.x), float(eN.y)),
                                ]
                        if self.osnap_mid and n >= 2:
                            e1 = pth.elementAt(1)
                            # Check if elements have x,y attributes before accessing
                            if (
                                hasattr(e0, "x")
                                and hasattr(e0, "y")
                                and hasattr(e1, "x")
                                and hasattr(e1, "y")
                            ):
                                pts += [
                                    QtCore.QPointF(
                                        (float(e0.x) + float(e1.x)) / 2.0,
                                        (float(e0.y) + float(e1.y)) / 2.0,
                                    )
                                ]
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
                    for j in range(i + 1, n):
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
                    vx, vy = bx - ax, by - ay
                    wx, wy = p.x() - ax, p.y() - ay
                    denom = vx * vx + vy * vy
                    if denom <= 1e-6:
                        continue
                    t = (wx * vx + wy * vy) / denom
                    if 0.0 <= t <= 1.0:
                        qx, qy = ax + t * vx, ay + t * vy
                        qpt = QtCore.QPointF(qx, qy)
                        d = QtCore.QLineF(p, qpt).length()
                        if d <= thr_scene:
                            cand.append((d, qpt))
            # Sort candidates by distance and deduplicate
            cand.sort(key=lambda x: x[0])
            uniq = []
            seen = set()
            for _, q in cand:
                key = (round(q.x(), 2), round(q.y(), 2))
                if key in seen:
                    continue
                seen.add(key)
                uniq.append(q)
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
            if getattr(self.win, "in_paper_space", False):
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
                if hasattr(sc, "snap") and callable(getattr(sc, "snap")):
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
        self.current_kind = infer_device_kind(proto)
        self._ensure_ghost()

    def _ensure_ghost(self):
        # clear if not a coverage-driven type
        if not self.current_proto or self.current_kind not in ("strobe", "speaker", "smoke"):
            if self.ghost:
                self.scene().removeItem(self.ghost)
                self.ghost = None
            return
        if not self.ghost:
            d = self.current_proto
            self.ghost = DeviceItem(
                0, 0, d["symbol"], d["name"], d.get("manufacturer", ""), d.get("part_number", "")
            )
            self.ghost.setOpacity(0.65)
            self.ghost.setParentItem(self.overlay_group)
        # defaults
        ppf = float(self.win.px_per_ft)
        if self.current_kind == "strobe":
            diam_ft = float(self.win.prefs.get("default_strobe_diameter_ft", 50.0))
            self.ghost.set_coverage(
                {
                    "mode": "strobe",
                    "mount": "ceiling",
                    "computed_radius_ft": max(0.0, diam_ft / 2.0),
                    "px_per_ft": ppf,
                }
            )
        elif self.current_kind == "speaker":
            self.ghost.set_coverage(
                {
                    "mode": "speaker",
                    "mount": "ceiling",
                    "computed_radius_ft": 30.0,
                    "px_per_ft": ppf,
                }
            )
        elif self.current_kind == "smoke":
            spacing_ft = float(self.win.prefs.get("default_smoke_spacing_ft", 30.0))
            self.ghost.set_coverage(
                {
                    "mode": "smoke",
                    "mount": "ceiling",
                    "params": {"spacing_ft": spacing_ft},
                    "computed_radius_ft": spacing_ft / 2.0,
                    "px_per_ft": ppf,
                }
            )
        # placement coverage toggle
        self.ghost.set_coverage_enabled(bool(self.win.prefs.get("show_placement_coverage", True)))

    def _update_crosshair(self, sp: QPointF):
        if not getattr(self, "show_crosshair", True):
            self.cross_v.setVisible(False)
            self.cross_h.setVisible(False)
            return

        # Ensure crosshair is visible
        self.cross_v.setVisible(True)
        self.cross_h.setVisible(True)

        # Set lines to span the entire viewable area, centered on the mouse position
        view_rect = self.viewport().rect()
        scene_top_left = self.mapToScene(view_rect.topLeft())
        scene_bottom_right = self.mapToScene(view_rect.bottomRight())

        self.cross_v.setLine(sp.x(), scene_top_left.y(), sp.x(), scene_bottom_right.y())
        self.cross_h.setLine(scene_top_left.x(), sp.y(), scene_bottom_right.x(), sp.y())

        dx_ft = sp.x() / self.win.px_per_ft
        dy_ft = sp.y() / self.win.px_per_ft
        # Append draw info if applicable
        draw_info = ""
        try:
            if getattr(self.win, "draw", None) and getattr(self.win.draw, "points", None):
                pts = self.win.draw.points
                if pts:
                    p0 = pts[-1]
                    vec = QtCore.QLineF(p0, sp)
                    length_ft = vec.length() / self.win.px_per_ft
                    ang = vec.angle()  # 0 to 360 CCW from +x in Qt
                    draw_info = f"  len={length_ft:.2f} ft  ang={ang:.1f}┬░"
        except Exception:
            pass
        self.win.statusBar().showMessage(
            f"x={dx_ft:.2f} ft   y={dy_ft:.2f} ft   scale={self.win.px_per_ft:.2f} px/ft  snap={self.win.snap_label}{draw_info}"
        )

    def wheelEvent(self, e: QtGui.QWheelEvent):
        s = 1.15 if e.angleDelta().y() > 0 else 1 / 1.15
        self.scale(s, s)

    def keyPressEvent(self, e: QtGui.QKeyEvent):
        k = e.key()
        if k == Qt.Key_Space:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setCursor(Qt.OpenHandCursor)
            e.accept()
            return
        if k == Qt.Key_Shift:
            self.ortho = True
            e.accept()
            return
        # Crosshair toggle moved to 'X' (keyboard shortcut handled in MainWindow too)
        if k == Qt.Key_Escape:
            self.win.cancel_active_tool()
            e.accept()
            return
        if k == Qt.Key_Tab:
            # cycle snap candidates
            if getattr(self, "_snap_candidates", None):
                self._snap_index = (self._snap_index + 1) % len(self._snap_candidates)
                q = self._snap_candidates[self._snap_index]
                self.osnap_marker.setPos(q)
                self.osnap_marker.setVisible(True)
                e.accept()
                return
        super().keyPressEvent(e)

    def keyReleaseEvent(self, e: QtGui.QKeyEvent):
        k = e.key()
        if k == Qt.Key_Space:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.unsetCursor()
            e.accept()
            return
        if k == Qt.Key_Shift:
            self.ortho = False
            e.accept()
            return
        super().keyReleaseEvent(e)

    def mouseMoveEvent(self, e: QtGui.QMouseEvent):
        # Middle-mouse panning (standard CAD feel)
        if self._mmb_panning:
            dx = e.position().x() - self._mmb_last.x()
            dy = e.position().y() - self._mmb_last.y()
            self._mmb_last = e.position()
            h = self.horizontalScrollBar()
            v = self.verticalScrollBar()
            h.setValue(h.value() - int(dx))
            v.setValue(v.value() - int(dy))
            e.accept()
            return

        sp = self.mapToScene(e.position().toPoint())
        sp = self._apply_osnap(sp)
        self.last_scene_pos = sp
        self._update_crosshair(sp)
        if getattr(self.win, "draw", None):
            try:
                self.win.draw.on_mouse_move(sp, shift_ortho=self.ortho)
            except Exception:
                pass
        if getattr(self.win, "dim_tool", None):
            try:
                self.win.dim_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "text_tool", None):
            try:
                self.win.text_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "mtext_tool", None) and getattr(self.win.mtext_tool, "active", False):
            try:
                self.win.mtext_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "freehand_tool", None) and getattr(
            self.win.freehand_tool, "active", False
        ):
            try:
                self.win.freehand_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "measure_tool", None) and getattr(
            self.win.measure_tool, "active", False
        ):
            try:
                self.win.measure_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "leader_tool", None) and getattr(
            self.win.leader_tool, "active", False
        ):
            try:
                self.win.leader_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "cloud_tool", None) and getattr(self.win.cloud_tool, "active", False):
            try:
                self.win.cloud_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "trim_tool", None) and getattr(self.win.trim_tool, "active", False):
            try:
                self.win.trim_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "extend_tool", None) and getattr(
            self.win.extend_tool, "active", False
        ):
            try:
                self.win.extend_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "fillet_tool", None) and getattr(
            self.win.fillet_tool, "active", False
        ):
            try:
                self.win.fillet_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "fillet_radius_tool", None) and getattr(
            self.win.fillet_radius_tool, "active", False
        ):
            try:
                self.win.fillet_radius_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "move_tool", None) and getattr(self.win.move_tool, "active", False):
            try:
                self.win.move_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "underlay_drag_tool", None) and getattr(
            self.win.underlay_drag_tool, "active", False
        ):
            try:
                self.win.underlay_drag_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "rotate_tool", None) and getattr(
            self.win.rotate_tool, "active", False
        ):
            try:
                self.win.rotate_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "mirror_tool", None) and getattr(
            self.win.mirror_tool, "active", False
        ):
            try:
                self.win.mirror_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "scale_tool", None) and getattr(self.win.scale_tool, "active", False):
            try:
                self.win.scale_tool.on_mouse_move(sp)
            except Exception:
                pass
        if getattr(self.win, "wire_tool", None) and getattr(self.win.wire_tool, "active", False):
            try:
                self.win.wire_tool.on_mouse_move(sp)
            except Exception:
                pass
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
            e.accept()
            return
        if e.button() == Qt.LeftButton:
            if getattr(win, "draw", None) and getattr(win.draw, "mode", 0) != 0:
                try:
                    if win.draw.on_click(sp, shift_ortho=self.ortho):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "dim_tool", None) and getattr(win.dim_tool, "active", False):
                try:
                    if win.dim_tool.on_click(sp):
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "text_tool", None) and getattr(win.text_tool, "active", False):
                try:
                    if win.text_tool.on_click(sp):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "mtext_tool", None) and getattr(win.mtext_tool, "active", False):
                try:
                    if win.mtext_tool.on_click(sp):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "freehand_tool", None) and getattr(win.freehand_tool, "active", False):
                try:
                    # freehand starts on press; release will commit
                    if win.freehand_tool.on_press(sp):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "leader_tool", None) and getattr(win.leader_tool, "active", False):
                try:
                    if win.leader_tool.on_click(sp):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "cloud_tool", None) and getattr(win.cloud_tool, "active", False):
                try:
                    if win.cloud_tool.on_click(sp):
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "measure_tool", None) and getattr(win.measure_tool, "active", False):
                try:
                    if win.measure_tool.on_click(sp):
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "trim_tool", None) and getattr(win.trim_tool, "active", False):
                try:
                    if win.trim_tool.on_click(sp):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "extend_tool", None) and getattr(win.extend_tool, "active", False):
                try:
                    if win.extend_tool.on_click(sp):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "fillet_tool", None) and getattr(win.fillet_tool, "active", False):
                try:
                    if win.fillet_tool.on_click(sp):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "move_tool", None) and getattr(win.move_tool, "active", False):
                try:
                    if win.move_tool.on_click(sp):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "rotate_tool", None) and getattr(win.rotate_tool, "active", False):
                try:
                    if win.rotate_tool.on_click(sp):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "mirror_tool", None) and getattr(win.mirror_tool, "active", False):
                try:
                    if win.mirror_tool.on_click(sp):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "scale_tool", None) and getattr(win.scale_tool, "active", False):
                try:
                    if win.scale_tool.on_click(sp):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "wire_tool", None) and getattr(win.wire_tool, "active", False):
                try:
                    if win.wire_tool.on_click(sp):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "chamfer_tool", None) and getattr(win.chamfer_tool, "active", False):
                try:
                    if win.chamfer_tool.on_click(sp):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "underlay_drag_tool", None) and getattr(
                win.underlay_drag_tool, "active", False
            ):
                try:
                    if win.underlay_drag_tool.on_click(sp):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(win, "fillet_radius_tool", None) and getattr(
                win.fillet_radius_tool, "active", False
            ):
                try:
                    if win.fillet_radius_tool.on_click(sp):
                        win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            # Prefer selection when clicking over existing selectable content
            try:
                under_items = self.items(e.position().toPoint())
                for it in under_items:
                    if it in (self.cross_v, self.cross_h, self.osnap_marker):
                        continue
                    if isinstance(it, QtWidgets.QGraphicsItem) and (
                        it.flags() & QtWidgets.QGraphicsItem.ItemIsSelectable
                    ):
                        return super().mousePressEvent(e)
            except Exception:
                pass
            if self.current_proto:
                d = self.current_proto
                layer_obj = next(
                    (l for l in self.win.layers if l["id"] == self.win.active_layer_id), None
                )
                it = DeviceItem(
                    sp.x(),
                    sp.y(),
                    d["symbol"],
                    d["name"],
                    d.get("manufacturer", ""),
                    d.get("part_number", ""),
                    layer_obj,
                )
                if self.ghost and self.current_kind in ("strobe", "speaker", "smoke"):
                    it.set_coverage(self.ghost.coverage)
                # Respect global overlay toggle on placement
                try:
                    it.set_coverage_enabled(bool(self.win.show_coverage))
                except Exception:
                    pass
                it.setParentItem(self.devices_group)
                win.push_history()
                e.accept()
                return
            else:
                # Clear selection when clicking empty space with no active tool
                self.scene().clearSelection()
        elif e.button() == Qt.RightButton:
            win.canvas_menu(e.globalPosition().toPoint())
            e.accept()
            return
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.MiddleButton and self._mmb_panning:
            self._mmb_panning = False
            self.unsetCursor()
            e.accept()
            return
        # If hand-drag mode (Space), let base handle release
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            return super().mouseReleaseEvent(e)
        if e.button() == Qt.LeftButton:
            if getattr(self.win, "freehand_tool", None) and getattr(
                self.win.freehand_tool, "active", False
            ):
                try:
                    if self.win.freehand_tool.on_release(self.last_scene_pos):
                        self.win.push_history()
                        e.accept()
                        return
                except Exception:
                    pass
            if getattr(self.win, "cloud_tool", None) and getattr(
                self.win.cloud_tool, "active", False
            ):
                try:
                    if self.win.cloud_tool.finish():
                        self.win.push_history()
                        e.accept()
                        return
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
        self.prefs.setdefault("active_layer_id", 1)  # Default to layer ID 1
        save_prefs(self.prefs)

        self.active_layer_id = self.prefs["active_layer_id"]

        # Theme
        self.set_theme(self.prefs.get("theme", "dark"))  # apply early

        self.devices_all = catalog.load_catalog()
        self.layers = db_loader.fetch_layers(db_loader.connect())

        self.scene = GridScene(int(self.prefs.get("grid", DEFAULT_GRID_SIZE)), 0, 0, 15000, 10000)
        self.paper_scene = QtWidgets.QGraphicsScene(
            0, 0, 15000, 10000
        )  # Separate scene for paperspace

        # Add a default viewport to the paperspace scene
        default_viewport = ViewportItem(self.scene, QtCore.QRectF(0, 0, 1000, 800), self)
        self.paper_scene.addItem(default_viewport)

        self.scene.snap_enabled = bool(self.prefs.get("snap", True))
        self.scene.set_grid_style(
            float(self.prefs.get("grid_opacity", 0.25)),
            float(self.prefs.get("grid_width_px", 0.0)),
            int(self.prefs.get("grid_major_every", 5)),
        )
        self._apply_snap_step_from_inches(self.snap_step_in)

        self.layer_underlay = QtWidgets.QGraphicsItemGroup()
        self.layer_underlay.setZValue(-50)
        self.scene.addItem(self.layer_underlay)
        self.layer_sketch = QtWidgets.QGraphicsItemGroup()
        self.layer_sketch.setZValue(40)
        self.scene.addItem(self.layer_sketch)
        self.layer_wires = QtWidgets.QGraphicsItemGroup()
        self.layer_wires.setZValue(60)
        self.scene.addItem(self.layer_wires)
        self.layer_devices = QtWidgets.QGraphicsItemGroup()
        self.layer_devices.setZValue(100)
        self.scene.addItem(self.layer_devices)
        self.layer_overlay = QtWidgets.QGraphicsItemGroup()
        self.layer_overlay.setZValue(200)
        self.scene.addItem(self.layer_overlay)
        # Allow child items to receive mouse events for selection and dragging
        for grp in (
            self.layer_underlay,
            self.layer_sketch,
            self.layer_wires,
            self.layer_devices,
            self.layer_overlay,
        ):
            try:
                grp.setHandlesChildEvents(False)
            except Exception:
                pass

        self.view = CanvasView(
            self.scene,
            self.layer_devices,
            self.layer_wires,
            self.layer_sketch,
            self.layer_overlay,
            self,
        )
        # Distinguish model space visually
        try:
            self.view.setBackgroundBrush(QtGui.QColor(20, 22, 26))
        except Exception:
            pass
        self.page_frame = None
        self.title_block = None
        # Sheet manager: list of {name, scene}; paper_scene points to current sheet
        self.sheets = []
        self.paper_scene = None
        self.in_paper_space = False

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

        self.connections_tree = ConnectionsTree(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.connections_tree)

        self.wire_tool = WireTool(self, self.layer_wires, self.connections_tree)

        # CAD Toolbar
        cad_toolbar = QToolBar("CAD Tools")
        cad_toolbar.addAction("Measure", self.start_measure)
        cad_toolbar.addAction("Scale", self.start_scale)
        self.addToolBar(cad_toolbar)

        # Menus
        menubar = self.menuBar()
        m_file = menubar.addMenu("&File")
        m_file.addAction("New", self.new_project, QtGui.QKeySequence.New)
        m_file.addAction("Open…", self.open_project, QtGui.QKeySequence.Open)
        m_file.addAction("Save As…", self.save_project_as, QtGui.QKeySequence.SaveAs)
        m_file.addSeparator()
        imp = m_file.addMenu("Import")
        imp.addAction("DXF Underlay…", self.import_dxf_underlay)
        imp.addAction("PDF Underlay…", self.import_pdf_underlay)
        exp = m_file.addMenu("Export")
        exp.addAction("PNG…", self.export_png)
        exp.addAction("PDF…", self.export_pdf)
        exp.addAction("Device Schedule (CSV)…", self.export_device_schedule_csv)
        exp.addAction("Bill of Materials (BOM)", self.show_bom_report)
        exp.addAction("Device Schedule", self.show_device_schedule_report)
        exp.addAction("Place Symbol Legend", self.place_symbol_legend)
        # Settings submenu (moved under File)
        m_settings = m_file.addMenu("Settings")
        m_settings.addAction("Open Settings...", self.open_settings)
        theme = m_settings.addMenu("Theme")
        theme.addAction("Dark", lambda: self.set_theme("dark"))
        theme.addAction("Light", lambda: self.set_theme("light"))
        theme.addAction("High Contrast (Dark)", lambda: self.set_theme("high_contrast"))
        m_file.addSeparator()
        m_file.addAction("Quit", self.close, QtGui.QKeySequence.Quit)

        # Edit menu
        m_edit = menubar.addMenu("&Edit")
        act_undo = QtGui.QAction("Undo", self)
        act_undo.setShortcut(QtGui.QKeySequence.Undo)
        act_undo.triggered.connect(self.undo)
        m_edit.addAction(act_undo)
        act_redo = QtGui.QAction("Redo", self)
        act_redo.setShortcut(QtGui.QKeySequence.Redo)
        act_redo.triggered.connect(self.redo)
        m_edit.addAction(act_redo)
        m_edit.addSeparator()
        act_del = QtGui.QAction("Delete", self)
        act_del.setShortcut(Qt.Key_Delete)
        act_del.triggered.connect(self.delete_selection)
        m_edit.addAction(act_del)

        # View menu
        m_view = menubar.addMenu("&View")
        m_view.addAction("Fit View to Content", self.fit_view_to_content, QtGui.QKeySequence("F2"))
        m_view.addSeparator()
        self.act_view_grid = QtGui.QAction("Grid", self, checkable=True)
        self.act_view_grid.setChecked(True)
        self.act_view_grid.toggled.connect(self.toggle_grid)
        m_view.addAction(self.act_view_grid)
        self.act_view_snap = QtGui.QAction("Snap", self, checkable=True)
        self.act_view_snap.setChecked(True)
        self.act_view_snap.toggled.connect(self.toggle_snap)
        m_view.addAction(self.act_view_snap)
        self.act_view_cross = QtGui.QAction("Crosshair (X)", self, checkable=True)
        self.act_view_cross.setChecked(True)
        self.act_view_cross.toggled.connect(self.toggle_crosshair)
        m_view.addAction(self.act_view_cross)
        m_view.addSeparator()
        m_view.addAction("Zoom In", self.zoom_in, QtGui.QKeySequence.ZoomIn)
        m_view.addAction("Zoom Out", self.zoom_out, QtGui.QKeySequence.ZoomOut)
        m_view.addAction("Zoom to Selection", self.zoom_to_selection)

        # Tools menu
        m_tools = menubar.addMenu("&Tools")

        def add_tool(name, cb):
            act = QtGui.QAction(name, self)
            act.triggered.connect(cb)
            m_tools.addAction(act)
            return act

        self.act_draw_line = add_tool(
            "Draw Line",
            lambda: (
                setattr(self.draw, "layer", self.layer_sketch),
                self.draw.set_mode(draw_tools.DrawMode.LINE),
            ),
        )
        self.act_draw_rect = add_tool(
            "Draw Rect",
            lambda: (
                setattr(self.draw, "layer", self.layer_sketch),
                self.draw.set_mode(draw_tools.DrawMode.RECT),
            ),
        )
        self.act_draw_circle = add_tool(
            "Draw Circle",
            lambda: (
                setattr(self.draw, "layer", self.layer_sketch),
                self.draw.set_mode(draw_tools.DrawMode.CIRCLE),
            ),
        )
        self.act_draw_poly = add_tool(
            "Draw Polyline",
            lambda: (
                setattr(self.draw, "layer", self.layer_sketch),
                self.draw.set_mode(draw_tools.DrawMode.POLYLINE),
            ),
        )
        self.act_draw_arc3 = add_tool(
            "Draw Arc (3-Point)",
            lambda: (
                setattr(self.draw, "layer", self.layer_sketch),
                self.draw.set_mode(draw_tools.DrawMode.ARC3),
            ),
        )
        self.act_draw_wire = add_tool("Draw Wire", self.start_wiring)
        self.act_text = add_tool("Text", self.start_text)
        self.act_mtext = add_tool("MText", self.start_mtext)
        self.act_freehand = add_tool("Freehand", self.start_freehand)
        self.act_leader = add_tool("Leader", self.start_leader)
        self.act_cloud = add_tool("Revision Cloud", self.start_cloud)
        self.act_place_token = add_tool("Place Token", self.place_token)
        m_tools.addSeparator()
        m_tools.addAction("Dimension (D)", self.start_dimension)
        m_tools.addAction("Measure (M)", self.start_measure)
        m_tools.addAction("Generate Riser Diagram", self.generate_riser_diagram)
        m_tools.addAction("Show Calculations", self.show_calculations)
        m_tools.addAction("Circuit Properties", self.show_circuit_properties)

        # (Settings moved under File)

        # Layout / Paper Space
        m_layout = menubar.addMenu("&Layout")
        m_layout.addAction("Add Page Frame…", self.add_page_frame)
        m_layout.addAction("Remove Page Frame", self.remove_page_frame)
        m_layout.addAction("Add/Update Title Block…", self.add_or_update_title_block)
        m_layout.addAction("Job Information...", self.show_job_info_dialog)
        m_layout.addAction("Page Setup…", self.page_setup_dialog)
        m_layout.addAction("Add Viewport", self.add_viewport)
        m_layout.addSeparator()
        m_layout.addAction("Switch to Paper Space", lambda: self.toggle_paper_space(True))
        m_layout.addAction("Switch to Model Space", lambda: self.toggle_paper_space(False))
        scale_menu = m_layout.addMenu("Print Scale")

        def add_scale(label, inches_per_ft):
            act = QtGui.QAction(label, self)
            act.triggered.connect(lambda v=inches_per_ft: self.set_print_scale(v))
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
        scale_menu.addAction("Custom…", self.set_print_scale_custom)

        # Help menu
        m_help = menubar.addMenu("&Help")
        m_help.addAction("User Guide", self.show_user_guide)
        m_help.addAction("Keyboard Shortcuts", self.show_shortcuts)
        m_help.addSeparator()
        m_help.addAction("About Auto-Fire", self.show_about)

        # Status bar: left space selector/lock; right badges
        self.space_combo = QtWidgets.QComboBox()
        self.space_combo.addItems(["Model", "Paper"])
        self.space_combo.setCurrentIndex(0)
        self.space_lock = QtWidgets.QToolButton()
        self.space_lock.setCheckable(True)
        self.space_lock.setText("Lock")
        self.statusBar().addWidget(QtWidgets.QLabel("Space:"))
        self.statusBar().addWidget(self.space_combo)
        self.statusBar().addWidget(self.space_lock)
        self.space_combo.currentIndexChanged.connect(self._on_space_combo_changed)
        # Right badges
        self.scale_badge = QtWidgets.QLabel("")
        self.scale_badge.setStyleSheet("QLabel { color: #c0c0c0; }")
        self.statusBar().addPermanentWidget(self.scale_badge)
        self.space_badge = QtWidgets.QLabel("MODEL SPACE")
        self.space_badge.setStyleSheet("QLabel { color: #7dcfff; font-weight: bold; }")
        self.statusBar().addPermanentWidget(self.space_badge)
        # Ensure central widget is just the view
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.view, "Model")
        self.setCentralWidget(self.tab_widget)

        self._init_sheet_manager()

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
        QtGui.QShortcut(QtGui.QKeySequence("X"), self, activated=self._toggle_crosshair_shortcut)

        # Selection change → update Properties
        self.scene.selectionChanged.connect(self._on_selection_changed)

        self.history = []
        self.history_index = -1
        self.push_history()
        # Fit view after UI ready
        try:
            QtCore.QTimer.singleShot(0, self.fit_view_to_content)
        except Exception:
            pass

    def _toggle_crosshair_shortcut(self):
        """Toggle crosshair visibility via keyboard shortcut."""
        self.act_view_cross.setChecked(not self.act_view_cross.isChecked())

    def _on_space_combo_changed(self, idx: int):
        if self.space_lock.isChecked():
            # Revert change if locked
            try:
                self.space_combo.blockSignals(True)
                self.space_combo.setCurrentIndex(1 if self.in_paper_space else 0)
            finally:
                self.space_combo.blockSignals(False)
            return
        # 0 = Model, 1 = Paper
        self.toggle_paper_space(idx == 1)

    # ---------- Theme ----------
    def set_theme(self, name: str):
        name = (name or "dark").lower()
        primary_color = self.prefs.get("primary_color", "#0078d7")
        if name == "light":
            self.apply_light_theme(primary_color)
        elif name in ("hc", "high", "high_contrast", "high-contrast"):
            self.apply_high_contrast_theme(primary_color)
        else:
            self.apply_dark_theme(primary_color)
        self.prefs["theme"] = name
        save_prefs(self.prefs)

    def apply_dark_theme(self, primary_color):
        app = QtWidgets.QApplication.instance()
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
        app = QtWidgets.QApplication.instance()
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
        app = QtWidgets.QApplication.instance()
        pal = app.palette()
        bg = QtGui.QColor(18, 18, 18)
        base = QtGui.QColor(10, 10, 12)
        text = QtGui.QColor(245, 245, 245)
        pal.setColor(QtGui.QPalette.ColorRole.Window, bg)
        pal.setColor(QtGui.QPalette.ColorRole.Base, base)
        pal.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(28, 28, 32))
        pal.setColor(QtGui.QPalette.ColorRole.Text, text)
        pal.setColor(QtGui.QPalette.ColorRole.WindowText, text)
        pal.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(26, 26, 30))
        pal.setColor(QtGui.QPalette.ColorRole.ButtonText, text)
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor(30, 30, 30))
        pal.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor(255, 255, 255))
        pal.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(primary_color))
        pal.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(0, 0, 0))
        app.setPalette(pal)
        self._apply_menu_stylesheet(contrast_boost=True)

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
        # Device Palette as dockable panel with improved organization
        left = QWidget()

        # Layout
        ll = QVBoxLayout(left)
        ll.setSpacing(5)
        ll.setContentsMargins(5, 5, 5, 5)

        # System Configuration Section
        system_group = QtWidgets.QGroupBox("System")
        system_group.setCheckable(True)
        system_group.toggled.connect(lambda checked: self.toggle_group(system_group, checked))
        system_layout = QVBoxLayout(system_group)

        facp_btn = QPushButton("System Configuration Wizard")
        facp_btn.setStyleSheet(
            "QPushButton { font-weight: bold; padding: 15px; background-color: #0078d7; color: white; border: none; border-radius: 4px; font-size: 11pt; margin-top: 15px; } QPushButton:hover { background-color: #005a9e; } QPushButton:pressed { background-color: #004578; }"
        )
        facp_btn.clicked.connect(self.place_facp_panel)
        system_layout.addWidget(facp_btn)

        wire_spool_btn = QPushButton("Wire Spool")
        wire_spool_btn.setStyleSheet(
            "QPushButton { font-weight: bold; padding: 15px; background-color: #555; color: white; border: none; border-radius: 4px; font-size: 11pt; margin-top: 15px; } QPushButton:hover { background-color: #666; } QPushButton:pressed { background-color: #777; }"
        )
        wire_spool_btn.clicked.connect(self.open_wire_spool)
        system_layout.addWidget(wire_spool_btn)

        ll.addWidget(system_group)

        # Device Palette Section
        device_palette_group = QtWidgets.QGroupBox("Device Palette")
        device_palette_group.setCheckable(True)
        device_palette_group.toggled.connect(
            lambda checked: self.toggle_group(device_palette_group, checked)
        )
        device_palette_layout = QVBoxLayout(device_palette_group)

        # Search section with enhanced styling and better organization
        search_layout = QHBoxLayout()
        search_layout.setSpacing(15)
        search_layout.setContentsMargins(15, 15, 15, 15)
        search_label = QLabel("Search:")
        search_label.setStyleSheet("QLabel { font-weight: bold; font-size: 10pt; }")
        search_layout.addWidget(search_label)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Enter device name, symbol, or part number...")
        self.search.setClearButtonEnabled(True)
        self.search.setStyleSheet(
            "QLineEdit { padding: 12px; border: 1px solid #555; border-radius: 4px; background-color: #3c3c40; color: #e0e0e0; selection-background-color: #0078d7; font-size: 10pt; } QLineEdit:focus { border: 1px solid #0078d7; }"
        )
        search_layout.addWidget(self.search)
        device_palette_layout.addLayout(search_layout)

        # Add search delay timer
        self.search_timer = QtCore.QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._filter_device_tree)
        self.search.textChanged.connect(self._on_search_text_changed)

        # Filter section with improved organization and reduced clustering
        filter_group = QtWidgets.QGroupBox("Filters")
        filter_layout = QVBoxLayout(filter_group)
        filter_layout.setSpacing(25)  # Increase spacing between filters to reduce clustering
        filter_layout.setContentsMargins(15, 15, 15, 15)

        # System Category filter with clearer labeling
        cat_layout = QHBoxLayout()
        cat_layout.setSpacing(15)
        category_label = QLabel("System Category:")
        category_label.setStyleSheet("QLabel { font-weight: bold; font-size: 10pt; }")
        cat_layout.addWidget(category_label)
        self.cmb_category = QComboBox()
        self.cmb_category.setStyleSheet(
            "QComboBox { padding: 12px; border: 1px solid #555; border-radius: 4px; background-color: #3c3c40; color: #e0e0e0; min-height: 24px; font-size: 10pt; } QComboBox:hover { border: 1px solid #0078d7; } QComboBox::drop-down { border: none; width: 25px; } QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid #a0a0a0; width: 0; height: 0; margin-right: 6px; margin-top: 8px; }"
        )
        cat_layout.addWidget(self.cmb_category, 2)
        filter_layout.addLayout(cat_layout)

        # Manufacturer filter with clearer labeling
        mfr_layout = QHBoxLayout()
        mfr_layout.setSpacing(15)
        manufacturer_label = QLabel("Manufacturer:")
        manufacturer_label.setStyleSheet("QLabel { font-weight: bold; font-size: 10pt; }")
        mfr_layout.addWidget(manufacturer_label)
        self.cmb_mfr = QComboBox()
        self.cmb_mfr.setStyleSheet(
            "QComboBox { padding: 12px; border: 1px solid #555; border-radius: 4px; background-color: #3c3c40; color: #e0e0e0; min-height: 24px; font-size: 10pt; } QComboBox:hover { border: 1px solid #0078d7; } QComboBox::drop-down { border: none; width: 25px; } QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid #a0a0a0; width: 0; height: 0; margin-right: 6px; margin-top: 8px; }"
        )
        mfr_layout.addWidget(self.cmb_mfr, 2)
        filter_layout.addLayout(mfr_layout)

        # Device Type filter with clearer labeling
        type_layout = QHBoxLayout()
        type_layout.setSpacing(15)
        type_label = QLabel("Device Type:")
        type_label.setStyleSheet("QLabel { font-weight: bold; font-size: 10pt; }")
        type_layout.addWidget(type_label)
        self.cmb_type = QComboBox()
        self.cmb_type.setStyleSheet(
            "QComboBox { padding: 12px; border: 1px solid #555; border-radius: 4px; background-color: #3c3c40; color: #e0e0e0; min-height: 24px; font-size: 10pt; } QComboBox:hover { border: 1px solid #0078d7; } QComboBox::drop-down { border: none; width: 25px; } QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid #a0a0a0; width: 0; height: 0; margin-right: 6px; margin-top: 8px; }"
        )
        type_layout.addWidget(self.cmb_type, 2)
        filter_layout.addLayout(type_layout)

        # Clear filters button with enhanced styling
        self.btn_clear_filters = QPushButton("Clear All Filters")
        self.btn_clear_filters.setStyleSheet(
            "QPushButton { padding: 12px 15px; border: 1px solid #555; border-radius: 4px; background-color: #3c3c40; color: #e0e0e0; min-height: 24px; font-weight: bold; font-size: 10pt; } QPushButton:hover { background-color: #46464a; border: 1px solid #0078d7; } QPushButton:pressed { background-color: #0078d7; }"
        )
        self.btn_clear_filters.clicked.connect(self._clear_filters)
        filter_layout.addWidget(self.btn_clear_filters)

        device_palette_layout.addWidget(filter_group)

        # Device tree view with improved categorized organization and better visual hierarchy
        self.device_tree = QtWidgets.QTreeWidget()
        self.device_tree.setHeaderLabels(["Devices"])
        self.device_tree.setAlternatingRowColors(True)
        self.device_tree.setSortingEnabled(True)
        self.device_tree.sortByColumn(0, Qt.AscendingOrder)
        self.device_tree.setIndentation(30)  # Increase indentation for better visual hierarchy
        self.device_tree.setUniformRowHeights(True)
        self.device_tree.setIconSize(QSize(24, 24))  # Larger icons for better visibility
        self.device_tree.setAnimated(True)
        self.device_tree.setStyleSheet(
            """
            QTreeWidget {
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #252526;
                alternate-background-color: #2d2d30;
                selection-background-color: #0078d7;
                selection-color: white;
                font-size: 10pt;
                margin-top: 15px;
            }
            QTreeWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3c3c40;
            }
            QTreeWidget::item:hover {
                background-color: #3f3f41;
            }
            QTreeWidget::item:selected {
                background-color: #0078d7;
            }
            QScrollBar:vertical {
                border: none;
                background: #333336;
                width: 16px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #555558;
                border-radius: 4px;
                min-height: 25px;
            }
            QScrollBar::handle:vertical:hover {
                background: #666669;
            }
        """
        )
        device_palette_layout.addWidget(self.device_tree)
        ll.addWidget(device_palette_group)

        # Populate filters and device tree
        self._populate_filters()
        self._populate_device_tree()

        # Create dock widget
        dock = QDockWidget("System & Device Palette", self)
        dock.setWidget(left)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        # Removed duplicate tab_widget initialization

    def _build_layers_and_props_dock(self):
        dock = QDockWidget("Properties", self)
        panel = QWidget()
        form = QVBoxLayout(panel)
        form.setContentsMargins(8, 8, 8, 8)
        form.setSpacing(6)

        # layer toggles (visibility)
        form.addWidget(QLabel("Layers"))
        self.chk_underlay = QCheckBox("Underlay")
        self.chk_underlay.setChecked(True)
        self.chk_underlay.toggled.connect(lambda v: self.layer_underlay.setVisible(v))
        form.addWidget(self.chk_underlay)
        self.chk_sketch = QCheckBox("Sketch")
        self.chk_sketch.setChecked(True)
        self.chk_sketch.toggled.connect(lambda v: self.layer_sketch.setVisible(v))
        form.addWidget(self.chk_sketch)
        self.chk_wires = QCheckBox("Wiring")
        self.chk_wires.setChecked(True)
        self.chk_wires.toggled.connect(lambda v: self.layer_wires.setVisible(v))
        form.addWidget(self.chk_wires)
        self.chk_devices = QCheckBox("Devices")
        self.chk_devices.setChecked(True)
        self.chk_devices.toggled.connect(lambda v: self.layer_devices.setVisible(v))
        form.addWidget(self.chk_devices)

        self.btn_layer_manager = QPushButton("Layer Manager")
        self.btn_layer_manager.clicked.connect(self.open_layer_manager)
        form.addWidget(self.btn_layer_manager)

        # properties
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

        # disable until selection
        self._enable_props(False)

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

    def _enable_props(self, on: bool):
        for w in (
            self.prop_label,
            self.prop_offx,
            self.prop_offy,
            self.prop_mount,
            self.prop_mode,
            self.prop_size,
            self.btn_apply_props,
        ):
            w.setEnabled(on)

    # ---------- DXF layers dock ----------
    def _build_dxf_layers_dock(self):
        dock = QDockWidget("DXF Layers", self)
        self.dxf_panel = QWidget()
        v = QVBoxLayout(self.dxf_panel)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(6)
        self.lst_dxf = QtWidgets.QListWidget()
        self.lst_dxf.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        v.addWidget(self.lst_dxf)
        # Controls row
        row1 = QHBoxLayout()
        self.btn_dxf_color = QPushButton("Set ColorΓÇª")
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
        self.btn_dxf_color.clicked.connect(self._pick_dxf_color)
        self.btn_dxf_reset.clicked.connect(self._reset_dxf_color)
        self.lst_dxf.itemChanged.connect(self._toggle_dxf_layer)
        self.chk_dxf_lock.toggled.connect(self._lock_dxf_layer)
        self.chk_dxf_print.toggled.connect(self._print_dxf_layer)
        self._refresh_dxf_layers_dock()
        # Tabify with properties dock if available
        if hasattr(self, "dock_layers_props"):
            try:
                self.tabifyDockWidget(self.dock_layers_props, self.dock_dxf_layers)
            except Exception:
                pass

    def _refresh_dxf_layers_dock(self):
        if not hasattr(self, "lst_dxf"):
            return
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
        name = item.text()
        grp = self._get_dxf_group(name)
        if grp is None:
            return
        grp.setVisible(item.checkState() == Qt.Checked)

    def _pick_dxf_color(self):
        it = self.lst_dxf.currentItem()
        if not it:
            return
        color = QtWidgets.QColorDialog.getColor(parent=self)
        if not color.isValid():
            return
        grp = self._get_dxf_group(it.text())
        if grp is None:
            return
        pen = QtGui.QPen(color)
        pen.setCosmetic(True)
        for ch in grp.childItems():
            try:
                if hasattr(ch, "setPen"):
                    ch.setPen(pen)
            except Exception:
                pass

    def _reset_dxf_color(self):
        it = self.lst_dxf.currentItem()
        if not it:
            return
        grp = self._get_dxf_group(it.text())
        if grp is None:
            return
        # Reset to original DXF color if stored
        orig = grp.data(2002)
        col = QtGui.QColor(orig) if orig else QtGui.QColor("#C0C0C0")
        pen = QtGui.QPen(col)
        pen.setCosmetic(True)
        for ch in grp.childItems():
            try:
                if hasattr(ch, "setPen"):
                    ch.setPen(pen)
            except Exception:
                pass

    def _current_dxf_group(self):
        it = self.lst_dxf.currentItem()
        return self._get_dxf_group(it.text()) if it else None

    def _lock_dxf_layer(self, on: bool):
        grp = self._current_dxf_group()
        if grp is None:
            return
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
        if grp is None:
            return
        grp.setData(2003, bool(on))

    # ---------- palette ----------
    def _populate_filters(self):
        """Populate filter dropdowns with unique values from the catalog."""
        categories = set()
        manufacturers = set()
        types = set()

        for d in self.devices_all:
            if d.get("system_category"):
                categories.add(d["system_category"])
            if d.get("manufacturer"):
                manufacturers.add(d["manufacturer"])
            if d.get("type"):
                types.add(d["type"])

        self.cmb_category.clear()
        self.cmb_category.addItems(["All Categories"] + sorted(list(categories)))

        self.cmb_mfr.clear()
        self.cmb_mfr.addItems(["All Manufacturers"] + sorted(list(manufacturers)))

        self.cmb_type.clear()
        self.cmb_type.addItems(["All Device Types"] + sorted(list(types)))

    def _populate_device_tree(self):
        """Populate the device tree with categorized devices and improved organization."""
        self.device_tree.clear()

        # Organize devices by category and type with better hierarchy
        categorized_devices = {}
        for d in self.devices_all:
            # Skip devices with empty names
            if not d.get("name"):
                continue

            category = d.get("system_category", "Unknown") or "Unknown"
            device_type = d.get("type", "Unknown") or "Unknown"

            # Ensure category and type are not empty
            if not category:
                category = "Unknown"
            if not device_type:
                device_type = "Unknown"

            if category not in categorized_devices:
                categorized_devices[category] = {}
            if device_type not in categorized_devices[category]:
                categorized_devices[category][device_type] = []

            categorized_devices[category][device_type].append(d)

        # Create tree items with improved visual hierarchy and spacing
        for category in sorted(categorized_devices.keys()):
            category_item = QtWidgets.QTreeWidgetItem([category])
            category_item.setExpanded(True)  # Start expanded for better visibility
            font = category_item.font(0)
            font.setBold(True)
            font.setPointSize(11)  # Larger font for categories
            category_item.setFont(0, font)
            category_item.setIcon(0, QtGui.QIcon())  # Add icon if needed

            for device_type in sorted(categorized_devices[category].keys()):
                type_item = QtWidgets.QTreeWidgetItem([device_type])
                type_item.setExpanded(True)  # Start expanded for better visibility
                font = type_item.font(0)
                font.setItalic(True)
                font.setBold(True)
                font.setPointSize(10)  # Slightly smaller than category
                type_item.setFont(0, font)
                type_item.setIcon(0, QtGui.QIcon())  # Add icon if needed

                for device in sorted(
                    categorized_devices[category][device_type], key=lambda x: x["name"]
                ):
                    # Create device item with formatted text and better spacing
                    display_text = f"{device['name']} ({device['symbol']})"
                    if device.get("part_number"):
                        display_text += f" - {device['part_number']}"

                    device_item = QtWidgets.QTreeWidgetItem([display_text])
                    device_item.setData(0, Qt.UserRole, device)

                    # Set tooltip with detailed information
                    tooltip = f"Name: {device['name']}\nSymbol: {device['symbol']}\nType: {device_type}\nCategory: {category}"
                    if device.get("manufacturer") and device["manufacturer"] != "(Any)":
                        tooltip += f"\nManufacturer: {device['manufacturer']}"
                    if device.get("part_number"):
                        tooltip += f"\nPart Number: {device['part_number']}"
                    device_item.setToolTip(0, tooltip)

                    # Add icon based on device type if needed
                    device_item.setIcon(0, QtGui.QIcon())  # Add icon if needed

                    type_item.addChild(device_item)

                category_item.addChild(type_item)

            self.device_tree.addTopLevelItem(category_item)

        # Expand all items by default for better visibility
        self.device_tree.expandAll()

        # Set better styling for the tree
        self.device_tree.setStyleSheet(
            "QTreeWidget { border: 1px solid #555; background-color: #252526; alternate-background-color: #2d2d30; selection-background-color: #0078d7; selection-color: white; } QTreeWidget::item { padding: 3px; } QTreeWidget::item:hover { background-color: #3f3f41; } QTreeWidget::item:selected { background-color: #0078d7; } QScrollBar:vertical { border: none; background: #333336; width: 14px; margin: 0px 0px 0px 0px; } QScrollBar::handle:vertical { background: #555558; border-radius: 4px; min-height: 20px; } QScrollBar::handle:vertical:hover { background: #666669; }"
        )

    def _filter_device_tree(self):
        """Filter the device tree based on search and filter criteria."""
        search_text = self.search.text().lower().strip()
        selected_category = self.cmb_category.currentText()
        selected_mfr = self.cmb_mfr.currentText()
        selected_type = self.cmb_type.currentText()

        def item_matches(item):
            """Recursively check if an item or any of its children match the filters."""
            # If it's a device, check if it matches
            device = item.data(0, Qt.UserRole)
            if device:
                search_matches = not search_text or (
                    search_text in device.get("name", "").lower()
                    or search_text in device.get("symbol", "").lower()
                    or search_text in device.get("part_number", "").lower()
                )
                mfr_matches = selected_mfr == "All Manufacturers" or selected_mfr == device.get(
                    "manufacturer", "(Any)"
                )
                type_matches = selected_type == "All Device Types" or selected_type == device.get(
                    "type", "Unknown"
                )
                category_matches = (
                    selected_category == "All Categories"
                    or selected_category == device.get("system_category", "Unknown")
                )

                return search_matches and mfr_matches and type_matches and category_matches

            # If it's a category or type, check if any children match
            child_count = item.childCount()
            any_child_matches = False
            for i in range(child_count):
                if item_matches(item.child(i)):
                    any_child_matches = True
                    break  # No need to check other children

            return any_child_matches

        def update_visibility(item):
            """Recursively update the visibility of items."""
            matches = item_matches(item)
            item.setHidden(not matches)

            for i in range(item.childCount()):
                update_visibility(item.child(i))

        # Iterate over top-level items and update visibility
        for i in range(self.device_tree.topLevelItemCount()):
            update_visibility(self.device_tree.topLevelItem(i))

        self.device_tree.expandAll()

    def _on_device_selected(self, item: QtWidgets.QTreeWidgetItem, column: int):
        """Handle device selection from the tree view."""
        # Only process leaf items (devices, not categories or types)
        if item.childCount() > 0 or not item.data(0, Qt.UserRole):
            return

        device = item.data(0, Qt.UserRole)
        self.view.set_current_device(device)
        self.statusBar().showMessage(f"Selected: {device['name']} ({device['symbol']})")

    def _clear_filters(self):
        """Clear all filter selections."""
        self.search.clear()
        self.cmb_category.setCurrentIndex(0)
        self.cmb_mfr.setCurrentIndex(0)
        self.cmb_type.setCurrentIndex(0)
        self._filter_device_tree()

    def _on_search_text_changed(self, text):
        """Handle search text changes with delay."""
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms delay

    # ---------- FACP placement ----------
    def place_facp_panel(self):
        """Place a FACP panel using the wizard dialog."""
        try:
            # Create and show the FACP wizard dialog
            dialog = FACPWizardDialog(self)
            if dialog.exec() == QtWidgets.QDialog.Accepted:
                # Get the configured panels
                panels = dialog.get_panel_configurations()
                print(f"DEBUG: Panels from wizard: {panels}")

                for panel in panels:
                    # Create a device item for the FACP panel
                    symbol = "FACP"
                    name = f"{panel.manufacturer} {panel.model}"
                    manufacturer = panel.manufacturer
                    part_number = panel.model

                    # Place the panel at the center of the current view
                    view_center = self.view.mapToScene(self.view.viewport().rect().center())
                    x, y = view_center.x(), view_center.y()

                    # Create the device item
                    layer_obj = next(
                        (l for l in self.layers if l["id"] == self.active_layer_id), None
                    )
                    device_item = DeviceItem(
                        x, y, symbol, name, manufacturer, part_number, layer_obj
                    )
                    device_item.setParentItem(self.layer_devices)

                    # Store panel configuration data in the device item
                    device_item.panel_data = {
                        "model": panel.model,
                        "manufacturer": panel.manufacturer,
                        "panel_type": panel.panel_type,
                        "max_devices": panel.max_devices,
                        "max_circuits": panel.max_circuits,
                        "accessories": panel.accessories,
                    }

                    # Add to history and update UI
                    self.push_history()
                    self.statusBar().showMessage(f"Placed FACP panel: {name}")
                    self.connections_tree.add_panel(name, device_item, panel.panel_type)

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "FACP Placement Error", f"Failed to place FACP panel: {str(e)}"
            )

    def show_properties_for_item(self, item):
        """Selects the given item on the canvas and updates the properties panel."""
        self.view.scene().clearSelection()
        item.setSelected(True)
        self.view.centerOn(item)

    def refresh_devices_on_canvas(self):
        """Refreshes the display of all devices on the canvas based on their layer properties."""
        # Re-fetch layers to get latest properties
        self.layers = db_loader.fetch_layers(db_loader.connect())
        layer_map = {layer["id"]: layer for layer in self.layers}

        for item in self.layer_devices.childItems():
            if isinstance(item, DeviceItem):
                # Update the device's layer object with the latest properties
                if item.layer and item.layer["id"] in layer_map:
                    item.layer = layer_map[item.layer["id"]]
                item.update_layer_properties()
        self.view.scene().update()  # Request a scene update

    def open_wire_spool(self):
        """Open the wire spool dialog to select a wire type."""
        dialog = WireSpoolDialog(self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            selected_wire = dialog.get_selected_wire()
            if selected_wire:
                self.wire_tool.set_wire_type(selected_wire)
                self.statusBar().showMessage(
                    f"Selected wire: {selected_wire['manufacturer']} {selected_wire['type']}"
                )

    def toggle_group(self, group_box, checked):
        for i in range(group_box.layout().count()):
            widget = group_box.layout().itemAt(i).widget()
            if widget is not None:
                widget.setVisible(checked)

    def open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()

    def open_layer_manager(self):
        """Open the layer manager dialog."""
        dialog = LayerManagerDialog(self)
        dialog.exec()

    def show_calculations(self):
        """Open the calculations dialog."""
        dialog = CalculationsDialog(self)
        dialog.exec()

    def show_bom_report(self):
        """Open the BOM report dialog."""
        dialog = BomReportDialog(self)
        dialog.exec()

    def show_device_schedule_report(self):
        """Open the device schedule report dialog."""
        dialog = DeviceScheduleReportDialog(self)
        dialog.exec()

    def generate_riser_diagram(self):
        """Open the riser diagram dialog."""
        dialog = RiserDiagramDialog(self)
        dialog.exec()

    def add_viewport(self):
        """Adds a new viewport to the current paperspace layout."""
        if not self.in_paper_space:
            QtWidgets.QMessageBox.warning(
                self, "Add Viewport", "Please switch to Paper Space first."
            )
            return

        # Create a new viewport item
        new_viewport = ViewportItem(self.scene, QtCore.QRectF(0, 0, 500, 400), self)
        self.paper_scene.addItem(new_viewport)
        self.push_history()
        self.statusBar().showMessage("New viewport added to Paperspace.")

    def show_job_info_dialog(self):
        """Open the job information dialog."""
        dialog = JobInfoDialog(self)
        dialog.exec()

    def place_token(self):
        """Open the token selector dialog and allow placing a token on the canvas, linked to a selected device."""
        selected_device = self._get_selected_device()
        if not selected_device:
            QtWidgets.QMessageBox.warning(
                self, "Place Token", "Please select a device on the canvas first."
            )
            return

        dialog = TokenSelectorDialog(self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            selected_token_string = dialog.get_selected_token()
            if selected_token_string:
                token_item = TokenItem(selected_token_string, selected_device)
                # Place the token relative to the device (e.g., slightly offset)
                token_item.setPos(
                    selected_device.pos() + QtCore.QPointF(20, 20)
                )  # Offset for visibility
                self.layer_sketch.addToGroup(token_item)
                self.push_history()
                self.statusBar().showMessage(
                    f"Placed token '{selected_token_string}' for {selected_device.name}"
                )

    # ---------- view toggles ----------
    def toggle_grid(self, on: bool):
        self.scene.show_grid = bool(on)
        self.scene.update()

    def toggle_snap(self, on: bool):
        self.scene.snap_enabled = bool(on)

    def toggle_crosshair(self, on: bool):
        self.view.show_crosshair = bool(on)

    def toggle_coverage(self, on: bool):
        self.show_coverage = bool(on)
        for it in self.layer_devices.childItems():
            if isinstance(it, DeviceItem):
                try:
                    it.set_coverage_enabled(self.show_coverage)
                except Exception:
                    pass
        self.prefs["show_coverage"] = self.show_coverage
        save_prefs(self.prefs)

    def toggle_placement_coverage(self, on: bool):
        self.prefs["show_placement_coverage"] = bool(on)
        save_prefs(self.prefs)

    # ---------- command bar ----------
    def _run_command(self):
        txt = (self.cmd.text() or "").strip().lower()
        self.cmd.clear()

        def set_draw(mode):
            setattr(self.draw, "layer", self.layer_sketch)
            self.draw.set_mode(mode)

        m = {
            "l": lambda: set_draw(draw_tools.DrawMode.LINE),
            "line": lambda: set_draw(draw_tools.DrawMode.LINE),
            "r": lambda: set_draw(draw_tools.DrawMode.RECT),
            "rect": lambda: set_draw(draw_tools.DrawMode.RECT),
            "rectangle": lambda: set_draw(draw_tools.DrawMode.RECT),
            "c": lambda: set_draw(draw_tools.DrawMode.CIRCLE),
            "circle": lambda: set_draw(draw_tools.DrawMode.CIRCLE),
            "p": lambda: set_draw(draw_tools.DrawMode.POLYLINE),
            "pl": lambda: set_draw(draw_tools.DrawMode.POLYLINE),
            "polyline": lambda: set_draw(draw_tools.DrawMode.POLYLINE),
            "a": lambda: set_draw(draw_tools.DrawMode.ARC3),
            "arc": lambda: set_draw(draw_tools.DrawMode.ARC3),
            "w": self._set_wire_mode,
            "wire": self._set_wire_mode,
            "dim": self.start_dimension,
            "d": self.start_dimension,
            "meas": self.start_measure,
            "m": self.start_measure,
            "off": self.offset_selected_dialog,
            "offset": self.offset_selected_dialog,
            "o": self.offset_selected_dialog,
            "tr": self.start_trim,
            "trim": self.start_trim,
            "ex": self.start_extend,
            "extend": self.start_extend,
            "fi": self.start_fillet,
            "fillet": self.start_fillet,
            "mo": self.start_move,
            "move": self.start_move,
            "co": self.start_copy,
            "copy": self.start_copy,
            "ro": self.start_rotate,
            "rotate": self.start_rotate,
            "mi": self.start_mirror,
            "mirror": self.start_mirror,
            "sc": self.start_scale,
            "scale": self.start_scale,
            "ch": self.start_chamfer,
            "chamfer": self.start_chamfer,
        }
        try:
            # If a draw tool is active, try to parse coordinate input
            if getattr(self.draw, "mode", 0) != 0 and txt:
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
        s = (s or "").strip().lower()
        try:
            base = None
            if self.draw.points:
                base = QtCore.QPointF(self.draw.points[-1])
            else:
                base = QtCore.QPointF(self.view.last_scene_pos)
            ppf = float(self.px_per_ft)
            if s.startswith("@") and "<" in s:
                # relative polar: @r<ang
                r, ang = s[1:].split("<", 1)
                r = float(r)
                ang = float(ang)
                dx = r * ppf * math.cos(math.radians(ang))
                dy = r * ppf * math.sin(math.radians(ang))
                return QtCore.QPointF(base.x() + dx, base.y() + dy)
            if "<" in s:
                # absolute polar: r<ang from origin (0,0)
                r, ang = s.split("<", 1)
                r = float(r)
                ang = float(ang)
                dx = r * ppf * math.cos(math.radians(ang))
                dy = r * ppf * math.sin(math.radians(ang))
                return QtCore.QPointF(dx, dy)
            if s.startswith("@") and "," in s:
                dx, dy = s[1:].split(",", 1)
                dx = float(dx) * ppf
                dy = float(dy) * ppf
                return QtCore.QPointF(base.x() + dx, base.y() + dy)
            if "," in s:
                x, y = s.split(",", 1)
                x = float(x) * ppf
                y = float(y) * ppf
                return QtCore.QPointF(x, y)
        except Exception:
            return None
        return None

    # ---------- OSNAP ----------
    def _set_osnap(self, which: str, val: bool):
        if which == "end":
            self.view.osnap_end = bool(val)
        elif which == "mid":
            self.view.osnap_mid = bool(val)
        elif which == "center":
            self.view.osnap_center = bool(val)
        elif which == "intersect":
            self.view.osnap_intersect = bool(val)
        elif which == "perp":
            self.view.osnap_perp = bool(val)
        # reflect in prefs
        self.prefs[f"osnap_{which}"] = bool(val)
        save_prefs(self.prefs)

    def grid_style_dialog(self):
        dlg = GridStyleDialog(self, scene=self.scene, prefs=self.prefs)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            op, wd, mj = dlg.apply()
            save_prefs(self.prefs)
            self.slider_grid.setValue(int(round(op * 100)))
            self.statusBar().showMessage(
                f"Grid updated (opacity={op:.2f}, width={wd:.1f}, major_every={mj})"
            )

    def set_px_per_ft(self):
        val, ok = QtWidgets.QInputDialog.getDouble(
            self, "Scale", "Pixels per foot", self.px_per_ft, 1.0, 1000.0, 2
        )
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
                committing_poly = (
                    getattr(self.draw, "mode", 0) == draw_tools.DrawMode.POLYLINE
                    and len(getattr(self.draw, "points", [])) >= 2
                )
            except Exception:
                committing_poly = False
            try:
                self.draw.finish()
            except Exception:
                pass
            if committing_poly:
                self.push_history()
        # cancel dimension tool
        if getattr(self, "dim_tool", None):
            try:
                if hasattr(self.dim_tool, "cancel"):
                    self.dim_tool.cancel()
                else:
                    self.dim_tool.active = False
            except Exception:
                pass
        # cancel text tool
        if getattr(self, "text_tool", None):
            try:
                self.text_tool.cancel()
            except Exception:
                pass
        # cancel trim tool
        if getattr(self, "trim_tool", None):
            try:
                self.trim_tool.cancel()
            except Exception:
                pass
        # cancel extend tool
        if getattr(self, "extend_tool", None):
            try:
                self.extend_tool.cancel()
            except Exception:
                pass
        # cancel fillet tool
        if getattr(self, "fillet_tool", None):
            try:
                self.fillet_tool.cancel()
            except Exception:
                pass
        # clear device placement
        self.view.current_proto = None
        if self.view.ghost:
            try:
                self.scene.removeItem(self.view.ghost)
            except Exception:
                pass
            self.view.ghost = None
        self.statusBar().showMessage("Cancelled")

    # ---------- scene menu ----------
    def canvas_menu(self, global_pos):
        menu = QMenu(self)
        view_pt = self.view.mapFromGlobal(global_pos)
        scene_pt = self.view.mapToScene(view_pt)
        item_under = self.scene.itemAt(scene_pt, self.view.transform())

        # Optimize by reducing full scene scans
        selected_devices = [it for it in self.scene.selectedItems() if isinstance(it, DeviceItem)]

        # Context-specific actions for the item directly under the cursor
        if isinstance(item_under, DeviceItem):
            menu.addAction("Select Similar (Type)", lambda: self._select_similar_from(item_under))
            menu.addSeparator()

        # Actions for selection
        if selected_devices:
            menu.addAction(f"Delete {len(selected_devices)} Devices", self.delete_selection)
            menu.addSeparator()
            d = selected_devices[0]
            act_cov = menu.addAction("CoverageΓÇª")
            act_tog = menu.addAction("Toggle Coverage On/Off")
            act_lbl = menu.addAction("Edit LabelΓÇª")
            # Connect these actions later in the function
        else:
            menu.addAction("Select All", self.select_all_items)

        menu.addAction("Clear Selection", self.clear_selection)
        menu.addSeparator()
        menu.addAction("Clear Underlay", self.clear_underlay)

        # Execute and process the chosen action
        act = menu.exec(global_pos)
        if act is None:
            return

        # Handle actions that were connected above
        if selected_devices:
            if act == act_cov:
                dlg = CoverageDialog(self, existing=d.coverage)
                if dlg.exec() == QtWidgets.QDialog.Accepted:
                    for dev in selected_devices:
                        dev.set_coverage(dlg.get_settings(self.px_per_ft))
                    self.push_history()
            elif act == act_tog:
                for dev in selected_devices:
                    if dev.coverage.get("mode", "none") == "none":
                        diam_ft = float(self.prefs.get("default_strobe_diameter_ft", 50.0))
                        dev.set_coverage(
                            {
                                "mode": "strobe",
                                "mount": "ceiling",
                                "computed_radius_ft": max(0.0, diam_ft / 2.0),
                                "px_per_ft": self.px_per_ft,
                            }
                        )
                    else:
                        dev.set_coverage(
                            {"mode": "none", "computed_radius_ft": 0.0, "px_per_ft": self.px_per_ft}
                        )
                self.push_history()
            elif act == act_lbl:
                txt, ok = QtWidgets.QInputDialog.getText(self, "Device Label", "Text:", text=d.name)
                if ok:
                    for dev in selected_devices:
                        dev.set_label_text(txt)
                    self.push_history()

    # ---------- history / serialize ----------
    def serialize_state(self):
        devs = []
        for it in self.layer_devices.childItems():
            if isinstance(it, DeviceItem):
                devs.append(it.to_json())
        # underlay transform
        ut = self.layer_underlay.transform()
        underlay = {
            "m11": ut.m11(),
            "m12": ut.m12(),
            "m13": ut.m13(),
            "m21": ut.m21(),
            "m22": ut.m22(),
            "m23": ut.m23(),
            "m31": ut.m31(),
            "m32": ut.m32(),
            "m33": ut.m33(),
        }
        # DXF layer states
        dxf_layers = {}
        for name, grp in (self._dxf_layers or {}).items():
            # get first child pen color
            color_hex = None
            for ch in grp.childItems():
                try:
                    if hasattr(ch, "pen"):
                        color_hex = ch.pen().color().name()
                        break
                except Exception:
                    pass
            dxf_layers[name] = {
                "visible": bool(grp.isVisible()),
                "locked": bool(grp.data(2004) or False),
                "print": False if grp.data(2003) is False else True,
                "color": color_hex,
                "orig_color": grp.data(2002),
            }

        # sketch geometry
        def _line_json(it: QtWidgets.QGraphicsLineItem):
            l = it.line()
            return {"type": "line", "x1": l.x1(), "y1": l.y1(), "x2": l.x2(), "y2": l.y2()}

        # connections
        connections = self.connections_tree.get_connections()

        def _rect_json(it: QtWidgets.QGraphicsRectItem):
            r = it.rect()
            return {"type": "rect", "x": r.x(), "y": r.y(), "w": r.width(), "h": r.height()}

        def _ellipse_json(it: QtWidgets.QGraphicsEllipseItem):
            r = it.rect()
            return {
                "type": "circle",
                "x": r.center().x(),
                "y": r.center().y(),
                "r": r.width() / 2.0,
            }

        def _path_json(it: QtWidgets.QGraphicsPathItem):
            p = it.path()
            pts = []
            for i in range(p.elementCount()):
                e = p.elementAt(i)
                pts.append({"x": e.x, "y": e.y})
            return {"type": "poly", "pts": pts}

        def _text_json(it: QtWidgets.QGraphicsSimpleTextItem):
            p = it.pos()
            return {"type": "text", "x": p.x(), "y": p.y(), "text": it.text()}

        sketch = []
        for it in self.layer_sketch.childItems():
            if isinstance(it, QtWidgets.QGraphicsLineItem):
                sketch.append(_line_json(it))
            elif isinstance(it, QtWidgets.QGraphicsRectItem):
                sketch.append(_rect_json(it))
            elif isinstance(it, QtWidgets.QGraphicsEllipseItem):
                sketch.append(_ellipse_json(it))
            elif isinstance(it, QtWidgets.QGraphicsPathItem):
                sketch.append(_path_json(it))
            elif isinstance(it, QtWidgets.QGraphicsSimpleTextItem):
                sketch.append(_text_json(it))
            elif isinstance(it, TokenItem):
                sketch.append(it.to_json())
        # wires
        wires = []
        for it in self.layer_wires.childItems():
            if isinstance(it, QtWidgets.QGraphicsPathItem):
                p = it.path()
                if p.elementCount() >= 2:
                    a = p.elementAt(0)
                    b = p.elementAt(1)
                    wires.append({"ax": a.x, "ay": a.y, "bx": b.x, "by": b.y})
        return {
            "grid": int(self.scene.grid_size),
            "snap": bool(self.scene.snap_enabled),
            "px_per_ft": float(self.px_per_ft),
            "snap_step_in": float(self.snap_step_in),
            "grid_opacity": float(self.prefs.get("grid_opacity", 0.25)),
            "grid_width_px": float(self.prefs.get("grid_width_px", 0.0)),
            "grid_major_every": int(self.prefs.get("grid_major_every", 5)),
            "devices": devs,
            "underlay_transform": underlay,
            "dxf_layers": dxf_layers,
            "sketch": sketch,
            "wires": wires,
            "connections": connections,
        }

    def load_state(self, data):
        for it in list(self.layer_devices.childItems()):
            it.scene().removeItem(it)
        for it in list(self.layer_wires.childItems()):
            it.scene().removeItem(it)
        for it in list(self.layer_sketch.childItems()):
            it.scene().removeItem(it)
        self.scene.snap_enabled = bool(data.get("snap", True))
        self.act_view_snap.setChecked(self.scene.snap_enabled)
        self.scene.grid_size = int(data.get("grid", DEFAULT_GRID_SIZE))
        if hasattr(self, "spin_grid"):
            self.spin_grid.setValue(self.scene.grid_size)
        self.px_per_ft = float(data.get("px_per_ft", self.px_per_ft))
        self.snap_step_in = float(data.get("snap_step_in", self.snap_step_in))
        self.prefs["grid_opacity"] = float(
            data.get("grid_opacity", self.prefs.get("grid_opacity", 0.25))
        )
        self.prefs["grid_width_px"] = float(
            data.get("grid_width_px", self.prefs.get("grid_width_px", 0.0))
        )
        self.prefs["grid_major_every"] = int(
            data.get("grid_major_every", self.prefs.get("grid_major_every", 5))
        )
        self.scene.set_grid_style(
            self.prefs["grid_opacity"], self.prefs["grid_width_px"], self.prefs["grid_major_every"]
        )
        self._apply_snap_step_from_inches(self.snap_step_in)

        device_map = {}

        for d in data.get("devices", []):
            it = DeviceItem.from_json(d)
            it.setParentItem(self.layer_devices)
            device_map[it.data(0, QtCore.Qt.UserRole)] = it  # Store device by ID
        # underlay transform
        ut = data.get("underlay_transform")
        if ut:
            tr = QtGui.QTransform(
                ut.get("m11", 1),
                ut.get("m12", 0),
                ut.get("m13", 0),
                ut.get("m21", 0),
                ut.get("m22", 1),
                ut.get("m23", 0),
                ut.get("m31", 0),
                ut.get("m32", 0),
                ut.get("m33", 1),
            )
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
                r = float(s.get("r", 0.0))
                cx = float(s.get("x", 0.0))
                cy = float(s.get("y", 0.0))
                it = QtWidgets.QGraphicsEllipseItem(cx - r, cy - r, 2 * r, 2 * r)
            elif t == "poly":
                pts = [QtCore.QPointF(p["x"], p["y"]) for p in s.get("pts", [])]
                if len(pts) < 2:
                    continue
                path = QtGui.QPainterPath(pts[0])
                for p in pts[1:]:
                    path.lineTo(p)
                it = QtWidgets.QGraphicsPathItem(path)
            elif t == "text":
                it = QtWidgets.QGraphicsSimpleTextItem(s.get("text", ""))
                it.setPos(float(s.get("x", 0.0)), float(s.get("y", 0.0)))
                it.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
            elif t == "token":
                it = TokenItem.from_json(s, device_map)
                if it is None:
                    continue  # Skip if device not found
            else:
                continue
            pen = QtGui.QPen(QtGui.QColor("#e0e0e0"))
            pen.setCosmetic(True)
            if hasattr(it, "setPen"):
                it.setPen(pen)
            it.setZValue(20)
            it.setParentItem(self.layer_sketch)
            it.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
            it.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        if "connections" in state:
            self.connections_tree.load_connections(state["connections"], device_map)
        # restore wires
        for w in data.get("wires", []):
            a = QtCore.QPointF(float(w.get("ax", 0.0)), float(w.get("ay", 0.0)))
            b = QtCore.QPointF(float(w.get("bx", 0.0)), float(w.get("by", 0.0)))
            path = QtGui.QPainterPath(a)
            path.lineTo(b)
            wi = QtWidgets.QGraphicsPathItem(path)
            pen = QtGui.QPen(QtGui.QColor("#2aa36b"))
            pen.setCosmetic(True)
            pen.setWidth(2)
            wi.setPen(pen)
            wi.setZValue(60)
            wi.setParentItem(self.layer_wires)
            wi.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
            wi.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)

    def push_history(self):
        if self.history_index < len(self.history) - 1:
            self.history = self.history[: self.history_index + 1]
        self.history.append(self.serialize_state())
        self.history_index += 1

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.load_state(self.history[self.history_index])
            self.statusBar().showMessage("Undo")

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.load_state(self.history[self.history_index])
            self.statusBar().showMessage("Redo")

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
            self.prop_showcov.setChecked(bool(getattr(d, "coverage_enabled", True)))
            offx = d.label_offset.x() / self.px_per_ft
            offy = d.label_offset.y() / self.px_per_ft
            self.prop_offx.blockSignals(True)
            self.prop_offy.blockSignals(True)
            self.prop_offx.setValue(offx)
            self.prop_offy.setValue(offy)
            self.prop_offx.blockSignals(False)
            self.prop_offy.blockSignals(False)
            # coverage
            cov = d.coverage or {}
            self.prop_mount.setCurrentText(cov.get("mount", "ceiling"))
            mode = cov.get("mode", "none")
            if mode not in ("none", "strobe", "speaker", "smoke"):
                mode = "none"
            self.prop_mode.setCurrentText(mode)
            # strobe candela
            cand = str(cov.get("params", {}).get("candela", ""))
            if cand in {"15", "30", "75", "95", "110", "135", "185"}:
                self.prop_candela.setCurrentText(cand)
            else:
                self.prop_candela.setCurrentText("(custom)")
            size_ft = (
                float(cov.get("computed_radius_ft", 0.0)) * 2.0
                if mode == "strobe"
                else (
                    float(cov.get("params", {}).get("spacing_ft", 0.0))
                    if mode == "smoke"
                    else float(cov.get("computed_radius_ft", 0.0))
                )
            )
            self.prop_size.setValue(max(0.0, size_ft))
        # Always update selection highlight for geometry
        self._update_selection_visuals()

    def _apply_label_offset_live(self):
        d = self._get_selected_device()
        if not d:
            return
        d.set_label_text(self.prop_label.text())
        dx_ft = float(self.prop_offx.value())
        dy_ft = float(self.prop_offy.value())
        d.set_label_offset(dx_ft * self.px_per_ft, dy_ft * self.px_per_ft)
        self.scene.update()

    def _apply_props_clicked(self):
        d = self._get_selected_device()
        if not d:
            return
        d.set_coverage_enabled(bool(self.prop_showcov.isChecked()))
        mode = self.prop_mode.currentText()
        mount = self.prop_mount.currentText()
        sz = float(self.prop_size.value())
        cov = {"mode": mode, "mount": mount, "px_per_ft": self.px_per_ft}
        if mode == "none":
            cov["computed_radius_ft"] = 0.0
        elif mode == "strobe":
            cand_txt = self.prop_candela.currentText()
            if cand_txt != "(custom)":
                try:
                    cand = int(cand_txt)
                    cov.setdefault("params", {})["candela"] = cand
                    cov["computed_radius_ft"] = self._strobe_radius_from_candela(cand)
                except Exception:
                    cov["computed_radius_ft"] = max(0.0, sz / 2.0)
            else:
                cov["computed_radius_ft"] = max(0.0, sz / 2.0)
        elif mode == "smoke":
            spacing_ft = max(0.0, sz)
            cov["params"] = {"spacing_ft": spacing_ft}
            cov["computed_radius_ft"] = spacing_ft / 2.0
        elif mode == "speaker":
            cov["computed_radius_ft"] = max(0.0, sz)
        d.set_coverage(cov)
        self.push_history()
        self.scene.update()

    def _on_mode_changed_props(self, mode: str):
        # Show candela chooser only for strobe
        want = mode == "strobe"
        self.prop_candela.setEnabled(want)

    # ---------- underlay / file ops ----------
    def clear_underlay(self):
        for it in list(self.layer_underlay.childItems()):
            it.scene().removeItem(it)

    # ---------- selection helpers ----------
    def _select_similar_from(self, base_item: QtWidgets.QGraphicsItem):
        try:
            # Device similarity: match symbol or name
            if isinstance(base_item, DeviceItem):
                sym = getattr(base_item, "symbol", None)
                name = getattr(base_item, "name", None)
                for it in self.layer_devices.childItems():
                    if isinstance(it, DeviceItem):
                        if (sym and getattr(it, "symbol", None) == sym) or (
                            name and getattr(it, "name", None) == name
                        ):
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
                items = [
                    it
                    for it in self.scene.items()
                    if not isinstance(it, QtWidgets.QGraphicsItemGroup)
                ]
            t = type(base_item)
            try:
                base_item.setSelected(True)
            except Exception:
                pass
            for it in items:
                try:
                    if type(it) == t:
                        it.setSelected(True)
                except Exception:
                    pass
            self._update_selection_visuals()
        except Exception as ex:
            print(f"Error in _select_similar_from: {ex}")

    def _update_selection_visuals(self):
        # Update visual appearance of selected items
        for it in self.scene.selectedItems():
            try:
                # Add selection highlight if not already present
                if not hasattr(it, "_selection_highlight"):
                    hl = QtWidgets.QGraphicsRectItem()
                    hl.setPen(QtGui.QPen(QtGui.QColor("#ff8c00"), 0))  # Orange highlight
                    hl.setBrush(
                        QtGui.QBrush(QtGui.QColor(255, 140, 0, 50))
                    )  # Semi-transparent fill
                    hl.setZValue(it.zValue() + 1)
                    if isinstance(it, QtWidgets.QGraphicsItemGroup):
                        r = it.childrenBoundingRect()
                    else:
                        r = it.boundingRect()
                    hl.setRect(r)
                    hl.setParentItem(it)
                    it._selection_highlight = hl
            except Exception:
                pass
        # Remove highlight from deselected items
        for it in self.scene.items():
            try:
                if not it.isSelected() and hasattr(it, "_selection_highlight"):
                    it.scene().removeItem(it._selection_highlight)
                    delattr(it, "_selection_highlight")
            except Exception:
                pass

    # ---------- strobe helpers ----------
    def _strobe_radius_from_candela(self, candela: int) -> float:
        # Approximate candela to radius mapping (in feet)
        # Based on NFPA 72 guidelines for candela ratings
        mapping = {
            15: 25.0,  # 15 candela Γëê 25 ft radius
            30: 35.0,  # 30 candela Γëê 35 ft radius
            75: 55.0,  # 75 candela Γëê 55 ft radius
            95: 62.0,  # 95 candela Γëê 62 ft radius
            110: 67.0,  # 110 candela Γëê 67 ft radius
            135: 74.0,  # 135 candela Γëê 74 ft radius
            185: 87.0,  # 185 candela Γëê 87 ft radius
        }
        return mapping.get(candela, 50.0)  # Default to 50 ft if not found

    # ---------- drawing tools ----------
    def _set_wire_mode(self):
        setattr(self.draw, "layer", self.layer_wires)
        self.draw.set_mode(draw_tools.DrawMode.LINE)

    def start_text(self):
        self.text_tool.start()

    def start_mtext(self):
        self.mtext_tool.start()

    def start_freehand(self):
        self.freehand_tool.start()

    def start_leader(self):
        self.leader_tool.start()

    def start_cloud(self):
        self.cloud_tool.start()

    def start_dimension(self):
        self.dim_tool.start()

    def start_measure(self):
        self.measure_tool.start()

    def start_trim(self):
        self.trim_tool.start()

    def finish_trim(self):
        self.trim_tool.finish()
        self.push_history()

    def start_extend(self):
        self.extend_tool.start()

    def start_fillet(self):
        self.fillet_tool.start()

    def start_fillet_radius(self):
        self.fillet_radius_tool.start()

    def start_move(self):
        self.move_tool.start()

    def start_copy(self):
        self.move_tool.start(copy_mode=True)

    def start_rotate(self):
        self.rotate_tool.start()

    def start_mirror(self):
        self.mirror_tool.start()

    def start_scale(self):
        self.scale_tool.start()

    def start_chamfer(self):
        self.chamfer_tool.start()

    def start_wiring(self):
        self.cancel_active_tool()
        self.wire_tool.start()

    def start_underlay_scale_ref(self):
        self.underlay_ref_tool.start()

    def start_underlay_scale_drag(self):
        self.underlay_drag_tool.start()

    # ---------- underlay helpers ----------
    def underlay_scale_factor(self):
        factor, ok = QtWidgets.QInputDialog.getDouble(
            self, "Scale Underlay", "Scale factor:", 1.0, 0.01, 100.0, 4
        )
        if ok:
            try:
                scale_underlay_by_factor(self.layer_underlay, factor)
                self.push_history()
                self.statusBar().showMessage(f"Underlay scaled by factor: {factor:.4f}")
            except Exception as ex:
                QMessageBox.critical(self, "Scale Error", str(ex))

    def center_underlay_in_view(self):
        try:
            # Get the bounding rect of all underlay items
            bounds = QtCore.QRectF()
            for it in self.layer_underlay.childItems():
                bounds = bounds.united(it.sceneBoundingRect())

            if not bounds.isEmpty():
                # Get the current view center
                view_center = self.view.mapToScene(self.view.viewport().rect().center())

                # Calculate the offset needed to center the underlay
                underlay_center = bounds.center()
                offset = view_center - underlay_center

                # Apply the transformation
                tr = self.layer_underlay.transform()
                tr.translate(offset.x(), offset.y())
                self.layer_underlay.setTransform(tr)

                self.push_history()
                self.statusBar().showMessage("Underlay centered in view")
        except Exception as ex:
            QMessageBox.critical(self, "Center Error", str(ex))

    def move_underlay_to_origin(self):
        try:
            # Get the bounding rect of all underlay items
            bounds = QtCore.QRectF()
            for it in self.layer_underlay.childItems():
                bounds = bounds.united(it.sceneBoundingRect())

            if not bounds.isEmpty():
                # Calculate the offset needed to move the underlay to origin
                offset = QtCore.QPointF(-bounds.left(), -bounds.top())

                # Apply the transformation
                tr = self.layer_underlay.transform()
                tr.translate(offset.x(), offset.y())
                self.layer_underlay.setTransform(tr)

                self.push_history()
                self.statusBar().showMessage("Underlay moved to origin")
        except Exception as ex:
            QMessageBox.critical(self, "Move Error", str(ex))

    def reset_underlay_transform(self):
        try:
            # Reset the underlay transform to identity
            self.layer_underlay.setTransform(QtGui.QTransform())
            self.push_history()
            self.statusBar().showMessage("Underlay transform reset")
        except Exception as ex:
            QMessageBox.critical(self, "Reset Error", str(ex))

    # ---------- modify tools ----------
    def offset_selected_dialog(self):
        items = self.scene.selectedItems()
        if not items:
            QMessageBox.information(self, "Offset", "Please select items to offset.")
            return

        distance, ok = QtWidgets.QInputDialog.getDouble(
            self, "Offset", "Distance (ft):", 1.0, -1000.0, 1000.0, 2
        )
        if not ok:
            return

        try:
            # Convert distance to pixels
            distance_px = distance * self.px_per_ft

            # Offset selected items
            for it in items:
                if isinstance(it, QtWidgets.QGraphicsItemGroup):
                    # For groups, offset each child
                    for child in it.childItems():
                        pos = child.pos()
                        child.setPos(pos.x() + distance_px, pos.y() + distance_px)
                else:
                    # For individual items, offset the position
                    pos = it.pos()
                    it.setPos(pos.x() + distance_px, pos.y() + distance_px)

            self.push_history()
            self.statusBar().showMessage(f"Offset {len(items)} items by {distance} ft")
        except Exception as ex:
            QMessageBox.critical(self, "Offset Error", str(ex))

    # ---------- view tools ----------
    def fit_view_to_content(self):
        # Get bounding rect of all content
        bounds = QtCore.QRectF()
        for layer in [self.layer_underlay, self.layer_sketch, self.layer_wires, self.layer_devices]:
            for it in layer.childItems():
                bounds = bounds.united(it.sceneBoundingRect())

        if not bounds.isEmpty():
            # Add some margin
            margin = 100
            bounds.adjust(-margin, -margin, margin, margin)
            self.view.fitInView(bounds, Qt.KeepAspectRatio)
            self.statusBar().showMessage("Fit view to content")
        else:
            # If no content, show default area
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self.statusBar().showMessage("Fit view to default area")

    def change_grid_size(self, size: int):
        self.scene.grid_size = size
        self.scene.update()
        self.prefs["grid"] = size
        save_prefs(self.prefs)

    # ---------- file operations ----------
    def new_project(self):
        # Clear all layers
        for layer in [self.layer_underlay, self.layer_sketch, self.layer_wires, self.layer_devices]:
            for it in list(layer.childItems()):
                layer.scene().removeItem(it)

        # Reset history
        self.history = []
        self.history_index = -1
        self.push_history()

        self.statusBar().showMessage("New project created")

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "AutoFire Files (*.autofire);;All Files (*)"
        )
        if not path:
            return

        try:
            with open(path) as f:
                data = json.load(f)
            self.load_state(data)
            self.statusBar().showMessage(f"Opened project: {os.path.basename(path)}")
        except Exception as ex:
            QMessageBox.critical(self, "Open Error", str(ex))

    def save_project_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", "AutoFire Files (*.autofire);;All Files (*)"
        )
        if not path:
            return

        try:
            data = self.serialize_state()
            with open(path, "w") as f:
                json.dump(data, f)
            self.statusBar().showMessage(f"Project saved: {os.path.basename(path)}")

            # Update prefs
            self.prefs["last_open"] = path
            save_prefs(self.prefs)

        except Exception as ex:
            QMessageBox.critical(self, "Save Error", str(ex))

    def save_project(self):
        if self.prefs["last_open"]:
            try:
                data = self.serialize_state()
                with open(self.prefs["last_open"], "w") as f:
                    json.dump(data, f)
                self.statusBar().showMessage(
                    f"Project saved: {os.path.basename(self.prefs['last_open'])}"
                )
            except Exception as ex:
                QMessageBox.critical(self, "Save Error", str(ex))
        else:
            self.save_project_as()

    # ---------- edit operations ----------
    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.load_state(self.history[self.history_index])
            self.statusBar().showMessage("Undo")

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.load_state(self.history[self.history_index])
            self.statusBar().showMessage("Redo")

    # ---------- item operations ----------
    def add_device(self, device: DeviceItem):
        try:
            self.layer_devices.addItem(device)
            self.push_history()
            self.statusBar().showMessage(f"Added device: {device.name}")
        except Exception as ex:
            QMessageBox.critical(self, "Add Device Error", str(ex))

    def remove_selected_items(self):
        items = self.scene.selectedItems()
        if not items:
            return

        try:
            for it in items:
                it.scene().removeItem(it)
            self.push_history()
            self.statusBar().showMessage(f"Removed {len(items)} items")
        except Exception as ex:
            QMessageBox.critical(self, "Remove Items Error", str(ex))

    def copy_selected_items(self):
        items = self.scene.selectedItems()
        if not items:
            return

        try:
            self.clipboard = [it.clone() for it in items]
            self.statusBar().showMessage(f"Copied {len(items)} items")
        except Exception as ex:
            QMessageBox.critical(self, "Copy Items Error", str(ex))

    def paste_items(self):
        if not self.clipboard:
            return

        try:
            # Create a group to hold the pasted items
            group = QtWidgets.QGraphicsItemGroup()

            # Add each item to the group and to the appropriate layer
            for it in self.clipboard:
                it.setPos(it.pos().x() + 20, it.pos().y() + 20)
                group.addToGroup(it)
                if isinstance(it, DeviceItem):
                    self.layer_devices.addItem(it)
                elif isinstance(it, QtWidgets.QGraphicsPathItem):  # Wire items are path items
                    self.layer_wires.addItem(it)
                else:
                    # For underlay items, just ensure they're in the right layer
                    # Underlay items are already in self.layer_underlay
                    pass

            # Add the group to the scene
            self.scene.addItem(group)

            # Select the pasted items
            self.scene.clearSelection()
            for it in group.childItems():
                it.setSelected(True)

            self.push_history()
            self.statusBar().showMessage(f"Pasted {len(self.clipboard)} items")
        except Exception as ex:
            QMessageBox.critical(self, "Paste Items Error", str(ex))

    def offset_selected_items(self):
        items = self.scene.selectedItems()
        if not items:
            return

        distance, ok = QtWidgets.QInputDialog.getDouble(
            self, "Offset", "Distance (ft):", 1.0, -1000.0, 1000.0, 2
        )
        if not ok:
            return

        try:
            # Convert distance to pixels
            distance_px = distance * self.px_per_ft

            # Offset selected items
            for it in items:
                if isinstance(it, QtWidgets.QGraphicsItemGroup):
                    # For groups, offset each child
                    for child in it.childItems():
                        pos = child.pos()
                        child.setPos(pos.x() + distance_px, pos.y() + distance_px)
                else:
                    # For individual items, offset the position
                    pos = it.pos()
                    it.setPos(pos.x() + distance_px, pos.y() + distance_px)

            self.push_history()
            self.statusBar().showMessage(f"Offset {len(items)} items by {distance} ft")
        except Exception as ex:
            QMessageBox.critical(self, "Offset Error", str(ex))

    # ---------- view tools ----------
    def fit_view_to_content(self):
        # Get bounding rect of all content
        bounds = QtCore.QRectF()
        for layer in [self.layer_underlay, self.layer_sketch, self.layer_wires, self.layer_devices]:
            for it in layer.childItems():
                bounds = bounds.united(it.sceneBoundingRect())

        if not bounds.isEmpty():
            # Add some margin
            margin = 100
            bounds.adjust(-margin, -margin, margin, margin)
            self.view.fitInView(bounds, Qt.KeepAspectRatio)
            self.statusBar().showMessage("Fit view to content")
        else:
            # If no content, show default area
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self.statusBar().showMessage("Fit view to default area")

    # ---------- import/export ----------

    def show_circuit_properties(self):
        """Open the circuit properties dialog."""
        try:
            from app.dialogs.circuit_properties import CircuitPropertiesDialog

            dialog = CircuitPropertiesDialog(self)
            dialog.exec()
        except Exception as e:
            QtWidgets.QMessageBox.information(
                self, "Circuit Properties", f"Circuit properties dialog not available: {str(e)}"
            )

    def zoom_in(self):
        """Zoom in."""
        self.view.scale(1.15, 1.15)

    def zoom_out(self):
        """Zoom out."""
        self.view.scale(1 / 1.15, 1 / 1.15)

    def zoom_to_selection(self):
        """Zoom to selected items."""
        # Get bounding rect of selected items
        bounds = QtCore.QRectF()
        for item in self.scene.selectedItems():
            bounds = bounds.united(item.sceneBoundingRect())

        if not bounds.isEmpty():
            # Add some margin
            margin = 50
            bounds.adjust(-margin, -margin, margin, margin)
            self.view.fitInView(bounds, Qt.AspectRatioMode.KeepAspectRatio)
            self.statusBar().showMessage("Zoomed to selection")
        else:
            self.statusBar().showMessage("No selection to zoom to")

    def show_user_guide(self):
        """Show the user guide."""
        QtWidgets.QMessageBox.information(
            self, "User Guide", "User guide functionality would be implemented here."
        )

    def show_about(self):
        """Show the about dialog."""
        QtWidgets.QMessageBox.about(
            self, "About Auto-Fire", f"Auto-Fire CAD Application\nVersion: {APP_VERSION}"
        )

    # ---------- import/export ----------
    def import_dxf_underlay(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import DXF", "", "DXF Files (*.dxf);;All Files (*)"
        )
        if not path:
            return

        try:
            # Import DXF file
            groups = dxf_import.import_dxf(path)

            # Add groups to underlay layer
            for name, group in groups.items():
                group.setParentItem(self.layer_underlay)
                self._dxf_layers[name] = group

            self._refresh_dxf_layers_dock()
            self.push_history()
            self.statusBar().showMessage(f"Imported DXF: {os.path.basename(path)}")
        except Exception as ex:
            QMessageBox.critical(self, "Import Error", str(ex))

    def import_pdf_underlay(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import PDF", "", "PDF Files (*.pdf);;All Files (*)"
        )
        if not path:
            return

        try:
            # For now, just show a message that PDF import is not yet implemented
            QMessageBox.information(self, "PDF Import", "PDF import is not yet implemented.")
        except Exception as ex:
            QMessageBox.critical(self, "Import Error", str(ex))

    def export_png(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export PNG", "", "PNG Files (*.png);;All Files (*)"
        )
        if not path:
            return

        try:
            # Create a pixmap to render the scene
            rect = self.scene.sceneRect()
            pixmap = QtGui.QPixmap(int(rect.width()), int(rect.height()))
            pixmap.fill(Qt.white)

            # Render the scene to the pixmap
            painter = QtGui.QPainter(pixmap)
            self.scene.render(painter, QtCore.QRectF(), rect)
            painter.end()

            # Save the pixmap
            pixmap.save(path, "PNG")
            self.statusBar().showMessage(f"Exported PNG: {os.path.basename(path)}")
        except Exception as ex:
            QMessageBox.critical(self, "Export Error", str(ex))

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", "", "PDF Files (*.pdf);;All Files (*)"
        )
        if not path:
            return

        try:
            # For now, just show a message that PDF export is not yet implemented
            QMessageBox.information(self, "PDF Export", "PDF export is not yet implemented.")
        except Exception as ex:
            QMessageBox.critical(self, "Export Error", str(ex))

    def export_device_schedule_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Device Schedule", "", "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return

        try:
            # Count devices by name/symbol/manufacturer/model
            counts = {}
            for it in self.layer_devices.childItems():
                if isinstance(it, DeviceItem):
                    key = (
                        it.name,
                        it.symbol,
                        getattr(it, "manufacturer", ""),
                        getattr(it, "part_number", ""),
                    )
                    counts[key] = counts.get(key, 0) + 1

            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Name", "Symbol", "Manufacturer", "Model", "Qty"])
                for (name, sym, mfr, model), qty in sorted(counts.items()):
                    w.writerow([name, sym, mfr, model, qty])

            self.statusBar().showMessage(f"Exported schedule: {os.path.basename(path)}")
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
        # Create legend items
        legend_group = QtWidgets.QGraphicsItemGroup()
        legend_group.setZValue(200)  # High z-value to stay on top
        legend_group.setParentItem(self.layer_overlay)

        # Background rectangle
        bg_rect = QtWidgets.QGraphicsRectItem(0, 0, 300, len(counts) * row_h + 30)
        bg_pen = QtGui.QPen(QtGui.QColor("#000000"))
        bg_brush = QtGui.QBrush(QtGui.QColor("#ffffff"))
        bg_rect.setPen(bg_pen)
        bg_rect.setBrush(bg_brush)
        bg_rect.setParentItem(legend_group)

        # Title
        title = QtWidgets.QGraphicsSimpleTextItem("Device Legend")
        title.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
        title.setPos(10, 5)
        title.setParentItem(legend_group)

        # Legend entries
        y = 30
        for (name, symbol), qty in sorted(counts.items()):
            text = f"{name} ({symbol}): {qty}"
            item = QtWidgets.QGraphicsSimpleTextItem(text)
            item.setFont(QtGui.QFont("Arial", 10))
            item.setPos(10, y)
            item.setParentItem(legend_group)
            y += row_h

        # Position the legend
        legend_group.setPos(x0, y0)

        self.statusBar().showMessage(f"Placed legend with {len(counts)} entries")

    # ---------- layout tools ----------
    def add_page_frame(self):
        try:
            pf = PageFrame(
                self.px_per_ft,
                size_name=self.prefs.get("page_size", "Letter"),
                orientation=self.prefs.get("page_orient", "Landscape"),
                margin_in=self.prefs.get("page_margin_in", 0.5),
            )
            pf.setParentItem(self.layer_underlay)
            self.page_frame = pf
            self.push_history()
            self.statusBar().showMessage("Added page frame")
        except Exception as ex:
            QMessageBox.critical(self, "Page Frame Error", str(ex))

    def remove_page_frame(self):
        if self.page_frame:
            try:
                self.page_frame.scene().removeItem(self.page_frame)
                self.page_frame = None
                self.push_history()
                self.statusBar().showMessage("Removed page frame")
            except Exception as ex:
                QMessageBox.critical(self, "Page Frame Error", str(ex))

    def add_or_update_title_block(self):
        try:
            if not self.title_block:
                self.title_block = TitleBlock()
                self.title_block.setParentItem(self.layer_underlay)
            # Update with current info
            self.title_block.update_content(
                {
                    "project": "Untitled Project",
                    "date": QtCore.QDate.currentDate().toString("MM/dd/yyyy"),
                    "scale": f"1\" = {int(12/self.px_per_ft)}'",
                    "sheet": "1 of 1",
                }
            )
            self.push_history()
            self.statusBar().showMessage("Added/updated title block")
        except Exception as ex:
            QMessageBox.critical(self, "Title Block Error", str(ex))

    def page_setup_dialog(self):
        # For now, just show a message that page setup is not yet implemented
        QMessageBox.information(self, "Page Setup", "Page setup is not yet implemented.")

    def add_viewport(self):
        try:
            # Create a viewport item
            vp = ViewportItem(self.px_per_ft)
            vp.setParentItem(self.layer_underlay)
            # Position it in the view
            try:
                vc = self.view.mapToScene(self.view.viewport().rect().center())
                vp.setPos(vc.x() - 100, vc.y() - 75)
            except Exception:
                vp.setPos(100, 100)
            self.push_history()
            self.statusBar().showMessage("Added viewport")
        except Exception as ex:
            QMessageBox.critical(self, "Viewport Error", str(ex))

    def _init_sheet_manager(self):
        # Clear existing sheets if any
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) != "Model":  # Don't remove the Model tab
                self.tab_widget.removeTab(i)

        self.sheets = []
        # Add a default paperspace sheet
        self.add_paperspace_sheet("Layout1")

        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        if self.tab_widget.tabText(index) == "Model":
            self.toggle_paper_space(False)
        else:
            self.toggle_paper_space(True)
            # Set the current paperspace scene based on the selected tab
            # This will require storing the scene in the tab's widget or data
            # For now, we'll just use the default paper_scene
            self.view.setScene(self.paper_scene)

    def add_paperspace_sheet(self, name):
        # Create a new QGraphicsView for the paperspace sheet
        paperspace_view = QtWidgets.QGraphicsView(self.paper_scene)
        paperspace_view.setRenderHints(
            QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.TextAntialiasing
        )
        paperspace_view.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)
        paperspace_view.setMouseTracking(True)
        paperspace_view.setBackgroundBrush(QtGui.QColor(20, 22, 26))

        self.tab_widget.addTab(paperspace_view, name)
        self.sheets.append(
            {"name": name, "view": paperspace_view, "scene": self.paper_scene}
        )  # Store view and scene

    def toggle_paper_space(self, on: bool):
        self.in_paper_space = bool(on)
        self.act_paperspace.setChecked(on)
        # Update UI to reflect paper space mode
        if on:
            self.space_badge.setText("PAPER SPACE")
            self.space_badge.setStyleSheet("QLabel { color: #ff9e64; font-weight: bold; }")
        else:
            self.space_badge.setText("MODEL SPACE")
            self.space_badge.setStyleSheet("QLabel { color: #7dcfff; font-weight: bold; }")
        self.scene.update()

    def set_print_scale(self, inches_per_ft: float):
        self.prefs["print_in_per_ft"] = inches_per_ft
        self.prefs["print_dpi"] = 300  # Default DPI
        save_prefs(self.prefs)
        # Update scale badge
        self.scale_badge.setText(f"Scale: {inches_per_ft}\" = 1'")
        self.statusBar().showMessage(f"Print scale set to {inches_per_ft}\" = 1'")

    def set_print_scale_custom(self):
        current = float(self.prefs.get("print_in_per_ft", 0.25))
        value, ok = QtWidgets.QInputDialog.getDouble(
            self, "Custom Scale", "Inches per foot:", current, 0.01, 12.0, 4
        )
        if ok:
            self.set_print_scale(value)

    # ---------- help tools ----------
    def show_user_guide(self):
        # For now, just show a message that user guide is not yet implemented
        QMessageBox.information(self, "User Guide", "User guide is not yet implemented.")

    def show_shortcuts(self):
        msg = """CAD-Style Shortcuts:
L - Draw Line
R - Draw Rectangle
C - Draw Circle
P - Draw Polyline
A - Draw Arc (3-Point)
W - Draw Wire
T - Text Tool
M - Measure Tool
D - Dimension Tool
O - Offset Selected
X - Toggle Crosshair

F2 - Fit View to Content
Esc - Cancel Active Tool
Space - Pan View
Shift - Ortho Mode
"""
        QMessageBox.information(self, "Keyboard Shortcuts", msg)

    def show_about(self):
        msg = f"""{APP_TITLE}

A CAD application for fire alarm system design.

Version: {APP_VERSION}
"""
        QMessageBox.about(self, "About Auto-Fire", msg)

    # ---------- device operations ----------
    def delete_selection(self):
        items = self.scene.selectedItems()
        if not items:
            return

        try:
            for it in items:
                it.scene().removeItem(it)
            self.push_history()
            self.statusBar().showMessage(f"Deleted {len(items)} items")
        except Exception as ex:
            QMessageBox.critical(self, "Delete Error", str(ex))


def create_window():
    """Factory function to create the main application window.

    This function is used by the new frontend bootstrap system
    to create the main window with enhanced tool integration.

    Returns:
        MainWindow: The main application window instance
    """
    return MainWindow()


def main():
    app = QApplication(sys.argv)

    # Set application information
    app.setApplicationName("Auto-Fire")
    app.setApplicationVersion(APP_VERSION)

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
