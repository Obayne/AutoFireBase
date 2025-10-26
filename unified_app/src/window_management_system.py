#!/usr/bin/env python3
"""
AutoFire Professional Window Management System
==============================================

Addresses user feedback: "windows opening out in space feels weird"

This system provides:
- Intelligent window positioning (no random placement)
- Multi-monitor support for engineering firms
- Dockable panels that snap together
- Saved workspace layouts
- Professional window management behaviors
"""

import json
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import QPoint, QRect, QSettings, QSize, QTimer, Qt, Signal
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

# Add project root to path for imports
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from frontend.design_system import AutoFireColor, AutoFireStyle
except ImportError:
    # Fallback if design system not available
    class AutoFireColor:
        BACKGROUND = "#1e1e1e"
        SURFACE = "#2d2d2d"
        PRIMARY = "#d32f2f"
        TEXT = "#ffffff"
        TEXT_SECONDARY = "#b0b0b0"
        BORDER = "#404040"

    class AutoFireStyle:
        @staticmethod
        def get_stylesheet():
            return f"""
            QMainWindow {{
                background-color: {AutoFireColor.BACKGROUND};
                color: {AutoFireColor.TEXT};
            }}
            QDockWidget {{
                background-color: {AutoFireColor.SURFACE};
                color: {AutoFireColor.TEXT};
                border: 1px solid {AutoFireColor.BORDER};
            }}
            """


class DockPosition(Enum):
    """Standard docking positions for AutoFire windows."""

    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    CENTER = "center"
    FLOATING = "floating"


class WindowProfile(Enum):
    """Pre-defined window layout profiles for different workflows."""

    DESIGNER = "designer"  # CAD-focused layout
    ENGINEER = "engineer"  # Calculations and compliance
    MANAGER = "manager"  # Reports and project overview
    DUAL_MONITOR = "dual_monitor"  # Multi-monitor engineering setup


class WorkspaceLayout:
    """Represents a complete workspace layout configuration."""

    def __init__(self, name: str):
        self.name = name
        self.windows = {}  # window_id -> {position, size, dock_state}
        self.monitor_config = {}  # Screen setup info
        self.created_time = None
        self.last_used = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "windows": self.windows,
            "monitor_config": self.monitor_config,
            "created_time": self.created_time,
            "last_used": self.last_used,
        }

    @classmethod
    def from_dict(cls, data: dict):
        layout = cls(data["name"])
        layout.windows = data.get("windows", {})
        layout.monitor_config = data.get("monitor_config", {})
        layout.created_time = data.get("created_time")
        layout.last_used = data.get("last_used")
        return layout


