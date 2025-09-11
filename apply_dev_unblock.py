# apply_dev_unblock.py
# One-shot repair:
# - ensures app/ is a package
# - writes app/tools/array.py (ArraySpec + fill_rect_with_points)
# - replaces app/main.py with a clean, working version that:
#     * shows device palette
#     * places devices by left click
#     * Tools ▸ Array in Area… (click two corners) fills with devices
#     * dark theme, status bar coord readout, grid/snap toggles
# - does NOT touch other files

from pathlib import Path
import datetime

ROOT = Path(".")
APP  = ROOT / "app"
TOOLS= APP / "tools"
ARR  = TOOLS / "array.py"
MAIN = APP  / "main.py"
INIT = APP  / "__init__.py"

def backup(p: Path):
    if p.exists():
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        p.with_suffix(p.suffix + f".bak_{ts}").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

# --- ensure package ---
APP.mkdir(parents=True, exist_ok=True)
if not INIT.exists():
    INIT.write_text("# package marker\n", encoding="utf-8")

# --- array.py (required by array-in-area & to avoid import crashes) ---
ARRAY_CODE = """from dataclasses import dataclass
from PySide6 import QtCore

@dataclass
class ArraySpec:
    spacing_ft: float = 10.0
    offset_ft_x: float = 0.0
    offset_ft_y: float = 0.0

def fill_rect_with_points(rect_px: QtCore.QRectF, px_per_ft: float, spec: ArraySpec):
    \"""Return a list of QPointF inside rect at a regular grid spacing (in feet).\"""
    if rect_px.width() <= 0 or rect_px.height() <= 0 or px_per_ft <= 0:
        return []
    step = spec.spacing_ft * px_per_ft
    ox = rect_px.left() + spec.offset_ft_x * px_per_ft
    oy = rect_px.top()  + spec.offset_ft_y * px_per_ft
    pts = []
    y = oy
    while y <= rect_px.bottom() - 1e-6:
        x = ox
        while x <= rect_px.right() - 1e-6:
            pts.append(QtCore.QPointF(x, y))
            x += step
        y += step
    return pts
"""
TOOLS.mkdir(parents=True, exist_ok=True)
backup(ARR)
ARR.write_text(ARRAY_CODE, encoding="utf-8")

