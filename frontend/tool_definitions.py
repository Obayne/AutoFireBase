"""Tool definitions for AutoFireBase CAD application.

This module defines all standard CAD tools and registers them with the tool registry.
It integrates with CAD core operations for geometry calculations.
"""

from typing import Any, Callable, Optional
from .tool_registry import ToolSpec, register


def create_drawing_tool_handler(mode_name: str, layer_setter: Optional[Callable] = None) -> Callable:
    """Create a handler for drawing tools that sets mode and optionally layer."""
    def handler(main_window: Any) -> None:
        # Import here to avoid circular imports
        from app.tools import draw as draw_tools
        
        if layer_setter:
            layer_setter(main_window)
        
        # Get the DrawMode enum value by name
        mode = getattr(draw_tools.DrawMode, mode_name)
        main_window.draw.set_mode(mode)
    
    return handler


def create_cad_tool_handler(method_name: str) -> Callable:
    """Create a handler for CAD operations that calls main window methods."""
    def handler(main_window: Any) -> None:
        method = getattr(main_window, method_name)
        method()
    
    return handler


def register_drawing_tools():
    """Register all drawing tools."""
    
    def set_sketch_layer(main_window):
        """Helper to set draw controller to sketch layer."""
        main_window.draw.layer = main_window.layer_sketch
    
    # Basic drawing tools
    register(ToolSpec(
        name="Draw Line",
        command="draw_line",
        shortcut="L",
        tooltip="Draw a line between two points",
        category="drawing",
        handler=lambda mw: (set_sketch_layer(mw), create_drawing_tool_handler("LINE")(mw))
    ))
    
    register(ToolSpec(
        name="Draw Rectangle",
        command="draw_rect",
        shortcut="R",
        tooltip="Draw a rectangle by two corners",
        category="drawing",
        handler=lambda mw: (set_sketch_layer(mw), create_drawing_tool_handler("RECT")(mw))
    ))
    
    register(ToolSpec(
        name="Draw Circle",
        command="draw_circle",
        shortcut="C",
        tooltip="Draw a circle by center and radius",
        category="drawing",
        handler=lambda mw: (set_sketch_layer(mw), create_drawing_tool_handler("CIRCLE")(mw))
    ))
    
    register(ToolSpec(
        name="Draw Polyline",
        command="draw_polyline",
        shortcut="P",
        tooltip="Draw a connected series of line segments",
        category="drawing",
        handler=lambda mw: (set_sketch_layer(mw), create_drawing_tool_handler("POLYLINE")(mw))
    ))
    
    register(ToolSpec(
        name="Draw Arc (3-Point)",
        command="draw_arc3",
        shortcut="A",
        tooltip="Draw an arc through three points",
        category="drawing",
        handler=lambda mw: (set_sketch_layer(mw), create_drawing_tool_handler("ARC3")(mw))
    ))
    
    register(ToolSpec(
        name="Draw Wire",
        command="draw_wire",
        shortcut="W",
        tooltip="Draw electrical wiring",
        category="wiring",
        handler=lambda mw: mw._set_wire_mode()
    ))


