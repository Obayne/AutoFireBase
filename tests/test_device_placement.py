"""
Tests for AutoFire Device Placement Engine.
"""

from unittest.mock import MagicMock, patch

import numpy as np

from autofire_device_placement import (
    AutoFireDevicePlacementEngine,
    DevicePlacement,
    FireAlarmDesign,
)
from autofire_visual_processor import Room, VisualAnalysisResult


class TestAutoFireDevicePlacementEngine:
    """Test suite for AutoFireDevicePlacementEngine class."""

    def test_init(self):
        """Test engine initialization."""
        engine = AutoFireDevicePlacementEngine()
        assert engine.SMOKE_DETECTOR_MAX_SPACING == 30
        assert engine.SMOKE_DETECTOR_MAX_AREA == 900
        assert engine.HORN_STROBE_MAX_SPACING == 50
        assert engine.MANUAL_PULL_MAX_DISTANCE == 200

    def test_place_smoke_detectors_small_room(self):
        """Test smoke detector placement for small room."""
        engine = AutoFireDevicePlacementEngine()

        # Small room under 900 sq ft should get 1 detector
        detectors = engine.place_smoke_detectors(
            center_x=250, center_y=250, width_ft=20, height_ft=20, area_sq_ft=400
        )

        assert len(detectors) == 1
        assert detectors[0].device_type == "Smoke Detector"
        assert detectors[0].coverage_radius_ft == 15.0
        assert "NFPA 72" in detectors[0].nfpa_rule
        assert 0 <= detectors[0].confidence <= 1.0

    def test_place_smoke_detectors_large_room(self):
        """Test smoke detector placement for large room."""
        engine = AutoFireDevicePlacementEngine()

        # Large room over 900 sq ft should get multiple detectors
        detectors = engine.place_smoke_detectors(
            center_x=500, center_y=500, width_ft=50, height_ft=50, area_sq_ft=2500
        )

        # Should place multiple detectors based on area
        assert len(detectors) >= 2
        for detector in detectors:
            assert detector.device_type == "Smoke Detector"
            assert "NFPA 72" in detector.nfpa_rule

    def test_place_horn_strobes_small_room(self):
        """Test horn/strobe placement for small room."""
        engine = AutoFireDevicePlacementEngine()

        # Small room should not get horn/strobe
        horn_strobes = engine.place_horn_strobes(
            center_x=250, center_y=250, width_ft=15, height_ft=15, area_sq_ft=225
        )

        assert len(horn_strobes) == 0

    def test_place_horn_strobes_large_room(self):
        """Test horn/strobe placement for large room."""
        engine = AutoFireDevicePlacementEngine()

        # Large room should get horn/strobe
        horn_strobes = engine.place_horn_strobes(
            center_x=500, center_y=500, width_ft=30, height_ft=30, area_sq_ft=900
        )

        assert len(horn_strobes) == 1
        assert horn_strobes[0].device_type == "Horn/Strobe"
        assert horn_strobes[0].coverage_radius_ft == 25.0
        assert "NFPA 72" in horn_strobes[0].nfpa_rule

    def test_place_manual_pull_stations(self):
        """Test manual pull station placement."""
        engine = AutoFireDevicePlacementEngine()

        # Test with typical room boundaries
        room_boundaries = [(100, 100), (400, 100), (400, 300), (100, 300)]

        pull_stations = engine.place_manual_pull_stations(room_boundaries)

        assert len(pull_stations) == 1
        assert pull_stations[0].device_type == "Manual Pull Station"
        assert pull_stations[0].coverage_radius_ft == 200.0
        assert "NFPA 72" in pull_stations[0].nfpa_rule

    def test_place_manual_pull_stations_insufficient_boundaries(self):
        """Test pull station placement with insufficient boundaries."""
        engine = AutoFireDevicePlacementEngine()

        # Test with too few boundary points
        room_boundaries = [(100, 100), (200, 100)]

        pull_stations = engine.place_manual_pull_stations(room_boundaries)

        # Should handle gracefully
        assert isinstance(pull_stations, list)

    def test_calculate_optimal_device_placement(self):
        """Test optimal device placement calculation for a room."""
        engine = AutoFireDevicePlacementEngine()

        # Create a mock room
        room = Room(
            id="R1",
            name="Test Room",
            boundaries=[(100, 100), (500, 100), (500, 400), (100, 400)],
            area_sq_ft=600.0,
            center_point=(300, 250),
            doors=[],
            windows=[],
            confidence=0.8,
        )

        placements = engine.calculate_optimal_device_placement(room)

        # Should have smoke detectors and pull stations
        assert len(placements) > 0

        # Check device types
        device_types = [p.device_type for p in placements]
        assert "Smoke Detector" in device_types

        # All placements should have proper structure
        for placement in placements:
            assert isinstance(placement, DevicePlacement)
            assert placement.device_type in [
                "Smoke Detector",
                "Horn/Strobe",
                "Manual Pull Station",
            ]
            assert placement.coverage_radius_ft > 0
            assert "NFPA 72" in placement.nfpa_rule
            assert len(placement.reasoning) > 0

    def test_design_fire_alarm_system(self):
        """Test complete fire alarm system design."""
        engine = AutoFireDevicePlacementEngine()

        # Create mock visual analysis
        visual_analysis = VisualAnalysisResult(
            rooms=[
                Room(
                    id="R1",
                    name="Room 1",
                    boundaries=[(100, 100), (500, 100), (500, 400), (100, 400)],
                    area_sq_ft=600.0,
                    center_point=(300, 250),
                    doors=[],
                    windows=[],
                    confidence=0.8,
                ),
                Room(
                    id="R2",
                    name="Room 2",
                    boundaries=[(600, 100), (900, 100), (900, 400), (600, 400)],
                    area_sq_ft=450.0,
                    center_point=(750, 250),
                    doors=[],
                    windows=[],
                    confidence=0.7,
                ),
            ],
            walls=[],
            scale=None,
            total_area_sq_ft=1050.0,
            drawing_bounds=(0, 0, 1000, 500),
            processing_notes=["Test analysis"],
        )

        designs = engine.design_fire_alarm_system(visual_analysis)

        assert len(designs) == 2
        for design in designs:
            assert isinstance(design, FireAlarmDesign)
            assert design.room_area_sq_ft > 0
            assert len(design.device_placements) > 0
            assert design.total_devices > 0
            assert design.nfpa_compliance in ["Compliant", "Non-compliant"]
            assert len(design.design_notes) > 0

    @patch("autofire_device_placement.AutoFireVisualProcessor")
    @patch("autofire_device_placement.cv2.imwrite")
    def test_create_device_placement_image(self, mock_imwrite, mock_processor_class):
        """Test device placement image creation."""
        engine = AutoFireDevicePlacementEngine()

        # Mock processor and image
        mock_processor = MagicMock()
        mock_image = np.ones((500, 500, 3), dtype=np.uint8) * 255
        mock_processor.process_pdf_page_to_image.return_value = mock_image
        mock_processor_class.return_value = mock_processor

        # Create test designs
        designs = [
            FireAlarmDesign(
                room_name="Test Room",
                room_area_sq_ft=500.0,
                device_placements=[
                    DevicePlacement(
                        device_type="Smoke Detector",
                        x_coordinate=250.0,
                        y_coordinate=250.0,
                        coverage_radius_ft=15.0,
                        nfpa_rule="NFPA 72: 7.6.3.2.3",
                        reasoning="Test placement",
                        confidence=0.9,
                    )
                ],
                total_devices=1,
                nfpa_compliance="Compliant",
                design_notes=["Test note"],
            )
        ]

        result = engine.create_device_placement_image("test.pdf", 0, designs)

        # Should create an image file
        assert mock_imwrite.called
        assert result is not None
        assert ".jpg" in result

    @patch("autofire_device_placement.AutoFireVisualProcessor")
    def test_create_device_placement_image_no_image(self, mock_processor_class):
        """Test device placement image creation when PDF processing fails."""
        engine = AutoFireDevicePlacementEngine()

        # Mock processor to return None
        mock_processor = MagicMock()
        mock_processor.process_pdf_page_to_image.return_value = None
        mock_processor_class.return_value = mock_processor

        designs = []
        result = engine.create_device_placement_image("bad.pdf", 0, designs)

        # Should handle gracefully
        assert result is None


