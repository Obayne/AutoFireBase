"""
Fixed Guided Fire Alarm System Builder
=====================================

Addresses critical UI issues:
1. Navigation buttons dropping off screen (proper scrolling)
2. Device selection not working (fixed selection logic)
3. Panel selection issues (improved auto-selection)
4. Menu behaviors and automatic selections

This is a completely redesigned version with proper layout management,
working selection mechanisms, and improved user experience.
"""

import os
import sqlite3
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

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
    QScrollArea,  # Added for proper scrolling
    QFrame,
    QSizePolicy,
    QSpacerItem,
)

# Import our professional design system
try:
    from frontend.design_system import AutoFireColor, AutoFireStyleSheet, AutoFireFont
    DESIGN_SYSTEM_AVAILABLE = True
except ImportError:
    # Fallback for development/testing
    DESIGN_SYSTEM_AVAILABLE = False
    class AutoFireColor:
        PRIMARY = "#C41E3A"
        SECONDARY = "#8B0000"
        ACCENT = "#FF6B35"
        
    class AutoFireStyleSheet:
        @staticmethod
        def group_box(): return ""
        @staticmethod 
        def button_primary(): return ""
        @staticmethod
        def input_field(): return ""


@dataclass
class BuildingAssessment:
    """Building assessment data."""
    building_type: str = ""
    size_sqft: int = 0
    floors: int = 1
    occupancy_level: str = ""
    special_hazards: List[str] = None
    ahj_requirements: str = ""

    def __post_init__(self):
        if self.special_hazards is None:
            self.special_hazards = []


@dataclass
class SystemRecommendation:
    """System recommendations based on assessment."""
    panel_type: str = ""
    panel_zones: int = 0
    device_count_estimate: Dict[str, int] = None
    wire_requirements: Dict[str, str] = None
    compliance_notes: List[str] = None

    def __post_init__(self):
        if self.device_count_estimate is None:
            self.device_count_estimate = {}
        if self.wire_requirements is None:
            self.wire_requirements = {}
        if self.compliance_notes is None:
            self.compliance_notes = []


