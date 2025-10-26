"""
Project Circuits Editor Integration

Integrates the Project Circuits Editor into the main AutoFire model space
as per Master Specification Section 6 requirements.
"""

import logging

logger = logging.getLogger(__name__)

try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
    from frontend.panels.project_circuits_editor import create_project_circuits_editor
    INTEGRATION_AVAILABLE = True
except ImportError as e:
    logger.error("Integration imports failed: %s", e)
    INTEGRATION_AVAILABLE = False


def integrate_project_circuits_editor(model_space_window):
    """
    Integrate the Project Circuits Editor into the model space.
    
    Args:
        model_space_window: The main model space window instance
        
    Returns:
        bool: True if integration successful, False otherwise
    """
    if not INTEGRATION_AVAILABLE:
        logger.error("Cannot integrate Project Circuits Editor - imports not available")
        return False
    
    try:
        logger.info("Integrating Project Circuits Editor into model space...")
        
        # Create the Project Circuits Editor
        circuits_editor = create_project_circuits_editor(model_space_window)
        
        # Add as a docked panel or tab
        if hasattr(model_space_window, 'addDockWidget'):
            # Add as docked widget
            from PySide6.QtWidgets import QDockWidget
            from PySide6.QtCore import Qt
            
            dock = QDockWidget("🔌 Project Circuits", model_space_window)
            dock.setWidget(circuits_editor)
            model_space_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
            
            logger.info("Project Circuits Editor added as docked panel")
            
        elif hasattr(model_space_window, 'tabWidget'):
            # Add as tab
            tab_widget = model_space_window.tabWidget
            tab_widget.addTab(circuits_editor, "🔌 Circuits")
            
            logger.info("Project Circuits Editor added as tab")
            
        else:
            # Fallback - add to layout if possible
            if hasattr(model_space_window, 'layout') and model_space_window.layout():
                model_space_window.layout().addWidget(circuits_editor)
                logger.info("Project Circuits Editor added to main layout")
            else:
                logger.warning("Could not determine how to add Project Circuits Editor")
                return False
        
        # Connect to live calculations if available
        if hasattr(model_space_window, 'live_calculations_engine'):
            circuits_editor.set_live_calculations_engine(
                model_space_window.live_calculations_engine
            )
            logger.info("Connected Project Circuits Editor to live calculations")
        
        # Store reference for future access
        model_space_window.project_circuits_editor = circuits_editor
        
        logger.info("✅ Project Circuits Editor integration complete")
        return True
        
    except Exception as e:
        logger.error("Failed to integrate Project Circuits Editor: %s", e)
        return False


def create_standalone_circuits_window(parent=None):
    """
    Create a standalone Project Circuits Editor window.
    
    Args:
        parent: Parent widget (optional)
        
    Returns:
        QWidget: The circuits editor window or None if failed
    """
    if not INTEGRATION_AVAILABLE:
        logger.error("Cannot create standalone circuits window - imports not available")
        return None
    
    try:
        from PySide6.QtWidgets import QMainWindow
        
        class StandaloneCircuitsWindow(QMainWindow):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("🔌 AutoFire Project Circuits Editor")
                self.setGeometry(100, 100, 1200, 800)
                
                # Create and set the circuits editor as central widget
                circuits_editor = create_project_circuits_editor(self)
                self.setCentralWidget(circuits_editor)
                
                # Store reference
                self.circuits_editor = circuits_editor
                
                logger.info("Standalone Project Circuits Editor window created")
        
        return StandaloneCircuitsWindow(parent)
        
    except Exception as e:
        logger.error("Failed to create standalone circuits window: %s", e)
        return None


def add_circuits_menu_actions(main_window):
    """
    Add Project Circuits Editor menu actions to the main window.
    
    Args:
        main_window: The main application window
    """
    if not INTEGRATION_AVAILABLE:
        return
    
    try:
        # Find or create Tools menu
        menubar = main_window.menuBar()
        tools_menu = None
        
        for action in menubar.actions():
            if action.text() == "Tools":
                tools_menu = action.menu()
                break
        
        if not tools_menu:
            tools_menu = menubar.addMenu("Tools")
        
        # Add Project Circuits action
        circuits_action = tools_menu.addAction("🔌 Project Circuits Editor")
        circuits_action.setStatusTip("Open the centralized circuit management interface")
        
        def open_circuits_editor():
            """Open the Project Circuits Editor."""
            if hasattr(main_window, 'project_circuits_editor'):
                # Show existing editor
                if hasattr(main_window.project_circuits_editor, 'show'):
                    main_window.project_circuits_editor.show()
                elif hasattr(main_window.project_circuits_editor, 'parent'):
                    dock = main_window.project_circuits_editor.parent()
                    if hasattr(dock, 'show'):
                        dock.show()
            else:
                # Create standalone window
                circuits_window = create_standalone_circuits_window(main_window)
                if circuits_window:
                    circuits_window.show()
                    main_window.circuits_window = circuits_window
        
        circuits_action.triggered.connect(open_circuits_editor)
        
        logger.info("Project Circuits Editor menu actions added")
        
    except Exception as e:
        logger.error("Failed to add circuits menu actions: %s", e)


def setup_circuits_keyboard_shortcuts(main_window):
    """
    Setup keyboard shortcuts for Project Circuits Editor.
    
    Args:
        main_window: The main application window
    """
    if not INTEGRATION_AVAILABLE:
        return
    
    try:
        from PySide6.QtGui import QKeySequence, QShortcut
        
        # Ctrl+Shift+C for Project Circuits
        circuits_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), main_window)
        
        def toggle_circuits_editor():
            """Toggle the Project Circuits Editor visibility."""
            if hasattr(main_window, 'project_circuits_editor'):
                editor = main_window.project_circuits_editor
                if hasattr(editor, 'isVisible'):
                    if editor.isVisible():
                        editor.hide()
                    else:
                        editor.show()
                elif hasattr(editor, 'parent'):
                    dock = editor.parent()
                    if hasattr(dock, 'isVisible'):
                        dock.setVisible(not dock.isVisible())
        
        circuits_shortcut.activated.connect(toggle_circuits_editor)
        
        logger.info("Project Circuits Editor keyboard shortcuts configured")
        
    except Exception as e:
        logger.error("Failed to setup circuits keyboard shortcuts: %s", e)


# Integration status check
def check_integration_status():
    """
    Check the status of Project Circuits Editor integration capabilities.
    
    Returns:
        dict: Status information
    """
    status = {
        'integration_available': INTEGRATION_AVAILABLE,
        'pyside6_available': False,
        'circuits_editor_available': False,
        'live_calculations_available': False
    }
    
    try:
        import PySide6
        status['pyside6_available'] = True
    except ImportError:
        pass
    
    try:
        from frontend.panels.project_circuits_editor import ProjectCircuitsEditor
        status['circuits_editor_available'] = True
    except ImportError:
        pass
    
    try:
        from cad_core.calculations.live_engine import LiveCalculationsEngine
        status['live_calculations_available'] = True
    except ImportError:
        pass
    
    return status


if __name__ == "__main__":
    # Print integration status when run directly
    status = check_integration_status()
    
    print("\n🔌 Project Circuits Editor Integration Status")
    print("=" * 50)
    
    for key, value in status.items():
        icon = "✅" if value else "❌"
        print(f"{icon} {key.replace('_', ' ').title()}: {value}")
    
    if status['integration_available']:
        print("\n✅ Ready for integration into AutoFire model space")
    else:
        print("\n❌ Integration not available - check dependencies")