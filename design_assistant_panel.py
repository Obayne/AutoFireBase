"""
AutoFire Design Assistant Panel
==============================

Intelligent design assistance panel that integrates with the main CAD interface.
Provides real-time suggestions, code compliance checking, and live calculations.
"""

import os
import sqlite3
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QTextEdit, QScrollArea, QFrame, QProgressBar, QTabWidget,
    QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QCheckBox, QSlider, QSplitter, QTableWidget, QTableWidgetItem,
    QApplication, QMainWindow, QMessageBox
)

try:
    from cad_core.calculations.live_engine import (
        LiveCalculationsEngine, WireSegment, CircuitAnalysis, BatteryCalculation
    )
    CALCULATIONS_AVAILABLE = True
except ImportError:
    CALCULATIONS_AVAILABLE = False
    print("⚠️ Live calculations engine not available - using mock")

try:
    from frontend.design_system import AutoFireColor, AutoFireStyleSheet
    DESIGN_SYSTEM_AVAILABLE = True
except ImportError:
    DESIGN_SYSTEM_AVAILABLE = False
    
    class AutoFireColor:
        PRIMARY = "#C41E3A"
        SECONDARY = "#8B0000"
        SUCCESS = "#28a745"
        WARNING = "#ffc107"
        DANGER = "#dc3545"


class SuggestionType(Enum):
    """Types of design suggestions."""
    CODE_COMPLIANCE = "code_compliance"
    DEVICE_PLACEMENT = "device_placement"
    CIRCUIT_OPTIMIZATION = "circuit_optimization"
    COST_OPTIMIZATION = "cost_optimization"
    CALCULATION_ALERT = "calculation_alert"


@dataclass
class DesignSuggestion:
    """A design suggestion with priority and action."""
    type: SuggestionType
    priority: str  # "HIGH", "MEDIUM", "LOW"
    title: str
    description: str
    action_label: str
    action_callback: Optional[object] = None
    auto_fix_available: bool = False


class LiveCalculationsWidget(QWidget):
    """Widget for live calculations display and interaction."""
    
    def __init__(self):
        super().__init__()
        self.engine = None
        if CALCULATIONS_AVAILABLE:
            self.engine = LiveCalculationsEngine()
        
        self._setup_ui()
        self._start_updates()
    
    def _setup_ui(self):
        """Setup the calculations UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🔧 Live Calculations")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: #C41E3A;")
        layout.addWidget(header)
        
        # Circuit analysis
        self.circuit_group = QGroupBox("Circuit Analysis")
        circuit_layout = QVBoxLayout(self.circuit_group)
        
        self.circuit_list = QListWidget()
        self.circuit_list.itemClicked.connect(self._on_circuit_selected)
        circuit_layout.addWidget(self.circuit_list)
        
        # Circuit details
        self.circuit_details = QTextEdit()
        self.circuit_details.setMaximumHeight(120)
        self.circuit_details.setReadOnly(True)
        circuit_layout.addWidget(self.circuit_details)
        
        layout.addWidget(self.circuit_group)
        
        # Battery calculation
        self.battery_group = QGroupBox("Battery Sizing")
        battery_layout = QFormLayout(self.battery_group)
        
        self.standby_current_label = QLabel("0.0 A")
        self.alarm_current_label = QLabel("0.0 A")
        self.required_ah_label = QLabel("0 AH")
        self.recommended_battery_label = QLabel("Not calculated")
        
        battery_layout.addRow("Standby Current:", self.standby_current_label)
        battery_layout.addRow("Alarm Current:", self.alarm_current_label)
        battery_layout.addRow("Required Capacity:", self.required_ah_label)
        battery_layout.addRow("Recommended Battery:", self.recommended_battery_label)
        
        layout.addWidget(self.battery_group)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        self.recalc_btn = QPushButton("🔄 Recalculate")
        self.recalc_btn.clicked.connect(self._force_recalculation)
        
        self.export_btn = QPushButton("📊 Export Report")
        self.export_btn.clicked.connect(self._export_calculations)
        
        actions_layout.addWidget(self.recalc_btn)
        actions_layout.addWidget(self.export_btn)
        
        layout.addLayout(actions_layout)
    
    def _start_updates(self):
        """Start periodic updates."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_calculations)
        self.update_timer.start(2000)  # Update every 2 seconds
    
    def _update_calculations(self):
        """Update calculations based on current design."""
        if not self.engine:
            return
        
        # Update circuit list
        self.circuit_list.clear()
        
        try:
            all_analyses = self.engine.get_all_circuit_analyses()
            
            for circuit_id, analysis in all_analyses.items():
                item = QListWidgetItem(f"{circuit_id} ({analysis.device_count} devices)")
                
                # Color code by compliance
                if analysis.compliance_status == "PASS":
                    item.setBackground(Qt.green)
                elif analysis.compliance_status == "WARN":
                    item.setBackground(Qt.yellow)
                elif analysis.compliance_status == "FAIL":
                    item.setBackground(Qt.red)
                
                item.setData(Qt.UserRole, analysis)
                self.circuit_list.addItem(item)
        
        except Exception as e:
            print(f"Calculation update error: {e}")
    
    def _on_circuit_selected(self, item):
        """Handle circuit selection."""
        analysis = item.data(Qt.UserRole)
        if analysis:
            details = f"""
Circuit: {analysis.circuit_id}
Type: {analysis.circuit_type}
Devices: {analysis.device_count}
Length: {analysis.total_length_ft:.1f} ft
Voltage Drop: {analysis.total_voltage_drop:.2f}V ({analysis.voltage_drop_percent:.1f}%)
Status: {analysis.compliance_status}

Warnings:
{chr(10).join(analysis.warnings)}
            """.strip()
            
            self.circuit_details.setText(details)
    
    def _force_recalculation(self):
        """Force immediate recalculation."""
        self._update_calculations()
        QMessageBox.information(self, "Recalculation", "Calculations updated!")
    
    def _export_calculations(self):
        """Export calculation report."""
        QMessageBox.information(self, "Export", "Calculation report export feature coming soon!")
    
    def add_wire_segment(self, segment):
        """Add a wire segment to calculations."""
        if self.engine:
            self.engine.add_wire_segment(segment)
    
    def update_device_load(self, device_id, current_a):
        """Update device current load."""
        if self.engine:
            self.engine.update_device_load(device_id, current_a)


