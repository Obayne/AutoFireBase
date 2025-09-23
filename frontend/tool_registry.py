"""Enhanced tool registry with shortcuts and CAD core integration.

This module provides centralized tool management with automatic shortcut
registration and integration with CAD core operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Any
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QObject


@dataclass(frozen=True)
class ToolSpec:
    """Specification for a CAD tool."""
    name: str
    command: str
    shortcut: Optional[str] = None
    icon: Optional[str] = None
    tooltip: Optional[str] = None
    category: str = "general"
    action_factory: Optional[Callable[[QObject], QtGui.QAction]] = None
    handler: Optional[Callable[..., Any]] = None
    checkable: bool = False
    enabled: bool = True


class ToolRegistry:
    """Centralized registry for CAD tools with shortcuts."""
    
    def __init__(self):
        self._tools: Dict[str, ToolSpec] = {}
        self._shortcuts: Dict[str, ToolSpec] = {}
        self._categories: Dict[str, List[ToolSpec]] = {}
        
    def register(self, spec: ToolSpec) -> None:
        """Register a tool specification."""
        self._tools[spec.command] = spec
        
        if spec.shortcut:
            self._shortcuts[spec.shortcut] = spec
            
        if spec.category not in self._categories:
            self._categories[spec.category] = []
        self._categories[spec.category].append(spec)
    
    def get(self, command: str) -> Optional[ToolSpec]:
        """Get tool by command."""
        return self._tools.get(command)
    
    def get_by_shortcut(self, shortcut: str) -> Optional[ToolSpec]:
        """Get tool by keyboard shortcut."""
        return self._shortcuts.get(shortcut)
    
    def get_category(self, category: str) -> List[ToolSpec]:
        """Get all tools in a category."""
        return self._categories.get(category, [])
    
    def all_tools(self) -> Dict[str, ToolSpec]:
        """Get all registered tools."""
        return dict(self._tools)
    
    def all_categories(self) -> List[str]:
        """Get all available categories."""
        return list(self._categories.keys())
    
    def create_action(self, spec: ToolSpec, parent: QObject) -> QtGui.QAction:
        """Create a QAction for a tool specification."""
        if spec.action_factory:
            return spec.action_factory(parent)
        
        action = QtGui.QAction(spec.name, parent)
        
        if spec.shortcut:
            action.setShortcut(QtGui.QKeySequence(spec.shortcut))
        
        if spec.tooltip:
            action.setToolTip(spec.tooltip)
        
        if spec.icon:
            # For now, just set text. Icons can be added later.
            pass
        
        if spec.handler:
            action.triggered.connect(spec.handler)
        
        action.setCheckable(spec.checkable)
        action.setEnabled(spec.enabled)
        
        return action
    
    def create_menu(self, category: str, parent: QtWidgets.QWidget) -> QtWidgets.QMenu:
        """Create a menu for a tool category."""
        menu = QtWidgets.QMenu(category.title(), parent)
        
        for spec in self.get_category(category):
            if spec.enabled:
                action = self.create_action(spec, parent)
                menu.addAction(action)
        
        return menu
    
    def install_shortcuts(self, parent: QObject) -> None:
        """Install all keyboard shortcuts on a parent widget."""
        for spec in self._tools.values():
            if spec.shortcut and spec.handler:
                shortcut = QtGui.QShortcut(QtGui.QKeySequence(spec.shortcut), parent)
                shortcut.activated.connect(spec.handler)


# Global registry instance
_REGISTRY = ToolRegistry()


def register(spec: ToolSpec) -> None:
    """Register a tool in the global registry."""
    _REGISTRY.register(spec)


def get(command: str) -> Optional[ToolSpec]:
    """Get tool by command from global registry."""
    return _REGISTRY.get(command)


def get_by_shortcut(shortcut: str) -> Optional[ToolSpec]:
    """Get tool by shortcut from global registry."""
    return _REGISTRY.get_by_shortcut(shortcut)


def get_category(category: str) -> List[ToolSpec]:
    """Get tools by category from global registry."""
    return _REGISTRY.get_category(category)


def all_tools() -> Dict[str, ToolSpec]:
    """Get all tools from global registry."""
    return _REGISTRY.all_tools()


def get_registry() -> ToolRegistry:
    """Get the global registry instance."""
    return _REGISTRY


__all__ = [
    "ToolSpec", 
    "ToolRegistry",
    "register", 
    "get", 
    "get_by_shortcut",
    "get_category",
    "all_tools",
    "get_registry"
]

