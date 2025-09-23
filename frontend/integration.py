"""Integration utilities for tool registry with main application.

This module provides functions to integrate the enhanced tool registry
with the existing main application without major refactoring.
"""

from typing import Any
from .tool_manager import ToolManager


def integrate_tool_registry(main_window: Any) -> ToolManager:
    """Integrate tool registry with the main application window.
    
    This function creates a ToolManager and sets up enhanced tools alongside
    the existing tool system. It can be called from the main window initialization.
    
    Args:
        main_window: The main application window instance
        
    Returns:
        ToolManager instance for further customization
    """
    # Create tool manager
    tool_manager = ToolManager(main_window)
    
    # Store reference on main window for later use
    main_window.tool_manager = tool_manager
    
    # Install enhanced shortcuts (these will work alongside existing ones)
    tool_manager.install_shortcuts()
    
    return tool_manager


def add_registry_command_support(main_window: Any) -> None:
    """Add command line support for tool registry commands.
    
    This enhances the existing command system to support registry-based commands.
    """
    if not hasattr(main_window, 'tool_manager'):
        return
    
    # Store reference to original command handler if it exists
    original_run_command = getattr(main_window, '_run_command', None)
    
    def enhanced_run_command():
        """Enhanced command handler that tries registry first, then fallback."""
        if not hasattr(main_window, 'cmd'):
            return
            
        text = main_window.cmd.text().strip().lower()
        if not text:
            return
            
        # Clear the command line
        main_window.cmd.clear()
        
        # Try tool registry first
        if main_window.tool_manager.execute_command(text):
            return
        
        # Fallback to original command handler
        if original_run_command:
            # Restore text for original handler
            main_window.cmd.setText(text)
            original_run_command()
            main_window.cmd.clear()
    
    # Replace the command handler
    main_window._run_command = enhanced_run_command
    
    # Reconnect the command line if it exists
    if hasattr(main_window, 'cmd') and hasattr(main_window.cmd, 'returnPressed'):
        main_window.cmd.returnPressed.disconnect()
        main_window.cmd.returnPressed.connect(enhanced_run_command)


__all__ = ["integrate_tool_registry", "add_registry_command_support"]