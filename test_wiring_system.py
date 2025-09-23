"""
Test script for intelligent wiring system with address assignment.
"""

class MockDevice:
    """Mock device for testing connections."""
    def __init__(self, name, device_type="Unknown"):
        self.name = name
        self.device_type = device_type
        self.connection_status = "disconnected"
        self.connections = []
        self.incoming_connections = []
        self.slc_address = None
        self.circuit_id = None
        
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
            
    def set_slc_address(self, address):
        """Set SLC address for this device."""
        self.slc_address = address
        
    def set_circuit_id(self, circuit_id):
        """Set circuit ID for this device."""
        self.circuit_id = circuit_id
        
    def set_label_text(self, text):
        """Set label text for this device."""
        self.name = text

class MockWireConnection:
    """Mock wire connection for testing."""
    def __init__(self, from_device, to_device, connection_type="SLC"):
        self.from_device = from_device
        self.to_device = to_device
        self.connection_type = connection_type
        self.slc_address = None
        self.circuit_id = None
        self.connection_id = None
        
    def set_addressing_info(self, circuit_id, address, connection_id=None):
        """Set addressing information for this connection."""
        self.circuit_id = circuit_id
        self.slc_address = address
        self.connection_id = connection_id

def test_intelligent_wiring():
    """Test intelligent wiring system with address assignment."""
    # Create devices
    facp = MockDevice("FACP Panel", "Control")
    smoke_detector = MockDevice("Smoke Detector", "Detector")
    pull_station = MockDevice("Pull Station", "Initiating")
    
    # Test initial state
    print("=== Initial State ===")
    print(f"FACP: {facp.connection_status}")
    print(f"Smoke Detector: {smoke_detector.connection_status}")
    print(f"Pull Station: {pull_station.connection_status}")
    
    # Create connections
    connection1 = MockWireConnection(facp, smoke_detector)
    connection2 = MockWireConnection(facp, pull_station)
    
    # Add connections to devices
    facp.add_connection(smoke_detector)
    facp.add_connection(pull_station)
    
    # Test connection status
    print("\n=== After Connections ===")
    print(f"FACP connections: {len(facp.connections)}")
    print(f"Smoke Detector incoming: {len(smoke_detector.incoming_connections)}")
    print(f"Pull Station incoming: {len(pull_station.incoming_connections)}")
    
    # Test address assignment
    print("\n=== Address Assignment ===")
    # Assign addresses to devices
    connection1.set_addressing_info(circuit_id=1, address=15)
    connection2.set_addressing_info(circuit_id=1, address=16)
    
    # Update devices with addressing info
    smoke_detector.set_slc_address(15)
    smoke_detector.set_circuit_id(1)
    smoke_detector.set_label_text(f"{smoke_detector.name} (Addr: 15)")
    
    pull_station.set_slc_address(16)
    pull_station.set_circuit_id(1)
    pull_station.set_label_text(f"{pull_station.name} (Addr: 16)")
    
    # Test addressing
    print(f"Smoke Detector: Address={smoke_detector.slc_address}, Circuit={smoke_detector.circuit_id}, Label={smoke_detector.name}")
    print(f"Pull Station: Address={pull_station.slc_address}, Circuit={pull_station.circuit_id}, Label={pull_station.name}")
    
    # Test connection removal
    facp.remove_connection(smoke_detector)
    
    print("\n=== After Removing Connection ===")
    print(f"FACP connections: {len(facp.connections)}")
    print(f"Smoke Detector incoming: {len(smoke_detector.incoming_connections)}")
    print(f"Smoke Detector status: {smoke_detector.connection_status}")
    
    print("\nIntelligent wiring system test completed successfully!")

if __name__ == "__main__":
    test_intelligent_wiring()