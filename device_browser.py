"""
Device Browser - Fire Protection Device Selection and Placement
==============================================================

Creates a docked panel for browsing and selecting fire protection devices
from the catalog for placement on the CAD canvas.
"""

from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import (
    QDockWidget,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

try:
    from app.catalog import load_catalog
    from app.device import DeviceItem

    HAS_CATALOG = True
except ImportError:
    HAS_CATALOG = False


class DeviceBrowserDock(QDockWidget):
    """
    Device Browser Dock Widget

    Provides a categorized list of fire protection devices for placement.
    Supports drag-and-drop or click-to-place workflows.
    """

    # Signal emitted when user wants to place a device
    device_selected = QtCore.Signal(dict)  # Emits device prototype dict

    def __init__(self, parent=None):
        super().__init__("Device Browser", parent)
        self.setAllowedAreas(
            QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
            | QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        )

        # Create main widget
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        # Title
        title_label = QLabel("🔥 Fire Protection Devices")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title_label)

        # Device list
        self.device_list = QListWidget()
        self.device_list.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        self.device_list.itemClicked.connect(self._on_device_clicked)
        layout.addWidget(self.device_list)

        # Instructions
        instructions = QLabel("💡 Click device to place on canvas")
        instructions.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        self.setWidget(main_widget)
        self.setMinimumWidth(200)

        # Load devices
        self._load_devices()

    def _load_devices(self):
        """Load fire protection devices from catalog."""
        if not HAS_CATALOG:
            # Add fallback devices
            devices = [
                {"name": "Smoke Detector", "symbol": "SD", "type": "Detector"},
                {"name": "Heat Detector", "symbol": "HD", "type": "Detector"},
                {"name": "Horn Strobe", "symbol": "HS", "type": "Notification"},
                {"name": "Pull Station", "symbol": "PS", "type": "Initiating"},
            ]
        else:
            devices = load_catalog()

        # Group devices by type
        device_types = {}
        for device in devices:
            device_type = device.get("type", "Other")
            if device_type not in device_types:
                device_types[device_type] = []
            device_types[device_type].append(device)

        # Add devices to list by category
        for device_type, type_devices in device_types.items():
            # Add category header
            header_item = QListWidgetItem(f"📁 {device_type}")
            header_item.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)  # Not selectable
            header_item.setBackground(QtGui.QColor("#f0f0f0"))
            font = header_item.font()
            font.setBold(True)
            header_item.setFont(font)
            self.device_list.addItem(header_item)

            # Add devices in this category
            for device in type_devices:
                item = QListWidgetItem()
                item.setText(f"  {device.get('symbol', '?')} - {device.get('name', 'Unknown')}")
                item.setData(QtCore.Qt.ItemDataRole.UserRole, device)  # Store device data
                item.setToolTip(
                    f"Type: {device.get('type', 'Unknown')}\n"
                    f"Manufacturer: {device.get('manufacturer', 'Unknown')}\n"
                    f"Part: {device.get('part_number', 'Unknown')}"
                )
                self.device_list.addItem(item)

    def _on_device_clicked(self, item):
        """Handle device selection."""
        device_data = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if device_data:  # Skip category headers
            print(f"Device selected: {device_data.get('name', 'Unknown')}")
            self.device_selected.emit(device_data)


class DevicePlacementTool:
    """
    Device Placement Tool

    Manages device placement workflow:
    1. User selects device from browser
    2. Tool switches to placement mode
    3. User clicks on canvas to place device
    """

    def __init__(self, model_space_window):
        self.window = model_space_window
        self.current_device_proto = None
        self.placement_active = False

    def set_device_prototype(self, device_proto):
        """Set the device to be placed."""
        self.current_device_proto = device_proto
        self.placement_active = True
        self.window.statusBar().showMessage(
            f"Device Placement: {device_proto.get('name', 'Unknown')} - Click to place, Esc to cancel"
        )

    def place_device_at(self, scene_pos):
        """Place the current device at the given scene position."""
        if not self.placement_active or not self.current_device_proto:
            return False

        try:
            # Import DeviceItem here to avoid circular imports
            from app.device import DeviceItem

            # Create device item
            device = DeviceItem(
                x=scene_pos.x(),
                y=scene_pos.y(),
                symbol=self.current_device_proto.get("symbol", "?"),
                name=self.current_device_proto.get("name", "Unknown"),
                manufacturer=self.current_device_proto.get("manufacturer", ""),
                part_number=self.current_device_proto.get("part_number", ""),
            )

            # Add to devices group
            device.setParentItem(self.window.devices_group)

            print(
                f"Placed device: {self.current_device_proto.get('name')} at ({scene_pos.x():.1f}, {scene_pos.y():.1f})"
            )

            # Continue placement mode (user can place multiple)
            return True

        except Exception as e:
            print(f"Error placing device: {e}")
            return False

    def cancel_placement(self):
        """Cancel device placement mode."""
        self.placement_active = False
        self.current_device_proto = None
        self.window.statusBar().showMessage("Device placement cancelled")

    def is_active(self):
        """Check if device placement is currently active."""
        return self.placement_active