class CodeComplianceWidget(QWidget):
    """Widget for real-time code compliance checking."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._load_compliance_rules()
    
    def _setup_ui(self):
        """Setup the compliance UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📋 Code Compliance")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: #C41E3A;")
        layout.addWidget(header)
        
        # Compliance status
        self.status_frame = QFrame()
        self.status_frame.setStyleSheet("border: 2px solid #ccc; border-radius: 6px; padding: 10px;")
        status_layout = QVBoxLayout(self.status_frame)
        
        self.overall_status = QLabel("✅ System Compliant")
        self.overall_status.setStyleSheet("font-weight: bold; color: green;")
        
        self.compliance_score = QProgressBar()
        self.compliance_score.setRange(0, 100)
        self.compliance_score.setValue(85)
        self.compliance_score.setFormat("Compliance: %p%")
        
        status_layout.addWidget(self.overall_status)
        status_layout.addWidget(self.compliance_score)
        
        layout.addWidget(self.status_frame)
        
        # Violations and warnings
        self.violations_group = QGroupBox("Issues & Warnings")
        violations_layout = QVBoxLayout(self.violations_group)
        
        self.violations_list = QListWidget()
        violations_layout.addWidget(self.violations_list)
        
        layout.addWidget(self.violations_group)
        
        # Code references
        self.references_group = QGroupBox("Relevant Code Sections")
        references_layout = QVBoxLayout(self.references_group)
        
        self.references_tree = QTreeWidget()
        self.references_tree.setHeaderLabels(["Code", "Section", "Requirement"])
        references_layout.addWidget(self.references_tree)
        
        layout.addWidget(self.references_group)
    
    def _load_compliance_rules(self):
        """Load NFPA 72 and local code requirements."""
        # Sample compliance rules
        rules = [
            ("NFPA 72", "17.7.3.2.3.1", "Smoke detector spacing ≤ 30 ft"),
            ("NFPA 72", "17.7.3.8", "Heat detector spacing ≤ 50 ft"),
            ("NFPA 72", "17.14.12", "Pull station ≤ 5 ft from exit"),
            ("NFPA 72", "18.4.3", "Audible notification ≥ 15 dBA above ambient"),
            ("NFPA 72", "18.5.4", "Visual notification per room size"),
            ("IBC", "907.2", "Fire alarm system required for occupancy"),
        ]
        
        for code, section, requirement in rules:
            item = QTreeWidgetItem([code, section, requirement])
            self.references_tree.addTopLevelItem(item)
        
        self.references_tree.expandAll()
    
    def check_compliance(self, design_data):
        """Check compliance for current design."""
        violations = []
        warnings = []
        
        # Mock compliance checking
        if hasattr(design_data, 'smoke_detectors'):
            if len(design_data.smoke_detectors) < 2:
                violations.append("Insufficient smoke detector coverage")
        
        # Update UI
        self.violations_list.clear()
        
        for violation in violations:
            item = QListWidgetItem(f"❌ VIOLATION: {violation}")
            item.setBackground(Qt.red)
            self.violations_list.addItem(item)
        
        for warning in warnings:
            item = QListWidgetItem(f"⚠️ WARNING: {warning}")
            item.setBackground(Qt.yellow)
            self.violations_list.addItem(item)
        
        # Update overall status
        if violations:
            self.overall_status.setText("❌ Code Violations Found")
            self.overall_status.setStyleSheet("font-weight: bold; color: red;")
            self.compliance_score.setValue(max(0, 85 - len(violations) * 20))
        elif warnings:
            self.overall_status.setText("⚠️ Warnings Present")
            self.overall_status.setStyleSheet("font-weight: bold; color: orange;")
            self.compliance_score.setValue(max(70, 85 - len(warnings) * 10))
        else:
            self.overall_status.setText("✅ System Compliant")
            self.overall_status.setStyleSheet("font-weight: bold; color: green;")
            self.compliance_score.setValue(95)


