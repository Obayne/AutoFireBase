# tools/apply_inline_050_cadA.py
# Writes CAD/units upgrade files into the project.
import os, io, sys, textwrap, json, pathlib

FILES = {
r"app\units.py": r'''
import math

IN_PER_FT = 12.0

def ft_to_inches(ft: float) -> float:
    return ft * IN_PER_FT

def inches_to_ft(inches: float) -> float:
    return inches / IN_PER_FT

def px_to_ft(px: float, px_per_ft: float) -> float:
    return px / px_per_ft

def ft_to_px(ft: float, px_per_ft: float) -> float:
    return ft * px_per_ft

def fmt_ft_inches(ft_val: float) -> str:
    neg = ft_val < 0
    ft_val = abs(ft_val)
    whole_ft = int(ft_val)
    inches = round((ft_val - whole_ft) * 12.0, 2)
    return f"-{whole_ft}' {inches:.2f}\"" if neg else f"{whole_ft}' {inches:.2f}\""

def from_db_spherical(db_at_1m: float, target_db: float, px_per_ft: float) -> float:
    """Return radius in *pixels* using 20*log10(r/reference). Uses 1m≈3.28084ft ref."""
    if db_at_1m <= 0: return 0.0
    if target_db >= db_at_1m: return 0.0
    ratio = 10 ** ((db_at_1m - target_db) / 20.0)  # r @ 1m reference
    r_ft = ratio * 3.28084
    return r_ft * px_per_ft

def from_db_per_10ft(db_at_10ft: float, target_db: float, loss_per_10ft: float, px_per_ft: float) -> float:
    """Simple linear-per-10ft model (designer-style rule)."""
    if db_at_10ft <= 0: return 0.0
    if target_db >= db_at_10ft: return 0.0
    steps = (db_at_10ft - target_db) / max(loss_per_10ft, 0.1)
    r_ft = 10.0 * steps
    return r_ft * px_per_ft

def strobe_radius_from_cd_lux(candela: float, lux: float, px_per_ft: float) -> float:
    if candela <= 0 or lux <= 0: return 0.0
    r_m = math.sqrt(candela / lux)
    r_ft = r_m * 3.28084
    return r_ft * px_per_ft
''',

r"app\dialogs\coverage.py": r'''
from PySide6 import QtWidgets, QtCore
from app import units

class CoverageDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, existing=None):
        super().__init__(parent)
        self.setWindowTitle("Device Coverage")
        self.setModal(True)
        self.setMinimumWidth(420)

        # Mode + mounting
        self.cmb_mode = QtWidgets.QComboBox(); self.cmb_mode.addItems(["none","manual","speaker","strobe"])
        self.cmb_mount = QtWidgets.QComboBox(); self.cmb_mount.addItems(["ceiling","wall"])

        # Manual radius (feet)
        self.spin_radius_ft = QtWidgets.QDoubleSpinBox(); self.spin_radius_ft.setRange(0, 10000); self.spin_radius_ft.setDecimals(2); self.spin_radius_ft.setValue(25.0)

        # Speaker models
        self.cmb_spk_model = QtWidgets.QComboBox(); self.cmb_spk_model.addItems(["physics (20log)","per 10 ft loss"])
        self.spin_db_ref = QtWidgets.QDoubleSpinBox(); self.spin_db_ref.setRange(20, 140); self.spin_db_ref.setValue(95); self.lbl_db_ref = QtWidgets.QLabel("dB @ 1m")
        self.spin_db_target = QtWidgets.QDoubleSpinBox(); self.spin_db_target.setRange(20, 140); self.spin_db_target.setValue(75)
        self.spin_db_loss10 = QtWidgets.QDoubleSpinBox(); self.spin_db_loss10.setRange(0.1, 40); self.spin_db_loss10.setValue(6.0); self.spin_db_loss10.setDecimals(1)

        # Strobe
        self.spin_cd = QtWidgets.QDoubleSpinBox(); self.spin_cd.setRange(0, 100000); self.spin_cd.setValue(177)
        self.spin_lux = QtWidgets.QDoubleSpinBox(); self.spin_lux.setRange(0.01, 1000); self.spin_lux.setDecimals(2); self.spin_lux.setValue(0.2)

        # Scale
        self.spin_px_per_ft = QtWidgets.QDoubleSpinBox(); self.spin_px_per_ft.setRange(1, 2000); self.spin_px_per_ft.setValue(12.0)

        form = QtWidgets.QFormLayout()
        form.addRow("Mode", self.cmb_mode)
        form.addRow("Mount", self.cmb_mount)
        form.addRow(QtWidgets.QLabel("<b>Manual</b>"))
        form.addRow("Radius (ft)", self.spin_radius_ft)
        form.addRow(QtWidgets.QLabel("<b>Speaker</b>"))
        form.addRow("Model", self.cmb_spk_model)
        form.addRow(self.lbl_db_ref, self.spin_db_ref)
        form.addRow("Target dB", self.spin_db_target)
        form.addRow("Loss per 10ft (dB)", self.spin_db_loss10)
        form.addRow(QtWidgets.QLabel("<b>Strobe</b>"))
        form.addRow("Candela (cd)", self.spin_cd)
        form.addRow("Target illuminance (lux)", self.spin_lux)
        form.addRow(QtWidgets.QLabel("<b>Scale</b>"))
        form.addRow("Pixels per foot", self.spin_px_per_ft)

        self.lbl_calc = QtWidgets.QLabel("")
        form.addRow("Computed radius (ft)", self.lbl_calc)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)

        main = QtWidgets.QVBoxLayout(self)
        main.addLayout(form); main.addWidget(btns)

        self.cmb_spk_model.currentTextChanged.connect(self._on_spk_model_changed)
        for w in (self.spin_db_ref, self.spin_db_target, self.spin_db_loss10, self.spin_cd, self.spin_lux, self.spin_radius_ft, self.spin_px_per_ft, self.cmb_mode):
            for sig in ("valueChanged","currentTextChanged"):
                try: getattr(w, sig).connect(self._recalc)
                except Exception: pass
        self._on_spk_model_changed()

        if existing:
            self.cmb_mode.setCurrentText(existing.get("mode","none"))
            self.cmb_mount.setCurrentText(existing.get("mount","ceiling"))
            self.spin_radius_ft.setValue(float(existing.get("radius_ft", 25.0)))
            sp = existing.get("speaker", {})
            self.cmb_spk_model.setCurrentText(sp.get("model","physics (20log)"))
            self.spin_db_ref.setValue(float(sp.get("db_ref",95)))
            self.spin_db_target.setValue(float(sp.get("target_db",75)))
            self.spin_db_loss10.setValue(float(sp.get("loss10",6.0)))
            st = existing.get("strobe", {})
            self.spin_cd.setValue(float(st.get("candela",177)))
            self.spin_lux.setValue(float(st.get("target_lux",0.2)))
            self.spin_px_per_ft.setValue(float(existing.get("px_per_ft",12.0)))

        self._recalc()

    def _on_spk_model_changed(self):
        if self.cmb_spk_model.currentText()=="physics (20log)":
            self.lbl_db_ref.setText("dB @ 1m"); self.spin_db_loss10.setEnabled(False)
        else:
            self.lbl_db_ref.setText("dB @ 10ft"); self.spin_db_loss10.setEnabled(True)
        self._recalc()

    def _recalc(self):
        mode = self.cmb_mode.currentText()
        pxpf = self.spin_px_per_ft.value()
        ft_val = 0.0
        if mode == "manual":
            ft_val = self.spin_radius_ft.value()
        elif mode == "speaker":
            if self.cmb_spk_model.currentText()=="physics (20log)":
                px = units.from_db_spherical(self.spin_db_ref.value(), self.spin_db_target.value(), pxpf)
            else:
                px = units.from_db_per_10ft(self.spin_db_ref.value(), self.spin_db_target.value(), self.spin_db_loss10.value(), pxpf)
            ft_val = units.px_to_ft(px, pxpf)
        elif mode == "strobe":
            px = units.strobe_radius_from_cd_lux(self.spin_cd.value(), self.spin_lux.value(), pxpf)
            ft_val = units.px_to_ft(px, pxpf)
        self.lbl_calc.setText(f"{ft_val:.2f}")

    def get_settings(self):
        pxpf = self.spin_px_per_ft.value()
        mode = self.cmb_mode.currentText()
        data = {
            "mode": mode,
            "mount": self.cmb_mount.currentText(),
            "radius_ft": self.spin_radius_ft.value(),
            "px_per_ft": pxpf,
            "speaker": {"model": self.cmb_spk_model.currentText(), "db_ref": self.spin_db_ref.value(), "target_db": self.spin_db_target.value(), "loss10": self.spin_db_loss10.value()},
            "strobe": {"candela": self.spin_cd.value(), "target_lux": self.spin_lux.value()},
        }
        if mode == "speaker":
            if data["speaker"]["model"]=="physics (20log)":
                data["computed_radius_px"] = units.from_db_spherical(data["speaker"]["db_ref"], data["speaker"]["target_db"], pxpf)
            else:
                data["computed_radius_px"] = units.from_db_per_10ft(data["speaker"]["db_ref"], data["speaker"]["target_db"], data["speaker"]["loss10"], pxpf)
        elif mode == "strobe":
            data["computed_radius_px"] = units.strobe_radius_from_cd_lux(data["strobe"]["candela"], data["strobe"]["target_lux"], pxpf)
        else:
            data["computed_radius_px"] = units.ft_to_px(data["radius_ft"], pxpf)
        return data
''',

r"app\dialogs\array.py": r'''
from PySide6 import QtWidgets
from app import units

class ArrayDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, default_px_per_ft=12.0):
        super().__init__(parent)
        self.setWindowTitle("Place Array")
        self.setModal(True); self.setMinimumWidth(360)

        self.spin_rows = QtWidgets.QSpinBox(); self.spin_rows.setRange(1, 500); self.spin_rows.setValue(3)
        self.spin_cols = QtWidgets.QSpinBox(); self.spin_cols.setRange(1, 500); self.spin_cols.setValue(3)
        self.spin_spacing_ft = QtWidgets.QDoubleSpinBox(); self.spin_spacing_ft.setRange(0.1, 1000); self.spin_spacing_ft.setValue(30.0); self.spin_spacing_ft.setDecimals(2)
        self.spin_px_per_ft = QtWidgets.QDoubleSpinBox(); self.spin_px_per_ft.setRange(1, 2000); self.spin_px_per_ft.setValue(default_px_per_ft)
        self.chk_use_cov = QtWidgets.QCheckBox("Use selected device coverage tile for spacing")

        form = QtWidgets.QFormLayout()
        form.addRow("Rows", self.spin_rows)
        form.addRow("Columns", self.spin_cols)
        form.addRow("Spacing (ft)", self.spin_spacing_ft)
        form.addRow("Pixels per foot", self.spin_px_per_ft)
        form.addRow(self.chk_use_cov)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)

        main = QtWidgets.QVBoxLayout(self)
        main.addLayout(form); main.addWidget(btns)

    def get_params(self):
        return {
            "rows": self.spin_rows.value(),
            "cols": self.spin_cols.value(),
            "spacing_px": units.ft_to_px(self.spin_spacing_ft.value(), self.spin_px_per_ft.value()),
            "use_coverage_tile": self.chk_use_cov.isChecked(),
        }
''',

r"app\tools\array.py": r'''
from PySide6 import QtWidgets, QtCore
from app.dialogs.array import ArrayDialog
from app.device import DeviceItem

class ArrayTool:
    def __init__(self, window, layer_devices):
        self.win = window
        self.layer_devices = layer_devices

    def run(self):
        proto = self.win.view.current_proto
        if not proto:
            QtWidgets.QMessageBox.information(self.win, "Array", "Select a device in the palette first.")
            return
        dlg = ArrayDialog(self.win, default_px_per_ft=self.win.px_per_ft)
        if dlg.exec()!=QtWidgets.QDialog.Accepted: return
        p = dlg.get_params()
        self._place_array(proto, p["rows"], p["cols"], p["spacing_px"], p["use_coverage_tile"])

    def _place_array(self, proto, rows, cols, spacing_px, use_coverage_tile):
        center = self.win.view.mapToScene(self.win.view.viewport().rect().center())
        if use_coverage_tile:
            temp = DeviceItem(center.x(), center.y(), proto["symbol"], proto["name"], proto.get("manufacturer",""), proto.get("part_number",""))
            temp.setParentItem(self.layer_devices)
            if temp.coverage.get("mode")!="none" and temp.coverage.get("computed_radius_px",0)>0:
                spacing_px = temp.coverage.get("computed_radius_px",0) * 2.0
            self.layer_devices.scene().removeItem(temp)

        start_x = center.x() - (cols-1)*spacing_px/2.0
        start_y = center.y() - (rows-1)*spacing_px/2.0
        for r in range(rows):
            for c in range(cols):
                x = start_x + c*spacing_px
                y = start_y + r*spacing_px
                it = DeviceItem(x, y, proto["symbol"], proto["name"], proto.get("manufacturer",""), proto.get("part_number",""))
                it.setParentItem(self.layer_devices)
        self.win.push_history()
''',

r"app\device.py": r'''
from PySide6 import QtCore, QtGui, QtWidgets

class DeviceItem(QtWidgets.QGraphicsItemGroup):
    def __init__(self, x: float, y: float, symbol: str, name: str, manufacturer: str = "", part_number: str = ""):
        super().__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.symbol = symbol
        self.name = name
        self.manufacturer = manufacturer
        self.part_number = part_number

        # Label offset (CAD-friendly)
        self.label_offset = QtCore.QPointF(12, -14)

        # Base glyph
        self._glyph = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
        pen = QtGui.QPen(Qt.black); pen.setCosmetic(True)
        self._glyph.setPen(pen)
        self._glyph.setBrush(QtGui.QBrush(Qt.white))
        self.addToGroup(self._glyph)

        # Label
        self._label = QtWidgets.QGraphicsSimpleTextItem(self.name)
        self._label.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self._label.setPos(self.label_offset)
        self.addToGroup(self._label)

        # Coverage overlay
        self.coverage = {"mode":"none","mount":"ceiling","radius_ft":0.0,"px_per_ft":12.0,
                         "speaker":{"model":"physics (20log)","db_ref":95.0,"target_db":75.0,"loss10":6.0},
                         "strobe":{"candela":177.0,"target_lux":0.2},
                         "computed_radius_px": 0.0}
        self._cov_circle = None
        self._cov_square = None   # for ceiling strobe: circle inside square
        self._cov_rect = None     # for wall: rectangle (simplified)

        self.setPos(x, y)

    def set_label_text(self, text: str):
        self._label.setText(text)

    def set_label_offset(self, dx: float, dy: float):
        self.label_offset = QtCore.QPointF(dx, dy)
        self._label.setPos(self.label_offset)

    # -------- coverage drawing ----------
    def set_coverage(self, settings: dict):
        if not settings: return
        self.coverage.update(settings)
        self._update_coverage_items()

    def _ensure_cov_items(self):
        if self._cov_circle is None:
            self._cov_circle = QtWidgets.QGraphicsEllipseItem(); self._cov_circle.setParentItem(self); self._cov_circle.setZValue(-5)
            pen = QtGui.QPen(QtGui.QColor(50,120,255,200)); pen.setStyle(QtCore.Qt.DashLine); pen.setCosmetic(True)
            self._cov_circle.setPen(pen); self._cov_circle.setBrush(QtGui.QColor(50,120,255,60))
        if self._cov_square is None:
            self._cov_square = QtWidgets.QGraphicsRectItem(); self._cov_square.setParentItem(self); self._cov_square.setZValue(-6)
            pen = QtGui.QPen(QtGui.QColor(50,120,255,120)); pen.setStyle(QtCore.Qt.DotLine); pen.setCosmetic(True)
            self._cov_square.setPen(pen); self._cov_square.setBrush(QtGui.QColor(50,120,255,30))
        if self._cov_rect is None:
            self._cov_rect = QtWidgets.QGraphicsRectItem(); self._cov_rect.setParentItem(self); self._cov_rect.setZValue(-6)
            pen = QtGui.QPen(QtGui.QColor(50,120,255,120)); pen.setStyle(QtCore.Qt.DotLine); pen.setCosmetic(True)
            self._cov_rect.setPen(pen); self._cov_rect.setBrush(QtGui.QColor(50,120,255,30))

    def _update_coverage_items(self):
        mode = self.coverage.get("mode","none")
        mount = self.coverage.get("mount","ceiling")
        r_px = float(self.coverage.get("computed_radius_px") or 0.0)

        # Hide all first
        for it in (self._cov_circle, self._cov_square, self._cov_rect):
            if it: it.setVisible(False)

        if mode=="none" or r_px <= 0:
            return

        self._ensure_cov_items()
        # Always draw circle
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
''',

r"app\main.py": r'''
import os, json, zipfile
import ezdxf

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
from app.tools import draw as draw_tools
from app.tools.array import ArrayTool
from app.dialogs.coverage import CoverageDialog
from app import units

APP_VERSION = "0.5.0-cadA"
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

        # Crosshair overlay
        self.cross_v = QtWidgets.QGraphicsLineItem(); self.cross_h = QtWidgets.QGraphicsLineItem()
        pen = QtGui.QPen(QtGui.QColor(150,150,150,170)); pen.setCosmetic(True); pen.setStyle(Qt.DashLine)
        self.cross_v.setPen(pen); self.cross_h.setPen(pen)
        self.cross_v.setParentItem(self.overlay_group); self.cross_h.setParentItem(self.overlay_group)
        self.show_crosshair = True

    def set_current_device(self, proto: dict):
        self.current_proto = proto

    def _update_crosshair(self, sp: QPointF):
        if not self.show_crosshair: return
        rect = self.scene().sceneRect()
        self.cross_v.setLine(sp.x(), rect.top(), sp.x(), rect.bottom())
        self.cross_h.setLine(rect.left(), sp.y(), rect.right(), sp.y())
        # status in ft/in
        dx_ft = units.px_to_ft(sp.x(), self.win.px_per_ft)
        dy_ft = units.px_to_ft(sp.y(), self.win.px_per_ft)
        self.win.statusBar().showMessage(f"x={units.fmt_ft_inches(dx_ft)}   y={units.fmt_ft_inches(dy_ft)}   scale={self.win.px_per_ft:.2f} px/ft")

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
        self._update_crosshair(sp)
        if getattr(self.win, "draw", None): self.win.draw.on_mouse_move(sp, shift_ortho=self.ortho)
        super().mouseMoveEvent(e)

    def mousePressEvent(self, e: QtGui.QMouseEvent):
        win = self.win
        sp = self.scene().snap(self.mapToScene(e.position().toPoint()))
        if e.button()==Qt.LeftButton:
            if getattr(win, "draw", None) and win.draw.mode != 0:
                if win.draw.on_click(sp, shift_ortho=self.ortho): win.push_history(); e.accept(); return
            if self.current_proto:
                d = self.current_proto
                it = DeviceItem(sp.x(), sp.y(), d["symbol"], d["name"], d.get("manufacturer",""), d.get("part_number",""))
                it.setParentItem(self.devices_group); win.push_history(); e.accept(); return
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

        self.devices_all = catalog.load_catalog()

        self.scene = GridScene(int(self.prefs.get("grid", DEFAULT_GRID_SIZE)), 0,0,10000,8000)
        self.scene.snap_enabled = bool(self.prefs.get("snap", True))

        self.layer_underlay = QtWidgets.QGraphicsItemGroup(); self.layer_underlay.setZValue(-10); self.scene.addItem(self.layer_underlay)
        self.layer_sketch   = QtWidgets.QGraphicsItemGroup(); self.layer_sketch.setZValue(40);   self.scene.addItem(self.layer_sketch)
        self.layer_wires    = QtWidgets.QGraphicsItemGroup(); self.layer_wires.setZValue(60);    self.scene.addItem(self.layer_wires)
        self.layer_devices  = QtWidgets.QGraphicsItemGroup(); self.layer_devices.setZValue(100);  self.scene.addItem(self.layer_devices)
        self.layer_overlay  = QtWidgets.QGraphicsItemGroup(); self.layer_overlay.setZValue(200);  self.scene.addItem(self.layer_overlay)

        self.view = CanvasView(self.scene, self.layer_devices, self.layer_wires, self.layer_sketch, self.layer_overlay, self)

        self.current_underlay_path = None
        self.underlay_opacity = 1.0

        self.draw = draw_tools.DrawController(self, self.layer_sketch)
        self.array_tool = ArrayTool(self, self.layer_devices)

        menubar = self.menuBar()
        m_file = menubar.addMenu("&File")
        m_file.addAction("New", self.new_project, QtGui.QKeySequence.New)
        m_file.addAction("Open…", self.open_project, QtGui.QKeySequence.Open)
        m_file.addAction("Save As…", self.save_project_as, QtGui.QKeySequence.SaveAs)
        m_file.addSeparator()
        m_file.addAction("Import DXF Underlay…", self.import_dxf_underlay)
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
        m_tools.addAction("Place Array…", self.array_tool.run)

        m_view = menubar.addMenu("&View")
        self.act_view_grid = QtGui.QAction("Grid", self, checkable=True); self.act_view_grid.setChecked(True); self.act_view_grid.toggled.connect(self.toggle_grid); m_view.addAction(self.act_view_grid)
        self.act_view_snap = QtGui.QAction("Snap", self, checkable=True); self.act_view_snap.setChecked(self.scene.snap_enabled); self.act_view_snap.toggled.connect(self.toggle_snap); m_view.addAction(self.act_view_snap)
        self.act_view_cross = QtGui.QAction("Crosshair (C)", self, checkable=True); self.act_view_cross.setChecked(True); self.act_view_cross.toggled.connect(self.toggle_crosshair); m_view.addAction(self.act_view_cross)
        m_view.addSeparator()
        act_scale = QtGui.QAction("Set Pixels per Foot…", self); act_scale.triggered.connect(self.set_px_per_ft); m_view.addAction(act_scale)

        m_help = menubar.addMenu("&Help")
        m_help.addAction("About AutoFire…", self.show_about)

        tb = QToolBar("Main"); tb.setIconSize(QSize(16,16)); self.addToolBar(tb)
        tb.addAction(self.act_view_grid); tb.addAction(self.act_view_snap); tb.addAction(self.act_view_cross)
        tb.addSeparator()
        tb.addAction(self.act_draw_line); tb.addAction(self.act_draw_rect); tb.addAction(self.act_draw_circle); tb.addAction(self.act_draw_poly)
        tb.addSeparator()
        tb.addAction("Array", self.array_tool.run)

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

        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Z"), self, activated=self.undo)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Y"), self, activated=self.redo)
        QtWidgets.QShortcut(QtGui.QKeySequence("F2"), self, activated=self.fit_view_to_content)

        self.history = []; self.history_index = -1
        self.push_history()

    # ---- palette ----
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

    # ---- view toggles ----
    def toggle_grid(self, on: bool): self.scene.show_grid = bool(on); self.scene.update()
    def toggle_snap(self, on: bool): self.scene.snap_enabled = bool(on)
    def toggle_crosshair(self, on: bool): self.view.show_crosshair = bool(on)

    def set_px_per_ft(self):
        val, ok = QtWidgets.QInputDialog.getDouble(self, "Scale", "Pixels per foot", self.px_per_ft, 1.0, 1000.0, 2)
        if ok:
            self.px_per_ft = float(val)
            self.prefs["px_per_ft"] = self.px_per_ft
            save_prefs(self.prefs)

    # ---- scene menu ----
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
            menu.addAction("Clear Underlay", self.clear_underlay)
            menu.exec(global_pos)

    # ---- serialize ----
    def serialize_state(self):
        devs = []
        for it in self.layer_devices.childItems():
            if isinstance(it, DeviceItem): devs.append(it.to_json())
        return {"grid":int(self.scene.grid_size), "snap":bool(self.scene.snap_enabled),
                "px_per_ft": float(self.px_per_ft),
                "underlay":{"opacity":1.0},"devices":devs,"wires":[]}

    def load_state(self, data):
        for it in list(self.layer_devices.childItems()): it.scene().removeItem(it)
        for it in list(self.layer_wires.childItems()): it.scene().removeItem(it)
        self.scene.snap_enabled = bool(data.get("snap", True)); self.act_view_snap.setChecked(self.scene.snap_enabled)
        self.scene.grid_size = int(data.get("grid", DEFAULT_GRID_SIZE)); self.spin_grid.setValue(self.scene.grid_size)
        self.px_per_ft = float(data.get("px_per_ft", self.px_per_ft))
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

    # ---- underlay ----
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
        pen=QtGui.QPen(Qt.darkGray); pen.setCosmetic(True); pen.setWidthF(0)
        item=QGraphicsPathItem(path); item.setPen(pen); item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False); item.setParentItem(self.layer_underlay)

    def _load_underlay(self, path):
        doc = ezdxf.readfile(path); msp = doc.modelspace(); p = self._build_underlay_path(msp); self._apply_underlay_path(p)

    def import_dxf_underlay(self):
        p,_ = QFileDialog.getOpenFileName(self,"Import DXF Underlay","","DXF Files (*.dxf)")
        if not p: return
        try: self._load_underlay(p)
        except Exception as ex: QMessageBox.critical(self,"DXF Import Error", str(ex))

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
        self.scene.grid_size = int(v); self.scene.update()

    def fit_view_to_content(self):
        rect=self.scene.itemsBoundingRect().adjusted(-100,-100,100,100)
        if rect.isNull(): rect=QtCore.QRectF(0,0,1000,800)
        self.view.fitInView(rect, Qt.KeepAspectRatio)

    def show_about(self):
        QtWidgets.QMessageBox.information(self,"About", f"Auto-Fire\\nVersion {APP_VERSION}")
    
def main():
    app = QApplication([])
    win = MainWindow(); win.show()
    app.exec()

if __name__ == "__main__":
    main()
''',

r"db\schema.py": r'''
# Minimal scaffolding for future SQLite catalog (not wired yet)
import sqlite3, os
from pathlib import Path

def ensure_db(path: str):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS manufacturers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS device_types(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        description TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS devices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        manufacturer_id INTEGER,
        type_id INTEGER,
        model TEXT,
        name TEXT,
        symbol TEXT,
        properties_json TEXT,
        FOREIGN KEY(manufacturer_id) REFERENCES manufacturers(id),
        FOREIGN KEY(type_id) REFERENCES device_types(id)
    );
    """)
    con.commit(); con.close()
''',

r"CHANGELOG.md": r'''
## 0.5.0-cadA
- Units: feet & inches support; scale stored as `px_per_ft`; status bar shows ft/in.
- Coverage: speaker supports physics (20log) or "per 10 ft" model; strobe coverage adds ceiling (circle inside square) and wall rectangle.
- Device labels: improved default offset; added "Edit Label…" action.
- Arrays: new "Place Array…" tool to lay out rows/columns with spacing in feet (or use coverage tile).
- Dialogs: Coverage dialog updated to ft/in scale.
- DB scaffolding: added `db/schema.py` with SQLite schema (not yet wired).
''',
}

def write(relpath, content):
    p = pathlib.Path(relpath)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("write", relpath)

def main():
    os.chdir(pathlib.Path(__file__).resolve().parents[1])
    for rel, content in FILES.items():
        write(rel, content)
    print("Done. Now run:  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned")
    print("Then:           .\\Build_AutoFire.ps1")

if __name__ == "__main__":
    main()
