# apply_dxf_v1_074.py
# Add robust DXF underlay import (ezdxf.recover + units -> feet -> px_per_ft).
# Safe: writes app/dxf_import.py, injects a new menu action + handler in app/main.py.
# Backups with timestamp suffixes are created.

from pathlib import Path
import time, re

ROOT = Path(__file__).resolve().parent
STAMP = time.strftime("%Y%m%d_%H%M%S")
DXF = ROOT / "app" / "dxf_import.py"
MAIN = ROOT / "app" / "main.py"

DXF_CODE = r'''
from PySide6 import QtCore, QtGui, QtWidgets

def _aci_to_qcolor(aci: int) -> QtGui.QColor:
    # Basic AutoCAD Color Index mapping (fallbacks)
    table = {
        1: "#FF0000", 2: "#FFFF00", 3: "#00FF00", 4: "#00FFFF",
        5: "#0000FF", 6: "#FF00FF", 7: "#FFFFFF",
    }
    return QtGui.QColor(table.get(int(aci or 7), "#CCCCCC"))

def _insunits_to_feet(code: int) -> float:
    # 0=unitless,1=in,2=ft,3=mm,4=cm,5=m,6=km  (common set)
    # return how many FEET are in 1 drawing unit
    m = {
        0: 1.0,              # treat unitless as feet
        1: 1.0/12.0,         # inch
        2: 1.0,              # foot
        3: 0.003280839895,   # mm
        4: 0.03280839895,    # cm
        5: 3.280839895,      # m
        6: 3280.839895,      # km
    }
    return float(m.get(int(code or 0), 1.0))

def _build_paths(doc, px_per_ft: float):
    msp = doc.modelspace()
    ins = int(doc.header.get("$INSUNITS", 0))
    feet_per_unit = _insunits_to_feet(ins)
    S = feet_per_unit * float(px_per_ft)

    # layer -> (QPainterPath, QPen)
    layers = {}
    def get_layer_pack(name: str):
        if name not in layers:
            try:
                lay = doc.layers.get(name)
                aci = getattr(lay, "color", 7)
            except Exception:
                aci = 7
            pen = QtGui.QPen(_aci_to_qcolor(aci))
            pen.setCosmetic(True); pen.setWidthF(0.0)
            layers[name] = (QtGui.QPainterPath(), pen)
        return layers[name]

    # Gather supported entities
    for e in msp:
        typ = e.dxftype()
        try:
            if typ == "LINE":
                (sx, sy, _), (ex, ey, _) = e.dxf.start, e.dxf.end
                p, pen = get_layer_pack(e.dxf.layer)
                p.moveTo(sx*S, -sy*S); p.lineTo(ex*S, -ey*S)

            elif typ in ("LWPOLYLINE", "POLYLINE"):
                points = []
                if typ == "LWPOLYLINE":
                    points = [(v[0], v[1]) for v in e.get_points()]  # bulge ignored
                    closed = bool(e.closed)
                else:
                    points = [(v.dxf.location[0], v.dxf.location[1]) for v in e.vertices]
                    closed = bool(e.is_closed)
                if points:
                    p, pen = get_layer_pack(e.dxf.layer)
                    x0, y0 = points[0]
                    p.moveTo(x0*S, -y0*S)
                    for (x, y) in points[1:]:
                        p.lineTo(x*S, -y*S)
                    if closed:
                        p.closeSubpath()

            elif typ == "CIRCLE":
                cx, cy, _ = e.dxf.center
                r = float(e.dxf.radius) * S
                rect = QtCore.QRectF(cx*S - r, -cy*S - r, 2*r, 2*r)
                p, pen = get_layer_pack(e.dxf.layer)
                p.addEllipse(rect)

            elif typ == "ARC":
                cx, cy, _ = e.dxf.center
                r = float(e.dxf.radius) * S
                start = float(e.dxf.start_angle)
                end   = float(e.dxf.end_angle)
                rect = QtCore.QRectF(cx*S - r, -cy*S - r, 2*r, 2*r)
                # painterpath uses cw/ccw in degrees: use arcMoveTo + arcTo
                path, pen = get_layer_pack(e.dxf.layer)
                path.arcMoveTo(rect, start)
                sweep = end - start
                path.arcTo(rect, start, sweep)

        except Exception:
            # ignore malformed entity
            continue

    return layers

def import_dxf_into_group(path: str, target_group: QtWidgets.QGraphicsItemGroup, px_per_ft: float) -> QtCore.QRectF:
    try:
        import ezdxf
        from ezdxf import recover
    except Exception as ex:
        raise RuntimeError("DXF support not available (ezdxf). Install it in this Python env.") from ex

    # Try normal open; on structure errors, recover
    try:
        doc = ezdxf.readfile(path)
    except Exception:
        doc, aud = recover.readfile(path)  # may have errors but usable

    # Clear previous items from the underlay group
    scn = target_group.scene()
    for child in list(target_group.childItems()):
        scn.removeItem(child)

    packs = _build_paths(doc, px_per_ft)

    bounds = QtCore.QRectF()
    for (p, pen) in packs.values():
        item = QtWidgets.QGraphicsPathItem(p)
        item.setPen(pen); item.setBrush(QtCore.Qt.NoBrush)
        item.setParentItem(target_group)
        bounds = bounds.united(p.controlPointRect())

    return bounds
'''

