#!/usr/bin/env python3
"""
AutoFire Information Panel System

Expandable information panels with drill-down functionality for:
- Device specifications and technical data
- NFPA code references and compliance information  
- Installation guides and procedures
- Engineering calculations and formulas
- Manufacturer documentation and datasheets

Provides rich information architecture optimized for fire alarm engineers.
"""

import sys
import json
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

try:
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                   QHBoxLayout, QFrame, QLabel, QPushButton, QLineEdit,
                                   QScrollArea, QStackedWidget, QListWidget, QListWidgetItem)
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont
except ImportError:
    print("PySide6 not available - using minimal fallbacks")
    sys.exit(1)

# Fallback design system
class AutoFireColor:
    PRIMARY = "#FF6B35"
    SECONDARY = "#2C3E50"
    SUCCESS = "#27AE60"
    WARNING = "#F39C12"
    DANGER = "#E74C3C"
    BACKGROUND = "#1E1E1E"
    SURFACE = "#2D2D2D"
    BORDER = "#404040"
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#B0B0B0"
    TEXT_MUTED = "#808080"
    ACCENT = "#3498DB"
    
class AutoFireFont:
    FAMILY = "Segoe UI"
    SIZE_SMALL = 9
    SIZE_NORMAL = 10
    SIZE_LARGE = 12
    SIZE_HEADING = 14
    SIZE_TITLE = 16

class PanelType(Enum):
    """Types of information panels."""
    DEVICE_SPECS = "device_specs"
    NFPA_CODES = "nfpa_codes"
    INSTALLATION = "installation"
    CALCULATIONS = "calculations"
    MANUFACTURER = "manufacturer"
    COMPLIANCE = "compliance"
    DOCUMENTATION = "documentation"

@dataclass
class PanelSection:
    """A section within an information panel."""
    title: str
    content: str
    subsections: Optional[List['PanelSection']] = None
    links: Optional[List[Dict[str, str]]] = None
    expanded: bool = False
    icon: str = ""
    tags: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []
        if self.links is None:
            self.links = []
        if self.tags is None:
            self.tags = []

@dataclass
class InformationPanel:
    """Complete information panel with metadata."""
    id: str
    title: str
    panel_type: PanelType
    sections: List[PanelSection]
    keywords: Optional[List[str]] = None
    last_updated: str = ""
    source: str = ""
    version: str = "1.0"
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()

