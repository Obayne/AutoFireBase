"""Frontend package for AutoFireBase.

This package contains the enhanced tool registry system, UI components,
and Qt application bootstrap functionality.
"""

from .tool_registry import ToolSpec, ToolRegistry, register, get, all_tools, get_registry
from .tool_definitions import register_all_tools
from .tool_manager import ToolManager
from .integration import integrate_tool_registry, add_registry_command_support
from .bootstrap import bootstrap_application, enhanced_bootstrap, main_bootstrap

__all__ = [
    "ToolSpec",
    "ToolRegistry", 
    "register",
    "get",
    "all_tools",
    "get_registry",
    "register_all_tools",
    "ToolManager",
    "integrate_tool_registry",
    "add_registry_command_support",
    "bootstrap_application",
    "enhanced_bootstrap",
    "main_bootstrap"
]