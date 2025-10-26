"""
DEBUGGED Guided System Builder
=============================

This version provides CRYSTAL CLEAR feedback about what's preventing you 
from proceeding past each step. No more guessing!
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
    QScrollArea,
    QFrame,
    QSizePolicy,
    QSpacerItem,
    QApplication,
    QMainWindow,
    QMessageBox,
    QButtonGroup,
    QRadioButton,
)

try:
    from frontend.design_system import AutoFireColor, AutoFireStyleSheet, AutoFireFont
    DESIGN_SYSTEM_AVAILABLE = True
except ImportError:
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


class ClearGuidedSystemBuilder(QWidget):
    """
    Crystal Clear Guided System Builder
    
    This version provides EXPLICIT feedback about what's blocking progress.
    """
    
    system_completed = Signal(dict)
    step_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Data storage
        self.building_assessment = BuildingAssessment()
        self.selected_devices = {}
        self.selected_panel = None
        self.auto_select_enabled = False
        
        # Current step tracking
        self.current_step = 0
        self.total_steps = 4
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Setup UI with VERY CLEAR feedback."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # CLEAR STATUS SECTION
        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: #f0f0f0; border: 2px solid #ccc; border-radius: 8px; padding: 10px;")
        status_layout = QVBoxLayout(status_frame)
        
        self.main_status = QLabel("🔥 Welcome to AutoFire System Builder")
        self.main_status.setStyleSheet("font-size: 16px; font-weight: bold; color: #C41E3A;")
        self.main_status.setAlignment(Qt.AlignCenter)
        
        self.step_status = QLabel("Step 1: Complete building assessment")
        self.step_status.setStyleSheet("font-size: 14px; color: #333;")
        self.step_status.setAlignment(Qt.AlignCenter)
        
        self.validation_status = QLabel("❌ Building type and occupancy required")
        self.validation_status.setStyleSheet("font-size: 12px; font-weight: bold; color: red;")
        self.validation_status.setAlignment(Qt.AlignCenter)
        
        status_layout.addWidget(self.main_status)
        status_layout.addWidget(self.step_status)
        status_layout.addWidget(self.validation_status)
        
        main_layout.addWidget(status_frame)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.total_steps)
        self.progress_bar.setValue(1)
        self.progress_bar.setFormat("Step %v of %m")
        main_layout.addWidget(self.progress_bar)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumHeight(400)
        
        self._setup_all_tabs()
        main_layout.addWidget(self.tab_widget)
        
        # Navigation
        nav_frame = QFrame()
        nav_frame.setFixedHeight(60)
        nav_layout = QHBoxLayout(nav_frame)
        
        self.back_btn = QPushButton("⬅️ Back")
        self.back_btn.setFixedSize(80, 40)
        self.back_btn.setEnabled(False)
        
        self.requirements_label = QLabel("Complete step to continue")
        self.requirements_label.setAlignment(Qt.AlignCenter)
        self.requirements_label.setStyleSheet("color: #666; font-style: italic;")
        
        self.next_btn = QPushButton("Next ➡️")
        self.next_btn.setFixedSize(80, 40)
        
        self.complete_btn = QPushButton("Complete")
        self.complete_btn.setFixedSize(80, 40)
        self.complete_btn.setVisible(False)
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.requirements_label)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.complete_btn)
        
        main_layout.addWidget(nav_frame)
        
        # Apply styling
        self.setStyleSheet("""
            QPushButton {
                background-color: #C41E3A;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8B0000;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
    
    def _setup_all_tabs(self):
        """Setup all workflow tabs."""
        self._setup_building_assessment_tab()
        self._setup_panel_selection_tab()
        self._setup_device_planning_tab()
        self._setup_system_review_tab()
    
    def _setup_building_assessment_tab(self):
        """Setup Step 1: Building Assessment."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Very clear instructions
        instructions = QLabel("""
        <h3>🏢 Step 1: Building Assessment</h3>
        <p><b>What you need to do:</b></p>
        <ol>
        <li>Select your building type from the dropdown</li>
        <li>Enter the building size in square feet</li>
        <li>Choose the occupancy level</li>
        </ol>
        <p><b style="color: red;">All three fields are required to proceed!</b></p>
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Building type
        type_group = QGroupBox("1. Building Type (REQUIRED)")
        type_layout = QFormLayout(type_group)
        
        self.building_type_combo = QComboBox()
        building_types = [
            "-- Please Select Building Type --",
            "Office Building",
            "Retail Store",
            "Warehouse", 
            "School",
            "Hospital",
            "Hotel",
            "Restaurant"
        ]
        self.building_type_combo.addItems(building_types)
        self.building_type_combo.currentTextChanged.connect(self._on_building_type_changed)
        
        type_layout.addRow("Building Type:", self.building_type_combo)
        layout.addWidget(type_group)
        
        # Building size
        size_group = QGroupBox("2. Building Size (REQUIRED)")
        size_layout = QFormLayout(size_group)
        
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(100, 1000000)
        self.size_spinbox.setValue(5000)
        self.size_spinbox.setSuffix(" sq ft")
        self.size_spinbox.valueChanged.connect(self._on_size_changed)
        
        size_layout.addRow("Building Size:", self.size_spinbox)
        layout.addWidget(size_group)
        
        # Occupancy level
        occupancy_group = QGroupBox("3. Occupancy Level (REQUIRED)")
        occupancy_layout = QFormLayout(occupancy_group)
        
        self.occupancy_combo = QComboBox()
        occupancy_levels = [
            "-- Please Select Occupancy Level --",
            "Light (< 50 people)",
            "Moderate (50-300 people)",
            "Heavy (300-1000 people)",
            "Very Heavy (> 1000 people)"
        ]
        self.occupancy_combo.addItems(occupancy_levels)
        self.occupancy_combo.currentTextChanged.connect(self._validate_step_1)
        
        occupancy_layout.addRow("Occupancy Level:", self.occupancy_combo)
        layout.addWidget(occupancy_group)
        
        # Clear validation feedback
        self.step1_validation = QLabel("❌ Please complete all required fields above")
        self.step1_validation.setStyleSheet("color: red; font-weight: bold; font-size: 14px; padding: 10px;")
        self.step1_validation.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.step1_validation)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "1. Building Assessment")
    
    def _setup_panel_selection_tab(self):
        """Setup Step 2: Panel Selection."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Clear instructions
        instructions = QLabel("""
        <h3>🔧 Step 2: Panel Selection</h3>
        <p><b>What you need to do:</b></p>
        <ol>
        <li>Review the recommended panels based on your building</li>
        <li>Click on ONE panel to select it (it will highlight)</li>
        <li>Your selection will show below the panels</li>
        </ol>
        <p><b style="color: red;">You must select exactly ONE panel to proceed!</b></p>
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Panel selection area
        self.panel_group = QGroupBox("Available Control Panels")
        self.panel_layout = QVBoxLayout(self.panel_group)
        
        # Initially show placeholder
        placeholder = QLabel("⏳ Complete Step 1 first to see panel options")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
        self.panel_layout.addWidget(placeholder)
        
        layout.addWidget(self.panel_group)
        
        # Selection feedback
        self.panel_selection_feedback = QLabel("❌ No panel selected")
        self.panel_selection_feedback.setStyleSheet("color: red; font-weight: bold; font-size: 14px; padding: 10px;")
        self.panel_selection_feedback.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.panel_selection_feedback)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "2. Panel Selection")
    
    def _setup_device_planning_tab(self):
        """Setup Step 3: Device Planning."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Clear instructions
        instructions = QLabel("""
        <h3>🔍 Step 3: Device Planning</h3>
        <p><b>What you need to do:</b></p>
        <ol>
        <li>Set the number of smoke detectors (minimum 1)</li>
        <li>Set the number of pull stations (minimum 1)</li>
        <li>Set the number of horn/strobes (minimum 1)</li>
        </ol>
        <p><b style="color: red;">You must have at least 3 total devices!</b></p>
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Device groups
        devices_group = QGroupBox("Device Selection")
        devices_layout = QFormLayout(devices_group)
        
        # Smoke detectors
        self.smoke_spin = QSpinBox()
        self.smoke_spin.setRange(0, 500)
        self.smoke_spin.setValue(0)
        self.smoke_spin.valueChanged.connect(self._on_device_changed)
        
        # Pull stations
        self.pull_spin = QSpinBox()
        self.pull_spin.setRange(0, 100)
        self.pull_spin.setValue(0)
        self.pull_spin.valueChanged.connect(self._on_device_changed)
        
        # Horn/strobes
        self.horn_spin = QSpinBox()
        self.horn_spin.setRange(0, 200)
        self.horn_spin.setValue(0)
        self.horn_spin.valueChanged.connect(self._on_device_changed)
        
        devices_layout.addRow("Smoke Detectors:", self.smoke_spin)
        devices_layout.addRow("Pull Stations:", self.pull_spin)
        devices_layout.addRow("Horn/Strobes:", self.horn_spin)
        
        layout.addWidget(devices_group)
        
        # Device summary
        self.device_summary = QLabel("Total Devices: 0 (Need at least 3)")
        self.device_summary.setStyleSheet("color: red; font-weight: bold; font-size: 14px; padding: 10px;")
        self.device_summary.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.device_summary)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "3. Device Planning")
    
    def _setup_system_review_tab(self):
        """Setup Step 4: System Review."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        instructions = QLabel("""
        <h3>📋 Step 4: System Review</h3>
        <p>Review your complete system and click Complete to finish!</p>
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        self.system_summary = QTextEdit()
        self.system_summary.setReadOnly(True)
        self.system_summary.setMaximumHeight(300)
        layout.addWidget(self.system_summary)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "4. System Review")
    
    def _connect_signals(self):
        """Connect signals."""
        self.back_btn.clicked.connect(self._on_back_clicked)
        self.next_btn.clicked.connect(self._on_next_clicked)
        self.complete_btn.clicked.connect(self._on_complete_clicked)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def _on_building_type_changed(self, building_type):
        """Handle building type change."""
        self.building_assessment.building_type = building_type
        self._validate_step_1()
        
        # Update panel options when assessment is complete
        if self._is_step_1_complete():
            self._populate_panel_options()
    
    def _on_size_changed(self, size):
        """Handle size change."""
        self.building_assessment.size_sqft = size
        self._validate_step_1()
        
        # Update panel options when assessment is complete
        if self._is_step_1_complete():
            self._populate_panel_options()
    
    def _validate_step_1(self):
        """Validate step 1 with CLEAR feedback."""
        issues = []
        
        if (not self.building_assessment.building_type or 
            self.building_assessment.building_type == "-- Please Select Building Type --"):
            issues.append("Building type")
        
        if (not self.occupancy_combo.currentText() or 
            self.occupancy_combo.currentText() == "-- Please Select Occupancy Level --"):
            issues.append("Occupancy level")
        
        if self.building_assessment.size_sqft < 100:
            issues.append("Building size")
        
        if issues:
            missing = ", ".join(issues)
            self.step1_validation.setText(f"❌ Still missing: {missing}")
            self.step1_validation.setStyleSheet("color: red; font-weight: bold; font-size: 14px; padding: 10px;")
            self.validation_status.setText(f"❌ Step 1: Missing {missing}")
        else:
            self.step1_validation.setText("✅ Step 1 complete! Ready to proceed to panel selection.")
            self.step1_validation.setStyleSheet("color: green; font-weight: bold; font-size: 14px; padding: 10px;")
            self.validation_status.setText("✅ Step 1: Complete")
    
    def _is_step_1_complete(self):
        """Check if step 1 is complete."""
        return (
            self.building_assessment.building_type and
            self.building_assessment.building_type != "-- Please Select Building Type --" and
            self.occupancy_combo.currentText() != "-- Please Select Occupancy Level --" and
            self.building_assessment.size_sqft >= 100
        )
    
    def _populate_panel_options(self):
        """Populate panel options based on building size."""
        # Clear existing options
        while self.panel_layout.count():
            child = self.panel_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Create radio button group for exclusive selection
        self.panel_button_group = QButtonGroup()
        self.panel_buttons = []
        
        # Determine panels based on size
        size = self.building_assessment.size_sqft
        
        if size < 10000:
            panels = [
                ("Small Conventional Panel", "4-zone conventional system", "$800"),
                ("Small Addressable Panel", "32-device addressable system", "$1,500")
            ]
        elif size < 50000:
            panels = [
                ("Medium Conventional Panel", "8-zone conventional system", "$1,200"),
                ("Medium Addressable Panel", "159-device addressable system", "$2,800"),
                ("Network Panel", "318-device networked system", "$4,500")
            ]
        else:
            panels = [
                ("Large Conventional Panel", "16-zone conventional system", "$2,000"),
                ("Large Addressable Panel", "636-device addressable system", "$6,500"),
                ("Enterprise Panel", "1272-device enterprise system", "$12,000")
            ]
        
        # Create radio buttons for each panel
        for i, (name, specs, cost) in enumerate(panels):
            panel_frame = QFrame()
            panel_frame.setStyleSheet("""
                QFrame {
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    padding: 10px;
                    margin: 5px;
                }
                QFrame:hover {
                    border-color: #C41E3A;
                }
            """)
            
            panel_layout = QHBoxLayout(panel_frame)
            
            radio_btn = QRadioButton()
            radio_btn.toggled.connect(lambda checked, n=name: self._on_panel_selected(n, checked))
            
            panel_info = QLabel(f"""
            <b>{name}</b><br>
            {specs}<br>
            <span style="color: green; font-weight: bold;">{cost}</span>
            """)
            
            panel_layout.addWidget(radio_btn)
            panel_layout.addWidget(panel_info)
            panel_layout.addStretch()
            
            self.panel_layout.addWidget(panel_frame)
            self.panel_button_group.addButton(radio_btn, i)
            self.panel_buttons.append((radio_btn, name))
        
        # Update instructions
        instruction_label = QLabel("👆 Click the circle next to a panel to select it")
        instruction_label.setStyleSheet("color: #666; font-style: italic; text-align: center;")
        self.panel_layout.addWidget(instruction_label)
    
    def _on_panel_selected(self, panel_name, checked):
        """Handle panel selection with clear feedback."""
        if checked:
            self.selected_panel = panel_name
            self.panel_selection_feedback.setText(f"✅ Selected: {panel_name}")
            self.panel_selection_feedback.setStyleSheet("color: green; font-weight: bold; font-size: 14px; padding: 10px;")
            self.validation_status.setText("✅ Step 2: Panel selected")
        else:
            # This shouldn't happen with radio buttons, but just in case
            if self.selected_panel == panel_name:
                self.selected_panel = None
                self.panel_selection_feedback.setText("❌ No panel selected")
                self.panel_selection_feedback.setStyleSheet("color: red; font-weight: bold; font-size: 14px; padding: 10px;")
                self.validation_status.setText("❌ Step 2: Select a panel")
    
    def _on_device_changed(self):
        """Handle device count changes."""
        smoke = self.smoke_spin.value()
        pull = self.pull_spin.value()
        horn = self.horn_spin.value()
        total = smoke + pull + horn
        
        self.selected_devices = {
            "smoke_detectors": smoke,
            "pull_stations": pull,
            "horn_strobes": horn
        }
        
        if total >= 3:
            self.device_summary.setText(f"✅ Total Devices: {total} (Good to go!)")
            self.device_summary.setStyleSheet("color: green; font-weight: bold; font-size: 14px; padding: 10px;")
            self.validation_status.setText("✅ Step 3: Devices selected")
        else:
            self.device_summary.setText(f"❌ Total Devices: {total} (Need at least 3)")
            self.device_summary.setStyleSheet("color: red; font-weight: bold; font-size: 14px; padding: 10px;")
            self.validation_status.setText(f"❌ Step 3: Need {3-total} more devices")
    
    def _on_back_clicked(self):
        """Handle back button."""
        if self.current_step > 0:
            self.current_step -= 1
            self.tab_widget.setCurrentIndex(self.current_step)
            self._update_navigation()
    
    def _on_next_clicked(self):
        """Handle next button with CLEAR validation."""
        can_proceed, message = self._can_proceed_from_current_step()
        
        if can_proceed:
            if self.current_step < self.total_steps - 1:
                self.current_step += 1
                self.tab_widget.setCurrentIndex(self.current_step)
                self._update_navigation()
                
                if self.current_step == 3:  # System review
                    self._update_system_summary()
        else:
            # Show clear error message
            QMessageBox.warning(self, "Cannot Proceed", message)
            self.validation_status.setText(f"❌ {message}")
    
    def _can_proceed_from_current_step(self):
        """Check if we can proceed from current step with detailed feedback."""
        if self.current_step == 0:  # Building assessment
            if not self._is_step_1_complete():
                issues = []
                if (not self.building_assessment.building_type or 
                    self.building_assessment.building_type == "-- Please Select Building Type --"):
                    issues.append("building type")
                if (not self.occupancy_combo.currentText() or 
                    self.occupancy_combo.currentText() == "-- Please Select Occupancy Level --"):
                    issues.append("occupancy level")
                
                missing = " and ".join(issues)
                return False, f"Please select {missing} in Step 1"
            
        elif self.current_step == 1:  # Panel selection
            if not self.selected_panel:
                return False, "Please select a control panel in Step 2"
                
        elif self.current_step == 2:  # Device planning
            total_devices = sum(self.selected_devices.values())
            if total_devices < 3:
                need = 3 - total_devices
                return False, f"Please add {need} more device(s) in Step 3"
        
        return True, "OK"
    
    def _on_complete_clicked(self):
        """Handle system completion."""
        system_data = {
            "building_assessment": asdict(self.building_assessment),
            "selected_panel": self.selected_panel,
            "selected_devices": self.selected_devices,
            "total_devices": sum(self.selected_devices.values()),
        }
        
        self.system_completed.emit(system_data)
        QMessageBox.information(self, "Success!", "🎉 Fire alarm system design completed!")
    
    def _update_navigation(self):
        """Update navigation states."""
        self.back_btn.setEnabled(self.current_step > 0)
        
        # Update step status
        step_names = ["Building Assessment", "Panel Selection", "Device Planning", "System Review"]
        self.step_status.setText(f"Step {self.current_step + 1}: {step_names[self.current_step]}")
        
        # Update requirements
        can_proceed, message = self._can_proceed_from_current_step()
        if can_proceed:
            if self.current_step == self.total_steps - 1:
                self.requirements_label.setText("Ready to complete!")
                self.next_btn.setVisible(False)
                self.complete_btn.setVisible(True)
            else:
                self.requirements_label.setText("✅ Ready for next step")
                self.next_btn.setVisible(True)
                self.complete_btn.setVisible(False)
        else:
            self.requirements_label.setText(f"❌ {message}")
            self.next_btn.setVisible(True)
            self.complete_btn.setVisible(False)
        
        self.progress_bar.setValue(self.current_step + 1)
    
    def _on_tab_changed(self, index):
        """Handle tab changes."""
        self.current_step = index
        self._update_navigation()
    
    def _update_system_summary(self):
        """Update system summary."""
        occupancy = self.occupancy_combo.currentText()
        
        summary = f"""
        <h3>🔥 Fire Alarm System Summary</h3>
        
        <h4>Building Information:</h4>
        <ul>
        <li>Type: {self.building_assessment.building_type}</li>
        <li>Size: {self.building_assessment.size_sqft:,} sq ft</li>
        <li>Occupancy: {occupancy}</li>
        </ul>
        
        <h4>Selected Panel:</h4>
        <p>{self.selected_panel}</p>
        
        <h4>Device Counts:</h4>
        <ul>
        <li>Smoke Detectors: {self.selected_devices.get('smoke_detectors', 0)}</li>
        <li>Pull Stations: {self.selected_devices.get('pull_stations', 0)}</li>
        <li>Horn/Strobes: {self.selected_devices.get('horn_strobes', 0)}</li>
        </ul>
        
        <h4>Total Devices: {sum(self.selected_devices.values())}</h4>
        
        <p><b>System ready for implementation!</b></p>
        """
        
        self.system_summary.setHtml(summary)


def create_debug_demo():
    """Create the debug demo."""
    import sys
    
    class DebugWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("🔥 AutoFire - CRYSTAL CLEAR System Builder")
            self.setGeometry(100, 100, 1000, 700)
            
            self.builder = ClearGuidedSystemBuilder()
            self.setCentralWidget(self.builder)
            
            self.builder.system_completed.connect(self.on_completed)
        
        def on_completed(self, data):
            print("System completed!")
            print(f"Panel: {data['selected_panel']}")
            print(f"Total devices: {data['total_devices']}")
    
    app = QApplication(sys.argv)
    window = DebugWindow()
    window.show()
    
    print("🚀 CRYSTAL CLEAR System Builder")
    print("=" * 40)
    print("✅ CRYSTAL CLEAR feedback on every step")
    print("✅ Exact requirements shown for each step")
    print("✅ No more guessing what's blocking you!")
    print("✅ Radio buttons for clear panel selection")
    print("✅ Visual validation at every step")
    
    return app.exec()


if __name__ == "__main__":
    create_debug_demo()