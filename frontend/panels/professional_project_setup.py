"""
Professional Project Setup - Direct workflow for experienced fire alarm designers.

This replaces the guided system builder with immediate project creation.
Professionals can:
1. Load floor plans (PDF/DWG)
2. Set project parameters quickly
3. Start designing immediately
4. Access AI assistance on-demand via settings
"""

import os
import sqlite3
from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Import our professional design system
try:
    from frontend.design_system import AutoFireColor, AutoFireStyleSheet

    DESIGN_SYSTEM_AVAILABLE = True
except ImportError:
    DESIGN_SYSTEM_AVAILABLE = False

    class AutoFireColor:
        PRIMARY = "#C41E3A"
        SECONDARY = "#8B0000"
        ACCENT = "#FF6B35"

    class AutoFireStyleSheet:
        @staticmethod
        def group_box():
            return ""

        @staticmethod
        def button_primary():
            return ""

        @staticmethod
        def input_field():
            return ""


@dataclass
class ProjectConfig:
    """Professional project configuration."""

    name: str = ""
    building_type: str = ""
    floor_plan_path: str = ""
    manufacturer: str = ""
    ai_assistance_level: int = 1  # 0=Off, 1=Minimal, 2=Active, 3=Aggressive
    nfpa_compliance: bool = True


