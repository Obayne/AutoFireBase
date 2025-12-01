import pytest
from unittest.mock import Mock
from PySide6 import QtCore, QtWidgets

from app.tools.trim_tool import TrimTool, _intersection_point, _nearest_line_item


class TestTrimTool:
    """Test trim tool functionality."""

    def test_trim_tool_init(self):
        """Test TrimTool initialization."""
        mock_window = Mock()
        tool = TrimTool(mock_window)

        assert tool.win == mock_window
        assert tool.active is False
        assert tool.cut_item is None

    def test_start(self):
        """Test starting trim tool."""
        mock_window = Mock()
        tool = TrimTool(mock_window)

        tool.start()

        assert tool.active is True
        assert tool.cut_item is None
        mock_window.statusBar().showMessage.assert_called_with("Trim: click cutting line, then target line to trim")

    def test_cancel(self):
        """Test canceling trim tool."""
        mock_window = Mock()
        tool = TrimTool(mock_window)
        tool.start()
        tool.cut_item = Mock()  # Simulate having a cut item

        tool.cancel()

        assert tool.active is False
        assert tool.cut_item is None

    def test_on_click_no_active(self):
        """Test click when tool is not active."""
        mock_window = Mock()
        tool = TrimTool(mock_window)

        result = tool.on_click(QtCore.QPointF(10, 20))

        assert result is False

    def test_on_click_no_line_found(self):
        """Test click when no line is found near click point."""
        mock_window = Mock()
        mock_scene = Mock()
        mock_scene.items.return_value = []  # No items
        mock_window.scene = mock_scene
        tool = TrimTool(mock_window)
        tool.start()

        result = tool.on_click(QtCore.QPointF(10, 20))

        assert result is False
        mock_window.statusBar().showMessage.assert_called_with("Trim: no line here")

    def test_on_click_select_cut_line(self):
        """Test selecting the cutting line."""
        mock_window = Mock()
        mock_scene = Mock()
        mock_line_item = Mock(spec=QtWidgets.QGraphicsLineItem)
        mock_scene.items.return_value = [mock_line_item]
        mock_window.scene = mock_scene
        tool = TrimTool(mock_window)
        tool.start()

        result = tool.on_click(QtCore.QPointF(10, 20))

        assert result is False
        assert tool.cut_item == mock_line_item
        mock_window.statusBar().showMessage.assert_called_with("Trim: now click target line to trim")

    def test_intersection_point_basic(self):
        """Test basic line intersection calculation."""
        l1 = QtCore.QLineF(0, 0, 10, 10)
        l2 = QtCore.QLineF(0, 10, 10, 0)

        ip = _intersection_point(l1, l2)

        assert ip is not None
        assert abs(ip.x() - 5.0) < 1e-6
        assert abs(ip.y() - 5.0) < 1e-6

    def test_intersection_point_parallel(self):
        """Test intersection of parallel lines."""
        l1 = QtCore.QLineF(0, 0, 10, 0)
        l2 = QtCore.QLineF(0, 5, 10, 5)

        ip = _intersection_point(l1, l2)

        assert ip is None

    def test_nearest_line_item_found(self):
        """Test finding nearest line item."""
        mock_scene = Mock()
        mock_line_item = Mock(spec=QtWidgets.QGraphicsLineItem)
        mock_scene.items.return_value = [mock_line_item]

        result = _nearest_line_item(mock_scene, QtCore.QPointF(10, 20))

        assert result == mock_line_item

    def test_nearest_line_item_not_found(self):
        """Test when no line item is found."""
        mock_scene = Mock()
        mock_scene.items.return_value = [Mock()]  # Non-line item

        result = _nearest_line_item(mock_scene, QtCore.QPointF(10, 20))

        assert result is None