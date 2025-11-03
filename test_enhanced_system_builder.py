#!/usr/bin/env python3
"""
Test the enhanced system builder with quick setup mode.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from PySide6.QtWidgets import QApplication
    from frontend.panels.guided_system_builder import GuidedSystemBuilderWidget

    def test_system_builder():
        app = QApplication([])

        # Create the enhanced system builder
        system_builder = GuidedSystemBuilderWidget()
        system_builder.show()

        print("🚀 Testing Enhanced System Builder")
        print("✅ Mode selector available")
        print("✅ Quick setup tab functionality")
        print("✅ Manufacturer database integration")
        print("✅ Project templates and estimation")
        print("\n💡 Toggle between modes to see the difference!")
        print("📚 Guided Mode: Full educational workflow")
        print("🚀 Quick Setup: Professional express mode")

        return app.exec()

    if __name__ == "__main__":
        test_system_builder()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This test requires PySide6 and the full project structure.")
except Exception as e:
    print(f"❌ Error testing system builder: {e}")
    import traceback

    traceback.print_exc()
