#!/usr/bin/env python3
"""
Test the integrated CAD workspace with AI context.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from PySide6.QtWidgets import QApplication

    from frontend.panels.direct_cad_launcher import DirectCADLauncher

    def test_ai_context_integration():
        """Test that AI context is properly loaded and applied."""
        app = QApplication([])

        # Create the direct CAD launcher
        launcher = DirectCADLauncher()

        def on_cad_ready(settings):
            """Handle CAD ready with AI context."""
            print("🎯 Testing AI Context Integration")
            print("=" * 40)

            ai_context = settings.get("ai_context", {})

            print(f"📊 AI Context Items Loaded: {len(ai_context)}")
            print("\n🤖 AI Knowledge Base:")

            # Location and jurisdiction
            location = ai_context.get("location", "Unknown")
            jurisdiction = ai_context.get("jurisdiction_type", "Unknown")
            print(f"   📍 Location: {location} ({jurisdiction})")

            # Fire codes and standards
            fire_code = ai_context.get("fire_code", "Unknown")
            nfpa_edition = ai_context.get("nfpa_edition", "Unknown")
            print(f"   📋 Fire Code: {fire_code}")
            print(f"   📖 NFPA Edition: {nfpa_edition}")

            # Manufacturers and devices
            manufacturers = ai_context.get("preferred_manufacturers", [])
            device_count = ai_context.get("device_count", 0)
            print(f"   🏭 Preferred Manufacturers: {', '.join(manufacturers)}")
            print(f"   📦 Device Catalog: {device_count:,} devices")

            # Technical standards
            voltage_standards = ai_context.get("voltage_standards", [])
            wire_types = ai_context.get("wire_types", [])
            print(f"   ⚡ Voltage Standards: {', '.join(voltage_standards)}")
            print(f"   🔌 Wire Types: {', '.join(wire_types)}")

            # Compliance settings
            compliance = ai_context.get("compliance_level", "Manual")
            code_checking = ai_context.get("code_checking", "Manual")
            print(f"   ✅ Compliance Level: {compliance}")
            print(f"   🔍 Code Checking: {code_checking}")

            print("\n🚀 Professional Benefits:")
            print("   ✅ No manual configuration needed")
            print("   ✅ Smart defaults based on location")
            print("   ✅ Automatic compliance checking")
            print("   ✅ Regional manufacturer preferences")
            print("   ✅ Local code requirements applied")

            print("\n💡 This AI context would enhance:")
            print("   🎯 Device filtering (regional preferences)")
            print("   📐 Circuit calculations (local standards)")
            print("   ✅ Compliance checking (local codes)")
            print("   📊 Smart suggestions (location-aware)")

            app.quit()

        launcher.cad_ready.connect(on_cad_ready)
        launcher.show()

        return app.exec()

    if __name__ == "__main__":
        test_ai_context_integration()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This test requires PySide6.")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
