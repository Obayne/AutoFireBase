"""
Project Builder Controller - Orchestrates different workflows based on user expertise.

Expert -> Direct to CAD
Intermediate -> Guidance then CAD
Beginner -> Full educational workflow
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QStackedWidget, QWidget

from frontend.panels.project_builder_menu import ProjectBuilderMenu
from frontend.panels.intermediate_guidance import IntermediateGuidance
from frontend.panels.guided_system_builder import GuidedSystemBuilderWidget


class ProjectBuilderController(QStackedWidget):
    """Controller that manages the different project builder workflows."""

    # Signals
    launch_cad_workspace = Signal(dict)  # Launch CAD with settings

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_workflows()

    def _setup_workflows(self):
        """Setup the different workflow panels."""

        # 1. Main menu - choose expertise level
        self.menu = ProjectBuilderMenu()
        self.menu.expert_mode_requested.connect(self._handle_expert_mode)
        self.menu.intermediate_mode_requested.connect(self._handle_intermediate_mode)
        self.menu.beginner_mode_requested.connect(self._handle_beginner_mode)
        self.addWidget(self.menu)

        # 2. Intermediate guidance panel
        self.intermediate_guidance = None  # Created on demand

        # 3. Beginner educational workflow
        self.beginner_workflow = None  # Created on demand

        # Start with menu
        self.setCurrentWidget(self.menu)

    def _handle_expert_mode(self):
        """Handle expert mode - go directly to CAD."""
        project_info = self.menu.get_project_info()

        cad_settings = {
            "assistance_level": "expert",
            "show_tips": False,
            "auto_compliance": False,
            "project_type": project_info.get("project_type"),
            "guidance_mode": False,
            "ai_suggestions": "minimal",
        }

        print("🎯 Expert Mode: Launching CAD workspace directly")
        self.launch_cad_workspace.emit(cad_settings)

    def _handle_intermediate_mode(self):
        """Handle intermediate mode - show guidance then CAD."""
        project_info = self.menu.get_project_info()

        # Create intermediate guidance if not exists
        if self.intermediate_guidance is None:
            self.intermediate_guidance = IntermediateGuidance(project_info)
            self.intermediate_guidance.proceed_to_cad.connect(self._launch_cad_from_guidance)
            self.addWidget(self.intermediate_guidance)
        else:
            # Update project info
            self.intermediate_guidance.project_info = project_info

        print("⚡ Intermediate Mode: Showing guidance panel")
        self.setCurrentWidget(self.intermediate_guidance)

    def _handle_beginner_mode(self):
        """Handle beginner mode - full educational workflow."""
        project_info = self.menu.get_project_info()

        # Create beginner workflow if not exists
        if self.beginner_workflow is None:
            self.beginner_workflow = GuidedSystemBuilderWidget()
            self.beginner_workflow.system_completed.connect(self._launch_cad_from_beginner)
            self.addWidget(self.beginner_workflow)

        print("📚 Beginner Mode: Starting full educational workflow")
        self.setCurrentWidget(self.beginner_workflow)

    def _launch_cad_from_guidance(self, settings):
        """Launch CAD from intermediate guidance."""
        print("⚡ Launching CAD from intermediate guidance")
        self.launch_cad_workspace.emit(settings)

    def _launch_cad_from_beginner(self, system_data):
        """Launch CAD from beginner workflow."""
        cad_settings = {
            "assistance_level": "full",
            "show_tips": True,
            "auto_compliance": True,
            "project_type": "Custom",
            "guidance_mode": True,
            "system_data": system_data,
        }

        print("📚 Launching CAD from beginner workflow")
        self.launch_cad_workspace.emit(cad_settings)

    def reset_to_menu(self):
        """Reset back to the main menu."""
        self.setCurrentWidget(self.menu)