class TestDevicePlacementDataClasses:
    """Test data classes for device placement."""

    def test_device_placement_dataclass(self):
        """Test DevicePlacement dataclass."""
        placement = DevicePlacement(
            device_type="Smoke Detector",
            x_coordinate=150.0,
            y_coordinate=200.0,
            coverage_radius_ft=15.0,
            nfpa_rule="NFPA 72: 7.6.3.2.3",
            reasoning="Centered in room for optimal coverage",
            confidence=0.9,
        )

        assert placement.device_type == "Smoke Detector"
        assert placement.x_coordinate == 150.0
        assert placement.y_coordinate == 200.0
        assert placement.coverage_radius_ft == 15.0
        assert "NFPA 72" in placement.nfpa_rule
        assert len(placement.reasoning) > 0
        assert placement.confidence == 0.9

    def test_fire_alarm_design_dataclass(self):
        """Test FireAlarmDesign dataclass."""
        design = FireAlarmDesign(
            room_name="Conference Room",
            room_area_sq_ft=800.0,
            device_placements=[
                DevicePlacement(
                    device_type="Smoke Detector",
                    x_coordinate=100.0,
                    y_coordinate=100.0,
                    coverage_radius_ft=15.0,
                    nfpa_rule="NFPA 72: 7.6.3.2.3",
                    reasoning="Test",
                    confidence=0.9,
                )
            ],
            total_devices=2,
            nfpa_compliance="Compliant",
            design_notes=["NFPA 72 compliant", "All areas covered"],
        )

        assert design.room_name == "Conference Room"
        assert design.room_area_sq_ft == 800.0
        assert len(design.device_placements) == 1
        assert design.total_devices == 2
        assert design.nfpa_compliance == "Compliant"
        assert len(design.design_notes) == 2
