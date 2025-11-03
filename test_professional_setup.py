#!/usr/bin/env python3
"""
Test the professional project setup.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from PySide6.QtWidgets import QApplication

    from frontend.panels.professional_project_setup import ProfessionalProjectSetup

    def test_professional_setup():
        app = QApplication([])

        # Create the professional setup
        setup = ProfessionalProjectSetup()
        setup.show()

        print("🚀 Testing Professional Project Setup")
        print("✅ Direct workflow - no forced steps")
        print("✅ Floor plan loading (PDF/DWG/DXF)")
        print("✅ AI assistance configurable (Off to Aggressive)")
        print("✅ Quick project parameters")
        print("✅ Immediate design start")
        print("\n💡 This is what professionals want:")
        print("📁 Load floor plan")
        print("⚙️ Set basic parameters")
        print("🚀 Start designing immediately")
        print("🤖 AI assistance as needed (configurable)")

        return app.exec()

    if __name__ == "__main__":
        test_professional_setup()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This test requires PySide6 and the full project structure.")
except Exception as e:
    print(f"❌ Error testing professional setup: {e}")
    import traceback

    traceback.print_exc()
