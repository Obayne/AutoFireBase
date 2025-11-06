from unittest.mock import Mock

from PySide6 import QtCore, QtWidgets

from app import main as app_main
from app.main import CanvasView

# Enable debug logging in app.main for these tests so diagnostic
# messages from _compute_osnap are visible during failures.
app_main._logger.setLevel(10)


class TestOSNAP:
    """Test OSNAP (Object Snap) functionality."""

    def test_canvas_view_osnap_init(self, qtbot):
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

    def test_compute_osnap_line_endpoints(self, qtbot):
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

        # Create mock line item that returns a real QLineF
        qline = QtCore.QLineF(0.0, 0.0, 10.0, 10.0)
        mock_line_item = Mock()
        mock_line_item.line.return_value = qline

        # Mock scene items
        mock_scene.items.return_value = [mock_line_item]

        # Test point near endpoint
        test_point = QtCore.QPointF(0.5, 0.5)  # Near (0,0) endpoint
        result = view._compute_osnap(test_point)

        # Should find the endpoint
        assert result is not None
        assert abs(result.x() - 0.0) < 1e-6
        assert abs(result.y() - 0.0) < 1e-6

    def test_compute_osnap_circle_center(self, qtbot):
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

        # Create mock ellipse item (circle) returning a rect-like object
        class RectLike:
            def center(self):
                return QtCore.QPointF(5.0, 5.0)

        mock_ellipse_item = Mock()
        mock_ellipse_item.rect.return_value = RectLike()

        # Mock scene items
        mock_scene.items.return_value = [mock_ellipse_item]

        # Test point near center
        test_point = QtCore.QPointF(5.5, 5.5)
        result = view._compute_osnap(test_point)

        # Should find the center
        assert result is not None
        assert abs(result.x() - 5.0) < 1e-6
        assert abs(result.y() - 5.0) < 1e-6

    def test_compute_osnap_line_intersection(self, qtbot):
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

        # Create two mock line items that intersect using real QLineF
        ql1 = QtCore.QLineF(0.0, 0.0, 10.0, 10.0)
        ql2 = QtCore.QLineF(0.0, 10.0, 10.0, 0.0)

        mock_line_item1 = Mock()
        mock_line_item1.line.return_value = ql1
        mock_line_item2 = Mock()
        mock_line_item2.line.return_value = ql2

        # Mock scene items
        mock_scene.items.return_value = [mock_line_item1, mock_line_item2]

        # Test point near intersection (5,5)
        test_point = QtCore.QPointF(5.5, 5.5)
        result = view._compute_osnap(test_point)

        # Should find the intersection
        assert result is not None
        assert abs(result.x() - 5.0) < 1e-6
        assert abs(result.y() - 5.0) < 1e-6

    def test_osnap_disabled(self, qtbot):
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

    def test_osnap_marker_properties(self, qtbot):
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
