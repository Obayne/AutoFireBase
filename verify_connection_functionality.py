"""
Test script to verify connection functionality without running the full GUI.
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
from app.wiring import WireManager

def test_connection_functionality():
    """Test the connection functionality."""
    print("Testing device connection functionality...")
    
    # Create devices
    facp = DeviceItem(100, 100, "FACP", "Fire Alarm Panel", "Generic", "FACP-001")
    facp.device_type = "Control"
    
    smoke = DeviceItem(200, 200, "SD", "Smoke Detector", "Generic", "SD-001")
    smoke.device_type = "Detector"
    
    print(f"Initial FACP connection status: {facp.connection_status}")
    print(f"Initial Smoke connection status: {smoke.connection_status}")
    
    # Test connection status indicators
    print("\nTesting connection status indicators:")
    facp.set_connection_status("disconnected")
    print(f"FACP disconnected status: {facp.connection_status}")
    
    facp.set_connection_status("partial")
    print(f"FACP partial status: {facp.connection_status}")
    
    facp.set_connection_status("connected")
    print(f"FACP connected status: {facp.connection_status}")
    
    # Test device connections
    print("\nTesting device connections:")
    facp.add_connection(smoke)
    print(f"FACP connections: {len(facp.connections)}")
    print(f"Smoke incoming connections: {len(smoke.incoming_connections)}")
    
    # Test connection count
    print(f"FACP total connections: {facp.get_connection_count()}")
    print(f"Smoke total connections: {smoke.get_connection_count()}")
    
    # Test WireManager
    print("\nTesting WireManager:")
    wire_manager = WireManager()
    wire_manager.create_circuit(1, "SLC", "Main SLC Loop")
    print(f"Created circuit 1")
    
    wire = wire_manager.connect_devices(facp, smoke, 1, "SLC")
    print(f"Connected devices with wire: {wire}")
    
    # Test automatic address assignment
    print("\nTesting automatic address assignment:")
    wire_manager.connect_device_to_circuit(smoke, 1, auto_assign_address=True)
    print(f"Smoke SLC address: {smoke.slc_address}")
    
    # Test circuit statistics
    stats = wire_manager.get_circuit_statistics(1)
    print(f"Circuit 1 statistics: {stats}")
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    test_connection_functionality()