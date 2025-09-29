"""
Model Space Window - CAD workspace for device placement and design
"""

import os
import sys
import json

# Allow running as `python app\main.py` by fixing sys.path for absolute `app.*` imports
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
)

from app import dxf_import
from app.catalog import get_device_types, search_devices
from app.device import DeviceItem
from app.logging_config import setup_logging
from app.parts_warehouse import PartsWarehouseDialog

# Grid scene and defaults used by the main window
from app.scene import DEFAULT_GRID_SIZE, GridScene
from app.tools import draw as draw_tools
from app.tools.chamfer_tool import ChamferTool
from app.tools.draw import DrawMode
from app.tools.extend_tool import ExtendTool
from app.tools.fillet_tool import FilletTool
from app.tools.measure_tool import MeasureTool
from app.tools.mirror_tool import MirrorTool
from app.tools.move_tool import MoveTool
from app.tools.rotate_tool import RotateTool
from app.tools.scale_tool import ScaleTool
from app.tools.text_tool import TextTool
from app.tools.trim_tool import TrimTool
from app.tools.wiring_tool import WiringTool

# Ensure logging is configured early so module-level loggers emit during
# headless simulators and when the app starts from __main__.
setup_logging()
import logging

_logger = logging.getLogger(__name__)


class ModelSpaceWindow(QMainWindow):
    """
    Model Space Window - Dedicated CAD workspace for device placement and design.
    Contains the main design canvas with device placement, drawing tools, and CAD operations.
    """

    def __init__(self, app_controller, parent=None):
        super().__init__(parent)
        self.app_controller = app_controller
        self.setWindowTitle("AutoFire - Model Space")
        self.setObjectName("ModelSpaceWindow")

        # Initialize core attributes
        self.prefs = app_controller.prefs
        # Don't load all devices at startup - use lazy loading
        self._devices_cache = {}  # Cache for loaded device types
        self._device_types_loaded = set()
        self.px_per_ft = float(self.prefs.get("px_per_ft", 12.0))
        self.snap_label = self.prefs.get("snap_label", "grid")
        self.snap_step_in = float(self.prefs.get("snap_step_in", 0.0))

        # Initialize layers early
        self.layers = [{"id": 1, "name": "Default", "visible": True}]
        self.active_layer_id = 1

        # Create the main scene and view
        self._setup_scene_and_view()

        # Setup UI components
        self._setup_ui()

        # Initialize tools and state
        self._initialize_tools()

        # Connect to app controller signals
        self._connect_signals()

        self.resize(1200, 800)

    def _setup_scene_and_view(self):
        """Setup the main CAD scene and view."""
        from app.main import CanvasView

        # Create scene
        self.scene = GridScene(int(self.prefs.get("grid", DEFAULT_GRID_SIZE)), 0, 0, 15000, 10000)
        self.scene.snap_enabled = bool(self.prefs.get("snap", True))

        # Create device and layer groups
        self.devices_group = QtWidgets.QGraphicsItemGroup()
        self.devices_group.setZValue(100)
        self.scene.addItem(self.devices_group)

        # For compatibility with layer controls, alias layer_devices to devices_group
        self.layer_devices = self.devices_group

        self.layer_underlay = QtWidgets.QGraphicsItemGroup()
        self.layer_underlay.setZValue(-50)
        self.scene.addItem(self.layer_underlay)

        self.layer_wires = QtWidgets.QGraphicsItemGroup()
        self.layer_wires.setZValue(60)
        self.scene.addItem(self.layer_wires)

        self.layer_sketch = QtWidgets.QGraphicsItemGroup()
        self.layer_sketch.setZValue(40)
        self.scene.addItem(self.layer_sketch)

        self.layer_overlay = QtWidgets.QGraphicsItemGroup()
        self.layer_overlay.setZValue(200)
        self.scene.addItem(self.layer_overlay)

        # Create view
        self.view = CanvasView(
            self.scene,
            self.devices_group,
            self.layer_wires,
            self.layer_sketch,
            self.layer_overlay,
            self,  # Pass self as window reference
        )

        self.setCentralWidget(self.view)

    def _setup_ui(self):
        """Setup UI components like docks and status bar."""
        self._setup_docks()
        self._setup_status_bar()
        self._setup_menus()

    def _setup_docks(self):
        """Setup dockable panels."""
        # Device palette dock
        self._setup_device_palette()

        # System info palette dock
        self._setup_system_info_palette()

        # Drawing tools palette dock
        self._setup_drawing_tools_palette()

        # Annotation tools palette dock
        self._setup_annotation_tools_palette()

        # Layer tools palette dock
        self._setup_layer_tools_palette()

        # Command line palette dock
        self._setup_command_line_palette()

        # Properties dock
        self._setup_properties_dock()

    def _setup_device_palette(self):
        """Setup the device palette dock with search, filtering, and system configuration."""
        dock = QtWidgets.QDockWidget("Device Manager", self)
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)
        lay.setSpacing(5)
        lay.setContentsMargins(5, 5, 5, 5)

        # System Configuration Section
        system_group = QtWidgets.QGroupBox("System Configuration")
        system_layout = QtWidgets.QVBoxLayout(system_group)

        # System controls
        system_controls = QtWidgets.QHBoxLayout()
        self.btn_new_system = QtWidgets.QPushButton("New System")
        self.btn_new_system.clicked.connect(self._new_system_config)
        system_controls.addWidget(self.btn_new_system)

        self.btn_load_system = QtWidgets.QPushButton("Load System")
        self.btn_load_system.clicked.connect(self._load_system_config)
        system_controls.addWidget(self.btn_load_system)

        self.btn_save_system = QtWidgets.QPushButton("Save System")
        self.btn_save_system.clicked.connect(self._save_system_config)
        system_controls.addWidget(self.btn_save_system)

        system_layout.addLayout(system_controls)

        # Current system info
        self.system_info_label = QtWidgets.QLabel("No system loaded")
        self.system_info_label.setStyleSheet("font-weight: bold; color: #666;")
        system_layout.addWidget(self.system_info_label)

        lay.addWidget(system_group)

        # Separator
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        lay.addWidget(separator)

        # Add debouncing timer for search
        self._search_timer = QtCore.QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_filter)

        # Filter combo boxes
        filter_layout = QtWidgets.QHBoxLayout()

        # Type filter
        type_layout = QtWidgets.QVBoxLayout()
        type_layout.addWidget(QtWidgets.QLabel("Type:"))
        self.device_filter = QtWidgets.QComboBox()
        self.device_filter.addItem("All Types", "")
        self.device_filter.currentTextChanged.connect(lambda: self._filter_devices())
        type_layout.addWidget(self.device_filter)
        filter_layout.addLayout(type_layout)

        # Manufacturer filter
        mfg_layout = QtWidgets.QVBoxLayout()
        mfg_layout.addWidget(QtWidgets.QLabel("Manufacturer:"))
        self.manufacturer_filter = QtWidgets.QComboBox()
        self.manufacturer_filter.addItem("All Manufacturers", "")
        self.manufacturer_filter.currentTextChanged.connect(lambda: self._filter_devices())
        mfg_layout.addWidget(self.manufacturer_filter)
        filter_layout.addLayout(mfg_layout)

        lay.addLayout(filter_layout)

        # Search bar
        search_layout = QtWidgets.QHBoxLayout()
        self.device_search = QtWidgets.QLineEdit()
        self.device_search.setPlaceholderText("Search devices...")
        self.device_search.textChanged.connect(self._on_search_text_changed)
        search_layout.addWidget(QtWidgets.QLabel("Search:"))
        search_layout.addWidget(self.device_search)
        lay.addLayout(search_layout)

        # Device tree
        self.device_tree = QtWidgets.QTreeWidget()
        self.device_tree.setHeaderLabels(["Devices"])
        self.device_tree.setAlternatingRowColors(True)
        self.device_tree.setSortingEnabled(True)
        self.device_tree.itemDoubleClicked.connect(self._on_device_double_clicked)
        self.device_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.device_tree.customContextMenuRequested.connect(self._show_device_context_menu)

        lay.addWidget(self.device_tree)

        # Device count label
        self.device_count_label = QtWidgets.QLabel()
        lay.addWidget(self.device_count_label)

        # Populate device tree
        self._populate_device_tree()

        dock.setWidget(w)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def _populate_device_tree(self):
        """Populate the device tree with available devices using lazy loading."""
        try:
            # Clear existing items
            self.device_tree.clear()

            # Load device types first (lightweight)
            device_types = self._get_device_types()

            # Populate filter combo boxes
            self.device_filter.clear()
            self.device_filter.addItem("All Types", "")
            for device_type in sorted(device_types):
                self.device_filter.addItem(device_type, device_type)

            # Populate manufacturer filter
            self.manufacturer_filter.clear()
            self.manufacturer_filter.addItem("All Manufacturers", "")
            manufacturers = self._get_manufacturers()
            for manufacturer in sorted(manufacturers):
                self.manufacturer_filter.addItem(manufacturer, manufacturer)

            # Create category items but don't load devices yet
            for cat in sorted(device_types):
                cat_item = QtWidgets.QTreeWidgetItem([cat])
                cat_item.setData(
                    0, QtCore.Qt.UserRole, {"type": "category", "name": cat, "loaded": False}
                )
                # Add a placeholder child to show expandability
                placeholder = QtWidgets.QTreeWidgetItem(["Loading..."])
                placeholder.setData(0, QtCore.Qt.UserRole, {"type": "placeholder"})
                cat_item.addChild(placeholder)
                self.device_tree.addTopLevelItem(cat_item)

            # Connect expansion signal to load devices on demand
            self.device_tree.itemExpanded.connect(self._on_category_expanded)

            self._update_device_count()
        except Exception as e:
            _logger.error(f"Failed to populate device tree: {e}")

    def _get_device_types(self):
        """Get available device types without loading all devices."""
        try:
            # Try to get types from a lightweight query
            from app import catalog

            return catalog.get_device_types()
        except Exception:
            # Fallback: load a small sample to get types
            try:
                devices_sample = self.app_controller.devices_all[:100]  # Load just first 100
                return set(d.get("type", "Unknown") for d in devices_sample if d.get("type"))
            except Exception:
                return {"Unknown"}

    def _get_manufacturers(self):
        """Get available manufacturers without loading all devices."""
        try:
            # Try to get manufacturers from database
            from db import loader as db_loader

            con = db_loader.connect()
            db_loader.ensure_schema(con)
            cur = con.cursor()
            cur.execute("SELECT DISTINCT name FROM manufacturers ORDER BY name")
            manufacturers = [row["name"] for row in cur.fetchall()]
            con.close()
            return manufacturers
        except Exception:
            # Fallback
            return ["Generic"]

    def _on_category_expanded(self, item):
        """Load devices for a category when it's expanded."""
        data = item.data(0, QtCore.Qt.UserRole)
        if not (data and isinstance(data, dict) and data.get("type") == "category"):
            return

        category_name = data.get("name")
        if data.get("loaded", False):
            return  # Already loaded

        try:
            # Remove placeholder
            if item.childCount() > 0:
                placeholder = item.child(0)
                placeholder_data = placeholder.data(0, QtCore.Qt.UserRole)
                if placeholder_data and placeholder_data.get("type") == "placeholder":
                    item.removeChild(placeholder)

            # Load devices for this category
            devices = self._load_devices_for_category(category_name)

            # Add device items
            for dev in sorted(devices, key=lambda x: x.get("name", "")):
                txt = f"{dev.get('name','<unknown>')} ({dev.get('symbol','')})"
                if dev.get("part_number"):
                    txt += f" - {dev.get('part_number')}"
                it = QtWidgets.QTreeWidgetItem([txt])
                it.setData(0, QtCore.Qt.UserRole, dev)

                # Add block preview if available
                preview_pixmap = self._get_device_preview(dev)
                if preview_pixmap:
                    it.setIcon(0, QtGui.QIcon(preview_pixmap))

                item.addChild(it)

            # Mark as loaded
            data["loaded"] = True
            item.setData(0, QtCore.Qt.UserRole, data)

            self._update_device_count()

        except Exception as e:
            _logger.error(f"Failed to load devices for category {category_name}: {e}")

    def _load_devices_for_category(self, category_name):
        """Load devices for a specific category."""
        # Check cache first
        if category_name in self._devices_cache:
            return self._devices_cache[category_name]

        try:
            # Load from catalog with filtering
            from app import catalog

            devices = catalog.get_devices_by_type(category_name)

            # Cache the results
            self._devices_cache[category_name] = devices
            self._device_types_loaded.add(category_name)

            return devices

        except Exception:
            # Fallback: filter from app_controller devices
            devices = [
                d
                for d in self.app_controller.devices_all
                if d.get("type", "Unknown") == category_name
            ]
            self._devices_cache[category_name] = devices
            return devices

    def _on_search_text_changed(self):
        """Handle search text changes with debouncing."""
        self._search_timer.start(300)  # 300ms delay

    def _filter_devices(self):
        """Start filtering with immediate response for type changes."""
        # Use a timer to debounce rapid changes
        if hasattr(self, "_filter_timer"):
            self._filter_timer.stop()
        self._filter_timer = QtCore.QTimer()
        self._filter_timer.setSingleShot(True)
        self._filter_timer.timeout.connect(self._perform_filter)
        self._filter_timer.start(300)  # 300ms delay

    def _perform_filter(self):
        """Perform the actual filtering operation."""
        search_text = self.device_search.text().strip()
        filter_type = self.device_filter.currentData()
        filter_manufacturer = self.manufacturer_filter.currentData()

        if not search_text and not filter_type and not filter_manufacturer:
            # No filters, show all categories
            self._show_all_categories()
            return

        # Clear current tree and show loading
        self.device_tree.clear()
        self.device_count_label.setText("Searching...")

        try:
            # Perform efficient database search with caching
            cache_key = (search_text, filter_type, filter_manufacturer)
            if not hasattr(self, "_search_cache"):
                self._search_cache = {}

            if cache_key in self._search_cache:
                devices = self._search_cache[cache_key]
            else:
                devices = search_devices(search_text, filter_type, filter_manufacturer)
                # Cache results for 30 seconds
                self._search_cache[cache_key] = devices
                QtCore.QTimer.singleShot(30000, lambda: self._search_cache.pop(cache_key, None))

            if not devices:
                self.device_count_label.setText("No devices found")
                return

            # Group devices by type for better organization
            devices_by_type = {}
            for device in devices:
                # Use the correct type field from database
                dev_type = device.get("type", "Unknown")
                if dev_type not in devices_by_type:
                    devices_by_type[dev_type] = []
                devices_by_type[dev_type].append(device)

            # Create tree items efficiently
            total_count = 0
            for dev_type, type_devices in sorted(devices_by_type.items()):
                # Create category item
                category_item = QtWidgets.QTreeWidgetItem([f"{dev_type} ({len(type_devices)})"])
                category_item.setData(0, QtCore.Qt.UserRole, {"type": "category", "name": dev_type})
                category_item.setExpanded(True)

                # Sort devices by name for better UX
                sorted_devices = sorted(
                    type_devices,
                    key=lambda x: (x.get("manufacturer", "").lower(), x.get("name", "").lower()),
                )

                # Add devices in batches to avoid UI freezing
                for device in sorted_devices:
                    device_item = QtWidgets.QTreeWidgetItem(
                        [
                            f"{device.get('manufacturer', 'Unknown')} - {device.get('name', 'Unknown')}"
                        ]
                    )
                    device_item.setData(0, QtCore.Qt.UserRole, device)
                    category_item.addChild(device_item)

                self.device_tree.addTopLevelItem(category_item)
                total_count += len(type_devices)

            self.device_count_label.setText(
                f"Found {total_count} device{'s' if total_count != 1 else ''}"
            )

        except Exception as e:
            print(f"Error filtering devices: {e}")
            self.device_count_label.setText("Error searching devices")
            # Fallback
            self._show_all_categories()

    def _show_all_categories(self):
        """Show all device categories without filtering."""
        self.device_tree.clear()
        try:
            device_types = get_device_types()
            for cat in sorted(device_types):
                cat_item = QtWidgets.QTreeWidgetItem([cat])
                cat_item.setData(
                    0, QtCore.Qt.UserRole, {"type": "category", "name": cat, "loaded": False}
                )
                # Add placeholder
                placeholder = QtWidgets.QTreeWidgetItem(["Loading..."])
                placeholder.setData(0, QtCore.Qt.UserRole, {"type": "placeholder"})
                cat_item.addChild(placeholder)
                self.device_tree.addTopLevelItem(cat_item)
        except Exception as e:
            print(f"Error showing categories: {e}")

        self._update_device_count()

    def _update_device_count(self):
        """Update the device count label based on currently loaded devices."""
        visible_count = 0
        total_loaded = 0

        def count_visible_items(item):
            nonlocal visible_count, total_loaded
            data = item.data(0, QtCore.Qt.UserRole)

            if item.childCount() == 0:
                # Device item
                if data and data.get("type") != "placeholder":
                    total_loaded += 1
                    if not item.isHidden():
                        visible_count += 1
            else:
                # Category item - count its loaded children
                for i in range(item.childCount()):
                    child = item.child(i)
                    child_data = child.data(0, QtCore.Qt.UserRole)
                    if child_data and child_data.get("type") != "placeholder":
                        total_loaded += 1
                        if not child.isHidden():
                            visible_count += 1

        for i in range(self.device_tree.topLevelItemCount()):
            count_visible_items(self.device_tree.topLevelItem(i))

        # Show count of loaded devices
        if total_loaded == 0:
            self.device_count_label.setText("No devices loaded - expand categories to load")
        else:
            self.device_count_label.setText(
                f"Showing {visible_count} of {total_loaded} loaded devices"
            )

    def _on_device_double_clicked(self, item, column):
        """Handle double-click on device item to place it."""
        data = item.data(0, QtCore.Qt.UserRole)
        if data and isinstance(data, dict) and data.get("type") != "category":
            # It's a device, set it as current
            self.current_proto = data
            self.current_kind = data.get("type", "other").lower()
            self.statusBar().showMessage(
                f"Selected: {data.get('name', 'Unknown')} - Double-click canvas to place"
            )

            # Update CanvasView's current device for placement
            if hasattr(self.view, "set_current_device"):
                self.view.set_current_device(data)
            else:
                # Fallback for compatibility
                if hasattr(self.view, "current_proto"):
                    self.view.current_proto = data
                    self.view.current_kind = self.current_kind

                # Update ghost device for placement preview
                if hasattr(self.view, "_ensure_ghost"):
                    self.view._ensure_ghost()

    def _show_device_context_menu(self, position):
        """Show context menu for device tree items."""
        item = self.device_tree.itemAt(position)
        if not item:
            return

        menu = QtWidgets.QMenu(self)

        # Get device data
        device_data = item.data(0, Qt.UserRole)

        if isinstance(device_data, dict) and "name" in device_data:
            # Device-specific actions
            place_action = menu.addAction("Place Device")
            place_action.triggered.connect(lambda: self._place_device_from_context(device_data))

            menu.addSeparator()

            select_similar_action = menu.addAction("Select Similar")
            select_similar_action.triggered.connect(
                lambda: self._select_similar_devices(device_data)
            )

            select_all_type_action = menu.addAction(f"Select All {device_data.get('type', 'Type')}")
            select_all_type_action.triggered.connect(
                lambda: self._select_all_type_devices(device_data)
            )

            menu.addSeparator()

            view_specs_action = menu.addAction("View Specifications")
            view_specs_action.triggered.connect(lambda: self._show_device_specs(device_data))

        elif isinstance(device_data, dict) and device_data.get("type") == "category":
            # Category-specific actions
            select_all_category_action = menu.addAction(
                f"Select All {device_data.get('name', 'Category')}"
            )
            select_all_category_action.triggered.connect(
                lambda: self._select_all_category_devices(device_data)
            )

            menu.addSeparator()

            expand_all_action = menu.addAction("Expand All Categories")
            expand_all_action.triggered.connect(self._expand_all_categories)

            collapse_all_action = menu.addAction("Collapse All Categories")
            collapse_all_action.triggered.connect(self._collapse_all_categories)

        menu.exec(self.device_tree.mapToGlobal(position))

    def _place_device_from_context(self, device_data):
        """Place device from context menu."""
        self._place_device(device_data)

    def _select_similar_devices(self, device_data):
        """Select all devices similar to the given device (same type and manufacturer)."""
        device_type = device_data.get("type")
        manufacturer = device_data.get("manufacturer")

        selected_count = 0
        # Select devices in scene that match
        for item in self.scene.items():
            if hasattr(item, "device_data"):
                if (
                    item.device_data.get("type") == device_type
                    and item.device_data.get("manufacturer") == manufacturer
                ):
                    item.setSelected(True)
                    selected_count += 1

        self.statusBar().showMessage(f"Selected {selected_count} similar devices")

    def _select_all_type_devices(self, device_data):
        """Select all devices of the same type."""
        device_type = device_data.get("type")

        selected_count = 0
        # Select devices in scene that match type
        for item in self.scene.items():
            if hasattr(item, "device_data"):
                if item.device_data.get("type") == device_type:
                    item.setSelected(True)
                    selected_count += 1

        self.statusBar().showMessage(f"Selected {selected_count} {device_type} devices")

    def _select_all_category_devices(self, category_data):
        """Select all devices in a category."""
        category_name = category_data.get("name")

        selected_count = 0
        # Select devices in scene that match category
        for item in self.scene.items():
            if hasattr(item, "device_data"):
                if item.device_data.get("type") == category_name:
                    item.setSelected(True)
                    selected_count += 1

        self.statusBar().showMessage(f"Selected {selected_count} {category_name} devices")

    def _show_device_specs(self, device_data):
        """Show device specifications."""
        specs_text = f"""Device Specifications:

Name: {device_data.get('name', 'Unknown')}
Type: {device_data.get('type', 'Unknown')}
Manufacturer: {device_data.get('manufacturer', 'Unknown')}
Model/Part #: {device_data.get('part_number', 'Unknown')}

Double-click to place this device on the canvas."""

        QtWidgets.QMessageBox.information(self, "Device Specifications", specs_text)

    def _expand_all_categories(self):
        """Expand all category items."""
        for i in range(self.device_tree.topLevelItemCount()):
            item = self.device_tree.topLevelItem(i)
            item.setExpanded(True)

    def _collapse_all_categories(self):
        """Collapse all category items."""
        for i in range(self.device_tree.topLevelItemCount()):
            item = self.device_tree.topLevelItem(i)
            item.setExpanded(False)

    def _get_device_preview(self, device_data):
        """Get a small preview pixmap for the device if block/SVG data is available."""
        # For now, create simple symbolic previews based on device type
        # In a full implementation, this would load SVG blocks or custom shapes

        pixmap = QtGui.QPixmap(24, 24)
        pixmap.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        device_type = device_data.get("type", "").lower()
        symbol = device_data.get("symbol", "")

        # Create simple preview based on device type
        if "detector" in device_type:
            # Smoke/heat detector - circle with symbol
            painter.setPen(QtGui.QPen(QtGui.QColor("#FF6B35"), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor("#FF6B35").lighter(150)))
            painter.drawEllipse(2, 2, 20, 20)
            painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
            painter.drawText(6, 16, symbol[:2])

        elif (
            "notification" in device_type
            or "strobe" in device_type.lower()
            or "speaker" in device_type.lower()
        ):
            # Notification device - square with symbol
            painter.setPen(QtGui.QPen(QtGui.QColor("#4ECDC4"), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor("#4ECDC4").lighter(150)))
            painter.drawRect(2, 2, 20, 20)
            painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
            painter.drawText(6, 16, symbol[:2])

        elif "nfpa" in device_type.lower() or "exit" in device_data.get("name", "").lower():
            # NFPA 170 symbols - distinctive shape
            painter.setPen(QtGui.QPen(QtGui.QColor("#45B7D1"), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor("#45B7D1").lighter(150)))
            if "arrow" in device_data.get("name", "").lower():
                # Arrow shape
                points = [
                    QtCore.QPoint(12, 2),  # top
                    QtCore.QPoint(22, 12),  # right
                    QtCore.QPoint(18, 12),  # right indent
                    QtCore.QPoint(18, 22),  # bottom right
                    QtCore.QPoint(6, 22),  # bottom left
                    QtCore.QPoint(6, 12),  # left indent
                    QtCore.QPoint(2, 12),  # left
                ]
                painter.drawPolygon(points)
            elif "exit" in device_data.get("name", "").lower():
                # Exit sign shape - rectangle with diagonal
                painter.drawRect(2, 2, 20, 20)
                painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 2))
                painter.drawLine(6, 6, 18, 18)
                painter.drawLine(6, 18, 18, 6)
            else:
                # Generic NFPA symbol
                painter.drawRect(2, 2, 20, 20)
                painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
                painter.drawText(6, 16, symbol[:2])

        elif "initiating" in device_type:
            # Pull station - distinctive shape
            painter.setPen(QtGui.QPen(QtGui.QColor("#FFA07A"), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor("#FFA07A").lighter(150)))
            painter.drawRect(4, 4, 16, 16)
            painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
            painter.drawText(8, 16, symbol[:2])

        else:
            # Generic device - simple circle
            painter.setPen(QtGui.QPen(QtGui.QColor("#95A5A6"), 2))
            painter.setBrush(QtGui.QBrush(QtGui.QColor("#95A5A6").lighter(150)))
            painter.drawEllipse(2, 2, 20, 20)
            painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
            painter.drawText(6, 16, symbol[:2] if symbol else "?")

        painter.end()
        return pixmap

    def _setup_properties_dock(self):
        """Setup the properties dock."""
        dock = QtWidgets.QDockWidget("Properties", self)
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)

        # Properties will be populated when devices are selected
        self.properties_label = QtWidgets.QLabel("Select a device to view properties")
        lay.addWidget(self.properties_label)

        dock.setWidget(w)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def _setup_system_info_palette(self):
        """Setup the system information palette dock."""
        from app.system_info_palette import SystemInfoPalette

        self.system_info_palette = SystemInfoPalette(self.app_controller, self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.system_info_palette)

    def _setup_drawing_tools_palette(self):
        """Setup the drawing tools palette dock with quick access buttons."""
        dock = QtWidgets.QDockWidget("Drawing Tools", self)
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setSpacing(8)  # Increased from 2
        layout.setContentsMargins(8, 8, 8, 8)  # Increased from 5

        # Drawing tools section
        draw_group = QtWidgets.QGroupBox("Draw")
        draw_layout = QtWidgets.QGridLayout(draw_group)
        draw_layout.setSpacing(6)  # Increased from 2

        # Row 1: Line, Circle, Rectangle
        line_btn = QtWidgets.QPushButton("Line")
        line_btn.setToolTip("Draw Line (L)")
        line_btn.clicked.connect(lambda: self.app_controller.start_draw_tool("line"))
        draw_layout.addWidget(line_btn, 0, 0)

        circle_btn = QtWidgets.QPushButton("Circle")
        circle_btn.setToolTip("Draw Circle (C)")
        circle_btn.clicked.connect(lambda: self.app_controller.start_draw_tool("circle"))
        draw_layout.addWidget(circle_btn, 0, 1)

        rect_btn = QtWidgets.QPushButton("Rectangle")
        rect_btn.setToolTip("Draw Rectangle (R)")
        rect_btn.clicked.connect(lambda: self.app_controller.start_draw_tool("rectangle"))
        draw_layout.addWidget(rect_btn, 0, 2)

        # Row 2: Polyline, Arc, Text
        poly_btn = QtWidgets.QPushButton("Polyline")
        poly_btn.setToolTip("Draw Polyline (P)")
        poly_btn.clicked.connect(lambda: self.app_controller.start_draw_tool("polyline"))
        draw_layout.addWidget(poly_btn, 1, 0)

        arc_btn = QtWidgets.QPushButton("Arc")
        arc_btn.setToolTip("Draw Arc (A)")
        arc_btn.clicked.connect(lambda: self.app_controller.start_draw_tool("arc"))
        draw_layout.addWidget(arc_btn, 1, 1)

        text_btn = QtWidgets.QPushButton("Text")
        text_btn.setToolTip("Add Text (T)")
        text_btn.clicked.connect(self.app_controller.start_text)
        draw_layout.addWidget(text_btn, 1, 2)

        layout.addWidget(draw_group)

        # Modify tools section
        modify_group = QtWidgets.QGroupBox("Modify")
        modify_layout = QtWidgets.QGridLayout(modify_group)
        modify_layout.setSpacing(6)  # Increased from 2

        # Row 1: Move, Copy, Rotate
        move_btn = QtWidgets.QPushButton("Move")
        move_btn.setToolTip("Move (Mo)")
        move_btn.clicked.connect(self.app_controller.start_move)
        modify_layout.addWidget(move_btn, 0, 0)

        copy_btn = QtWidgets.QPushButton("Copy")
        copy_btn.setToolTip("Copy (Co)")
        copy_btn.clicked.connect(self.app_controller.start_copy)
        modify_layout.addWidget(copy_btn, 0, 1)

        rotate_btn = QtWidgets.QPushButton("Rotate")
        rotate_btn.setToolTip("Rotate (Ro)")
        rotate_btn.clicked.connect(self.app_controller.start_rotate)
        modify_layout.addWidget(rotate_btn, 0, 2)

        # Row 2: Scale, Mirror, Delete
        scale_btn = QtWidgets.QPushButton("Scale")
        scale_btn.setToolTip("Scale (Sc)")
        scale_btn.clicked.connect(self.app_controller.start_scale)
        modify_layout.addWidget(scale_btn, 1, 0)

        mirror_btn = QtWidgets.QPushButton("Mirror")
        mirror_btn.setToolTip("Mirror (Mi)")
        mirror_btn.clicked.connect(self.app_controller.start_mirror)
        modify_layout.addWidget(mirror_btn, 1, 1)

        delete_btn = QtWidgets.QPushButton("Delete")
        delete_btn.setToolTip("Delete Selection")
        delete_btn.clicked.connect(self.app_controller.action_delete_selection.trigger)
        modify_layout.addWidget(delete_btn, 1, 2)

        layout.addWidget(modify_group)

        # Special tools section
        special_group = QtWidgets.QGroupBox("Special")
        special_layout = QtWidgets.QVBoxLayout(special_group)
        special_layout.setSpacing(6)  # Increased from 2

        wire_btn = QtWidgets.QPushButton("Wire")
        wire_btn.setToolTip("Draw Wire (W)")
        wire_btn.clicked.connect(self.app_controller.start_wiring)
        special_layout.addWidget(wire_btn)

        place_btn = QtWidgets.QPushButton("Place Device")
        place_btn.setToolTip("Place Device from Palette")
        place_btn.clicked.connect(self._start_device_placement)
        special_layout.addWidget(place_btn)

        layout.addWidget(special_group)

        # Reports section - place reports on drawings
        reports_group = QtWidgets.QGroupBox("Reports on Drawing")
        reports_layout = QtWidgets.QVBoxLayout(reports_group)
        reports_layout.setSpacing(6)

        # Place calculations report
        calc_report_btn = QtWidgets.QPushButton("Calc Report")
        calc_report_btn.setToolTip("Place calculations report on drawing")
        calc_report_btn.clicked.connect(self._place_calculations_report)
        reports_layout.addWidget(calc_report_btn)

        # Place BOM report
        bom_report_btn = QtWidgets.QPushButton("BOM Report")
        bom_report_btn.setToolTip("Place bill of materials on drawing")
        bom_report_btn.clicked.connect(self._place_bom_report)
        reports_layout.addWidget(bom_report_btn)

        # Place device schedule
        schedule_btn = QtWidgets.QPushButton("Device Schedule")
        schedule_btn.setToolTip("Place device schedule on drawing")
        schedule_btn.clicked.connect(self._place_device_schedule)
        reports_layout.addWidget(schedule_btn)

        layout.addWidget(reports_group)
        for btn in w.findChildren(QtWidgets.QPushButton):
            btn.setMinimumHeight(32)
            btn.setMaximumWidth(120)
            font = QtGui.QFont("Segoe UI", 9)
            btn.setFont(font)

        dock.setWidget(w)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def _start_device_placement(self):
        """Start device placement mode from the selected device in palette."""
        if self.current_proto:
            self.view.current_proto = self.current_proto
            self.view.current_kind = self.current_kind
            self.statusBar().showMessage(
                f"Ready to place: {self.current_proto.get('name', 'Unknown')}"
            )
        else:
            QtWidgets.QMessageBox.information(
                self, "Place Device", "Select a device in the palette first."
            )

    def _setup_annotation_tools_palette(self):
        """Setup the annotation tools palette dock with text and dimensioning tools."""
        dock = QtWidgets.QDockWidget("Annotation Tools", self)
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setSpacing(2)
        layout.setContentsMargins(5, 5, 5, 5)

        # Text tools section
        text_group = QtWidgets.QGroupBox("Text")
        text_layout = QtWidgets.QVBoxLayout(text_group)
        text_layout.setSpacing(2)

        text_btn = QtWidgets.QPushButton("Single Line Text")
        text_btn.setToolTip("Add Single Line Text (T)")
        text_btn.clicked.connect(self.app_controller.start_text)
        text_layout.addWidget(text_btn)

        mtext_btn = QtWidgets.QPushButton("Multi-line Text")
        mtext_btn.setToolTip("Add Multi-line Text")
        mtext_btn.clicked.connect(self.app_controller.start_mtext)
        text_layout.addWidget(mtext_btn)

        layout.addWidget(text_group)

        # Dimension tools section
        dim_group = QtWidgets.QGroupBox("Dimensions")
        dim_layout = QtWidgets.QVBoxLayout(dim_group)
        dim_layout.setSpacing(2)

        measure_btn = QtWidgets.QPushButton("Measure")
        measure_btn.setToolTip("Measure Distance (M)")
        measure_btn.clicked.connect(self.app_controller.start_measure)
        dim_layout.addWidget(measure_btn)

        dim_btn = QtWidgets.QPushButton("Dimension")
        dim_btn.setToolTip("Add Dimension (D)")
        dim_btn.clicked.connect(self.app_controller.start_dimension)
        dim_layout.addWidget(dim_btn)

        layout.addWidget(dim_group)

        # Annotation tools section
        anno_group = QtWidgets.QGroupBox("Annotations")
        anno_layout = QtWidgets.QVBoxLayout(anno_group)
        anno_layout.setSpacing(2)

        leader_btn = QtWidgets.QPushButton("Leader")
        leader_btn.setToolTip("Add Leader Line")
        leader_btn.clicked.connect(self.app_controller.start_leader)
        anno_layout.addWidget(leader_btn)

        cloud_btn = QtWidgets.QPushButton("Revision Cloud")
        cloud_btn.setToolTip("Add Revision Cloud")
        cloud_btn.clicked.connect(self.app_controller.start_cloud)
        anno_layout.addWidget(cloud_btn)

        layout.addWidget(anno_group)

        # Make buttons smaller
        for btn in w.findChildren(QtWidgets.QPushButton):
            btn.setMinimumHeight(30)

        dock.setWidget(w)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def _setup_layer_tools_palette(self):
        """Setup the layer tools palette dock with layer management controls."""
        dock = QtWidgets.QDockWidget("Layer Tools", self)
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setSpacing(8)  # Increased from 2
        layout.setContentsMargins(8, 8, 8, 8)  # Increased from 5

        # Current layer display
        current_group = QtWidgets.QGroupBox("Current Layer")
        current_layout = QtWidgets.QVBoxLayout(current_group)

        self.current_layer_label = QtWidgets.QLabel("Default")
        self.current_layer_label.setStyleSheet(
            "font-weight: bold; padding: 5px; background: #e6e6e6;"
        )
        current_layout.addWidget(self.current_layer_label)

        layout.addWidget(current_group)

        # Layer controls
        controls_group = QtWidgets.QGroupBox("Layer Controls")
        controls_layout = QtWidgets.QVBoxLayout(controls_group)
        controls_layout.setSpacing(6)  # Increased from 2

        # Layer visibility toggles
        grid_btn = QtWidgets.QPushButton("Toggle Grid")
        grid_btn.setCheckable(True)
        grid_btn.setChecked(True)
        grid_btn.clicked.connect(self.toggle_grid)
        controls_layout.addWidget(grid_btn)

        snap_btn = QtWidgets.QPushButton("Toggle Snap")
        snap_btn.setCheckable(True)
        snap_btn.setChecked(bool(self.prefs.get("snap", True)))
        snap_btn.clicked.connect(self.toggle_snap)
        controls_layout.addWidget(snap_btn)

        coverage_btn = QtWidgets.QPushButton("Toggle Coverage")
        coverage_btn.setCheckable(True)
        coverage_btn.setChecked(bool(self.prefs.get("show_coverage", True)))
        coverage_btn.clicked.connect(self._toggle_coverage)
        controls_layout.addWidget(coverage_btn)

        layout.addWidget(controls_group)

        # Layer management
        manage_group = QtWidgets.QGroupBox("Layer Management")
        manage_layout = QtWidgets.QVBoxLayout(manage_group)
        manage_layout.setSpacing(6)  # Increased from 2

        layer_mgr_btn = QtWidgets.QPushButton("Layer Manager")
        layer_mgr_btn.setToolTip("Open detailed layer manager")
        layer_mgr_btn.clicked.connect(self.open_layer_manager)
        manage_layout.addWidget(layer_mgr_btn)

        # Quick layer controls
        quick_group = QtWidgets.QGroupBox("Quick Controls")
        quick_layout = QtWidgets.QVBoxLayout(quick_group)
        quick_layout.setSpacing(4)

        # Show all layers
        show_all_btn = QtWidgets.QPushButton("Show All")
        show_all_btn.setToolTip("Show all layers")
        show_all_btn.clicked.connect(self._show_all_layers)
        quick_layout.addWidget(show_all_btn)

        # Hide all layers
        hide_all_btn = QtWidgets.QPushButton("Hide All")
        hide_all_btn.setToolTip("Hide all layers except current")
        hide_all_btn.clicked.connect(self._hide_all_layers)
        quick_layout.addWidget(hide_all_btn)

        manage_layout.addWidget(quick_group)

        layout.addWidget(manage_group)

        # Make buttons smaller and set better font
        for btn in w.findChildren(QtWidgets.QPushButton):
            btn.setMinimumHeight(32)
            btn.setMaximumWidth(120)
            font = QtGui.QFont("Segoe UI", 9)
            btn.setFont(font)

        dock.setWidget(w)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def _show_all_layers(self):
        """Show all layers."""
        # Show all layer groups
        self.devices_group.setVisible(True)
        self.layer_underlay.setVisible(True)
        self.layer_wires.setVisible(True)
        self.layer_sketch.setVisible(True)
        self.layer_overlay.setVisible(True)
        self.statusBar().showMessage("All layers shown")

    def _hide_all_layers(self):
        """Hide all layers except the current active layer."""
        # For now, just hide non-essential layers
        self.layer_underlay.setVisible(False)
        self.layer_wires.setVisible(False)
        self.layer_sketch.setVisible(False)
        self.layer_overlay.setVisible(False)
        # Keep devices layer visible
        self.devices_group.setVisible(True)
        self.statusBar().showMessage("Non-essential layers hidden")

    def _place_calculations_report(self):
        """Place a calculations report as a graphical element on the drawing."""
        try:
            from app.dialogs.calculations_dialog import CalculationsDialog
            # Generate report data
            report_data = self._generate_calculations_report_data()

            # Create a graphical text item with the report
            report_text = self._format_report_text("CALCULATIONS REPORT", report_data)
            self._place_report_on_drawing(report_text, "Calculations Report")
        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Could not place calculations report: {str(e)}")

    def _place_bom_report(self):
        """Place a bill of materials report as a graphical element on the drawing."""
        try:
            from app.dialogs.bom import BomReportDialog
            # Generate BOM data
            bom_data = self._generate_bom_report_data()

            # Create a graphical text item with the BOM
            report_text = self._format_report_text("BILL OF MATERIALS", bom_data)
            self._place_report_on_drawing(report_text, "BOM Report")
        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Could not place BOM report: {str(e)}")

    def _place_device_schedule(self):
        """Place a device schedule report as a graphical element on the drawing."""
        try:
            # Generate device schedule data
            schedule_data = self._generate_device_schedule_data()

            # Create a graphical text item with the schedule
            report_text = self._format_report_text("DEVICE SCHEDULE", schedule_data)
            self._place_report_on_drawing(report_text, "Device Schedule")
        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Could not place device schedule: {str(e)}")

    def _generate_calculations_report_data(self):
        """Generate calculations report data."""
        # This would normally get data from the calculations dialog
        return [
            "Device Count: 25",
            "Coverage Area: 5000 sq ft",
            "Battery Capacity: 100 AH",
            "Circuit Count: 3",
            "Voltage Drop: < 3%",
            "NFPA 72 Compliant: Yes"
        ]

    def _generate_bom_report_data(self):
        """Generate BOM report data."""
        # This would normally get data from the BOM dialog
        return [
            "Smoke Detectors: 15 x $25 = $375",
            "Heat Detectors: 5 x $30 = $150",
            "Pull Stations: 3 x $45 = $135",
            "Strobes: 8 x $85 = $680",
            "Control Panel: 1 x $1200 = $1200",
            "Total: $2540"
        ]

    def _generate_device_schedule_data(self):
        """Generate device schedule data."""
        # This would normally get data from the device schedule dialog
        return [
            "Zone 1: Devices 1-8 (Floor 1)",
            "Zone 2: Devices 9-15 (Floor 2)",
            "Zone 3: Devices 16-25 (Floor 3)",
            "Total Devices: 25",
            "Addressable: Yes"
        ]

    def _format_report_text(self, title, data_lines):
        """Format report data into a text block."""
        text = f"{title}\n{'=' * len(title)}\n\n"
        for line in data_lines:
            text += f"{line}\n"
        text += f"\nGenerated: {QtCore.QDateTime.currentDateTime().toString()}"
        return text

    def _place_report_on_drawing(self, report_text, report_type):
        """Place a report as a graphical text item on the drawing."""
        # Create a text item with the report
        text_item = QtWidgets.QGraphicsTextItem(report_text)
        text_item.setFont(QtGui.QFont("Segoe UI", 10))
        text_item.setDefaultTextColor(QtGui.QColor("black"))

        # Add a background rectangle for better visibility
        rect = text_item.boundingRect()
        background = QtWidgets.QGraphicsRectItem(rect)
        background.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255, 220)))
        background.setPen(QtGui.QPen(QtGui.QColor("gray"), 1))

        # Group the background and text
        group = QtWidgets.QGraphicsItemGroup()
        group.addToGroup(background)
        group.addToGroup(text_item)

        # Position near the center but offset
        center = self.view.mapToScene(self.view.viewport().rect().center())
        group.setPos(center.x() - rect.width()/2, center.y() - rect.height()/2)

        # Make it movable and selectable
        group.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        group.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        # Add to the overlay layer
        self.layer_overlay.addToGroup(group)

        self.statusBar().showMessage(f"{report_type} placed on drawing - drag to reposition")

    def _toggle_coverage(self):
        """Toggle coverage overlays display."""
        self.show_coverage = not self.show_coverage
        # Update all coverage items in the scene
        for item in self.scene.items():
            if hasattr(item, "set_coverage_enabled"):
                item.set_coverage_enabled(self.show_coverage)

    def _toggle_device_palette(self):
        """Toggle device palette visibility."""
        # Find the device palette dock
        for dock in self.findChildren(QtWidgets.QDockWidget):
            if dock.windowTitle() == "Device Manager":
                dock.setVisible(not dock.isVisible())
                self.act_device_palette.setChecked(dock.isVisible())
                break

    def _toggle_drawing_tools(self):
        """Toggle drawing tools palette visibility."""
        for dock in self.findChildren(QtWidgets.QDockWidget):
            if dock.windowTitle() == "Drawing Tools":
                dock.setVisible(not dock.isVisible())
                self.act_drawing_tools.setChecked(dock.isVisible())
                break

    def _toggle_annotation_tools(self):
        """Toggle annotation tools palette visibility."""
        for dock in self.findChildren(QtWidgets.QDockWidget):
            if dock.windowTitle() == "Annotation Tools":
                dock.setVisible(not dock.isVisible())
                self.act_annotation_tools.setChecked(dock.isVisible())
                break

    def _toggle_layer_tools(self):
        """Toggle layer tools palette visibility."""
        for dock in self.findChildren(QtWidgets.QDockWidget):
            if dock.windowTitle() == "Layer Tools":
                dock.setVisible(not dock.isVisible())
                self.act_layer_tools.setChecked(dock.isVisible())
                break

    def _toggle_command_line(self):
        """Toggle command line palette visibility."""
        for dock in self.findChildren(QtWidgets.QDockWidget):
            if dock.windowTitle() == "Command Line":
                dock.setVisible(not dock.isVisible())
                self.act_command_line.setChecked(dock.isVisible())
                break

    def _toggle_system_info(self):
        """Toggle system info palette visibility."""
        for dock in self.findChildren(QtWidgets.QDockWidget):
            if dock.windowTitle() == "System Info":
                dock.setVisible(not dock.isVisible())
                self.act_system_info.setChecked(dock.isVisible())
                break

    def _setup_command_line_palette(self):
        """Setup the command line palette dock for CAD commands."""
        dock = QtWidgets.QDockWidget("Command Line", self)
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setSpacing(2)
        layout.setContentsMargins(5, 5, 5, 5)

        # Command input
        input_group = QtWidgets.QGroupBox("Command Input")
        input_layout = QtWidgets.QVBoxLayout(input_group)

        self.command_input = QtWidgets.QLineEdit()
        self.command_input.setPlaceholderText("Enter CAD command...")
        self.command_input.returnPressed.connect(self._execute_command)
        input_layout.addWidget(self.command_input)

        # Quick commands
        quick_layout = QtWidgets.QHBoxLayout()
        quick_layout.setSpacing(2)

        for cmd in ["line", "circle", "move", "copy", "delete"]:
            btn = QtWidgets.QPushButton(cmd.upper())
            btn.setMinimumHeight(25)
            btn.clicked.connect(lambda checked, c=cmd: self._execute_quick_command(c))
            quick_layout.addWidget(btn)

        input_layout.addLayout(quick_layout)
        layout.addWidget(input_group)

        # Command history
        history_group = QtWidgets.QGroupBox("Command History")
        history_layout = QtWidgets.QVBoxLayout(history_group)

        self.command_history = QtWidgets.QListWidget()
        self.command_history.setMaximumHeight(150)
        self.command_history.itemDoubleClicked.connect(self._repeat_command)
        history_layout.addWidget(self.command_history)

        # Clear history button
        clear_btn = QtWidgets.QPushButton("Clear History")
        clear_btn.clicked.connect(self.command_history.clear)
        history_layout.addWidget(clear_btn)

        layout.addWidget(history_group)

        dock.setWidget(w)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    def _execute_command(self):
        """Execute the command entered in the command line."""
        command = self.command_input.text().strip().lower()
        if command:
            self._add_to_history(command)
            self._process_command(command)
            self.command_input.clear()

    def _execute_quick_command(self, command):
        """Execute a quick command from the button."""
        self._add_to_history(command)
        self._process_command(command)

    def _process_command(self, command):
        """Process a CAD command."""
        command_map = {
            "line": lambda: self.app_controller.start_draw_tool("line"),
            "circle": lambda: self.app_controller.start_draw_tool("circle"),
            "rectangle": lambda: self.app_controller.start_draw_tool("rectangle"),
            "polyline": lambda: self.app_controller.start_draw_tool("polyline"),
            "arc": lambda: self.app_controller.start_draw_tool("arc"),
            "move": self.app_controller.start_move,
            "copy": self.app_controller.start_copy,
            "rotate": self.app_controller.start_rotate,
            "scale": self.app_controller.start_scale,
            "mirror": self.app_controller.start_mirror,
            "delete": lambda: self.app_controller.action_delete_selection.trigger(),
            "text": self.app_controller.start_text,
            "measure": self.app_controller.start_measure,
        }

        if command in command_map:
            try:
                command_map[command]()
                self.statusBar().showMessage(f"Command '{command}' executed")
            except Exception as e:
                self.statusBar().showMessage(f"Error executing '{command}': {e}")
        else:
            self.statusBar().showMessage(f"Unknown command: {command}")

    def _add_to_history(self, command):
        """Add command to history list."""
        self.command_history.addItem(command)
        # Keep only last 50 commands
        while self.command_history.count() > 50:
            self.command_history.takeItem(0)
        # Scroll to bottom
        self.command_history.scrollToBottom()

    def _repeat_command(self, item):
        """Repeat a command from history."""
        command = item.text()
        self._process_command(command)

    def _setup_status_bar(self):
        """Setup the AutoCAD-like status bar with command bar, space indicators, and controls."""
        # Left side: Space selector and lock
        self.space_combo = QtWidgets.QComboBox()
        self.space_combo.addItems(["Model", "Paper"])
        self.space_combo.setCurrentIndex(0)  # Always start in Model space
        self.space_lock = QtWidgets.QToolButton()
        self.space_lock.setCheckable(True)
        self.space_lock.setText("Lock")
        self.statusBar().addWidget(QtWidgets.QLabel("Space:"))
        self.statusBar().addWidget(self.space_combo)
        self.statusBar().addWidget(self.space_lock)

        # Space combo is disabled since this is Model Space window
        self.space_combo.setEnabled(False)
        self.space_lock.setEnabled(False)

        # Right side: Scale badge, space badge, grid controls, command bar
        self.scale_badge = QtWidgets.QLabel("")
        self.scale_badge.setStyleSheet("QLabel { color: #c0c0c0; }")
        self.statusBar().addPermanentWidget(self.scale_badge)

        self.space_badge = QtWidgets.QLabel("MODEL SPACE")
        self.space_badge.setStyleSheet("QLabel { color: #7dcfff; font-weight: bold; }")
        self.statusBar().addPermanentWidget(self.space_badge)

        # Grid controls
        grid_wrap = QtWidgets.QWidget()
        grid_lay = QtWidgets.QHBoxLayout(grid_wrap)
        grid_lay.setContentsMargins(6, 0, 6, 0)
        grid_lay.setSpacing(10)

        # Grid opacity control
        grid_lay.addWidget(QtWidgets.QLabel("Grid"))
        self.slider_grid = QtWidgets.QSlider(Qt.Horizontal)
        self.slider_grid.setMinimum(10)
        self.slider_grid.setMaximum(100)
        self.slider_grid.setFixedWidth(110)
        cur_op = float(self.prefs.get("grid_opacity", 0.25))
        self.slider_grid.setValue(int(max(10, min(100, round(cur_op * 100)))))
        self.lbl_gridp = QtWidgets.QLabel(f"{int(self.slider_grid.value())}%")
        grid_lay.addWidget(self.slider_grid)
        grid_lay.addWidget(self.lbl_gridp)

        # Grid size control
        grid_lay.addWidget(QtWidgets.QLabel("Size"))
        self.spin_grid_status = QtWidgets.QSpinBox()
        self.spin_grid_status.setRange(2, 500)
        self.spin_grid_status.setValue(self.scene.grid_size)
        self.spin_grid_status.setFixedWidth(70)
        grid_lay.addWidget(self.spin_grid_status)

        self.statusBar().addPermanentWidget(grid_wrap)

        # Command bar
        cmd_wrap = QtWidgets.QWidget()
        cmd_l = QtWidgets.QHBoxLayout(cmd_wrap)
        cmd_l.setContentsMargins(6, 0, 6, 0)
        cmd_l.setSpacing(6)
        cmd_l.addWidget(QtWidgets.QLabel("Cmd:"))
        self.cmd = QtWidgets.QLineEdit()
        self.cmd.setPlaceholderText("Type command (e.g., L, RECT, MOVE)…")
        self.cmd.returnPressed.connect(self._run_command)
        cmd_l.addWidget(self.cmd)
        self.statusBar().addPermanentWidget(cmd_wrap, 1)

        # Connect grid controls
        self.slider_grid.valueChanged.connect(self._apply_grid_opacity)
        self.spin_grid_status.valueChanged.connect(self._change_grid_size)

        # Update initial scale badge
        self._update_scale_badge()

    def _apply_grid_opacity(self, val: int):
        """Apply grid opacity from slider."""
        op = max(0.10, min(1.00, val / 100.0))
        self.scene.set_grid_style(opacity=op)
        self.prefs["grid_opacity"] = op
        self.app_controller.save_prefs()
        self.lbl_gridp.setText(f"{int(val)}%")

    def _change_grid_size(self, val: int):
        """Change grid size."""
        self.scene.set_grid_size(val)
        self.prefs["grid"] = val
        self.app_controller.save_prefs()

    def _update_scale_badge(self):
        """Update the scale badge with current pixels per foot."""
        px_per_ft = self.px_per_ft
        self.scale_badge.setText(f"{px_per_ft:.1f} px/ft")

    def _run_command(self):
        """Execute command from command bar."""
        cmd = self.cmd.text().strip().upper()
        self.cmd.clear()

        if cmd in ("L", "LINE"):
            self.draw.set_mode(draw_tools.DrawMode.LINE)
            self.statusBar().showMessage("Draw: Line — click to start, Esc to finish")
        elif cmd in ("R", "RECT", "RECTANGLE"):
            self.draw.set_mode(draw_tools.DrawMode.RECT)
            self.statusBar().showMessage("Draw: Rectangle — click to start, Esc to finish")
        elif cmd in ("C", "CIRCLE"):
            self.draw.set_mode(draw_tools.DrawMode.CIRCLE)
            self.statusBar().showMessage("Draw: Circle — click to start, Esc to finish")
        elif cmd in ("P", "POLY", "POLYLINE"):
            self.draw.set_mode(draw_tools.DrawMode.POLYLINE)
            self.statusBar().showMessage("Draw: Polyline — click points, Enter to finish")
        elif cmd in ("A", "ARC"):
            self.draw.set_mode(draw_tools.DrawMode.ARC3)
            self.statusBar().showMessage("Draw: Arc (3-point) — click 3 points")
        elif cmd in ("W", "WIRE"):
            self.draw.set_mode(draw_tools.DrawMode.WIRE)
            self.statusBar().showMessage("Draw: Wire — click to start, Esc to finish")
        elif cmd in ("T", "TEXT"):
            self.start_text()
        elif cmd in ("M", "MEASURE"):
            self.start_measure()
        elif cmd in ("O", "OFFSET"):
            self.offset_selected_dialog()
        elif cmd in ("TRIM",):
            self.start_trim()
        elif cmd in ("EXTEND", "EXT"):
            self.start_extend()
        elif cmd in ("MOVE",):
            self.start_move()
        elif cmd in ("COPY",):
            self.start_copy()
        elif cmd in ("ROTATE", "ROT"):
            self.start_rotate()
        elif cmd in ("MIRROR", "MIR"):
            self.start_mirror()
        elif cmd in ("SCALE",):
            self.start_scale()
        elif cmd in ("F", "FILLET"):
            self.start_fillet()
        elif cmd in ("CHAMFER", "CHA"):
            self.start_chamfer()
        else:
            self.statusBar().showMessage(f"Unknown command: {cmd}")

    def start_text(self):
        """Start text placement tool."""
        self.text_tool.start()

    def start_measure(self):
        """Start measure tool."""
        self.measure_tool.start()

    def start_dimension(self):
        """Start dimension tool."""
        QMessageBox.information(self, "Dimension", "Dimension tool not yet implemented.")

    def start_move(self):
        """Start move tool."""
        self.move_tool.start()

    def start_copy(self):
        """Start copy tool (move with copy)."""
        self.move_tool.start(copy=True)

    def start_rotate(self):
        """Start rotate tool."""
        self.rotate_tool.start()

    def start_scale(self):
        """Start scale tool."""
        self.scale_tool.start()

    def start_mirror(self):
        """Start mirror tool."""
        self.mirror_tool.start()

    def start_trim(self):
        """Start trim tool."""
        self.trim_tool.start()

    def start_extend(self):
        """Start extend tool."""
        self.extend_tool.start()

    def start_fillet(self):
        """Start fillet tool."""
        self.fillet_tool.start()

    def start_chamfer(self):
        """Start chamfer tool."""
        self.chamfer_tool.start()

    def offset_selected_dialog(self):
        """Show offset dialog for selected items (stub)."""
        self.statusBar().showMessage("Offset: not yet implemented")

    def _setup_menus(self):
        """Setup menus using global menu bar."""
        # Use global menu bar from app controller
        self.app_controller.create_global_menu_bar(self)

        # Setup main toolbar
        self._setup_toolbar()

        # Add window-specific menus after global ones
        menubar = self.menuBar()

        # View menu for model space specific options
        view_menu = menubar.addMenu("&View")
        self.act_grid = QtGui.QAction("Grid", self, checkable=True)
        self.act_grid.setChecked(True)
        self.act_grid.toggled.connect(self.toggle_grid)
        view_menu.addAction(self.act_grid)

        self.act_snap = QtGui.QAction("Snap", self, checkable=True)
        self.act_snap.setChecked(bool(self.prefs.get("snap", True)))
        self.act_snap.toggled.connect(self.toggle_snap)
        view_menu.addAction(self.act_snap)

        view_menu.addSeparator()

        # Tool palettes submenu
        palettes_menu = view_menu.addMenu("Tool Palettes")

        self.act_device_palette = QtGui.QAction("Device Manager", self, checkable=True)
        self.act_device_palette.setChecked(True)
        self.act_device_palette.triggered.connect(self._toggle_device_palette)
        palettes_menu.addAction(self.act_device_palette)

        self.act_drawing_tools = QtGui.QAction("Drawing Tools", self, checkable=True)
        self.act_drawing_tools.setChecked(True)
        self.act_drawing_tools.triggered.connect(self._toggle_drawing_tools)
        palettes_menu.addAction(self.act_drawing_tools)

        self.act_annotation_tools = QtGui.QAction("Annotation Tools", self, checkable=True)
        self.act_annotation_tools.setChecked(True)
        self.act_annotation_tools.triggered.connect(self._toggle_annotation_tools)
        palettes_menu.addAction(self.act_annotation_tools)

        self.act_layer_tools = QtGui.QAction("Layer Tools", self, checkable=True)
        self.act_layer_tools.setChecked(True)
        self.act_layer_tools.triggered.connect(self._toggle_layer_tools)
        palettes_menu.addAction(self.act_layer_tools)

        self.act_command_line = QtGui.QAction("Command Line", self, checkable=True)
        self.act_command_line.setChecked(True)
        self.act_command_line.triggered.connect(self._toggle_command_line)
        palettes_menu.addAction(self.act_command_line)

        self.act_system_info = QtGui.QAction("System Info", self, checkable=True)
        self.act_system_info.setChecked(True)
        self.act_system_info.triggered.connect(self._toggle_system_info)
        palettes_menu.addAction(self.act_system_info)

    def _setup_toolbar(self):
        """Setup the main toolbar with commonly used tools."""
        # Create main toolbar
        self.main_toolbar = self.addToolBar("Main Tools")
        self.main_toolbar.setIconSize(QtCore.QSize(24, 24))

        # Set toolbar font
        toolbar_font = QtGui.QFont("Segoe UI", 9)
        self.main_toolbar.setFont(toolbar_font)

        # Drawing tools section
        self.main_toolbar.addWidget(QtWidgets.QLabel("Draw: "))

        # Line tool
        line_action = QtGui.QAction("Line", self)
        line_action.setShortcut("L")
        line_action.triggered.connect(lambda: self.app_controller.start_draw_tool("line"))
        self.main_toolbar.addAction(line_action)

        # Circle tool
        circle_action = QtGui.QAction("Circle", self)
        circle_action.setShortcut("C")
        circle_action.triggered.connect(lambda: self.app_controller.start_draw_tool("circle"))
        self.main_toolbar.addAction(circle_action)

        # Rectangle tool
        rect_action = QtGui.QAction("Rectangle", self)
        rect_action.setShortcut("R")
        rect_action.triggered.connect(lambda: self.app_controller.start_draw_tool("rectangle"))
        self.main_toolbar.addAction(rect_action)

        # Polyline tool
        poly_action = QtGui.QAction("Polyline", self)
        poly_action.setShortcut("P")
        poly_action.triggered.connect(lambda: self.app_controller.start_draw_tool("polyline"))
        self.main_toolbar.addAction(poly_action)

        self.main_toolbar.addSeparator()

        # Modify tools section
        self.main_toolbar.addWidget(QtWidgets.QLabel("Modify: "))

        # Move tool
        move_action = QtGui.QAction("Move", self)
        move_action.setShortcut("Mo")
        move_action.triggered.connect(self.app_controller.start_move)
        self.main_toolbar.addAction(move_action)

        # Copy tool
        copy_action = QtGui.QAction("Copy", self)
        copy_action.setShortcut("Co")
        copy_action.triggered.connect(self.app_controller.start_copy)
        self.main_toolbar.addAction(copy_action)

        # Rotate tool
        rotate_action = QtGui.QAction("Rotate", self)
        rotate_action.setShortcut("Ro")
        rotate_action.triggered.connect(self.app_controller.start_rotate)
        self.main_toolbar.addAction(rotate_action)

        # Scale tool
        scale_action = QtGui.QAction("Scale", self)
        scale_action.setShortcut("Sc")
        scale_action.triggered.connect(self.app_controller.start_scale)
        self.main_toolbar.addAction(scale_action)

        self.main_toolbar.addSeparator()

        # Annotation tools section
        self.main_toolbar.addWidget(QtWidgets.QLabel("Annotate: "))

        # Text tool
        text_action = QtGui.QAction("Text", self)
        text_action.setShortcut("T")
        text_action.triggered.connect(self.app_controller.start_text)
        self.main_toolbar.addAction(text_action)

        # Measure tool
        measure_action = QtGui.QAction("Measure", self)
        measure_action.setShortcut("M")
        measure_action.triggered.connect(self.app_controller.start_measure)
        self.main_toolbar.addAction(measure_action)

        self.main_toolbar.addSeparator()

        # View controls
        self.main_toolbar.addWidget(QtWidgets.QLabel("View: "))

        # Zoom in
        zoom_in_action = QtGui.QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.app_controller.action_zoom_in.trigger)
        self.main_toolbar.addAction(zoom_in_action)

        # Zoom out
        zoom_out_action = QtGui.QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(self.app_controller.action_zoom_out.trigger)
        self.main_toolbar.addAction(zoom_out_action)

        # Fit view
        fit_action = QtGui.QAction("Fit View", self)
        fit_action.triggered.connect(self.app_controller.action_fit_view.trigger)
        self.main_toolbar.addAction(fit_action)

    def _initialize_tools(self):
        """Initialize CAD tools and state."""
        # Initialize tool state
        self.current_proto = None
        self.current_kind = "other"
        self.ghost = None
        self.show_coverage = bool(self.prefs.get("show_coverage", True))

        # Initialize history
        self.history = []
        self.history_index = -1

        # Initialize draw controller
        self.draw = draw_tools.DrawController(self, self.layer_sketch)

        # Initialize CAD tools
        self.text_tool = TextTool(self, self.layer_sketch)
        self.measure_tool = MeasureTool(self, self.layer_overlay)
        self.move_tool = MoveTool(self)
        self.rotate_tool = RotateTool(self)
        self.scale_tool = ScaleTool(self)
        self.mirror_tool = MirrorTool(self)
        self.trim_tool = TrimTool(self)
        self.extend_tool = ExtendTool(self)
        self.fillet_tool = FilletTool(self)
        self.chamfer_tool = ChamferTool(self)
        self.wiring_tool = WiringTool(self)

        # Connect wiring tool to system info palette
        if hasattr(self, "system_info_palette"):
            self.system_info_palette.wiring_tool = self.wiring_tool

    def _connect_signals(self):
        """Connect to app controller signals."""
        # Connect device tree selection
        self.device_tree.itemClicked.connect(self.on_device_selected)

        # Connect scene selection changes
        self.scene.selectionChanged.connect(self._on_selection_changed)

        # Connect to app controller signals for inter-window communication
        self.app_controller.model_space_changed.connect(self.on_model_space_changed)
        self.app_controller.paperspace_changed.connect(self.on_paperspace_changed)
        self.app_controller.project_changed.connect(self.on_project_changed)

        # Note: CanvasView already handles coordinate display in status bar

    def on_device_selected(self, item, column):
        """Handle device selection from palette."""
        dev = item.data(0, 256)  # Qt.UserRole
        if dev:
            self.current_proto = dev
            self.current_kind = dev.get("type", "other").lower()
            self.statusBar().showMessage(f"Selected: {dev.get('name', 'Unknown')}")

            # Update CanvasView's current_proto for device placement
            self.view.current_proto = dev
            self.view.current_kind = self.current_kind

            # Update ghost device for placement preview
            if hasattr(self.view, "_ensure_ghost"):
                self.view._ensure_ghost()

    def on_model_space_changed(self, change_data):
        """Handle model space changes from other windows."""
        change_type = change_data.get("type", "general")
        # Handle different types of changes
        if change_type == "device_placed":
            # Refresh device display if needed
            self.scene.update()
        elif change_type == "scene_cleared":
            # Handle scene clearing
            pass

    def on_paperspace_changed(self, change_data):
        """Handle paperspace changes from other windows."""
        change_type = change_data.get("type", "general")
        # Model space window might not need to react to paperspace changes
        # but this is here for future expansion
        pass

    def on_project_changed(self, change_data):
        """Handle project state changes."""
        change_type = change_data.get("type", "general")
        if change_type == "new_project":
            # Clear current scene
            self._initialize_tools()
        elif change_type == "project_loaded":
            # Refresh display
            self.scene.update()

    def toggle_grid(self, on):
        """Toggle grid visibility."""
        self.scene.show_grid = bool(on)
        self.scene.update()

    def toggle_snap(self, on):
        """Toggle snap functionality."""
        self.scene.snap_enabled = bool(on)

    def get_scene_state(self):
        """Get the current scene state for serialization."""
        # Return scene data for project saving
        return {
            "scene_type": "model_space",
            "devices": [],  # Will be populated
            "wires": [],  # Will be populated
            "sketch": [],  # Will be populated
        }

    def load_scene_state(self, data):
        """Load scene state from serialized data."""
        # Load scene data from project
        pass

    # ---------- Menu action implementations ----------
    # File operations
    def import_dxf_underlay(self):
        """Import DXF file as underlay."""
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(
            self, "Import DXF", "", "DXF Files (*.dxf);;All Files (*)"
        )
        if not path:
            return
        try:
            bounds, layer_groups = dxf_import.import_dxf_into_group(
                path, self.layer_underlay, self.px_per_ft
            )
            if bounds and not bounds.isNull():
                # Expand scene rect to include underlay, then fit
                self.scene.setSceneRect(
                    self.scene.sceneRect().united(bounds.adjusted(-200, -200, 200, 200))
                )
                self.view.fitInView(
                    bounds.adjusted(-100, -100, 100, 100), Qt.AspectRatioMode.KeepAspectRatio
                )
            self.statusBar().showMessage(f"Imported underlay: {os.path.basename(path)}")
            self._dxf_layers = layer_groups
        except Exception as ex:
            QMessageBox.critical(self, "DXF Import Error", str(ex))

    def import_pdf_underlay(self):
        """Import PDF file as underlay."""
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(
            self, "Import PDF", "", "PDF Files (*.pdf);;All Files (*)"
        )
        if not path:
            return

        try:
            # Import required libraries
            from pdf2image import convert_from_path

            # Ask user which page to import
            from PyPDF2 import PdfReader
            from PySide6.QtGui import QImage, QPixmap
            from PySide6.QtWidgets import QGraphicsPixmapItem

            reader = PdfReader(path)
            if len(reader.pages) == 0:
                QMessageBox.warning(self, "PDF Import", "PDF file has no pages.")
                return

            if len(reader.pages) > 1:
                from PySide6.QtWidgets import QInputDialog

                page_num, ok = QInputDialog.getInt(
                    self,
                    "PDF Import",
                    f"PDF has {len(reader.pages)} pages. Enter page number (1-{len(reader.pages)}):",
                    1,
                    1,
                    len(reader.pages),
                )
                if not ok:
                    return
                page_idx = page_num - 1
            else:
                page_idx = 0

            # Convert PDF page to image
            self.statusBar().showMessage("Converting PDF page to image...")
            images = convert_from_path(
                path, first_page=page_idx + 1, last_page=page_idx + 1, dpi=150
            )

            if not images:
                QMessageBox.warning(self, "PDF Import", "Failed to convert PDF page to image.")
                return

            # Convert PIL image to QPixmap
            pil_image = images[0]

            # Convert PIL image to QImage
            if pil_image.mode == "RGB":
                format = QImage.Format.Format_RGB888
            elif pil_image.mode == "RGBA":
                format = QImage.Format.Format_RGBA8888
            else:
                pil_image = pil_image.convert("RGB")
                format = QImage.Format.Format_RGB888

            # Create QImage from PIL image data
            qimg = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, format)
            pixmap = QPixmap.fromImage(qimg)

            # Create graphics item
            item = QGraphicsPixmapItem(pixmap)

            # Scale to reasonable size (150 DPI, scale to our coordinate system)
            scale_factor = self.px_per_ft / 150.0  # Convert from 150 DPI to our units
            item.setScale(scale_factor)

            # Add to underlay layer
            self.layer_underlay.addToGroup(item)

            # Position at origin
            item.setPos(0, 0)

            self.statusBar().showMessage(f"PDF page {page_idx + 1} imported as underlay")
            QMessageBox.information(
                self,
                "PDF Import",
                f"PDF page {page_idx + 1} imported successfully as underlay image.",
            )

        except ImportError as ex:
            QMessageBox.critical(
                self,
                "PDF Import Error",
                f"Required libraries not available: {ex}\nPlease install pdf2image and PyPDF2.",
            )
        except Exception as ex:
            QMessageBox.critical(self, "PDF Import Error", str(ex))

    def export_png(self):
        """Export current view as PNG."""
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getSaveFileName(
            self, "Export PNG", "", "PNG Files (*.png);;All Files (*)"
        )
        if not path:
            return
        try:
            # Create a pixmap to render the scene
            rect = self.scene.sceneRect()
            pixmap = QtGui.QPixmap(int(rect.width()), int(rect.height()))
            pixmap.fill(QtGui.QColor("white"))
            # Render the scene to the pixmap
            painter = QtGui.QPainter(pixmap)
            self.scene.render(painter, QtCore.QRectF(), rect)
            painter.end()
            # Save the pixmap
            pixmap.save(path, "PNG")
            self.statusBar().showMessage(f"Exported PNG: {os.path.basename(path)}")
        except Exception as ex:
            QMessageBox.critical(self, "Export Error", str(ex))

    def export_pdf(self):
        """Export current view as PDF."""
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", "", "PDF Files (*.pdf);;All Files (*)"
        )
        if not path:
            return

        try:
            # Import reportlab
            from PySide6.QtCore import QRectF
            from PySide6.QtGui import QImage, QPainter
            from reportlab.lib.pagesizes import A4, letter
            from reportlab.lib.units import inch
            from reportlab.pdfgen import canvas

            # Get current view rect
            view_rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()

            # Create PDF
            c = canvas.Canvas(path, pagesize=letter)
            width, height = letter

            # Calculate scale to fit content
            scale_x = width / view_rect.width()
            scale_y = height / view_rect.height()
            scale = min(scale_x, scale_y) * 0.9  # Leave some margin

            # Center content
            offset_x = (width - view_rect.width() * scale) / 2
            offset_y = (height - view_rect.height() * scale) / 2

            # Create a QImage to render the scene
            img_width = int(view_rect.width() * scale)
            img_height = int(view_rect.height() * scale)

            image = QImage(img_width, img_height, QImage.Format.Format_ARGB32)
            image.fill(QtCore.Qt.GlobalColor.white)

            # Render scene to image
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Set up transformation
            painter.translate(-view_rect.left() * scale, -view_rect.top() * scale)
            painter.scale(scale, scale)

            # Render scene
            self.scene.render(
                painter, QRectF(0, 0, view_rect.width(), view_rect.height()), view_rect
            )
            painter.end()

            # Save image temporarily
            import os
            import tempfile

            temp_path = tempfile.mktemp(suffix=".png")
            if not image.save(temp_path):
                raise Exception("Failed to save temporary image")

            # Add image to PDF
            c.drawImage(temp_path, offset_x, offset_y, width=img_width, height=img_height)

            # Add image to PDF
            c.drawImage(temp_path, offset_x, offset_y, width=img_width, height=img_height)

            # Add title/metadata
            c.setFont("Helvetica", 12)
            c.drawString(0.5 * inch, height - 0.5 * inch, "AutoFire Drawing Export")
            c.drawString(
                0.5 * inch,
                height - 0.7 * inch,
                f"Exported: {QtCore.QDateTime.currentDateTime().toString()}",
            )

            c.save()

            # Clean up temp file
            os.unlink(temp_path)

            self.statusBar().showMessage(f"PDF exported to {path}")
            QMessageBox.information(self, "PDF Export", f"PDF exported successfully to {path}")

        except ImportError:
            QMessageBox.critical(
                self,
                "PDF Export Error",
                "ReportLab library not available. Please install reportlab.",
            )
        except Exception as ex:
            QMessageBox.critical(self, "PDF Export Error", str(ex))

    def export_device_schedule_csv(self):
        """Export device schedule as CSV."""
        import csv

        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Device Schedule", "", "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return
        try:
            # Count devices by name/symbol/manufacturer/model
            counts = {}
            for it in self.devices_group.childItems():
                if hasattr(it, "name") and hasattr(it, "symbol"):
                    key = (
                        getattr(it, "name", ""),
                        getattr(it, "symbol", ""),
                        getattr(it, "manufacturer", ""),
                        getattr(it, "part_number", ""),
                    )
                    counts[key] = counts.get(key, 0) + 1

            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Name", "Symbol", "Manufacturer", "Model", "Qty"])
                for (name, sym, mfr, model), qty in sorted(counts.items()):
                    w.writerow([name, sym, mfr, model, qty])

            self.statusBar().showMessage(f"Exported schedule: {os.path.basename(path)}")
        except Exception as ex:
            QMessageBox.critical(self, "Export CSV Error", str(ex))

    # Edit operations
    def undo(self):
        """Undo the last action."""
        if hasattr(self, "history") and hasattr(self, "history_index") and self.history_index > 0:
            self.history_index -= 1
            self.load_state(self.history[self.history_index])
            self.statusBar().showMessage("Undo")

    def redo(self):
        """Redo the last undone action."""
        if (
            hasattr(self, "history")
            and hasattr(self, "history_index")
            and self.history_index < len(self.history) - 1
        ):
            self.history_index += 1
            self.load_state(self.history[self.history_index])
            self.statusBar().showMessage("Redo")

    def delete_selection(self):
        """Delete selected items."""
        items = self.scene.selectedItems()
        if not items:
            return
        try:
            for it in items:
                it.scene().removeItem(it)
            self.push_history()
            self.statusBar().showMessage(f"Deleted {len(items)} items")
        except Exception as ex:
            QMessageBox.critical(self, "Delete Error", str(ex))

    def select_all_items(self):
        """Select all items in the current view."""
        for it in self.scene.items():
            if hasattr(it, "setSelected"):
                it.setSelected(True)
        self.statusBar().showMessage("Selected all items")

    # View operations
    def zoom_in(self):
        """Zoom in."""
        self.view.scale(1.15, 1.15)

    def zoom_out(self):
        """Zoom out."""
        self.view.scale(1 / 1.15, 1 / 1.15)

    def zoom_to_selection(self):
        """Zoom to selected items."""
        # Get bounding rect of selected items
        bounds = QtCore.QRectF()
        for item in self.scene.selectedItems():
            bounds = bounds.united(item.sceneBoundingRect())
        if not bounds.isEmpty():
            # Add some margin
            margin = 50
            bounds.adjust(-margin, -margin, margin, margin)
            self.view.fitInView(bounds, Qt.AspectRatioMode.KeepAspectRatio)
            self.statusBar().showMessage("Zoomed to selection")
        else:
            self.statusBar().showMessage("No selection to zoom to")

    def fit_view_to_content(self):
        """Fit view to show all content."""
        # Get bounding rect of all content
        bounds = QtCore.QRectF()
        for layer in [self.layer_underlay, self.layer_sketch, self.layer_wires, self.devices_group]:
            for it in layer.childItems():
                bounds = bounds.united(it.sceneBoundingRect())
        if not bounds.isEmpty():
            # Add some margin
            margin = 100
            bounds.adjust(-margin, -margin, margin, margin)
            self.view.fitInView(bounds, Qt.AspectRatioMode.KeepAspectRatio)
            self.statusBar().showMessage("Fit view to content")
        else:
            # If no content, show default area
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.statusBar().showMessage("Fit view to default area")

    def toggle_grid(self, on: bool):
        """Toggle grid visibility."""
        self.scene.show_grid = bool(on)
        self.scene.update()

    def toggle_snap(self, on: bool):
        """Toggle snap functionality."""
        self.scene.snap_enabled = bool(on)

    def toggle_crosshair(self, on: bool):
        """Toggle crosshair visibility."""
        self.view.show_crosshair = bool(on)

    def toggle_coverage(self, on: bool):
        """Toggle coverage overlays."""
        self.show_coverage = bool(on)
        for it in self.devices_group.childItems():
            if hasattr(it, "set_coverage_enabled"):
                it.set_coverage_enabled(self.show_coverage)
        self.prefs["show_coverage"] = self.show_coverage
        self.app_controller.save_prefs()

    def toggle_placement_coverage(self, on: bool):
        """Toggle placement coverage."""
        self.prefs["show_placement_coverage"] = bool(on)
        self.app_controller.save_prefs()

    def grid_style_dialog(self):
        """Show grid style dialog."""
        from app.dialogs.gridstyle import GridStyleDialog

        dialog = GridStyleDialog(self, self.scene, self.prefs)
        if dialog.exec():
            dialog.apply()
            self.app_controller.save_prefs()

    # Draw operations
    def cancel_active_tool(self):
        """Cancel the currently active tool."""
        if hasattr(self, "draw") and self.draw:
            self.draw.finish()
        self.statusBar().showMessage("Tool cancelled")

    def start_draw_tool(self, tool_type: str):
        """Start a drawing tool."""
        # Map tool_type strings to DrawMode enum values
        mode_map = {
            "line": DrawMode.LINE,
            "rectangle": DrawMode.RECT,
            "circle": DrawMode.CIRCLE,
            "polyline": DrawMode.POLYLINE,
            "arc": DrawMode.ARC3,
        }

        if tool_type in mode_map:
            self.draw.set_mode(mode_map[tool_type])
        else:
            QMessageBox.warning(self, "Unknown Tool", f"Unknown drawing tool: {tool_type}")

    def start_wiring(self):
        """Start wiring tool."""
        self.wiring_tool.start()

    def start_text(self):
        """Start text tool."""
        QMessageBox.information(self, "Text Tool", "Text tool not yet implemented.")

    def start_mtext(self):
        """Start multi-line text tool."""
        QMessageBox.information(
            self, "Multi-line Text", "Multi-line text tool not yet implemented."
        )

    def start_freehand(self):
        """Start freehand drawing tool."""
        QMessageBox.information(self, "Freehand", "Freehand drawing tool not yet implemented.")

    def start_leader(self):
        """Start leader tool."""
        QMessageBox.information(self, "Leader", "Leader tool not yet implemented.")

    def start_cloud(self):
        """Start revision cloud tool."""
        QMessageBox.information(self, "Revision Cloud", "Revision cloud tool not yet implemented.")

    def place_facp_panel(self):
        """Place FACP panel using wizard."""
        self._place_facp_panel()

    def open_wire_spool(self):
        """Open wire spool dialog."""
        self._open_wire_spool()

    def open_system_builder(self):
        """Open system builder dialog."""
        self._open_system_builder()

    def open_device_manager(self):
        """Open device manager dialog."""
        from app.dialogs.device_manager import DeviceManagerDialog

        dlg = DeviceManagerDialog(self, self)
        dlg.exec()

    def open_layer_manager(self):
        """Open layer manager dialog."""
        from app.dialogs.layer_manager import LayerManagerDialog

        dlg = LayerManagerDialog(self, self)
        dlg.exec()

    def open_settings(self):
        """Open settings dialog."""
        QMessageBox.information(self, "Settings", "Settings dialog not yet implemented.")

    def place_token(self):
        """Place token on selected device."""
        QMessageBox.information(self, "Place Token", "Token placement not yet implemented.")

    # Reports operations
    def show_calculations(self):
        """Show calculations dialog."""
        QMessageBox.information(self, "Calculations", "Calculations dialog not yet implemented.")

    def show_bom_report(self):
        """Show bill of materials report."""
        QMessageBox.information(self, "Bill of Materials", "BOM report not yet implemented.")

    def show_device_schedule_report(self):
        """Show device schedule report."""
        QMessageBox.information(
            self, "Device Schedule", "Device schedule report not yet implemented."
        )

    def generate_riser_diagram(self):
        """Generate riser diagram."""
        QMessageBox.information(self, "Riser Diagram", "Riser diagram not yet implemented.")

    def show_circuit_properties(self):
        """Show circuit properties dialog."""
        QMessageBox.information(
            self, "Circuit Properties", "Circuit properties dialog not yet implemented."
        )

    def show_job_info_dialog(self):
        """Show job information dialog."""
        QMessageBox.information(
            self, "Job Information", "Job information dialog not yet implemented."
        )

    def place_symbol_legend(self):
        """Place symbol legend on drawing."""
        QMessageBox.information(
            self, "Symbol Legend", "Symbol legend placement not yet implemented."
        )

    # Layout operations
    def add_page_frame(self):
        """Add page frame to layout."""
        QMessageBox.information(self, "Page Frame", "Page frame addition not yet implemented.")

    def remove_page_frame(self):
        """Remove page frame from layout."""
        QMessageBox.information(self, "Page Frame", "Page frame removal not yet implemented.")

    def add_or_update_title_block(self):
        """Add or update title block."""
        QMessageBox.information(self, "Title Block", "Title block not yet implemented.")

    def page_setup_dialog(self):
        """Show page setup dialog."""
        QMessageBox.information(self, "Page Setup", "Page setup dialog not yet implemented.")

    def add_viewport(self):
        """Add viewport to paperspace."""
        QMessageBox.information(self, "Add Viewport", "Viewport addition not yet implemented.")

    # Helper methods
    def push_history(self):
        """Push current state to history."""
        # This would need to be implemented with proper history management
        pass

    def load_state(self, data):
        """Load scene state from serialized data."""
        # This would need to be implemented with proper state loading
        # For now, just show a message
        QMessageBox.information(self, "Load State", "State loading not yet implemented.")

    def _place_facp_panel(self):
        """Place a FACP panel using the wizard dialog."""
        from app.system_builder import SystemBuilderDialog

        dialog = SystemBuilderDialog(self)
        dialog.exec()

    def _open_wire_spool(self):
        """Open the wire spool dialog to select a wire type."""
        from app.wire_spool import WireSpoolDialog

        dialog = WireSpoolDialog(self)
        dialog.exec()

    def _open_system_builder(self):
        """Open the system builder dialog."""
        from app.system_builder import SystemBuilderDialog

        dialog = SystemBuilderDialog(self)
        dialog.exec()

    def _get_selected_device(self):
        for it in self.scene.selectedItems():
            if isinstance(it, DeviceItem):
                return it
        return None

    def _apply_label_offset_live(self):
        d = self._get_selected_device()
        if not d:
            return
        # Note: This method expects prop_label, prop_offx, prop_offy to be accessed from app_controller
        # Since the controls are in AppController, we need to delegate back
        if (
            hasattr(self.app_controller, "prop_label")
            and hasattr(self.app_controller, "prop_offx")
            and hasattr(self.app_controller, "prop_offy")
        ):
            d.set_label_text(self.app_controller.prop_label.text())
            dx_ft = float(self.app_controller.prop_offx.value())
            dy_ft = float(self.app_controller.prop_offy.value())
            d.set_label_offset(dx_ft * self.px_per_ft, dy_ft * self.px_per_ft)
            self.scene.update()

    def _apply_props_clicked(self):
        d = self._get_selected_device()
        if not d:
            return
        # Access controls from app_controller
        if not hasattr(self.app_controller, "prop_showcov"):
            return

        d.set_coverage_enabled(bool(self.app_controller.prop_showcov.isChecked()))
        mode = self.app_controller.prop_mode.currentText()
        mount = self.app_controller.prop_mount.currentText()
        sz = float(self.app_controller.prop_size.value())
        cov = {"mode": mode, "mount": mount, "px_per_ft": self.px_per_ft}
        if mode == "none":
            cov["computed_radius_ft"] = 0.0
        elif mode == "strobe":
            cand_txt = self.app_controller.prop_candela.currentText()
            if cand_txt != "(custom)":
                try:
                    cand = int(cand_txt)
                    cov.setdefault("params", {})["candela"] = cand
                    cov["computed_radius_ft"] = self._strobe_radius_from_candela(cand)
                except Exception:
                    cov["computed_radius_ft"] = max(0.0, sz / 2.0)
            else:
                cov["computed_radius_ft"] = max(0.0, sz / 2.0)
        elif mode == "smoke":
            spacing_ft = max(0.0, sz)
            cov["params"] = {"spacing_ft": spacing_ft}
            cov["computed_radius_ft"] = spacing_ft / 2.0
        elif mode == "speaker":
            cov["computed_radius_ft"] = max(0.0, sz)
        d.set_coverage(cov)
        self.push_history()
        self.scene.update()

    def _strobe_radius_from_candela(self, cand: int) -> float:
        # Try DB first
        try:
            from db import loader as db_loader

            con = db_loader.connect()
            db_loader.ensure_schema(con)
            r = db_loader.strobe_radius_for_candela(con, int(cand))
            con.close()
            if r is not None:
                return float(r)
        except Exception:
            pass
        # Fallback mapping
        table = {15: 15.0, 30: 20.0, 75: 30.0, 95: 35.0, 110: 38.0, 135: 43.0, 185: 50.0}
        return float(table.get(int(cand), 25.0))

    def _on_mode_changed_props(self, mode: str):
        # Show candela chooser only for strobe
        want = mode == "strobe"
        if hasattr(self.app_controller, "prop_candela"):
            self.app_controller.prop_candela.setEnabled(want)

    def _enable_props(self, on: bool):
        if not hasattr(self.app_controller, "prop_label"):
            return
        for w in (
            self.app_controller.prop_label,
            self.app_controller.prop_offx,
            self.app_controller.prop_offy,
            self.app_controller.prop_mount,
            self.app_controller.prop_mode,
            self.app_controller.prop_size,
            self.app_controller.btn_apply_props,
        ):
            w.setEnabled(on)

    def _on_selection_changed(self):
        # Update device properties panel if a device is selected
        d = self._get_selected_device()
        if not d:
            self._enable_props(False)
        else:
            self._enable_props(True)
            # label + offset in ft
            if hasattr(self.app_controller, "prop_label"):
                self.app_controller.prop_label.setText(d._label.text())
                self.app_controller.prop_showcov.setChecked(
                    bool(getattr(d, "coverage_enabled", True))
                )
                offx = d.label_offset.x() / self.px_per_ft
                offy = d.label_offset.y() / self.px_per_ft
                self.app_controller.prop_offx.blockSignals(True)
                self.app_controller.prop_offy.blockSignals(True)
                self.app_controller.prop_offx.setValue(offx)
                self.app_controller.prop_offy.setValue(offy)
                self.app_controller.prop_offx.blockSignals(False)
                self.app_controller.prop_offy.blockSignals(False)
                # coverage
                cov = d.coverage or {}
                self.app_controller.prop_mount.setCurrentText(cov.get("mount", "ceiling"))
                mode = cov.get("mode", "none")
                if mode not in ("none", "strobe", "speaker", "smoke"):
                    mode = "none"
                self.app_controller.prop_mode.setCurrentText(mode)
                # strobe candela
                cand = str(cov.get("params", {}).get("candela", ""))
                if cand in {"15", "30", "75", "95", "110", "135", "185"}:
                    self.app_controller.prop_candela.setCurrentText(cand)
                else:
                    self.app_controller.prop_candela.setCurrentText("(custom)")
                size_ft = (
                    float(cov.get("computed_radius_ft", 0.0)) * 2.0
                    if mode == "strobe"
                    else (
                        float(cov.get("params", {}).get("spacing_ft", 0.0))
                        if mode == "smoke"
                        else float(cov.get("computed_radius_ft", 0.0))
                    )
                )
                self.app_controller.prop_size.setValue(max(0.0, size_ft))
        # Always update selection highlight for geometry
        self._update_selection_visuals()

    def _update_selection_visuals(self):
        hi_pen = QtGui.QPen(QtGui.QColor(66, 160, 255))
        hi_pen.setCosmetic(True)
        hi_pen.setWidthF(2.0)

        def apply(item, on: bool):
            try:
                if hasattr(item, "setPen"):
                    if on:
                        if item.data(1001) is None:
                            # store original pen
                            try:
                                item.setData(1001, item.pen())
                            except Exception:
                                item.setData(1001, None)
                        item.setPen(hi_pen)
                    else:
                        op = item.data(1001)
                        if op is not None:
                            try:
                                item.setPen(op)
                            except Exception:
                                pass
                            item.setData(1001, None)
            except Exception:
                pass

        # clear highlights on non-selected geometry
        for layer in (self.layer_sketch, self.layer_wires):
            for it in layer.childItems():
                apply(it, it.isSelected())

    def canvas_menu(self, global_pos):
        menu = QtWidgets.QMenu(self)
        # Determine item under cursor
        view_pt = self.view.mapFromGlobal(global_pos)
        try:
            scene_pt = self.view.mapToScene(view_pt)
        except Exception:
            scene_pt = None
        item_under = None
        if scene_pt is not None:
            try:
                item_under = self.scene.itemAt(scene_pt, self.view.transform())
            except Exception:
                item_under = None

        # Selection actions
        act_sel = None
        act_sim = None
        if item_under is not None and (
            not isinstance(item_under, QtWidgets.QGraphicsItemGroup)
            or isinstance(item_under, DeviceItem)
        ):
            act_sel = menu.addAction("Select")
            act_sim = menu.addAction("Select Similar")
        act_all = menu.addAction("Select All")
        act_none = menu.addAction("Clear Selection")
        if self.scene.selectedItems():
            menu.addAction("Delete Selection", self.delete_selection)

        # Device-specific when a device is selected
        dev_sel = [it for it in self.scene.selectedItems() if isinstance(it, DeviceItem)]
        if dev_sel:
            menu.addSeparator()
            d = dev_sel[0]
            act_cov = menu.addAction("Coverage…")
            act_tog = menu.addAction("Toggle Coverage On/Off")
            act_lbl = menu.addAction("Edit Label…")
            # Connect these actions later in the function
        else:
            # Some startup paths may not have enhanced menu methods attached
            # (eg. `enhanced_menus.add_main_window_methods` wasn't called). Use
            # a safe fallback to avoid AttributeError in the context menu.
            if hasattr(self, "select_all_items"):
                menu.addAction("Select All", self.select_all_items)
            else:
                # Fallback: select all QGraphicsItems in the scene
                menu.addAction(
                    "Select All",
                    lambda: [
                        it.setSelected(True)
                        for it in self.scene.items()
                        if isinstance(it, QtWidgets.QGraphicsItem)
                    ],
                )

        # Some runtime builds may not have enhanced menu methods attached;
        # provide safe fallbacks to avoid AttributeError in the context menu.
        if hasattr(self, "clear_selection"):
            menu.addAction("Clear Selection", self.clear_selection)
        else:
            menu.addAction("Clear Selection", lambda: self.scene.clearSelection())
        menu.addSeparator()
        act_clear_underlay = menu.addAction("Clear Underlay")

        act = menu.exec(global_pos)
        if act is None:
            return
        if act == act_sel and item_under is not None:
            try:
                item_under.setSelected(True)
            except Exception:
                pass
            return
        if act == act_sim and item_under is not None:
            self._select_similar_from(item_under)
            return
        if act == act_all:
            self.scene.clearSelection()
            for it in self.scene.items():
                try:
                    if not isinstance(it, QtWidgets.QGraphicsItemGroup):
                        it.setSelected(True)
                except Exception:
                    pass
            return
        if act == act_none:
            self.scene.clearSelection()
            return
        if dev_sel and act in (act_cov, act_tog, act_lbl):
            d = dev_sel[0]
            if act == act_cov:
                from app.main import CoverageDialog

                dlg = CoverageDialog(self, existing=d.coverage)
                if dlg.exec() == QtWidgets.QDialog.Accepted:
                    d.set_coverage(dlg.get_settings(self.px_per_ft))
                    self.push_history()
            elif act == act_tog:
                if d.coverage.get("mode", "none") == "none":
                    diam_ft = float(self.prefs.get("default_strobe_diameter_ft", 50.0))
                    d.set_coverage(
                        {
                            "mode": "strobe",
                            "mount": "ceiling",
                            "computed_radius_ft": max(0.0, diam_ft / 2.0),
                            "px_per_ft": self.px_per_ft,
                        }
                    )
                else:
                    d.set_coverage(
                        {"mode": "none", "computed_radius_ft": 0.0, "px_per_ft": self.px_per_ft}
                    )
                self.push_history()
            elif act == act_lbl:
                txt, ok = QtWidgets.QInputDialog.getText(self, "Device Label", "Text:", text=d.name)
                if ok:
                    d.set_label_text(txt)
            return
        if act == act_clear_underlay:
            self.clear_underlay()
            return

    def clear_selection(self):
        """Clear the current selection."""
        self.scene.clearSelection()

    def clear_underlay(self):
        """Clear the underlay layer."""
        for item in self.layer_underlay.childItems():
            if item.scene():
                self.scene.removeItem(item)

    def _select_similar_from(self, base_item):
        """Select similar items based on the base item (stub for now)."""
        pass

    def open_device_manager(self):
        """Open the device manager dialog."""
        from app.dialogs.device_manager import DeviceManagerDialog

        dlg = DeviceManagerDialog(self, self)
        dlg.exec()

    def open_parts_warehouse(self):
        """Open the parts warehouse dialog."""
        dlg = PartsWarehouseDialog(self)
        dlg.exec()

    def open_layer_manager(self):
        """Open the layer manager dialog."""
        from app.dialogs.layer_manager import LayerManagerDialog

        dlg = LayerManagerDialog(self, self)
        dlg.exec()

    def _new_system_config(self):
        """Create a new system configuration."""
        try:
            from app.system_builder import SystemConfiguration

            self.current_system = SystemConfiguration()
            self.system_info_label.setText(f"System: {self.current_system.name}")
            self._update_device_palette_for_system()
            self.statusBar().showMessage("New system created")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "System Error", f"Failed to create new system: {e}")

    def _load_system_config(self):
        """Load a system configuration from file."""
        try:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Load System Configuration", "", "JSON Files (*.json)"
            )
            if not filename:
                return

            with open(filename, 'r') as f:
                data = json.load(f)

            from app.system_builder import SystemConfiguration
            self.current_system = SystemConfiguration.from_dict(data)
            self.system_info_label.setText(f"System: {self.current_system.name}")
            self._update_device_palette_for_system()
            self.statusBar().showMessage(f"System '{self.current_system.name}' loaded")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Load Error", f"Failed to load system: {e}")

    def _save_system_config(self):
        """Save the current system configuration to file."""
        try:
            if not hasattr(self, 'current_system') or not self.current_system:
                QtWidgets.QMessageBox.warning(self, "Save Error", "No system to save")
                return

            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save System Configuration", "", "JSON Files (*.json)"
            )
            if not filename:
                return

            if not filename.lower().endswith('.json'):
                filename += '.json'

            with open(filename, 'w') as f:
                json.dump(self.current_system.to_dict(), f, indent=2)

            self.statusBar().showMessage(f"System '{self.current_system.name}' saved")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Save Error", f"Failed to save system: {e}")

    def _update_device_palette_for_system(self):
        """Update the device palette to show only devices relevant to the current system."""
        try:
            if not hasattr(self, 'current_system') or not self.current_system:
                # No system loaded, show all devices
                self._populate_device_tree()
                return

            # Clear existing tree
            self.device_tree.clear()

            # Get system device requirements
            system_devices = set()
            for device_type, devices in self.current_system.devices.items():
                for device in devices:
                    system_devices.add((device_type, device.get('manufacturer', ''), device.get('part_number', '')))

            # Create filtered device tree
            device_types = self._get_device_types()
            for cat in sorted(device_types):
                # Only show categories that have devices in the system
                if cat.lower() in [dt.lower() for dt, _, _ in system_devices]:
                    cat_item = QtWidgets.QTreeWidgetItem([f"{cat} (System)"])
                    cat_item.setData(0, QtCore.Qt.UserRole, {"type": "category", "name": cat, "loaded": False})

                    # Load devices for this category that are in the system
                    devices = self._load_devices_for_category(cat)
                    system_devices_in_cat = [
                        dev for dev in devices
                        if any(dev.get('manufacturer', '') == mfg and dev.get('part_number', '') == part
                               for _, mfg, part in system_devices if _ == cat)
                    ]

                    for dev in sorted(system_devices_in_cat, key=lambda x: x.get("name", "")):
                        txt = f"{dev.get('name','<unknown>')} ({dev.get('symbol','')})"
                        if dev.get("part_number"):
                            txt += f" - {dev.get('part_number')}"
                        it = QtWidgets.QTreeWidgetItem([txt])
                        it.setData(0, QtCore.Qt.UserRole, dev)
                        cat_item.addChild(it)

                    if system_devices_in_cat:
                        self.device_tree.addTopLevelItem(cat_item)

            self._update_device_count()
        except Exception as e:
            _logger.error(f"Failed to update device palette for system: {e}")

    def closeEvent(self, event):
        """Handle window close event."""
        # Notify controller about window closing
        if hasattr(self.app_controller, "on_model_space_closed"):
            self.app_controller.on_model_space_closed()
        event.accept()
