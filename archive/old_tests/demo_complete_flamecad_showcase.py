"""
Complete FlameCAD Professional UI Showcase
Demonstrates the full transformation with all enhanced components working together
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QTabWidget, QPushButton, QLabel, QFrame,
    QGridLayout, QScrollArea, QTextEdit, QGroupBox,
    QSplitter, QDockWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon

# Add the parent directory to the path for importing
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from frontend.design_system import (
        AutoFireColor, AutoFireStyleSheet, AutoFireSpacing, AutoFireTypography
    )
    design_system_available = True
    print("✅ Design System Available: True")
except ImportError as e:
    print(f"❌ Design System Import Error: {e}")
    design_system_available = False


class FlameCADShowcaseMainWindow(QMainWindow):
    """Main showcase window demonstrating complete FlameCAD professional transformation"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlameCAD Professional Suite - Complete Showcase")
        self.setGeometry(100, 100, 1400, 900)
        
        if design_system_available:
            self.setStyleSheet(AutoFireStyleSheet.get_main_window())
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the complete showcase interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(AutoFireSpacing.MD if design_system_available else 8)
        main_layout.setContentsMargins(AutoFireSpacing.MD if design_system_available else 8, 
                                     AutoFireSpacing.MD if design_system_available else 8, 
                                     AutoFireSpacing.MD if design_system_available else 8, 
                                     AutoFireSpacing.MD if design_system_available else 8)
        
        # Create main splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Tool palette and device selection
        self.create_left_panel(splitter)
        
        # Center panel - Main workspace
        self.create_center_panel(splitter)
        
        # Right panel - Properties and settings
        self.create_right_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([300, 700, 300])
        
        # Create status bar
        self.create_status_bar()
    
    def create_left_panel(self, parent):
        """Create left tool palette panel"""
        left_widget = QWidget()
        if design_system_available:
            left_widget.setStyleSheet(AutoFireStyleSheet.get_panel())
        
        layout = QVBoxLayout(left_widget)
        layout.setSpacing(AutoFireSpacing.MD if design_system_available else 8)
        
        # Title
        title = QLabel("FlameCAD Tools")
        if design_system_available:
            title.setStyleSheet(AutoFireStyleSheet.get_heading())
            title.setFont(AutoFireTypography.get_heading_font())
        layout.addWidget(title)
        
        # Device Palette Section
        device_group = QGroupBox("Device Palette")
        if design_system_available:
            device_group.setStyleSheet(AutoFireStyleSheet.get_group_box())
        device_layout = QVBoxLayout(device_group)
        
        # Circuit color indicators
        circuit_frame = QFrame()
        circuit_layout = QGridLayout(circuit_frame)
        
        circuits = [
            ("SLC Devices", AutoFireColor.CIRCUIT_SLC if design_system_available else "#DC3545"),
            ("NAC Devices", AutoFireColor.CIRCUIT_NAC if design_system_available else "#FFC107"),
            ("Power Devices", AutoFireColor.CIRCUIT_POWER if design_system_available else "#FF6B35")
        ]
        
        for i, (label, color) in enumerate(circuits):
            indicator = QLabel("●")
            indicator.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")
            circuit_layout.addWidget(indicator, i, 0)
            
            label_widget = QLabel(label)
            if design_system_available:
                label_widget.setStyleSheet(AutoFireStyleSheet.get_label())
            circuit_layout.addWidget(label_widget, i, 1)
        
        device_layout.addWidget(circuit_frame)
        
        # Device selection button
        select_devices_btn = QPushButton("Select from Database")
        if design_system_available:
            select_devices_btn.setStyleSheet(AutoFireStyleSheet.get_primary_button())
        device_layout.addWidget(select_devices_btn)
        
        layout.addWidget(device_group)
        
        # System Builder Section
        system_group = QGroupBox("System Builder")
        if design_system_available:
            system_group.setStyleSheet(AutoFireStyleSheet.get_group_box())
        system_layout = QVBoxLayout(system_group)
        
        system_buttons = [
            "Enhanced Panel Config",
            "Expansion Boards",
            "Zone Planning",
            "Circuit Analysis"
        ]
        
        for btn_text in system_buttons:
            btn = QPushButton(btn_text)
            if design_system_available:
                btn.setStyleSheet(AutoFireStyleSheet.get_secondary_button())
            system_layout.addWidget(btn)
        
        layout.addWidget(system_group)
        
        layout.addStretch()
        parent.addWidget(left_widget)
    
    def create_center_panel(self, parent):
        """Create center workspace panel"""
        center_widget = QWidget()
        if design_system_available:
            center_widget.setStyleSheet(AutoFireStyleSheet.get_canvas())
        
        layout = QVBoxLayout(center_widget)
        layout.setSpacing(AutoFireSpacing.SM if design_system_available else 4)
        
        # Toolbar
        toolbar_frame = QFrame()
        if design_system_available:
            toolbar_frame.setStyleSheet(AutoFireStyleSheet.get_toolbar())
        toolbar_layout = QHBoxLayout(toolbar_frame)
        
        toolbar_buttons = [
            "New Project", "Open", "Save", "Export DXF", 
            "Zoom In", "Zoom Out", "Pan", "Select"
        ]
        
        for btn_text in toolbar_buttons:
            btn = QPushButton(btn_text)
            if design_system_available:
                btn.setStyleSheet(AutoFireStyleSheet.get_tool_button())
            toolbar_layout.addWidget(btn)
        
        toolbar_layout.addStretch()
        layout.addWidget(toolbar_frame)
        
        # Main canvas area
        canvas_label = QLabel("FlameCAD Professional Workspace\n\nFire Alarm System Design Canvas")
        canvas_label.setAlignment(Qt.AlignCenter)
        if design_system_available:
            canvas_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {AutoFireColor.CANVAS_BG};
                    color: {AutoFireColor.TEXT_PRIMARY};
                    border: 2px dashed {AutoFireColor.ACCENT};
                    border-radius: 8px;
                    font-size: 18px;
                    padding: 40px;
                }}
            """)
        canvas_label.setMinimumHeight(400)
        layout.addWidget(canvas_label)
        
        parent.addWidget(center_widget)
    
    def create_right_panel(self, parent):
        """Create right properties panel"""
        right_widget = QWidget()
        if design_system_available:
            right_widget.setStyleSheet(AutoFireStyleSheet.get_panel())
        
        layout = QVBoxLayout(right_widget)
        layout.setSpacing(AutoFireSpacing.MD if design_system_available else 8)
        
        # Title
        title = QLabel("Properties & Settings")
        if design_system_available:
            title.setStyleSheet(AutoFireStyleSheet.get_heading())
            title.setFont(AutoFireTypography.get_heading_font())
        layout.addWidget(title)
        
        # Tabbed interface
        tab_widget = QTabWidget()
        if design_system_available:
            tab_widget.setStyleSheet(AutoFireStyleSheet.get_tab_widget())
        
        # Properties tab
        props_widget = QWidget()
        props_layout = QVBoxLayout(props_widget)
        
        props_text = QTextEdit()
        props_text.setPlainText("""