class ImprovedGuidedSystemBuilder(QWidget):
    """
    Improved Guided System Builder with fixed UI issues.
    
    Key improvements:
    - Proper scrollable layout to prevent buttons from dropping off screen
    - Working device and panel selection with clear feedback
    - No automatic selections unless explicitly enabled
    - Improved menu behaviors and navigation
    """
    
    # Signals
    system_completed = Signal(dict)
    step_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Data storage
        self.building_assessment = BuildingAssessment()
        self.system_recommendation = SystemRecommendation()
        self.selected_devices = {}
        self.selected_panel = None
        self.auto_select_enabled = False  # User must explicitly enable
        
        # Current step tracking
        self.current_step = 0
        self.total_steps = 4
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Setup the improved UI with proper layout management."""
        # Main layout - use proper sizing
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header with progress
        self.header_widget = self._create_header()
        main_layout.addWidget(self.header_widget)
        
        # Create scrollable content area - THIS FIXES THE DROPDOWN ISSUE
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Content widget inside scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Tab widget for steps
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumHeight(500)  # Ensure minimum visible area
        
        # Setup all tabs
        self._setup_all_tabs()
        
        content_layout.addWidget(self.tab_widget)
        
        # Add some spacing at bottom to ensure buttons are always visible
        content_layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # FIXED NAVIGATION BAR - Always visible at bottom
        nav_frame = QFrame()
        nav_frame.setFrameStyle(QFrame.StyledPanel)
        nav_frame.setFixedHeight(80)  # Fixed height prevents dropping off
        
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(15, 10, 15, 10)
        
        # Back button
        self.back_btn = QPushButton("⬅️ Back")
        self.back_btn.setFixedSize(100, 40)
        self.back_btn.setEnabled(False)
        
        # Auto-select toggle
        self.auto_select_checkbox = QCheckBox("Enable Auto-Selection")
        self.auto_select_checkbox.setToolTip("When enabled, system will automatically select recommended options")
        self.auto_select_checkbox.toggled.connect(self._on_auto_select_toggled)
        
        # Progress indicator
        progress_label = QLabel(f"Step {self.current_step + 1} of {self.total_steps}")
        progress_label.setAlignment(Qt.AlignCenter)
        
        # Next/Complete buttons
        self.next_btn = QPushButton("Next ➡️")
        self.next_btn.setFixedSize(100, 40)
        
        self.complete_btn = QPushButton("🚀 Complete System")
        self.complete_btn.setFixedSize(150, 40)
        self.complete_btn.setVisible(False)
        
        # Layout navigation
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.auto_select_checkbox)
        nav_layout.addStretch()
        nav_layout.addWidget(progress_label)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.complete_btn)
        
        main_layout.addWidget(nav_frame)
        
        # Apply styling
        if DESIGN_SYSTEM_AVAILABLE:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: #f8f9fa;
                    color: #333;
                }}
                QPushButton {{
                    background-color: {AutoFireColor.PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {AutoFireColor.SECONDARY};
                }}
                QPushButton:disabled {{
                    background-color: #ccc;
                    color: #666;
                }}
                QFrame {{
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                }}
            """)
    
    def _create_header(self):
        """Create header with progress tracking."""
        header = QFrame()
        header.setFixedHeight(120)
        layout = QVBoxLayout(header)
        
        # Title
        title = QLabel("🔥 FlameCAD Professional System Builder")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #C41E3A; padding: 10px;")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.total_steps)
        self.progress_bar.setValue(self.current_step + 1)
        self.progress_bar.setFormat("Step %v of %m")
        
        # Status label
        self.status_label = QLabel("Complete building assessment to begin")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        
        layout.addWidget(title)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
        return header
    
    def _setup_all_tabs(self):
        """Setup all workflow tabs."""
        self._setup_building_assessment_tab()
        self._setup_panel_selection_tab()
        self._setup_device_planning_tab()
        self._setup_system_review_tab()
    
    def _setup_building_assessment_tab(self):
        """Setup Step 1: Building Assessment with working form."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Guidance text
        guidance = QLabel("""
        <h3>🏢 Building Assessment</h3>
        <p>Provide information about your building to receive accurate system recommendations.</p>
        <p><b>Note:</b> All fields are required for proper system sizing.</p>
        """)
        guidance.setWordWrap(True)
        layout.addWidget(guidance)
        
        # Form with improved controls
        form_group = QGroupBox("Building Information")
        form_layout = QFormLayout(form_group)
        
        # Building type with clear options
        self.building_type_combo = QComboBox()
        building_types = [
            "-- Select Building Type --",
            "Office Building",
            "Retail Store", 
            "Warehouse",
            "School",
            "Hospital/Healthcare",
            "Hotel",
            "Restaurant",
            "Manufacturing",
            "Other"
        ]
        self.building_type_combo.addItems(building_types)
        self.building_type_combo.currentTextChanged.connect(self._on_building_type_changed)
        
        # Size with validation
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(100, 1000000)
        self.size_spinbox.setValue(5000)
        self.size_spinbox.setSuffix(" sq ft")
        self.size_spinbox.valueChanged.connect(self._on_size_changed)
        
        # Floors
        self.floors_spinbox = QSpinBox()
        self.floors_spinbox.setRange(1, 50)
        self.floors_spinbox.setValue(1)
        
        # Occupancy level
        self.occupancy_combo = QComboBox()
        occupancy_levels = [
            "-- Select Occupancy Level --",
            "Light (< 50 people)",
            "Moderate (50-300 people)",
            "Heavy (300-1000 people)",
            "Very Heavy (> 1000 people)"
        ]
        self.occupancy_combo.addItems(occupancy_levels)
        
        # Special hazards with checkboxes
        hazards_group = QGroupBox("Special Hazards (Check all that apply)")
        hazards_layout = QVBoxLayout(hazards_group)
        
        self.hazard_checkboxes = {}
        hazards = [
            "Kitchen/Cooking Areas",
            "Server/Computer Rooms", 
            "Chemical Storage",
            "High Ceiling Areas (>30 ft)",
            "Outdoor Areas",
            "Freezer/Cold Storage"
        ]
        
        for hazard in hazards:
            checkbox = QCheckBox(hazard)
            self.hazard_checkboxes[hazard] = checkbox
            hazards_layout.addWidget(checkbox)
        
        # Add to form
        form_layout.addRow("Building Type:", self.building_type_combo)
        form_layout.addRow("Building Size:", self.size_spinbox)
        form_layout.addRow("Number of Floors:", self.floors_spinbox)
        form_layout.addRow("Occupancy Level:", self.occupancy_combo)
        
        layout.addWidget(form_group)
        layout.addWidget(hazards_group)
        
        # Validation status
        self.validation_label = QLabel("❌ Please complete all required fields")
        self.validation_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.validation_label)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "1. Building Assessment")
    
    def _setup_panel_selection_tab(self):
        """Setup Step 2: Panel Selection with working selection."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Guidance
        guidance = QLabel("""
        <h3>🔧 Fire Alarm Control Panel Selection</h3>
        <p>Select an appropriate control panel based on your building assessment.</p>
        <p><b>Recommendation:</b> Panels are suggested based on building size and device count.</p>
        """)
        guidance.setWordWrap(True)
        layout.addWidget(guidance)
        
        # Panel options group
        self.panel_group = QGroupBox("Available Control Panels")
        panel_layout = QVBoxLayout(self.panel_group)
        
        # Panel selection will be populated after building assessment
        self.panel_selection_label = QLabel("⏳ Complete building assessment first")
        panel_layout.addWidget(self.panel_selection_label)
        
        layout.addWidget(self.panel_group)
        
        # Selected panel display
        self.selected_panel_label = QLabel("No panel selected")
        self.selected_panel_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.selected_panel_label)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "2. Panel Selection")
    
    def _setup_device_planning_tab(self):
        """Setup Step 3: Device Planning with working selection."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Guidance
        guidance = QLabel("""
        <h3>🔍 Detection & Notification Device Planning</h3>
        <p>Select devices for your fire alarm system. Recommendations are based on building type and NFPA 72.</p>
        """)
        guidance.setWordWrap(True)
        layout.addWidget(guidance)
        
        # Device categories
        self.device_groups = {}
        
        # Smoke Detectors
        smoke_group = QGroupBox("Smoke Detection Devices")
        smoke_layout = QFormLayout(smoke_group)
        
        self.smoke_detector_spin = QSpinBox()
        self.smoke_detector_spin.setRange(0, 500)
        self.smoke_detector_spin.valueChanged.connect(lambda v: self._on_device_count_changed("smoke_detectors", v))
        
        smoke_layout.addRow("Smoke Detectors:", self.smoke_detector_spin)
        self.device_groups["smoke_detectors"] = self.smoke_detector_spin
        
        # Manual Pull Stations
        pull_group = QGroupBox("Manual Notification Devices")
        pull_layout = QFormLayout(pull_group)
        
        self.pull_station_spin = QSpinBox()
        self.pull_station_spin.setRange(0, 100)
        self.pull_station_spin.valueChanged.connect(lambda v: self._on_device_count_changed("pull_stations", v))
        
        pull_layout.addRow("Manual Pull Stations:", self.pull_station_spin)
        self.device_groups["pull_stations"] = self.pull_station_spin
        
        # Notification Appliances
        notification_group = QGroupBox("Notification Appliances")
        notification_layout = QFormLayout(notification_group)
        
        self.horn_strobe_spin = QSpinBox()
        self.horn_strobe_spin.setRange(0, 200)
        self.horn_strobe_spin.valueChanged.connect(lambda v: self._on_device_count_changed("horn_strobes", v))
        
        notification_layout.addRow("Horn/Strobes:", self.horn_strobe_spin)
        self.device_groups["horn_strobes"] = self.horn_strobe_spin
        
        layout.addWidget(smoke_group)
        layout.addWidget(pull_group)
        layout.addWidget(notification_group)
        
        # Device summary
        self.device_summary_label = QLabel("Total Devices: 0")
        self.device_summary_label.setStyleSheet("font-weight: bold; color: #C41E3A;")
        layout.addWidget(self.device_summary_label)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "3. Device Planning")
    
    def _setup_system_review_tab(self):
        """Setup Step 4: System Review."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Guidance
        guidance = QLabel("""
        <h3>📋 System Review & Completion</h3>
        <p>Review your complete fire alarm system configuration before finalizing.</p>
        """)
        guidance.setWordWrap(True)
        layout.addWidget(guidance)
        
        # System summary
        self.system_summary = QTextEdit()
        self.system_summary.setReadOnly(True)
        self.system_summary.setMaximumHeight(300)
        layout.addWidget(self.system_summary)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "4. System Review")
    
    def _connect_signals(self):
        """Connect all UI signals."""
        self.back_btn.clicked.connect(self._on_back_clicked)
        self.next_btn.clicked.connect(self._on_next_clicked)
        self.complete_btn.clicked.connect(self._on_complete_clicked)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def _on_auto_select_toggled(self, checked):
        """Handle auto-selection toggle."""
        self.auto_select_enabled = checked
        if checked:
            self.status_label.setText("🤖 Auto-selection enabled - recommendations will be pre-selected")
            self._apply_auto_selections()
        else:
            self.status_label.setText("Manual selection mode - choose your options carefully")
    
    def _on_building_type_changed(self, building_type):
        """Handle building type change with recommendations."""
        if building_type != "-- Select Building Type --":
            self.building_assessment.building_type = building_type
            self._validate_assessment()
            if self.auto_select_enabled:
                self._suggest_building_defaults()
    
    def _on_size_changed(self, size):
        """Handle building size change."""
        self.building_assessment.size_sqft = size
        self._validate_assessment()
        if self.auto_select_enabled:
            self._update_device_recommendations()
    
    def _validate_assessment(self):
        """Validate building assessment completion."""
        valid = (
            self.building_assessment.building_type and
            self.building_assessment.building_type != "-- Select Building Type --" and
            self.building_assessment.size_sqft > 0 and
            self.occupancy_combo.currentText() != "-- Select Occupancy Level --"
        )
        
        if valid:
            self.validation_label.setText("✅ Assessment complete - ready to proceed")
            self.validation_label.setStyleSheet("color: green; font-weight: bold;")
            self._update_panel_options()
        else:
            self.validation_label.setText("❌ Please complete all required fields")
            self.validation_label.setStyleSheet("color: red; font-weight: bold;")
    
    def _update_panel_options(self):
        """Update panel selection based on assessment."""
        # Clear existing options
        panel_layout = self.panel_group.layout()
        while panel_layout.count():
            child = panel_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add panel options based on building size
        size = self.building_assessment.size_sqft
        
        panels = []
        if size < 10000:
            panels = [
                ("Small System Panel", "4-zone conventional", "$800"),
                ("Addressable Small Panel", "32-device addressable", "$1,500")
            ]
        elif size < 50000:
            panels = [
                ("Medium System Panel", "8-zone conventional", "$1,200"),
                ("Addressable Medium Panel", "159-device addressable", "$2,800"),
                ("Network Panel", "318-device networked", "$4,500")
            ]
        else:
            panels = [
                ("Large System Panel", "16-zone conventional", "$2,000"),
                ("Addressable Large Panel", "636-device addressable", "$6,500"),
                ("Enterprise Network Panel", "1272-device networked", "$12,000")
            ]
        
        self.panel_buttons = []
        for name, specs, cost in panels:
            button = QPushButton(f"{name}\\n{specs}\\n{cost}")
            button.setCheckable(True)
            button.clicked.connect(lambda checked, n=name: self._on_panel_selected(n, checked))
            panel_layout.addWidget(button)
            self.panel_buttons.append(button)
        
        # Auto-select first option if enabled
        if self.auto_select_enabled and panels:
            self.panel_buttons[0].setChecked(True)
            self._on_panel_selected(panels[0][0], True)
    
    def _on_panel_selected(self, panel_name, checked):
        """Handle panel selection."""
        if checked:
            # Uncheck other panels
            for button in self.panel_buttons:
                if button.text().split("\\n")[0] != panel_name:
                    button.setChecked(False)
            
            self.selected_panel = panel_name
            self.selected_panel_label.setText(f"✅ Selected: {panel_name}")
            self.selected_panel_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.selected_panel = None
            self.selected_panel_label.setText("No panel selected")
            self.selected_panel_label.setStyleSheet("color: #666; font-style: italic;")
    
    def _on_device_count_changed(self, device_type, count):
        """Handle device count changes."""
        self.selected_devices[device_type] = count
        self._update_device_summary()
    
    def _update_device_summary(self):
        """Update device count summary."""
        total = sum(self.selected_devices.values())
        self.device_summary_label.setText(f"Total Devices: {total}")
        
        if total > 0:
            self.device_summary_label.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.device_summary_label.setStyleSheet("font-weight: bold; color: #C41E3A;")
    
    def _apply_auto_selections(self):
        """Apply automatic selections when enabled."""
        if self.building_assessment.size_sqft > 0:
            self._update_device_recommendations()
    
    def _update_device_recommendations(self):
        """Update device recommendations based on building assessment."""
        if not self.auto_select_enabled:
            return
        
        size = self.building_assessment.size_sqft
        
        # Calculate recommended device counts
        smoke_count = max(1, size // 900)  # ~30x30 ft coverage
        pull_count = max(2, size // 2000)  # ~200 ft travel distance
        horn_count = max(1, size // 1000)  # Notification coverage
        
        # Update spinboxes
        self.smoke_detector_spin.setValue(smoke_count)
        self.pull_station_spin.setValue(pull_count)
        self.horn_strobe_spin.setValue(horn_count)
    
    def _suggest_building_defaults(self):
        """Suggest defaults based on building type."""
        if not self.auto_select_enabled:
            return
            
        building_type = self.building_assessment.building_type
        
        # Set reasonable defaults based on building type
        if "Office" in building_type:
            self.occupancy_combo.setCurrentText("Moderate (50-300 people)")
        elif "Warehouse" in building_type:
            self.occupancy_combo.setCurrentText("Light (< 50 people)")
        elif "School" in building_type or "Hospital" in building_type:
            self.occupancy_combo.setCurrentText("Heavy (300-1000 people)")
    
    def _on_back_clicked(self):
        """Handle back button click."""
        if self.current_step > 0:
            self.current_step -= 1
            self.tab_widget.setCurrentIndex(self.current_step)
            self._update_navigation()
    
    def _on_next_clicked(self):
        """Handle next button click."""
        if self._validate_current_step():
            if self.current_step < self.total_steps - 1:
                self.current_step += 1
                self.tab_widget.setCurrentIndex(self.current_step)
                self._update_navigation()
                
                # Populate next step if needed
                if self.current_step == 2 and self.auto_select_enabled:  # Device planning
                    self._update_device_recommendations()
                elif self.current_step == 3:  # System review
                    self._update_system_summary()
    
    def _on_complete_clicked(self):
        """Handle system completion."""
        system_data = {
            "building_assessment": asdict(self.building_assessment),
            "selected_panel": self.selected_panel,
            "selected_devices": self.selected_devices,
            "total_devices": sum(self.selected_devices.values()),
            "estimated_cost": self._calculate_estimated_cost()
        }
        
        self.system_completed.emit(system_data)
        self.status_label.setText("🎉 System design completed successfully!")
    
    def _validate_current_step(self):
        """Validate current step before proceeding."""
        if self.current_step == 0:  # Building assessment
            valid = (
                self.building_assessment.building_type and
                self.building_assessment.building_type != "-- Select Building Type --" and
                self.occupancy_combo.currentText() != "-- Select Occupancy Level --"
            )
            if not valid:
                self.status_label.setText("❌ Please complete building assessment")
                return False
                
        elif self.current_step == 1:  # Panel selection
            if not self.selected_panel:
                self.status_label.setText("❌ Please select a control panel")
                return False
                
        elif self.current_step == 2:  # Device planning
            if sum(self.selected_devices.values()) == 0:
                self.status_label.setText("❌ Please select at least one device")
                return False
        
        return True
    
    def _update_navigation(self):
        """Update navigation button states."""
        self.back_btn.setEnabled(self.current_step > 0)
        
        if self.current_step == self.total_steps - 1:
            self.next_btn.setVisible(False)
            self.complete_btn.setVisible(True)
        else:
            self.next_btn.setVisible(True)
            self.complete_btn.setVisible(False)
        
        self.progress_bar.setValue(self.current_step + 1)
        self.step_changed.emit(f"step_{self.current_step + 1}")
    
    def _on_tab_changed(self, index):
        """Handle tab change."""
        self.current_step = index
        self._update_navigation()
    
    def _update_system_summary(self):
        """Update the system review summary."""
        summary = f"""
        <h3>🔥 Fire Alarm System Summary</h3>
        
        <h4>Building Information:</h4>
        <ul>
        <li>Type: {self.building_assessment.building_type}</li>
        <li>Size: {self.building_assessment.size_sqft:,} sq ft</li>
        <li>Floors: {self.floors_spinbox.value()}</li>
        <li>Occupancy: {self.occupancy_combo.currentText()}</li>
        </ul>
        
        <h4>Selected Panel:</h4>
        <p>{self.selected_panel or 'None selected'}</p>
        
        <h4>Device Count:</h4>
        <ul>
        <li>Smoke Detectors: {self.selected_devices.get('smoke_detectors', 0)}</li>
        <li>Pull Stations: {self.selected_devices.get('pull_stations', 0)}</li>
        <li>Horn/Strobes: {self.selected_devices.get('horn_strobes', 0)}</li>
        </ul>
        
        <h4>Total Devices: {sum(self.selected_devices.values())}</h4>
        
        <h4>Estimated Cost: ${self._calculate_estimated_cost():,}</h4>
        """
        
        self.system_summary.setHtml(summary)
    
    def _calculate_estimated_cost(self):
        """Calculate estimated system cost."""
        base_cost = 5000  # Base panel cost
        device_cost = sum(self.selected_devices.values()) * 150  # $150 per device
        installation_cost = sum(self.selected_devices.values()) * 100  # $100 installation per device
        
        return base_cost + device_cost + installation_cost


def create_demo_application():
    """Create demo application with the improved builder."""
    from PySide6.QtWidgets import QApplication, QMainWindow
    import sys
    
    class DemoWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("🔥 FlameCAD Professional System Builder - IMPROVED")
            self.setGeometry(100, 100, 1200, 800)  # Larger window
            
            # Create the improved builder
            self.builder = ImprovedGuidedSystemBuilder()
            self.setCentralWidget(self.builder)
            
            # Connect signals
            self.builder.system_completed.connect(self.on_system_completed)
            self.builder.step_changed.connect(self.on_step_changed)
        
        def on_system_completed(self, system_data):
            print("🎉 System completed!")
            print(f"Panel: {system_data['selected_panel']}")
            print(f"Devices: {system_data['total_devices']}")
            print(f"Cost: ${system_data['estimated_cost']:,}")
        
        def on_step_changed(self, step):
            print(f"📋 Step changed: {step}")
    
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    
    print("🚀 IMPROVED Guided System Builder Demo")
    print("=" * 45)
    print("✅ FIXES IMPLEMENTED:")
    print("   • Navigation buttons stay visible (fixed scrolling)")
    print("   • Device selection works properly")
    print("   • Panel selection works with clear feedback")
    print("   • No automatic selections unless toggled ON")
    print("   • Improved menu behaviors and validation")
    print("   • Better user experience throughout")
    
    return app.exec()


if __name__ == "__main__":
    create_demo_application()