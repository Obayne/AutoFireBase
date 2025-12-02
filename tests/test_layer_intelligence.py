"""Tests for autofire_layer_intelligence module."""

import pytest

from autofire_layer_intelligence import CADDevice, CADLayerIntelligence, LayerInfo


class TestLayerInfo:
    """Test LayerInfo dataclass."""

    def test_layer_info_creation(self):
        """Test creating a LayerInfo object."""
        layer = LayerInfo(name="FIRE-ALARM", color="red", device_count=5)
        assert layer.name == "FIRE-ALARM"
        assert layer.color == "red"
        assert layer.device_count == 5
        assert layer.is_visible is True

    def test_layer_info_defaults(self):
        """Test default values for optional fields."""
        layer = LayerInfo(name="TEST-LAYER")
        assert layer.color is None
        assert layer.linetype is None
        assert layer.lineweight is None
        assert layer.is_visible is True
        assert layer.device_count == 0


class TestCADDevice:
    """Test CADDevice dataclass."""

    def test_cad_device_creation(self):
        """Test creating a CADDevice object."""
        device = CADDevice(
            device_type="smoke_detector",
            coordinates=(10.5, 20.3),
            layer_name="FIRE-SMOKE",
        )
        assert device.device_type == "smoke_detector"
        assert device.coordinates == (10.5, 20.3)
        assert device.layer_name == "FIRE-SMOKE"
        assert device.nfpa_compliant is True

    def test_cad_device_with_properties(self):
        """Test creating a device with custom properties."""
        props = {"model": "SD-100", "manufacturer": "System Sensor"}
        device = CADDevice(
            device_type="smoke_detector",
            coordinates=(5.0, 5.0),
            layer_name="FIRE",
            properties=props,
        )
        assert device.properties == props
        assert device.properties["model"] == "SD-100"


class TestCADLayerIntelligence:
    """Test CADLayerIntelligence class."""

    @pytest.fixture
    def intelligence(self):
        """Create a fresh CADLayerIntelligence instance."""
        return CADLayerIntelligence()

    def test_initialization(self, intelligence):
        """Test that CADLayerIntelligence initializes correctly."""
        assert isinstance(intelligence.fire_protection_patterns, list)
        assert isinstance(intelligence.device_patterns, dict)
        assert len(intelligence.fire_protection_patterns) > 0
        assert len(intelligence.device_patterns) > 0

    def test_fire_protection_patterns(self, intelligence):
        """Test that common fire protection keywords are recognized."""
        patterns = intelligence.fire_protection_patterns
        assert "fire" in patterns
        assert "smoke" in patterns
        assert "alarm" in patterns
        assert "detector" in patterns

    def test_device_patterns(self, intelligence):
        """Test that device type patterns are defined."""
        patterns = intelligence.device_patterns
        assert "smoke_detector" in patterns
        assert "heat_detector" in patterns
        assert "manual_pull_station" in patterns

    def test_smoke_detector_patterns(self, intelligence):
        """Test smoke detector pattern keywords."""
        smoke_patterns = intelligence.device_patterns.get("smoke_detector", [])
        assert "smoke" in smoke_patterns
        assert "detector" in [p for p in smoke_patterns if "det" in p.lower()]

    def test_heat_detector_patterns(self, intelligence):
        """Test heat detector pattern keywords."""
        heat_patterns = intelligence.device_patterns.get("heat_detector", [])
        assert "heat" in heat_patterns

    def test_pull_station_patterns(self, intelligence):
        """Test manual pull station pattern keywords."""
        pull_patterns = intelligence.device_patterns.get("manual_pull_station", [])
        assert "pull" in pull_patterns
        assert "manual" in pull_patterns


class TestLayerAnalysis:
    """Test layer analysis functionality."""

    @pytest.fixture
    def intelligence(self):
        """Create intelligence instance for testing."""
        return CADLayerIntelligence()

    def test_analyze_layer_name_fire_protection(self, intelligence):
        """Test that fire protection layer names are recognized."""
        fire_layers = [
            "FIRE-ALARM",
            "E-FIRE",
            "SMOKE-DETECTORS",
            "FP-DEVICES",
            "NOTIFICATION",
        ]

        for layer_name in fire_layers:
            # Layer should contain fire protection keywords
            is_fire_layer = any(
                pattern in layer_name.lower() for pattern in intelligence.fire_protection_patterns
            )
            assert is_fire_layer, f"Layer '{layer_name}' not recognized as fire protection"

    def test_device_type_detection(self, intelligence):
        """Test device type detection from layer/block names."""
        test_cases = {
            "SD": "smoke_detector",
            "SMOKE-DET": "smoke_detector",
            "HEAT-DET": "heat_detector",
            "MPS": "manual_pull_station",
            "PULL-STATION": "manual_pull_station",
        }

        for name, expected_type in test_cases.items():
            patterns = intelligence.device_patterns.get(expected_type, [])
            # Check if name contains any of the patterns
            matches = any(pattern.lower() in name.lower() for pattern in patterns)
            assert matches, f"'{name}' should match device type '{expected_type}' patterns"


class TestDeviceDetection:
    """Test device detection algorithms."""

    @pytest.fixture
    def intelligence(self):
        """Create intelligence instance."""
        return CADLayerIntelligence()

    def test_device_coordinates_valid(self):
        """Test that device coordinates are tuples of floats."""
        device = CADDevice(
            device_type="smoke_detector", coordinates=(10.5, 20.5), layer_name="FIRE"
        )

        assert isinstance(device.coordinates, tuple)
        assert len(device.coordinates) == 2
        assert isinstance(device.coordinates[0], int | float)
        assert isinstance(device.coordinates[1], int | float)

    def test_device_with_room_assignment(self):
        """Test device with room assignment."""
        device = CADDevice(
            device_type="smoke_detector",
            coordinates=(5.0, 5.0),
            layer_name="FIRE",
            room="ROOM-101",
        )
        assert device.room == "ROOM-101"

    def test_device_nfpa_compliance_flag(self):
        """Test NFPA compliance flag."""
        compliant_device = CADDevice(
            device_type="smoke_detector",
            coordinates=(5.0, 5.0),
            layer_name="FIRE",
            nfpa_compliant=True,
        )
        assert compliant_device.nfpa_compliant is True

        non_compliant_device = CADDevice(
            device_type="smoke_detector",
            coordinates=(5.0, 5.0),
            layer_name="FIRE",
            nfpa_compliant=False,
        )
        assert non_compliant_device.nfpa_compliant is False


class TestIntegration:
    """Integration tests for layer intelligence."""

    @pytest.fixture
    def intelligence(self):
        """Create intelligence instance."""
        return CADLayerIntelligence()

    def test_multiple_device_types(self, intelligence):
        """Test handling multiple device types."""
        devices = [
            CADDevice("smoke_detector", (10, 10), "FIRE-SMOKE"),
            CADDevice("heat_detector", (20, 20), "FIRE-HEAT"),
            CADDevice("manual_pull_station", (30, 30), "FIRE-MPS"),
        ]

        assert len(devices) == 3
        assert len(set(d.device_type for d in devices)) == 3

    def test_layer_with_multiple_devices(self):
        """Test a layer containing multiple devices."""
        layer = LayerInfo(name="FIRE-ALARM", device_count=10)
        assert layer.device_count == 10

        # Simulate adding devices
        devices = [CADDevice("smoke_detector", (i * 10, i * 10), "FIRE-ALARM") for i in range(10)]
        assert len(devices) == layer.device_count
