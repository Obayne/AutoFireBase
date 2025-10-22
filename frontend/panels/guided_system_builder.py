"""
Guided Fire Alarm System Builder - Intuitive workflow for any skill level.

This module provides a step-by-step guided approach to building fire alarm systems:
1. Building Assessment - Understand requirements
2. Panel Selection - Choose appropriate control panel
3. Device Planning - Select detection and notification devices
4. Wire Specification - Plan circuits and wiring
5. System Assembly - Review and deploy complete system

The workflow adapts to user skill level and provides intelligent recommendations.
"""

import os
import sqlite3
from dataclasses import asdict, dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


@dataclass
class BuildingAssessment:
    """Building assessment data."""

    building_type: str = ""
    size_sqft: int = 0
    floors: int = 1
    occupancy_level: str = ""
    special_hazards: list[str] | None = None
    ahj_requirements: str = ""

    def __post_init__(self):
        if self.special_hazards is None:
            self.special_hazards = []


@dataclass
class SystemRecommendation:
    """System recommendations based on assessment."""

    panel_type: str = ""
    panel_zones: int = 0
    device_count_estimate: dict[str, int] | None = None
    wire_requirements: dict[str, str] | None = None
    compliance_notes: list[str] | None = None

    def __post_init__(self):
        if self.device_count_estimate is None:
            self.device_count_estimate = {}
        if self.wire_requirements is None:
            self.wire_requirements = {}
        if self.compliance_notes is None:
            self.compliance_notes = []


