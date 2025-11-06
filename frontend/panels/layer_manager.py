"""
Layer Manager - Advanced layer management for CAD
"""

from PySide6 import QtCore
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class LayerManager(QtCore.QObject):
    """Manages layers in the CAD system."""

    # Signals
    layer_changed = QtCore.Signal(str)  # Emitted when current layer changes
    layer_selected = QtCore.Signal(str)  # Emitted when a layer is selected

    def __init__(self):
        super().__init__()
        self.layers = {
            "devices": {"name": "Devices", "visible": True, "locked": False},
            "wires": {"name": "Wires", "visible": True, "locked": False},
            "sketch": {"name": "Sketch", "visible": True, "locked": False},
            "overlay": {"name": "Overlay", "visible": True, "locked": False},
        }
        self.current_layer = "devices"

    def set_current_layer(self, layer_name: str):
        """Set the current active layer."""
        if layer_name in self.layers:
            self.current_layer = layer_name
            self.layer_changed.emit(layer_name)

    def get_current_layer(self) -> str:
        """Get the current active layer."""
        return self.current_layer

    def toggle_layer_visibility(self, layer_name: str):
        """Toggle visibility of a layer."""
        if layer_name in self.layers:
            self.layers[layer_name]["visible"] = not self.layers[layer_name]["visible"]

    def is_layer_visible(self, layer_name: str) -> bool:
        """Check if a layer is visible."""
        return self.layers.get(layer_name, {}).get("visible", True)

    def get_all_layers(self):
        """Get all layers."""
        return self.layers.copy()


class LayerManagerWidget(QWidget):
    """Widget for managing layers in the UI."""

    def __init__(self, layer_manager: LayerManager, parent=None):
        super().__init__(parent)
        self.layer_manager = layer_manager

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Layer Manager"))

        # Connect to layer manager signals
        self.layer_manager.layer_changed.connect(self.on_layer_changed)

    def on_layer_changed(self, layer_name: str):
        """Handle layer change."""
        print(f"Layer changed to: {layer_name}")
