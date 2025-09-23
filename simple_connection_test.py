"""
Simple test for device connection functionality without GUI.
"""

class MockDevice:
    """Mock device for testing connections."""
    def __init__(self, name):
        self.name = name
        self.connection_status = "disconnected"
        self.connections = []
        self.incoming_connections = []
        
    def add_connection(self, device):
        """Add a connection to another device."""
        if device not in self.connections:
            self.connections.append(device)
            if self not in device.incoming_connections:
                device.incoming_connections.append(self)
            self._update_connection_status()
            
    def remove_connection(self, device):
        """Remove a connection to another device."""
        if device in self.connections:
            self.connections.remove(device)
            if self in device.incoming_connections:
                device.incoming_connections.remove(self)
            self._update_connection_status()
            
    def _update_connection_status(self):
        """Update connection status based on connections."""
        total_connections = len(self.connections) + len(self.incoming_connections)
        
        if total_connections == 0:
            self.connection_status = "disconnected"
        else:
            self.connection_status = "connected"

def test_device_connections():
    """Test device connection functionality."""
    # Create two devices
    device1 = MockDevice("Device 1")
    device2 = MockDevice("Device 2")
    
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

if __name__ == "__main__":
    test_device_connections()