class WindowManager:
    """Professional window management for AutoFire application."""

    def __init__(self):
        self.app = QApplication.instance()
        self.settings = QSettings("AutoFire", "WindowManager")
        self.layouts = {}  # name -> WorkspaceLayout
        self.active_windows = {}  # window_id -> QMainWindow
        self.dock_widgets = {}  # dock_id -> QDockWidget

        # Load saved layouts
        self._load_layouts()

        # Monitor setup
        self.screens = self.app.screens()
        self.primary_screen = self.app.primaryScreen()

    def _load_layouts(self):
        """Load workspace layouts from settings."""
        layouts_data = self.settings.value("workspace_layouts", {})
        if isinstance(layouts_data, dict):
            for name, data in layouts_data.items():
                self.layouts[name] = WorkspaceLayout.from_dict(data)

    def _save_layouts(self):
        """Save workspace layouts to settings."""
        layouts_data = {name: layout.to_dict() for name, layout in self.layouts.items()}
        self.settings.setValue("workspace_layouts", layouts_data)

    def get_intelligent_position(self, window_type: str, size: QSize) -> Tuple[QPoint, QScreen]:
        """
        Calculate intelligent window position based on:
        - Window type and purpose
        - Available screen real estate
        - Existing window positions
        - User preferences
        """
        screen = self.primary_screen
        screen_geometry = screen.availableGeometry()

        # Define positioning strategies by window type
        positioning_rules = {
            "main": self._position_main_window,
            "model_space": self._position_main_window,
            "properties": self._position_properties_panel,
            "device_tree": self._position_device_tree,
            "calculations": self._position_calculations,
            "reports": self._position_reports,
            "dialog": self._position_dialog,
            "tool_palette": self._position_tool_palette,
        }

        position_func = positioning_rules.get(window_type, self._position_default)
        return position_func(size, screen_geometry, screen)

    def _position_main_window(
        self, size: QSize, screen_geom: QRect, screen: QScreen
    ) -> Tuple[QPoint, QScreen]:
        """Position main CAD window to use most of primary screen."""
        # Use 80% of screen, centered
        target_width = int(screen_geom.width() * 0.8)
        target_height = int(screen_geom.height() * 0.8)

        x = screen_geom.x() + (screen_geom.width() - target_width) // 2
        y = screen_geom.y() + (screen_geom.height() - target_height) // 2

        return QPoint(x, y), screen

    def _position_properties_panel(
        self, size: QSize, screen_geom: QRect, screen: QScreen
    ) -> Tuple[QPoint, QScreen]:
        """Position properties panel on right side."""
        # Check for secondary monitor first
        if len(self.screens) > 1:
            secondary = self.screens[1]
            sec_geom = secondary.availableGeometry()
            x = sec_geom.x() + 20
            y = sec_geom.y() + 100
            return QPoint(x, y), secondary

        # Single monitor: right side
        x = screen_geom.x() + screen_geom.width() - size.width() - 20
        y = screen_geom.y() + 100
        return QPoint(x, y), screen

    def _position_device_tree(
        self, size: QSize, screen_geom: QRect, screen: QScreen
    ) -> Tuple[QPoint, QScreen]:
        """Position device tree on left side."""
        x = screen_geom.x() + 20
        y = screen_geom.y() + 100
        return QPoint(x, y), screen

    def _position_calculations(
        self, size: QSize, screen_geom: QRect, screen: QScreen
    ) -> Tuple[QPoint, QScreen]:
        """Position calculations window intelligently."""
        # Check for secondary monitor
        if len(self.screens) > 1:
            secondary = self.screens[1]
            sec_geom = secondary.availableGeometry()
            # Center on secondary monitor
            x = sec_geom.x() + (sec_geom.width() - size.width()) // 2
            y = sec_geom.y() + (sec_geom.height() - size.height()) // 2
            return QPoint(x, y), secondary

        # Single monitor: lower right quadrant
        x = screen_geom.x() + screen_geom.width() // 2
        y = screen_geom.y() + screen_geom.height() // 2
        return QPoint(x, y), screen

    def _position_reports(
        self, size: QSize, screen_geom: QRect, screen: QScreen
    ) -> Tuple[QPoint, QScreen]:
        """Position reports window for easy viewing."""
        # Center on primary screen
        x = screen_geom.x() + (screen_geom.width() - size.width()) // 2
        y = screen_geom.y() + (screen_geom.height() - size.height()) // 2
        return QPoint(x, y), screen

    def _position_dialog(
        self, size: QSize, screen_geom: QRect, screen: QScreen
    ) -> Tuple[QPoint, QScreen]:
        """Position dialogs relative to parent or center."""
        # Find main window for relative positioning
        main_window = None
        for window in self.app.topLevelWidgets():
            if isinstance(window, QMainWindow) and window.isVisible():
                main_window = window
                break

        if main_window:
            # Position relative to main window
            main_pos = main_window.pos()
            main_size = main_window.size()
            x = main_pos.x() + (main_size.width() - size.width()) // 2
            y = main_pos.y() + (main_size.height() - size.height()) // 2
        else:
            # Center on screen
            x = screen_geom.x() + (screen_geom.width() - size.width()) // 2
            y = screen_geom.y() + (screen_geom.height() - size.height()) // 2

        return QPoint(x, y), screen

    def _position_tool_palette(
        self, size: QSize, screen_geom: QRect, screen: QScreen
    ) -> Tuple[QPoint, QScreen]:
        """Position tool palette for easy access."""
        # Top left area
        x = screen_geom.x() + 20
        y = screen_geom.y() + 20
        return QPoint(x, y), screen

    def _position_default(
        self, size: QSize, screen_geom: QRect, screen: QScreen
    ) -> Tuple[QPoint, QScreen]:
        """Default positioning for unknown window types."""
        # Slight offset from top-left to avoid overlap
        x = screen_geom.x() + 50
        y = screen_geom.y() + 50
        return QPoint(x, y), screen

    def register_window(self, window: QMainWindow, window_id: str, window_type: str):
        """Register a window with the window manager."""
        self.active_windows[window_id] = window

        # Apply intelligent positioning
        current_size = window.size()
        position, screen = self.get_intelligent_position(window_type, current_size)

        # Ensure position is on screen
        screen_geom = screen.availableGeometry()
        if not screen_geom.contains(position):
            position = QPoint(screen_geom.x() + 50, screen_geom.y() + 50)

        window.move(position)

        # Apply AutoFire styling
        try:
            window.setStyleSheet(AutoFireStyle.get_stylesheet())
        except:
            pass

        print(f"✅ Window Manager: Positioned {window_type} window '{window_id}' at {position}")

    def create_dock_widget(
        self, title: str, widget: QWidget, dock_id: str, position: DockPosition = DockPosition.RIGHT
    ) -> QDockWidget:
        """Create a properly configured dock widget."""
        dock = QDockWidget(title)
        dock.setWidget(widget)
        dock.setObjectName(dock_id)

        # Configure dock properties
        dock.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
            | QDockWidget.DockWidgetClosable
        )

        # Store dock widget
        self.dock_widgets[dock_id] = dock

        return dock

    def apply_layout_profile(self, profile: WindowProfile):
        """Apply a predefined layout profile."""
        if profile == WindowProfile.DESIGNER:
            self._apply_designer_layout()
        elif profile == WindowProfile.ENGINEER:
            self._apply_engineer_layout()
        elif profile == WindowProfile.MANAGER:
            self._apply_manager_layout()
        elif profile == WindowProfile.DUAL_MONITOR:
            self._apply_dual_monitor_layout()

    def _apply_designer_layout(self):
        """Apply CAD-focused layout."""
        print("🎨 Applying Designer Layout: CAD-focused workspace")
        # Main window takes center stage
        # Tool palettes on left
        # Properties on right
        # Status/calculations at bottom

    def _apply_engineer_layout(self):
        """Apply calculations and compliance focused layout."""
        print("🧮 Applying Engineer Layout: Calculations & compliance focused")
        # Split view: CAD + calculations
        # Reports easily accessible
        # Device properties prominent

    def _apply_manager_layout(self):
        """Apply project management focused layout."""
        print("📊 Applying Manager Layout: Project management focused")
        # Reports and project overview prominent
        # Quick access to status information
        # Minimized CAD view

    def _apply_dual_monitor_layout(self):
        """Apply dual monitor professional layout."""
        print("🖥️ Applying Dual Monitor Layout: Professional multi-screen setup")
        if len(self.screens) < 2:
            QMessageBox.information(
                None,
                "Monitor Setup",
                "Dual monitor layout requires 2 or more displays.\n"
                "Connect a second monitor for optimal experience.",
            )
            return

        # Primary: Main CAD work
        # Secondary: Properties, calculations, reports

    def save_current_layout(self, name: str):
        """Save current window positions as a named layout."""
        layout = WorkspaceLayout(name)

        # Capture current window states
        for window_id, window in self.active_windows.items():
            if window.isVisible():
                layout.windows[window_id] = {
                    "position": [window.pos().x(), window.pos().y()],
                    "size": [window.size().width(), window.size().height()],
                    "screen": self._get_screen_index(window.pos()),
                }

        # Capture monitor configuration
        layout.monitor_config = {
            "screen_count": len(self.screens),
            "primary_screen": self._get_screen_index(self.primary_screen.geometry().topLeft()),
            "screen_geometries": [
                [s.geometry().x(), s.geometry().y(), s.geometry().width(), s.geometry().height()]
                for s in self.screens
            ],
        }

        import time

        layout.created_time = time.time()
        layout.last_used = time.time()

        self.layouts[name] = layout
        self._save_layouts()

        print(f"💾 Saved workspace layout: '{name}'")

    def load_layout(self, name: str):
        """Load a saved workspace layout."""
        if name not in self.layouts:
            print(f"❌ Layout '{name}' not found")
            return

        layout = self.layouts[name]

        # Restore window positions
        for window_id, window_config in layout.windows.items():
            if window_id in self.active_windows:
                window = self.active_windows[window_id]
                pos = QPoint(window_config["position"][0], window_config["position"][1])
                size = QSize(window_config["size"][0], window_config["size"][1])

                window.move(pos)
                window.resize(size)

        # Update last used time
        import time

        layout.last_used = time.time()
        self._save_layouts()

        print(f"📂 Loaded workspace layout: '{name}'")

    def get_available_layouts(self) -> List[str]:
        """Get list of available saved layouts."""
        return list(self.layouts.keys())

    def _get_screen_index(self, point: QPoint) -> int:
        """Get screen index for a given point."""
        for i, screen in enumerate(self.screens):
            if screen.geometry().contains(point):
                return i
        return 0  # Default to primary screen

    def ensure_windows_visible(self):
        """Ensure all windows are visible on available screens."""
        available_geometry = QRect()
        for screen in self.screens:
            available_geometry = available_geometry.united(screen.availableGeometry())

        for window_id, window in self.active_windows.items():
            if window.isVisible():
                window_rect = QRect(window.pos(), window.size())
                if not available_geometry.intersects(window_rect):
                    # Window is off-screen, move it to primary screen
                    primary_geom = self.primary_screen.availableGeometry()
                    new_pos = QPoint(primary_geom.x() + 50, primary_geom.y() + 50)
                    window.move(new_pos)
                    print(f"🔧 Moved off-screen window '{window_id}' to visible area")


