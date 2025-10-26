"""
Demo script showing Enhanced Connections Panel with realistic fire alarm data.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_demo_enhanced_connections():
    """Create a demo of the enhanced connections panel with realistic data."""
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
        from frontend.panels.enhanced_connections import EnhancedConnectionsPanel
        
        # Create QApplication
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Create main window
        window = QMainWindow()
        window.setWindowTitle("🔥 AutoFire Enhanced Connections Demo")
        window.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create enhanced connections panel
        connections_panel = EnhancedConnectionsPanel()
        layout.addWidget(connections_panel)
        
        # Add realistic fire alarm circuit data
        print("Adding realistic fire alarm circuit data...")
        
        # SLC Circuit 1 - First floor detectors
        connections_panel.add_wire_segment("PANEL1", "SMOKE_101", 65.0, "14", 0.020, "SLC")
        connections_panel.add_wire_segment("SMOKE_101", "SMOKE_102", 35.0, "14", 0.020, "SLC")
        connections_panel.add_wire_segment("SMOKE_102", "PULL_101", 45.0, "14", 0.001, "SLC")
        connections_panel.add_wire_segment("PULL_101", "SMOKE_103", 55.0, "14", 0.020, "SLC")
        connections_panel.add_wire_segment("SMOKE_103", "SMOKE_104", 40.0, "14", 0.020, "SLC")
        connections_panel.add_wire_segment("SMOKE_104", "PANEL1", 85.0, "14", 0.020, "SLC")  # Class A return
        
        # SLC Circuit 2 - Second floor detectors  
        connections_panel.add_wire_segment("PANEL1", "SMOKE_201", 125.0, "14", 0.020, "SLC")
        connections_panel.add_wire_segment("SMOKE_201", "SMOKE_202", 30.0, "14", 0.020, "SLC")
        connections_panel.add_wire_segment("SMOKE_202", "HEAT_201", 25.0, "14", 0.015, "SLC")
        connections_panel.add_wire_segment("HEAT_201", "PULL_201", 60.0, "14", 0.001, "SLC")
        connections_panel.add_wire_segment("PULL_201", "PANEL1", 140.0, "14", 0.020, "SLC")  # Class A return
        
        # NAC Circuit 1 - Horns and strobes
        connections_panel.add_wire_segment("PANEL1", "HORN_101", 95.0, "12", 0.150, "NAC")
        connections_panel.add_wire_segment("HORN_101", "STROBE_101", 15.0, "12", 0.085, "NAC")
        connections_panel.add_wire_segment("STROBE_101", "HORN_102", 75.0, "12", 0.150, "NAC")
        connections_panel.add_wire_segment("HORN_102", "STROBE_102", 15.0, "12", 0.085, "NAC")
        
        # NAC Circuit 2 - More horns and strobes
        connections_panel.add_wire_segment("PANEL1", "HORN_201", 145.0, "12", 0.150, "NAC")
        connections_panel.add_wire_segment("HORN_201", "STROBE_201", 20.0, "12", 0.085, "NAC")
        connections_panel.add_wire_segment("STROBE_201", "HORN_202", 85.0, "12", 0.150, "NAC")
        
        # Update device currents for more realistic loads
        connections_panel.update_device_current("SMOKE_101", 0.020)
        connections_panel.update_device_current("SMOKE_102", 0.020)
        connections_panel.update_device_current("SMOKE_103", 0.020)
        connections_panel.update_device_current("SMOKE_104", 0.020)
        connections_panel.update_device_current("SMOKE_201", 0.020)
        connections_panel.update_device_current("SMOKE_202", 0.020)
        connections_panel.update_device_current("HEAT_201", 0.015)  # Heat detector uses less
        connections_panel.update_device_current("PULL_101", 0.001)  # Pull station minimal
        connections_panel.update_device_current("PULL_201", 0.001)
        connections_panel.update_device_current("HORN_101", 0.150)  # Horn high current
        connections_panel.update_device_current("HORN_102", 0.150)
        connections_panel.update_device_current("HORN_201", 0.150)
        connections_panel.update_device_current("HORN_202", 0.150)
        connections_panel.update_device_current("STROBE_101", 0.085)  # Strobe medium current
        connections_panel.update_device_current("STROBE_102", 0.085)
        connections_panel.update_device_current("STROBE_201", 0.085)
        
        # Add a problematic circuit to show compliance warnings
        connections_panel.add_wire_segment("PANEL1", "REMOTE_SMOKE", 8500.0, "18", 0.020, "SLC")  # Very long, small wire
        connections_panel.update_device_current("REMOTE_SMOKE", 0.020)
        
        # Perform calculations
        connections_panel.refresh_all_calculations()
        
        # Set up the main window
        window.setCentralWidget(central_widget)
        
        # Show window
        window.show()
        
        print("🔥 Enhanced Connections Demo Window opened!")
        print("Features demonstrated:")
        print("• Hierarchical circuit tree with panels, circuits, and devices")
        print("• Live voltage drop calculations per circuit")
        print("• Battery sizing calculations per panel")
        print("• NFPA 72 compliance checking with warnings")
        print("• Real-time updates as circuits change")
        print("• Professional fire alarm calculation accuracy")
        print("\nCircuits created:")
        print("• SLC_PANEL1: First floor detection loop")
        print("• SLC_PANEL1: Second floor detection loop")  
        print("• NAC_PANEL1: First floor notification")
        print("• NAC_PANEL1: Second floor notification")
        print("• SLC_PANEL1: Remote device (shows compliance warning)")
        
        return window, app
        
    except ImportError as e:
        print(f"❌ Demo requires PySide6 and AutoFire components: {e}")
        return None, None


if __name__ == "__main__":
    print("🔥 AutoFire Enhanced Connections Panel Demo")
    print("=" * 50)
    
    window, app = create_demo_enhanced_connections()
    
    if window and app:
        # Run the application
        try:
            app.exec()
        except KeyboardInterrupt:
            print("\n👋 Demo closed by user")
    else:
        print("❌ Could not create demo window")