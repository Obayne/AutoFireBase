# Frontend Tools Registry

This document describes the enhanced tool registry system for AutoFireBase, which provides centralized tool management with automatic shortcuts and CAD core integration.

## Overview

The enhanced tool registry system provides:

- **Centralized Tool Management**: All tools defined in one place with metadata
- **Automatic Shortcut Registration**: Keyboard shortcuts automatically wired
- **CAD Core Integration**: Tools call into `cad_core` for geometry operations  
- **Category Organization**: Tools organized by function (drawing, modify, view, etc.)
- **Extensible Architecture**: Easy to add new tools and customize behavior

## Architecture

### Core Components

1. **ToolSpec**: Dataclass defining tool metadata (name, shortcut, handler, etc.)
2. **ToolRegistry**: Central registry for storing and retrieving tools
3. **ToolManager**: High-level interface for integrating with main application
4. **Tool Definitions**: Pre-defined tools for standard CAD operations

### Key Features

- **No Geometry Logic in UI**: All CAD operations delegate to `cad_core` modules
- **Automatic Menu Generation**: Menus created automatically from tool categories
- **Keyboard Shortcut Management**: Shortcuts installed and managed centrally
- **Command Line Integration**: Tools accessible via command line interface

## Usage

### Basic Integration

```python
from frontend import integrate_tool_registry, add_registry_command_support

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # ... existing initialization ...
        
        # Integrate enhanced tool registry
        self.tool_manager = integrate_tool_registry(self)
        
        # Add command line support for registry tools
        add_registry_command_support(self)
        
        # ... rest of initialization ...
```

### Tool Categories

#### Drawing Tools
- **Line (L)**: Draw lines using CAD core line algorithms
- **Rectangle (R)**: Draw rectangles  
- **Circle (C)**: Draw circles
- **Polyline (P)**: Draw connected line segments
- **Arc (A)**: Draw arcs through three points
- **Wire (W)**: Draw electrical wiring

#### Modify Tools (CAD Core Integration)
- **Trim (TR)**: Trim lines using `cad_core.trim_line_to_boundary`
- **Extend (EX)**: Extend lines using `cad_core.extend_line_to_boundary` 
- **Fillet (F)**: Create fillets using `cad_core.fillet_two_lines`
- **Offset (O)**: Create parallel copies
- **Move, Copy, Rotate, Mirror, Scale**: Standard CAD transformations

#### View Tools
- **Grid**: Toggle grid display
- **Snap**: Toggle snap to grid/objects
- **Crosshair (X)**: Toggle crosshair cursor
- **Fit View (F2)**: Fit all content in view

#### Annotation Tools
- **Dimension (D)**: Add dimension annotations
- **Text (T)**: Add text annotations
- **Measure (M)**: Measure distances and areas

### Advanced Usage

#### Creating Custom Tools

```python
from frontend.tool_registry import ToolSpec, register

# Define a custom tool
custom_tool = ToolSpec(
    name="Custom Operation",
    command="custom_op",
    shortcut="Ctrl+K",
    tooltip="Perform custom operation",
    category="custom",
    handler=lambda mw: my_custom_function(mw)
)

# Register the tool
register(custom_tool)
```

#### Tool Manager API

```python
# Get tool manager instance
tool_manager = self.tool_manager

# Execute tool by command
tool_manager.execute_command("draw_line")

# Get tools by category
drawing_tools = tool_manager.get_tools_by_category("drawing")

# Get available commands
commands = tool_manager.get_available_commands()
```

## CAD Core Integration

The tool registry system is designed to work with the enhanced CAD core:

### Trim/Extend Operations
```python
# Tools automatically call CAD core functions
from cad_core import trim_line_to_boundary, extend_line_to_boundary

# trim tool handler calls:
result = trim_line_to_boundary(selected_line, boundary_line, end="b")
```

### Fillet Operations  
```python
# Fillet tools use CAD core algorithms
from cad_core import fillet_two_lines

# fillet tool handler calls:
result = fillet_two_lines(line1, line2, radius)
```

### Pure Function Architecture
- **No Side Effects**: CAD core functions are pure - no UI dependencies
- **Testable**: All geometry operations can be unit tested
- **Reusable**: Core algorithms can be used in different contexts

## Testing

The tool registry includes comprehensive tests:

```bash
# Run tool registry tests
python -m pytest tests/frontend/test_tool_registry.py -v

# Run CAD core tests (verify integration)
python -m pytest tests/cad_core/test_trim_extend.py -v
```

## Benefits

### For Users
- **Consistent Interface**: All tools work the same way
- **Keyboard Shortcuts**: Efficient CAD-style shortcuts (L for line, etc.)
- **Command Line**: Type commands like traditional CAD systems

### For Developers
- **Clean Architecture**: Clear separation between UI and geometry logic
- **Easy Extension**: Add new tools by defining ToolSpec objects
- **Centralized Management**: All tool metadata in one place
- **Type Safety**: Full type annotations and IDE support

### For Testing
- **Unit Testable**: Core algorithms can be tested independently
- **Mock Friendly**: UI can be mocked for isolated testing
- **Behavior Verification**: Tool behavior can be verified programmatically

## Migration Guide

The enhanced tool registry can be integrated gradually:

1. **Phase 1**: Install alongside existing tools (no conflicts)
2. **Phase 2**: Migrate individual tools to use registry
3. **Phase 3**: Remove legacy tool definitions

Current implementation supports both systems running simultaneously.

## Future Enhancements

- **Tool Icons**: Add icon support to ToolSpec
- **Tool Groups**: Group related tools in UI
- **Custom Shortcuts**: User-configurable keyboard shortcuts
- **Tool Scripts**: Support for scripted/macro tools
- **Plugin System**: Load tools from external plugins

## Conclusion

The enhanced tool registry provides a solid foundation for CAD tool management in AutoFireBase, with clean architecture, comprehensive testing, and integration with the CAD core geometry engine.