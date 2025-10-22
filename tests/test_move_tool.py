from unittest.mock import Mock

import pytest
from PySide6 import QtCore

from cad_core.tools.move_tool import MoveTool


@pytest.mark.gui
class TestMoveTool:
    """Test move tool functionality."""

    def test_move_tool_init(self):
        """Test MoveTool initialization."""
        mock_window = Mock()
        tool = MoveTool(mock_window)

        assert tool.win == mock_window
        assert tool.active is False
        assert tool.base is None
        assert tool.copy is False

    def test_start_move(self):
        """Test starting move tool."""
        mock_window = Mock()
        tool = MoveTool(mock_window)

        tool.start(copy=False)

        assert tool.active is True
        assert tool.base is None
        assert tool.copy is False
        mock_window.statusBar().showMessage.assert_called_with(
            "Move: click base point, then destination"
        )

    def test_start_copy(self):
        """Test starting copy tool."""
        mock_window = Mock()
        tool = MoveTool(mock_window)

        tool.start(copy=True)

        assert tool.active is True
        assert tool.base is None
        assert tool.copy is True
        mock_window.statusBar().showMessage.assert_called_with(
            "Move: click base point, then destination"
        )

    def test_cancel(self):
        """Test canceling move tool."""
        mock_window = Mock()
        tool = MoveTool(mock_window)
        tool.start()
        tool.base = QtCore.QPointF(10, 20)

        tool.cancel()

        assert tool.active is False
        assert tool.base is None

    def test_on_click_no_active(self):
        """Test click when tool is not active."""
        mock_window = Mock()
        tool = MoveTool(mock_window)

        result = tool.on_click(QtCore.QPointF(10, 20))

        assert result is False

    def test_on_click_set_base_point(self):
        """Test setting base point on first click."""
        mock_window = Mock()
        tool = MoveTool(mock_window)
        tool.start()

        result = tool.on_click(QtCore.QPointF(10, 20))

        assert result is False
        assert tool.base == QtCore.QPointF(10, 20)

    def test_on_click_move_no_selection(self):
        """Test move with no selected items."""
        mock_window = Mock()
        mock_scene = Mock()
        mock_scene.selectedItems.return_value = []
        mock_window.scene = mock_scene
        tool = MoveTool(mock_window)
        tool.start()
        tool.base = QtCore.QPointF(0, 0)

        result = tool.on_click(QtCore.QPointF(10, 20))

        assert result is False
        assert tool.active is False
        assert tool.base is None

    @pytest.mark.parametrize("copy_mode", [False, True])
    def test_on_click_move_selected_items(self, copy_mode):
        """Test moving selected items."""
        mock_window = Mock()
        mock_scene = Mock()
        mock_item = Mock()
        mock_item.pos.return_value = QtCore.QPointF(0, 0)
        mock_scene.selectedItems.return_value = [mock_item]
        mock_window.scene = mock_scene
        tool = MoveTool(mock_window)
        tool.start(copy=copy_mode)
        tool.base = QtCore.QPointF(0, 0)

        result = tool.on_click(QtCore.QPointF(10, 20))

        assert result is True
        assert tool.active is False
        assert tool.base is None

        if copy_mode:
            # In copy mode, should not modify original position
            mock_item.setPos.assert_not_called()
        else:
            # In move mode, should update position
            expected_pos = QtCore.QPointF(10, 20)
            mock_item.setPos.assert_called_with(expected_pos)