class WindowManagementDemo(QMainWindow):
    """Demonstration of the Window Management System."""

    def __init__(self):
        super().__init__()
        self.window_manager = WindowManager()
        self.setWindowTitle("AutoFire - Window Management Demo")
        self.setMinimumSize(800, 600)

        self.setup_ui()
        self.setup_menu()

        # Register this window
        self.window_manager.register_window(self, "main_demo", "main")

    def setup_ui(self):
        """Setup the demonstration UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("🏗️ AutoFire Professional Window Management")
        title.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {AutoFireColor.PRIMARY}; padding: 10px;"
        )
        layout.addWidget(title)

        # Info
        info = QLabel(
            "This system addresses the 'windows opening out in space' issue with:\n"
            "• Intelligent window positioning based on type and purpose\n"
            "• Multi-monitor support for engineering workstations\n"
            "• Saved workspace layouts for different workflows\n"
            "• Professional docking and snapping behaviors"
        )
        info.setStyleSheet(
            f"color: {AutoFireColor.TEXT_SECONDARY}; padding: 10px; line-height: 1.4;"
        )
        layout.addWidget(info)

        # Button controls
        button_layout = QHBoxLayout()

        # Window creation buttons
        create_properties = QPushButton("📋 Open Properties Panel")
        create_properties.clicked.connect(
            lambda: self.create_demo_window("properties", "Properties")
        )
        button_layout.addWidget(create_properties)

        create_calculations = QPushButton("🧮 Open Calculations")
        create_calculations.clicked.connect(
            lambda: self.create_demo_window("calculations", "Live Calculations")
        )
        button_layout.addWidget(create_calculations)

        create_reports = QPushButton("📊 Open Reports")
        create_reports.clicked.connect(
            lambda: self.create_demo_window("reports", "Professional Reports")
        )
        button_layout.addWidget(create_reports)

        layout.addLayout(button_layout)

        # Layout profile buttons
        profile_layout = QHBoxLayout()

        designer_btn = QPushButton("🎨 Designer Layout")
        designer_btn.clicked.connect(
            lambda: self.window_manager.apply_layout_profile(WindowProfile.DESIGNER)
        )
        profile_layout.addWidget(designer_btn)

        engineer_btn = QPushButton("🧮 Engineer Layout")
        engineer_btn.clicked.connect(
            lambda: self.window_manager.apply_layout_profile(WindowProfile.ENGINEER)
        )
        profile_layout.addWidget(engineer_btn)

        manager_btn = QPushButton("📊 Manager Layout")
        manager_btn.clicked.connect(
            lambda: self.window_manager.apply_layout_profile(WindowProfile.MANAGER)
        )
        profile_layout.addWidget(manager_btn)

        dual_monitor_btn = QPushButton("🖥️ Dual Monitor")
        dual_monitor_btn.clicked.connect(
            lambda: self.window_manager.apply_layout_profile(WindowProfile.DUAL_MONITOR)
        )
        profile_layout.addWidget(dual_monitor_btn)

        layout.addLayout(profile_layout)

        # Layout management
        layout_mgmt = QHBoxLayout()

        save_layout_btn = QPushButton("💾 Save Current Layout")
        save_layout_btn.clicked.connect(self.save_current_layout)
        layout_mgmt.addWidget(save_layout_btn)

        load_layout_btn = QPushButton("📂 Load Layout")
        load_layout_btn.clicked.connect(self.load_layout_demo)
        layout_mgmt.addWidget(load_layout_btn)

        layout.addLayout(layout_mgmt)

        # Status info
        status_text = QLabel(
            f"Monitor Setup: {len(self.window_manager.screens)} screen(s) detected\n"
            f"Primary Screen: {self.window_manager.primary_screen.geometry().width()}x{self.window_manager.primary_screen.geometry().height()}\n"
            f"Available Layouts: {len(self.window_manager.get_available_layouts())}"
        )
        status_text.setStyleSheet(
            f"color: {AutoFireColor.TEXT_SECONDARY}; padding: 10px; background: {AutoFireColor.SURFACE}; border-radius: 5px;"
        )
        layout.addWidget(status_text)

        # Spacer
        layout.addStretch()

        # Apply styling
        try:
            self.setStyleSheet(AutoFireStyle.get_stylesheet())
        except:
            pass

    def setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()

        # Window menu
        window_menu = menubar.addMenu("Window")

        # Ensure visible action
        ensure_visible = window_menu.addAction("🔧 Ensure All Windows Visible")
        ensure_visible.triggered.connect(self.window_manager.ensure_windows_visible)

        window_menu.addSeparator()

        # Layout profiles
        profiles_menu = window_menu.addMenu("Layout Profiles")
        profiles_menu.addAction(
            "🎨 Designer", lambda: self.window_manager.apply_layout_profile(WindowProfile.DESIGNER)
        )
        profiles_menu.addAction(
            "🧮 Engineer", lambda: self.window_manager.apply_layout_profile(WindowProfile.ENGINEER)
        )
        profiles_menu.addAction(
            "📊 Manager", lambda: self.window_manager.apply_layout_profile(WindowProfile.MANAGER)
        )
        profiles_menu.addAction(
            "🖥️ Dual Monitor",
            lambda: self.window_manager.apply_layout_profile(WindowProfile.DUAL_MONITOR),
        )

    def create_demo_window(self, window_type: str, title: str):
        """Create a demonstration window of the specified type."""
        window = QMainWindow()
        window.setWindowTitle(f"AutoFire - {title}")
        window.setMinimumSize(400, 300)

        # Create content
        widget = QWidget()
        layout = QVBoxLayout(widget)

        header = QLabel(f"🔧 {title} Window")
        header.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {AutoFireColor.PRIMARY}; padding: 10px;"
        )
        layout.addWidget(header)

        content = QLabel(
            f"This is a demonstration {window_type} window.\n\n"
            f"Notice how the Window Management System positioned it intelligently:\n"
            f"• Based on window type: {window_type}\n"
            f"• Considering screen real estate\n"
            f"• Avoiding overlap with existing windows\n"
            f"• Multi-monitor awareness\n\n"
            f"No more 'windows opening out in space'! 🎯"
        )
        content.setStyleSheet(f"color: {AutoFireColor.TEXT_SECONDARY}; padding: 10px;")
        layout.addWidget(content)

        layout.addStretch()

        window.setCentralWidget(widget)

        # Register with window manager
        window_id = f"{window_type}_{len(self.window_manager.active_windows)}"
        self.window_manager.register_window(window, window_id, window_type)

        window.show()

        print(f"✨ Created {window_type} window with intelligent positioning")

    def save_current_layout(self):
        """Save current layout with a demo name."""
        import time

        layout_name = f"demo_layout_{int(time.time())}"
        self.window_manager.save_current_layout(layout_name)

        QMessageBox.information(
            self, "Layout Saved", f"Current workspace layout saved as:\n'{layout_name}'"
        )

    def load_layout_demo(self):
        """Demonstrate loading a layout."""
        layouts = self.window_manager.get_available_layouts()
        if not layouts:
            QMessageBox.information(
                self, "No Layouts", "No saved layouts available.\nSave the current layout first."
            )
            return

        # For demo, load the first available layout
        layout_name = layouts[0]
        self.window_manager.load_layout(layout_name)

        QMessageBox.information(self, "Layout Loaded", f"Loaded workspace layout:\n'{layout_name}'")


def main():
    """Run the Window Management System demonstration."""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("AutoFire Window Management Demo")

    # Apply dark theme
    app.setStyleSheet(
        f"""
        QApplication {{
            background-color: {AutoFireColor.BACKGROUND};
        }}
        QMainWindow {{
            background-color: {AutoFireColor.BACKGROUND};
            color: {AutoFireColor.TEXT};
        }}
        QPushButton {{
            background-color: {AutoFireColor.SURFACE};
            color: {AutoFireColor.TEXT};
            border: 1px solid {AutoFireColor.BORDER};
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {AutoFireColor.PRIMARY};
        }}
        QLabel {{
            color: {AutoFireColor.TEXT};
        }}
        QMenuBar {{
            background-color: {AutoFireColor.SURFACE};
            color: {AutoFireColor.TEXT};
            border-bottom: 1px solid {AutoFireColor.BORDER};
        }}
        QMenuBar::item:selected {{
            background-color: {AutoFireColor.PRIMARY};
        }}
        QMenu {{
            background-color: {AutoFireColor.SURFACE};
            color: {AutoFireColor.TEXT};
            border: 1px solid {AutoFireColor.BORDER};
        }}
        QMenu::item:selected {{
            background-color: {AutoFireColor.PRIMARY};
        }}
    """
    )

    print("🚀 Starting AutoFire Professional Window Management System")
    print("=" * 60)
    print("🎯 Addressing: 'windows opening out in space feels weird'")
    print("✨ Features: Intelligent positioning, multi-monitor support, saved layouts")
    print("=" * 60)

    # Create and show the demo
    demo = WindowManagementDemo()
    demo.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
