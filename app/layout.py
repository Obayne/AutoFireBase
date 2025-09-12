
from PySide6 import QtCore, QtGui, QtWidgets

PAGE_SIZES = {
    "Letter": (8.5, 11),
    "Tabloid": (11, 17),
    "A3": (11.69, 16.54),
    "A2": (16.54, 23.39),
    "A1": (23.39, 33.11),
    "A0": (33.11, 46.81),
    # Architectural sizes (inches)
    "Arch A": (9, 12),
    "Arch B": (12, 18),
    "Arch C": (18, 24),
    "Arch D": (24, 36),
    "Arch E": (36, 48),
}

class PageFrame(QtWidgets.QGraphicsItemGroup):
    def __init__(self, px_per_ft: float, size_name="Letter", orientation="Portrait", margin_in=0.5):
        super().__init__()
        self._px_per_ft = float(px_per_ft)
        self._size_name = size_name
        self._orient = orientation
        self._margin_in = float(margin_in)
        self._outer = QtWidgets.QGraphicsRectItem(); self._outer.setPen(QtGui.QPen(QtGui.QColor(180,180,180)))
        self._inner = QtWidgets.QGraphicsRectItem(); pen = QtGui.QPen(QtGui.QColor(130,130,130)); pen.setStyle(QtCore.Qt.DashLine); self._inner.setPen(pen)
        self.addToGroup(self._outer); self.addToGroup(self._inner)
        self.setZValue(-50)
        self._recalc()

    def _inch_to_px(self, inches: float) -> float:
        return (float(inches)/12.0) * self._px_per_ft

    def _recalc(self):
        w_in, h_in = PAGE_SIZES.get(self._size_name, PAGE_SIZES["Letter"])
        if (self._orient or "Portrait").lower().startswith("land"):
            w_in, h_in = h_in, w_in
        w_px = self._inch_to_px(w_in); h_px = self._inch_to_px(h_in)
        m = self._inch_to_px(self._margin_in)
        self._outer.setRect(0, 0, w_px, h_px)
        self._inner.setRect(m, m, max(0, w_px-2*m), max(0, h_px-2*m))

    def set_params(self, *, size_name=None, orientation=None, margin_in=None, px_per_ft=None):
        if size_name: self._size_name = size_name
        if orientation: self._orient = orientation
        if margin_in is not None: self._margin_in = float(margin_in)
        if px_per_ft is not None: self._px_per_ft = float(px_per_ft)
        self._recalc()


class TitleBlock(QtWidgets.QGraphicsItemGroup):
    def __init__(self, px_per_ft: float, size_name="Letter", orientation="Landscape", meta: dict | None = None):
        super().__init__()
        self._px_per_ft = float(px_per_ft)
        self._size = size_name
        self._orient = orientation
        self._meta = meta or {}
        self._items = []
        self.setZValue(10)
        self._build()


class ViewportItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, model_scene: QtWidgets.QGraphicsScene, rect: QtCore.QRectF, window: QtWidgets.QMainWindow | None = None):
        super().__init__(rect)
        self.model_scene = model_scene
        self.win = window
        # model pixels shown per viewport pixel (higher = zoomed out)
        self.scale_factor = 1.0
        # model source center
        try:
            self.src_center = model_scene.itemsBoundingRect().center()
        except Exception:
            self.src_center = QtCore.QPointF(0, 0)
        self.locked = False
        self.setPen(QtGui.QPen(QtGui.QColor(160,160,160)))
        self.setBrush(QtCore.Qt.NoBrush)
        self.setZValue(5)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable)

    def set_scale_factor(self, f: float):
        self.scale_factor = max(0.001, float(f))
        self.update()

    def set_src_center(self, c: QtCore.QPointF):
        self.src_center = QtCore.QPointF(c)
        self.update()

    def contextMenuEvent(self, event: QtWidgets.QGraphicsSceneContextMenuEvent):
        m = QtWidgets.QMenu()
        act_scale = m.addAction("Set Scale Factor…")
        act_center = m.addAction("Center on Model View")
        act_lock = m.addAction("Lock Viewport")
        act_lock.setCheckable(True); act_lock.setChecked(self.locked)
        chosen = m.exec(event.screenPos())
        if chosen == act_scale:
            val, ok = QtWidgets.QInputDialog.getDouble(self.win or None, "Viewport Scale", "Scale factor", self.scale_factor, 0.001, 1000.0, 3)
            if ok:
                self.set_scale_factor(val)
        elif chosen == act_center:
            try:
                if self.win is not None:
                    vc = self.win.view.mapToScene(self.win.view.viewport().rect().center())
                    self.set_src_center(vc)
            except Exception:
                pass
        elif chosen == act_lock:
            self.locked = act_lock.isChecked()
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, not self.locked)
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, not self.locked)

    def paint(self, painter: QtGui.QPainter, option, widget=None):
        # clip to rect and render source from model scene
        r = self.rect()
        painter.save()
        painter.setClipRect(r)
        w_src = r.width() * self.scale_factor
        h_src = r.height() * self.scale_factor
        src = QtCore.QRectF(self.src_center.x() - w_src/2, self.src_center.y() - h_src/2, w_src, h_src)
        # draw border
        super().paint(painter, option, widget)
        # render model scene into this item
        try:
            self.model_scene.render(painter, r, src)
        except Exception:
            pass
        painter.restore()

    def _inch_to_px(self, inches: float) -> float:
        return (float(inches)/12.0) * self._px_per_ft

    def _build(self):
        # Simple block at bottom right with a few fields
        for it in self._items:
            try:
                if it.scene(): it.scene().removeItem(it)
            except Exception: pass
        self._items.clear()
        w_in, h_in = PAGE_SIZES.get(self._size, PAGE_SIZES["Letter"])
        if (self._orient or "").lower().startswith("port"): pass
        else:
            w_in, h_in = h_in, w_in
        w = self._inch_to_px(w_in); h = self._inch_to_px(h_in)
        # Block rectangle 3x10 inches in bottom-right
        bw = self._inch_to_px(10); bh = self._inch_to_px(3)
        rect = QtCore.QRectF(w - bw - self._inch_to_px(0.5), h - bh - self._inch_to_px(0.5), bw, bh)
        box = QtWidgets.QGraphicsRectItem(rect)
        pen = QtGui.QPen(QtGui.QColor(180,180,180)); pen.setCosmetic(True)
        box.setPen(pen); box.setBrush(QtCore.Qt.NoBrush)
        self.addToGroup(box); self._items.append(box)
        # Text rows
        def add_line(label, value, y_off_in):
            y = rect.top() + self._inch_to_px(y_off_in)
            t = QtWidgets.QGraphicsSimpleTextItem(f"{label}: {value}")
            t.setPen(QtGui.QPen(QtGui.QColor(200,200,210)))
            t.setBrush(QtGui.QBrush(QtGui.QColor(200,200,210)))
            t.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
            t.setPos(rect.left() + self._inch_to_px(0.3), y)
            self.addToGroup(t); self._items.append(t)
        add_line("Project", self._meta.get("project",""), 0.3)
        add_line("Address", self._meta.get("address",""), 0.8)
        add_line("Sheet", self._meta.get("sheet",""), 1.3)
        add_line("Date", self._meta.get("date",""), 1.8)
        add_line("By", self._meta.get("by",""), 2.3)

    def set_meta(self, meta: dict | None):
        self._meta = meta or {}
        self._build()
