from PySide6 import QtCore, QtWidgets

from frontend.windows.scene import CanvasView


class MockLine:
    def __init__(self, x1, y1, x2, y2):
        self._x1, self._y1, self._x2, self._y2 = x1, y1, x2, y2

    def x1(self):
        return self._x1

    def y1(self):
        return self._y1

    def x2(self):
        return self._x2

    def y2(self):
        return self._y2


class MockScene:
    def __init__(self, items):
        self._items = items

    def items(self):
        return self._items


class MockLineItem:
    def __init__(self, line):
        self._line = line

    def line(self):
        return self._line


def test_osnap_line_intersection():
    # Ensure a QApplication exists for QWidget-based components
    _ = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    # Two lines intersecting at (5,5)
    line1 = MockLine(0, 0, 10, 10)
    line2 = MockLine(0, 10, 10, 0)
    scene = MockScene([MockLineItem(line1), MockLineItem(line2)])
    view = CanvasView(scene, None, None, None, None, None)
    view.osnap_intersect = True
    result = view.compute_osnap_for_test(QtCore.QPointF(5.5, 5.5))
    assert result is not None
    assert abs(result.x() - 5) < 1e-6
    assert abs(result.y() - 5) < 1e-6
    # Clean up view; leave app running for pytest session
    view.deleteLater()
