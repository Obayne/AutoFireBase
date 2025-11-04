"""
Tests for AutoFire Visual Processing Pipeline.
"""

from unittest.mock import MagicMock, patch

import numpy as np

from autofire_visual_processor import (
    AutoFireVisualProcessor,
    DetectedScale,
    Room,
    VisualAnalysisResult,
    Wall,
)


class TestAutoFireVisualProcessor:
    """Test suite for AutoFireVisualProcessor class."""

    def test_init(self):
        """Test processor initialization."""
        processor = AutoFireVisualProcessor()
        assert processor.debug_mode is True

    def test_detect_walls_empty_image(self):
        """Test wall detection with empty image."""
        processor = AutoFireVisualProcessor()
        # Create a blank white image
        blank_image = np.ones((500, 500, 3), dtype=np.uint8) * 255
        walls = processor.detect_walls(blank_image)
        # Blank image should have no walls
        assert isinstance(walls, list)

    def test_detect_walls_simple_lines(self):
        """Test wall detection with simple horizontal and vertical lines."""
        processor = AutoFireVisualProcessor()
        # Create image with horizontal and vertical lines
        image = np.ones((500, 500, 3), dtype=np.uint8) * 255
        # Draw a horizontal line (black)
        image[250, 100:400] = [0, 0, 0]
        # Draw a vertical line (black)
        image[100:400, 250] = [0, 0, 0]

        walls = processor.detect_walls(image)
        # Should detect some wall-like features
        assert isinstance(walls, list)
        # Walls should have expected structure
        for wall in walls:
            assert isinstance(wall, Wall)
            assert hasattr(wall, "start_point")
            assert hasattr(wall, "end_point")
            assert hasattr(wall, "confidence")

    def test_detect_rooms_basic(self):
        """Test room detection."""
        processor = AutoFireVisualProcessor()
        # Create a simple image
        image = np.ones((500, 500, 3), dtype=np.uint8) * 255
        walls = []  # Empty wall list for basic test

        rooms = processor.detect_rooms(image, walls)
        assert isinstance(rooms, list)
        # Verify room structure if any detected
        for room in rooms:
            assert isinstance(room, Room)
            assert hasattr(room, "id")
            assert hasattr(room, "name")
            assert hasattr(room, "area_sq_ft")
            assert hasattr(room, "center_point")
            assert hasattr(room, "confidence")

    def test_detect_scale_returns_default(self):
        """Test scale detection returns default scale."""
        processor = AutoFireVisualProcessor()
        image = np.ones((500, 500, 3), dtype=np.uint8) * 255

        scale = processor.detect_scale(image)
        assert isinstance(scale, DetectedScale)
        assert scale.scale_ratio == 48.0
        assert '1/4"' in scale.scale_text
        assert 0 <= scale.confidence <= 1.0

    @patch("autofire_visual_processor.fitz")
    def test_process_pdf_page_to_image_success(self, mock_fitz):
        """Test successful PDF to image conversion."""
        processor = AutoFireVisualProcessor()

        # Mock PyMuPDF document and page
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_pixmap = MagicMock()

        # Create a small test image
        test_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        import io

        from PIL import Image

        pil_img = Image.fromarray(test_image)
        img_bytes = io.BytesIO()
        pil_img.save(img_bytes, format="PPM")

        mock_pixmap.tobytes.return_value = img_bytes.getvalue()
        mock_page.get_pixmap.return_value = mock_pixmap
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz.open.return_value = mock_doc

        result = processor.process_pdf_page_to_image("test.pdf", 0)

        assert result is not None
        assert isinstance(result, np.ndarray)
        mock_fitz.open.assert_called_once_with("test.pdf")
        mock_doc.close.assert_called_once()

    @patch("autofire_visual_processor.fitz")
    def test_process_pdf_page_to_image_error(self, mock_fitz):
        """Test PDF conversion handles errors gracefully."""
        processor = AutoFireVisualProcessor()
        mock_fitz.open.side_effect = Exception("PDF error")

        result = processor.process_pdf_page_to_image("bad.pdf", 0)
        assert result is None

    def test_save_debug_image_creates_file(self, tmp_path):
        """Test debug image saving."""
        processor = AutoFireVisualProcessor()
        processor.debug_mode = True

        # Create test image and analysis
        image = np.ones((500, 500, 3), dtype=np.uint8) * 255
        analysis = VisualAnalysisResult(
            rooms=[
                Room(
                    id="R1",
                    name="Test Room",
                    boundaries=[(100, 100), (200, 100), (200, 200), (100, 200)],
                    area_sq_ft=100.0,
                    center_point=(150, 150),
                    doors=[],
                    windows=[],
                    confidence=0.8,
                )
            ],
            walls=[
                Wall(
                    start_point=(100, 100),
                    end_point=(200, 100),
                    thickness=2.0,
                    wall_type="interior",
                    confidence=0.7,
                )
            ],
            scale=None,
            total_area_sq_ft=100.0,
            drawing_bounds=(0, 0, 500, 500),
            processing_notes=["Test note"],
        )

        debug_file = tmp_path / "test_debug.jpg"
        processor.save_debug_image(image, analysis, str(debug_file))

        # Verify file was created
        assert debug_file.exists()

    def test_save_debug_image_disabled(self, tmp_path):
        """Test debug image saving when debug mode is disabled."""
        processor = AutoFireVisualProcessor()
        processor.debug_mode = False

        image = np.ones((500, 500, 3), dtype=np.uint8) * 255
        analysis = VisualAnalysisResult(
            rooms=[],
            walls=[],
            scale=None,
            total_area_sq_ft=0.0,
            drawing_bounds=(0, 0, 500, 500),
            processing_notes=[],
        )

        debug_file = tmp_path / "test_debug.jpg"
        processor.save_debug_image(image, analysis, str(debug_file))

        # File should not be created when debug is disabled
        assert not debug_file.exists()


