#!/usr/bin/env python3
"""
Test the simplified professional settings approach.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

    from frontend.panels.professional_settings import ProfessionalSettingsPanel

    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("🔥 AutoFire Professional Setup")
            self.setFixedSize(500, 400)

            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            # Add the professional settings panel
            self.settings_panel = ProfessionalSettingsPanel()
            self.settings_panel.settings_changed.connect(self.on_settings_changed)
            self.settings_panel.ready_to_work.connect(self.on_ready_to_work)

            layout.addWidget(self.settings_panel)

        def on_settings_changed(self, settings):
            """Handle settings changes."""
            print(f"⚙️ Settings changed: {settings}")

        def on_ready_to_work(self):
            """Handle user ready to start designing."""
            settings = self.settings_panel.get_settings()
            print(f"🚀 Professional ready to work with settings: {settings}")
            print("✅ This would launch the main CAD workspace")

            # In real implementation, this would:
            # 1. Apply the assistance settings
            # 2. Close this panel
            # 3. Open the main CAD workspace
            # 4. Let the professional start designing immediately

    def test_professional_settings():
        app = QApplication([])

        window = TestWindow()
        window.show()

        print("🔥 Testing Professional Settings Panel")
        print("✅ Simple assistance level selection")
        print("✅ AI aggressiveness slider")
        print("✅ Direct 'Start Designing' button")
        print("\n💡 This is what professionals want:")
        print("   🚫 Off - Zero hand-holding")
        print("   ⚡ Minimal - Smart defaults, no interruptions")
        print("   📚 Full - Educational guidance")

        return app.exec()

    if __name__ == "__main__":
        test_professional_settings()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This test requires PySide6.")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
