"""
Improved Guided System Builder - Better Layout and Usability

This version fixes the window cascading and scrolling issues by using:
- Proper scroll areas
- Better window management
- Cleaner layout without nested complex widgets
- More responsive design
- Real database integration for panel selection
- Comprehensive logging for user decisions
"""

import logging
import os
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from frontend.utils.manufacturer_aliases import normalize_manufacturer

# Set up logging for system builder decisions
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SystemBuilder")


@dataclass
class ProjectAssessment:
    """Project assessment data."""

    project_type: str = ""
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


class ImprovedGuidedSystemBuilder(QWidget):
    """
    Improved Guided System Builder with better usability.

    Fixes:
    - No more cascading windows
    - Proper scrolling
    - Better layout management
    - Cleaner, more responsive design
    """

    # Signals
    system_completed = Signal(dict)
    step_changed = Signal(int)
    assembled = Signal(dict)  # Backward compatibility
    staging_changed = Signal()  # Backward compatibility
    panel_selected = Signal(dict)  # Panel selection signal

    def __init__(self, parent=None):
        super().__init__(parent)

        # Workflow state
        self.current_step = 0
        self.assessment = ProjectAssessment()
        self.recommendations = SystemRecommendation()
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
        """Setup improved UI with better layout management."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header (fixed at top)
        header = self._create_header()
        layout.addWidget(header)

        # Main content area with stacked widget (much better than tabs for this)
        self.content_stack = QStackedWidget()
        self.content_stack.setMinimumHeight(400)

        # Create all workflow pages
        self._create_welcome_page()
        self._create_assessment_page()
        self._create_panel_page()
        self._create_power_supply_page()
        self._create_nac_booster_page()
        self._create_device_page()
        self._create_wire_page()
        self._create_review_page()

        layout.addWidget(self.content_stack)

        # Navigation footer (fixed at bottom)
        footer = self._create_navigation_footer()
        layout.addWidget(footer)

        # Set initial state
        self.content_stack.setCurrentIndex(0)

    def _create_header(self):
        """Create compact header with progress."""
        header = QFrame()
        header.setFrameStyle(QFrame.Shape.StyledPanel)
        header.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #34495e);
                border-radius: 6px;
                padding: 8px;
                border: 1px solid #34495e;
            }
        """
        )
        header.setMaximumHeight(120)

        layout = QVBoxLayout(header)
        layout.setContentsMargins(15, 10, 15, 10)

        # Title
        title = QLabel("🚨 Fire Alarm System Builder")
        title.setStyleSheet(
            """
            color: #ffffff;
            font-size: 20px;
            font-weight: 900;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
        """
        )
        layout.addWidget(title)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(6)
        self.progress_bar.setValue(1)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #ffffff;
                border-radius: 8px;
                background-color: rgba(255,255,255,0.15);
                height: 18px;
                color: #ffffff;
                font-weight: bold;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 6px;
            }
        """
        )
        layout.addWidget(self.progress_bar)

        # Step indicator
        steps_layout = QHBoxLayout()
        steps = ["🏠 Welcome", "📋 Assess", "🔧 Panel", "🔍 Devices", "🔌 Wiring", "✅ Review"]

        self.step_labels = []
        for i, step in enumerate(steps):
            label = QLabel(step)
            label.setStyleSheet(
                f"""
                color: {'#ffffff' if i == 0 else '#d5dbdb'};
                font-weight: {'900' if i == 0 else '600'};
                padding: 8px 12px;
                border-radius: 18px;
                background-color: {'rgba(255,255,255,0.25)' if i == 0 else 'rgba(255,255,255,0.1)'};
                font-size: 12px;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                border: {'2px solid #ffffff' if i == 0 else '1px solid rgba(255,255,255,0.3)'};
            """
            )
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.step_labels.append(label)
            steps_layout.addWidget(label)

        layout.addLayout(steps_layout)

        # Guidance
        self.guidance_label = QLabel(
            "Welcome to AutoFire! Start a new project or load recent work..."
        )
        self.guidance_label.setStyleSheet(
            """
            color: #ffffff;
            font-style: normal;
            font-weight: 600;
            padding: 10px 15px;
            background-color: rgba(255,255,255,0.2);
            border-radius: 8px;
            font-size: 15px;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            border: 1px solid rgba(255,255,255,0.3);
        """
        )
        self.guidance_label.setWordWrap(True)
        layout.addWidget(self.guidance_label)

        return header

    def _create_assessment_page(self):
        """Create project assessment page with proper scrolling."""
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Welcome section
        welcome_html = "".join(
            [
                '<h3 style="color: #1a252f; margin-bottom: 10px; '
                'font-size: 18px; font-weight: 900;">🏢 Project Assessment</h3>',
                '<p style="color: #2c3e50; font-size: 16px; line-height: 1.5; '
                'font-weight: 600;">',
                "Help us understand your project to provide the best fire alarm "
                "system recommendations. ",
                "This assessment ensures your system meets code requirements and "
                "project-specific needs.",
                "</p>",
            ]
        )
        welcome = QLabel(welcome_html)
        welcome.setWordWrap(True)
        welcome.setStyleSheet(
            "".join(
                [
                    "background-color: #e8f4f8;",
                    "padding: 25px;",
                    "border-radius: 10px;",
                    "border-left: 6px solid #2980b9;",
                    "border: 2px solid #85c1e9;",
                    "font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;",
                ]
            )
        )
        layout.addWidget(welcome)

        # Project info form
        project_group = QGroupBox("Project Information")
        project_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: 900;
                padding-top: 18px;
                color: #1a252f;
                font-size: 16px;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                border: 3px solid #85c1e9;
                border-radius: 10px;
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 12px 0 12px;
                color: #1a252f;
                background-color: #ffffff;
                font-weight: 900;
            }
        """
        )
        project_layout = QFormLayout(project_group)
        project_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # Project type
        self.building_type = QComboBox()
        self.building_type.addItems(
            [
                "Select project type...",
                "🏢 Office Building",
                "🏭 Industrial/Manufacturing",
                "🏫 School/Educational",
                "🏥 Healthcare Facility",
                "🏨 Hotel/Hospitality",
                "🏪 Retail/Mercantile",
                "🏠 Residential Building",
                "🏛️ Assembly Occupancy",
                "📦 Storage/Warehouse",
            ]
        )
        self.building_type.setStyleSheet(
            """
            QComboBox {
                background-color: #ffffff;
                border: 3px solid #85c1e9;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 15px;
                font-weight: 600;
                min-height: 25px;
            }
            QComboBox:focus {
                border-color: #2980b9;
                background-color: #f8fdff;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #34495e;
                margin-right: 8px;
            }
        """
        )
        self.building_type.currentTextChanged.connect(self._on_assessment_changed)

        # Create bold label
        project_type_label = QLabel("Project Type:")
        project_type_label.setStyleSheet(
            """
            color: #1a252f;
            font-weight: 900;
            font-size: 15px;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
        """
        )
        project_layout.addRow(project_type_label, self.building_type)

        # Size and floors in same row
        size_floors_layout = QHBoxLayout()

        self.building_size = QSpinBox()
        self.building_size.setRange(500, 999999)
        self.building_size.setValue(10000)
        self.building_size.setSuffix(" sq ft")
        self.building_size.setStyleSheet(
            """
            QSpinBox {
                background-color: #ffffff;
                border: 3px solid #85c1e9;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 15px;
                color: #1a252f;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                font-weight: 600;
                min-height: 25px;
            }
            QSpinBox:focus {
                border-color: #2980b9;
                background-color: #f8fdff;
            }
        """
        )
        self.building_size.valueChanged.connect(self._on_assessment_changed)

        self.floors = QSpinBox()
        self.floors.setRange(1, 50)
        self.floors.setValue(1)
        self.floors.setStyleSheet(
            """
            QSpinBox {
                background-color: #ffffff;
                border: 3px solid #85c1e9;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 15px;
                color: #1a252f;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                font-weight: 600;
                min-height: 25px;
            }
            QSpinBox:focus {
                border-color: #2980b9;
                background-color: #f8fdff;
            }
        """
        )
        self.floors.valueChanged.connect(self._on_assessment_changed)

        size_label = QLabel("Size:")
        size_label.setStyleSheet(
            """
            color: #1a252f;
            font-weight: 900;
            font-size: 15px;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
        """
        )
        floors_label = QLabel("Floors:")
        floors_label.setStyleSheet(
            """
            color: #1a252f;
            font-weight: 900;
            font-size: 15px;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
        """
        )

        size_floors_layout.addWidget(size_label)
        size_floors_layout.addWidget(self.building_size)
        size_floors_layout.addWidget(floors_label)
        size_floors_layout.addWidget(self.floors)
        size_floors_layout.addStretch()

        # Create bold label for the row
        size_floors_label = QLabel("Building Size & Floors:")
        size_floors_label.setStyleSheet(
            """
            color: #1a252f;
            font-weight: 900;
            font-size: 15px;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
        """
        )
        project_layout.addRow(size_floors_label, size_floors_layout)

        # Occupancy
        self.occupancy = QComboBox()
        self.occupancy.addItems(
            [
                "Light (1-49 people)",
                "Moderate (50-299 people)",
                "Heavy (300-999 people)",
                "High-Occupancy (1000+ people)",
            ]
        )
        self.occupancy.setStyleSheet(
            """
            QComboBox {
                background-color: #ffffff;
                border: 3px solid #85c1e9;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 15px;
                color: #1a252f;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                font-weight: 600;
                min-height: 25px;
            }
            QComboBox:focus {
                border-color: #2980b9;
                background-color: #f8fdff;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #34495e;
                margin-right: 8px;
            }
        """
        )
        self.occupancy.currentTextChanged.connect(self._on_assessment_changed)

        # Create bold label
        occupancy_label = QLabel("Occupant Load:")
        occupancy_label.setStyleSheet(
            """
            color: #1a252f;
            font-weight: 900;
            font-size: 15px;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
        """
        )
        project_layout.addRow(occupancy_label, self.occupancy)

        layout.addWidget(project_group)

        # Special considerations with much better visibility
        special_group = QGroupBox("⚠️ Special Areas - Check All That Apply")
        special_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: 900;
                padding-top: 20px;
                color: #8b2635;
                font-size: 16px;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                border: 3px solid #e7b10a;
                border-radius: 10px;
                margin-top: 15px;
                background-color: #fffbf0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 12px 0 12px;
                color: #8b2635;
                background-color: #fffbf0;
                font-weight: 900;
            }
        """
        )

        # Use vertical layout for better readability
        special_layout = QVBoxLayout(special_group)
        special_layout.setSpacing(12)
        special_layout.setContentsMargins(20, 25, 20, 20)

        # Create checkboxes with much better styling
        self.hazards_kitchen = QCheckBox("🍳 Commercial Kitchen Areas")
        self.hazards_mechanical = QCheckBox("⚙️ Mechanical/Electrical Rooms")
        self.hazards_storage = QCheckBox("🧪 Hazardous Material Storage")
        self.hazards_datacenter = QCheckBox("💻 Data Center/Server Rooms")

        # Much more visible checkbox styling
        checkbox_style = """
            QCheckBox {
                color: #1a252f;
                font-size: 16px;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                font-weight: 700;
                spacing: 15px;
                padding: 8px 12px;
                background-color: #ffffff;
                border-radius: 6px;
                border: 2px solid #e7b10a;
                margin: 2px;
            }
            QCheckBox:hover {
                background-color: #fffbf0;
                border-color: #d4ac0d;
            }
            QCheckBox::indicator {
                width: 28px;
                height: 28px;
                border: 4px solid #e7b10a;
                border-radius: 6px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:hover {
                border-color: #d4ac0d;
                background-color: #fffbf0;
            }
            QCheckBox::indicator:checked {
                background-color: #e67e22;
                border-color: #d35400;
                image: none;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #d35400;
            }
        """

        self.special_hazards_checkboxes = [
            self.hazards_kitchen,
            self.hazards_mechanical,
            self.hazards_storage,
            self.hazards_datacenter,
        ]

        for checkbox in self.special_hazards_checkboxes:
            checkbox.setStyleSheet(checkbox_style)
            checkbox.toggled.connect(self._on_assessment_changed)
            special_layout.addWidget(checkbox)

        layout.addWidget(special_group)

        # Recommendations (compact)
        rec_group = QGroupBox("💡 System Recommendations")
        rec_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: 900;
                padding-top: 18px;
                color: #0d5016;
                font-size: 16px;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                border: 3px solid #82e89a;
                border-radius: 10px;
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 12px 0 12px;
                color: #0d5016;
                background-color: #ffffff;
                font-weight: 900;
            }
        """
        )
        rec_layout = QVBoxLayout(rec_group)

        self.recommendations_display = QTextEdit()
        self.recommendations_display.setMaximumHeight(160)
        self.recommendations_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #f0fdf4;
                border: 3px solid #82e89a;
                border-radius: 8px;
                padding: 15px;
                font-size: 15px;
                color: #0d5016;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                font-weight: 600;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border-color: #15803d;
                background-color: #ecfdf5;
            }
        """
        )
        self.recommendations_display.setPlainText(
            "Complete the assessment above to see recommendations..."
        )
        rec_layout.addWidget(self.recommendations_display)

        layout.addWidget(rec_group)

        layout.addStretch()

        # Set content in scroll area
        scroll_area.setWidget(content)
        self.content_stack.addWidget(scroll_area)

    def _create_panel_page(self):
        """Create a simple, intuitive panel selection page."""
        panel_page = self._create_simple_panel_selection()
        self.content_stack.addWidget(panel_page)

        # Your building summary
        self.building_summary_frame = QFrame()
        # Apply theme-aware styling using the same approach as other panels
        self.building_summary_frame.setStyleSheet(
            """
            QFrame {
                background-color: #3C3C3C;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                color: #FFFFFF;
            }
        """
        )
        summary_layout = QVBoxLayout(self.building_summary_frame)

        summary_title = QLabel("📋 Your Project Summary:")
        summary_title.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #C41E3A; margin-bottom: 8px;"
        )
        summary_layout.addWidget(summary_title)

        self.building_summary_text = QLabel("Loading project information...")
        self.building_summary_text.setStyleSheet(
            "font-size: 13px; color: #CCCCCC; margin-left: 10px;"
        )
        self.building_summary_text.setWordWrap(True)
        summary_layout.addWidget(self.building_summary_text)

        # Old method content removed - using simple selection interface

        # Recommended panels - simple categories
        rec_title = QLabel("🎯 Recommended Control Panels:")
        rec_title.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin: 20px 0 15px 0;
            font-family: 'Segoe UI', Arial, sans-serif;
        """
        )
        # Old method content removed - using simple selection interface

        # Container for recommended panels
        self.recommended_panels_widget = QWidget()
        self.recommended_panels_layout = QVBoxLayout(self.recommended_panels_widget)
        # layout.addWidget(self.recommended_panels_widget)  # Disabled due to undefined layout

        # Advanced section (collapsible)
        self.advanced_section = QFrame()
        self.advanced_section.setStyleSheet(
            """
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-top: 20px;
            }
        """
        )
        advanced_layout = QVBoxLayout(self.advanced_section)

        self.advanced_toggle_btn = QPushButton("🔧 Show All Panels (Advanced)")
        self.advanced_toggle_btn.setStyleSheet(
            """
            QPushButton {
                text-align: left;
                border: none;
                background: transparent;
                padding: 15px;
                font-size: 14px;
                color: #6c757d;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #495057;
                background-color: #e9ecef;
            }
        """
        )
        self.advanced_toggle_btn.clicked.connect(self._toggle_advanced_panels)
        advanced_layout.addWidget(self.advanced_toggle_btn)

        # Container for recommended panels
        self.recommended_panels_widget = QWidget()
        self.recommended_panels_layout = QVBoxLayout(self.recommended_panels_widget)
        # layout.addWidget(self.recommended_panels_widget)  # Disabled due to undefined layout

        # Advanced section (collapsible)
        self.advanced_section = QFrame()
        self.advanced_section.setStyleSheet(
            """
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-top: 20px;
            }
        """
        )
        advanced_layout = QVBoxLayout(self.advanced_section)

        self.advanced_toggle_btn = QPushButton("� Show All Panels (Advanced)")
        self.advanced_toggle_btn.setStyleSheet(
            """
            QPushButton {
                text-align: left;
                border: none;
                background: transparent;
                padding: 15px;
                font-size: 14px;
                color: #6c757d;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #495057;
                background-color: #e9ecef;
            }
        """
        )
        self.advanced_toggle_btn.clicked.connect(self._toggle_advanced_panels)
        advanced_layout.addWidget(self.advanced_toggle_btn)

        # Advanced grid (hidden initially)
        self.advanced_panels_widget = QWidget()
        self.advanced_panels_widget.hide()
        self.panel_grid_layout = QGridLayout(self.advanced_panels_widget)
        self.panel_grid_layout.setSpacing(10)
        advanced_layout.addWidget(self.advanced_panels_widget)

        # layout.addWidget(self.advanced_section)  # Disabled due to undefined layout

        # layout.addStretch()  # Disabled due to undefined layout

    def _create_simple_panel_selection(self):
        """Create SIMPLE dropdown-based panel selection."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("🎛️ Select Control Panel")
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;"
        )
        layout.addWidget(title)

        # Form
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)

        # 1. Manufacturer
        self.manufacturer_combo = QComboBox()
        # Dynamically populate canonical manufacturers from panels DB
        all_panels = self._get_all_panels_from_db()
        canonical_mfrs = set()
        for p in all_panels:
            canon = normalize_manufacturer(p.get("manufacturer", "Unknown"))
            if canon:
                canonical_mfrs.add(canon)
        mfr_list = ["Select Manufacturer..."] + sorted(canonical_mfrs)
        self.manufacturer_combo.addItems(mfr_list)
        self.manufacturer_combo.setStyleSheet("font-size: 14px; padding: 8px; min-height: 20px;")
        self.manufacturer_combo.currentTextChanged.connect(self._on_manufacturer_changed)
        form_layout.addRow("1. Manufacturer:", self.manufacturer_combo)

        # 2. Panel Type
        self.panel_type_combo = QComboBox()
        self.panel_type_combo.addItems(
            ["Select Type...", "Addressable", "Conventional", "Networked"]
        )
        self.panel_type_combo.setStyleSheet("font-size: 14px; padding: 8px; min-height: 20px;")
        self.panel_type_combo.setEnabled(False)
        self.panel_type_combo.currentTextChanged.connect(self._on_panel_type_changed)
        form_layout.addRow("2. Panel Type:", self.panel_type_combo)

        # 3. Model List
        self.model_list = QListWidget()
        self.model_list.setStyleSheet(
            """
            QListWidget {
                font-size: 14px;
                border: 1px solid #ccc;
                min-height: 120px;
                max-height: 200px;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """
        )
        self.model_list.itemClicked.connect(self._on_model_selected)
        form_layout.addRow("3. Model:", self.model_list)

        # Selection display
        self.selection_display = QLabel("Make selections above...")
        self.selection_display.setStyleSheet(
            """
            background-color: #f8f9fa;
            padding: 15px;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            margin: 10px 0;
        """
        )
        self.selection_display.setWordWrap(True)
        form_layout.addRow("Selected:", self.selection_display)

        layout.addWidget(form_widget)
        layout.addStretch()

        scroll_area.setWidget(content)
        return scroll_area

    def _on_manufacturer_changed(self, manufacturer):
        """Handle manufacturer selection."""
        if manufacturer == "Select Manufacturer...":
            self.panel_type_combo.setEnabled(False)
            self.model_list.clear()
            return

        # Enable panel type selection
        self.panel_type_combo.setEnabled(True)
        self.panel_type_combo.setCurrentIndex(0)
        self.model_list.clear()
        self._update_selection_display()

    def _on_panel_type_changed(self, panel_type):
        """Handle panel type selection."""
        if panel_type == "Select Type...":
            self.model_list.clear()
            return

        # Populate models based on manufacturer and type
        self._populate_models()
        self._update_selection_display()

    def _populate_models(self):
        """Populate model list based on manufacturer and type."""
        self.model_list.clear()

        manufacturer = self.manufacturer_combo.currentText()
        panel_type = self.panel_type_combo.currentText()

        if manufacturer == "Select Manufacturer..." or panel_type == "Select Type...":
            return

        # Get panels from database
        all_panels = self._get_all_panels_from_db()
        logger.info(
            "Filtering panels for manufacturer: '%s', found %d total panels",
            manufacturer,
            len(all_panels),
        )

        # Filter by canonical manufacturer
        filtered_panels = [
            p
            for p in all_panels
            if normalize_manufacturer(p.get("manufacturer", "")) == manufacturer
        ]
        logger.info("After canonical manufacturer filter: %d panels found", len(filtered_panels))
        # Debug: show first few panel manufacturers for troubleshooting
        if len(filtered_panels) == 0 and len(all_panels) > 0:
            sample_manufacturers = [
                p.get("manufacturer", "NO_MANUFACTURER") for p in all_panels[:5]
            ]
            logger.warning(
                "No panels found for '%s'. Sample database manufacturers: %s",
                manufacturer,
                sample_manufacturers,
            )
        # Add model items to list
        for panel in filtered_panels:
            model = panel.get("model", "Unknown Model")
            name = panel.get("name", panel.get("description", "Fire Alarm Control Panel"))
            item_text = f"{model} - {name}"
            self.model_list.addItem(item_text)
            # Store panel data with the item
            self.model_list.item(self.model_list.count() - 1).setData(
                Qt.ItemDataRole.UserRole, panel
            )

        if len(filtered_panels) > 0:
            logger.info("Added %d models to list", len(filtered_panels))

        # Remove unreachable/duplicate legacy filtering code below (if present)

    def _on_model_selected(self, item):
        """Handle model selection."""
        panel_data = item.data(Qt.ItemDataRole.UserRole)
        if panel_data:
            self.selected_panel = panel_data
            self.next_btn.setEnabled(True)
            self._update_selection_display()
            logger.info(
                f"Panel selected: {panel_data.get('manufacturer')} {panel_data.get('model')}"
            )

    def _update_selection_display(self):
        """Update the selection display."""
        manufacturer = self.manufacturer_combo.currentText()
        panel_type = self.panel_type_combo.currentText()

        if hasattr(self, "selected_panel") and self.selected_panel:
            canon = normalize_manufacturer(self.selected_panel.get("manufacturer"))
            text = f"✅ {canon} {self.selected_panel.get('model')} ({panel_type})"
            self.selection_display.setStyleSheet(
                """
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
                padding: 15px;
                border-radius: 4px;
                margin: 10px 0;
                font-weight: bold;
            """
            )
        elif manufacturer != "Select Manufacturer..." and panel_type != "Select Type...":
            text = f"📋 {manufacturer} - {panel_type} (Choose model above)"
            self.selection_display.setStyleSheet(
                """
                background-color: #fff3cd;
                color: #856404;
                border: 1px solid #ffeaa7;
                padding: 15px;
                border-radius: 4px;
                margin: 10px 0;
            """
            )
        else:
            text = "Make selections above..."
            self.selection_display.setStyleSheet(
                """
                background-color: #f8f9fa;
                padding: 15px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                margin: 10px 0;
            """
            )
        self.selection_display.setText(text)

    def _go_to_options_page(self):
        """Navigate to the options/expanders page."""
        if hasattr(self, "selected_panel") and self.selected_panel:
            logger.info(f"Proceeding with panel: {self.selected_panel}")
            # For now, emit a signal or handle panel selection completion
            self.panel_selected.emit(self.selected_panel)
        else:
            logger.warning("No panel selected when trying to proceed")

    def _create_power_supply_page(self):
        """Create power supply selection page."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("⚡ Select Power Supplies")
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;"
        )
        layout.addWidget(title)

        # Instructions
        instructions = QLabel("Choose additional power supplies needed for your system:")
        instructions.setStyleSheet("font-size: 14px; color: #34495e; margin-bottom: 20px;")
        layout.addWidget(instructions)

        # Power supply list
        self.power_supply_list = QListWidget()
        self.power_supply_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
                min-height: 200px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """
        )

        # Populate power supplies
        self._populate_power_supplies()
        layout.addWidget(self.power_supply_list)

        # Selection summary
        self.power_summary = QLabel("No power supplies selected")
        self.power_summary.setStyleSheet(
            """
            background-color: #f8f9fa;
            padding: 10px;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            margin: 10px 0;
        """
        )
        layout.addWidget(self.power_summary)

        layout.addStretch()
        scroll_area.setWidget(content)
        self.content_stack.addWidget(scroll_area)

    def _create_nac_booster_page(self):
        """Create NAC booster selection page."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("📡 Select NAC Boosters")
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;"
        )
        layout.addWidget(title)

        # Instructions
        instructions = QLabel("Choose NAC boosters/extenders for notification circuits:")
        instructions.setStyleSheet("font-size: 14px; color: #34495e; margin-bottom: 20px;")
        layout.addWidget(instructions)

        # NAC booster list
        self.nac_booster_list = QListWidget()
        self.nac_booster_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
                min-height: 200px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """
        )

        # Populate NAC boosters
        self._populate_nac_boosters()
        layout.addWidget(self.nac_booster_list)

        # Selection summary
        self.nac_summary = QLabel("No NAC boosters selected")
        self.nac_summary.setStyleSheet(
            """
            background-color: #f8f9fa;
            padding: 10px;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            margin: 10px 0;
        """
        )
        layout.addWidget(self.nac_summary)

        layout.addStretch()
        scroll_area.setWidget(content)
        self.content_stack.addWidget(scroll_area)

    def _populate_power_supplies(self):
        """Populate the power supply list with available devices."""
        try:
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "autofire.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT d.id, m.name as manufacturer, d.model, d.name, d.properties_json
                FROM devices d
                JOIN device_types dt ON d.type_id = dt.id
                JOIN manufacturers m ON d.manufacturer_id = m.id
                WHERE dt.code = 'PWR'
                ORDER BY m.name, d.model
            """
            )

            for row in cursor.fetchall():
                device_id, manufacturer, model, name, properties = row
                item_text = f"{manufacturer} {model} - {name}"
                item = QListWidgetItem(item_text)
                item.setData(
                    Qt.ItemDataRole.UserRole,
                    {
                        "id": device_id,
                        "manufacturer": manufacturer,
                        "model": model,
                        "name": name,
                        "properties": properties,
                    },
                )
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.power_supply_list.addItem(item)

            conn.close()
            logger.info(f"Loaded {self.power_supply_list.count()} power supplies")

        except Exception as e:
            logger.error(f"Error loading power supplies: {e}")

    def _populate_nac_boosters(self):
        """Populate the NAC booster list with available devices."""
        try:
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "autofire.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT d.id, m.name as manufacturer, d.model, d.name, d.properties_json
                FROM devices d
                JOIN device_types dt ON d.type_id = dt.id
                JOIN manufacturers m ON d.manufacturer_id = m.id
                WHERE dt.code = 'NAC'
                ORDER BY m.name, d.model
            """
            )

            for row in cursor.fetchall():
                device_id, manufacturer, model, name, properties = row
                item_text = f"{manufacturer} {model} - {name}"
                item = QListWidgetItem(item_text)
                item.setData(
                    Qt.ItemDataRole.UserRole,
                    {
                        "id": device_id,
                        "manufacturer": manufacturer,
                        "model": model,
                        "name": name,
                        "properties": properties,
                    },
                )
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.nac_booster_list.addItem(item)

            conn.close()
            logger.info(f"Loaded {self.nac_booster_list.count()} NAC boosters")

        except Exception as e:
            logger.error(f"Error loading NAC boosters: {e}")

    def _create_device_page(self):
        """Create device planning page."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)

        header_html = "".join(
            [
                '<h3 style="color: #2c3e50; margin-bottom: 8px;">🔍 Device Planning</h3>',
                '<p style="color: #34495e; font-size: 14px; line-height: 1.4;">',
                "Select detection and notification devices based on your building ",
                "requirements.",
                "</p>",
            ]
        )
        header = QLabel(header_html)
        header.setWordWrap(True)
        header.setStyleSheet(
            """
            background-color: #e8f5e8;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #27ae60;
            border: 1px solid #a9dfbf;
            font-family: 'Segoe UI', Arial, sans-serif;
        """
        )
        layout.addWidget(header)

        self.device_options_layout = QVBoxLayout()
        layout.addLayout(self.device_options_layout)

        layout.addStretch()
        scroll_area.setWidget(content)
        self.content_stack.addWidget(scroll_area)

    def _create_wire_page(self):
        """Create wire planning page."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)

        header_html = "".join(
            [
                '<h3 style="color: #2c3e50; margin-bottom: 8px;">🔌 Wiring & Circuits</h3>',
                '<p style="color: #34495e; font-size: 14px; line-height: 1.4;">',
                "Specify wire types and circuit configurations for your system.",
                "</p>",
            ]
        )
        header = QLabel(header_html)
        header.setWordWrap(True)
        header.setStyleSheet(
            """
            background-color: #fdf2e9;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #e67e22;
            border: 1px solid #f8c471;
            font-family: 'Segoe UI', Arial, sans-serif;
        """
        )
        layout.addWidget(header)

        self.wire_options_layout = QVBoxLayout()
        layout.addLayout(self.wire_options_layout)

        layout.addStretch()
        scroll_area.setWidget(content)
        self.content_stack.addWidget(scroll_area)

    def _create_review_page(self):
        """Create system review page."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)

        header_html = "".join(
            [
                '<h3 style="color: #2c3e50; margin-bottom: 8px;">✅ System Review</h3>',
                '<p style="color: #34495e; font-size: 14px; line-height: 1.4;">',
                "Review your complete fire alarm system and verify code compliance.",
                "</p>",
            ]
        )
        header = QLabel(header_html)
        header.setWordWrap(True)
        header.setStyleSheet(
            """
            background-color: #eaf2f8;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #3498db;
            border: 1px solid #aed6f1;
            font-family: 'Segoe UI', Arial, sans-serif;
        """
        )
        layout.addWidget(header)

        self.review_layout = QVBoxLayout()
        layout.addLayout(self.review_layout)

        layout.addStretch()
        scroll_area.setWidget(content)
        self.content_stack.addWidget(scroll_area)

    def _create_navigation_footer(self):
        """Create navigation footer."""
        footer = QFrame()
        footer.setFrameStyle(QFrame.Shape.StyledPanel)
        footer.setStyleSheet(
            """
            QFrame {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
                padding: 8px;
            }
        """
        )
        footer.setMaximumHeight(60)

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(15, 10, 15, 10)

        # Back button
        self.back_btn = QPushButton("⬅️ Back")
        self.back_btn.setEnabled(False)
        self.back_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #7f8c8d;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-weight: 900;
                font-size: 15px;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                min-height: 20px;
            }
            QPushButton:hover:enabled {
                background-color: #6c7b7d;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        self.back_btn.clicked.connect(self._go_back)

        # Status info
        self.status_info = QLabel("Step 1 of 6: Welcome")
        self.status_info.setStyleSheet(
            """
            color: #1a252f;
            font-size: 15px;
            font-style: normal;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 700;
        """
        )

        layout.addWidget(self.back_btn)
        layout.addWidget(self.status_info)
        layout.addStretch()

        # Next/Complete buttons
        self.next_btn = QPushButton("Next ➡️")
        self.next_btn.setEnabled(False)
        self.next_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2980b9;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-weight: 900;
                font-size: 15px;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                min-height: 20px;
            }
            QPushButton:hover:enabled {
                background-color: #1f4e79;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        self.next_btn.clicked.connect(self._go_next)

        self.complete_btn = QPushButton("🎉 Complete System")
        self.complete_btn.setVisible(False)
        self.complete_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #15803d;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-weight: 900;
                font-size: 15px;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #0d5016;
            }
        """
        )
        self.complete_btn.clicked.connect(self._complete_system)

        layout.addWidget(self.next_btn)
        layout.addWidget(self.complete_btn)

        return footer

    def _create_welcome_page(self):
        """Create enhanced welcome page with project info integration."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # AutoFire branding header
        branding_widget = QFrame()
        branding_widget.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fdff, stop:1 #eaf2f8);
                border: 3px solid #3498db;
                border-radius: 12px;
                padding: 25px;
                margin: 10px;
            }
        """
        )

        branding_layout = QVBoxLayout(branding_widget)
        branding_layout.setSpacing(15)

        # Title and version
        title_label = QLabel("🔥 AutoFire System Builder")
        title_label.setStyleSheet(
            """
            font-size: 32px;
            color: #1a252f;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 900;
            margin-bottom: 8px;
        """
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        branding_layout.addWidget(title_label)

        subtitle_label = QLabel("Professional Fire Alarm CAD System v0.8.0")
        subtitle_label.setStyleSheet(
            """
            font-size: 18px;
            color: #2c3e50;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 600;
            margin-bottom: 15px;
        """
        )
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        branding_layout.addWidget(subtitle_label)

        layout.addWidget(branding_widget)

        # Project information section
        project_info_widget = self._create_project_info_section()
        layout.addWidget(project_info_widget)

        # Welcome content
        welcome_content_widget = QFrame()
        welcome_content_widget.setStyleSheet(
            """
            QFrame {
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                padding: 25px;
                margin: 10px 0px;
            }
        """
        )

        welcome_content_layout = QVBoxLayout(welcome_content_widget)
        welcome_content_layout.setSpacing(20)

        welcome_html = "".join(
            [
                '<h3 style="color: #1a252f; margin-bottom: 15px; '
                'font-size: 20px; font-weight: 900;">',
                "Welcome to Professional Fire Alarm System Design",
                "</h3>",
                '<p style="color: #2c3e50; font-size: 16px; line-height: 1.6; '
                'font-weight: 600;">',
                "This guided workflow will help you design a complete fire alarm system that "
                "meets NFPA 72 standards and local code requirements. We'll assess your "
                "building, recommend appropriate equipment, and generate professional "
                "documentation.",
                "</p>",
                '<div style="background-color: #d5f4e6; padding: 15px; border-radius: 8px; '
                'border-left: 5px solid #27ae60; margin: 15px 0;">',
                '<p style="color: #0d5016; font-size: 14px; font-weight: 700; margin: 0;">',
                "✓ Code-compliant system design<br>",
                "✓ Professional equipment recommendations<br>",
                "✓ Complete documentation and specifications<br>",
                "✓ Integration with AutoFire CAD system",
                "</p>",
                "</div>",
            ]
        )
        welcome_text = QLabel(welcome_html)
        welcome_text.setWordWrap(True)
        welcome_text.setStyleSheet(
            """
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
        """
        )
        welcome_content_layout.addWidget(welcome_text)

        layout.addWidget(welcome_content_widget)

        # Action buttons
        button_widget = QFrame()
        button_widget.setStyleSheet(
            """
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 20px;
            }
        """
        )

        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(25)

        start_assessment_btn = QPushButton("🏢 Start Building Assessment")
        start_assessment_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 18px 30px;
                font-weight: 900;
                font-size: 16px;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                min-width: 240px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """
        )
        start_assessment_btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(1))

        load_project_btn = QPushButton("📁 Load Recent Project")
        load_project_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 18px 30px;
                font-weight: 900;
                font-size: 16px;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                min-width: 240px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
        )
        load_project_btn.clicked.connect(self._show_recent_projects)

        button_layout.addWidget(start_assessment_btn)
        button_layout.addWidget(load_project_btn)
        layout.addWidget(button_widget)

        # Footer with copyright
        footer_label = QLabel("© 2025 AutoFire - Professional Fire Alarm CAD System")
        footer_label.setStyleSheet(
            """
            color: #7f8c8d;
            font-size: 12px;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            margin-top: 20px;
            padding: 10px;
        """
        )
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer_label)

        layout.addStretch()

        scroll_area.setWidget(content)
        self.content_stack.addWidget(scroll_area)

    def _create_project_info_section(self):
        """Create project information section similar to splash screen."""
        widget = QFrame()
        widget.setStyleSheet(
            """
            QFrame {
                background-color: #ffffff;
                border: 2px solid #e8f4f8;
                border-radius: 8px;
                padding: 20px;
                margin: 10px 0px;
            }
        """
        )

        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # Project info header
        header = QLabel("📋 Current Project Information")
        header.setStyleSheet(
            """
            font-size: 18px;
            color: #1a252f;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 900;
            margin-bottom: 10px;
        """
        )
        layout.addWidget(header)

        # Project details form
        details_layout = QFormLayout()
        details_layout.setSpacing(12)

        # Project name
        self.project_name_edit = QLineEdit()
        self.project_name_edit.setPlaceholderText(
            "Enter project name (e.g., 'Main Street Office Building')"
        )
        self.project_name_edit.setStyleSheet(
            """
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """
        )

        project_label = QLabel("Project Name:")
        project_label.setStyleSheet(
            """
            font-size: 14px;
            color: #2c3e50;
            font-weight: 700;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
        """
        )
        details_layout.addRow(project_label, self.project_name_edit)

        # Client name
        self.client_name_edit = QLineEdit()
        self.client_name_edit.setPlaceholderText("Client or building owner name")
        self.client_name_edit.setStyleSheet(self.project_name_edit.styleSheet())

        client_label = QLabel("Client:")
        client_label.setStyleSheet(project_label.styleSheet())
        details_layout.addRow(client_label, self.client_name_edit)

        # Project address
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Building address")
        self.address_edit.setStyleSheet(self.project_name_edit.styleSheet())

        address_label = QLabel("Address:")
        address_label.setStyleSheet(project_label.styleSheet())
        details_layout.addRow(address_label, self.address_edit)

        layout.addLayout(details_layout)

        # Quick start note
        note_html = "".join(
            [
                '<div style="background-color: #fef9e7; padding: 12px; border-radius: 6px; '
                'border-left: 4px solid #f39c12;">',
                '<strong style="color: #d68910;">💡 Quick Start:</strong>',
                '<span style="color: #8b6914;">You can start the assessment immediately and '
                "add project details later, or fill in the information now for better "
                "documentation.</span>",
                "</div>",
            ]
        )
        note_label = QLabel(note_html)
        note_label.setWordWrap(True)
        layout.addWidget(note_label)

        return widget

    def _show_recent_projects(self):
        """Show recent projects dialog similar to splash screen."""
        import json
        from pathlib import Path

        from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMessageBox

        # Create recent projects dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Recent AutoFire Projects")
        dialog.setModal(True)
        dialog.resize(500, 400)
        dialog.setStyleSheet(
            """
            QDialog {
                background-color: #f8fdff;
                border: 2px solid #3498db;
                border-radius: 8px;
            }
        """
        )

        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header = QLabel("📁 Recent Projects")
        header.setStyleSheet(
            """
            font-size: 20px;
            color: #1a252f;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 900;
            margin-bottom: 15px;
        """
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Recent projects list
        recent_list = QListWidget()
        recent_list.setStyleSheet(
            """
            QListWidget {
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: 600;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #ecf0f1;
                border-radius: 4px;
                margin-bottom: 5px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #e8f4f8;
            }
        """
        )

        # Load recent projects
        try:
            settings_file = Path.home() / ".autofire" / "settings.json"
            if settings_file.exists():
                with open(settings_file) as f:
                    settings = json.load(f)
                    recent_projects = settings.get("recent_projects", [])

                    for project_path in recent_projects[:5]:  # Show last 5
                        if os.path.exists(project_path):
                            item = QListWidgetItem(f"📂 {os.path.basename(project_path)}")
                            item.setData(Qt.ItemDataRole.UserRole, project_path)
                            recent_list.addItem(item)
        except Exception:
            # If no recent projects, show placeholder
            item = QListWidgetItem("No recent projects found")
            item.setData(Qt.ItemDataRole.UserRole, None)
            recent_list.addItem(item)

        layout.addWidget(recent_list)

        # Buttons
        button_layout = QHBoxLayout()

        open_btn = QPushButton("Open Selected")
        open_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """
        )

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #95a5a6;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """
        )

        button_layout.addWidget(open_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        # Connect buttons
        def on_open():
            current_item = recent_list.currentItem()
            if current_item and current_item.data(Qt.ItemDataRole.UserRole):
                project_path = current_item.data(Qt.ItemDataRole.UserRole)
                logger.info(f"Loading recent project: {project_path}")
                # Here you would load the project data
                dialog.accept()
            else:
                QMessageBox.information(dialog, "No Selection", "Please select a project to open.")

        open_btn.clicked.connect(on_open)
        cancel_btn.clicked.connect(dialog.reject)
        recent_list.itemDoubleClicked.connect(on_open)

        dialog.exec()

    def _start_workflow(self):
        """Initialize the workflow."""
        self.current_step = 0
        self._update_navigation()

    def _on_assessment_changed(self):
        """Handle assessment changes with logging."""
        # Log the change
        logger.info(
            f"Assessment changed: Building type={self.building_type.currentText()}, "
            f"Size={self.building_size.value()}sqft, Floors={self.floors.value()}, "
            f"Occupancy={self.occupancy.currentText()}"
        )

        self.assessment.project_type = self.building_type.currentText()
        self.assessment.size_sqft = self.building_size.value()
        self.assessment.floors = self.floors.value()
        self.assessment.occupancy_level = self.occupancy.currentText()

        # Update special hazards with proper tracking
        self.assessment.special_hazards = []
        for checkbox in self.special_hazards_checkboxes:
            if checkbox.isChecked():
                checkbox_text = checkbox.text()
                if "Kitchen" in checkbox_text:
                    self.assessment.special_hazards.append("commercial_kitchen")
                elif "Mechanical" in checkbox_text:
                    self.assessment.special_hazards.append("mechanical_rooms")
                elif "Hazardous" in checkbox_text:
                    self.assessment.special_hazards.append("hazardous_storage")
                elif "Data" in checkbox_text:
                    self.assessment.special_hazards.append("data_center")

        # Log special hazards
        if self.assessment.special_hazards:
            logger.info(f"Special hazards selected: {', '.join(self.assessment.special_hazards)}")

        # Generate recommendations if building type is selected
        if not self.assessment.building_type.startswith("Select"):
            self._generate_recommendations()

            # Update panel recommendations and project summary
            if hasattr(self, "recommended_panels_layout"):
                self._populate_panel_recommendations()
            if hasattr(self, "building_summary_text"):
                self._update_project_summary()

            self.next_btn.setEnabled(True)
            self._update_guidance(
                "✅ Assessment complete! Review your building details and proceed to panel options."
            )
            logger.info("Assessment completed, recommendations generated")

    def _generate_recommendations(self):
        """Generate system recommendations."""
        assessment = self.assessment
        recommendations = []

        # Panel guidance (less aggressive, more informational)
        if assessment.size_sqft < 5000:
            recommendations.append(
                "ℹ️ INFO: Smaller buildings often use conventional panels (cost-effective)"
            )
            self.recommendations.panel_type = "conventional"
        elif assessment.size_sqft < 25000:
            recommendations.append(
                "ℹ️ INFO: Medium buildings typically benefit from "
                "addressable panels (better monitoring)"
            )
            self.recommendations.panel_type = "addressable"
        else:
            recommendations.append(
                "ℹ️ INFO: Large buildings may consider networked systems (scalability)"
            )
            self.recommendations.panel_type = "networked"

        # Device estimates (more informational, less prescriptive)
        if "Office" in assessment.building_type:
            smoke_count = max(assessment.size_sqft // 900, assessment.floors * 2)
            heat_count = assessment.floors
            recommendations.append(
                f"📊 ESTIMATE: Approximately {smoke_count} smoke detectors, "
                f"{heat_count} heat detectors may be needed"
            )
        elif "Industrial" in assessment.building_type:
            heat_count = max(assessment.size_sqft // 900, assessment.floors * 3)
            recommendations.append(
                f"📊 ESTIMATE: Approximately {heat_count} heat detectors "
                f"(often preferred for industrial)"
            )

        # Code notes (helpful information)
        if assessment.floors > 3:
            recommendations.append(
                "📋 NOTE: High-rise fire alarm provisions may apply to this building"
            )

        self.recommendations_display.setPlainText("\\n\\n".join(recommendations))

    def _go_next(self):
        """Go to next step."""
        if self.current_step < 4:
            self.current_step += 1
            self.content_stack.setCurrentIndex(self.current_step)
            self._update_step_indicators()
            self._update_navigation()
            self._populate_current_step()

    def _go_back(self):
        """Go to previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            self.content_stack.setCurrentIndex(self.current_step)
            self._update_step_indicators()
            self._update_navigation()

    def _update_step_indicators(self):
        """Update step indicators."""
        for i, label in enumerate(self.step_labels):
            if i == self.current_step:
                label.setStyleSheet(
                    """
                    color: #ffffff;
                    font-weight: bold;
                    padding: 6px 12px;
                    border-radius: 15px;
                    background-color: rgba(255,255,255,0.35);
                    border: 2px solid #ffffff;
                    font-size: 12px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                """
                )
            elif i < self.current_step:
                label.setStyleSheet(
                    """
                    color: #ffffff;
                    font-weight: bold;
                    padding: 6px 12px;
                    border-radius: 15px;
                    background-color: #27ae60;
                    border: 2px solid #27ae60;
                    font-size: 12px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                """
                )
            else:
                label.setStyleSheet(
                    """
                    color: #bdc3c7;
                    font-weight: normal;
                    padding: 6px 12px;
                    border-radius: 15px;
                    background-color: rgba(255,255,255,0.1);
                    border: 1px solid rgba(255,255,255,0.3);
                    font-size: 12px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                """
                )

        self.progress_bar.setValue(self.current_step + 1)

    def _update_navigation(self):
        """Update navigation state."""
        self.back_btn.setEnabled(self.current_step > 0)

        # Update status
        step_names = [
            "Welcome",
            "Building Assessment",
            "Panel Selection",
            "Power Supplies",
            "NAC Boosters",
            "Device Planning",
            "Wire Planning",
            "System Review",
        ]
        self.status_info.setText(
            f"Step {self.current_step + 1} of 8: {step_names[self.current_step]}"
        )

        if self.current_step == 7:
            self.next_btn.setVisible(False)
            self.complete_btn.setVisible(True)
        else:
            self.next_btn.setVisible(True)
            self.complete_btn.setVisible(False)

        # Update guidance
        guidance_messages = [
            "AutoFire System Builder - Start with building assessment",
            "Building Assessment - Enter project specifications",
            "Panel Selection - Filter and choose control panel",
            "Device Planning - Select detection and notification devices",
            "Wire Planning - Configure circuits and connections",
            "System Review - Verify system configuration",
        ]
        self._update_guidance(guidance_messages[self.current_step])

    def _populate_current_step(self):
        """Populate current step with data."""
        if self.current_step == 2:
            self._populate_panel_options()
        elif self.current_step == 3:
            self._populate_device_options()
        elif self.current_step == 4:
            self._populate_wire_options()
        elif self.current_step == 5:
            self._populate_review()

    def _populate_panel_options(self):
        """Populate panel selection options using the new filter system."""
        # Simply trigger the filter to populate the grid

    def _toggle_advanced_panels(self):
        """Toggle the advanced panels section."""
        if self.advanced_panels_widget.isVisible():
            self.advanced_panels_widget.hide()
            self.advanced_toggle_btn.setText("🔧 Show All Panels (Advanced)")
        else:
            self.advanced_panels_widget.show()
            self.advanced_toggle_btn.setText("🔧 Hide Advanced Panels")
            # Populate the advanced grid with all panels
            self._populate_all_panels_grid()

    def _populate_all_panels_grid(self):
        """Populate the advanced grid with all available panels."""
        # Clear current grid
        while self.panel_grid_layout.count():
            child = self.panel_grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Get all panels from database
        all_panels = self._get_all_panels_from_db()

        # Display all panels in grid
        row, col = 0, 0
        for panel in all_panels:
            panel_card = self._create_panel_card(panel)
            self.panel_grid_layout.addWidget(panel_card, row, col)
            col += 1
            if col >= 3:  # 3 columns
                col = 0
                row += 1

    def _create_simple_panel_recommendation(self, title, description, panels, recommended=True):
        """Create a simple panel recommendation card."""
        frame = QFrame()
        if recommended:
            frame.setStyleSheet(
                """
                QFrame {
                    background-color: #e8f5e8;
                    border: 2px solid #28a745;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px 0;
                }
            """
            )
        else:
            frame.setStyleSheet(
                """
                QFrame {
                    background-color: #f8f9fa;
                    border: 2px solid #dee2e6;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px 0;
                }
            """
            )

        layout = QVBoxLayout(frame)

        # Title with recommendation badge
        title_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """
        )
        title_layout.addWidget(title_label)

        if recommended:
            badge = QLabel("✅ RECOMMENDED")
            badge.setStyleSheet(
                """
                background-color: #28a745;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            """
            )
            title_layout.addWidget(badge)

        title_layout.addStretch()
        layout.addLayout(title_layout)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet(
            """
            font-size: 13px;
            color: #6c757d;
            margin: 8px 0;
        """
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Panel options
        for panel in panels:
            panel_btn = QPushButton(f"Choose {panel['manufacturer']} {panel['model']}")
            if recommended:
                panel_btn.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #28a745;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 15px;
                        font-weight: bold;
                        font-size: 13px;
                        margin: 2px;
                    }
                    QPushButton:hover {
                        background-color: #218838;
                    }
                """
                )
            else:
                panel_btn.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #6c757d;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 15px;
                        font-weight: bold;
                        font-size: 13px;
                        margin: 2px;
                    }
                    QPushButton:hover {
                        background-color: #5a6268;
                    }
                """
                )
            panel_btn.clicked.connect(lambda checked, p=panel: self._select_simple_panel(p))
            layout.addWidget(panel_btn)

        return frame

    def _select_simple_panel(self, panel):
        """Select a panel from the simple recommendations."""
        self.selected_panel = panel
        self.next_btn.setEnabled(True)
        logger.info(f"Panel selected: {panel['manufacturer']} {panel['model']}")

        # Update project summary to show selection
        self._update_project_summary()

        # Show success message
        self._update_guidance(
            f"✅ Selected {panel['manufacturer']} {panel['model']}. Ready for device planning."
        )

    def _update_project_summary(self):
        """Update the project summary with current assessment and selection."""
        if hasattr(self, "building_summary_text"):
            assessment = self.assessment

            summary_parts = []
            summary_parts.append(f"Project Type: {assessment.project_type}")
            summary_parts.append(f"Size: {assessment.size_sqft:,} sq ft")
            summary_parts.append(f"Floors: {assessment.floors}")
            summary_parts.append(f"Occupancy: {assessment.occupancy_level}")

            if assessment.special_hazards:
                summary_parts.append(f"Special Hazards: {', '.join(assessment.special_hazards)}")

            if hasattr(self, "selected_panel") and self.selected_panel:
                summary_parts.append(
                    f"Selected Panel: {self.selected_panel['manufacturer']}"
                    f" {self.selected_panel['model']}"
                )

            self.building_summary_text.setText(" | ".join(summary_parts))

    def _populate_panel_recommendations(self):
        """Populate simple panel recommendations based on building assessment."""
        # Clear existing recommendations
        while self.recommended_panels_layout.count():
            child = self.recommended_panels_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        assessment = self.assessment

        # Get some sample panels from database
        all_panels = self._get_all_panels_from_db()

        if not all_panels:
            no_panels_label = QLabel(
                "No panels found in database. Please check database connection."
            )
            no_panels_label.setStyleSheet("color: #dc3545; font-weight: bold; padding: 20px;")
            self.recommended_panels_layout.addWidget(no_panels_label)
            return

        # Create simple categories based on building size
        small_panels = [
            p for p in all_panels if "4100ES" in p.get("model", "") or "MS-4" in p.get("model", "")
        ]
        medium_panels = [
            p
            for p in all_panels
            if "NFS2-640" in p.get("model", "") or "MS-9050" in p.get("model", "")
        ]
        large_panels = [
            p
            for p in all_panels
            if "MS-9600" in p.get("model", "") or "NFS-320" in p.get("model", "")
        ]

        # Default to showing at least some panels
        if not small_panels and all_panels:
            small_panels = all_panels[:1]
        if not medium_panels and all_panels:
            medium_panels = all_panels[:1]
        if not large_panels and all_panels:
            large_panels = all_panels[:1]

        # Determine which category is recommended based on building size
        building_size = assessment.size_sqft

        if building_size <= 5000:
            # Small building
            self.recommended_panels_layout.addWidget(
                self._create_simple_panel_recommendation(
                    "🏠 Small Building Panel",
                    "Perfect for smaller buildings under 5,000 sq ft. "
                    "Simple setup and maintenance.",
                    small_panels,
                    recommended=True,
                )
            )
            if medium_panels:
                self.recommended_panels_layout.addWidget(
                    self._create_simple_panel_recommendation(
                        "🏢 Medium Building Panel",
                        "For buildings 5,000-20,000 sq ft. More device capacity.",
                        medium_panels,
                        recommended=False,
                    )
                )
        elif building_size <= 20000:
            # Medium building
            self.recommended_panels_layout.addWidget(
                self._create_simple_panel_recommendation(
                    "🏢 Medium Building Panel",
                    "Ideal for buildings 5,000-20,000 sq ft. Good balance of "
                    "features and capacity.",
                    medium_panels,
                    recommended=True,
                )
            )
            if small_panels:
                self.recommended_panels_layout.addWidget(
                    self._create_simple_panel_recommendation(
                        "🏠 Small Building Panel",
                        "For smaller areas. May need multiple panels for full coverage.",
                        small_panels,
                        recommended=False,
                    )
                )
            if large_panels:
                self.recommended_panels_layout.addWidget(
                    self._create_simple_panel_recommendation(
                        "🏭 Large Building Panel",
                        "For buildings over 20,000 sq ft. Maximum device capacity.",
                        large_panels,
                        recommended=False,
                    )
                )
        else:
            # Large building
            self.recommended_panels_layout.addWidget(
                self._create_simple_panel_recommendation(
                    "🏭 Large Building Panel",
                    "Designed for large buildings over 20,000 sq ft. Maximum device "
                    "capacity and features.",
                    large_panels,
                    recommended=True,
                )
            )
            if medium_panels:
                self.recommended_panels_layout.addWidget(
                    self._create_simple_panel_recommendation(
                        "🏢 Medium Building Panel",
                        "Alternative option. May need multiple panels for full coverage.",
                        medium_panels,
                        recommended=False,
                    )
                )
        """Handle complexity level change - removed in favor of direct filtering."""
        # This method is kept for compatibility but doesn't do anything
        # since we removed the complexity selector
        pass

    def _get_panel_capacity_info(self, panel):
        """Get capacity information for panel instead of suitability score."""
        model = panel.get("model", "").upper()

        # Provide typical capacity info based on common panel models
        if "NFS2-640" in model or "MS-9600" in model:
            return "Capacity: Up to 636 devices, 99 zones"
        elif "MS-9050" in model or "NFS-320" in model:
            return "Capacity: Up to 318 devices, 159 zones"
        elif "4100ES" in model:
            return "Capacity: Up to 1,590 devices, networked"
        elif "MS-5" in model or "MS-4" in model:
            return "Capacity: Conventional zones, basic detection"
        else:
            return "Capacity: Check manufacturer specifications"

    def _get_all_panels_from_db(self):
        """Get all available panels from database."""
        try:
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "autofire.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT p.id, m.name as manufacturer, p.name, p.model,
                p.properties_json as description
                FROM panels p
                LEFT JOIN manufacturers m ON m.id = p.manufacturer_id
                ORDER BY m.name, p.model
            """
            )

            panels = []
            for row in cursor.fetchall():
                panels.append(
                    {
                        "id": row[0],
                        "manufacturer": row[1],
                        "name": row[2],
                        "model": row[3],
                        "description": row[4] or "",
                    }
                )

            conn.close()
            return panels

        except Exception as e:
            logger.error(f"Error loading panels from database: {e}")
            return self._get_fallback_panels()

    def _create_panel_card(self, panel):
        """Create a clean panel card for the grid."""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setStyleSheet(
            """
            QFrame {
                border: 3px solid #000000;
                border-radius: 8px;
                background-color: #F0F0F0;
                padding: 12px;
                margin: 4px;
            }
            QFrame:hover {
                border-color: #0066CC;
                background-color: #E0E0E0;
            }
        """
        )
        card.setFixedSize(260, 180)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # Model name
        model_label = QLabel(panel["model"])
        model_label.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            color: #000000;
            background-color: #FFFFFF;
            border: 1px solid #000000;
            padding: 4px;
        """
        )
        model_label.setWordWrap(True)
        layout.addWidget(model_label)

        # Manufacturer
        mfg_label = QLabel(panel["manufacturer"])
        mfg_label.setStyleSheet(
            """
            font-size: 12px;
            color: #000000;
            background-color: #FFFFFF;
            border: 1px solid #000000;
            padding: 3px;
            font-weight: bold;
        """
        )
        mfg_label.setWordWrap(True)
        layout.addWidget(mfg_label)

        # Capacity
        capacity = self._get_panel_capacity_info(panel)
        capacity_label = QLabel(capacity)
        capacity_label.setStyleSheet(
            """
            font-size: 10px;
            color: #000000;
            background-color: #FFFFFF;
            border: 1px solid #000000;
            padding: 2px;
            font-weight: normal;
        """
        )
        capacity_label.setWordWrap(True)
        layout.addWidget(capacity_label)

        layout.addStretch()

        # Select button
        select_btn = QPushButton("Select")
        select_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """
        )
        select_btn.clicked.connect(lambda: self._select_panel_from_card(panel))
        layout.addWidget(select_btn)

        return card

    def _select_panel_from_card(self, panel):
        """Select panel from card."""
        self.selected_panel = panel
        self.next_btn.setEnabled(True)
        logger.info(f"Panel selected: {panel['manufacturer']} {panel['model']}")

        # Highlight selected card by updating all cards

    def _show_coverage_reference(self):
        """Show coverage approximations popup for quick reference."""
        if not hasattr(self, "assessment") or not self.assessment:
            QMessageBox.information(
                self,
                "Coverage Reference",
                "Complete the building assessment first to see coverage estimates.",
            )
            return

        area = self.assessment.size_sqft
        floors = self.assessment.floors

        # Typical coverage calculations
        smoke_coverage = 900  # sq ft per smoke detector
        _heat_coverage = 900  # sq ft per heat detector (unused placeholder)
        notification_coverage = 2500  # sq ft per horn/strobe

        estimated_smoke = max(area // smoke_coverage, floors * 2)
        estimated_heat = max(floors, len(self.assessment.special_hazards or []))
        estimated_notification = max(area // notification_coverage, floors * 2)
        estimated_pulls = max(floors * 2, 4)  # 2 per floor, minimum 4

        reference_text = f"""Building: {area:,} sq ft over {floors} floor(s)

