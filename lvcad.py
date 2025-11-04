#!/usr/bin/env python3
"""
LV CAD - Low Voltage CAD Intelligence
====================================

SIMPLE, UNIFIED SOLUTION
- One application, clear purpose
- Professional CAD design with Layer Vision intelligence
- No confusion, no complexity

Launch Command: python lvcad.py
"""

import sys

# Add current directory to path for imports
sys.path.insert(0, ".")


def show_product_info():
    """Display clear product information."""
    print("🎯 LV CAD - Low Voltage CAD Intelligence")
    print("=" * 50)
    print("✨ SIMPLE. PROFESSIONAL. INTELLIGENT.")
    print()
    print("🧠 WHAT IT DOES:")
    print("   • Professional CAD design for fire protection systems")
    print("   • Intelligent layer analysis with exact device detection")
    print("   • Real-world engineering precision vs manual estimation")
    print("   • Complete project management and compliance checking")
    print()
    print("👥 WHO IT'S FOR:")
    print("   • Fire protection engineers and designers")
    print("   • Project managers and compliance specialists")
    print("   • Anyone designing low voltage fire systems")
    print()
    print("💰 SIMPLE PRICING:")
    print("   🆓 FREE TIER:")
    print("      • Basic CAD drawing tools")
    print("      • Manual device placement")
    print("      • Export to standard formats")
    print()
    print("   💼 PROFESSIONAL ($99/month):")
    print("      • Layer Vision Intelligence Engine")
    print("      • Automatic device detection from CAD")
    print("      • AI-powered document analysis")
    print("      • Compliance checking and reporting")
    print("      • Project management tools")
    print()
    print("   🏢 ENTERPRISE (Contact Sales):")
    print("      • Multi-user collaboration")
    print("      • Custom integrations")
    print("      • Priority support")
    print("      • Training and consulting")
    print()


def launch_unified_interface():
    """Launch the unified LV CAD interface."""
    print("🚀 LAUNCHING LV CAD...")
    print("=" * 30)

    try:
        # Try modern frontend first
        print("✅ Loading modern CAD interface...")
        from frontend.app import main as frontend_main

        print("🎨 Starting LV CAD Professional Interface")
        frontend_main()

    except ImportError:
        print("⚠️  Modern interface unavailable, using legacy CAD...")
        try:
            # Fallback to legacy app
            from app.main import main as legacy_main

            print("🎨 Starting LV CAD Legacy Interface")
            legacy_main()

        except ImportError as e:
            print(f"❌ Could not start CAD interface: {e}")
            print("💡 Try: pip install -r requirements.txt")
            return False

    return True


def check_system_requirements():
    """Verify system is ready for LV CAD."""
    print("🔍 CHECKING SYSTEM REQUIREMENTS...")

    requirements = [
        ("Python 3.11+", sys.version_info >= (3, 11)),
        ("PySide6", check_import("PySide6")),
        ("Layer Intelligence", check_import("autofire_layer_intelligence")),
        ("Document Analysis", check_import("fire_pilot")),
    ]

    all_good = True
    for name, status in requirements:
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {name}")
        if not status:
            all_good = False

    if not all_good:
        print()
        print("⚠️  Missing requirements detected.")
        print("💡 Run: pip install -r requirements.txt")
        return False

    print("✅ System ready for LV CAD!")
    return True


def check_import(module_name):
    """Helper to check if module can be imported."""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def show_getting_started():
    """Show simple getting started guide."""
    print()
    print("🎯 GETTING STARTED:")
    print("=" * 20)
    print("1. 📁 Create new project or open existing .lvcad file")
    print("2. 🎨 Use drawing tools to create your fire protection layout")
    print("3. 🧠 Run Layer Intelligence to detect devices automatically")
    print("4. 📄 Generate compliance reports and documentation")
    print("5. 💾 Save and share your professional fire protection design")
    print()
    print("💡 Need help? Check documentation or contact support")


def main():
    """Main LV CAD launcher with clear, simple interface."""
    print()
    show_product_info()
    print()

    # Check if user wants to see system info
    if len(sys.argv) > 1 and sys.argv[1] in ["--info", "-i", "info"]:
        show_getting_started()
        return

    # Check system requirements
    if not check_system_requirements():
        print()
        print("🔧 Please install requirements and try again:")
        print("   pip install -r requirements.txt")
        return

    print()
    show_getting_started()
    print()

    # Launch the unified interface
    try:
        success = launch_unified_interface()
        if success:
            print("✅ LV CAD launched successfully!")
        else:
            print("❌ Failed to launch LV CAD")

    except KeyboardInterrupt:
        print("\n⏹️  LV CAD startup cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("💡 Please report this issue to support")


if __name__ == "__main__":
    main()
