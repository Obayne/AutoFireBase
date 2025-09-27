from PySide6 import QtWidgets


def test_layout_drawer_constructs_and_hides(qtbot):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    from frontend.layout_drawer import create_layout_drawer

    dock = create_layout_drawer(win)
    assert isinstance(dock, QtWidgets.QDockWidget)
    assert dock.isHidden() is True
    # show/hide roundtrip
    dock.show()
    assert dock.isVisible() is True
    dock.hide()
    assert dock.isHidden() is True
