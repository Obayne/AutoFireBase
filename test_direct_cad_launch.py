#!/usr/bin/env python3
"""
Test the direct CAD launch with AI initialization.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

    from frontend.panels.direct_cad_launcher import DirectCADLauncher

    class TestDirectCAD(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("🔥 AutoFire - Direct Professional Launch")
            self.setFixedSize(600, 400)

            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            # Add the direct CAD launcher
            self.cad_launcher = DirectCADLauncher()
            self.cad_launcher.cad_ready.connect(self.on_cad_ready)

            layout.addWidget(self.cad_launcher)

        def on_cad_ready(self, settings):
            """Handle CAD workspace ready."""
            print("\n🎯 PROFESSIONAL CAD WORKSPACE READY!")
            print("=====================================")

            ai_context = settings.get("ai_context", {})
            print("🤖 AI learned about your environment:")
            print(f"   📍 Location: {ai_context.get('location', 'Unknown')}")
            print(f"   📋 Fire Code: {ai_context.get('fire_code', 'Standard')}")
            print(
                f"   🏭 Manufacturers: {len(ai_context.get('preferred_manufacturers', []))} detected"
            )
            print(f"   📦 Device Catalog: {ai_context.get('device_count', 0)} devices")
            print(f"   ⚡ Compliance: {ai_context.get('compliance_level', 'Basic')}")

            print("\n🚀 READY FOR PROFESSIONAL WORK:")
            print("   ✅ Load floor plans (PDF/DWG/DXF)")
            print("   ✅ Place fire alarm devices")
            print("   ✅ Design circuits with voltage drop calculations")
            print("   ✅ Generate professional documentation")
            print("   ✅ AI assists quietly in background")

            print("\n💡 This is what fire alarm professionals want:")
            print("   → No menus or wizards to slow them down")
            print("   → Direct access to CAD tools immediately")
            print("   → AI learns context without interrupting workflow")
            print("   → Professional results from day one")

    def test_direct_cad():
        app = QApplication([])

        window = TestDirectCAD()
        window.show()

        print("🔥 Testing Direct CAD Launch")
        print("🎯 Professional Approach:")
        print("   1. Launch AutoFire")
        print("   2. AI initialization (3-4 seconds)")
        print("   3. CAD workspace ready")
        print("   4. Start designing immediately")
        print("\n⏱️ Watch the initialization process...")

        return app.exec()

    if __name__ == "__main__":
        test_direct_cad()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This test requires PySide6.")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
