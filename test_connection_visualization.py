"""
Test script to demonstrate device connection visualization and automatic addressing.
"""

import sys
import os
from PySide6 import QtWidgets, QtCore
from app.main import MainWindow
from app.device import DeviceItem

def test_connection_visualization():
    """Test the connection visualization and automatic addressing features."""
    
    # Create a simple Qt application
    app = QtWidgets.QApplication(sys.argv)
    
    # Create the main window
    window = MainWindow()
    
    # Add a FACP panel
    facp = DeviceItem(100, 100, "FACP", "Fire Alarm Panel", "Generic", "FACP-001")
    facp.device_type = "Control"
    facp.setParentItem(window.layer_devices)
    
    # Add a smoke detector
    smoke = DeviceItem(200, 200, "SD", "Smoke Detector", "Generic", "SD-001")
    smoke.device_type = "Detector"
    smoke.setParentItem(window.layer_devices)
    
    # Add a pull station
    pull = DeviceItem(300, 100, "PS", "Pull Station", "Generic", "PS-001")
    pull.device_type = "Initiating"
    pull.setParentItem(window.layer_devices)
    
    # Add a strobe
    strobe = DeviceItem(200, 300, "S", "Strobe", "Generic", "S-001")
    strobe.device_type = "Notification"
    strobe.setParentItem(window.layer_devices)
    
    # Show initial connection status (should be red blinking squares)
    print("Initial connection status:")
    print(f"FACP: {facp.connection_status}")
    print(f"Smoke: {smoke.connection_status}")
    print(f"Pull: {pull.connection_status}")
    print(f"Strobe: {strobe.connection_status}")
    
    # Connect devices to demonstrate automatic addressing
    # In a real implementation, this would be done through the wire tool
    facp.add_connection(smoke)
    facp.add_connection(pull)
    facp.add_connection(strobe)
    
    # Set SLC addresses for connected devices
    smoke.set_slc_address(1)
    pull.set_slc_address(2)
    strobe.set_slc_address(3)
    
    # Update connection status (should now be green)
    facp._update_connection_status()
    smoke._update_connection_status()
    pull._update_connection_status()
    strobe._update_connection_status()
    
    print("\nAfter connecting devices:")
    print(f"FACP: {facp.connection_status} (connections: {facp.get_connection_count()})")
    print(f"Smoke: {smoke.connection_status} (address: {smoke.slc_address})")
    print(f"Pull: {pull.connection_status} (address: {pull.slc_address})")
    print(f"Strobe: {strobe.connection_status} (address: {strobe.slc_address})")
    
    # Show the window
    window.show()
    
    # Update the view to show the devices
    window.fit_view_to_content()
    
    print("\nTest completed. You should see:")
    print("1. Four devices on the canvas")
    print("2. Red blinking squares for disconnected devices initially")
    print("3. Green squares for connected devices after connection")
    print("4. Address annotations next to devices")
    
    # Run the application
    # sys.exit(app.exec())  # Commented out for testing purposes

if __name__ == "__main__":
    test_connection_visualization()