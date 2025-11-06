#!/usr/bin/env python3
"""
LV CAD Functionality Test
Tests drawing tools and device placement functionality
"""

import os
import sys

import pytest

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication

from app.app_controller import AppController
from app.tools.draw import DrawMode
from frontend.windows.model_space import ModelSpaceWindow


def test_drawing_tools():
    """Test that drawing tools are properly initialized."""
    print("🧪 Testing Drawing Tools...")

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create app controller
    app_controller = AppController()

    # Create model space window
    window = ModelSpaceWindow(app_controller)

    # Check if draw controller exists
    if hasattr(window, "draw") and window.draw is not None:
        print("✅ DrawController initialized")

        # Test setting different modes
        window.draw.set_mode(DrawMode.LINE)
        print("✅ Line mode set")

        window.draw.set_mode(DrawMode.RECT)
        print("✅ Rectangle mode set")

        window.draw.set_mode(DrawMode.CIRCLE)
        print("✅ Circle mode set")

        window.draw.set_mode(DrawMode.POLYLINE)
        print("✅ Polyline mode set")

        print("✅ Drawing tools test PASSED")
        assert True
    else:
        print("❌ DrawController not initialized")
        pytest.fail("DrawController not initialized")


def test_device_browser():
    """Test that device browser is properly initialized."""
    print("🧪 Testing Device Browser...")

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create app controller
    app_controller = AppController()

    # Create model space window
    window = ModelSpaceWindow(app_controller)

    # Check if device browser exists
    if hasattr(window, "device_browser") and window.device_browser is not None:
        print("✅ DeviceBrowser initialized")

        # Check if it has devices loaded
        device_tree = window.device_browser.device_tree
        if device_tree.topLevelItemCount() > 0:
            print(f"✅ Device tree has {device_tree.topLevelItemCount()} categories")
            print("✅ Device browser test PASSED")
            assert True
        else:
            pytest.fail("Device tree is empty")
    else:
        pytest.fail("DeviceBrowser not initialized")


def test_toolbar_connections():
    """Test that toolbar buttons are connected."""
    print("🧪 Testing Toolbar Connections...")

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create app controller
    app_controller = AppController()

    # Create model space window
    window = ModelSpaceWindow(app_controller)

    # Check toolbar exists - find QToolBar with title "Main"
    toolbar = None
    for child in window.children():
        if hasattr(child, "windowTitle") and child.windowTitle() == "Main":
            toolbar = child
            break
    if toolbar:
        print("✅ Toolbar found")

        # Check for drawing tool actions
        actions = toolbar.actions()
        drawing_tools_found = 0
        for action in actions:
            text = action.text()
            if text in ["Line", "Rectangle", "Circle", "Polyline"]:
                drawing_tools_found += 1
                print(f"✅ Found drawing tool: {text}")

        if drawing_tools_found >= 4:
            print("✅ All drawing tools found in toolbar")
            print("✅ Toolbar connections test PASSED")
            assert True
        else:
            pytest.fail(f"Only found {drawing_tools_found} drawing tools")
    else:
        print("❌ Toolbar not found")
        pytest.fail("Toolbar not found")


def main():
    """Run all tests."""
    print("🚀 LV CAD Functionality Test Suite")
    print("=" * 50)

    tests = [test_drawing_tools, test_device_browser, test_toolbar_connections]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print()

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! LV CAD is functional!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