def write_dxf():
    DXF.parent.mkdir(parents=True, exist_ok=True)
    if DXF.exists():
        bak = DXF.with_suffix(".py.bak-"+STAMP)
        bak.write_text(DXF.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[backup] {bak}")
    DXF.write_text(DXF_CODE.lstrip(), encoding="utf-8")
    print(f"[write ] {DXF}")

def patch_main():
    if not MAIN.exists():
        print(f"[!] missing {MAIN}")
        return
    src = MAIN.read_text(encoding="utf-8")

    # 1) add import only once
    if "from app import dxf_import" not in src:
        # insert after other "from app import ..." lines if present
        new_src = re.sub(
            r'(\nfrom app[^\n]*\n)(?!.*from app import dxf_import)',
            r'\1from app import dxf_import\n',
            src, count=1, flags=re.S
        )
        if new_src == src:
            # fallback: append near top after first imports block
            new_src = src.replace("from app import catalog", "from app import catalog\nfrom app import dxf_import")
        src = new_src

    # 2) inject new menu action under File menu
    if "Import DXF Underlay (v1)…" not in src:
        src = re.sub(
            r'(m_file\s*=\s*menubar\.addMenu\([^\)]+\)\s*.*?)(m_file\.addSeparator\(\)\s*.*?m_file\.addAction\("Quit",.*?\)\s*)',
            r'\1m_file.addAction("Import DXF Underlay (v1)…", self.import_dxf_underlay_v1)\n        \2',
            src, flags=re.S
        )

    # 3) add handler method into MainWindow if missing
    if "def import_dxf_underlay_v1(self)" not in src:
        insert_point = src.rfind("def show_about(self):")
        if insert_point == -1:
            insert_point = len(src)
        handler = r'''

    def import_dxf_underlay_v1(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import DXF Underlay (v1)", "", "DXF Files (*.dxf)")
        if not path:
            return
        try:
            bounds = dxf_import.import_dxf_into_group(path, self.layer_underlay, self.px_per_ft)
            # make sure underlay is visible
            self.layer_underlay.setVisible(True)
            self.chk_underlay.setChecked(True)
            # Fit view to content (underlay + devices)
            if bounds and not bounds.isNull():
                margin = 100
                rect = bounds.adjusted(-margin, -margin, margin, margin)
                self.view.fitInView(rect, QtCore.Qt.KeepAspectRatio)
            self.statusBar().showMessage(f"Imported underlay: {path}")
        except Exception as ex:
            QtWidgets.QMessageBox.critical(self, "DXF Import Error", str(ex))
'''
        src = src[:insert_point] + handler + src[insert_point:]

    # write out
    bak = MAIN.with_suffix(".py.bak-"+STAMP)
    bak.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")
    MAIN.write_text(src, encoding="utf-8")
    print(f"[backup] {bak}")
    print(f"[write ] {MAIN}")

if __name__ == "__main__":
    write_dxf()
    patch_main()
    print("\nDone. Launch with:  py -3 -m app.boot")
