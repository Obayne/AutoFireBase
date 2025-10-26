#!/usr/bin/env python3
"""
Demo application for FlameCAD Dark Theme Design System.

Tests the high-contrast dark theme for improved readability,
with professional fire alarm industry styling.
"""

import sys
import os

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                                 QWidget, QLabel, QPushButton, QGroupBox, 
                                 QLineEdit, QComboBox, QHBoxLayout, QTextEdit)
    from PySide6.QtCore import Qt
    from frontend.design_system import AutoFireColor, AutoFireStyleSheet
    
    class DarkThemeDemoWindow(QMainWindow):
        """Demo window showing the new dark theme with high contrast."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("🔥 FlameCAD Dark Theme - High Contrast Demo")
            self.setGeometry(200, 200, 800, 700)
            
            # Apply dark theme background
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {AutoFireColor.BACKGROUND.value};
                    color: {AutoFireColor.TEXT_PRIMARY.value};
                }}
            """)
            
            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            layout.setSpacing(20)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Header with high contrast
            header = QLabel("🔥 FlameCAD Dark Theme - Professional Fire Alarm CAD")
            header.setStyleSheet(f"""
                QLabel {{
                    color: {AutoFireColor.PRIMARY.value};
                    font-size: 22px;
                    font-weight: bold;
                    padding: 20px;
                    background-color: {AutoFireColor.SURFACE_PRIMARY.value};
                    border-radius: 10px;
                    margin-bottom: 15px;
                    border: 2px solid {AutoFireColor.BORDER_PRIMARY.value};
                }}
            """)
            header.setAlignment(Qt.AlignCenter)
            layout.addWidget(header)
            
            # Dark theme info
            info_text = QTextEdit()
            info_text.setHtml(f"""
                <div style="color: {AutoFireColor.TEXT_PRIMARY.value}; font-size: 14px; line-height: 1.6;">
                    <h3 style="color: {AutoFireColor.ACCENT.value};">🌙 High Contrast Dark Theme Benefits:</h3>
                    <ul>
                        <li><strong>Reduced Eye Strain:</strong> Dark backgrounds are easier on the eyes</li>
                        <li><strong>Better Contrast:</strong> Bright text on dark backgrounds improves readability</li>
                        <li><strong>Professional Appearance:</strong> Modern dark themes look sophisticated</li>
                        <li><strong>Fire Alarm Colors:</strong> Industry-standard circuit colors remain vibrant</li>
                        <li><strong>NFPA Compliance:</strong> Clear visual hierarchy for code compliance</li>
                    </ul>
                    <p><em>This theme is optimized for long CAD sessions and detailed technical work.</em></p>
                </div>
            """)
            info_text.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {AutoFireColor.SURFACE_SECONDARY.value};
                    color: {AutoFireColor.TEXT_PRIMARY.value};
                    border: 2px solid {AutoFireColor.BORDER_PRIMARY.value};
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 13px;
                }}
            """)
            info_text.setMaximumHeight(200)
            layout.addWidget(info_text)
            
            # Buttons demo group
            button_group = QGroupBox("Button Styles Demo")
            button_group.setStyleSheet(AutoFireStyleSheet.group_box())
            button_layout = QHBoxLayout(button_group)
            
            # Primary button
            primary_btn = QPushButton("🔥 Primary Action")
            primary_btn.setStyleSheet(AutoFireStyleSheet.button_primary())
            button_layout.addWidget(primary_btn)
            
            # Secondary button  
            secondary_btn = QPushButton("⚙️ Secondary Action")
            secondary_btn.setStyleSheet(AutoFireStyleSheet.button_secondary())
            button_layout.addWidget(secondary_btn)
            
            # Success button
            success_btn = QPushButton("✅ Success Action")
            success_btn.setStyleSheet(AutoFireStyleSheet.button_success())
            button_layout.addWidget(success_btn)
            
            layout.addWidget(button_group)
            
            # Input fields demo group
            input_group = QGroupBox("Input Fields Demo")
            input_group.setStyleSheet(AutoFireStyleSheet.group_box())
            input_layout = QVBoxLayout(input_group)
            
            # Text input
            text_input = QLineEdit("Type here to test text input contrast...")
            text_input.setStyleSheet(AutoFireStyleSheet.input_field())
            input_layout.addWidget(text_input)
            
            # Combo box
            combo = QComboBox()
            combo.addItems(["🏭 Manufacturer A", "🏭 Manufacturer B", "🏭 Manufacturer C"])
            combo.setStyleSheet(AutoFireStyleSheet.input_field())
            input_layout.addWidget(combo)
            
            layout.addWidget(input_group)
            
            # Circuit colors demo
            circuit_group = QGroupBox("Fire Alarm Circuit Colors")
            circuit_group.setStyleSheet(AutoFireStyleSheet.group_box())
            circuit_layout = QVBoxLayout(circuit_group)
            
            circuits = [
                ("NAC Circuit", AutoFireColor.CIRCUIT_NAC.value),
                ("SLC Circuit", AutoFireColor.CIRCUIT_SLC.value),
                ("Power Circuit", AutoFireColor.CIRCUIT_POWER.value),
                ("Control Circuit", AutoFireColor.CIRCUIT_CONTROL.value),
                ("Telephone Circuit", AutoFireColor.CIRCUIT_TELEPHONE.value),
            ]
            
            for name, color in circuits:
                circuit_label = QLabel(f"● {name}")
                circuit_label.setStyleSheet(f"""
                    QLabel {{
                        color: {color};
                        font-size: 14px;
                        font-weight: bold;
                        padding: 8px;
                        background-color: {AutoFireColor.SURFACE_SECONDARY.value};
                        border-radius: 4px;
                        margin: 2px;
                        border-left: 4px solid {color};
                    }}
                """)
                circuit_layout.addWidget(circuit_label)
            
            layout.addWidget(circuit_group)
            
            # Status bar
            status_label = QLabel("✅ Dark theme loaded successfully - much better contrast for reading!")
            status_label.setStyleSheet(f"""
                QLabel {{
                    color: {AutoFireColor.COMPLIANCE_PASS.value};
                    font-size: 12px;
                    font-weight: bold;
                    padding: 10px;
                    background-color: {AutoFireColor.SURFACE_PRIMARY.value};
                    border: 1px solid {AutoFireColor.BORDER_PRIMARY.value};
                    border-radius: 4px;
                    margin-top: 10px;
                }}
            """)
            layout.addWidget(status_label)
            
    def main():
        """Run the dark theme demo application."""
        print("🔥 Starting FlameCAD Dark Theme Demo...")
        
        app = QApplication(sys.argv)
        
        # Set application-wide dark palette for native widgets too
        app.setStyle('Fusion')  # Modern style that works well with dark themes
        
        # Create and show the demo window
        window = DarkThemeDemoWindow()
        window.show()
        
        print("✅ Dark theme demo launched!")
        print("📝 Dark theme features:")
        print("   - High contrast text on dark backgrounds")
        print("   - Reduced eye strain for long work sessions")
        print("   - Professional fire alarm industry colors")
        print("   - Clear visual hierarchy and readability")
        print("   - Modern sophisticated appearance")
        
        return app.exec()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("⚠️  This demo requires PySide6.")
    print("💡 Try running: pip install PySide6")
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())