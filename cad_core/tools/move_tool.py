from PySide6 import QtCore, QtWidgets


class MoveTool:
    def __init__(self, window):
        self.win = window
        self.active = False
        self.base = None
        self.copy = False

    def start(self, copy=False):
        self.active = True
        self.base = None
        self.copy = bool(copy)
        self.win.statusBar().showMessage("Move: click base point, then destination")

    def cancel(self):
        self.active = False
        self.base = None

    def on_mouse_move(self, p: QtCore.QPointF):
        pass

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        if self.base is None:
            self.base = p
            return False
        delta = p - self.base
        sel = list(self.win.scene.selectedItems())
        if not sel:
            self.active = False
            self.base = None
            return False
        for it in sel:
            try:
                if self.copy:
                    # attempt to duplicate simple items
                    dup = None
                    if isinstance(it, QtWidgets.QGraphicsLineItem):
                        line = it.line()
                        dup = QtWidgets.QGraphicsLineItem(line)
                    elif isinstance(it, QtWidgets.QGraphicsRectItem):
                        r = it.rect()
                        dup = QtWidgets.QGraphicsRectItem(r)
                    elif isinstance(it, QtWidgets.QGraphicsEllipseItem):
                        r = it.rect()
                        dup = QtWidgets.QGraphicsEllipseItem(r)
                    elif isinstance(it, QtWidgets.QGraphicsPathItem):
                        dup = QtWidgets.QGraphicsPathItem(it.path())
                    elif hasattr(it, "to_json") and hasattr(type(it), "from_json"):
                        dup = type(it).from_json(it.to_json())
                    if dup is not None:
                        dup.setParentItem(it.parentItem())
                        dup.setPos(it.pos() + delta)
                        dup.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
                        dup.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
                else:
                    it.setPos(it.pos() + delta)
            except Exception:
                pass
        self.active = False
        self.base = None
        return True
