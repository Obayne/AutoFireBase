"""Frontend bootstrap module for Qt application initialization.

This module provides the Qt application bootstrap functionality,
extracted from the main application for better organization.
Phase 1: Extract Qt boot into frontend/; behavior unchanged.
"""

import os
import sys
import traceback
import time
from typing import Callable, Any

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt


def log_startup_error(msg: str) -> str:
    """Log startup errors to user's AutoFire directory.
    
    Args:
        msg: Error message to log
        
    Returns:
        Path to log file, or empty string if failed
    """
    try:
        base = os.path.join(os.path.expanduser("~"), "AutoFire", "logs")
        os.makedirs(base, exist_ok=True)
        stamp = time.strftime("%Y%m%d_%H%M%S")
        p = os.path.join(base, f"startup_error_{stamp}.log")
        with open(p, "w", encoding="utf-8") as f:
            f.write("Frontend bootstrap startup error:\n\n" + msg + "\n")
        return p
    except Exception:
        return ""


def create_fallback_window() -> QtWidgets.QWidget:
    """Create a fallback window when main UI fails to load.
    
    Returns:
        Fallback QWidget with error message
    """
    w = QtWidgets.QWidget()
    w.setWindowTitle("Auto-Fire (Frontend Bootstrap Fallback)")
    w.resize(600, 320)
    
    lab = QtWidgets.QLabel(
        "Main UI failed to load via frontend bootstrap.\n\n"
        "See latest file in ~/AutoFire/logs for details.\n"
        "Tip: ensure the window factory function is properly configured."
    )
    lab.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    
    lay = QtWidgets.QVBoxLayout(w)
    lay.addWidget(lab)
    
    return w


def bootstrap_application(window_factory: Callable[[], Any]) -> None:
    """Bootstrap the Qt application with error handling.
    
    This function handles:
    - QApplication creation
    - Main window instantiation via factory
    - Error logging and fallback UI
    - Application execution
    
    Args:
        window_factory: Function that creates and returns the main window
    """
    try:
        # Ensure we have a QApplication instance
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])
        
        try:
            # Create main window via factory
            win = window_factory()
            win.show()
            
            # Execute application
            app.exec()
            
        except Exception as e:
            # Log error and show fallback
            tb = traceback.format_exc()
            log_path = log_startup_error(tb)
            
            # Show fallback window
            fallback = create_fallback_window()
            fallback.show()
            
            # Add error details to fallback if logging succeeded
            if log_path:
                fallback.setWindowTitle(f"Auto-Fire (Error - see {os.path.basename(log_path)})")
            
            app.exec()
            
    except Exception as e:
        # Critical error - can't even create QApplication
        print(f"Critical frontend bootstrap error: {e}")
        traceback.print_exc()
        sys.exit(1)


def enhanced_bootstrap(window_factory: Callable[[], Any], 
                      tool_integration: bool = True) -> None:
    """Enhanced bootstrap with tool registry integration.
    
    This function provides the same bootstrap functionality as bootstrap_application
    but with optional enhanced tool registry integration.
    
    Args:
        window_factory: Function that creates and returns the main window
        tool_integration: Whether to integrate enhanced tool registry
    """
    try:
        # Ensure we have a QApplication instance
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])
        
        try:
            # Create main window via factory
            win = window_factory()
            
            # Optional: integrate enhanced tool registry
            if tool_integration:
                try:
                    from .integration import integrate_tool_registry, add_registry_command_support
                    integrate_tool_registry(win)
                    add_registry_command_support(win)
                except ImportError:
                    # Tool registry not available - continue without it
                    pass
                except Exception as e:
                    # Log tool registry integration error but continue
                    log_startup_error(f"Tool registry integration failed: {e}\n{traceback.format_exc()}")
            
            win.show()
            app.exec()
            
        except Exception as e:
            # Log error and show fallback
            tb = traceback.format_exc()
            log_path = log_startup_error(tb)
            
            # Show fallback window
            fallback = create_fallback_window()
            fallback.show()
            
            if log_path:
                fallback.setWindowTitle(f"Auto-Fire (Error - see {os.path.basename(log_path)})")
            
            app.exec()
            
    except Exception as e:
        # Critical error - can't even create QApplication
        print(f"Critical enhanced bootstrap error: {e}")
        traceback.print_exc()
        sys.exit(1)


# Legacy compatibility function
def main_bootstrap(create_window_func: Callable[[], Any]) -> None:
    """Legacy compatibility bootstrap function.
    
    Provides the same interface as the original main() function
    but uses the new frontend bootstrap system.
    
    Args:
        create_window_func: Function that creates the main window
    """
    bootstrap_application(create_window_func)


__all__ = [
    "bootstrap_application",
    "enhanced_bootstrap", 
    "main_bootstrap",
    "log_startup_error",
    "create_fallback_window"
]