"""
Tests for CAD Layer Intelligence
"""

import pytest

from cad_core.intelligence import (
    EZDXF_AVAILABLE,
    CADDevice,
    CADLayerIntelligence,
    LayerClassification,
    LayerInfo,
)


class TestCADLayerIntelligence:
    """Test CAD layer intelligence functionality."""

    def test_layer_intelligence_initialization(self):
        """Test that layer intelligence engine initializes properly."""
        engine = CADLayerIntelligence()

        assert engine is not None
        assert hasattr(engine, "aia_layer_standards")
        assert hasattr(engine, "fire_safety_layers")
        assert len(engine.fire_safety_layers) > 0

    def test_layer_classification(self):
        """Test layer classification by naming conventions."""
        engine = CADLayerIntelligence()

        # Test fire safety layer classification
        assert engine._classify_layer("E-FIRE") == LayerClassification.FIRE_SAFETY
        assert engine._classify_layer("SPRINKLER") == LayerClassification.FIRE_SAFETY
        assert engine._classify_layer("SMOKE-DETECTOR") == LayerClassification.FIRE_SAFETY

        # Test electrical layer classification
        assert engine._classify_layer("E-LITE") == LayerClassification.ELECTRICAL
        assert engine._classify_layer("ELECTRICAL") == LayerClassification.ELECTRICAL

        # Test architectural layer classification
        assert engine._classify_layer("A-WALL") == LayerClassification.ARCHITECTURAL
        assert engine._classify_layer("DOOR") == LayerClassification.ARCHITECTURAL

        # Test structural layer classification
        assert engine._classify_layer("S-BEAM") == LayerClassification.STRUCTURAL
        assert engine._classify_layer("COLUMN") == LayerClassification.STRUCTURAL

    def test_fire_safety_relevance_assessment(self):
        """Test fire safety relevance assessment."""
        engine = CADLayerIntelligence()

        # Critical layers
        assert engine._assess_fire_safety_relevance("E-FIRE") == "critical"
        assert engine._assess_fire_safety_relevance("SPRINKLER") == "critical"

        # Important layers
        assert engine._assess_fire_safety_relevance("E-LITE") == "important"
        assert engine._assess_fire_safety_relevance("ELECTRICAL") == "important"

        # Contextual layers
        assert engine._assess_fire_safety_relevance("A-WALL") == "contextual"
        assert engine._assess_fire_safety_relevance("DOOR") == "contextual"

        # Minimal layers
        assert engine._assess_fire_safety_relevance("NOTES") == "minimal"

    def test_device_classification_by_block(self):
        """Test device classification based on block names."""
        engine = CADLayerIntelligence()

        # Smoke detectors
        assert engine._classify_device_by_block("SMOKE-DETECTOR") == "smoke_detector"
        assert engine._classify_device_by_block("SD-TYPE-A") == "smoke_detector"

        # Sprinklers
        assert engine._classify_device_by_block("SPRINKLER-HEAD") == "sprinkler_head"
        assert engine._classify_device_by_block("SPKR-UPRIGHT") == "sprinkler_head"

        # Pull stations
        assert engine._classify_device_by_block("PULL-STATION") == "manual_pull_station"
        assert engine._classify_device_by_block("MPS-WALL") == "manual_pull_station"

        # Horn strobes
        assert engine._classify_device_by_block("HORN-STROBE") == "horn_strobe"
        assert engine._classify_device_by_block("HS-CEILING") == "horn_strobe"

        # Unknown devices
        assert engine._classify_device_by_block("UNKNOWN-BLOCK") == "unknown_device"

    def test_is_fire_safety_layer(self):
        """Test fire safety layer detection."""
        engine = CADLayerIntelligence()

        # Fire safety layers
        assert engine._is_fire_safety_layer("E-FIRE") is True
        assert engine._is_fire_safety_layer("SMOKE-DETECTOR") is True
        assert engine._is_fire_safety_layer("SPRINKLER") is True
        assert engine._is_fire_safety_layer("FIRE-ALARM") is True

        # Non-fire safety layers
        assert engine._is_fire_safety_layer("A-WALL") is False
        assert engine._is_fire_safety_layer("NOTES") is False
        assert engine._is_fire_safety_layer("DIMENSIONS") is False

    def test_aia_standards_loaded(self):
        """Test that AIA standards are properly loaded."""
        engine = CADLayerIntelligence()

        standards = engine._load_aia_standards()

        # Check some key standards exist
        assert "A-WALL" in standards
        assert "E-FIRE" in standards
        assert "E-SPKR" in standards
        assert "M-HVAC" in standards

        # Check structure
        assert "description" in standards["A-WALL"]
        assert "discipline" in standards["A-WALL"]

    def test_device_mappings_loaded(self):
        """Test that device mappings are properly loaded."""
        engine = CADLayerIntelligence()

        mappings = engine._load_device_mappings()

        # Check device types exist
        assert "smoke_detector" in mappings
        assert "sprinkler_head" in mappings
        assert "manual_pull_station" in mappings
        assert "horn_strobe" in mappings

        # Check keywords
        assert "SMOKE" in mappings["smoke_detector"]
        assert "SPRINKLER" in mappings["sprinkler_head"]

    def test_availability_check(self):
        """Test availability checking."""
        engine = CADLayerIntelligence()

        # Should return a boolean
        available = engine.is_available()
        assert isinstance(available, bool)

        # Should match module-level constant
        assert available == EZDXF_AVAILABLE

    def test_cad_device_dataclass(self):
        """Test CADDevice dataclass."""
        device = CADDevice(
            device_type="smoke_detector",
            coordinates=(100.0, 200.0),
            block_name="SD-TYPE-A",
            layer_name="E-FIRE",
            rotation=45.0,
            scale_x=1.5,
            scale_y=1.5,
        )

        assert device.device_type == "smoke_detector"
        assert device.coordinates == (100.0, 200.0)
        assert device.block_name == "SD-TYPE-A"
        assert device.layer_name == "E-FIRE"
        assert device.rotation == 45.0
        assert device.scale_x == 1.5

    def test_layer_info_dataclass(self):
        """Test LayerInfo dataclass."""
        layer_info = LayerInfo(
            name="E-FIRE",
            element_count=12,
            color=1,
            line_weight=0.25,
            classification=LayerClassification.FIRE_SAFETY,
            fire_safety_relevance="critical",
            is_frozen=False,
            is_off=False,
        )

        assert layer_info.name == "E-FIRE"
        assert layer_info.element_count == 12
        assert layer_info.classification == LayerClassification.FIRE_SAFETY
        assert layer_info.fire_safety_relevance == "critical"
        assert layer_info.is_frozen is False

    def test_aia_compliance_check(self):
        """Test AIA compliance checking."""
        engine = CADLayerIntelligence()

        # Standard layer should be compliant
        result = engine._check_aia_compliance("E-FIRE")
        assert result["compliant"] is True

        # Non-standard layer should not be compliant
        result = engine._check_aia_compliance("MY-CUSTOM-LAYER")
        assert result["compliant"] is False

    @pytest.mark.skipif(not EZDXF_AVAILABLE, reason="ezdxf not installed")
    def test_analyze_cad_file_with_invalid_path(self):
        """Test analyzing CAD file with invalid path."""
        engine = CADLayerIntelligence()

        result = engine.analyze_cad_file_layers("nonexistent_file.dxf")

        # Should return error dict
        assert "error" in result

    @pytest.mark.skipif(not EZDXF_AVAILABLE, reason="ezdxf not installed")
    def test_extract_fire_devices_with_invalid_path(self):
        """Test extracting fire devices with invalid path."""
        engine = CADLayerIntelligence()

        devices = engine.extract_precise_fire_devices("nonexistent_file.dxf")

        # Should return empty list on error
        assert isinstance(devices, list)
        assert len(devices) == 0


class TestLayerIntelligenceIntegration:
    """Test layer intelligence integration functions."""

    def test_enhance_autofire_without_ezdxf(self, monkeypatch):
        """Test enhancement function when ezdxf is not available."""
        # Import the function
        from cad_core.intelligence.layer_intelligence import enhance_autofire_with_layer_intelligence

        # Mock EZDXF_AVAILABLE to False
        import cad_core.intelligence.layer_intelligence as module
        original_available = module.EZDXF_AVAILABLE
        module.EZDXF_AVAILABLE = False

        try:
            autofire_results = {"devices": [], "method": "visual"}
            result = enhance_autofire_with_layer_intelligence("test.dxf", autofire_results)

            # Should include original results
            assert "devices" in result
            assert "method" in result

            # Should include layer intelligence error
            assert "layer_intelligence" in result
            assert "error" in result["layer_intelligence"]
        finally:
            # Restore original value
            module.EZDXF_AVAILABLE = original_available


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
