"""
Circuit Manager - Circuit management and organization
"""


class CircuitManager:
    """Manages circuits in the CAD system."""

    def __init__(self, scene):
        self.scene = scene
        self.circuits = {}
        self.next_id = 1

    def add_circuit(self, name: str, circuit_type: str = "power") -> str:
        """Add a new circuit."""
        circuit_id = f"C{self.next_id:03d}"
        self.circuits[circuit_id] = {
            "id": circuit_id,
            "name": name,
            "type": circuit_type,
            "devices": [],
            "wires": [],
        }
        self.next_id += 1
        return circuit_id

    def get_circuit(self, circuit_id: str):
        """Get a circuit by ID."""
        return self.circuits.get(circuit_id)

    def get_all_circuits(self):
        """Get all circuits."""
        return list(self.circuits.values())

    def remove_circuit(self, circuit_id: str) -> bool:
        """Remove a circuit."""
        if circuit_id in self.circuits:
            del self.circuits[circuit_id]
            return True
        return False