class TestDataClasses:
    """Test data classes used in visual processing."""

    def test_room_dataclass(self):
        """Test Room dataclass."""
        room = Room(
            id="R1",
            name="Conference Room",
            boundaries=[(0, 0), (10, 0), (10, 10), (0, 10)],
            area_sq_ft=150.0,
            center_point=(5, 5),
            doors=[(2, 0)],
            windows=[(8, 10)],
            confidence=0.9,
        )

        assert room.id == "R1"
        assert room.name == "Conference Room"
        assert len(room.boundaries) == 4
        assert room.area_sq_ft == 150.0
        assert room.confidence == 0.9

    def test_wall_dataclass(self):
        """Test Wall dataclass."""
        wall = Wall(
            start_point=(0, 0),
            end_point=(10, 0),
            thickness=6.0,
            wall_type="exterior",
            confidence=0.85,
        )

        assert wall.start_point == (0, 0)
        assert wall.end_point == (10, 0)
        assert wall.thickness == 6.0
        assert wall.wall_type == "exterior"
        assert wall.confidence == 0.85

    def test_detected_scale_dataclass(self):
        """Test DetectedScale dataclass."""
        scale = DetectedScale(
            scale_ratio=48.0, scale_text='1/4" = 1\'-0"', confidence=0.9, location=(100, 100)
        )

        assert scale.scale_ratio == 48.0
        assert "1/4" in scale.scale_text
        assert scale.confidence == 0.9
        assert scale.location == (100, 100)

    def test_visual_analysis_result_dataclass(self):
        """Test VisualAnalysisResult dataclass."""
        result = VisualAnalysisResult(
            rooms=[],
            walls=[],
            scale=DetectedScale(48.0, '1/4" = 1\'-0"', 0.9, (100, 100)),
            total_area_sq_ft=500.0,
            drawing_bounds=(0, 0, 1000, 800),
            processing_notes=["Processed successfully"],
        )

        assert result.total_area_sq_ft == 500.0
        assert result.drawing_bounds == (0, 0, 1000, 800)
        assert len(result.processing_notes) == 1
        assert result.scale.scale_ratio == 48.0