TYPICAL DEVICE COVERAGE ESTIMATES:

• Smoke Detectors: ~{estimated_smoke} units
  (900 sq ft coverage each)

• Heat Detectors: ~{estimated_heat} units
  (special areas + backup)

• Horn/Strobes: ~{estimated_notification} units
  (2,500 sq ft coverage each)

• Pull Stations: ~{estimated_pulls} units
  (exit routes + code requirements)

NOTE: These are planning estimates only.
Final device count depends on specific layout,
code requirements, and engineering judgment."""

        msg = QMessageBox(self)
        msg.setWindowTitle("Device Coverage Reference")
        msg.setText(reference_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def _show_sprinkler_code_requirements(self):
        """Show sprinkler system code requirements popup."""
        code_text = """SPRINKLER SYSTEM MONITORING - CODE REQUIREMENTS

NFPA 72 - Required Monitoring:

🚿 FLOW SWITCHES (Required):
• Monitor water flow in sprinkler piping
• Required on all sprinkler systems
• Typically one per floor or zone
• Must transmit to fire alarm panel

🔧 TAMPER SWITCHES (Required):
• Monitor valve positions
• Main control valve supervision
• Sectional valve supervision
• Prevents unauthorized system shutdown

💨 PRESSURE/AIR SWITCHES:
• Dry pipe systems: Air pressure monitoring
• Pre-action systems: Supervisory air
• Deluge systems: Water pressure
• Required where applicable

