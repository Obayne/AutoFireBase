from unittest.mock import Mock, patch

import pytest
from PySide6 import QtCore, QtWidgets

from frontend.windows.scene import CanvasView


@pytest.mark.gui
class TestOSNAP:
    """Test OSNAP (Object Snap) functionality."""

    def test_canvas_view_osnap_init(self):
        """Test CanvasView OSNAP initialization."""
        mock_scene = Mock()
        mock_devices = Mock()
        mock_wires = Mock()
        mock_sketch = Mock()
        mock_overlay = Mock()
        mock_window = Mock()

        view = CanvasView(
            mock_scene, mock_devices, mock_wires, mock_sketch, mock_overlay, mock_window
        )

        # Check OSNAP toggles are initialized
        assert view.osnap_end is True
        assert view.osnap_mid is True
        assert view.osnap_center is True
        assert view.osnap_intersect is True
        assert view.osnap_perp is False

        # Check OSNAP marker is created
        assert view.osnap_marker is not None
        assert isinstance(view.osnap_marker, QtWidgets.QGraphicsEllipseItem)

    @patch("frontend.windows.scene.QtWidgets.QGraphicsLineItem")
    def test_compute_osnap_line_endpoints(self, mock_line_item):
        """Test OSNAP finds line endpoints."""
        mock_scene = Mock()
        mock_devices = Mock()
        mock_wires = Mock()
        mock_sketch = Mock()
        mock_overlay = Mock()
        mock_window = Mock()

        view = CanvasView(
            mock_scene, mock_devices, mock_wires, mock_sketch, mock_overlay, mock_window
        )

        # Create mock line item
        mock_line = Mock()
        mock_line.x1.return_value = 0.0
        mock_line.y1.return_value = 0.0
        mock_line.x2.return_value = 10.0
        mock_line.y2.return_value = 10.0
        mock_line_item.line.return_value = mock_line
        mock_line_item.return_value = mock_line_item

        # Mock scene items
        mock_scene.items.return_value = [mock_line_item]

        # Test point near endpoint
        test_point = QtCore.QPointF(0.5, 0.5)  # Near (0,0) endpoint
        result = view._compute_osnap(test_point)

        # Should find the endpoint
        assert result is not None
        assert abs(result.x() - 0.0) < 1e-6
        assert abs(result.y() - 0.0) < 1e-6

    @patch("frontend.windows.scene.QtWidgets.QGraphicsEllipseItem")
    def test_compute_osnap_circle_center(self, mock_ellipse_item):
        """Test OSNAP finds circle centers."""
        mock_scene = Mock()
        mock_devices = Mock()
        mock_wires = Mock()
        mock_sketch = Mock()
        mock_overlay = Mock()
        mock_window = Mock()

        view = CanvasView(
            mock_scene, mock_devices, mock_wires, mock_sketch, mock_overlay, mock_window
        )

        # Create mock ellipse item (circle)
        mock_rect = Mock()
        mock_rect.center.return_value = QtCore.QPointF(5.0, 5.0)
        mock_ellipse_item.rect.return_value = mock_rect

        # Mock scene items
        mock_scene.items.return_value = [mock_ellipse_item]

        # Test point near center
        test_point = QtCore.QPointF(5.5, 5.5)
        result = view._compute_osnap(test_point)

        # Should find the center
        assert result is not None
        assert abs(result.x() - 5.0) < 1e-6
        assert abs(result.y() - 5.0) < 1e-6

    @patch("frontend.windows.scene.QtWidgets.QGraphicsLineItem")
    def test_compute_osnap_line_intersection(self, mock_line_item):
        """Test OSNAP finds line intersections."""
        mock_scene = Mock()
        mock_devices = Mock()
        mock_wires = Mock()
        mock_sketch = Mock()
        mock_overlay = Mock()
        mock_window = Mock()

        view = CanvasView(
            mock_scene, mock_devices, mock_wires, mock_sketch, mock_overlay, mock_window
        )

        # Create two mock line items that intersect
        mock_line1 = Mock()
        mock_line1.x1.return_value = 0.0
        mock_line1.y1.return_value = 0.0
        mock_line1.x2.return_value = 10.0
        mock_line1.y2.return_value = 10.0

        mock_line2 = Mock()
        mock_line2.x1.return_value = 0.0
        mock_line2.y1.return_value = 10.0
        mock_line2.x2.return_value = 10.0
        mock_line2.y2.return_value = 0.0

        mock_line_item1 = Mock()
        mock_line_item1.line.return_value = mock_line1
        mock_line_item2 = Mock()
        mock_line_item2.line.return_value = mock_line2

        # Mock scene items
        mock_scene.items.return_value = [mock_line_item1, mock_line_item2]

        # Test point near intersection (5,5)
        test_point = QtCore.QPointF(5.5, 5.5)
        result = view._compute_osnap(test_point)

        # Should find the intersection
        assert result is not None
        assert abs(result.x() - 5.0) < 1e-6
        assert abs(result.y() - 5.0) < 1e-6

    def test_osnap_disabled(self):
        """Test OSNAP when all snaps are disabled."""
        mock_scene = Mock()
        mock_devices = Mock()
        mock_wires = Mock()
        mock_sketch = Mock()
        mock_overlay = Mock()
        mock_window = Mock()

        view = CanvasView(
            mock_scene, mock_devices, mock_wires, mock_sketch, mock_overlay, mock_window
        )

        # Disable all OSNAP
        view.osnap_end = False
        view.osnap_mid = False
        view.osnap_center = False
        view.osnap_intersect = False
        view.osnap_perp = False

        # Mock empty scene
        mock_scene.items.return_value = []

        test_point = QtCore.QPointF(5.0, 5.0)
        result = view._compute_osnap(test_point)

        # Should return None when no snaps enabled
        assert result is None

    def test_osnap_marker_properties(self):
        """Test OSNAP marker visual properties."""
        mock_scene = Mock()
        mock_devices = Mock()
        mock_wires = Mock()
        mock_sketch = Mock()
        mock_overlay = Mock()
        mock_window = Mock()

        view = CanvasView(
            mock_scene, mock_devices, mock_wires, mock_sketch, mock_overlay, mock_window
        )

        marker = view.osnap_marker

        # Check marker is properly configured
        assert marker.parentItem() == mock_overlay
        assert marker.zValue() == 250
        assert not marker.isVisible()  # Initially hidden

        # Check pen and brush colors (yellow)
        pen = marker.pen()
        brush = marker.brush()
        assert pen.color().name() == "#ffd166"
        assert brush.color().name() == "#ffd166"
