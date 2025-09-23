"""Tool manager for integrating tool registry with main application.

This module provides the ToolManager class that handles tool registration,
menu creation, and keyboard shortcut installation for the main application.
"""

from typing import Any, Dict, List, Optional
from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import QObject

from .tool_registry import ToolRegistry, ToolSpec, get_registry
from .tool_definitions import register_all_tools


class ToolManager:
    """Manages tools for the main application window."""
    
    def __init__(self, main_window: Any):
        self.main_window = main_window
        self.registry = get_registry()
        self._actions: Dict[str, QtGui.QAction] = {}
        
        # Register all tool definitions
        register_all_tools()
    
    def create_menus(self, menubar: QtWidgets.QMenuBar) -> Dict[str, QtWidgets.QMenu]:
        """Create menus for all tool categories.
        
        Returns:
            Dictionary mapping category names to menu objects.
        """
        menus = {}
        
        # Tools menu for drawing and modification tools
        m_tools = menubar.addMenu("&Tools")
        drawing_tools = self.registry.get_category("drawing")
        for spec in drawing_tools:
            if spec.enabled:
                action = self._create_tool_action(spec)
                m_tools.addAction(action)
        
        m_tools.addSeparator()
        annotation_tools = self.registry.get_category("annotation") 
        for spec in annotation_tools:
            if spec.enabled and spec.command in ["dimension", "text", "measure"]:
                action = self._create_tool_action(spec)
                m_tools.addAction(action)
        
        menus["tools"] = m_tools
        
        # Modify menu for editing operations that use CAD core
        m_modify = menubar.addMenu("&Modify")
        modify_tools = self.registry.get_category("modify")
        for spec in modify_tools:
            if spec.enabled:
                action = self._create_tool_action(spec)
                m_modify.addAction(action)
        
        menus["modify"] = m_modify
        
        # View menu for display controls
        m_view = menubar.addMenu("&View")
        view_tools = self.registry.get_category("view")
        for spec in view_tools:
            if spec.enabled:
                action = self._create_tool_action(spec)
                if spec.checkable:
                    # Set initial state for checkable view tools
                    if spec.command == "toggle_grid":
                        grid_action = getattr(self.main_window, 'act_view_grid', None)
                        action.setChecked(bool(grid_action and grid_action.isChecked()))
                    elif spec.command == "toggle_snap":
                        action.setChecked(getattr(self.main_window.scene, 'snap_enabled', True))
                    elif spec.command == "toggle_crosshair":
                        action.setChecked(getattr(self.main_window.view, 'show_crosshair', True))
                    elif spec.command == "toggle_paper_space":
                        action.setChecked(getattr(self.main_window, 'paper_space_mode', False))
                m_view.addAction(action)
        
        menus["view"] = m_view
        
        return menus
    
    def install_shortcuts(self) -> None:
        """Install all keyboard shortcuts."""
        for command, spec in self.registry.all_tools().items():
            if spec.shortcut and spec.handler:
                shortcut = QtGui.QShortcut(QtGui.QKeySequence(spec.shortcut), self.main_window)
                # Wrap handler to pass main_window
                handler = spec.handler
                if handler:
                    shortcut.activated.connect(lambda h=handler: h(self.main_window))
    
    def get_action(self, command: str) -> Optional[QtGui.QAction]:
        """Get QAction for a tool command."""
        return self._actions.get(command)
    
    def _create_tool_action(self, spec: ToolSpec) -> QtGui.QAction:
        """Create and cache a QAction for a tool specification."""
        if spec.command in self._actions:
            return self._actions[spec.command]
        
        action = QtGui.QAction(spec.name, self.main_window)
        
        if spec.shortcut:
            action.setShortcut(QtGui.QKeySequence(spec.shortcut))
        
        if spec.tooltip:
            action.setToolTip(spec.tooltip)
        
        if spec.handler:
            # Wrap handler to pass main_window
            handler = spec.handler
            if handler:
                action.triggered.connect(lambda checked=False, h=handler: h(self.main_window))
        
        action.setCheckable(spec.checkable)
        action.setEnabled(spec.enabled)
        
        self._actions[spec.command] = action
        return action
    
    def execute_command(self, command: str) -> bool:
        """Execute a tool command programmatically.
        
        Args:
            command: Tool command to execute
            
        Returns:
            True if command was found and executed, False otherwise
        """
        spec = self.registry.get(command)
        if spec and spec.handler:
            spec.handler(self.main_window)
            return True
        return False
    
    def get_tools_by_category(self, category: str) -> List[ToolSpec]:
        """Get all tools in a category."""
        return self.registry.get_category(category)
    
    def get_available_commands(self) -> List[str]:
        """Get list of all available tool commands."""
        return list(self.registry.all_tools().keys())


__all__ = ["ToolManager"]