# --- main.py (minimal but solid; uses your DeviceItem + GridScene if present) ---
MAIN_CODE = r'''import json, os, zipfile
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QPointF, QSize
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QLineEdit, QLabel, QToolBar, QFileDialog,
    QGraphicsView, QMenu, QDockWidget, QCheckBox, QSpinBox, QComboBox, QMessageBox)

# ---- safe imports from your project, with fallbacks ----
try:
    from app.scene import GridScene, DEFAULT_GRID_SIZE  # your grid/snap scene
except Exception:
    DEFAULT_GRID_SIZE = 24
    class GridScene(QtWidgets.QGraphicsScene):
        def __init__(self, grid=DEFAULT_GRID_SIZE, *a):
            super().__init__(*a); self.grid_size = grid; self.snap_enabled = True; self.snap_step_px = 0.0; self.show_grid=True
        def drawBackground(self, painter, rect):
            if not self.show_grid: return
            gs = max(2, int(self.grid_size))
            painter.setPen(QtGui.QPen(QtGui.QColor(60,60,60)))
            left = int(rect.left()) - (int(rect.left()) % gs)
            top  = int(rect.top())  - (int(rect.top())  % gs)
            for x in range(left, int(rect.right()), gs): painter.drawLine(x, rect.top(), x, rect.bottom())
            for y in range(top, int(rect.bottom()), gs): painter.drawLine(rect.left(), y, rect.right(), y)
        def snap(self, p:QtCore.QPointF)->QtCore.QPointF:
            if not self.snap_enabled: return p
            s = self.snap_step_px if self.snap_step_px>0 else self.grid_size
            return QtCore.QPointF(round(p.x()/s)*s, round(p.y()/s)*s)

try:
    from app.device import DeviceItem
except Exception:
    class DeviceItem(QtWidgets.QGraphicsItemGroup):
        def __init__(self, x, y, symbol, name, mfr="", pn=""):
            super().__init__(); self.symbol=symbol; self.name=name
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
            d=8; dot=QtWidgets.QGraphicsEllipseItem(-d/2,-d/2,d,d); dot.setBrush(Qt.white)
            dot.setPen(QtGui.QPen(Qt.black)); self.addToGroup(dot)
            lab=QtWidgets.QGraphicsSimpleTextItem(name); lab.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
            lab.setPos(10,-14); self.addToGroup(lab); self.setPos(x,y)
        def to_json(self):
            return {"x":float(self.pos().x()),"y":float(self.pos().y()),"symbol":self.symbol,"name":self.name}

# array helpers (never crash if module is missing)
try:
    from app.tools.array import ArraySpec, fill_rect_with_points
except Exception:
    from dataclasses import dataclass
    @dataclass
    class ArraySpec:
        spacing_ft: float = 10.0
        offset_ft_x: float = 0.0
        offset_ft_y: float = 0.0
    def fill_rect_with_points(rect_px, px_per_ft, spec): return []

# units helpers (very small; keeps feet/inches readout working)
def ft_to_px(ft: float, px_per_ft: float) -> float: return ft*px_per_ft
def px_to_ft(px: float, px_per_ft: float) -> float: return px/px_per_ft
def fmt_ft_inches(ft: float) -> str:
    sign = "-" if ft<0 else ""; ft=abs(ft); whole=int(ft); inches=(ft-whole)*12.0
    return f"{sign}{whole}'-{inches:.1f}\""

APP_VERSION = "0.6.3-dev"
APP_TITLE   = f"Auto-Fire {APP_VERSION}"
PREF_DIR    = os.path.join(os.path.expanduser("~"), "AutoFire"); os.makedirs(PREF_DIR, exist_ok=True)
PREF_PATH   = os.path.join(PREF_DIR, "preferences.json")

def load_prefs():
    try:
        with open(PREF_PATH,"r",encoding="utf-8") as f: return json.load(f)
    except Exception: return {}
def save_prefs(p):
    try:
        with open(PREF_PATH,"w",encoding="utf-8") as f: json.dump(p,f,indent=2)
    except Exception: pass

# very small device "catalog"
CATALOG = [
    {"symbol":"S","name":"Smoke Detector","type":"Detector","manufacturer":"(generic)","part_number":"SMK-001"},
    {"symbol":"H","name":"Heat Detector","type":"Detector","manufacturer":"(generic)","part_number":"HEAT-001"},
    {"symbol":"AV","name":"Horn/Strobe","type":"Notification","manufacturer":"(generic)","part_number":"AV-001"},
    {"symbol":"SP","name":"Speaker","type":"Notification","manufacturer":"(generic)","part_number":"SPK-001"},
]

class CanvasView(QGraphicsView):
    def __init__(self, scene, devices_group, window_ref):
        super().__init__(scene)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)
        self.setMouseTracking(True)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.devices_group = devices_group
        self.win = window_ref
        self.current_proto = None
        # crosshair
        self.cross_v = QtWidgets.QGraphicsLineItem(); self.cross_h = QtWidgets.QGraphicsLineItem()
        pen = QtGui.QPen(QtGui.QColor(130,130,130,160)); pen.setCosmetic(True); pen.setStyle(Qt.DashLine)
        for ln in (self.cross_v,self.cross_h): ln.setPen(pen); ln.setZValue(500); scene.addItem(ln)

    def set_current_device(self, proto: dict): self.current_proto = proto

    def _update_cross(self, p: QPointF):
        r = self.scene().sceneRect()
        self.cross_v.setLine(p.x(), r.top(), p.x(), r.bottom())
        self.cross_h.setLine(r.left(), p.y(), r.right(), p.y())
        xft = px_to_ft(p.x(), self.win.px_per_ft); yft = px_to_ft(p.y(), self.win.px_per_ft)
        self.win.statusBar().showMessage(f"x={fmt_ft_inches(xft)}  y={fmt_ft_inches(yft)}  scale={self.win.px_per_ft:.2f} px/ft")

    def wheelEvent(self, e: QtGui.QWheelEvent):
        s = 1.15 if e.angleDelta().y()>0 else 1/1.15
        self.scale(s, s)

    def mouseMoveEvent(self, e: QtGui.QMouseEvent):
        sp = self.mapToScene(e.position().toPoint())
        self._update_cross(sp)
        super().mouseMoveEvent(e)

    def mousePressEvent(self, e: QtGui.QMouseEvent):
        sp = self.mapToScene(e.position().toPoint())
        sp = self.scene().snap(sp)
        if e.button()==Qt.LeftButton:
            # array-in-area mode?
            if self.win._array_rect_start is not None:
                self.win._handle_array_click(sp); e.accept(); return
            # normal placement
            if self.current_proto:
                d = self.current_proto
                it = DeviceItem(sp.x(), sp.y(), d["symbol"], d["name"], d.get("manufacturer",""), d.get("part_number",""))
                it.setParentItem(self.devices_group); self.win.statusBar().showMessage(f"Placed: {d['name']}")
                e.accept(); return
        elif e.button()==Qt.RightButton:
            self.win.canvas_menu(e.globalPosition().toPoint()); e.accept(); return
        super().mousePressEvent(e)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1400, 900)
        self.prefs = load_prefs()
        self.px_per_ft = float(self.prefs.get("px_per_ft", 12.0))

        # dark theme
        pal = self.palette()
        pal.setColor(pal.Window, QtGui.QColor(32,32,36))
        pal.setColor(pal.Base,   QtGui.QColor(26,26,28))
        pal.setColor(pal.Text,   Qt.white); pal.setColor(pal.WindowText, Qt.white)
        pal.setColor(pal.Button, QtGui.QColor(48,48,52)); pal.setColor(pal.ButtonText, Qt.white)
        self.setPalette(pal)

        self.scene = GridScene(int(self.prefs.get("grid", DEFAULT_GRID_SIZE)), 0,0,12000,9000)
        self.scene.snap_enabled = bool(self.prefs.get("snap", True))
        self.scene.setSceneRect(0,0,12000,9000)

        self.layer_devices = QtWidgets.QGraphicsItemGroup(); self.layer_devices.setZValue(100); self.scene.addItem(self.layer_devices)

        self.view = CanvasView(self.scene, self.layer_devices, self)
        self._array_rect_start = None  # clicking first corner puts us in "array area" mode

        # left panel (device palette)
        left = QWidget(); lv = QVBoxLayout(left)
        lv.addWidget(QLabel("Device Palette"))
        self.search = QLineEdit(); self.search.setPlaceholderText("Search…"); lv.addWidget(self.search)
        self.list = QListWidget(); lv.addWidget(self.list, 1)

        self._refresh_device_list()
        self.search.textChanged.connect(self._refresh_device_list)
        self.list.itemClicked.connect(self.choose_device)

        # toolbar (small)
        tb = QToolBar("Main"); tb.setIconSize(QSize(16,16)); self.addToolBar(tb)
        act_fit = QtGui.QAction("Fit (F2)", self); act_fit.triggered.connect(self.fit_view_to_content); tb.addAction(act_fit)
        act_arr = QtGui.QAction("Array in Area…", self); act_arr.triggered.connect(self.array_in_area); tb.addAction(act_arr)
        tb.addSeparator()
        act_snap = QtGui.QAction("Snap", self, checkable=True); act_snap.setChecked(self.scene.snap_enabled); act_snap.toggled.connect(lambda v: setattr(self.scene, "snap_enabled", bool(v))); tb.addAction(act_snap)

        # menu (File / Tools / Help)
        menubar = self.menuBar()
        m_file = menubar.addMenu("&File")
        m_file.addAction("Open…", self.open_project, QtGui.QKeySequence.Open)
        m_file.addAction("Save As…", self.save_project_as, QtGui.QKeySequence.SaveAs)
        m_tools = menubar.addMenu("&Tools")
        m_tools.addAction("Array in Area…", self.array_in_area)
        m_help = menubar.addMenu("&Help")
        m_help.addAction("About", lambda: QtWidgets.QMessageBox.information(self,"About", APP_TITLE))

        # shortcuts
        QtGui.QShortcut(QtGui.QKeySequence("F2"), self, activated=self.fit_view_to_content)

        # layout
        splitter = QtWidgets.QSplitter(); splitter.addWidget(left); splitter.addWidget(self.view); splitter.setStretchFactor(1,1)
        container = QWidget(); lay = QHBoxLayout(container); lay.addWidget(splitter); self.setCentralWidget(container)
        self.statusBar().showMessage("Ready")

    # ---- device palette ----
    def _refresh_device_list(self):
        q = self.search.text().lower().strip() if self.search.text() else ""
        self.list.clear()
        for d in CATALOG:
            txt = f"{d['name']} ({d['symbol']})"
            if q and q not in txt.lower(): continue
            it = QListWidgetItem(txt); it.setData(Qt.UserRole, d); self.list.addItem(it)

    def choose_device(self, it: QListWidgetItem):
        proto = it.data(Qt.UserRole)
        self.view.set_current_device(proto)
        self.statusBar().showMessage(f"Selected: {proto['name']} — Left-click to place")

    # ---- array in area ----
    def array_in_area(self):
        self._array_rect_start = None
        self.statusBar().showMessage("Array in Area: click first corner, then opposite corner")

    def _handle_array_click(self, p: QPointF):
        if self._array_rect_start is None:
            self._array_rect_start = p
            self.statusBar().showMessage("Array in Area: click opposite corner")
            return
        # finish rect
        p0, p1 = self._array_rect_start, p
        self._array_rect_start = None
        rect = QtCore.QRectF(QtCore.QPointF(min(p0.x(),p1.x()), min(p0.y(),p1.y())),
                             QtCore.QPointF(max(p0.x(),p1.x()), max(p0.y(),p1.y())))
        spec = ArraySpec(spacing_ft=10.0)  # TODO: later expose in UI
        pts  = fill_rect_with_points(rect, self.px_per_ft, spec)
        if not pts:
            self.statusBar().showMessage("No points generated (check spacing/scale)")
            return
        proto = self.view.current_proto or CATALOG[0]
        for pt in pts:
            it = DeviceItem(pt.x(), pt.y(), proto["symbol"], proto["name"], proto.get("manufacturer",""), proto.get("part_number",""))
            it.setParentItem(self.layer_devices)
        self.statusBar().showMessage(f"Array placed: {len(pts)} devices")

    # ---- serialize ----
    def serialize_state(self):
        devs = []
        for it in self.layer_devices.childItems():
            if isinstance(it, DeviceItem): devs.append(it.to_json())
        return {"grid":int(self.scene.grid_size), "snap":bool(self.scene.snap_enabled),
                "px_per_ft": float(self.px_per_ft), "devices":devs}

    def save_project_as(self):
        p,_ = QFileDialog.getSaveFileName(self,"Save Project As","","AutoFire Bundle (*.autofire)")
        if not p: return
        if not p.lower().endswith(".autofire"): p += ".autofire"
        data=self.serialize_state()
        with zipfile.ZipFile(p,"w",compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("project.json", json.dumps(data, indent=2))
        self.statusBar().showMessage(f"Saved: {os.path.basename(p)}")

    def open_project(self):
        p,_=QFileDialog.getOpenFileName(self,"Open Project","","AutoFire Bundle (*.autofire)")
        if not p: return
        with zipfile.ZipFile(p,"r") as z:
            data=json.loads(z.read("project.json").decode("utf-8"))
        self.scene.snap_enabled = bool(data.get("snap", True))
        for it in list(self.layer_devices.childItems()): it.scene().removeItem(it)
        for d in data.get("devices", []):
            di = DeviceItem(float(d.get("x",0)), float(d.get("y",0)), d.get("symbol","?"), d.get("name","Device"))
            di.setParentItem(self.layer_devices)
        self.statusBar().showMessage(f"Opened: {os.path.basename(p)}")

    def fit_view_to_content(self):
        rect=self.scene.itemsBoundingRect().adjusted(-100,-100,100,100)
        if rect.isNull(): rect=QtCore.QRectF(0,0,2000,1500)
        self.view.fitInView(rect, Qt.KeepAspectRatio)

# factory for boot.py
def create_window(): return MainWindow()

def main():
    app = QApplication([])
    w = create_window()
    w.show()
    app.exec()
'''
backup(MAIN)
MAIN.write_text(MAIN_CODE, encoding="utf-8")

print("Done. Wrote:")
print(" -", ARR)
print(" -", MAIN)
print("\nNext steps:")
print("  1) Run: py -3 app\\boot.py")
print("  2) Select a device in the left list, then LEFT-CLICK on the canvas to place.")
print("  3) Tools ▸ Array in Area… → click two corners to populate devices.")
