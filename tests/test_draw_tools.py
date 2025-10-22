from unittest.mock import Mock, patch

import pytest
from PySide6 import QtCore

from cad_core.tools.draw import DrawController, DrawMode, _circle_from_3pts


@pytest.mark.gui
class TestDrawTools:
    """Test draw tools functionality."""

    def test_draw_mode_enum(self):
        """Test DrawMode enum values."""
        assert DrawMode.NONE == 0
        assert DrawMode.LINE == 1
        assert DrawMode.RECT == 2
        assert DrawMode.CIRCLE == 3
        assert DrawMode.POLYLINE == 4
        assert DrawMode.ARC3 == 5
        assert DrawMode.WIRE == 6

    def test_draw_controller_init(self):
        """Test DrawController initialization."""
        mock_window = Mock()
        mock_layer = Mock()

        controller = DrawController(mock_window, mock_layer)

        assert controller.win == mock_window
        assert controller.layer == mock_layer
        assert controller.mode == DrawMode.NONE
        assert controller.temp_item is None
        assert controller.points == []

    def test_set_mode(self):
        """Test setting draw mode."""
        mock_window = Mock()
        mock_layer = Mock()

        controller = DrawController(mock_window, mock_layer)
        controller.set_mode(DrawMode.LINE)

        assert controller.mode == DrawMode.LINE
        mock_window.statusBar().showMessage.assert_called_once()
        assert "Draw: Line" in mock_window.statusBar().showMessage.call_args[0][0]

    def test_circle_from_3pts_collinear(self):
        """Test circle calculation for collinear points (degenerate case)."""
        a = QtCore.QPointF(0, 0)
        b = QtCore.QPointF(1, 1)
        c = QtCore.QPointF(2, 2)

        cx, cy, r, start, span = _circle_from_3pts(a, b, c)

        # Should return invalid circle (negative radius)
        assert r < 0

    def test_circle_from_3pts_valid(self):
        """Test circle calculation for valid 3 points."""
        # Points forming an equilateral triangle
        a = QtCore.QPointF(0, 0)
        b = QtCore.QPointF(1, 0)
        c = QtCore.QPointF(0.5, 0.866)  # Height of equilateral triangle with side 1

        cx, cy, r, start, span = _circle_from_3pts(a, b, c)

        # Should have valid radius
        assert r > 0
        # Center should be at centroid-ish for equilateral triangle
        assert abs(cx - 0.5) < 0.1  # Approximate center X
        assert abs(cy - 0.2887) < 0.1  # Approximate center Y (1/(2*sqrt(3)))

    def test_add_point_command_no_mode(self):
        """Test add_point_command with no active mode."""
        mock_window = Mock()
        mock_layer = Mock()

        controller = DrawController(mock_window, mock_layer)

        result = controller.add_point_command(QtCore.QPointF(10, 20))

        assert result is False
        assert controller.points == []

    def test_add_point_command_first_point(self):
        """Test add_point_command adding first point."""
        mock_window = Mock()
        mock_layer = Mock()

        controller = DrawController(mock_window, mock_layer)
        controller.set_mode(DrawMode.LINE)

        result = controller.add_point_command(QtCore.QPointF(10, 20))

        assert result is False
        assert len(controller.points) == 1
        assert controller.points[0] == QtCore.QPointF(10, 20)

    @patch("cad_core.tools.draw.QtWidgets.QGraphicsLineItem")
    def test_add_point_command_line_commit(self, mock_line_item):
        """Test add_point_command committing a line."""
        mock_window = Mock()
        mock_layer = Mock()
        mock_item = Mock()
        mock_line_item.return_value = mock_item

        controller = DrawController(mock_window, mock_layer)
        controller.set_mode(DrawMode.LINE)
        controller.add_point_command(QtCore.QPointF(0, 0))  # First point

        result = controller.add_point_command(QtCore.QPointF(10, 20))  # Second point

        assert result is True
        assert controller.mode == DrawMode.NONE  # Should finish after commit
        assert controller.points == []  # Should clear points
        mock_item.setParentItem.assert_called_with(mock_layer)

    @patch("cad_core.tools.draw.QtWidgets.QGraphicsPathItem")
    def test_finish_polyline_commit(self, mock_path_item):
        """Test finishing polyline with multiple points."""
        mock_window = Mock()
        mock_layer = Mock()
        mock_item = Mock()
        mock_path_item.return_value = mock_item

        controller = DrawController(mock_window, mock_layer)
        controller.set_mode(DrawMode.POLYLINE)
        controller.add_point_command(QtCore.QPointF(0, 0))
        controller.add_point_command(QtCore.QPointF(10, 0))
        controller.add_point_command(QtCore.QPointF(10, 10))

        # Finish should commit the polyline
        controller.finish()

        assert controller.mode == DrawMode.NONE
        assert controller.points == []
        mock_item.setParentItem.assert_called_with(mock_layer)

    def test_on_mouse_move_no_points(self):
        """Test mouse move with no points (should do nothing)."""
        mock_window = Mock()
        mock_layer = Mock()

        controller = DrawController(mock_window, mock_layer)
        controller.set_mode(DrawMode.LINE)

        # Should not crash
        controller.on_mouse_move(QtCore.QPointF(10, 20))

        assert controller.temp_item is None

    @patch("cad_core.tools.draw.QtWidgets.QGraphicsLineItem")
    def test_on_mouse_move_creates_temp_line_item(self, mock_line_item):
        """Test that mouse move creates temporary line preview."""
        mock_window = Mock()
        mock_layer = Mock()
        mock_item = Mock()
        mock_line_item.return_value = mock_item

        controller = DrawController(mock_window, mock_layer)
        controller.set_mode(DrawMode.LINE)
        controller.add_point_command(QtCore.QPointF(0, 0))  # Add first point

        controller.on_mouse_move(QtCore.QPointF(10, 20))

        # Should create a temp item
        assert controller.temp_item is not None
        mock_item.setParentItem.assert_called_with(mock_layer)

    @patch("cad_core.tools.draw.QtWidgets.QGraphicsLineItem")
    def test_wire_mode_special_styling(self, mock_line_item):
        """Test that wire mode gets special pen styling."""
        mock_window = Mock()
        mock_layer = Mock()
        mock_item = Mock()
        mock_line_item.return_value = mock_item

        controller = DrawController(mock_window, mock_layer)
        controller.set_mode(DrawMode.WIRE)
        controller.add_point_command(QtCore.QPointF(0, 0))

        controller.on_mouse_move(QtCore.QPointF(10, 20))

        # Check that temp item has wire styling (width 2)
        assert controller.temp_item is not None
        # Verify pen was set with width 2
        mock_item.setPen.assert_called()
        pen_arg = mock_item.setPen.call_args[0][0]
        assert pen_arg.width() == 2