class InformationDatabase:
    """Database of information panels and content."""
    
    def __init__(self):
        self.panels: Dict[str, InformationPanel] = {}
        self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample fire alarm engineering data."""
        
        # Sample device specifications panel
        device_panel = InformationPanel(
            id="smoke_detector_specs",
            title="Photoelectric Smoke Detector - Model FSP-851",
            panel_type=PanelType.DEVICE_SPECS,
            sections=[
                PanelSection(
                    title="Technical Specifications",
                    content="High-performance photoelectric smoke detector with advanced signal processing",
                    subsections=[
                        PanelSection(
                            title="Operating Voltage",
                            content="15.2V to 32.4V DC (24V nominal)",
                            icon="⚡"
                        ),
                        PanelSection(
                            title="Current Consumption",
                            content="Standby: 45μA, Alarm: 60mA max",
                            icon="🔋"
                        ),
                        PanelSection(
                            title="Operating Temperature",
                            content="-10°C to +50°C (14°F to 122°F)",
                            icon="🌡️"
                        ),
                        PanelSection(
                            title="Humidity Range",
                            content="10% to 93% RH non-condensing",
                            icon="💧"
                        )
                    ]
                ),
                PanelSection(
                    title="Installation Requirements",
                    content="Ceiling or wall mount with proper spacing requirements",
                    subsections=[
                        PanelSection(
                            title="Spacing Requirements",
                            content="Maximum 30ft spacing, 15ft from walls per NFPA 72",
                            tags=["NFPA 72", "spacing"]
                        ),
                        PanelSection(
                            title="Mounting Height",
                            content="4 inches minimum from ceiling, maximum varies by application",
                            tags=["installation", "mounting"]
                        )
                    ]
                ),
                PanelSection(
                    title="Wiring Information",
                    content="Four-wire conventional or addressable installation",
                    subsections=[
                        PanelSection(
                            title="Wire Gauge",
                            content="18 AWG minimum, 12 AWG maximum",
                            icon="🔌"
                        ),
                        PanelSection(
                            title="Terminal Connections",
                            content="+ (positive), - (negative), AUX+ (auxiliary), AUX- (auxiliary return)",
                            icon="🔧"
                        )
                    ]
                )
            ],
            keywords=["smoke detector", "photoelectric", "FSP-851", "fire alarm"],
            source="System Sensor Technical Documentation"
        )
        
        # NFPA code reference panel
        nfpa_panel = InformationPanel(
            id="nfpa72_detection_spacing",
            title="NFPA 72: Smoke Detector Spacing Requirements",
            panel_type=PanelType.NFPA_CODES,
            sections=[
                PanelSection(
                    title="Chapter 17: Initiating Device Installation",
                    content="Requirements for proper installation and spacing of smoke detectors",
                    subsections=[
                        PanelSection(
                            title="17.7.3.2.3 Spot-Type Smoke Detectors",
                            content="Standard spacing requirements for ceiling-mounted detectors",
                            subsections=[
                                PanelSection(
                                    title="Smooth Ceiling Spacing",
                                    content="30 ft (9.1 m) spacing with 15 ft (4.6 m) from walls",
                                    tags=["spacing", "smooth ceiling"]
                                ),
                                PanelSection(
                                    title="Beam Construction Considerations",
                                    content="Spacing reduction required for beam depths >4 inches",
                                    tags=["beams", "construction"]
                                )
                            ]
                        ),
                        PanelSection(
                            title="17.7.3.2.4 High Ceiling Applications",
                            content="Special requirements for ceilings above 30 feet",
                            subsections=[
                                PanelSection(
                                    title="Stratification Considerations",
                                    content="Thermal stratification may prevent smoke from reaching ceiling",
                                    tags=["high ceiling", "stratification"]
                                )
                            ]
                        )
                    ],
                    links=[
                        {"title": "NFPA 72 Full Document", "url": "https://www.nfpa.org/codes-and-standards/all-codes-and-standards/list-of-codes-and-standards/detail?code=72"},
                        {"title": "NFPA 72 Handbook", "url": "https://www.nfpa.org/codes-and-standards/all-codes-and-standards/list-of-codes-and-standards/detail?code=72HB"}
                    ]
                )
            ],
            keywords=["NFPA 72", "smoke detector", "spacing", "installation"],
            source="NFPA 72 National Fire Alarm and Signaling Code"
        )
        
        # Installation guide panel
        install_panel = InformationPanel(
            id="detector_installation_guide",
            title="Smoke Detector Installation Guide",
            panel_type=PanelType.INSTALLATION,
            sections=[
                PanelSection(
                    title="Pre-Installation Planning",
                    content="Essential steps before beginning installation",
                    subsections=[
                        PanelSection(
                            title="Site Survey",
                            content="Document ceiling types, heights, obstacles, and environmental conditions",
                            icon="📋"
                        ),
                        PanelSection(
                            title="Layout Design",
                            content="Create scaled drawings showing device locations and wire runs",
                            icon="📐"
                        ),
                        PanelSection(
                            title="Material List",
                            content="Calculate quantities of devices, wire, and mounting hardware",
                            icon="📦"
                        )
                    ]
                ),
                PanelSection(
                    title="Installation Procedure",
                    content="Step-by-step installation process",
                    subsections=[
                        PanelSection(
                            title="Step 1: Mount Detector Base",
                            content="Secure base to ceiling with appropriate fasteners",
                            subsections=[
                                PanelSection(
                                    title="Drywall Installation",
                                    content="Use toggle bolts or find ceiling joists for secure mounting"
                                ),
                                PanelSection(
                                    title="Concrete/Masonry",
                                    content="Use concrete anchors rated for detector weight and seismic loads"
                                )
                            ]
                        ),
                        PanelSection(
                            title="Step 2: Wire Connections",
                            content="Connect field wiring to detector terminals",
                            subsections=[
                                PanelSection(
                                    title="Strip Wire Insulation",
                                    content="Strip 1/4 inch of insulation from each conductor"
                                ),
                                PanelSection(
                                    title="Terminal Connections",
                                    content="Insert conductors fully into terminals and tighten screws"
                                )
                            ]
                        ),
                        PanelSection(
                            title="Step 3: Install Detector",
                            content="Attach detector to base and verify operation",
                            icon="🔧"
                        )
                    ]
                ),
                PanelSection(
                    title="Testing and Commissioning",
                    content="Verify proper operation and document results",
                    subsections=[
                        PanelSection(
                            title="Initial Testing",
                            content="Use calibrated smoke source or detector tester",
                            tags=["testing", "commissioning"]
                        ),
                        PanelSection(
                            title="Documentation",
                            content="Record test results and device information",
                            tags=["documentation", "records"]
                        )
                    ]
                )
            ],
            keywords=["installation", "smoke detector", "mounting", "wiring"],
            source="AutoFire Installation Guide"
        )
        
        self.panels[device_panel.id] = device_panel
        self.panels[nfpa_panel.id] = nfpa_panel
        self.panels[install_panel.id] = install_panel
    
    def get_panel(self, panel_id: str) -> Optional[InformationPanel]:
        """Get a specific information panel."""
        return self.panels.get(panel_id)
    
    def search_panels(self, query: str) -> List[InformationPanel]:
        """Search panels by keywords and content."""
        query_lower = query.lower()
        results = []
        
        for panel in self.panels.values():
            # Check title
            if query_lower in panel.title.lower():
                results.append(panel)
                continue
                
            # Check keywords
            if panel.keywords and any(query_lower in keyword.lower() for keyword in panel.keywords):
                results.append(panel)
                continue
                
            # Check section content
            if self._search_sections(panel.sections, query_lower):
                results.append(panel)
        
        return results
    
    def _search_sections(self, sections: List[PanelSection], query: str) -> bool:
        """Recursively search section content."""
        for section in sections:
            if (query in section.title.lower() or 
                query in section.content.lower() or
                (section.tags and any(query in tag.lower() for tag in section.tags))):
                return True
            if section.subsections and self._search_sections(section.subsections, query):
                return True
        return False

class ExpandableSectionWidget(QFrame):
    """Widget for displaying an expandable section with subsections."""
    
    def __init__(self, section: PanelSection, level: int = 0, parent=None):
        super().__init__(parent)
        self.section = section
        self.level = level
        self.subsection_widgets = []
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {AutoFireColor.SURFACE};
                border: 1px solid {AutoFireColor.BORDER};
                border-radius: 4px;
                margin: 2px;
                padding: 4px;
            }}
        """)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the section UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(self.level * 20, 5, 5, 5)
        
        # Header with expand/collapse button
        header_layout = QHBoxLayout()
        
        # Expand/collapse button
        self.expand_btn = QPushButton()
        self.expand_btn.setFixedSize(20, 20)
        self.expand_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AutoFireColor.PRIMARY};
                border: none;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {AutoFireColor.ACCENT};
            }}
        """)
        self.expand_btn.clicked.connect(self._toggle_expanded)
        
        # Icon if available
        if self.section.icon:
            icon_label = QLabel(self.section.icon)
            icon_label.setStyleSheet(f"font-size: 16px; margin-right: 5px;")
            header_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(self.section.title)
        title_label.setStyleSheet(f"""
            font-family: {AutoFireFont.FAMILY};
            font-size: {AutoFireFont.SIZE_LARGE}px;
            font-weight: bold;
            color: {AutoFireColor.TEXT_PRIMARY};
            margin-left: 5px;
        """)
        
        header_layout.addWidget(self.expand_btn)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Tags
        if self.section.tags:
            tags_layout = QHBoxLayout()
            for tag in self.section.tags:
                tag_label = QLabel(tag)
                tag_label.setStyleSheet(f"""
                    background-color: {AutoFireColor.ACCENT};
                    color: white;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-size: {AutoFireFont.SIZE_SMALL}px;
                    margin-right: 5px;
                """)
                tags_layout.addWidget(tag_label)
            tags_layout.addStretch()
            header_layout.addLayout(tags_layout)
        
        layout.addLayout(header_layout)
        
        # Content area
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        
        # Main content
        content_label = QLabel(self.section.content)
        content_label.setWordWrap(True)
        content_label.setStyleSheet(f"""
            color: {AutoFireColor.TEXT_SECONDARY};
            font-family: {AutoFireFont.FAMILY};
            font-size: {AutoFireFont.SIZE_NORMAL}px;
            margin: 5px 0px;
            padding: 5px;
            background-color: {AutoFireColor.BACKGROUND};
            border-radius: 3px;
        """)
        content_layout.addWidget(content_label)
        
        # Links
        if self.section.links:
            links_widget = QWidget()
            links_layout = QVBoxLayout(links_widget)
            links_layout.setContentsMargins(0, 0, 0, 0)
            
            links_title = QLabel("Related Links:")
            links_title.setStyleSheet(f"""
                font-weight: bold;
                color: {AutoFireColor.TEXT_PRIMARY};
                margin-top: 10px;
            """)
            links_layout.addWidget(links_title)
            
            for link in self.section.links:
                link_btn = QPushButton(link['title'])
                link_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: 1px solid {AutoFireColor.ACCENT};
                        color: {AutoFireColor.ACCENT};
                        padding: 5px 10px;
                        border-radius: 3px;
                        text-align: left;
                        margin: 2px 0px;
                    }}
                    QPushButton:hover {{
                        background-color: {AutoFireColor.ACCENT};
                        color: white;
                    }}
                """)
                link_btn.clicked.connect(lambda checked, url=link['url']: webbrowser.open(url))
                links_layout.addWidget(link_btn)
            
            content_layout.addWidget(links_widget)
        
        # Subsections
        if self.section.subsections:
            for subsection in self.section.subsections:
                subsection_widget = ExpandableSectionWidget(subsection, self.level + 1)
                self.subsection_widgets.append(subsection_widget)
                content_layout.addWidget(subsection_widget)
        
        layout.addWidget(self.content_widget)
        
        # Set initial state
        self._update_expand_button()
        self.content_widget.setVisible(self.section.expanded)
    
    def _toggle_expanded(self):
        """Toggle the expanded state of this section."""
        self.section.expanded = not self.section.expanded
        self.content_widget.setVisible(self.section.expanded)
        self._update_expand_button()
    
    def _update_expand_button(self):
        """Update the expand/collapse button appearance."""
        if self.section.subsections or self.section.links:
            self.expand_btn.setText("−" if self.section.expanded else "+")
            self.expand_btn.setVisible(True)
        else:
            self.expand_btn.setVisible(False)

