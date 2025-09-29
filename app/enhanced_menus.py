"""
Enhanced menu functionality for AutoFire.

This module adds device-related menu items and functionality to the main window.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def add_main_window_methods(cls: type) -> None:
    """Add enhanced methods to the MainWindow class."""
    # Add device-related methods if they don't exist
    if not hasattr(cls, "show_device_palette"):

        def show_device_palette(self):
            """Show or focus the device palette dock widget."""
            from PySide6 import QtWidgets

            for dock in self.findChildren(QtWidgets.QDockWidget):
                if dock.windowTitle() == "Device Palette":
                    dock.show()
                    dock.raise_()
                    return
            # If not found, the palette should already be created in __init__

        cls.show_device_palette = show_device_palette


def enhance_menus(window) -> None:
    """Add enhanced menu items to the main window."""

    menubar = window.menuBar()

    # Add Devices menu if it doesn't exist
    devices_menu = None
    for action in menubar.actions():
        if action.text() == "&Devices":
            devices_menu = action.menu()
            break

    if devices_menu is None:
        devices_menu = menubar.addMenu("&Devices")

    # Add device-related actions
    if hasattr(window, "show_device_palette"):
        act_show_palette = devices_menu.addAction("Show Device Palette")
        act_show_palette.triggered.connect(window.show_device_palette)

    # Add separator and device management actions
    devices_menu.addSeparator()

    # Add device management actions if methods exist
    if hasattr(window, "choose_device"):
        act_add_device = devices_menu.addAction("Add Device...")
        act_add_device.triggered.connect(lambda: window.choose_device(None))

    # Add reports menu integration for battery calculations
    reports_menu = None
    for action in menubar.actions():
        if action.text() == "&Reports":
            reports_menu = action.menu()
            break

    if reports_menu is None:
        # Find Tools menu and add Reports submenu
        tools_menu = None
        for action in menubar.actions():
            if action.text() == "&Tools":
                tools_menu = action.menu()
                break

        if tools_menu:
            reports_menu = tools_menu.addMenu("Reports")

    if reports_menu:
        # Add battery calculation reports
        if hasattr(window, "show_reports_dialog"):
            act_battery = reports_menu.addAction("Battery Calculations...")
            act_battery.triggered.connect(window.show_reports_dialog)
