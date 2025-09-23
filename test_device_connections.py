"""
Test script for device connection functionality.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Mock the PySide6 imports for testing
import unittest.mock as mock

# Mock PySide6 modules
sys.modules['PySide6'] = mock.MagicMock()
sys.modules['PySide6.QtCore'] = mock.MagicMock()
sys.modules['PySide6.QtGui'] = mock.MagicMock()
sys.modules['PySide6.QtWidgets'] = mock.MagicMock()

from app.device import DeviceItem

def test_device_connections():
    """Test device connection functionality."""
    # Create two devices
    device1 = DeviceItem(100, 100, "FACP", "Fire Alarm Panel", "Generic", "FACP-001")
    device1.device_type = "Control"  # Set device type after creation
    
    device2 = DeviceItem(200, 200, "SD", "Smoke Detector", "Generic", "SD-001")
    device2.device_type = "Detector"  # Set device type after creation
    
    # Test initial connection status
    print(f"Device 1 initial status: {device1.connection_status}")
    print(f"Device 2 initial status: {device2.connection_status}")
    
    # Connect devices
    device1.add_connection(device2)
    
    # Test connection status after connecting
    print(f"Device 1 status after connection: {device1.connection_status}")
    print(f"Device 2 status after connection: {device2.connection_status}")
    
    print(f"Device 1 connections: {len(device1.connections)}")
    print(f"Device 2 incoming connections: {len(device2.incoming_connections)}")
    
    # Test removing connection
    device1.remove_connection(device2)
    
    # Test connection status after disconnecting
    print(f"Device 1 status after disconnection: {device1.connection_status}")
    print(f"Device 2 status after disconnection: {device2.connection_status}")
    
    print("Device connection test completed successfully!")
    
    return 0

if __name__ == "__main__":
    test_device_connections()