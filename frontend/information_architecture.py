"""
AutoFire Information Architecture - Professional UI Layout System

This module defines the intelligent information architecture for AutoFire,
ensuring information is organized by professional workflow needs, not just
randomly placed in windows.

Key Principles:
- Context drives content (what you select determines what you see)
- Professional hierarchy (Critical > Important > Reference)
- Fast access to frequently needed data
- Information panels that expand/collapse based on need
- Logical spatial organization matching designer mental models
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import logging

try:
    from PySide6.QtCore import Qt, QTimer, pyqtSignal
    from PySide6.QtGui import QFont, QColor, QPalette
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
        QTabWidget, QScrollArea, QFrame, QLabel,
        QPushButton, QToolButton, QGroupBox,
        QTreeWidget, QTreeWidgetItem, QTextEdit,
        QTableWidget, QTableWidgetItem, QApplication
    )
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    # When PySide6 is not available, we can't run the UI
    pass

from frontend.design_system import AutoFireColor, AutoFireTypography, AutoFireSpacing

logger = logging.getLogger(__name__)


class InformationPriority(Enum):
    """Information priority levels for professional workflow."""
    CRITICAL = 1    # Code violations, safety issues, calculation errors
    IMPORTANT = 2   # Device specs, placement requirements, circuit properties
    REFERENCE = 3   # Full datasheets, standards text, installation guides
    CONTEXT = 4     # Contextual help, tips, related information


class InformationContext(Enum):
    """Context types that drive information display."""
    DEVICE_SELECTED = "device"
    WIRE_SELECTED = "wire"
    AREA_SELECTED = "area"
    PANEL_SELECTED = "panel"
    CIRCUIT_SELECTED = "circuit"
    NOTHING_SELECTED = "none"
    PROJECT_OVERVIEW = "project"


@dataclass
class InformationPanel:
    """Definition of an information panel with its behavior."""
    name: str
    title: str
    priority: InformationPriority
    contexts: List[InformationContext]
    expandable: bool = True
    default_expanded: bool = False
    min_height: int = 100
    preferred_height: int = 200
    max_height: int = 400


class ProfessionalInformationLayout:
    """
    Thoughtful information architecture for fire alarm design professionals.
    
    Layout Philosophy:
    - Left: Project navigator & device library (what you can use)
    - Center: Main design canvas (what you're working on)
    - Right: Context information (details about what's selected)
    - Bottom: Status, calculations, compliance (critical feedback)
    """
    
    # Define the professional panel layout
    PANELS = {
        # LEFT SIDEBAR - Tools and Resources
        "project_navigator": InformationPanel(
            "project_navigator",
            "Project Navigator",
            InformationPriority.IMPORTANT,
            [InformationContext.PROJECT_OVERVIEW],
            expandable=False,
            default_expanded=True,
            min_height=200,
            preferred_height=300
        ),
        
        "device_library": InformationPanel(
            "device_library", 
            "Device Library",
            InformationPriority.IMPORTANT,
            [InformationContext.NOTHING_SELECTED, InformationContext.PROJECT_OVERVIEW],
            expandable=True,
            default_expanded=True,
            min_height=150,
            preferred_height=250
        ),
        
        "quick_reference": InformationPanel(
            "quick_reference",
            "Quick Reference",
            InformationPriority.REFERENCE,
            [InformationContext.NOTHING_SELECTED],
            expandable=True,
            default_expanded=False,
            min_height=100,
            preferred_height=150
        ),
        
        # RIGHT SIDEBAR - Context Information
        "device_properties": InformationPanel(
            "device_properties",
            "Device Properties",
            InformationPriority.IMPORTANT,
            [InformationContext.DEVICE_SELECTED],
            expandable=True,
            default_expanded=True,
            min_height=150,
            preferred_height=250
        ),
        
        "circuit_properties": InformationPanel(
            "circuit_properties",
            "Circuit Properties", 
            InformationPriority.IMPORTANT,
            [InformationContext.WIRE_SELECTED, InformationContext.CIRCUIT_SELECTED],
            expandable=True,
            default_expanded=True,
            min_height=120,
            preferred_height=200
        ),
        
        "coverage_analysis": InformationPanel(
            "coverage_analysis",
            "Coverage Analysis",
            InformationPriority.IMPORTANT,
            [InformationContext.AREA_SELECTED, InformationContext.DEVICE_SELECTED],
            expandable=True,
            default_expanded=True,
            min_height=100,
            preferred_height=180
        ),
        
        "detailed_specs": InformationPanel(
            "detailed_specs",
            "Detailed Specifications",
            InformationPriority.REFERENCE,
            [InformationContext.DEVICE_SELECTED, InformationContext.PANEL_SELECTED],
            expandable=True,
            default_expanded=False,
            min_height=150,
            preferred_height=300,
            max_height=500
        ),
        
        # BOTTOM PANEL - Critical Information
        "compliance_status": InformationPanel(
            "compliance_status",
            "Compliance & Calculations",
            InformationPriority.CRITICAL,
            [InformationContext.PROJECT_OVERVIEW, InformationContext.DEVICE_SELECTED, 
             InformationContext.CIRCUIT_SELECTED],
            expandable=True,
            default_expanded=True,
            min_height=80,
            preferred_height=120
        )
    }


if PYSIDE6_AVAILABLE:
    class ContextAwareInformationWidget(QWidget):
        """
        Smart information widget that shows relevant content based on current selection.
        
        This is the core of the 'thoughtful UI' - it knows what information professionals
        need based on what they're working on.
        """
        
        context_changed = pyqtSignal(InformationContext)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.current_context = InformationContext.NOTHING_SELECTED
            self.selected_object = None
            self.information_panels = {}
            
            self._setup_ui()
            
        def _setup_ui(self):
            """Setup the main information architecture layout."""
            self.setObjectName("ContextAwareInformationWidget")
            
            # Main horizontal splitter: Left sidebar | Center canvas | Right sidebar
            main_splitter = QSplitter(Qt.Horizontal)
            
            # Left sidebar - Project tools and resources
            left_sidebar = self._create_left_sidebar()
            
            # Center area will be the main canvas (managed elsewhere)
            center_placeholder = QLabel("Main Canvas Area\n(Managed by ModelSpaceWindow)")
            center_placeholder.setAlignment(Qt.AlignCenter)
            center_placeholder.setStyleSheet(f"""
                background-color: {AutoFireColor.BACKGROUND_SECONDARY.value};
                color: {AutoFireColor.TEXT_MUTED.value};
                border: 2px dashed {AutoFireColor.BORDER_SECONDARY.value};
                border-radius: 8px;
                font-size: 14px;
            """)
            
            # Right sidebar - Context-aware information
            right_sidebar = self._create_right_sidebar()
            
            # Add to main splitter
            main_splitter.addWidget(left_sidebar)
            main_splitter.addWidget(center_placeholder)
            main_splitter.addWidget(right_sidebar)
            
            # Set professional proportions: 20% left, 60% center, 20% right
            main_splitter.setSizes([300, 900, 300])
            main_splitter.setCollapsible(0, False)  # Left sidebar always visible
            main_splitter.setCollapsible(2, False)  # Right sidebar always visible
            
            # Bottom panel for critical information
            bottom_panel = self._create_bottom_panel()
            
            # Main vertical layout
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Vertical splitter for main content and bottom panel
            vertical_splitter = QSplitter(Qt.Vertical)
            vertical_splitter.addWidget(main_splitter)
            vertical_splitter.addWidget(bottom_panel)
            vertical_splitter.setSizes([800, 150])  # Main area larger than bottom
            
            main_layout.addWidget(vertical_splitter)
            self.setLayout(main_layout)
        
    def _create_left_sidebar(self) -> QWidget:
        """Create the left sidebar with project tools and device library."""
        sidebar = QWidget()
        sidebar.setObjectName("LeftSidebar")
        sidebar.setMinimumWidth(250)
        sidebar.setMaximumWidth(400)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(AutoFireSpacing.SM, AutoFireSpacing.SM, 
                                  AutoFireSpacing.SM, AutoFireSpacing.SM)
        layout.setSpacing(AutoFireSpacing.SM)
        
        # Project Navigator
        nav_panel = self._create_information_panel(
            ProfessionalInformationLayout.PANELS["project_navigator"],
            self._create_project_navigator_content()
        )
        layout.addWidget(nav_panel)
        
        # Device Library
        device_panel = self._create_information_panel(
            ProfessionalInformationLayout.PANELS["device_library"],
            self._create_device_library_content()
        )
        layout.addWidget(device_panel)
        
        # Quick Reference (collapsed by default)
        ref_panel = self._create_information_panel(
            ProfessionalInformationLayout.PANELS["quick_reference"],
            self._create_quick_reference_content()
        )
        layout.addWidget(ref_panel)
        
        layout.addStretch()  # Push everything to top
        
        sidebar.setLayout(layout)
        sidebar.setStyleSheet(f"""
            QWidget#LeftSidebar {{
                background-color: {AutoFireColor.SURFACE_PRIMARY.value};
                border-right: 1px solid {AutoFireColor.BORDER_PRIMARY.value};
            }}
        """)
        
        return sidebar
        
    def _create_right_sidebar(self) -> QWidget:
        """Create the right sidebar with context-aware information."""
        sidebar = QWidget()
        sidebar.setObjectName("RightSidebar")
        sidebar.setMinimumWidth(250)
        sidebar.setMaximumWidth(400)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(AutoFireSpacing.SM, AutoFireSpacing.SM,
                                  AutoFireSpacing.SM, AutoFireSpacing.SM)
        layout.setSpacing(AutoFireSpacing.SM)
        
        # Context-aware panels (will show/hide based on selection)
        self.device_props_panel = self._create_information_panel(
            ProfessionalInformationLayout.PANELS["device_properties"],
            self._create_device_properties_content()
        )
        layout.addWidget(self.device_props_panel)
        
        self.circuit_props_panel = self._create_information_panel(
            ProfessionalInformationLayout.PANELS["circuit_properties"],
            self._create_circuit_properties_content()
        )
        layout.addWidget(self.circuit_props_panel)
        
        self.coverage_panel = self._create_information_panel(
            ProfessionalInformationLayout.PANELS["coverage_analysis"],
            self._create_coverage_analysis_content()
        )
        layout.addWidget(self.coverage_panel)
        
        self.detailed_specs_panel = self._create_information_panel(
            ProfessionalInformationLayout.PANELS["detailed_specs"],
            self._create_detailed_specs_content()
        )
        layout.addWidget(self.detailed_specs_panel)
        
        layout.addStretch()
        
        sidebar.setLayout(layout)
        sidebar.setStyleSheet(f"""
            QWidget#RightSidebar {{
                background-color: {AutoFireColor.SURFACE_PRIMARY.value};
                border-left: 1px solid {AutoFireColor.BORDER_PRIMARY.value};
            }}
        """)
        
        return sidebar
        
    def _create_bottom_panel(self) -> QWidget:
        """Create the bottom panel for critical compliance and calculation information."""
        panel = self._create_information_panel(
            ProfessionalInformationLayout.PANELS["compliance_status"],
            self._create_compliance_status_content()
        )
        
        panel.setStyleSheet(f"""
            QWidget {{
                background-color: {AutoFireColor.SURFACE_SECONDARY.value};
                border-top: 1px solid {AutoFireColor.BORDER_PRIMARY.value};
            }}
        """)
        
        return panel
        
    def _create_information_panel(self, panel_def: InformationPanel, content_widget: QWidget) -> QWidget:
        """Create a collapsible information panel with professional styling."""
        panel = QFrame()
        panel.setObjectName(f"InfoPanel_{panel_def.name}")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with expand/collapse button
        header = QFrame()
        header.setFixedHeight(32)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(AutoFireSpacing.SM, AutoFireSpacing.XS,
                                       AutoFireSpacing.SM, AutoFireSpacing.XS)
        
        # Panel title
        title_label = QLabel(panel_def.title)
        title_label.setFont(QFont(AutoFireTypography.PRIMARY_FONT, AutoFireTypography.TITLE_MEDIUM))
        title_label.setStyleSheet(f"color: {AutoFireColor.TEXT_PRIMARY.value};")
        
        # Expand/collapse button (if expandable)
        if panel_def.expandable:
            expand_btn = QToolButton()
            expand_btn.setText("▼" if panel_def.default_expanded else "▶")
            expand_btn.setStyleSheet(f"""
                QToolButton {{
                    background: transparent;
                    border: none;
                    color: {AutoFireColor.TEXT_SECONDARY.value};
                    font-size: 12px;
                }}
                QToolButton:hover {{
                    color: {AutoFireColor.TEXT_PRIMARY.value};
                }}
            """)
            
            # Connect expand/collapse functionality
            content_visible = panel_def.default_expanded
            content_widget.setVisible(content_visible)
            
            def toggle_panel():
                nonlocal content_visible
                content_visible = not content_visible
                content_widget.setVisible(content_visible)
                expand_btn.setText("▼" if content_visible else "▶")
                
            expand_btn.clicked.connect(toggle_panel)
            header_layout.addWidget(expand_btn)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Priority indicator
        priority_color = {
            InformationPriority.CRITICAL: AutoFireColor.COMPLIANCE_FAIL.value,
            InformationPriority.IMPORTANT: AutoFireColor.ACCENT.value,
            InformationPriority.REFERENCE: AutoFireColor.TEXT_MUTED.value,
            InformationPriority.CONTEXT: AutoFireColor.TEXT_MUTED.value
        }[panel_def.priority]
        
        priority_indicator = QFrame()
        priority_indicator.setFixedSize(4, 20)
        priority_indicator.setStyleSheet(f"background-color: {priority_color}; border-radius: 2px;")
        header_layout.addWidget(priority_indicator)
        
        header.setLayout(header_layout)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {AutoFireColor.SURFACE_SECONDARY.value};
                border-bottom: 1px solid {AutoFireColor.BORDER_SECONDARY.value};
            }}
        """)
        
        layout.addWidget(header)
        layout.addWidget(content_widget)
        
        panel.setLayout(layout)
        panel.setFrameStyle(QFrame.Box)
        panel.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {AutoFireColor.BORDER_SECONDARY.value};
                border-radius: 4px;
                background-color: {AutoFireColor.SURFACE_PRIMARY.value};
            }}
        """)
        
        # Store panel reference for context switching
        self.information_panels[panel_def.name] = {
            "widget": panel,
            "content": content_widget,
            "definition": panel_def
        }
        
        return panel
        
    def _create_project_navigator_content(self) -> QWidget:
        """Create content for project navigator panel."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(AutoFireSpacing.SM, AutoFireSpacing.SM,
                                  AutoFireSpacing.SM, AutoFireSpacing.SM)
        
        # Project tree
        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {AutoFireColor.BACKGROUND.value};
                color: {AutoFireColor.TEXT_PRIMARY.value};
                border: 1px solid {AutoFireColor.BORDER_SECONDARY.value};
                border-radius: 4px;
            }}
            QTreeWidget::item:hover {{
                background-color: {AutoFireColor.HOVER_LIGHT.value};
            }}
            QTreeWidget::item:selected {{
                background-color: {AutoFireColor.SELECTION_BG.value};
            }}
        """)
        
        # Sample project structure
        root = QTreeWidgetItem(tree, ["Current Project"])
        floors = QTreeWidgetItem(root, ["Floors"])
        QTreeWidgetItem(floors, ["Ground Floor"])
        QTreeWidgetItem(floors, ["Second Floor"])
        QTreeWidgetItem(floors, ["Basement"])
        
        systems = QTreeWidgetItem(root, ["Systems"])
        QTreeWidgetItem(systems, ["Fire Alarm Panel"])
        QTreeWidgetItem(systems, ["NAC Circuits"])
        QTreeWidgetItem(systems, ["SLC Circuits"])
        
        tree.expandAll()
        layout.addWidget(tree)
        
        widget.setLayout(layout)
        return widget
        
    def _create_device_library_content(self) -> QWidget:
        """Create content for device library panel."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(AutoFireSpacing.SM, AutoFireSpacing.SM,
                                  AutoFireSpacing.SM, AutoFireSpacing.SM)
        
        # Device categories
        categories = QTreeWidget()
        categories.setHeaderHidden(True)
        categories.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {AutoFireColor.BACKGROUND.value};
                color: {AutoFireColor.TEXT_PRIMARY.value};
                border: 1px solid {AutoFireColor.BORDER_SECONDARY.value};
                border-radius: 4px;
            }}
        """)
        
        # Sample device categories
        detectors = QTreeWidgetItem(categories, ["Smoke Detectors"])
        QTreeWidgetItem(detectors, ["Photoelectric"])
        QTreeWidgetItem(detectors, ["Ionization"])
        QTreeWidgetItem(detectors, ["Multi-Sensor"])
        
        notification = QTreeWidgetItem(categories, ["Notification"])
        QTreeWidgetItem(notification, ["Horns"])
        QTreeWidgetItem(notification, ["Strobes"])
        QTreeWidgetItem(notification, ["Speaker/Strobes"])
        
        manual = QTreeWidgetItem(categories, ["Manual Devices"])
        QTreeWidgetItem(manual, ["Pull Stations"])
        QTreeWidgetItem(manual, ["Key Switches"])
        
        categories.expandAll()
        layout.addWidget(categories)
        
        widget.setLayout(layout)
        return widget
        
    def _create_quick_reference_content(self) -> QWidget:
        """Create content for quick reference panel."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(AutoFireSpacing.SM, AutoFireSpacing.SM,
                                  AutoFireSpacing.SM, AutoFireSpacing.SM)
        
        # Quick reference data
        ref_text = QTextEdit()
        ref_text.setMaximumHeight(120)
        ref_text.setPlainText("""NFPA 72 Quick Reference:
• Smoke Detector Spacing: 30' max
• Heat Detector Spacing: 50' max
• Strobe Candela: 15/30/75/110 cd
• NAC Circuit: 24V max load
• SLC Circuit: 3000' max length
• Voltage Drop: 10% max""")
        
        ref_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AutoFireColor.BACKGROUND.value};
                color: {AutoFireColor.TEXT_SECONDARY.value};
                border: 1px solid {AutoFireColor.BORDER_SECONDARY.value};
                border-radius: 4px;
                font-family: {AutoFireTypography.MONOSPACE_FONT};
                font-size: 9px;
            }}
        """)
        
        layout.addWidget(ref_text)
        widget.setLayout(layout)
        return widget
        
    def _create_device_properties_content(self) -> QWidget:
        """Create content for device properties panel."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(AutoFireSpacing.SM, AutoFireSpacing.SM,
                                  AutoFireSpacing.SM, AutoFireSpacing.SM)
        
        # Properties table
        props_table = QTableWidget(0, 2)
        props_table.setHorizontalHeaderLabels(["Property", "Value"])
        props_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {AutoFireColor.BACKGROUND.value};
                color: {AutoFireColor.TEXT_PRIMARY.value};
                border: 1px solid {AutoFireColor.BORDER_SECONDARY.value};
                border-radius: 4px;
            }}
            QHeaderView::section {{
                background-color: {AutoFireColor.SURFACE_SECONDARY.value};
                color: {AutoFireColor.TEXT_PRIMARY.value};
                border: none;
                padding: 4px;
            }}
        """)
        
        layout.addWidget(QLabel("Select a device to view properties"))
        layout.addWidget(props_table)
        
        widget.setLayout(layout)
        return widget
        
    def _create_circuit_properties_content(self) -> QWidget:
        """Create content for circuit properties panel."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(AutoFireSpacing.SM, AutoFireSpacing.SM,
                                  AutoFireSpacing.SM, AutoFireSpacing.SM)
        
        layout.addWidget(QLabel("Select a circuit to view electrical properties"))
        
        # Circuit calculation display
        calc_text = QTextEdit()
        calc_text.setMaximumHeight(100)
        calc_text.setPlainText("Voltage Drop Calculation:\nNo circuit selected")
        calc_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AutoFireColor.BACKGROUND.value};
                color: {AutoFireColor.TEXT_PRIMARY.value};
                border: 1px solid {AutoFireColor.BORDER_SECONDARY.value};
                border-radius: 4px;
                font-family: {AutoFireTypography.MONOSPACE_FONT};
            }}
        """)
        
        layout.addWidget(calc_text)
        widget.setLayout(layout)
        return widget
        
    def _create_coverage_analysis_content(self) -> QWidget:
        """Create content for coverage analysis panel."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(AutoFireSpacing.SM, AutoFireSpacing.SM,
                                  AutoFireSpacing.SM, AutoFireSpacing.SM)
        
        layout.addWidget(QLabel("Coverage Analysis"))
        
        # Coverage status
        status_text = QTextEdit()
        status_text.setMaximumHeight(80)
        status_text.setPlainText("Select an area or device to analyze coverage")
        status_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AutoFireColor.BACKGROUND.value};
                color: {AutoFireColor.TEXT_PRIMARY.value};
                border: 1px solid {AutoFireColor.BORDER_SECONDARY.value};
                border-radius: 4px;
            }}
        """)
        
        layout.addWidget(status_text)
        widget.setLayout(layout)
        return widget
        
    def _create_detailed_specs_content(self) -> QWidget:
        """Create content for detailed specifications panel."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(AutoFireSpacing.SM, AutoFireSpacing.SM,
                                  AutoFireSpacing.SM, AutoFireSpacing.SM)
        
        # Scrollable detailed specs
        scroll = QScrollArea()
        specs_widget = QWidget()
        specs_layout = QVBoxLayout()
        
        specs_layout.addWidget(QLabel("Detailed Specifications"))
        
        specs_text = QTextEdit()
        specs_text.setPlainText("Select a device to view detailed specifications, installation guides, and compliance information.")
        specs_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AutoFireColor.BACKGROUND.value};
                color: {AutoFireColor.TEXT_PRIMARY.value};
                border: 1px solid {AutoFireColor.BORDER_SECONDARY.value};
                border-radius: 4px;
            }}
        """)
        
        specs_layout.addWidget(specs_text)
        specs_widget.setLayout(specs_layout)
        scroll.setWidget(specs_widget)
        
        layout.addWidget(scroll)
        widget.setLayout(layout)
        return widget
        
    def _create_compliance_status_content(self) -> QWidget:
        """Create content for compliance status panel."""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(AutoFireSpacing.SM, AutoFireSpacing.SM,
                                  AutoFireSpacing.SM, AutoFireSpacing.SM)
        
        # Status indicators
        status_label = QLabel("Project Status: ")
        status_label.setStyleSheet(f"color: {AutoFireColor.TEXT_PRIMARY.value};")
        
        compliance_status = QLabel("✓ NFPA 72 Compliant")
        compliance_status.setStyleSheet(f"""
            color: {AutoFireColor.COMPLIANCE_PASS.value};
            font-weight: bold;
        """)
        
        calc_status = QLabel("⚠ Voltage Drop: 8.2%")
        calc_status.setStyleSheet(f"""
            color: {AutoFireColor.COMPLIANCE_WARNING.value};
            font-weight: bold;
        """)
        
        layout.addWidget(status_label)
        layout.addWidget(compliance_status)
        layout.addWidget(calc_status)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
        
    def update_context(self, context: InformationContext, selected_object=None):
        """Update the information display based on current context."""
        logger.info(f"Updating information context to: {context}")
        
        self.current_context = context
        self.selected_object = selected_object
        
        # Show/hide panels based on context
        for panel_name, panel_info in self.information_panels.items():
            panel_def = panel_info["definition"]
            should_show = context in panel_def.contexts
            
            # For expandable panels, only show if context matches
            if panel_def.expandable:
                panel_info["widget"].setVisible(should_show)
            
        # Update content based on selection
        self._update_panel_content(context, selected_object)
        
        self.context_changed.emit(context)
        
    def _update_panel_content(self, context: InformationContext, selected_object):
        """Update panel content based on current selection."""
        # This would be implemented to update the actual content
        # based on what's selected in the main canvas
        pass


if __name__ == "__main__":
    # Demo the information architecture
    if not PYSIDE6_AVAILABLE:
        print("PySide6 not available - cannot run demo")
        sys.exit(1)
        
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Apply dark theme
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(AutoFireColor.BACKGROUND.value))
    palette.setColor(QPalette.WindowText, QColor(AutoFireColor.TEXT_PRIMARY.value))
    app.setPalette(palette)
    
    widget = ContextAwareInformationWidget()
    widget.resize(1400, 800)
    widget.show()
    
    # Demo context switching
    QTimer.singleShot(2000, lambda: widget.update_context(InformationContext.DEVICE_SELECTED))
    QTimer.singleShot(4000, lambda: widget.update_context(InformationContext.CIRCUIT_SELECTED))
    
    sys.exit(app.exec())