from PySide6 import QtCore, QtGui, QtWidgets


class ScaleUnderlayRefTool:
    def __init__(self, window, underlay_group: QtWidgets.QGraphicsItemGroup):
        self.win = window
        self.group = underlay_group
        self.active = False
        self.p1 = None
        self.p2 = None

    def start(self):
        self.active = True
        self.p1 = None
        self.p2 = None
        self.win.statusBar().showMessage(
            "Underlay Scale (Ref): click first point, then second point"
        )

    def cancel(self):
        self.active = False
        self.p1 = None
        self.p2 = None

    def on_mouse_move(self, p: QtCore.QPointF):
        pass

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        if self.p1 is None:
            self.p1 = QtCore.QPointF(p)
            return False
        if self.p2 is None:
            self.p2 = QtCore.QPointF(p)
            # prompt for real distance (feet)
            dist_px = QtCore.QLineF(self.p1, self.p2).length()
            if dist_px <= 0.0:
                self.active = False
                return False
            val, ok = QtWidgets.QInputDialog.getDouble(
                self.win, "Real Distance", "Distance (feet)", 10.0, 0.01, 100000.0, 3
            )
            if not ok:
                self.active = False
                return False
            factor = (float(val) * float(self.win.px_per_ft)) / float(dist_px)
            # scale underlay about p1
            t = QtGui.QTransform()
            t.translate(self.p1.x(), self.p1.y())
            t.scale(factor, factor)
            t.translate(-self.p1.x(), -self.p1.y())
            try:
                self.group.setTransform(t, combine=True)
            except Exception:
                pass
            self.active = False
            self.win.statusBar().showMessage(f"Underlay scaled by factor {factor:.4f}")
            return True
        return False


def scale_underlay_by_factor(
    group: QtWidgets.QGraphicsItemGroup,
    factor: float,
    anchor: QtCore.QPointF = QtCore.QPointF(0, 0),
):
    t = QtGui.QTransform()
    t.translate(anchor.x(), anchor.y())
    t.scale(float(factor), float(factor))
    t.translate(-anchor.x(), -anchor.y())
    group.setTransform(t, combine=True)


class ScaleUnderlayDragTool:
    def __init__(self, window, underlay_group: QtWidgets.QGraphicsItemGroup):
        self.win = window
        self.group = underlay_group
        self.active = False
        self.anchor = None
        self.orig = None

    def start(self):
        self.active = True
        self.anchor = None
        self.orig = self.group.transform()
        self.win.statusBar().showMessage(
            "Underlay Scale (Drag): click anchor point, then move mouse; click again to commit, Esc to cancel"
        )

    def cancel(self):
        if self.active and self.orig is not None:
            try:
                self.group.setTransform(self.orig)
            except Exception:
                pass
        self.active = False
        self.anchor = None
        self.orig = None

    def on_mouse_move(self, p: QtCore.QPointF):
        if not self.active or self.anchor is None:
            return
        # scale factor from horizontal drag distance
        try:
            cur = p
            dx = cur.x() - self.anchor.x()
            factor = max(0.01, 1.0 + dx / 200.0)
            t = QtGui.QTransform(self.orig)
            t.translate(self.anchor.x(), self.anchor.y())
            t.scale(factor, factor)
            t.translate(-self.anchor.x(), -self.anchor.y())
            self.group.setTransform(t)
            self.win.statusBar().showMessage(f"Underlay Scale (Drag): factor={factor:.3f}")
        except Exception:
            pass

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        if self.anchor is None:
            self.anchor = QtCore.QPointF(p)
            return False
        # commit current transform
        self.active = False
        self.anchor = None
        self.orig = None
        return True
