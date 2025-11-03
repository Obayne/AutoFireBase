#!/usr/bin/env python3
"""
Test the complete project builder menu system with expertise-based routing.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

    from frontend.panels.project_builder_controller import ProjectBuilderController

    class TestProjectBuilder(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("🔥 AutoFire Project Builder - Complete System")
            self.setFixedSize(800, 600)

            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            # Add the project builder controller
            self.project_builder = ProjectBuilderController()
            self.project_builder.launch_cad_workspace.connect(self.on_launch_cad)

            layout.addWidget(self.project_builder)

        def on_launch_cad(self, settings):
            """Handle CAD workspace launch."""
            print("\n🚀 LAUNCHING CAD WORKSPACE")
            print(f"Settings: {settings}")

            expertise = settings.get("assistance_level", "unknown")
            project_type = settings.get("project_type", "General")

            if expertise == "expert":
                print("🎯 EXPERT MODE:")
                print("   ✅ Direct access to all CAD tools")
                print("   ✅ No assistance popups")
                print("   ✅ Professional workflow")
                print("   → Load floor plan → Place devices → Design circuits → Done")

            elif expertise == "intermediate":
                print("⚡ INTERMEDIATE MODE:")
                print("   ✅ Helpful tooltips and guidance")
                print("   ✅ Smart suggestions during design")
                print("   ✅ Automatic compliance checking")
                print("   → Guided design process with helpful tips")

            else:  # full/beginner
                print("📚 BEGINNER MODE:")
                print("   ✅ Full educational experience")
                print("   ✅ Step-by-step instructions")
                print("   ✅ NFPA 72 compliance training")
                print("   → Complete learning workflow")

            print(f"\n🏗️ Project Type: {project_type}")
            print("✅ This would now launch the main CAD workspace")
            print("✅ Settings applied to configure assistance level")

    def test_project_builder():
        app = QApplication([])

        window = TestProjectBuilder()
        window.show()

        print("🔥 Testing Complete Project Builder System")
        print("\n📋 Available Workflows:")
        print("🎯 Expert Mode:")
        print("   → Clicks 'Expert' → Goes directly to CAD")
        print("   → Zero hand-holding, all tools available")
        print("\n⚡ Intermediate Mode:")
        print("   → Clicks 'Intermediate' → Shows guidance page → CAD")
        print("   → Helpful instructions and tips during design")
        print("\n📚 Beginner Mode:")
        print("   → Clicks 'Beginner' → Full educational workflow")
        print("   → Step-by-step learning with NFPA 72 guidance")
        print("\n💡 Try each expertise level to see different workflows!")

        return app.exec()

    if __name__ == "__main__":
        test_project_builder()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This test requires PySide6.")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