class InformationPanelWidget(QWidget):
    """Main widget for displaying an information panel."""
    
    def __init__(self, panel: InformationPanel, parent=None):
        super().__init__(parent)
        self.panel = panel
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the panel UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header_widget = QFrame()
        header_widget.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {AutoFireColor.PRIMARY}, stop:1 {AutoFireColor.ACCENT});
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
            }}
        """)
        
        header_layout = QVBoxLayout(header_widget)
        
        # Title
        title_label = QLabel(self.panel.title)
        title_label.setStyleSheet(f"""
            font-family: {AutoFireFont.FAMILY};
            font-size: {AutoFireFont.SIZE_TITLE}px;
            font-weight: bold;
            color: white;
        """)
        header_layout.addWidget(title_label)
        
        # Metadata
        metadata_layout = QHBoxLayout()
        
        type_label = QLabel(f"Type: {self.panel.panel_type.value.replace('_', ' ').title()}")
        type_label.setStyleSheet("color: white; font-size: 10px;")
        metadata_layout.addWidget(type_label)
        
        if self.panel.source:
            source_label = QLabel(f"Source: {self.panel.source}")
            source_label.setStyleSheet("color: white; font-size: 10px;")
            metadata_layout.addWidget(source_label)
        
        metadata_layout.addStretch()
        
        updated_label = QLabel(f"Updated: {self.panel.last_updated[:10]}")
        updated_label.setStyleSheet("color: white; font-size: 10px;")
        metadata_layout.addWidget(updated_label)
        
        header_layout.addLayout(metadata_layout)
        layout.addWidget(header_widget)
        
        # Search within panel
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search within this panel...")
        search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {AutoFireColor.BORDER};
                border-radius: 4px;
                background-color: {AutoFireColor.SURFACE};
                color: {AutoFireColor.TEXT_PRIMARY};
                font-size: {AutoFireFont.SIZE_NORMAL}px;
            }}
            QLineEdit:focus {{
                border-color: {AutoFireColor.PRIMARY};
            }}
        """)
        search_input.textChanged.connect(self._filter_sections)
        
        expand_all_btn = QPushButton("Expand All")
        expand_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AutoFireColor.ACCENT};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {AutoFireColor.PRIMARY};
            }}
        """)
        expand_all_btn.clicked.connect(self._expand_all_sections)
        
        collapse_all_btn = QPushButton("Collapse All")
        collapse_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AutoFireColor.SECONDARY};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {AutoFireColor.BORDER};
            }}
        """)
        collapse_all_btn.clicked.connect(self._collapse_all_sections)
        
        search_layout.addWidget(search_input)
        search_layout.addWidget(expand_all_btn)
        search_layout.addWidget(collapse_all_btn)
        layout.addLayout(search_layout)
        
        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {AutoFireColor.BACKGROUND};
            }}
            QScrollBar:vertical {{
                background-color: {AutoFireColor.SURFACE};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {AutoFireColor.BORDER};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {AutoFireColor.ACCENT};
            }}
        """)
        
        # Content widget
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(5)
        
        # Create section widgets
        self.section_widgets = []
        for section in self.panel.sections:
            section_widget = ExpandableSectionWidget(section)
            self.section_widgets.append(section_widget)
            self.content_layout.addWidget(section_widget)
        
        self.content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Store search input for filtering
        self.search_input = search_input
    
    def _filter_sections(self, query: str):
        """Filter visible sections based on search query."""
        query_lower = query.lower()
        
        for widget in self.section_widgets:
            visible = self._section_matches_query(widget.section, query_lower)
            widget.setVisible(visible)
    
    def _section_matches_query(self, section: PanelSection, query: str) -> bool:
        """Check if a section matches the search query."""
        if not query:
            return True
            
        matches_basic = (query in section.title.lower() or
                        query in section.content.lower())
        
        matches_tags = bool(section.tags and any(query in tag.lower() for tag in section.tags))
        
        matches_subsections = bool(section.subsections and 
                                  any(self._section_matches_query(subsection, query) 
                                      for subsection in section.subsections))
        
        return bool(matches_basic or matches_tags or matches_subsections)
    
    def _expand_all_sections(self):
        """Expand all sections."""
        self._set_all_sections_expanded(True)
    
    def _collapse_all_sections(self):
        """Collapse all sections."""
        self._set_all_sections_expanded(False)
    
    def _set_all_sections_expanded(self, expanded: bool):
        """Recursively set all sections expanded/collapsed."""
        def set_section_expanded(section: PanelSection):
            section.expanded = expanded
            if section.subsections:
                for subsection in section.subsections:
                    set_section_expanded(subsection)
        
        for section in self.panel.sections:
            set_section_expanded(section)
        
        # Update UI
        for widget in self.section_widgets:
            self._update_widget_expansion(widget)
    
    def _update_widget_expansion(self, widget: ExpandableSectionWidget):
        """Recursively update widget expansion state."""
        widget.content_widget.setVisible(widget.section.expanded)
        widget._update_expand_button()
        
        for subsection_widget in widget.subsection_widgets:
            self._update_widget_expansion(subsection_widget)

class InformationPanelDemo(QMainWindow):
    """Demo application for the Information Panel System."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoFire Information Panel System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply professional styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {AutoFireColor.BACKGROUND};
                color: {AutoFireColor.TEXT_PRIMARY};
            }}
        """)
        
        self.database = InformationDatabase()
        self._setup_ui()
        
        # Load initial panel
        first_panel = list(self.database.panels.values())[0]
        self._show_panel(first_panel)
        
        print("🔍 AutoFire Information Panel System initialized")
        print(f"📚 Loaded {len(self.database.panels)} information panels")
    
    def _setup_ui(self):
        """Set up the main UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # Left sidebar - panel list
        sidebar = QFrame()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {AutoFireColor.SURFACE};
                border-right: 2px solid {AutoFireColor.BORDER};
            }}
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Sidebar header
        sidebar_title = QLabel("Information Panels")
        sidebar_title.setStyleSheet(f"""
            font-family: {AutoFireFont.FAMILY};
            font-size: {AutoFireFont.SIZE_HEADING}px;
            font-weight: bold;
            color: {AutoFireColor.PRIMARY};
            padding: 10px;
            border-bottom: 1px solid {AutoFireColor.BORDER};
        """)
        sidebar_layout.addWidget(sidebar_title)
        
        # Search panels
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search panels...")
        search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {AutoFireColor.BORDER};
                border-radius: 4px;
                background-color: {AutoFireColor.BACKGROUND};
                color: {AutoFireColor.TEXT_PRIMARY};
                margin: 10px;
            }}
            QLineEdit:focus {{
                border-color: {AutoFireColor.PRIMARY};
            }}
        """)
        search_input.textChanged.connect(self._filter_panel_list)
        sidebar_layout.addWidget(search_input)
        
        # Panel list
        self.panel_list = QListWidget()
        self.panel_list.setStyleSheet(f"""
            QListWidget {{
                border: none;
                background-color: transparent;
                outline: none;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {AutoFireColor.BORDER};
                color: {AutoFireColor.TEXT_PRIMARY};
            }}
            QListWidget::item:selected {{
                background-color: {AutoFireColor.PRIMARY};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {AutoFireColor.ACCENT};
                color: white;
            }}
        """)
        
        # Populate panel list
        for panel in self.database.panels.values():
            item = QListWidgetItem(panel.title)
            item.setData(Qt.ItemDataRole.UserRole, panel.id)
            self.panel_list.addItem(item)
        
        self.panel_list.itemClicked.connect(self._on_panel_selected)
        sidebar_layout.addWidget(self.panel_list)
        
        layout.addWidget(sidebar)
        
        # Main content area
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {AutoFireColor.BACKGROUND};
            }}
        """)
        
        layout.addWidget(self.content_area)
        
        # Store search input
        self.search_input = search_input
    
    def _filter_panel_list(self, query: str):
        """Filter the panel list based on search query."""
        for i in range(self.panel_list.count()):
            item = self.panel_list.item(i)
            panel_id = item.data(Qt.ItemDataRole.UserRole)
            panel = self.database.get_panel(panel_id)
            
            if panel and (query.lower() in panel.title.lower() or 
                         (panel.keywords and any(query.lower() in keyword.lower() for keyword in panel.keywords))):
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def _on_panel_selected(self, item):
        """Handle panel selection."""
        panel_id = item.data(Qt.ItemDataRole.UserRole)
        panel = self.database.get_panel(panel_id)
        if panel:
            self._show_panel(panel)
    
    def _show_panel(self, panel: InformationPanel):
        """Display the selected panel."""
        # Remove existing panel widgets
        while self.content_area.count() > 0:
            widget = self.content_area.widget(0)
            self.content_area.removeWidget(widget)
            widget.deleteLater()
        
        # Create and add new panel widget
        panel_widget = InformationPanelWidget(panel)
        self.content_area.addWidget(panel_widget)
        self.content_area.setCurrentWidget(panel_widget)

def main():
    """Run the Information Panel System demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("AutoFire Information Panel System")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("AutoFire")
    
    # Create and show demo
    demo = InformationPanelDemo()
    demo.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())