Selected Device Properties:

Device Type: Smoke Detector
Manufacturer: System Sensor
Model: 2451
Circuit: SLC
Address: 15
Zone: Office Area
Installation: Surface Mount

NFPA 72 Compliance: ✅
UL Listed: ✅
Spacing: 30' x 30' max
Response Time: < 20 seconds
        """)
        if design_system_available:
            props_text.setStyleSheet(AutoFireStyleSheet.get_text_edit())
        props_layout.addWidget(props_text)
        
        tab_widget.addTab(props_widget, "Properties")
        
        # Settings tab  
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        settings_btn = QPushButton("Open Professional Settings")
        if design_system_available:
            settings_btn.setStyleSheet(AutoFireStyleSheet.get_primary_button())
        settings_layout.addWidget(settings_btn)
        
        compliance_label = QLabel("NFPA 72 Compliance Mode: ✅ Active")
        if design_system_available:
            compliance_label.setStyleSheet(f"color: {AutoFireColor.SUCCESS}; font-weight: bold;")
        settings_layout.addWidget(compliance_label)
        
        settings_layout.addStretch()
        tab_widget.addTab(settings_widget, "Settings")
        
        # Analysis tab
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        
        analysis_text = QTextEdit()
        analysis_text.setPlainText("""
System Analysis:

Total Devices: 247
SLC Circuits: 8 (76% capacity)
NAC Circuits: 4 (45% capacity) 
Power Draw: 2.4A (48% capacity)

Compliance Status:
✅ Device spacing compliant
✅ Circuit loading within limits
✅ Battery backup adequate
⚠️  Consider redundant pathways

Recommendations:
• Add 2 additional zones
• Upgrade to Class A wiring
• Install network monitoring
        """)
        if design_system_available:
            analysis_text.setStyleSheet(AutoFireStyleSheet.get_text_edit())
        analysis_layout.addWidget(analysis_text)
        
        tab_widget.addTab(analysis_widget, "Analysis")
        
        layout.addWidget(tab_widget)
        parent.addWidget(right_widget)
    
    def create_status_bar(self):
        """Create professional status bar"""
        status_bar = self.statusBar()
        if design_system_available:
            status_bar.setStyleSheet(AutoFireStyleSheet.get_status_bar())
        
        status_bar.showMessage("FlameCAD Professional Ready | Project: Office Building Fire Alarm System | Devices: 247 | Compliance: NFPA 72 ✅")


def main():
    """Main function to run the complete FlameCAD showcase"""
    app = QApplication(sys.argv)
    
    # Set application style
    if design_system_available:
        app.setStyleSheet(f"""
            QApplication {{
                background-color: {AutoFireColor.BACKGROUND};
                color: {AutoFireColor.TEXT_PRIMARY};
            }}
        """)
    
    # Create and show main window
    window = FlameCADShowcaseMainWindow()
    window.show()
    
    print("\n" + "="*60)
    print("🔥 FLAMECAD PROFESSIONAL SUITE - COMPLETE SHOWCASE")
    print("="*60)
    print("✅ Circuit Colors: SLC=Red, NAC=Yellow, Power=Orange")
    print("✅ Database-Driven Device Selection")
    print("✅ Professional Design System Applied")
    print("✅ Complete UI/UX Transformation")
    print("✅ Fire Alarm Industry Standards")
    print("="*60)
    
    if design_system_available:
        print("🎨 Design System Status: FULLY OPERATIONAL")
        print(f"🎯 Theme: Professional Fire Alarm CAD")
        print(f"🔧 Components: All Enhanced")
    else:
        print("⚠️  Design System: Limited (missing imports)")
    
    print("\nFlameCAD is ready for professional fire alarm system design!")
    
    return app.exec()


if __name__ == "__main__":
    main()