def register_modify_tools():
    """Register modification/editing tools that use CAD core."""
    
    register(ToolSpec(
        name="Trim Lines",
        command="trim",
        shortcut="TR",
        tooltip="Trim lines to boundaries using CAD core algorithms",
        category="modify",
        handler=lambda mw: mw.start_trim()
    ))
    
    register(ToolSpec(
        name="Extend Lines", 
        command="extend",
        shortcut="EX",
        tooltip="Extend lines to boundaries using CAD core algorithms",
        category="modify",
        handler=lambda mw: mw.start_extend()
    ))
    
    register(ToolSpec(
        name="Fillet (Corner)",
        command="fillet",
        shortcut="F",
        tooltip="Create rounded corners between lines using CAD core",
        category="modify",
        handler=lambda mw: mw.start_fillet()
    ))
    
    register(ToolSpec(
        name="Fillet (Radius)...",
        command="fillet_radius",
        tooltip="Create fillet with specific radius using CAD core",
        category="modify",
        handler=lambda mw: mw.start_fillet_radius()
    ))
    
    register(ToolSpec(
        name="Offset Selected...",
        command="offset",
        shortcut="O",
        tooltip="Create parallel copies at specified distance",
        category="modify",
        handler=lambda mw: mw.offset_selected_dialog()
    ))
    
    register(ToolSpec(
        name="Move",
        command="move",
        shortcut="M",
        tooltip="Move selected objects",
        category="modify", 
        handler=lambda mw: mw.start_move()
    ))
    
    register(ToolSpec(
        name="Copy",
        command="copy",
        shortcut="CP",
        tooltip="Copy selected objects",
        category="modify",
        handler=lambda mw: mw.start_copy()
    ))
    
    register(ToolSpec(
        name="Rotate",
        command="rotate",
        shortcut="RO",
        tooltip="Rotate selected objects",
        category="modify",
        handler=lambda mw: mw.start_rotate()
    ))
    
    register(ToolSpec(
        name="Mirror",
        command="mirror",
        shortcut="MI",
        tooltip="Mirror selected objects",
        category="modify",
        handler=lambda mw: mw.start_mirror()
    ))
    
    register(ToolSpec(
        name="Scale",
        command="scale",
        shortcut="SC",
        tooltip="Scale selected objects",
        category="modify",
        handler=lambda mw: mw.start_scale()
    ))


def register_annotation_tools():
    """Register annotation and measurement tools."""
    
    register(ToolSpec(
        name="Dimension",
        command="dimension",
        shortcut="D",
        tooltip="Add dimension annotations",
        category="annotation",
        handler=lambda mw: mw.start_dimension()
    ))
    
    register(ToolSpec(
        name="Text",
        command="text",
        shortcut="T",
        tooltip="Add single-line text",
        category="annotation",
        handler=lambda mw: mw.start_text()
    ))
    
    register(ToolSpec(
        name="Multiline Text",
        command="mtext",
        tooltip="Add multi-line text",
        category="annotation",
        handler=lambda mw: mw.start_mtext()
    ))
    
    register(ToolSpec(
        name="Measure",
        command="measure",
        shortcut="M",
        tooltip="Measure distances and areas",
        category="annotation",
        handler=lambda mw: mw.start_measure()
    ))
    
    register(ToolSpec(
        name="Leader",
        command="leader",
        tooltip="Add leader lines with text",
        category="annotation", 
        handler=lambda mw: mw.start_leader()
    ))


def register_view_tools():
    """Register view and display tools."""
    
    register(ToolSpec(
        name="Grid",
        command="toggle_grid",
        tooltip="Toggle grid display",
        category="view",
        checkable=True,
        handler=lambda mw: mw.toggle_grid()
    ))
    
    register(ToolSpec(
        name="Snap",
        command="toggle_snap",
        tooltip="Toggle snap to grid/objects",
        category="view",
        checkable=True,
        handler=lambda mw: mw.toggle_snap()
    ))
    
    register(ToolSpec(
        name="Crosshair",
        command="toggle_crosshair",
        shortcut="X",
        tooltip="Toggle crosshair cursor",
        category="view",
        checkable=True,
        handler=lambda mw: mw.toggle_crosshair(not mw.view.show_crosshair)
    ))
    
    register(ToolSpec(
        name="Fit View",
        command="fit_view",
        shortcut="F2",
        tooltip="Fit all content in view",
        category="view",
        handler=lambda mw: mw.fit_view_to_content()
    ))
    
    register(ToolSpec(
        name="Paper Space Mode",
        command="toggle_paper_space", 
        tooltip="Toggle between model and paper space",
        category="view",
        checkable=True,
        handler=lambda mw: mw.toggle_paper_space()
    ))


def register_utility_tools():
    """Register utility and system tools."""
    
    register(ToolSpec(
        name="Cancel",
        command="cancel",
        shortcut="Esc",
        tooltip="Cancel current operation",
        category="utility",
        handler=lambda mw: mw.cancel_active_tool()
    ))


def register_all_tools():
    """Register all tool definitions."""
    register_drawing_tools()
    register_modify_tools() 
    register_annotation_tools()
    register_view_tools()
    register_utility_tools()


__all__ = [
    "register_all_tools",
    "register_drawing_tools",
    "register_modify_tools", 
    "register_annotation_tools",
    "register_view_tools",
    "register_utility_tools"
]