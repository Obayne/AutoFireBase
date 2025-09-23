"""Tests for enhanced tool registry system."""

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow
from frontend.tool_registry import ToolSpec, ToolRegistry, register, get, all_tools
from frontend.tool_manager import ToolManager
from frontend.tool_definitions import register_all_tools


def test_register_and_get_tool():
    """Test basic tool registration and retrieval."""
    spec = ToolSpec(name="Trim", command="trim", shortcut="T")
    register(spec)
    got = get("trim")
    assert got is not None
    assert got.name == "Trim"
    assert all_tools()["trim"].shortcut == "T"


def test_enhanced_tool_spec():
    """Test enhanced ToolSpec with new fields."""
    spec = ToolSpec(
        name="Draw Line",
        command="draw_line",
        shortcut="L",
        tooltip="Draw a line between two points",
        category="drawing",
        checkable=False,
        enabled=True
    )
    
    assert spec.name == "Draw Line"
    assert spec.command == "draw_line"
    assert spec.shortcut == "L"
    assert spec.tooltip == "Draw a line between two points"
    assert spec.category == "drawing"
    assert not spec.checkable
    assert spec.enabled


def test_tool_registry_categories():
    """Test tool registry category functionality."""
    registry = ToolRegistry()
    
    # Register tools in different categories
    line_spec = ToolSpec(name="Line", command="line", category="drawing")
    trim_spec = ToolSpec(name="Trim", command="trim", category="modify")
    
    registry.register(line_spec)
    registry.register(trim_spec)
    
    # Test category retrieval
    drawing_tools = registry.get_category("drawing")
    modify_tools = registry.get_category("modify")
    
    assert len(drawing_tools) == 1
    assert drawing_tools[0].command == "line"
    assert len(modify_tools) == 1
    assert modify_tools[0].command == "trim"
    
    # Test all categories
    categories = registry.all_categories()
    assert "drawing" in categories
    assert "modify" in categories


def test_shortcut_lookup():
    """Test shortcut-based tool lookup."""
    registry = ToolRegistry()
    
    spec = ToolSpec(name="Circle", command="circle", shortcut="C")
    registry.register(spec)
    
    found = registry.get_by_shortcut("C")
    assert found is not None
    assert found.command == "circle"
    
    not_found = registry.get_by_shortcut("Z")
    assert not_found is None


@pytest.fixture
def mock_main_window():
    """Create a mock main window for testing."""
    class MockMainWindow:
        def __init__(self):
            self.layer_sketch = None
            self.draw = MockDrawController()
            self.scene = MockScene()
            self.view = MockView()
    
    class MockDrawController:
        def __init__(self):
            self.layer = None
            self.mode = None
        
        def set_mode(self, mode):
            self.mode = mode
    
    class MockScene:
        def __init__(self):
            self.snap_enabled = True
    
    class MockView:
        def __init__(self):
            self.show_crosshair = True
    
    return MockMainWindow()


def test_tool_definitions_registration():
    """Test that tool definitions are properly registered."""
    # Clear any existing registrations
    from frontend.tool_registry import _REGISTRY
    _REGISTRY._tools.clear()
    _REGISTRY._shortcuts.clear()
    _REGISTRY._categories.clear()
    
    # Register all tools
    register_all_tools()
    
    # Check that drawing tools are registered
    line_tool = get("draw_line")
    assert line_tool is not None
    assert line_tool.shortcut == "L"
    assert line_tool.category == "drawing"
    
    # Check that modify tools are registered
    trim_tool = get("trim")
    assert trim_tool is not None
    assert trim_tool.category == "modify"
    
    # Check that view tools are registered
    grid_tool = get("toggle_grid")
    assert grid_tool is not None
    assert grid_tool.checkable
    assert grid_tool.category == "view"


def test_tool_manager_creation(mock_main_window):
    """Test tool manager creation and basic functionality."""
    tool_manager = ToolManager(mock_main_window)
    
    assert tool_manager.main_window == mock_main_window
    assert tool_manager.registry is not None
    
    # Test command execution
    commands = tool_manager.get_available_commands()
    assert len(commands) > 0
    
    # Test category retrieval
    drawing_tools = tool_manager.get_tools_by_category("drawing")
    assert len(drawing_tools) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

