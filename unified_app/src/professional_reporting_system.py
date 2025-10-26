"""
AutoFire Professional Reporting System

The bread and butter of fire alarm design - professional documentation that clients,
AHJs, and installers need. This system provides:

1. Auto-generated standard reports (device schedules, compliance, calculations)
2. Customizable report templates with save/favorites
3. Export to multiple formats (PDF, Excel, CAD blocks)
4. Professional formatting for model space and paperspace insertion
5. Frequently used report configurations

Core Reports:
- Device Schedule (with addresses, locations, specifications)
- Circuit Analysis (voltage drop, load calculations, wire schedules)
- Compliance Summary (NFPA 72 requirements, code analysis)
- Installation Guide (device placement, routing instructions)
- As-Built Documentation (final system configuration)
"""

import sys
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtPrintSupport import QPrinter, QPrintDialog

    PYSIDE6_AVAILABLE = True
except ImportError:
    print("PySide6 not available - cannot run reporting demo")
    sys.exit(1)

from frontend.design_system import AutoFireColor, AutoFireTypography, AutoFireSpacing

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Standard fire alarm report types."""

    DEVICE_SCHEDULE = "device_schedule"
    CIRCUIT_ANALYSIS = "circuit_analysis"
    COMPLIANCE_SUMMARY = "compliance_summary"
    INSTALLATION_GUIDE = "installation_guide"
    AS_BUILT_DOCS = "as_built_docs"
    CUTSHEET_PACKAGE = "cutsheet_package"
    CALCULATION_SUMMARY = "calculation_summary"


class ExportFormat(Enum):
    """Available export formats."""

    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    CAD_BLOCK = "cad_block"
    HTML = "html"
    PRINT = "print"


@dataclass
class ReportTemplate:
    """Report template configuration."""

    name: str
    report_type: ReportType
    description: str
    columns: List[str]
    filters: Dict[str, Any] = field(default_factory=dict)
    formatting: Dict[str, Any] = field(default_factory=dict)
    is_favorite: bool = False
    last_used: Optional[str] = None
    custom_fields: List[str] = field(default_factory=list)


@dataclass
class DeviceRecord:
    """Device record for reports."""

    address: str
    device_type: str
    model: str
    location: str
    circuit: str
    zone: str
    voltage: str
    current: str
    notes: str = ""


@dataclass
class CircuitRecord:
    """Circuit record for analysis reports."""

    circuit_id: str
    circuit_type: str
    wire_gauge: str
    length_ft: float
    device_count: int
    load_amps: float
    voltage_drop: float
    compliance_status: str


class ProfessionalReportingSystem(QMainWindow):
    """
    Professional reporting system for fire alarm documentation.

    Focus: Getting reports right - the bread and butter of the business.
    """

    def __init__(self):
        super().__init__()
        self.report_templates = self.load_default_templates()
        self.favorite_templates = []
        self.current_data = self.load_sample_data()
        self.setup_ui()

    def load_default_templates(self) -> List[ReportTemplate]:
        """Load standard fire alarm report templates."""
        templates = [
            ReportTemplate(
                name="Standard Device Schedule",
                report_type=ReportType.DEVICE_SCHEDULE,
                description="Complete device listing with addresses and specifications",
                columns=["Address", "Device Type", "Model", "Location", "Circuit", "Zone"],
                formatting={"page_orientation": "landscape", "font_size": 10, "include_logo": True},
            ),
            ReportTemplate(
                name="Detailed Device Schedule",
                report_type=ReportType.DEVICE_SCHEDULE,
                description="Extended device schedule with electrical specifications",
                columns=[
                    "Address",
                    "Device Type",
                    "Model",
                    "Location",
                    "Circuit",
                    "Zone",
                    "Voltage",
                    "Current",
                    "Notes",
                ],
                formatting={"page_orientation": "landscape", "font_size": 9, "include_logo": True},
            ),
            ReportTemplate(
                name="Circuit Analysis Report",
                report_type=ReportType.CIRCUIT_ANALYSIS,
                description="Voltage drop calculations and circuit loading analysis",
                columns=[
                    "Circuit ID",
                    "Type",
                    "Wire Gauge",
                    "Length (ft)",
                    "Devices",
                    "Load (A)",
                    "V-Drop (%)",
                    "Status",
                ],
                formatting={"page_orientation": "portrait", "include_calculations": True},
            ),
            ReportTemplate(
                name="NFPA 72 Compliance Summary",
                report_type=ReportType.COMPLIANCE_SUMMARY,
                description="Code compliance verification and exception documentation",
                columns=["Requirement", "Status", "Value", "Code Reference", "Notes"],
                formatting={"include_code_references": True, "highlight_violations": True},
            ),
            ReportTemplate(
                name="Installation Guide",
                report_type=ReportType.INSTALLATION_GUIDE,
                description="Device placement and wiring instructions for installers",
                columns=[
                    "Device",
                    "Location",
                    "Height",
                    "Mounting",
                    "Wire Routing",
                    "Special Instructions",
                ],
                formatting={"include_diagrams": True, "large_text": True},
            ),
            ReportTemplate(
                name="Cutsheet Package",
                report_type=ReportType.CUTSHEET_PACKAGE,
                description="Device specification sheets and technical data",
                columns=["Device Type", "Model", "Manufacturer", "Specifications", "Cutsheet"],
                formatting={"include_cutsheets": True, "group_by_manufacturer": True},
            ),
        ]

        # Mark some as favorites for demo
        templates[0].is_favorite = True
        templates[2].is_favorite = True

        return templates

    def load_sample_data(self) -> Dict[str, List]:
        """Load sample project data for reports."""
        devices = [
            DeviceRecord(
                "01-001",
                "Smoke Detector",
                "SIGA-PS",
                "Conference Room A",
                "SLC-1",
                "Zone 1",
                "24V",
                "220µA",
                "Ceiling mount",
            ),
            DeviceRecord(
                "01-002",
                "Smoke Detector",
                "SIGA-PS",
                "Conference Room B",
                "SLC-1",
                "Zone 1",
                "24V",
                "220µA",
                "Ceiling mount",
            ),
            DeviceRecord(
                "01-003",
                "Horn/Strobe",
                "MASS-24-15/75",
                "Corridor - North",
                "NAC-1",
                "Zone 1",
                "24V",
                "0.095A",
                'Wall mount 80" AFF',
            ),
            DeviceRecord(
                "01-004",
                "Horn/Strobe",
                "MASS-24-15/75",
                "Corridor - South",
                "NAC-1",
                "Zone 1",
                "24V",
                "0.095A",
                'Wall mount 80" AFF',
            ),
            DeviceRecord(
                "01-005",
                "Pull Station",
                "M5A-R",
                "Main Exit",
                "SLC-1",
                "Zone 1",
                "24V",
                "50µA",
                '48" AFF per ADA',
            ),
            DeviceRecord(
                "01-006",
                "Monitor Module",
                "SIGA-MIM",
                "Sprinkler Flow Switch",
                "SLC-1",
                "Zone 2",
                "24V",
                "50µA",
                "Electrical room",
            ),
            DeviceRecord(
                "01-007",
                "Control Module",
                "SIGA-CRM",
                "Fire Pump Start",
                "SLC-1",
                "Zone 2",
                "24V",
                "50µA",
                "Fire pump room",
            ),
            DeviceRecord(
                "02-001",
                "Smoke Detector",
                "SIGA-PS",
                "Office Area - East",
                "SLC-2",
                "Zone 2",
                "24V",
                "220µA",
                "Ceiling mount",
            ),
            DeviceRecord(
                "02-002",
                "Smoke Detector",
                "SIGA-PS",
                "Office Area - West",
                "SLC-2",
                "Zone 2",
                "24V",
                "220µA",
                "Ceiling mount",
            ),
            DeviceRecord(
                "02-003",
                "Speaker/Strobe",
                "MASS-24VSR-15/75",
                "Reception Area",
                "NAC-2",
                "Zone 2",
                "24V",
                "0.125A",
                'Wall mount 80" AFF',
            ),
        ]

        circuits = [
            CircuitRecord("SLC-1", "Signaling Line", "14 AWG", 285.0, 5, 0.78, 7.2, "✓ Compliant"),
            CircuitRecord("SLC-2", "Signaling Line", "14 AWG", 195.0, 3, 0.49, 4.8, "✓ Compliant"),
            CircuitRecord("NAC-1", "Notification", "12 AWG", 150.0, 2, 0.19, 1.2, "✓ Compliant"),
            CircuitRecord("NAC-2", "Notification", "12 AWG", 95.0, 1, 0.125, 0.8, "✓ Compliant"),
        ]

        return {
            "devices": devices,
            "circuits": circuits,
            "project_info": {
                "name": "Downtown Office Complex - Floor 3",
                "address": "123 Main Street, Downtown",
                "engineer": "AutoFire Professional User",
                "date": datetime.now().strftime("%B %d, %Y"),
                "panel": "FACP-100 Addressable Fire Alarm Control Panel",
            },
        }

    def setup_ui(self):
        """Setup the professional reporting interface."""
        self.setWindowTitle("AutoFire Professional - Reporting System")
        self.resize(1400, 900)

        central = QWidget()
        self.setCentralWidget(central)

        # Main layout: Template selection + Report preview + Export options
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # LEFT: Template selection and customization
        left_panel = self.create_template_panel()
        left_panel.setMinimumWidth(350)
        left_panel.setMaximumWidth(450)

        # CENTER: Report preview
        center_panel = self.create_preview_panel()

        # RIGHT: Export options and actions
        right_panel = self.create_export_panel()
        right_panel.setMinimumWidth(300)
        right_panel.setMaximumWidth(400)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(center_panel)
        main_layout.addWidget(right_panel)

        central.setLayout(main_layout)
        self.apply_professional_styling()

        # Load first template by default
        self.load_template(self.report_templates[0])

    def create_template_panel(self) -> QWidget:
        """LEFT: Report template selection and customization."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = QLabel("Report Templates")
        header.setStyleSheet(
            f"""
            QLabel {{
                color: {AutoFireColor.TEXT_PRIMARY.value};
                font-size: 18px;
                font-weight: bold;
                padding: 8px 0px;
            }}
        """
        )
        layout.addWidget(header)

        # Favorites section
        favorites_group = QGroupBox("⭐ Frequently Used")
        favorites_layout = QVBoxLayout()

        self.favorites_list = QListWidget()
        self.favorites_list.setMaximumHeight(120)
        self.update_favorites_list()
        self.favorites_list.itemClicked.connect(self.on_favorite_selected)

        favorites_layout.addWidget(self.favorites_list)
        favorites_group.setLayout(favorites_layout)
        layout.addWidget(favorites_group)

        # All templates section
        templates_group = QGroupBox("All Report Templates")
        templates_layout = QVBoxLayout()

        self.templates_list = QTreeWidget()
        self.templates_list.setHeaderHidden(True)
        self.update_templates_list()
        self.templates_list.itemClicked.connect(self.on_template_selected)

        templates_layout.addWidget(self.templates_list)
        templates_group.setLayout(templates_layout)
        layout.addWidget(templates_group)

        # Template customization
        custom_group = QGroupBox("Template Customization")
        custom_layout = QVBoxLayout()

        # Template name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.template_name_edit = QLineEdit()
        name_layout.addWidget(self.template_name_edit)
        custom_layout.addLayout(name_layout)

        # Column selection
        columns_label = QLabel("Columns to Include:")
        custom_layout.addWidget(columns_label)

        self.columns_list = QListWidget()
        self.columns_list.setMaximumHeight(150)
        self.columns_list.setSelectionMode(QAbstractItemView.MultiSelection)
        custom_layout.addWidget(self.columns_list)

        # Action buttons
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("💾 Save Template")
        save_btn.clicked.connect(self.save_current_template)

        favorite_btn = QPushButton("⭐ Add to Favorites")
        favorite_btn.clicked.connect(self.add_to_favorites)

        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(favorite_btn)

        custom_layout.addLayout(buttons_layout)
        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)

        layout.addStretch()

        widget.setLayout(layout)
        widget.setStyleSheet(
            f"""
            QWidget {{
                background-color: {AutoFireColor.SURFACE_PRIMARY.value};
                border-right: 1px solid {AutoFireColor.BORDER_PRIMARY.value};
            }}
        """
        )

        return widget

    def create_preview_panel(self) -> QWidget:
        """CENTER: Live report preview."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Preview header
        preview_header = QHBoxLayout()

        title = QLabel("Report Preview")
        title.setStyleSheet(
            f"""
            QLabel {{
                color: {AutoFireColor.TEXT_PRIMARY.value};
                font-size: 18px;
                font-weight: bold;
            }}
        """
        )

        self.template_info = QLabel("Standard Device Schedule")
        self.template_info.setStyleSheet(
            f"""
            QLabel {{
                color: {AutoFireColor.TEXT_SECONDARY.value};
                font-size: 12px;
                font-style: italic;
            }}
        """
        )

        preview_header.addWidget(title)
        preview_header.addStretch()
        preview_header.addWidget(self.template_info)

        layout.addLayout(preview_header)

        # Project info header (as it would appear in report)
        project_header = self.create_report_header()
        layout.addWidget(project_header)

        # Report table
        self.report_table = QTableWidget()
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setSortingEnabled(True)
        self.report_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(self.report_table)

        # Report footer/summary
        self.report_footer = QTextEdit()
        self.report_footer.setMaximumHeight(80)
        self.report_footer.setReadOnly(True)
        layout.addWidget(self.report_footer)

        widget.setLayout(layout)
        return widget

    def create_export_panel(self) -> QWidget:
        """RIGHT: Export options and actions."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Export header
        header = QLabel("Export & Actions")
        header.setStyleSheet(
            f"""
            QLabel {{
                color: {AutoFireColor.TEXT_PRIMARY.value};
                font-size: 18px;
                font-weight: bold;
                padding: 8px 0px;
            }}
        """
        )
        layout.addWidget(header)

        # Quick export buttons
        quick_export_group = QGroupBox("Quick Export")
        quick_layout = QVBoxLayout()

        export_buttons = [
            ("📄 Export to PDF", ExportFormat.PDF, "Professional PDF for client delivery"),
            ("📊 Export to Excel", ExportFormat.EXCEL, "Spreadsheet for further analysis"),
            ("🖨️ Print Report", ExportFormat.PRINT, "Send directly to printer"),
            ("📋 Copy to Clipboard", ExportFormat.CSV, "Copy table for pasting elsewhere"),
        ]

        for text, format_type, tooltip in export_buttons:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked, fmt=format_type: self.export_report(fmt))
            quick_layout.addWidget(btn)

        quick_export_group.setLayout(quick_layout)
        layout.addWidget(quick_export_group)

        # CAD integration
        cad_group = QGroupBox("CAD Integration")
        cad_layout = QVBoxLayout()

        cad_buttons = [
            ("📐 Create CAD Block", "Generate AutoCAD block for model space"),
            ("📋 Export for Paperspace", "Format table for paperspace insertion"),
            ("🔗 Link to Drawing", "Associate report with drawing file"),
        ]

        for text, tooltip in cad_buttons:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda: self.cad_export(text))
            cad_layout.addWidget(btn)

        cad_group.setLayout(cad_layout)
        layout.addWidget(cad_group)

        # Report statistics
        stats_group = QGroupBox("Report Statistics")
        stats_layout = QVBoxLayout()

        self.stats_label = QLabel("Loading statistics...")
        self.stats_label.setStyleSheet(
            f"""
            QLabel {{
                color: {AutoFireColor.TEXT_SECONDARY.value};
                font-size: 11px;
                padding: 8px;
                background-color: {AutoFireColor.BACKGROUND.value};
                border-radius: 4px;
            }}
        """
        )
        self.stats_label.setWordWrap(True)

        stats_layout.addWidget(self.stats_label)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Recent exports
        recent_group = QGroupBox("Recent Exports")
        recent_layout = QVBoxLayout()

        recent_list = QListWidget()
        recent_list.setMaximumHeight(120)
        recent_items = [
            "Device Schedule - PDF (Today 2:15 PM)",
            "Circuit Analysis - Excel (Today 11:30 AM)",
            "Compliance Summary - PDF (Yesterday)",
        ]
        for item in recent_items:
            recent_list.addItem(item)

        recent_layout.addWidget(recent_list)
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)

        layout.addStretch()

        widget.setLayout(layout)
        widget.setStyleSheet(
            f"""
            QWidget {{
                background-color: {AutoFireColor.SURFACE_PRIMARY.value};
                border-left: 1px solid {AutoFireColor.BORDER_PRIMARY.value};
            }}
        """
        )

        return widget

    def create_report_header(self) -> QWidget:
        """Create professional report header."""
        header_widget = QFrame()
        header_widget.setFrameStyle(QFrame.Box)
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(16, 12, 16, 12)

        # Company/project title
        title_layout = QHBoxLayout()

        company_label = QLabel("AUTOFIRE PROFESSIONAL")
        company_label.setStyleSheet(
            f"""
            QLabel {{
                color: {AutoFireColor.PRIMARY.value};
                font-size: 16px;
                font-weight: bold;
            }}
        """
        )

        logo_placeholder = QLabel("🔥")
        logo_placeholder.setStyleSheet(
            f"""
            QLabel {{
                font-size: 24px;
                color: {AutoFireColor.PRIMARY.value};
            }}
        """
        )

        title_layout.addWidget(logo_placeholder)
        title_layout.addWidget(company_label)
        title_layout.addStretch()

        # Project info
        project_info = self.current_data["project_info"]

        project_label = QLabel(f"Fire Alarm System Design Report")
        project_label.setStyleSheet(
            f"""
            QLabel {{
                color: {AutoFireColor.TEXT_PRIMARY.value};
                font-size: 14px;
                font-weight: 600;
            }}
        """
        )

        project_details = QLabel(
            f"Project: {project_info['name']}\\nLocation: {project_info['address']}\\nEngineer: {project_info['engineer']}\\nDate: {project_info['date']}"
        )
        project_details.setStyleSheet(
            f"""
            QLabel {{
                color: {AutoFireColor.TEXT_SECONDARY.value};
                font-size: 11px;
                line-height: 1.4;
            }}
        """
        )

        header_layout.addLayout(title_layout)
        header_layout.addWidget(project_label)
        header_layout.addWidget(project_details)

        header_widget.setLayout(header_layout)
        header_widget.setStyleSheet(
            f"""
            QFrame {{
                background-color: {AutoFireColor.SURFACE_SECONDARY.value};
                border: 1px solid {AutoFireColor.BORDER_PRIMARY.value};
                border-radius: 6px;
            }}
        """
        )

        return header_widget

    def update_favorites_list(self):
        """Update the favorites list display."""
        self.favorites_list.clear()
        for template in self.report_templates:
            if template.is_favorite:
                item = QListWidgetItem(f"⭐ {template.name}")
                item.setData(Qt.UserRole, template)
                self.favorites_list.addItem(item)

    def update_templates_list(self):
        """Update the main templates list display."""
        self.templates_list.clear()

        # Group by report type
        type_groups = {}
        for template in self.report_templates:
            type_name = template.report_type.value.replace("_", " ").title()
            if type_name not in type_groups:
                type_groups[type_name] = []
            type_groups[type_name].append(template)

        for type_name, templates in type_groups.items():
            type_item = QTreeWidgetItem(self.templates_list, [type_name])
            type_item.setExpanded(True)

            for template in templates:
                template_item = QTreeWidgetItem(type_item, [template.name])
                template_item.setData(0, Qt.UserRole, template)
                if template.is_favorite:
                    template_item.setText(0, f"⭐ {template.name}")

    def on_favorite_selected(self, item):
        """Handle favorite template selection."""
        template = item.data(Qt.UserRole)
        if template:
            self.load_template(template)

    def on_template_selected(self, item):
        """Handle template selection from main list."""
        template = item.data(0, Qt.UserRole)
        if template:
            self.load_template(template)

    def load_template(self, template: ReportTemplate):
        """Load a template and update the preview."""
        self.current_template = template
        self.template_info.setText(f"{template.name} - {template.description}")
        self.template_name_edit.setText(template.name)

        # Update columns list
        self.columns_list.clear()
        all_columns = self.get_available_columns(template.report_type)
        for column in all_columns:
            item = QListWidgetItem(column)
            item.setCheckState(Qt.Checked if column in template.columns else Qt.Unchecked)
            self.columns_list.addItem(item)

        # Update report preview
        self.update_report_preview(template)

    def get_available_columns(self, report_type: ReportType) -> List[str]:
        """Get all available columns for a report type."""
        if report_type == ReportType.DEVICE_SCHEDULE:
            return [
                "Address",
                "Device Type",
                "Model",
                "Location",
                "Circuit",
                "Zone",
                "Voltage",
                "Current",
                "Notes",
            ]
        elif report_type == ReportType.CIRCUIT_ANALYSIS:
            return [
                "Circuit ID",
                "Type",
                "Wire Gauge",
                "Length (ft)",
                "Devices",
                "Load (A)",
                "V-Drop (%)",
                "Status",
            ]
        else:
            return ["Column 1", "Column 2", "Column 3", "Column 4"]

    def update_report_preview(self, template: ReportTemplate):
        """Update the report table preview."""
        if template.report_type == ReportType.DEVICE_SCHEDULE:
            self.populate_device_schedule(template)
        elif template.report_type == ReportType.CIRCUIT_ANALYSIS:
            self.populate_circuit_analysis(template)
        else:
            self.populate_generic_report(template)

        self.update_report_statistics()

    def populate_device_schedule(self, template: ReportTemplate):
        """Populate device schedule report."""
        devices = self.current_data["devices"]

        self.report_table.setRowCount(len(devices))
        self.report_table.setColumnCount(len(template.columns))
        self.report_table.setHorizontalHeaderLabels(template.columns)

        for row, device in enumerate(devices):
            for col, column_name in enumerate(template.columns):
                value = ""
                if column_name == "Address":
                    value = device.address
                elif column_name == "Device Type":
                    value = device.device_type
                elif column_name == "Model":
                    value = device.model
                elif column_name == "Location":
                    value = device.location
                elif column_name == "Circuit":
                    value = device.circuit
                elif column_name == "Zone":
                    value = device.zone
                elif column_name == "Voltage":
                    value = device.voltage
                elif column_name == "Current":
                    value = device.current
                elif column_name == "Notes":
                    value = device.notes

                self.report_table.setItem(row, col, QTableWidgetItem(value))

        self.report_table.resizeColumnsToContents()

        # Update footer
        device_count = len(devices)
        circuit_count = len(set(d.circuit for d in devices))
        self.report_footer.setText(
            f"Summary: {device_count} devices across {circuit_count} circuits. All devices meet NFPA 72 requirements for addressable fire alarm systems."
        )

    def populate_circuit_analysis(self, template: ReportTemplate):
        """Populate circuit analysis report."""
        circuits = self.current_data["circuits"]

        self.report_table.setRowCount(len(circuits))
        self.report_table.setColumnCount(len(template.columns))
        self.report_table.setHorizontalHeaderLabels(template.columns)

        for row, circuit in enumerate(circuits):
            for col, column_name in enumerate(template.columns):
                value = ""
                if column_name == "Circuit ID":
                    value = circuit.circuit_id
                elif column_name == "Type":
                    value = circuit.circuit_type
                elif column_name == "Wire Gauge":
                    value = circuit.wire_gauge
                elif column_name == "Length (ft)":
                    value = str(circuit.length_ft)
                elif column_name == "Devices":
                    value = str(circuit.device_count)
                elif column_name == "Load (A)":
                    value = f"{circuit.load_amps:.3f}"
                elif column_name == "V-Drop (%)":
                    value = f"{circuit.voltage_drop:.1f}%"
                elif column_name == "Status":
                    value = circuit.compliance_status

                item = QTableWidgetItem(value)

                # Color code compliance status
                if column_name == "Status":
                    if "✓" in value:
                        item.setForeground(QColor(AutoFireColor.COMPLIANCE_PASS.value))
                    elif "⚠" in value:
                        item.setForeground(QColor(AutoFireColor.COMPLIANCE_WARNING.value))

                self.report_table.setItem(row, col, item)

        self.report_table.resizeColumnsToContents()

        # Update footer
        total_devices = sum(c.device_count for c in circuits)
        max_voltage_drop = max(c.voltage_drop for c in circuits)
        self.report_footer.setText(
            f"Circuit Analysis Summary: {len(circuits)} circuits serving {total_devices} devices. Maximum voltage drop: {max_voltage_drop:.1f}% (NFPA 72 limit: 10%)."
        )

    def populate_generic_report(self, template: ReportTemplate):
        """Populate a generic report template."""
        self.report_table.setRowCount(3)
        self.report_table.setColumnCount(len(template.columns))
        self.report_table.setHorizontalHeaderLabels(template.columns)

        for row in range(3):
            for col, column_name in enumerate(template.columns):
                value = f"Sample {column_name} {row + 1}"
                self.report_table.setItem(row, col, QTableWidgetItem(value))

        self.report_table.resizeColumnsToContents()
        self.report_footer.setText(
            "Sample report data. Select a specific report type for actual project data."
        )

    def update_report_statistics(self):
        """Update report statistics display."""
        row_count = self.report_table.rowCount()
        col_count = self.report_table.columnCount()

        stats_text = f"Report Statistics:\\n"
        stats_text += f"• {row_count} records\\n"
        stats_text += f"• {col_count} columns\\n"
        stats_text += f"• Template: {self.current_template.name}\\n"
        stats_text += f"• Last updated: {datetime.now().strftime('%I:%M %p')}"

        self.stats_label.setText(stats_text)

    def save_current_template(self):
        """Save the current template configuration."""
        # Get selected columns
        selected_columns = []
        for i in range(self.columns_list.count()):
            item = self.columns_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_columns.append(item.text())

        # Update template
        self.current_template.columns = selected_columns
        self.current_template.name = self.template_name_edit.text()

        # Refresh preview
        self.update_report_preview(self.current_template)

        self.statusBar().showMessage(
            f"Template '{self.current_template.name}' saved successfully", 3000
        )

    def add_to_favorites(self):
        """Add current template to favorites."""
        self.current_template.is_favorite = True
        self.update_favorites_list()
        self.update_templates_list()
        self.statusBar().showMessage(f"'{self.current_template.name}' added to favorites", 3000)

    def export_report(self, format_type: ExportFormat):
        """Export report in specified format."""
        if format_type == ExportFormat.PDF:
            self.export_to_pdf()
        elif format_type == ExportFormat.EXCEL:
            self.export_to_excel()
        elif format_type == ExportFormat.PRINT:
            self.print_report()
        elif format_type == ExportFormat.CSV:
            self.copy_to_clipboard()

    def export_to_pdf(self):
        """Export report to PDF."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Report to PDF",
            f"{self.current_template.name.replace(' ', '_')}.pdf",
            "PDF Files (*.pdf)",
        )

        if filename:
            # In a real implementation, this would generate a proper PDF
            self.statusBar().showMessage(f"Report exported to PDF: {filename}", 5000)

    def export_to_excel(self):
        """Export report to Excel."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Report to Excel",
            f"{self.current_template.name.replace(' ', '_')}.xlsx",
            "Excel Files (*.xlsx)",
        )

        if filename:
            # In a real implementation, this would generate Excel file
            self.statusBar().showMessage(f"Report exported to Excel: {filename}", 5000)

    def print_report(self):
        """Print the report."""
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)

        if dialog.exec() == QPrintDialog.Accepted:
            # In a real implementation, this would print the formatted report
            self.statusBar().showMessage("Report sent to printer", 3000)

    def copy_to_clipboard(self):
        """Copy report table to clipboard."""
        # Get table data
        rows = []
        headers = [
            self.report_table.horizontalHeaderItem(i).text()
            for i in range(self.report_table.columnCount())
        ]
        rows.append("\\t".join(headers))

        for row in range(self.report_table.rowCount()):
            row_data = []
            for col in range(self.report_table.columnCount()):
                item = self.report_table.item(row, col)
                row_data.append(item.text() if item else "")
            rows.append("\\t".join(row_data))

        clipboard_text = "\\n".join(rows)

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_text)

        self.statusBar().showMessage(
            "Report table copied to clipboard - ready to paste into Excel or CAD", 5000
        )

    def cad_export(self, export_type: str):
        """Handle CAD export options."""
        if "CAD Block" in export_type:
            self.statusBar().showMessage(
                "Generating AutoCAD block for model space insertion...", 3000
            )
        elif "Paperspace" in export_type:
            self.statusBar().showMessage("Formatting table for paperspace insertion...", 3000)
        elif "Link" in export_type:
            self.statusBar().showMessage("Linking report to drawing file...", 3000)

    def apply_professional_styling(self):
        """Apply professional theme to reporting interface."""
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {AutoFireColor.BACKGROUND.value};
                color: {AutoFireColor.TEXT_PRIMARY.value};
            }}

            QGroupBox {{
                font-weight: 600;
                border: 1px solid {AutoFireColor.BORDER_PRIMARY.value};
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 6px;
                background-color: {AutoFireColor.SURFACE_SECONDARY.value};
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
                color: {AutoFireColor.TEXT_PRIMARY.value};
                font-size: 12px;
            }}

            QTableWidget {{
                background-color: {AutoFireColor.BACKGROUND.value};
                border: 1px solid {AutoFireColor.BORDER_SECONDARY.value};
                border-radius: 4px;
                color: {AutoFireColor.TEXT_PRIMARY.value};
                gridline-color: {AutoFireColor.BORDER_SECONDARY.value};
                selection-background-color: {AutoFireColor.SELECTION_BG.value};
            }}

            QTableWidget::item {{
                padding: 6px;
                border-bottom: 1px solid {AutoFireColor.BORDER_SECONDARY.value};
            }}

            QTableWidget::item:selected {{
                background-color: {AutoFireColor.SELECTION_BG.value};
                color: {AutoFireColor.TEXT_PRIMARY.value};
            }}

            QHeaderView::section {{
                background-color: {AutoFireColor.SURFACE_SECONDARY.value};
                color: {AutoFireColor.TEXT_PRIMARY.value};
                border: none;
                border-right: 1px solid {AutoFireColor.BORDER_PRIMARY.value};
                border-bottom: 1px solid {AutoFireColor.BORDER_PRIMARY.value};
                padding: 8px;
                font-weight: 600;
            }}

            QListWidget, QTreeWidget {{
                background-color: {AutoFireColor.BACKGROUND.value};
                border: 1px solid {AutoFireColor.BORDER_SECONDARY.value};
                border-radius: 4px;
                color: {AutoFireColor.TEXT_PRIMARY.value};
                selection-background-color: {AutoFireColor.SELECTION_BG.value};
            }}

            QListWidget::item, QTreeWidget::item {{
                padding: 6px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}

            QListWidget::item:hover, QTreeWidget::item:hover {{
                background-color: {AutoFireColor.HOVER_LIGHT.value};
            }}

            QPushButton {{
                background-color: {AutoFireColor.SURFACE_SECONDARY.value};
                border: 1px solid {AutoFireColor.BORDER_PRIMARY.value};
                border-radius: 6px;
                color: {AutoFireColor.TEXT_PRIMARY.value};
                padding: 8px 16px;
                font-weight: 500;
                text-align: left;
            }}

            QPushButton:hover {{
                background-color: {AutoFireColor.BUTTON_HOVER.value};
                border-color: {AutoFireColor.ACCENT.value};
            }}

            QPushButton:pressed {{
                background-color: {AutoFireColor.BUTTON_PRESSED.value};
            }}

            QLineEdit, QTextEdit {{
                background-color: {AutoFireColor.BACKGROUND.value};
                border: 1px solid {AutoFireColor.BORDER_SECONDARY.value};
                border-radius: 4px;
                color: {AutoFireColor.TEXT_PRIMARY.value};
                padding: 6px;
            }}

            QLineEdit:focus, QTextEdit:focus {{
                border-color: {AutoFireColor.ACCENT.value};
            }}
        """
        )


def main():
    """Run the professional reporting system demo."""
    app = QApplication(sys.argv)
    app.setApplicationName("AutoFire Professional Reporting")
    app.setStyle("Fusion")

    reporting_system = ProfessionalReportingSystem()
    reporting_system.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