class ProfessionalProjectSetup(QWidget):
    """
    Direct project setup for professionals.

    Gets designers working immediately:
    - Load floor plans
    - Set basic parameters
    - Start designing
    - AI assistance configurable
    """

    # Signals
    project_created = Signal(dict)  # Emitted when project is ready
    floor_plan_loaded = Signal(str)  # Emitted when floor plan is loaded

    def __init__(self, parent=None):
        super().__init__(parent)

        self.config = ProjectConfig()
        self._setup_ui()

    def _setup_ui(self):
        """Setup direct professional UI."""
        layout = QVBoxLayout(self)

        # Professional header
        header = QLabel(
            """
            <h2>🔥 New Fire Alarm Project</h2>
            <p>Professional setup - load floor plan and start designing immediately</p>
        """
        )
        header.setWordWrap(True)
        header.setStyleSheet(
            """
            background-color: #1a237e;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        """
        )
        layout.addWidget(header)

        # Main setup area
        setup_group = QGroupBox("Project Setup")
        setup_layout = QFormLayout(setup_group)

        # Project name
        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("Enter project name...")
        setup_layout.addRow("Project Name:", self.project_name)

        # Floor plan import
        floor_plan_layout = QHBoxLayout()
        self.floor_plan_path = QLineEdit()
        self.floor_plan_path.setPlaceholderText("No floor plan loaded")
        self.floor_plan_path.setReadOnly(True)

        self.load_floor_plan_btn = QPushButton("📁 Load Floor Plan")
        self.load_floor_plan_btn.clicked.connect(self._load_floor_plan)

        floor_plan_layout.addWidget(self.floor_plan_path)
        floor_plan_layout.addWidget(self.load_floor_plan_btn)
        setup_layout.addRow("Floor Plan:", floor_plan_layout)

        # Building type (quick selection)
        self.building_type = QComboBox()
        self.building_type.addItems(
            [
                "Commercial Office",
                "Industrial Facility",
                "Educational Building",
                "Healthcare Facility",
                "Hotel/Lodging",
                "Retail Store",
                "Assembly Building",
                "Residential Complex",
                "Other",
            ]
        )
        setup_layout.addRow("Building Type:", self.building_type)

        # Primary manufacturer
        self.manufacturer = QComboBox()
        manufacturers = self._get_manufacturers()
        self.manufacturer.addItems(["Auto-detect"] + manufacturers)
        setup_layout.addRow("Primary Manufacturer:", self.manufacturer)

        layout.addWidget(setup_group)

        # AI assistance settings
        ai_group = QGroupBox("🤖 AI Assistance Settings")
        ai_layout = QVBoxLayout(ai_group)

        ai_label = QLabel("AI assistance level (professionals can turn this down or off):")
        ai_layout.addWidget(ai_label)

        self.ai_slider = QSlider(Qt.Horizontal)
        self.ai_slider.setRange(0, 3)
        self.ai_slider.setValue(1)  # Minimal by default for pros
        self.ai_slider.setTickPosition(QSlider.TicksBelow)
        self.ai_slider.setTickInterval(1)
        self.ai_slider.valueChanged.connect(self._update_ai_description)

        ai_layout.addWidget(self.ai_slider)

        self.ai_description = QLabel("Minimal - Basic compliance checking only")
        self.ai_description.setStyleSheet("color: #666; font-style: italic;")
        ai_layout.addWidget(self.ai_description)

        # NFPA compliance toggle
        self.nfpa_compliance = QCheckBox("Enable NFPA 72 compliance checking")
        self.nfpa_compliance.setChecked(True)
        ai_layout.addWidget(self.nfpa_compliance)

        layout.addWidget(ai_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.guided_mode_btn = QPushButton("📚 Guided Mode")
        self.guided_mode_btn.clicked.connect(self._show_guided_mode)
        self.guided_mode_btn.setStyleSheet(
            "background-color: #6c757d; color: white; padding: 8px 16px; border-radius: 4px;"
        )

        button_layout.addWidget(self.guided_mode_btn)
        button_layout.addStretch()

        self.create_project_btn = QPushButton("🚀 Create Project & Start Designing")
        self.create_project_btn.clicked.connect(self._create_project)
        self.create_project_btn.setStyleSheet(
            "background-color: #C41E3A; color: white; padding: 12px 24px; border-radius: 4px; font-weight: bold;"
        )

        button_layout.addWidget(self.create_project_btn)
        layout.addLayout(button_layout)

        layout.addStretch()

    def _load_floor_plan(self):
        """Load floor plan file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Floor Plan",
            "",
            "Floor Plans (*.pdf *.dwg *.dxf *.png *.jpg *.jpeg);;All Files (*)",
        )

        if file_path:
            self.floor_plan_path.setText(file_path)
            self.config.floor_plan_path = file_path

            # Auto-suggest project name from filename
            if not self.project_name.text():
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                self.project_name.setText(f"Fire Alarm - {base_name}")

            self.floor_plan_loaded.emit(file_path)

    def _update_ai_description(self, value):
        """Update AI assistance description."""
        descriptions = {
            0: "Off - No AI assistance, pure manual design",
            1: "Minimal - Basic compliance checking only",
            2: "Active - Device suggestions and code validation",
            3: "Aggressive - Full AI recommendations and auto-placement",
        }
        self.ai_description.setText(descriptions.get(value, "Unknown"))

    def _get_manufacturers(self):
        """Get manufacturers from database."""
        try:
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "autofire.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT DISTINCT m.name
                FROM manufacturers m
                INNER JOIN devices d ON d.manufacturer_id = m.id
                WHERE m.name IS NOT NULL AND m.name != ''
                ORDER BY m.name
            """
            )

            manufacturers = [row[0] for row in cursor.fetchall()]
            conn.close()
            return manufacturers[:15]  # Top 15
        except Exception as e:
            print(f"Error loading manufacturers: {e}")
            return ["Notifier", "Honeywell", "Simplex", "Edwards", "System Sensor"]

    def _show_guided_mode(self):
        """Show guided mode for educational purposes."""
        # This would switch to the guided system builder
        print("Switching to guided mode for educational workflow")

    def _create_project(self):
        """Create project and start designing immediately."""
        # Collect configuration
        self.config.name = self.project_name.text() or "Untitled Project"
        self.config.building_type = self.building_type.currentText()
        self.config.manufacturer = self.manufacturer.currentText()
        self.config.ai_assistance_level = self.ai_slider.value()
        self.config.nfpa_compliance = self.nfpa_compliance.isChecked()

        # Emit project data
        project_data = {
            "name": self.config.name,
            "building_type": self.config.building_type,
            "floor_plan_path": self.config.floor_plan_path,
            "manufacturer": self.config.manufacturer,
            "ai_assistance_level": self.config.ai_assistance_level,
            "nfpa_compliance": self.config.nfpa_compliance,
            "setup_mode": "professional_direct",
        }

        self.project_created.emit(project_data)
        print(f"🚀 Project '{self.config.name}' created - ready for design work!")


# Alias for backward compatibility
class SystemBuilderWidget(ProfessionalProjectSetup):
    """Professional project setup (replaces guided system builder)."""

    pass
