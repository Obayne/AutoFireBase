#!/usr/bin/env python3
"""Test device placement flow: select device and place it on the canvas."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication

from app.app_controller import AppController
from frontend.windows.model_space import ModelSpaceWindow


def main():
    _app = QApplication.instance() or QApplication(sys.argv)

    controller = AppController()
    window = ModelSpaceWindow(controller)

    # Ensure device browser exists and has items
    db = getattr(window, "device_browser", None)
    if db is None:
        print("❌ Device browser missing")
        return 2

    tree = getattr(db, "device_tree", None)
    if tree is None or tree.topLevelItemCount() == 0:
        print("❌ Device tree empty")
        return 2

    # pick first device child under first category
    cat = tree.topLevelItem(0)
    if cat is None or cat.childCount() == 0:
        print("❌ No devices under first category")
        return 2

    dev_item = cat.child(0)
    dev = dev_item.data(0, QtCore.Qt.ItemDataRole.UserRole)
    if not dev:
        print("❌ Device data missing on tree item")
        return 2

    initial_count = len(window.devices_group.childItems())

    # Start placement
    window._start_device_placement(dev)
    tool = getattr(window, "device_placement_tool", None)
    if tool is None or not tool.is_active():
        print("❌ Placement tool not active")
        return 2

    # Place at center
    center = window.view.mapToScene(window.view.viewport().rect().center())
    ok = tool.place_device_at(center)
    if not ok:
        print("❌ place_device_at returned False")
        return 2

    final_count = len(window.devices_group.childItems())
    if final_count <= initial_count:
        print("❌ Device not added to devices_group")
        return 2

    print("✅ Device placement test PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
