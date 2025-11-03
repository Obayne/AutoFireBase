"""
Intermediate Designer Guidance - Helpful instructions without hand-holding.

Provides structured guidance for designers with some experience who want
helpful tips and instructions throughout the design process.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class IntermediateGuidance(QWidget):
    """Guidance panel for intermediate designers."""

    proceed_to_cad = Signal(dict)  # Emit when ready to proceed to CAD

    def __init__(self, project_info=None, parent=None):
        super().__init__(parent)
        self.project_info = project_info or {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup the guidance interface."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("⚡ Intermediate Designer Guidance")
        header.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            color: #1a237e;
            padding: 15px;
            text-align: center;
        """
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Scrollable content area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Project overview
        self._add_project_overview(scroll_layout)

        # Design workflow steps
        self._add_workflow_steps(scroll_layout)

        # Key reminders
        self._add_key_reminders(scroll_layout)

        # Quick reference
        self._add_quick_reference(scroll_layout)

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # Proceed button
        button_layout = QHBoxLayout()

        proceed_button = QPushButton("🚀 Proceed to CAD Workspace")
        proceed_button.setStyleSheet(
            """
            QPushButton {
                background-color: #1a237e;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 30px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0d1766;
            }
        """
        )
        proceed_button.clicked.connect(self._proceed_to_cad)

        button_layout.addStretch()
        button_layout.addWidget(proceed_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

    def _add_project_overview(self, layout):
        """Add project overview section."""
        overview_group = QGroupBox("📋 Project Overview")
        overview_layout = QVBoxLayout(overview_group)

        project_type = self.project_info.get("project_type", "General")

        overview_text = f"""
        <b>Project Type:</b> {project_type} Building<br/>
        <b>Your Level:</b> Intermediate Designer<br/>
        <b>Assistance:</b> Helpful guidance and tips provided<br/>
        <br/>
        <b>What you'll get:</b><br/>
        • Smart suggestions during device placement<br/>
        • Automatic compliance checking<br/>
        • Code reference tooltips<br/>
        • Circuit calculation assistance<br/>
        """

        overview_label = QLabel(overview_text)
        overview_label.setWordWrap(True)
        overview_label.setStyleSheet("padding: 10px;")
        overview_layout.addWidget(overview_label)

        layout.addWidget(overview_group)

    def _add_workflow_steps(self, layout):
        """Add workflow steps section."""
        workflow_group = QGroupBox("🔄 Recommended Design Workflow")
        workflow_layout = QVBoxLayout(workflow_group)

        steps = [
            (
                "1. Import Floor Plan",
                "Load architectural drawings (PDF/DWG). Set proper scale.",
                "#e8f5e8",
            ),
            (
                "2. Place Control Panel",
                "Position main fire alarm control panel. Consider AHJ requirements.",
                "#fff3cd",
            ),
            (
                "3. Add Detection Devices",
                "Place smoke/heat detectors per NFPA spacing requirements.",
                "#d1ecf1",
            ),
            (
                "4. Add Notification Devices",
                "Place horns/strobes for proper coverage and ADA compliance.",
                "#f8d7da",
            ),
            (
                "5. Design Circuits",
                "Create SLC/NAC circuits with proper voltage drop calculations.",
                "#e2e3e5",
            ),
            (
                "6. Generate Documentation",
                "Create schedules, risers, and compliance reports.",
                "#d4edda",
            ),
        ]

        for step, description, color in steps:
            step_widget = QWidget()
            step_widget.setStyleSheet(
                f"""
                QWidget {{
                    background-color: {color};
                    border-radius: 6px;
                    margin: 2px;
                }}
            """
            )
            step_layout = QVBoxLayout(step_widget)

            step_title = QLabel(f"<b>{step}</b>")
            step_desc = QLabel(description)
            step_desc.setStyleSheet("font-style: italic; color: #555;")

            step_layout.addWidget(step_title)
            step_layout.addWidget(step_desc)

            workflow_layout.addWidget(step_widget)

        layout.addWidget(workflow_group)

    def _add_key_reminders(self, layout):
        """Add key reminders section."""
        reminders_group = QGroupBox("⚠️ Key Reminders")
        reminders_layout = QVBoxLayout(reminders_group)

        project_type = self.project_info.get("project_type", "General")

        # Base reminders
        reminders = [
            "🔍 Check local AHJ requirements before starting",
            "📏 Verify detector spacing per NFPA 72 Table 17.6.2.1",
            "🔊 Ensure notification appliance coverage meets 15cd minimum",
            "⚡ Calculate voltage drop for all circuits",
            "📋 Document all device types and quantities",
        ]

        # Add project-specific reminders
        if project_type == "Healthcare":
            reminders.extend(
                [
                    "🏥 Healthcare: Consider nurse call integration",
                    "🚨 Special requirements for patient sleeping areas",
                ]
            )
        elif project_type == "School":
            reminders.extend(
                [
                    "🏫 School: Mass notification requirements",
                    "🔔 Consider classroom occupancy variations",
                ]
            )
        elif project_type == "Hotel":
            reminders.extend(
                [
                    "🏨 Hotel: Guest room smoke detector requirements",
                    "🚪 Corridor and common area coverage",
                ]
            )

        for reminder in reminders:
            reminder_label = QLabel(reminder)
            reminder_label.setStyleSheet("padding: 3px; margin: 2px;")
            reminders_layout.addWidget(reminder_label)

        layout.addWidget(reminders_group)

    def _add_quick_reference(self, layout):
        """Add quick reference section."""
        reference_group = QGroupBox("📖 Quick Reference")
        reference_layout = QVBoxLayout(reference_group)

        reference_text = """
        <b>Common Detector Spacing (NFPA 72):</b><br/>
        • Smoke Detectors: 30ft spacing, 15ft from walls<br/>
        • Heat Detectors: Per manufacturer listing (typically 50ft)<br/>
        <br/>
        <b>Notification Appliance Requirements:</b><br/>
        • Visual: 15cd minimum, follow spacing tables<br/>
        • Audible: 15dB above ambient, 5dB above max 60-second sound<br/>
        <br/>
        <b>Circuit Voltage Drop Limits:</b><br/>
        • SLC Circuits: Varies by manufacturer (typically 10-20V)<br/>
        • NAC Circuits: 10% maximum voltage drop<br/>
        """

        reference_label = QLabel(reference_text)
        reference_label.setWordWrap(True)
        reference_label.setStyleSheet(
            """
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #1a237e;
        """
        )
        reference_layout.addWidget(reference_label)

        layout.addWidget(reference_group)

    def _proceed_to_cad(self):
        """Proceed to CAD workspace with guidance settings."""
        cad_settings = {
            "assistance_level": "intermediate",
            "show_tips": True,
            "auto_compliance": True,
            "project_type": self.project_info.get("project_type"),
            "guidance_mode": True,
        }
        self.proceed_to_cad.emit(cad_settings)