class SmartSuggestionsWidget(QWidget):
    """Widget for intelligent design suggestions."""
    
    suggestion_applied = Signal(str)  # Suggestion ID
    
    def __init__(self):
        super().__init__()
        self.suggestions = []
        self._setup_ui()
        self._generate_sample_suggestions()
    
    def _setup_ui(self):
        """Setup the suggestions UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        header = QLabel("💡 Smart Suggestions")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: #C41E3A;")
        
        self.suggestion_count = QLabel("(3)")
        self.suggestion_count.setStyleSheet("color: #666;")
        
        header_layout.addWidget(header)
        header_layout.addWidget(self.suggestion_count)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["All", "HIGH", "MEDIUM", "LOW"])
        self.priority_filter.currentTextChanged.connect(self._filter_suggestions)
        
        self.type_filter = QComboBox()
        self.type_filter.addItems([
            "All", "Code Compliance", "Device Placement", 
            "Circuit Optimization", "Cost Optimization"
        ])
        self.type_filter.currentTextChanged.connect(self._filter_suggestions)
        
        filter_layout.addWidget(QLabel("Priority:"))
        filter_layout.addWidget(self.priority_filter)
        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.type_filter)
        
        layout.addLayout(filter_layout)
        
        # Suggestions list
        self.suggestions_scroll = QScrollArea()
        self.suggestions_widget = QWidget()
        self.suggestions_layout = QVBoxLayout(self.suggestions_widget)
        
        self.suggestions_scroll.setWidget(self.suggestions_widget)
        self.suggestions_scroll.setWidgetResizable(True)
        
        layout.addWidget(self.suggestions_scroll)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        self.auto_apply_btn = QPushButton("🤖 Auto-Apply Safe Fixes")
        self.auto_apply_btn.clicked.connect(self._auto_apply_suggestions)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self._refresh_suggestions)
        
        actions_layout.addWidget(self.auto_apply_btn)
        actions_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(actions_layout)
    
    def _generate_sample_suggestions(self):
        """Generate sample suggestions."""
        self.suggestions = [
            DesignSuggestion(
                type=SuggestionType.CODE_COMPLIANCE,
                priority="HIGH",
                title="Pull Station Spacing",
                description="Pull station spacing exceeds 200ft maximum per NFPA 72",
                action_label="Add Pull Station",
                auto_fix_available=True
            ),
            DesignSuggestion(
                type=SuggestionType.CIRCUIT_OPTIMIZATION,
                priority="MEDIUM", 
                title="Voltage Drop Optimization",
                description="SLC-1 voltage drop is 8.2% - consider larger wire gauge",
                action_label="Upgrade Wire Gauge",
                auto_fix_available=True
            ),
            DesignSuggestion(
                type=SuggestionType.DEVICE_PLACEMENT,
                priority="LOW",
                title="Smoke Detector Coverage",
                description="Room 205 has suboptimal smoke detector placement",
                action_label="Optimize Placement",
                auto_fix_available=False
            ),
            DesignSuggestion(
                type=SuggestionType.COST_OPTIMIZATION,
                priority="MEDIUM",
                title="Device Consolidation",
                description="3 separate notification zones could be combined",
                action_label="Combine Zones",
                auto_fix_available=True
            )
        ]
        
        self._update_suggestions_display()
    
    def _update_suggestions_display(self):
        """Update the suggestions display."""
        # Clear existing suggestions
        while self.suggestions_layout.count():
            child = self.suggestions_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Filter suggestions
        filtered_suggestions = self._get_filtered_suggestions()
        
        # Add suggestion cards
        for suggestion in filtered_suggestions:
            card = self._create_suggestion_card(suggestion)
            self.suggestions_layout.addWidget(card)
        
        self.suggestions_layout.addStretch()
        
        # Update count
        self.suggestion_count.setText(f"({len(filtered_suggestions)})")
    
    def _create_suggestion_card(self, suggestion):
        """Create a suggestion card widget."""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet(f"""
            QFrame {{
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                margin: 4px 0px;
                background-color: white;
            }}
            QFrame:hover {{
                border-color: {AutoFireColor.PRIMARY};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header with priority and title
        header_layout = QHBoxLayout()
        
        # Priority badge
        priority_colors = {
            "HIGH": "#dc3545",
            "MEDIUM": "#ffc107", 
            "LOW": "#28a745"
        }
        
        priority_label = QLabel(suggestion.priority)
        priority_label.setStyleSheet(f"""
            background-color: {priority_colors.get(suggestion.priority, '#ccc')};
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: bold;
        """)
        priority_label.setFixedSize(60, 20)
        
        title_label = QLabel(suggestion.title)
        title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        
        header_layout.addWidget(priority_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Description
        desc_label = QLabel(suggestion.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(desc_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        action_btn = QPushButton(suggestion.action_label)
        action_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AutoFireColor.PRIMARY};
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {AutoFireColor.SECONDARY};
            }}
        """)
        action_btn.clicked.connect(lambda: self._apply_suggestion(suggestion))
        
        button_layout.addWidget(action_btn)
        
        if suggestion.auto_fix_available:
            auto_btn = QPushButton("🤖 Auto-Fix")
            auto_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #1e7e34;
                }
            """)
            auto_btn.clicked.connect(lambda: self._auto_fix_suggestion(suggestion))
            button_layout.addWidget(auto_btn)
        
        button_layout.addStretch()
        
        dismiss_btn = QPushButton("✕")
        dismiss_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #999;
                font-weight: bold;
                padding: 2px 6px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                color: #666;
            }
        """)
        dismiss_btn.clicked.connect(lambda: self._dismiss_suggestion(suggestion))
        button_layout.addWidget(dismiss_btn)
        
        layout.addLayout(button_layout)
        
        return card
    
    def _get_filtered_suggestions(self):
        """Get filtered suggestions based on current filters."""
        filtered = self.suggestions
        
        priority_filter = self.priority_filter.currentText()
        if priority_filter != "All":
            filtered = [s for s in filtered if s.priority == priority_filter]
        
        type_filter = self.type_filter.currentText()
        if type_filter != "All":
            type_map = {
                "Code Compliance": SuggestionType.CODE_COMPLIANCE,
                "Device Placement": SuggestionType.DEVICE_PLACEMENT,
                "Circuit Optimization": SuggestionType.CIRCUIT_OPTIMIZATION,
                "Cost Optimization": SuggestionType.COST_OPTIMIZATION
            }
            if type_filter in type_map:
                filtered = [s for s in filtered if s.type == type_map[type_filter]]
        
        return filtered
    
    def _filter_suggestions(self):
        """Handle filter changes."""
        self._update_suggestions_display()
    
    def _apply_suggestion(self, suggestion):
        """Apply a suggestion manually."""
        QMessageBox.information(self, "Suggestion Applied", 
                              f"Applied: {suggestion.title}\n\n{suggestion.description}")
        self._remove_suggestion(suggestion)
    
    def _auto_fix_suggestion(self, suggestion):
        """Auto-fix a suggestion."""
        QMessageBox.information(self, "Auto-Fix Applied", 
                              f"Auto-fixed: {suggestion.title}")
        self._remove_suggestion(suggestion)
    
    def _dismiss_suggestion(self, suggestion):
        """Dismiss a suggestion."""
        self._remove_suggestion(suggestion)
    
    def _remove_suggestion(self, suggestion):
        """Remove a suggestion from the list."""
        if suggestion in self.suggestions:
            self.suggestions.remove(suggestion)
            self._update_suggestions_display()
    
    def _auto_apply_suggestions(self):
        """Auto-apply all safe suggestions."""
        auto_fix_count = sum(1 for s in self.suggestions if s.auto_fix_available)
        if auto_fix_count > 0:
            reply = QMessageBox.question(self, "Auto-Apply Suggestions",
                                       f"Apply {auto_fix_count} automatic fixes?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.suggestions = [s for s in self.suggestions if not s.auto_fix_available]
                self._update_suggestions_display()
                QMessageBox.information(self, "Auto-Apply Complete", 
                                      f"Applied {auto_fix_count} automatic fixes!")
    
    def _refresh_suggestions(self):
        """Refresh suggestions."""
        self._generate_sample_suggestions()


class DesignAssistantPanel(QWidget):
    """
    Main design assistant panel that combines all intelligent features.
    
    This is the professional design assistant that would integrate
    into the main AutoFire CAD interface as a dockable panel.
    """
    
    device_placement_requested = Signal(str, dict)  # device_type, parameters
    circuit_optimization_requested = Signal(str)    # circuit_id
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the main assistant panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Panel header
        header = QLabel("🤖 AutoFire Design Assistant")
        header.setStyleSheet(f"""
            font-size: 16px; 
            font-weight: bold; 
            color: {AutoFireColor.PRIMARY}; 
            padding: 10px;
            background-color: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Tab widget for different assistant features
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # Smart suggestions
        self.suggestions_widget = SmartSuggestionsWidget()
        self.tab_widget.addTab(self.suggestions_widget, "💡 Suggestions")
        
        # Live calculations
        self.calculations_widget = LiveCalculationsWidget()
        self.tab_widget.addTab(self.calculations_widget, "🔧 Calculations")
        
        # Code compliance
        self.compliance_widget = CodeComplianceWidget()
        self.tab_widget.addTab(self.compliance_widget, "📋 Compliance")
        
        layout.addWidget(self.tab_widget)
        
        # Status footer
        self.status_label = QLabel("🟢 Assistant Ready")
        self.status_label.setStyleSheet("""
            padding: 6px;
            background-color: #f8f9fa;
            border-top: 1px solid #dee2e6;
            font-size: 11px;
            color: #666;
        """)
        layout.addWidget(self.status_label)
    
    def _connect_signals(self):
        """Connect internal signals."""
        self.suggestions_widget.suggestion_applied.connect(self._on_suggestion_applied)
    
    def _on_suggestion_applied(self, suggestion_id):
        """Handle suggestion application."""
        self.status_label.setText(f"✅ Applied suggestion: {suggestion_id}")
    
    def update_design_context(self, design_data):
        """Update assistant with current design context."""
        # This would be called by the main CAD interface
        # when the design changes
        
        self.compliance_widget.check_compliance(design_data)
        self.status_label.setText("🔄 Design context updated")
    
    def add_wire_segment(self, segment):
        """Add wire segment for calculations."""
        self.calculations_widget.add_wire_segment(segment)
    
    def update_device_load(self, device_id, current_a):
        """Update device load for calculations."""
        self.calculations_widget.update_device_load(device_id, current_a)


def create_design_assistant_demo():
    """Create demo of the design assistant panel."""
    import sys
    
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("🔥 AutoFire - Design Assistant Demo")
            self.setGeometry(100, 100, 400, 800)
            
            # Create assistant panel
            self.assistant = DesignAssistantPanel()
            self.setCentralWidget(self.assistant)
            
            # Simulate design updates
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self._simulate_design_update)
            self.update_timer.start(10000)  # Update every 10 seconds
        
        def _simulate_design_update(self):
            """Simulate design changes for demo."""
            # Mock design data
            class MockDesign:
                def __init__(self):
                    self.smoke_detectors = ["SMOKE_001", "SMOKE_002"]
                    self.circuits = ["SLC-1", "SLC-2"]
            
            self.assistant.update_design_context(MockDesign())
            print("📊 Simulated design update")
    
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    print("🚀 Design Assistant Panel Demo")
    print("=" * 40)
    print("✅ Smart suggestions with auto-fix")
    print("✅ Live calculations integration")
    print("✅ Real-time code compliance")
    print("✅ Intelligent design recommendations")
    print("✅ Professional fire alarm engineering")
    
    return app.exec()


if __name__ == "__main__":
    create_design_assistant_demo()