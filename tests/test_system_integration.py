"""
Integration tests for system configuration and device palette integration.
"""
import json
import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from app.system_builder import SystemConfiguration


class TestSystemConfigurationIntegration:
    """Test system configuration integration with device palette."""

    def test_system_configuration_creation(self):
        """Test creating a new system configuration."""
        system = SystemConfiguration("Test System")

        assert system.name == "Test System"
        assert system.facp_type == "Conventional"
        assert "smoke_detectors" in system.devices
        assert "heat_detectors" in system.devices
        assert "pull_stations" in system.devices
        assert "horn_strobes" in system.devices
        assert "speakers" in system.devices

    def test_system_configuration_serialization(self):
        """Test system configuration serialization and deserialization."""
        # Create system with devices
        system = SystemConfiguration("Test System")
        system.facp_type = "Addressable"
        system.devices["smoke_detectors"] = [
            {"manufacturer": "FireLite", "part_number": "SD100", "name": "Smoke Detector"}
        ]
        system.devices["pull_stations"] = [
            {"manufacturer": "System Sensor", "part_number": "PS100", "name": "Pull Station"}
        ]

        # Serialize
        data = system.to_dict()
        assert data["name"] == "Test System"
        assert data["facp_type"] == "Addressable"
        assert len(data["devices"]["smoke_detectors"]) == 1
        assert len(data["devices"]["pull_stations"]) == 1

        # Deserialize
        system2 = SystemConfiguration.from_dict(data)
        assert system2.name == "Test System"
        assert system2.facp_type == "Addressable"
        assert len(system2.devices["smoke_detectors"]) == 1
        assert len(system2.devices["pull_stations"]) == 1

    def test_system_configuration_power_calculation(self):
        """Test power load calculations for system configurations."""
        system = SystemConfiguration("Power Test")

        # Add some devices
        system.devices["smoke_detectors"] = [{"manufacturer": "Test", "part_number": "SD1"}] * 10
        system.devices["horn_strobes"] = [{"manufacturer": "Test", "part_number": "HS1"}] * 5
        system.devices["speakers"] = [{"manufacturer": "Test", "part_number": "SP1"}] * 3

        load = system.calculate_power_load()

        # Should be FACP base load + device loads
        expected_load = 0.5 + (10 * 0.02) + (5 * 0.15) + (3 * 0.20)  # Conventional FACP + devices
        assert abs(load - expected_load) < 0.01
        assert system.power_requirements["calculated_load"] == load

    @pytest.mark.integration
    def test_system_file_operations(self):
        """Test saving and loading system configurations to/from files."""
        system = SystemConfiguration("File Test")
        system.facp_type = "Hybrid"
        system.devices["smoke_detectors"] = [
            {"manufacturer": "FireLite", "part_number": "SD200"}
        ]

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(system.to_dict(), f)
            temp_file = f.name

        try:
            # Load from file
            with open(temp_file, 'r') as f:
                data = json.load(f)

            loaded_system = SystemConfiguration.from_dict(data)
            assert loaded_system.name == "File Test"
            assert loaded_system.facp_type == "Hybrid"
            assert len(loaded_system.devices["smoke_detectors"]) == 1

        finally:
            os.unlink(temp_file)

    def test_system_configuration_zones(self):
        """Test zone management in system configurations."""
        system = SystemConfiguration("Zone Test")

        # Add zones
        system.zones = [
            {"id": 1, "name": "Zone 1", "devices": ["smoke_1", "smoke_2"]},
            {"id": 2, "name": "Zone 2", "devices": ["pull_1"]}
        ]

        # Test serialization includes zones
        data = system.to_dict()
        assert len(data["zones"]) == 2
        assert data["zones"][0]["name"] == "Zone 1"
        assert data["zones"][1]["name"] == "Zone 2"

        # Test deserialization
        system2 = SystemConfiguration.from_dict(data)
        assert len(system2.zones) == 2
        assert system2.zones[0]["name"] == "Zone 1"