⚡ PUMP MONITORING (If Present):
• Fire pump running status
• Fire pump trouble conditions
• Pump controller supervision

📋 CODE REFERENCES:
• NFPA 72: Chapter 17 - Initiating Devices
• NFPA 13: Chapter 16 - Supervision
• IFC: Section 903 - Automatic Sprinkler Systems

NOTE: Local AHJ requirements may vary.
Always check local codes and amendments."""

        msg = QMessageBox(self)
        msg.setWindowTitle("Sprinkler Code Requirements")
        msg.setText(code_text)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def _get_recommended_panels(self):
        """Get recommended panels from actual database based on assessment."""
        panels = []

        try:
            # Load panels directly from the panels table
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "autofire.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT p.id, m.name as manufacturer, p.model, p.name, p.panel_type,
                       p.max_devices, p.properties_json
                FROM panels p
                LEFT JOIN manufacturers m ON m.id = p.manufacturer_id
                WHERE p.panel_type = 'main'
                ORDER BY m.name, p.model
            """
            )

            for row in cursor.fetchall():
                panel = {
                    "id": row[0],
                    "manufacturer": row[1] or "Unknown",
                    "model": row[2] or "Unknown",
                    "name": row[3] or "Unnamed Panel",
                    "panel_type": row[4] or "main",
                    "max_devices": row[5] or 0,
                    "properties": row[6] or "{}",
                }

                # Add scoring based on building requirements
                score = self._calculate_panel_suitability_score(panel)
                panel["suitability_score"] = score
                panel["recommendation_reason"] = self._get_panel_recommendation_reason(panel, score)
                panels.append(panel)

            conn.close()

            # Remove duplication: Use only panels table as authoritative source
            # Devices table panels caused "three instances" issue - now fixed

            # Sort by suitability score and return top 5 (increased from 3)
            panels.sort(key=lambda x: x.get("suitability_score", 0), reverse=True)

            # Now MS-9050UD should appear in top recommendations
            return panels[:5] if panels else self._get_fallback_panels()

        except Exception as e:
            logger.error(f"Error getting recommended panels: {e}")
            return self._get_fallback_panels()

    def _calculate_panel_suitability_score(self, panel):
        """Calculate how suitable a panel is for the current building assessment."""
        score = 50  # Base score

        model = panel.get("model", "").upper()
        name = panel.get("name", "").upper()
        manufacturer = panel.get("manufacturer", "").upper()

        # Size-based scoring
        if self.assessment.size_sqft < 5000:
            # Small buildings - favor conventional panels
            if any(keyword in model or keyword in name for keyword in ["2-", "4-", "8-", "CONV"]):
                score += 30
        elif self.assessment.size_sqft < 25000:
            # Medium buildings - favor addressable panels
            if any(
                keyword in model or keyword in name for keyword in ["NFS", "MS-", "FC-", "ADDR"]
            ):
                score += 30
        else:
            # Large buildings - favor networked/expandable panels
            if any(
                keyword in model or keyword in name
                for keyword in ["NFS", "NET", "NETWORK", "100", "200"]
            ):
                score += 30

        # Floor-based scoring
        if self.assessment.floors > 3:
            if any(keyword in model or keyword in name for keyword in ["HIGH", "RISE", "NFS"]):
                score += 20

        # Special hazards scoring
        if self.assessment.special_hazards:
            if any(
                keyword in model or keyword in name
                for keyword in ["SPECIAL", "HAZARD", "INDUSTRIAL"]
            ):
                score += 15

        # Manufacturer reputation (basic scoring)
        if any(
            trusted in manufacturer for trusted in ["NOTIFIER", "FIRE-LITE", "HONEYWELL", "SIEMENS"]
        ):
            score += 10

        return score

    def _get_panel_recommendation_reason(self, panel, score):
        """Get human-readable reason for panel recommendation."""
        reasons = []

        if self.assessment.size_sqft < 5000:
            reasons.append("Cost-effective for smaller buildings")
        elif self.assessment.size_sqft < 25000:
            reasons.append("Ideal monitoring capability for medium buildings")
        else:
            reasons.append("Scalable solution for large buildings")

        if self.assessment.floors > 3:
            reasons.append("High-rise compatible")

        if self.assessment.special_hazards:
            reasons.append("Handles special hazard areas")

        return " • ".join(reasons[:2])  # Limit to top 2 reasons

    def _get_fallback_panels(self):
        """Fallback panels if database query fails."""
        return [
            {
                "id": "fallback_1",
                "manufacturer": "Fire-Lite",
                "name": "Fire Alarm Control Panel",
                "model": "NFS2-3030",
                "suitability_score": 80,
                "recommendation_reason": "Reliable addressable system",
            },
            {
                "id": "fallback_2",
                "manufacturer": "Notifier",
                "name": "Fire Alarm Control Panel",
                "model": "NFS-320",
                "suitability_score": 75,
                "recommendation_reason": "Proven performance for medium buildings",
            },
        ]

    def _create_panel_option(self, panel):
        """Create a panel selection option."""
        option = QFrame()
        option.setFrameStyle(QFrame.Shape.StyledPanel)
        option.setStyleSheet(
            """
            QFrame {
                border: 3px solid #000000;
                border-radius: 8px;
                padding: 15px;
                margin: 8px;
                background-color: #F0F0F0;
            }
            QFrame:hover {
                border-color: #0066CC;
                background-color: #E0E0E0;
            }
        """
        )

        layout = QHBoxLayout(option)

        # Panel info
        info_layout = QVBoxLayout()

        name_label = QLabel(f"<b>{panel['name']}</b>")
        name_label.setStyleSheet(
            """
            font-size: 18px;
            color: #000000;
            font-family: 'Arial Black', sans-serif;
            font-weight: bold;
            background-color: #FFFFFF;
            border: 1px solid #000000;
            padding: 5px;
        """
        )

        details_label = QLabel(f"Model: {panel['model']} | {panel['manufacturer']}")
        details_label.setStyleSheet(
            """
            color: #000000;
            font-size: 16px;
            font-family: 'Arial', sans-serif;
            margin-top: 4px;
            background-color: #FFFFFF;
            font-weight: bold;
            border: 1px solid #000000;
            padding: 3px;
        """
        )

        # Less pushy information - just typical applications
        application_info = panel.get(
            "recommendation_reason",
            f"Typically used for {self.recommendations.panel_type} applications",
        )
        reason_label = QLabel(f"ℹ️ {application_info}")
        reason_label.setStyleSheet(
            """
            color: #000000;
            font-size: 14px;
            font-style: normal;
            font-family: 'Arial', sans-serif;
            font-weight: bold;
            margin-top: 8px;
            background-color: #FFFFFF;
            border: 1px solid #000000;
            padding: 3px;
        """
        )
        reason_label.setWordWrap(True)

        # Show device capacity instead of suitability score
        capacity_info = self._get_panel_capacity_info(panel)
        capacity_label = QLabel(f"📊 {capacity_info}")
        capacity_label.setStyleSheet(
            """
            color: #000000;
            font-size: 14px;
            font-family: 'Arial', sans-serif;
            font-weight: bold;
            margin-top: 4px;
            background-color: #FFFFFF;
            border: 1px solid #000000;
            padding: 3px;
        """
        )

        info_layout.addWidget(name_label)
        info_layout.addWidget(details_label)
        info_layout.addWidget(reason_label)
        info_layout.addWidget(capacity_label)

        # Choose button (less pushy language)
        select_btn = QPushButton("Choose This Panel")
        select_btn.setFixedSize(140, 35)
        select_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        select_btn.clicked.connect(lambda: self._select_panel(panel))

        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addWidget(select_btn)

        return option

    def _select_panel(self, panel):
        """Select a panel with logging."""
        self.selected_panel = panel
        self.next_btn.setEnabled(True)

        # Log the selection
        logger.info(
            f"Panel selected: {panel.get('manufacturer', 'Unknown')} "
            f"{panel.get('model', 'Unknown')} (Score: {panel.get('suitability_score', 'N/A')})"
        )

        self._update_guidance(
            f"✅ Selected {panel['manufacturer']} {panel['model']}. Ready for device planning."
        )

    def _populate_device_options(self):
        """Populate device options based on real assessment and selected panel."""
        while self.device_options_layout.count():
            child = self.device_options_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.selected_panel:
            info = QLabel("Please select a control panel first.")
            info.setStyleSheet(
                """
                padding: 25px;
                color: #e67e22;
                font-style: italic;
                font-size: 16px;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                font-weight: 600;
                background-color: #fff8e1;
                border: 3px dashed #f39c12;
                border-radius: 10px;
                text-align: center;
            """
            )
            self.device_options_layout.addWidget(info)
            return

        # Calculate device requirements based on assessment
        device_requirements = self._calculate_device_requirements()
        try:
            logger.info(
                "Device categories for planning: %s",
                ", ".join(list(device_requirements.keys())),
            )
        except Exception:
            pass

        # Sort categories to show Annunciators after main detection/notification
        def category_sort_key(cat):
            order = [
                "Smoke Detection",
                "Heat Detection",
                "Notification",
                "Manual Pull Stations",
                "Annunciators",
                "Special Hazard Protection",
            ]
            try:
                return order.index(cat)
            except ValueError:
                return len(order)

        for category in sorted(device_requirements.keys(), key=category_sort_key):
            devices = device_requirements[category]
            # Only show Annunciators if there are device options
            if category == "Annunciators" and not devices["devices"]:
                continue
            category_widget = self._create_device_category_widget(category, devices)
            self.device_options_layout.addWidget(category_widget)

        # Enable next step
        self.next_btn.setEnabled(True)
        logger.info(f"Device planning populated for {len(device_requirements)} categories")

    def _calculate_device_requirements(self):
        """Calculate device requirements based on building assessment."""
        requirements = {}

        # Base calculations
        area_per_smoke = 900  # sq ft per smoke detector (typical)

        # Smoke detectors (main detection)
        smoke_count = max(self.assessment.size_sqft // area_per_smoke, self.assessment.floors * 2)
        requirements["Smoke Detection"] = {
            "count": smoke_count,
            "devices": self._get_devices_by_type(["smoke", "detector"]),
            "reasoning": f"Based on {self.assessment.size_sqft:,} sq ft area coverage",
        }

        # Heat detectors (special areas + backup)
        special_hazards = self.assessment.special_hazards or []
        heat_count = self.assessment.floors + len(special_hazards)
        if "commercial_kitchen" in special_hazards:
            heat_count += 3  # Kitchens need more heat detectors
        if "mechanical_rooms" in special_hazards:
            heat_count += 2

        requirements["Heat Detection"] = {
            "count": heat_count,
            "devices": self._get_devices_by_type(["heat", "detector"]),
            "reasoning": f"For special areas and {self.assessment.floors} floors",
        }

        # Notification devices (horns/strobes)
        notification_count = max(self.assessment.size_sqft // 2500, self.assessment.floors * 3)
        requirements["Notification"] = {
            "count": notification_count,
            "devices": self._get_devices_by_type(["horn", "strobe", "speaker", "bell"]),
            "reasoning": f"Coverage for {self.assessment.occupancy_level.lower()} occupancy",
        }

        # Manual pull stations
        pull_count = max(self.assessment.floors * 2, 4)  # Minimum 4, 2 per floor
        requirements["Manual Pull Stations"] = {
            "count": pull_count,
            "devices": self._get_devices_by_type(["pull", "station", "manual"]),
            "reasoning": "Code-required manual activation points",
        }

        # Annunciators (distinct category)
        annunciator_count = max(1, self.assessment.floors // 2)  # Example logic: 1 per 2 floors
        requirements["Annunciators"] = {
            "count": annunciator_count,
            "devices": self._get_devices_by_type(["annunciator"]),
            "reasoning": "For remote status indication and code compliance",
        }

        # Special hazard devices
        special_hazards = self.assessment.special_hazards or []
        if special_hazards:
            special_devices = []
            if "data_center" in special_hazards:
                special_devices.extend(self._get_devices_by_type(["aspirating", "vesda"]))
            if "hazardous_storage" in special_hazards:
                special_devices.extend(self._get_devices_by_type(["flame", "gas"]))

            if special_devices:
                requirements["Special Hazard Protection"] = {
                    "count": len(special_hazards),
                    "devices": special_devices,
                    "reasoning": f"For {', '.join(special_hazards)}",
                }

        return requirements

    def _get_devices_by_type(self, keywords):
        """Get devices from catalog that match keywords."""
        matching_devices = []
        for device in self.device_catalog:
            device_type = device.get("type", "").lower()
            device_name = device.get("name", "").lower()
            device_model = device.get("model", "").lower()

            # Create combined search text
            search_text = f"{device_type} {device_name} {device_model}".lower()

            # Check if any keyword matches - prioritize exact matches
            match_found = False
            for keyword in keywords:
                keyword = keyword.lower()
                if keyword in search_text:
                    # For detector types, be more specific
                    if keyword == "smoke" and "smoke" in search_text:
                        match_found = True
                        break
                    elif keyword == "heat" and "heat" in search_text:
                        match_found = True
                        break
                    elif keyword == "detector" and "detector" in search_text:
                        # Only match 'detector' if no specific type is specified
                        if not any(
                            specific in keywords for specific in ["smoke", "heat", "flame", "gas"]
                        ):
                            match_found = True
                            break
                    elif keyword in [
                        "horn",
                        "strobe",
                        "speaker",
                        "bell",
                        "pull",
                        "station",
                        "manual",
                    ]:
                        if keyword in search_text:
                            match_found = True
                            break

            if match_found:
                matching_devices.append(device)

        return matching_devices[:5]  # Limit to top 5 options

    def _create_device_category_widget(self, category, device_info):
        """Create a widget for a device category."""
        category_frame = QFrame()
        category_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        category_frame.setStyleSheet(
            """
            QFrame {
                border: 3px solid #85c1e9;
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
                background-color: #f8fdff;
            }
        """
        )

        layout = QVBoxLayout(category_frame)

        # Category header
        header = QLabel(f"🔍 {category}")
        header.setStyleSheet(
            """
            font-size: 16px;
            color: #1a252f;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 900;
            margin-bottom: 8px;
        """
        )
        layout.addWidget(header)

        # Requirement info
        count = device_info["count"]
        reasoning = device_info["reasoning"]
        req_label = QLabel(f"📊 Estimated quantity: {count} devices\\n💡 {reasoning}")
        req_label.setStyleSheet(
            """
            font-size: 14px;
            color: #34495e;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 600;
            margin-bottom: 10px;
            line-height: 1.4;
        """
        )
        req_label.setWordWrap(True)
        layout.addWidget(req_label)

        # Device options
        devices = device_info["devices"]
        if devices:
            for device in devices[:3]:  # Show top 3 options
                device_option = self._create_device_option_widget(device, category)
                layout.addWidget(device_option)
        else:
            no_devices = QLabel("ℹ️ No matching devices found in catalog")
            no_devices.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 10px;")
            layout.addWidget(no_devices)

        return category_frame

    def _create_device_option_widget(self, device, category):
        """Create a device option widget."""
        option_frame = QFrame()
        option_frame.setStyleSheet(
            """
            QFrame {
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 10px;
                margin: 5px;
            }
            QFrame:hover {
                border-color: #3498db;
                background-color: #ebf5fb;
            }
        """
        )

        layout = QHBoxLayout(option_frame)

        # Device info
        info_layout = QVBoxLayout()

        name_label = QLabel(f"{device['manufacturer']} - {device['name']}")
        name_label.setStyleSheet(
            """
            font-size: 14px;
            color: #1a252f;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 700;
        """
        )

        model_label = QLabel(f"Model: {device['model']}")
        model_label.setStyleSheet(
            """
            font-size: 12px;
            color: #7f8c8d;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
        """
        )

        info_layout.addWidget(name_label)
        info_layout.addWidget(model_label)

        # Add button
        add_btn = QPushButton("➕ Add to System")
        add_btn.setFixedSize(120, 30)
        add_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-weight: 600;
                font-size: 11px;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """
        )
        add_btn.clicked.connect(lambda: self._add_device_to_system(device, category))

        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addWidget(add_btn)

        return option_frame

    def _add_device_to_system(self, device, category):
        """Add a device to the selected system."""
        if not hasattr(self, "selected_devices_by_category"):
            self.selected_devices_by_category = {}

        if category not in self.selected_devices_by_category:
            self.selected_devices_by_category[category] = []

        self.selected_devices_by_category[category].append(device)

        logger.info(
            f"Device added to system: {device['manufacturer']} {device['model']} "
            f"(Category: {category})"
        )

        # Update the device list
        self.selected_devices = []
        for devices in self.selected_devices_by_category.values():
            self.selected_devices.extend(devices)

    def _populate_wire_options(self):
        """Populate wire options based on actual device selections."""
        while self.wire_options_layout.count():
            child = self.wire_options_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if (
            not hasattr(self, "selected_devices_by_category")
            or not self.selected_devices_by_category
        ):
            info = QLabel("Please select devices first to see wire requirements.")
            info.setStyleSheet(
                """
                padding: 25px;
                color: #e67e22;
                font-style: italic;
                font-size: 16px;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                font-weight: 600;
                background-color: #fff8e1;
                border: 3px dashed #f39c12;
                border-radius: 10px;
                text-align: center;
            """
            )
            self.wire_options_layout.addWidget(info)
            return

        # Calculate wire requirements based on selected devices
        wire_requirements = self._calculate_wire_requirements()

        # Create wire category sections
        for circuit_type, wire_info in wire_requirements.items():
            wire_widget = self._create_wire_category_widget(circuit_type, wire_info)
            self.wire_options_layout.addWidget(wire_widget)

        # Store wire selections for system review
        self.selected_wires = wire_requirements

        # Enable next step
        self.next_btn.setEnabled(True)
        logger.info(f"Wire planning populated for {len(wire_requirements)} circuit types")

    def _calculate_wire_requirements(self):
        """Calculate wire requirements based on selected devices and panel."""
        requirements = {}

        # Get device counts by category
        total_devices = sum(len(devices) for devices in self.selected_devices_by_category.values())

        # SLC (Signaling Line Circuit) - for addressable devices
        if self.selected_panel and "addressable" in self.recommendations.panel_type.lower():
            slc_devices = total_devices
            slc_length = self._estimate_circuit_length(slc_devices)

            requirements["SLC (Signaling Line Circuit)"] = {
                "wire_type": "FPLR 18 AWG Shielded",
                "estimated_length": slc_length,
                "device_count": slc_devices,
                "reasoning": "Connects addressable devices to control panel",
                "code_requirements": "NFPA 72: Class A or Class B wiring permitted",
            }

        # NAC (Notification Appliance Circuit) - for horns/strobes
        notification_devices = len(self.selected_devices_by_category.get("Notification", []))
        if notification_devices > 0:
            nac_length = self._estimate_circuit_length(notification_devices)

            requirements["NAC (Notification Appliance Circuit)"] = {
                "wire_type": "FPLR 14 AWG or 16 AWG",
                "estimated_length": nac_length,
                "device_count": notification_devices,
                "reasoning": "Powers horns, strobes, and speakers",
                "code_requirements": "NFPA 72: Supervised circuits required",
            }

        # IDC (Initiating Device Circuit) - for conventional detectors
        if "conventional" in self.recommendations.panel_type.lower():
            detection_devices = len(
                self.selected_devices_by_category.get("Smoke Detection", [])
            ) + len(self.selected_devices_by_category.get("Heat Detection", []))
            if detection_devices > 0:
                idc_length = self._estimate_circuit_length(detection_devices)

                requirements["IDC (Initiating Device Circuit)"] = {
                    "wire_type": "FPLR 18 AWG",
                    "estimated_length": idc_length,
                    "device_count": detection_devices,
                    "reasoning": "Connects conventional detectors to panel",
                    "code_requirements": "NFPA 72: Class B wiring typical",
                }

        # Power/Control wiring
        power_length = max(100, self.assessment.size_sqft // 50)  # Rough estimate
        requirements["Power & Control Wiring"] = {
            "wire_type": "THHN 12 AWG in conduit",
            "estimated_length": power_length,
            "device_count": 1,
            "reasoning": "AC power and control connections",
            "code_requirements": "NEC Article 760: Listed fire alarm cables",
        }

        # Communication/Data (if needed)
        if self.assessment.floors > 1 or "data_center" in (self.assessment.special_hazards or []):
            comm_length = self.assessment.floors * 200
            requirements["Communication/Data"] = {
                "wire_type": "CAT6 or Fiber Optic",
                "estimated_length": comm_length,
                "device_count": self.assessment.floors,
                "reasoning": "Network communication between floors/buildings",
                "code_requirements": "NFPA 72: Listed communication cables",
            }

        return requirements

    def _estimate_circuit_length(self, device_count):
        """Estimate circuit wire length based on device count and building size."""
        # Base calculation: building perimeter + vertical runs + device drops
        base_length = (self.assessment.size_sqft**0.5) * 4  # Rough building perimeter
        vertical_runs = self.assessment.floors * 50  # 50 ft per floor
        device_drops = device_count * 25  # 25 ft average per device

        total_length = base_length + vertical_runs + device_drops

        # Add 20% safety factor
        return int(total_length * 1.2)

    def _create_wire_category_widget(self, circuit_type, wire_info):
        """Create a widget for a wire circuit category."""
        category_frame = QFrame()
        category_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        category_frame.setStyleSheet(
            """
            QFrame {
                border: 3px solid #f8c471;
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
                background-color: #fef9e7;
            }
        """
        )

        layout = QVBoxLayout(category_frame)

        # Circuit header
        header = QLabel(f"🔌 {circuit_type}")
        header.setStyleSheet(
            """
            font-size: 16px;
            color: #1a252f;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 900;
            margin-bottom: 8px;
        """
        )
        layout.addWidget(header)

        # Wire specifications
        wire_type = wire_info["wire_type"]
        length = wire_info["estimated_length"]
        device_count = wire_info["device_count"]
        reasoning = wire_info["reasoning"]
        code_req = wire_info["code_requirements"]

        spec_text = f"""
        📏 Wire Type: {wire_type}
        📐 Estimated Length: {length:,} feet
        🔗 Connected Devices: {device_count}
        💡 Purpose: {reasoning}
        📋 Code: {code_req}
        """

        spec_label = QLabel(spec_text.strip())
        spec_label.setStyleSheet(
            """
            font-size: 14px;
            color: #34495e;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 600;
            line-height: 1.5;
            padding: 10px;
            background-color: #ffffff;
            border-radius: 6px;
            border: 2px solid #f8c471;
        """
        )
        spec_label.setWordWrap(True)
        layout.addWidget(spec_label)

        return category_frame

    def _populate_review(self):
        """Populate comprehensive system review with export options."""
        while self.review_layout.count():
            child = self.review_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # System summary header
        summary_html = "".join(
            [
                '<h3 style="color: #1a252f; margin-bottom: 10px; '
                'font-size: 18px; font-weight: 900;">� Fire Alarm System Design Summary</h3>',
                '<p style="color: #2c3e50; font-size: 14px; line-height: 1.5;">',
                "Complete system design ready for implementation and documentation.",
                "</p>",
            ]
        )
        summary_header = QLabel(summary_html)
        summary_header.setWordWrap(True)
        summary_header.setStyleSheet(
            """
            background-color: #eaf2f8;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #3498db;
            border: 2px solid #aed6f1;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            margin-bottom: 15px;
        """
        )
        self.review_layout.addWidget(summary_header)

        # Project assessment summary
        assessment_widget = self._create_assessment_summary_widget()
        self.review_layout.addWidget(assessment_widget)

        # Selected panel summary
        if self.selected_panel:
            panel_widget = self._create_panel_summary_widget()
            self.review_layout.addWidget(panel_widget)

        # Device summary
        if hasattr(self, "selected_devices_by_category") and self.selected_devices_by_category:
            device_widget = self._create_device_summary_widget()
            self.review_layout.addWidget(device_widget)

        # Wire summary
        if hasattr(self, "selected_wires") and self.selected_wires:
            wire_widget = self._create_wire_summary_widget()
            self.review_layout.addWidget(wire_widget)

        # Export options
        export_widget = self._create_export_options_widget()
        self.review_layout.addWidget(export_widget)

        logger.info("System review populated with complete design summary")

    def _create_assessment_summary_widget(self):
        """Create project assessment summary widget."""
        widget = QFrame()
        widget.setStyleSheet(
            """
            QFrame {
                background-color: #f8fdff;
                border: 3px solid #85c1e9;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }
        """
        )

        layout = QVBoxLayout(widget)

        header = QLabel("🏢 Building Assessment")
        header.setStyleSheet(
            """
            font-size: 16px;
            color: #1a252f;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 900;
            margin-bottom: 10px;
        """
        )
        layout.addWidget(header)

        special_hazards = self.assessment.special_hazards or []
        hazards_text = ", ".join(special_hazards) if special_hazards else "None"

        summary_text = f"""
        • Building Type: {self.assessment.building_type}
        • Size: {self.assessment.size_sqft:,} sq ft
        • Floors: {self.assessment.floors}
        • Occupancy: {self.assessment.occupancy_level}
        • Special Hazards: {hazards_text}
        """

        summary_label = QLabel(summary_text.strip())
        summary_label.setStyleSheet(
            """
            font-size: 14px;
            color: #34495e;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 600;
            line-height: 1.6;
        """
        )
        layout.addWidget(summary_label)

        return widget

    def _create_panel_summary_widget(self):
        """Create selected panel summary widget."""
        widget = QFrame()
        widget.setStyleSheet(
            """
            QFrame {
                background-color: #f0fdf4;
                border: 3px solid #82e89a;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }
        """
        )

        layout = QVBoxLayout(widget)

        header = QLabel("🔧 Selected Control Panel")
        header.setStyleSheet(
            """
            font-size: 16px;
            color: #0d5016;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 900;
            margin-bottom: 10px;
        """
        )
        layout.addWidget(header)

        if self.selected_panel:
            panel_text = f"""
        • Manufacturer: {self.selected_panel.get('manufacturer', 'Unknown')}
        • Model: {self.selected_panel.get('model', 'Unknown')}
        • Suitability Score: {self.selected_panel.get('suitability_score', 'N/A')}%
        • Reason: {self.selected_panel.get('recommendation_reason', 'Selected by user')}
        """
        else:
            panel_text = "• No panel selected"

        panel_label = QLabel(panel_text.strip())
        panel_label.setStyleSheet(
            """
            font-size: 14px;
            color: #0d5016;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 600;
            line-height: 1.6;
        """
        )
        layout.addWidget(panel_label)

        return widget

    def _create_device_summary_widget(self):
        """Create device selection summary widget."""
        widget = QFrame()
        widget.setStyleSheet(
            """
            QFrame {
                background-color: #fffbf0;
                border: 3px solid #f8c471;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }
        """
        )

        layout = QVBoxLayout(widget)

        header = QLabel("🔍 Selected Devices")
        header.setStyleSheet(
            """
            font-size: 16px;
            color: #8b2635;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 900;
            margin-bottom: 10px;
        """
        )
        layout.addWidget(header)

        device_text = ""
        total_devices = 0
        for category, devices in self.selected_devices_by_category.items():
            device_count = len(devices)
            total_devices += device_count
            device_text += f"• {category}: {device_count} devices\\n"

        device_text += f"\\n• Total Devices: {total_devices}"

        device_label = QLabel(device_text.strip())
        device_label.setStyleSheet(
            """
            font-size: 14px;
            color: #8b2635;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 600;
            line-height: 1.6;
        """
        )
        layout.addWidget(device_label)

        return widget

    def _create_wire_summary_widget(self):
        """Create wire requirements summary widget."""
        widget = QFrame()
        widget.setStyleSheet(
            """
            QFrame {
                background-color: #fef9e7;
                border: 3px solid #f8c471;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }
        """
        )

        layout = QVBoxLayout(widget)

        header = QLabel("🔌 Wire Requirements")
        header.setStyleSheet(
            """
            font-size: 16px;
            color: #d68910;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 900;
            margin-bottom: 10px;
        """
        )
        layout.addWidget(header)

        wire_text = ""
        total_length = 0

        if hasattr(self, "selected_wires") and self.selected_wires:
            # Handle both dict and list formats
            if isinstance(self.selected_wires, dict):
                for circuit_type, wire_info in self.selected_wires.items():
                    if isinstance(wire_info, dict):
                        length = wire_info.get("estimated_length", 0)
                        wire_type = wire_info.get("wire_type", "Unknown")
                        total_length += length
                        wire_text += f"• {circuit_type}: {length:,} ft ({wire_type})\\n"
            elif isinstance(self.selected_wires, list):
                for wire_info in self.selected_wires:
                    if isinstance(wire_info, dict):
                        circuit_type = wire_info.get("circuit_type", "Unknown")
                        length = wire_info.get("estimated_length", 0)
                        wire_type = wire_info.get("wire_type", "Unknown")
                        total_length += length
                        wire_text += f"• {circuit_type}: {length:,} ft ({wire_type})\\n"

        if wire_text:
            wire_text += f"\\n• Total Wire Length: {total_length:,} feet"
        else:
            wire_text = "• No wire requirements calculated"

        wire_label = QLabel(wire_text.strip())
        wire_label.setStyleSheet(
            """
            font-size: 14px;
            color: #d68910;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 600;
            line-height: 1.6;
        """
        )
        layout.addWidget(wire_label)

        return widget

    def _create_export_options_widget(self):
        """Create export options widget."""
        widget = QFrame()
        widget.setStyleSheet(
            """
            QFrame {
                background-color: #f4f6f7;
                border: 3px solid #aab7b8;
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
            }
        """
        )

        layout = QVBoxLayout(widget)

        header = QLabel("📄 Export & Documentation Options")
        header.setStyleSheet(
            """
            font-size: 16px;
            color: #1a252f;
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-weight: 900;
            margin-bottom: 15px;
        """
        )
        layout.addWidget(header)

        # Export buttons
        button_layout = QHBoxLayout()

        export_summary_btn = QPushButton("📋 Export System Summary")
        export_summary_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 900;
                font-size: 14px;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        export_summary_btn.clicked.connect(self._export_system_summary)

        export_specs_btn = QPushButton("📊 Generate Specifications")
        export_specs_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e67e22;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 900;
                font-size: 14px;
                font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """
        )
        export_specs_btn.clicked.connect(self._generate_specifications)

        button_layout.addWidget(export_summary_btn)
        button_layout.addWidget(export_specs_btn)
        layout.addLayout(button_layout)

        return widget

    def _export_system_summary(self):
        """Export system summary to text file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fire_alarm_system_summary_{timestamp}.txt"

            summary_content = self._generate_summary_content()

            with open(filename, "w") as f:
                f.write(summary_content)

            logger.info(f"System summary exported to {filename}")
            self._show_export_success(f"System summary exported to {filename}")

        except Exception as e:
            logger.error(f"Error exporting system summary: {e}")
            self._show_export_error(f"Error exporting summary: {e}")

    def _generate_specifications(self):
        """Generate detailed specifications document."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fire_alarm_specifications_{timestamp}.txt"

            specs_content = self._generate_specifications_content()

            with open(filename, "w") as f:
                f.write(specs_content)

            logger.info(f"Specifications generated: {filename}")
            self._show_export_success(f"Specifications generated: {filename}")

        except Exception as e:
            logger.error(f"Error generating specifications: {e}")
            self._show_export_error(f"Error generating specifications: {e}")

    def _generate_summary_content(self):
        """Generate summary content for export."""
        content = f"""
FIRE ALARM SYSTEM DESIGN SUMMARY
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
========================================

BUILDING ASSESSMENT:
- Building Type: {self.assessment.building_type}
- Size: {self.assessment.size_sqft:,} sq ft
- Floors: {self.assessment.floors}
- Occupancy: {self.assessment.occupancy_level}
- Special Hazards: {', '.join(self.assessment.special_hazards or ['None'])}

SELECTED CONTROL PANEL:
- Manufacturer: {self.selected_panel['manufacturer'] if self.selected_panel else 'None selected'}
- Model: {self.selected_panel['model'] if self.selected_panel else 'None selected'}
- Suitability Score: {
    self.selected_panel.get('suitability_score', 'N/A') if self.selected_panel else 'N/A'
}%

DEVICE SUMMARY:
"""

        if hasattr(self, "selected_devices_by_category") and self.selected_devices_by_category:
            total_devices = 0
            for category, devices in self.selected_devices_by_category.items():
                device_count = len(devices)
                total_devices += device_count
                content += f"- {category}: {device_count} devices\\n"
            content += f"- Total Devices: {total_devices}\\n"
        else:
            content += "- No devices selected\\n"

        content += "\\nWIRE REQUIREMENTS:\\n"
        if hasattr(self, "selected_wires") and self.selected_wires:
            total_length = 0
            # Handle both dict and list formats
            if isinstance(self.selected_wires, dict):
                for circuit_type, wire_info in self.selected_wires.items():
                    if isinstance(wire_info, dict):
                        length = wire_info.get("estimated_length", 0)
                        wire_type = wire_info.get("wire_type", "Unknown")
                        total_length += length
                        content += f"- {circuit_type}: {length:,} ft ({wire_type})\\n"
            elif isinstance(self.selected_wires, list):
                for wire_info in self.selected_wires:
                    if isinstance(wire_info, dict):
                        circuit_type = wire_info.get("circuit_type", "Unknown")
                        length = wire_info.get("estimated_length", 0)
                        wire_type = wire_info.get("wire_type", "Unknown")
                        total_length += length
                        content += f"- {circuit_type}: {length:,} ft ({wire_type})\\n"

            if total_length > 0:
                content += f"- Total Wire Length: {total_length:,} feet\\n"
            else:
                content += "- No wire requirements calculated\\n"
        else:
            content += "- No wire requirements calculated\\n"

        return content

    def _generate_specifications_content(self):
        """Generate detailed specifications content."""
        content = self._generate_summary_content()

        content += """

DETAILED SPECIFICATIONS:
========================

CODE COMPLIANCE:
- NFPA 72: National Fire Alarm and Signaling Code
- Local Authority Having Jurisdiction (AHJ) requirements
- Building codes and accessibility standards

INSTALLATION REQUIREMENTS:
- All devices installed per manufacturer specifications
- Proper circuit supervision and monitoring
- Regular testing and maintenance schedule
- Documentation and as-built drawings required

SYSTEM TESTING:
- Initial acceptance testing per NFPA 72
- Annual testing and inspection
- Battery backup testing
- Communication pathway verification
"""

        return content

    def _show_export_success(self, message):
        """Show export success message."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Export Successful")
        msg.setText(message)
        msg.exec()

    def _show_export_error(self, message):
        """Show export error message."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Export Error")
        msg.setText(message)
        msg.exec()

    def _update_guidance(self, message):
        """Update guidance text."""
        self.guidance_label.setText(f"💡 {message}")

    def _complete_system(self):
        """Complete the system design."""
        system_data = {
            "assessment": asdict(self.assessment),
            "recommendations": asdict(self.recommendations),
            "selected_panel": self.selected_panel,
            "selected_devices": self.selected_devices,
            "selected_wires": self.selected_wires,
        }

        self.system_completed.emit(system_data)
        self.assembled.emit(system_data)  # Backward compatibility

        self._update_guidance("🎉 System design complete! Ready for implementation.")

    def _assemble_system(self):
        """Backward compatibility method."""
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
            ]


# Export for backward compatibility
SystemBuilderWidget = ImprovedGuidedSystemBuilder
GuidedSystemBuilderWidget = ImprovedGuidedSystemBuilder
