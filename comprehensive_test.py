#!/usr/bin/env python3
"""
Comprehensive AutoFire Test Suite
Tests device palette, placement, and System Builder functionality
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication


def test_device_catalog():
    """Test device catalog loading."""
    print("=== Testing Device Catalog ===")
    try:
        from backend.catalog import load_catalog

        devices = load_catalog()
        print(f"✓ Loaded {len(devices)} devices")

        # Check device types
        types = {}
        for d in devices:
            t = d.get("type", "Unknown")
            types[t] = types.get(t, 0) + 1

        print("Device breakdown:")
        for t, count in sorted(types.items()):
            print(f"  {t}: {count} devices")
def test_model_space(qapp, app_controller):
        return None
    except Exception as e:
        pytest.fail(f"Device catalog test failed: {e}")


def test_database_connectivity():
    """Test database connectivity and panel/device loading."""
    print("\n=== Testing Database Connectivity ===")
    try:
        from db import loader as db_loader

        con = db_loader.connect()

        # Test panels
        panels = db_loader.fetch_panels(con)
        print(f"✓ Loaded {len(panels)} panels")

        # Test devices
        devices = db_loader.fetch_devices(con)
        print(f"✓ Loaded {len(devices)} devices")

        # Test wires
        wires = db_loader.fetch_wires(con)
        print(f"✓ Loaded {len(wires)} wires")

        con.close()
        print("✓ Database operations completed successfully")
        return None
    except Exception as e:
        pytest.fail(f"Database test failed: {e}")


def test_system_builder():
    """Test System Builder panel creation and basic functionality."""
    print("\n=== Testing System Builder ===")
    try:
        # Ensure QApplication exists
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        from frontend.panels.panel_system_builder import PanelSelectionDialog, SystemBuilderPanel

        # Test panel selection dialog
        dialog = PanelSelectionDialog()
        dialog._load_panel_data()
        panels = dialog.panels
        print(f"✓ Panel selection dialog loaded {len(panels)} panels")

        # Test system builder panel
        panel = SystemBuilderPanel()

        # Test panel selection and device loading
        panel.panel_config = {"panel": {"id": 1, "name": "MS-9050UD Fire Alarm Control Panel"}}
        panel._load_compatible_devices()
        print(f"✓ System Builder loaded {len(panel.devices)} compatible devices")

        # Test wire loading
        _wires = panel._load_wire_types()
        print("✓ Loaded wire types (UI populated)")

        return None
    except Exception as e:
        pytest.fail(f"System Builder test failed: {e}")


def test_model_space(qapp, app_controller):
    """Test Model Space window and device palette."""
    print("\n=== Testing Model Space ===")
    try:
    from frontend.windows.model_space import ModelSpaceWindow

    # Use test-safe controller fixture to avoid importing Qt-heavy app
    controller = app_controller
        devices_all = controller.devices_all

        print(f"✓ Controller loaded {len(devices_all)} devices")

        # Test model space window creation (without showing)
        window = ModelSpaceWindow(controller)
        print("✓ Model Space window created successfully")

        # Test device tree population
        device_count = window.device_tree.topLevelItemCount()
        total_devices = 0
        for i in range(device_count):
            category = window.device_tree.topLevelItem(i)
            if category:
                total_devices += category.childCount()

        print(
            f"✓ Device palette populated with {total_devices} devices in {device_count} categories"
        )

        return None
    except Exception as e:
        pytest.fail(f"Model Space test failed: {e}")


def test_device_placement(qapp):
    """Test device placement functionality."""
    print("\n=== Testing Device Placement ===")
    try:
        from frontend.device import DeviceItem

        # Test device item creation
        device = DeviceItem(100, 100, "SD", "Smoke Detector", "Test Mfg", "TEST-001")
        print("✓ Device item created successfully")

        # Test basic properties
        assert device.symbol == "SD"
        assert device.name == "Smoke Detector"
        assert device.manufacturer == "Test Mfg"
        assert device.part_number == "TEST-001"
        print("✓ Device properties set correctly")
        def test_gui_components(qapp):
        # Test position
        pos = device.pos()
        assert pos.x() == 100
        assert pos.y() == 100
        print("✓ Device position set correctly")

        return None
    except Exception as e:
        import traceback

        traceback.print_exc()
        pytest.fail(f"Device placement test failed: {e}")


def test_gui_components(qapp):
    """Run a quick GUI test to ensure windows can be created."""
    print("\n=== Testing GUI Components ===")

    try:
    print("Creating AutoFire controller (test fixture)...")
    # Use the test fixture rather than constructing the real controller
    controller = app_controller
        print("✓ AutoFire controller created")

        # Test that we can access main components
        devices = controller.devices_all
        print(f"✓ Controller has {len(devices)} devices loaded")

        return None
    except Exception as e:
        import traceback

        traceback.print_exc()
        pytest.fail(f"GUI test failed: {e}")


def main():
    """Run all tests."""
    print("🚀 AutoFire Comprehensive Test Suite")
    print("=" * 50)

    tests = [
        test_device_catalog,
        test_database_connectivity,
        test_system_builder,
        test_model_space,
        test_device_placement,
        test_gui_components,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test {test.__name__} failed: {e}")
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! AutoFire is ready for use.")
        return 0
    else:
        print(f"⚠️  {total - passed} tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