class GuidedSystemBuilderWidget(QWidget):
    """
    Guided System Builder with intuitive workflow.

    Provides step-by-step guidance for building fire alarm systems,
    regardless of user skill level.
    """

    # Signals
    system_completed = Signal(dict)  # Emitted when system is complete
    step_changed = Signal(int)  # Emitted when workflow step changes
    assembled = Signal(dict)  # For backward compatibility with old system
    staging_changed = Signal()  # For backward compatibility

    def __init__(self, parent=None):
        super().__init__(parent)

        # Workflow state
        self.current_step = 0
        self.assessment = BuildingAssessment()
        self.recommendations = SystemRecommendation()
        # Ensure recommendations are properly initialized
        self.recommendations.device_count_estimate = {}
        self.recommendations.wire_requirements = {}
        self.recommendations.compliance_notes = []

        self.selected_panel = None
        self.selected_devices = []
        self.selected_wires = []

        # Device catalog
        self.device_catalog = self._load_device_catalog()

        self._setup_ui()
        self._start_workflow()

    def _setup_ui(self):
        """Setup the guided workflow UI."""
        layout = QVBoxLayout(self)

        # Workflow header with progress
        self.workflow_header = self._create_workflow_header()
        layout.addWidget(self.workflow_header)

        # Main content area
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.tabBarClicked.connect(self._on_tab_clicked)

        # Create workflow steps
        self._setup_assessment_tab()  # Step 1
        self._setup_panel_selection_tab()  # Step 2
        self._setup_device_planning_tab()  # Step 3
        self._setup_wire_planning_tab()  # Step 4
        self._setup_system_review_tab()  # Step 5

        layout.addWidget(self.tab_widget)

        # Navigation controls
        nav_layout = QHBoxLayout()

        self.back_btn = QPushButton("⬅️ Back")
        self.back_btn.setEnabled(False)
        self.back_btn.clicked.connect(self._go_back)

        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()

        self.next_btn = QPushButton("Next ➡️")
        self.next_btn.clicked.connect(self._go_next)

        self.complete_btn = QPushButton("🎉 Complete System")
        self.complete_btn.setVisible(False)
        self.complete_btn.clicked.connect(self._complete_system)

        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.complete_btn)

        layout.addLayout(nav_layout)

    def _create_workflow_header(self):
        """Create the workflow progress header."""
        header = QWidget()
        header.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0078d4, stop:1 #005a9f);
                border-radius: 8px;
                margin-bottom: 15px;
            }
        """
        )

        layout = QVBoxLayout(header)

        # Title
        title = QLabel("🚨 Fire Alarm System Builder")
        title.setStyleSheet(
            """
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin: 10px;
        """
        )
        layout.addWidget(title)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(5)
        self.progress_bar.setValue(1)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid white;
                border-radius: 5px;
                background-color: rgba(255,255,255,0.2);
                margin: 5px 15px;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 3px;
            }
        """
        )
        layout.addWidget(self.progress_bar)

        # Step indicators
        steps_layout = QHBoxLayout()
        steps_layout.setContentsMargins(15, 5, 15, 15)

        self.step_indicators = []
        steps = ["📋 Assess", "🔧 Panel", "🔍 Devices", "🔌 Wiring", "✅ Review"]

        for i, step in enumerate(steps):
            indicator = QLabel(step)
            indicator.setStyleSheet(
                f"""
                color: {'white' if i == 0 else 'rgba(255,255,255,0.6)'};
                font-weight: {'bold' if i == 0 else 'normal'};
                padding: 5px 10px;
                border-radius: 15px;
                background-color: {'rgba(255,255,255,0.2)' if i == 0 else 'transparent'};
            """
            )
            indicator.setAlignment(Qt.AlignCenter)
            self.step_indicators.append(indicator)
            steps_layout.addWidget(indicator)

        layout.addLayout(steps_layout)

        # Current guidance
        self.guidance_label = QLabel("Let's start by understanding your building requirements...")
        self.guidance_label.setStyleSheet(
            """
            color: white;
            font-style: italic;
            margin: 0 15px 10px 15px;
            padding: 8px;
            background-color: rgba(255,255,255,0.1);
            border-radius: 4px;
        """
        )
        layout.addWidget(self.guidance_label)

        return header

    def _setup_assessment_tab(self):
        """Setup Step 1: Building Assessment."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Welcome message
        welcome = QLabel(
            """
        <h3>🏢 Welcome to the Fire Alarm System Builder!</h3>
        <p>This guided workflow will help you design a complete fire alarm system
        tailored to your building's specific requirements and code compliance needs.</p>
        <p><b>Step 1:</b> Let's assess your building to determine the right system components.</p>
        """
        )
        welcome.setWordWrap(True)
        welcome.setStyleSheet(
            "background-color: #e3f2fd; padding: 15px; border-radius: 6px; margin-bottom: 15px;"
        )
        layout.addWidget(welcome)

        # Building assessment form
        assessment_group = QGroupBox("Building Information")
        assessment_layout = QFormLayout(assessment_group)

        # Building type with guidance
        self.building_type = QComboBox()
        self.building_type.addItems(
            [
                "Select building type...",
                "🏢 Office Building (Business occupancy)",
                "🏭 Industrial/Manufacturing (Industrial occupancy)",
                "🏫 School/Educational (Educational occupancy)",
                "🏥 Healthcare Facility (Healthcare occupancy)",
                "🏨 Hotel/Hospitality (Residential occupancy)",
                "🏪 Retail/Mercantile (Mercantile occupancy)",
                "🏠 Apartment/Residential (Residential occupancy)",
                "🏛️ Assembly (Assembly occupancy)",
                "📦 Storage/Warehouse (Storage occupancy)",
            ]
        )
        self.building_type.currentTextChanged.connect(self._on_assessment_changed)
        assessment_layout.addRow("Building Type:", self.building_type)

        # Building size
        size_layout = QHBoxLayout()
        self.building_size = QSpinBox()
        self.building_size.setRange(500, 999999)
        self.building_size.setValue(10000)
        self.building_size.setSuffix(" sq ft")
        self.building_size.valueChanged.connect(self._on_assessment_changed)

        self.size_guidance = QLabel("💡 Affects device count and panel capacity")
        self.size_guidance.setStyleSheet("color: #6c757d; font-size: 10px; font-style: italic;")

        size_layout.addWidget(self.building_size)
        size_layout.addWidget(self.size_guidance)
        assessment_layout.addRow("Total Floor Area:", size_layout)

        # Number of floors
        floors_layout = QHBoxLayout()
        self.floors = QSpinBox()
        self.floors.setRange(1, 50)
        self.floors.setValue(1)
        self.floors.valueChanged.connect(self._on_assessment_changed)

        self.floors_guidance = QLabel("💡 Multi-story buildings may need additional features")
        self.floors_guidance.setStyleSheet("color: #6c757d; font-size: 10px; font-style: italic;")

        floors_layout.addWidget(self.floors)
        floors_layout.addWidget(self.floors_guidance)
        assessment_layout.addRow("Number of Floors:", floors_layout)

        # Occupant load
        occupancy_layout = QHBoxLayout()
        self.occupancy = QComboBox()
        self.occupancy.addItems(
            [
                "Light (1-49 people)",
                "Moderate (50-299 people)",
                "Heavy (300-999 people)",
                "High-Occupancy (1000+ people)",
            ]
        )
        self.occupancy.currentTextChanged.connect(self._on_assessment_changed)

        self.occupancy_guidance = QLabel("💡 Higher occupancy requires enhanced notification")
        self.occupancy_guidance.setStyleSheet(
            "color: #6c757d; font-size: 10px; font-style: italic;"
        )

        occupancy_layout.addWidget(self.occupancy)
        occupancy_layout.addWidget(self.occupancy_guidance)
        assessment_layout.addRow("Occupant Load:", occupancy_layout)

        layout.addWidget(assessment_group)

        # Special considerations
        special_group = QGroupBox("Special Considerations (Optional)")
        special_layout = QVBoxLayout(special_group)

        self.hazards_kitchen = QCheckBox("Commercial kitchen")
        self.hazards_mechanical = QCheckBox("Large mechanical rooms")
        self.hazards_storage = QCheckBox("Hazardous material storage")
        self.hazards_datacenter = QCheckBox("Data center/server room")

        for checkbox in [
            self.hazards_kitchen,
            self.hazards_mechanical,
            self.hazards_storage,
            self.hazards_datacenter,
        ]:
            checkbox.toggled.connect(self._on_assessment_changed)
            special_layout.addWidget(checkbox)

        layout.addWidget(special_group)

        # System recommendations display
        self.recommendations_display = QTextEdit()
        self.recommendations_display.setMaximumHeight(120)
        self.recommendations_display.setStyleSheet(
            """
            background-color: #f8f9fa;
            border: 2px solid #28a745;
            border-radius: 6px;
            padding: 10px;
            font-family: 'Segoe UI', Arial, sans-serif;
        """
        )
        self.recommendations_display.setPlainText(
            "Complete the building assessment above to see intelligent system recommendations..."
        )

        layout.addWidget(QLabel("💡 Intelligent System Recommendations:"))
        layout.addWidget(self.recommendations_display)

        layout.addStretch()
        self.tab_widget.addTab(widget, "1. Building Assessment")

    def _setup_panel_selection_tab(self):
        """Setup Step 2: Panel Selection."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Panel selection guidance
        guidance = QLabel(
            "<h3>🔧 Fire Alarm Control Panel Selection</h3>"
            + "<p>Based on your building assessment, we'll recommend the most appropriate "
            + "control panel.</p>"
            + (
                '<p>The panel is the "brain" of your fire alarm system and must have adequate '
                + "capacity for your building.</p>"
            )
        )
        guidance.setWordWrap(True)
        guidance.setStyleSheet(
            "background-color: #fff3cd; padding: 15px; border-radius: 6px; margin-bottom: 15px;"
        )
        layout.addWidget(guidance)

        # Recommended panels
        self.panel_recommendations = QGroupBox("Recommended Panels for Your Building")
        self.panel_layout = QVBoxLayout(self.panel_recommendations)
        layout.addWidget(self.panel_recommendations)

        # Selected panel display
        self.selected_panel_display = QGroupBox("Selected Panel")
        self.selected_panel_layout = QVBoxLayout(self.selected_panel_display)
        self.selected_panel_display.setVisible(False)
        layout.addWidget(self.selected_panel_display)

        layout.addStretch()
        self.tab_widget.addTab(widget, "2. Panel Selection")

    def _setup_device_planning_tab(self):
        """Setup Step 3: Device Planning."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        guidance = QLabel(
            """
        <h3>🔍 Detection & Notification Device Planning</h3>
        <p>Now we'll plan the detection devices (smoke/heat detectors) and notification devices
        (horns/strobes) based on your building type and selected panel capabilities.</p>
        """
        )
        guidance.setWordWrap(True)
        guidance.setStyleSheet(
            "background-color: #d1ecf1; padding: 15px; border-radius: 6px; margin-bottom: 15px;"
        )
        layout.addWidget(guidance)

        # Device recommendations will be populated dynamically
        self.device_recommendations = QGroupBox("Recommended Devices")
        self.device_rec_layout = QVBoxLayout(self.device_recommendations)
        layout.addWidget(self.device_recommendations)

        layout.addStretch()
        self.tab_widget.addTab(widget, "3. Device Planning")

    def _setup_wire_planning_tab(self):
        """Setup Step 4: Wire Planning."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        guidance = QLabel(
            "<h3>🔌 Circuit & Wiring Planning</h3>"
            + "<p>Based on your selected devices, we'll specify the appropriate wire types and "
            + "circuit configurations to ensure reliable communication and code compliance.</p>"
        )
        guidance.setWordWrap(True)
        guidance.setStyleSheet(
            "background-color: #d4edda; padding: 15px; border-radius: 6px; margin-bottom: 15px;"
        )
        layout.addWidget(guidance)

        # Wire recommendations will be populated dynamically
        self.wire_recommendations = QGroupBox("Recommended Wiring")
        self.wire_rec_layout = QVBoxLayout(self.wire_recommendations)
        layout.addWidget(self.wire_recommendations)

        layout.addStretch()
        self.tab_widget.addTab(widget, "4. Wire Planning")

    def _setup_system_review_tab(self):
        """Setup Step 5: System Review."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        guidance = QLabel(
            """
        <h3>✅ System Review & Completion</h3>
        <p>Review your complete fire alarm system design. We'll verify code compliance
        and provide a complete bill of materials.</p>
        """
        )
        guidance.setWordWrap(True)
        guidance.setStyleSheet(
            "background-color: #d1ecf1; padding: 15px; border-radius: 6px; margin-bottom: 15px;"
        )
        layout.addWidget(guidance)

        # System summary will be populated dynamically
        self.system_summary = QGroupBox("Complete System Summary")
        self.summary_layout = QVBoxLayout(self.system_summary)
        layout.addWidget(self.system_summary)

        layout.addStretch()
        self.tab_widget.addTab(widget, "5. System Review")

    def _start_workflow(self):
        """Initialize the workflow."""
        # Disable all tabs except the first
        for i in range(1, self.tab_widget.count()):
            self.tab_widget.setTabEnabled(i, False)

        # Set initial state
        self.current_step = 0
        self._update_step_indicators()
        self._update_navigation()

    def _on_assessment_changed(self):
        """Handle changes to building assessment."""
        # Update assessment data
        self.assessment.building_type = self.building_type.currentText()
        self.assessment.size_sqft = self.building_size.value()
        self.assessment.floors = self.floors.value()
        self.assessment.occupancy_level = self.occupancy.currentText()

        # Update special hazards
        self.assessment.special_hazards = []
        if self.hazards_kitchen.isChecked():
            self.assessment.special_hazards.append("kitchen")
        if self.hazards_mechanical.isChecked():
            self.assessment.special_hazards.append("mechanical")
        if self.hazards_storage.isChecked():
            self.assessment.special_hazards.append("hazardous_storage")
        if self.hazards_datacenter.isChecked():
            self.assessment.special_hazards.append("datacenter")

        # Generate recommendations
        if not self.assessment.building_type.startswith("Select"):
            self._generate_system_recommendations()
            self._enable_next_step()

    def _generate_system_recommendations(self):
        """Generate intelligent system recommendations."""
        assessment = self.assessment
        recommendations = []

        # Panel recommendations
        if assessment.size_sqft < 5000:
            panel_rec = (
                "📟 **Conventional Panel Recommended**\\n"
                "- Cost-effective for smaller buildings\\n"
                "- 2-8 zones typical\\n"
                "- Manual device addressing"
            )
            self.recommendations.panel_type = "conventional"
            self.recommendations.panel_zones = min(4, max(2, assessment.floors * 2))
        elif assessment.size_sqft < 25000:
            panel_rec = (
                "📟 **Addressable Panel Recommended**\\n"
                "- Better monitoring and diagnostics\\n"
                "- Individual device addressing\\n"
                "- Reduced installation time"
            )
            self.recommendations.panel_type = "addressable"
            self.recommendations.panel_zones = min(8, max(4, assessment.floors * 2))
        else:
            panel_rec = (
                "📟 **Networked Addressable System Recommended**\\n"
                "- Multiple panels with network capability\\n"
                "- Advanced monitoring and control\\n"
                "- Scalable for future expansion"
            )
            self.recommendations.panel_type = "networked"
            self.recommendations.panel_zones = max(8, assessment.floors * 3)

        recommendations.append(panel_rec)

        # Device recommendations
        if "Office" in assessment.building_type:
            device_rec = (
                "🔍 **Detection Strategy**\\n"
                "- Photoelectric smoke detectors in offices\\n"
                "- Heat detectors in mechanical/storage areas\\n"
                "- Standard 30ft spacing"
            )
            self.recommendations.device_count_estimate = {
                "smoke_detectors": max(assessment.size_sqft // 900, assessment.floors * 2),
                "heat_detectors": assessment.floors,
                "pull_stations": max(assessment.floors * 2, 2),
                "horn_strobes": max(assessment.size_sqft // 2500, assessment.floors * 2),
            }
        elif "Industrial" in assessment.building_type:
            device_rec = (
                "🔍 **Detection Strategy**\\n"
                "- Heat detectors primary (high ceiling/dust)\\n"
                "- Smoke detectors in office areas only\\n"
                "- Enhanced spacing for ceiling height"
            )
            self.recommendations.device_count_estimate = {
                "heat_detectors": max(assessment.size_sqft // 900, assessment.floors * 3),
                "smoke_detectors": max(assessment.size_sqft // 3000, 2),
                "pull_stations": max(assessment.floors * 2, 3),
                "horn_strobes": max(assessment.size_sqft // 2000, assessment.floors * 3),
            }
        else:
            device_rec = (
                "🔍 **Detection Strategy**\\n"
                "- Mixed smoke/heat detection per NFPA 72\\n"
                "- Standard commercial spacing\\n"
                "- Code-compliant notification coverage"
            )
            self.recommendations.device_count_estimate = {
                "smoke_detectors": max(assessment.size_sqft // 900, assessment.floors * 2),
                "heat_detectors": max(assessment.floors, 1),
                "pull_stations": max(assessment.floors * 2, 2),
                "horn_strobes": max(assessment.size_sqft // 2500, assessment.floors * 2),
            }

        recommendations.append(device_rec)

        # Notification recommendations
        if "High-Occupancy" in assessment.occupancy_level:
            notif_rec = (
                "🔊 **Notification Requirements**\\n"
                "- Voice evacuation system required\\n"
                "- Enhanced audible/visual coverage\\n"
                "- Emergency communication capability"
            )
            self.recommendations.compliance_notes.append(
                "Voice evacuation system required for high-occupancy"
            )
        else:
            notif_rec = (
                "🔊 **Notification Requirements**\\n"
                "- Standard horn/strobe notification\\n"
                "- ADA-compliant visual devices\\n"
                "- Adequate sound pressure levels"
            )

        recommendations.append(notif_rec)

        # Code compliance notes
        compliance = []
        special_hazards = assessment.special_hazards or []
        if assessment.floors > 3:
            compliance.append("🏢 High-rise provisions may apply (verify with AHJ)")
        if "kitchen" in special_hazards:
            compliance.append("🍳 Kitchen suppression system integration required")
        if "datacenter" in special_hazards:
            compliance.append("💻 Pre-action sprinkler coordination required")

        if compliance:
            compliance_rec = "📋 **Code Compliance Notes**\\n" + "\\n".join(
                f"- {note}" for note in compliance
            )
            recommendations.append(compliance_rec)
            if self.recommendations.compliance_notes is not None:
                self.recommendations.compliance_notes.extend(compliance)

        # Update display
        recommendations_text = "\\n\\n".join(recommendations)
        self.recommendations_display.setPlainText(recommendations_text.replace("\\n", "\n"))

    def _enable_next_step(self):
        """Enable the next step in the workflow."""
        self.next_btn.setEnabled(True)
        self._update_guidance("✅ Assessment complete! Click 'Next' to proceed to panel selection.")

    def _go_next(self):
        """Proceed to the next step."""
        if self.current_step < self.tab_widget.count() - 1:
            self.current_step += 1
            self.tab_widget.setTabEnabled(self.current_step, True)
            self.tab_widget.setCurrentIndex(self.current_step)
            self._update_step_indicators()
            self._update_navigation()
            self._populate_current_step()

    def _go_back(self):
        """Go back to the previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            self.tab_widget.setCurrentIndex(self.current_step)
            self._update_step_indicators()
            self._update_navigation()

    def _update_step_indicators(self):
        """Update the visual step indicators."""
        for i, indicator in enumerate(self.step_indicators):
            if i == self.current_step:
                # Current step
                indicator.setStyleSheet(
                    """
                    color: white;
                    font-weight: bold;
                    padding: 5px 10px;
                    border-radius: 15px;
                    background-color: rgba(255,255,255,0.3);
                    border: 2px solid white;
                """
                )
            elif i < self.current_step:
                # Completed step
                indicator.setStyleSheet(
                    """
                    color: #28a745;
                    font-weight: bold;
                    padding: 5px 10px;
                    border-radius: 15px;
                    background-color: rgba(40,167,69,0.2);
                    border: 2px solid #28a745;
                """
                )
            else:
                # Future step
                indicator.setStyleSheet(
                    """
                    color: rgba(255,255,255,0.6);
                    font-weight: normal;
                    padding: 5px 10px;
                    border-radius: 15px;
                    background-color: transparent;
                """
                )

        # Update progress bar
        self.progress_bar.setValue(self.current_step + 1)

    def _update_navigation(self):
        """Update navigation button states."""
        self.back_btn.setEnabled(self.current_step > 0)

        if self.current_step == self.tab_widget.count() - 1:
            # Last step - show complete button
            self.next_btn.setVisible(False)
            self.complete_btn.setVisible(True)
        else:
            # Not last step - show next button
            self.next_btn.setVisible(True)
            self.complete_btn.setVisible(False)
            # Enable next only if current step is valid
            self.next_btn.setEnabled(self._is_current_step_complete())

    def _is_current_step_complete(self):
        """Check if current step has required information."""
        if self.current_step == 0:
            # Assessment step
            return not self.assessment.building_type.startswith("Select")
        elif self.current_step == 1:
            # Panel selection step
            return self.selected_panel is not None
        elif self.current_step == 2:
            # Device planning step
            return len(self.selected_devices) > 0
        elif self.current_step == 3:
            # Wire planning step
            return len(self.selected_wires) > 0
        else:
            return True

    def _populate_current_step(self):
        """Populate the current step with relevant data."""
        if self.current_step == 1:
            self._populate_panel_selection()
        elif self.current_step == 2:
            self._populate_device_planning()
        elif self.current_step == 3:
            self._populate_wire_planning()
        elif self.current_step == 4:
            self._populate_system_review()

    def _populate_panel_selection(self):
        """Populate panel selection options."""
        # Clear existing panels
        for i in reversed(range(self.panel_layout.count())):
            self.panel_layout.itemAt(i).widget().setParent(None)

        # Filter panels based on recommendations
        recommended_panels = self._get_recommended_panels()

        if not recommended_panels:
            no_panels = QLabel(
                "⚠️ No suitable panels found in catalog. "
                + "Please ensure your device catalog is properly populated."
            )
            no_panels.setStyleSheet("color: #dc3545; padding: 10px;")
            self.panel_layout.addWidget(no_panels)
            return

        for panel in recommended_panels:
            panel_widget = self._create_panel_option(panel)
            self.panel_layout.addWidget(panel_widget)

        self._update_guidance(
            "Select the fire alarm control panel that best fits your building requirements."
        )

    def _get_recommended_panels(self):
        """Get panels that match the recommendations."""
        recommended = []

        for device in self.device_catalog:
            if device.get("type", "").lower() in ["panel", "facp", "control"]:
                # Simple matching for now - in real implementation,
                # would have detailed specifications
                recommended.append(device)

        return recommended[:3]  # Limit to top 3 recommendations

    def _create_panel_option(self, panel):
        """Create a selectable panel option widget."""
        widget = QWidget()
        widget.setStyleSheet(
            """
            QWidget {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
                background-color: white;
            }
            QWidget:hover {
                border-color: #007bff;
                background-color: #f8f9fa;
            }
        """
        )

        layout = QVBoxLayout(widget)

        # Panel name and model
        name_label = QLabel(f"<b>{panel['name']}</b>")
        model_label = QLabel(
            "Model: "
            + str(panel.get("model", ""))
            + " | Manufacturer: "
            + str(panel.get("manufacturer", ""))
        )
        model_label.setStyleSheet("color: #6c757d; font-size: 11px;")

        # Recommendation reason
        reason = self._get_panel_recommendation_reason(panel)
        reason_label = QLabel(f"💡 {reason}")
        reason_label.setStyleSheet("color: #28a745; font-size: 11px; font-style: italic;")
        reason_label.setWordWrap(True)

        # Select button
        select_btn = QPushButton("Select This Panel")
        select_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """
        )
        select_btn.clicked.connect(lambda: self._select_panel(panel))

        layout.addWidget(name_label)
        layout.addWidget(model_label)
        layout.addWidget(reason_label)
        layout.addWidget(select_btn)

        return widget

    def _get_panel_recommendation_reason(self, panel):
        """Get the reason why this panel is recommended."""
        reasons = []

        if self.recommendations.panel_type == "conventional":
            reasons.append("Cost-effective conventional design")
        elif self.recommendations.panel_type == "addressable":
            reasons.append("Addressable technology for enhanced monitoring")
        else:
            reasons.append("Advanced networking capability")

        if self.assessment.size_sqft < 10000:
            reasons.append("Right-sized for your building")
        else:
            reasons.append("Adequate capacity for large building")

        return " • ".join(reasons)

    def _select_panel(self, panel):
        """Select a panel and update the UI."""
        self.selected_panel = panel

        # Update selected panel display
        self.selected_panel_display.setVisible(True)

        # Clear existing content
        for i in reversed(range(self.selected_panel_layout.count())):
            self.selected_panel_layout.itemAt(i).widget().setParent(None)

        # Add selected panel info
        selected_info = QLabel(
            f"""
        <b>Selected Panel:</b> {panel['name']}<br>
        <b>Model:</b> {panel['model']}<br>
        <b>Manufacturer:</b> {panel['manufacturer']}<br>
        ✅ This panel meets your building requirements.
        """
        )
        selected_info.setStyleSheet("background-color: #d4edda; padding: 10px; border-radius: 4px;")
        self.selected_panel_layout.addWidget(selected_info)

        # Enable next step
        self._update_navigation()
        self._update_guidance(
            "✅ Panel selected! Click 'Next' to plan your detection and notification devices."
        )

    def _populate_device_planning(self):
        """Populate device planning based on selected panel and assessment."""
        # Clear existing content
        for i in reversed(range(self.device_rec_layout.count())):
            self.device_rec_layout.itemAt(i).widget().setParent(None)

        # Create device categories
        device_categories = [
            ("🔍 Detection Devices", self._get_detection_devices()),
            ("🔊 Notification Devices", self._get_notification_devices()),
            ("🚨 Initiating Devices", self._get_initiating_devices()),
        ]

        for category_name, devices in device_categories:
            if devices:
                category_group = QGroupBox(category_name)
                category_layout = QVBoxLayout(category_group)

                for device in devices:
                    device_widget = self._create_device_option(device)
                    category_layout.addWidget(device_widget)

                self.device_rec_layout.addWidget(category_group)

        self._update_guidance(
            "Select the devices your system needs. "
            + "Recommendations are based on your building type "
            + "and code requirements."
        )

    def _get_detection_devices(self):
        """Get recommended detection devices."""
        detection_devices = []
        for device in self.device_catalog:
            if device.get("type", "").lower() in ["detector", "detection"]:
                detection_devices.append(device)
        return detection_devices

    def _get_notification_devices(self):
        """Get recommended notification devices."""
        notification_devices = []
        for device in self.device_catalog:
            if device.get("type", "").lower() in ["notification", "horn", "strobe", "speaker"]:
                notification_devices.append(device)
        return notification_devices

    def _get_initiating_devices(self):
        """Get recommended initiating devices."""
        initiating_devices = []
        for device in self.device_catalog:
            if device.get("type", "").lower() in ["initiating", "pull", "station"]:
                initiating_devices.append(device)
        return initiating_devices

    def _create_device_option(self, device):
        """Create a selectable device option."""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Device info
        info_layout = QVBoxLayout()
        name_label = QLabel("<b>" + device.get("name", "") + "</b>")
        model_label = QLabel(
            str(device.get("model", "")) + " - " + str(device.get("manufacturer", ""))
        )
        model_label.setStyleSheet("color: #6c757d; font-size: 10px;")

        info_layout.addWidget(name_label)
        info_layout.addWidget(model_label)

        # Estimated quantity
        estimated_qty = self._estimate_device_quantity(device)
        qty_label = QLabel(f"Estimated: {estimated_qty}")
        qty_label.setStyleSheet("color: #28a745; font-weight: bold;")

        # Add button
        add_btn = QPushButton("Add to System")
        add_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """
        )
        add_btn.clicked.connect(lambda: self._add_device(device, estimated_qty))

        layout.addLayout(info_layout)
        layout.addWidget(qty_label)
        layout.addWidget(add_btn)

        return widget

    def _estimate_device_quantity(self, device):
        """Estimate quantity needed for this device type."""
        device_name = device["name"].lower()
        device_estimates = self.recommendations.device_count_estimate or {}

        if "smoke" in device_name:
            return device_estimates.get("smoke_detectors", 1)
        elif "heat" in device_name:
            return device_estimates.get("heat_detectors", 1)
        elif "pull" in device_name or "station" in device_name:
            return device_estimates.get("pull_stations", 1)
        elif any(x in device_name for x in ["horn", "strobe", "speaker"]):
            return device_estimates.get("horn_strobes", 1)
        else:
            return 1

    def _add_device(self, device, quantity):
        """Add a device to the selected devices list."""
        device_entry = {
            "device": device,
            "quantity": quantity,
            "rationale": self._get_device_rationale(device),
        }

        self.selected_devices.append(device_entry)
        self._update_navigation()

        # Update guidance
        if len(self.selected_devices) == 1:
            self._update_guidance(
                "Great! Continue adding devices as needed, then click 'Next' for wire planning."
            )
        else:
            self._update_guidance(
                "✅ Added "
                + device.get("name", "")
                + ". Total devices: "
                + str(len(self.selected_devices))
                + ". Continue adding or proceed to wire planning."
            )

    def _get_device_rationale(self, device):
        """Get the rationale for including this device."""
        device_name = device["name"].lower()

        if "smoke" in device_name:
            return "Required for early fire detection in occupied spaces"
        elif "heat" in device_name:
            return "Required for detection in areas where smoke detectors may false alarm"
        elif "pull" in device_name:
            return "Required for manual fire alarm initiation"
        elif "horn" in device_name or "strobe" in device_name:
            return "Required for occupant notification and evacuation"
        else:
            return "Recommended for complete fire protection coverage"

    def _populate_wire_planning(self):
        """Populate wire planning based on selected devices."""
        # Implementation would analyze selected devices and recommend appropriate wiring
        pass

    def _populate_system_review(self):
        """Populate the final system review."""
        # Implementation would show complete system summary
        pass

    def _on_tab_clicked(self, index):
        """Handle direct tab clicks (only allow if tab is enabled)."""
        if not self.tab_widget.isTabEnabled(index):
            # Reset to current step if user tries to click disabled tab
            self.tab_widget.setCurrentIndex(self.current_step)

    def _update_guidance(self, message):
        """Update the guidance message."""
        self.guidance_label.setText(f"💡 {message}")

    def _complete_system(self):
        """Complete the system and emit the result."""
        system_data = {
            "assessment": asdict(self.assessment),
            "recommendations": asdict(self.recommendations),
            "selected_panel": self.selected_panel,
            "selected_devices": self.selected_devices,
            "selected_wires": self.selected_wires,
        }

        # Emit both new and old signals for compatibility
        self.system_completed.emit(system_data)
        self.assembled.emit(system_data)  # Backward compatibility
        self._update_guidance(
            "🎉 System design complete! Your fire alarm system is ready for implementation."
        )

    def _assemble_system(self):
        """Backward compatibility method for old system."""
        self._complete_system()

    def _load_device_catalog(self):
        """Load device catalog from database."""
        try:
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "autofire.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT d.id, m.name as manufacturer, dt.code as type, d.model, d.name, d.symbol
                FROM devices d
                LEFT JOIN manufacturers m ON m.id = d.manufacturer_id
                LEFT JOIN device_types dt ON dt.id = d.type_id
                WHERE d.name IS NOT NULL AND d.name != ''
                ORDER BY m.name, dt.code, d.name
            """
            )

            devices = []
            for row in cursor.fetchall():
                devices.append(
                    {
                        "id": row[0],
                        "manufacturer": row[1] or "Unknown",
                        "type": row[2] or "Unknown",
                        "model": row[3] or "",
                        "name": row[4] or "Unnamed Device",
                        "symbol": row[5] or "?",
                    }
                )

            conn.close()
            return devices
        except Exception as e:
            print(f"Error loading device catalog: {e}")
            return self._get_fallback_devices()

    def _get_fallback_devices(self):
        """Fallback device list if database fails."""
        return [
            {
                "id": 1,
                "manufacturer": "Fire-Lite",
                "type": "Panel",
                "model": "NFS2-3030",
                "name": "Fire Alarm Control Panel",
                "symbol": "FACP",
            },
            {
                "id": 2,
                "manufacturer": "System Sensor",
                "type": "Detector",
                "model": "2WT-B",
                "name": "Smoke Detector",
                "symbol": "SD",
            },
            {
                "id": 3,
                "manufacturer": "System Sensor",
                "type": "Detector",
                "model": "5602",
                "name": "Heat Detector",
                "symbol": "HD",
            },
            {
                "id": 4,
                "manufacturer": "Wheelock",
                "type": "Notification",
                "model": "AS-24MCW",
                "name": "Horn Strobe",
                "symbol": "HS",
            },
            {
                "id": 5,
                "manufacturer": "Edwards",
                "type": "Initiating",
                "model": "270-SPO",
                "name": "Pull Station",
                "symbol": "PS",
            },
        ]
