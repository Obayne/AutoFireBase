"""Enhanced connections / circuits panel (stub).

Provides a factory function used by ModelSpaceWindow: create_enhanced_connections_tab(window)
and exposes three Qt signals that ModelSpaceWindow connects to. The UI here is
minimal but signal-compatible so the right-dock can use the enhanced panel when
available.
"""

from PySide6 import QtCore, QtWidgets


class EnhancedConnectionsPanel(QtWidgets.QWidget):
    circuit_selected = QtCore.Signal(object)
    device_selected = QtCore.Signal(object)
    calculations_updated = QtCore.Signal(dict)

    def __init__(self, window):
        super().__init__(window)
        self.window = window
        lay = QtWidgets.QVBoxLayout(self)

        header = QtWidgets.QLabel("Enhanced Connections (preview)")
        header.setStyleSheet("font-weight:bold; margin:6px 0;")
        lay.addWidget(header)

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Circuit/Device"])
        lay.addWidget(self.tree)

        # Populate with a small example when devices are present
        try:
            devices = getattr(self.window, "all_devices", []) or []
            if devices:
                root = QtWidgets.QTreeWidgetItem(["Demo Circuits"])
                for i, d in enumerate(devices[:10]):
                    it = QtWidgets.QTreeWidgetItem([d.get("name", str(i))])
                    it.setData(0, QtCore.Qt.ItemDataRole.UserRole, d)
                    root.addChild(it)
                self.tree.addTopLevelItem(root)
                self.tree.expandAll()
        except Exception:
            pass

        self.tree.itemClicked.connect(self._on_item_clicked)

    def _on_item_clicked(self, item, col=0):
        data = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        if data:
            self.device_selected.emit(data)


def create_enhanced_connections_tab(window) -> EnhancedConnectionsPanel:
    return EnhancedConnectionsPanel(window)