class TestDevicePaletteIntegration:
    """Test device palette integration with system configurations."""

    @pytest.mark.integration
    @patch('app.model_space_window.ModelSpaceWindow.app_controller')
    def test_device_palette_system_filtering(self, mock_controller):
        """Test that device palette filters devices based on system configuration."""
        from app.model_space_window import ModelSpaceWindow

        # Mock controller and devices
        mock_controller.devices_all = [
            {"type": "smoke_detector", "name": "SD-100", "manufacturer": "FireLite", "part_number": "SD100", "symbol": "SD"},
            {"type": "pull_station", "name": "PS-100", "manufacturer": "System Sensor", "part_number": "PS100", "symbol": "PS"},
            {"type": "heat_detector", "name": "HD-100", "manufacturer": "FireLite", "part_number": "HD100", "symbol": "HD"},
        ]
        mock_controller.prefs = {}

        # Create window (this would normally require Qt, so we'll mock)
        with patch('PySide6.QtWidgets.QMainWindow.__init__', return_value=None):
            window = ModelSpaceWindow(mock_controller)

            # Mock the device tree
            window.device_tree = Mock()

            # Create system with specific devices
            system = SystemConfiguration("Palette Test")
            system.devices["smoke_detectors"] = [
                {"manufacturer": "FireLite", "part_number": "SD100"}
            ]

            # Set current system
            window.current_system = system

            # Mock the device loading methods
            with patch.object(window, '_load_devices_for_category') as mock_load:
                mock_load.return_value = [
                    {"type": "smoke_detector", "name": "SD-100", "manufacturer": "FireLite", "part_number": "SD100", "symbol": "SD"}
                ]

                # Test the update method
                window._update_device_palette_for_system()

                # Verify that device tree operations were called
                assert window.device_tree.clear.called
                # The method should have attempted to populate with system-filtered devices

    def test_system_device_matching(self):
        """Test matching devices between system config and catalog."""
        system = SystemConfiguration("Match Test")
        system.devices["smoke_detectors"] = [
            {"manufacturer": "FireLite", "part_number": "SD100"},
            {"manufacturer": "System Sensor", "part_number": "SD200"}
        ]

        # Extract system device requirements
        system_devices = set()
        for device_type, devices in system.devices.items():
            for device in devices:
                system_devices.add((device_type, device.get('manufacturer', ''), device.get('part_number', '')))

        assert ("smoke_detectors", "FireLite", "SD100") in system_devices
        assert ("smoke_detectors", "System Sensor", "SD200") in system_devices
        assert len(system_devices) == 2


@pytest.mark.performance
class TestSystemConfigurationPerformance:
    """Performance tests for system configuration operations."""

    def test_bulk_system_creation_performance(self):
        """Test performance of creating multiple system configurations."""
        import time

        start_time = time.time()

        systems = []
        for i in range(100):
            system = SystemConfiguration(f"PerfSystem_{i}")
            # Add some devices
            system.devices["smoke_detectors"] = [
                {"manufacturer": f"Mfg_{j}", "part_number": f"PN_{j}"} for j in range(5)
            ]
            systems.append(system)

        end_time = time.time()
        duration = end_time - start_time

        # Should create 100 systems in reasonable time
        assert duration < 5.0  # Less than 5 seconds
        assert len(systems) == 100

        # Verify all systems have correct structure
        for system in systems:
            assert len(system.devices["smoke_detectors"]) == 5
            assert system.name.startswith("PerfSystem_")

    def test_serialization_performance(self):
        """Test performance of system serialization/deserialization."""
        import time

        # Create a large system
        system = SystemConfiguration("LargeSystem")
        for device_type in system.devices.keys():
            system.devices[device_type] = [
                {"manufacturer": f"Mfg_{i}", "part_number": f"PN_{i}"} for i in range(50)
            ]

        # Test serialization performance
        start_time = time.time()
        data = system.to_dict()
        serialize_time = time.time() - start_time

        # Test deserialization performance
        start_time = time.time()
        system2 = SystemConfiguration.from_dict(data)
        deserialize_time = time.time() - start_time

        # Should be fast
        assert serialize_time < 1.0
        assert deserialize_time < 1.0

        # Verify data integrity
        assert system2.name == "LargeSystem"
        assert len(system2.devices["smoke_detectors"]) == 50