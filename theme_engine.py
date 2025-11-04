"""
AutoFire Theme Engine
====================

Robust theme utility with custom skins for personalizing the AutoFire workspace.
Supports built-in themes, custom color schemes, and workspace personalization.
"""

import os
import json
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSettings
from PySide6.QtGui import QColor, QPalette, QFont, QPixmap, QPainter, QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel, 
    QPushButton, QComboBox, QSlider, QSpinBox, QColorDialog, QFileDialog,
    QTabWidget, QScrollArea, QFrame, QCheckBox, QLineEdit, QTextEdit,
    QApplication, QMainWindow, QMessageBox, QSplitter, QListWidget,
    QListWidgetItem, QProgressBar
)


class ThemeCategory(Enum):
    """Theme categories for organization."""
    BUILT_IN = "built_in"
    PROFESSIONAL = "professional"
    FIRE_ALARM = "fire_alarm"
    HIGH_CONTRAST = "high_contrast"
    CUSTOM = "custom"


@dataclass
class ColorScheme:
    """Complete color scheme for AutoFire interface."""
    # Primary colors
    primary: str = "#C41E3A"           # AutoFire red
    secondary: str = "#8B0000"         # Dark red
    accent: str = "#FF6B35"            # Orange accent
    
    # Background colors
    background_primary: str = "#FFFFFF"      # Main background
    background_secondary: str = "#F8F9FA"    # Panel backgrounds
    background_tertiary: str = "#E9ECEF"     # Toolbar backgrounds
    
    # Text colors
    text_primary: str = "#212529"      # Main text
    text_secondary: str = "#6C757D"    # Secondary text
    text_inverse: str = "#FFFFFF"      # Text on dark backgrounds
    text_disabled: str = "#ADB5BD"     # Disabled text
    
    # UI element colors
    border: str = "#DEE2E6"            # Borders
    border_active: str = "#C41E3A"     # Active borders
    input_background: str = "#FFFFFF"   # Input backgrounds
    input_border: str = "#CED4DA"      # Input borders
    
    # Status colors
    success: str = "#28A745"           # Success/pass
    warning: str = "#FFC107"           # Warning
    danger: str = "#DC3545"            # Error/fail
    info: str = "#17A2B8"              # Information
    
    # CAD-specific colors
    cad_background: str = "#2C2C2C"    # CAD drawing area
    cad_grid: str = "#404040"          # Grid lines
    cad_cursor: str = "#FFFF00"        # Cursor/crosshairs
    cad_selection: str = "#00BFFF"     # Selection highlight
    
    # Fire alarm device colors
    smoke_detector: str = "#FF6B35"    # Smoke detectors
    heat_detector: str = "#FF0000"     # Heat detectors
    pull_station: str = "#C41E3A"      # Pull stations
    horn_strobe: str = "#FFD700"       # Horn/strobes
    panel: str = "#8B0000"             # Control panels
    
    # Circuit colors
    slc_circuit: str = "#0066CC"       # SLC circuits
    nac_circuit: str = "#FF6600"       # NAC circuits
    power_circuit: str = "#CC0000"     # Power circuits


@dataclass
class ThemeMetadata:
    """Theme metadata and configuration."""
    name: str
    display_name: str
    description: str
    category: ThemeCategory
    author: str = "AutoFire"
    version: str = "1.0"
    created_date: str = ""
    preview_image: str | None = None
    
    # Theme settings
    font_family: str = "Segoe UI"
    font_size: int = 9
    ui_scale: float = 1.0
    use_animations: bool = True
    rounded_corners: bool = True
    
    # Advanced settings
    transparency_level: float = 1.0
    shadow_effects: bool = True
    custom_icons: bool = False
    icon_set: str = "default"


@dataclass
class AutoFireTheme:
    """Complete AutoFire theme definition."""
    metadata: ThemeMetadata
    colors: ColorScheme
    
    def to_dict(self) -> Dict:
        """Convert theme to dictionary for serialization."""
        metadata_dict = asdict(self.metadata)
        # Convert enum to string for JSON serialization
        metadata_dict['category'] = self.metadata.category.value
        
        return {
            "metadata": metadata_dict,
            "colors": asdict(self.colors)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AutoFireTheme':
        """Create theme from dictionary."""
        # Handle category enum conversion
        metadata_data = data["metadata"].copy()
        if isinstance(metadata_data['category'], str):
            metadata_data['category'] = ThemeCategory(metadata_data['category'])
        
        metadata = ThemeMetadata(**metadata_data)
        colors = ColorScheme(**data["colors"])
        return cls(metadata=metadata, colors=colors)


class ThemeLibrary:
    """Library of built-in and custom themes."""
    
    @classmethod
    def get_built_in_themes(cls) -> List[AutoFireTheme]:
        """Get all built-in themes."""
        themes = []
        
        # Classic AutoFire Theme
        classic = AutoFireTheme(
            metadata=ThemeMetadata(
                name="classic",
                display_name="Classic AutoFire",
                description="Traditional AutoFire red and white theme",
                category=ThemeCategory.BUILT_IN
            ),
            colors=ColorScheme()  # Default colors
        )
        themes.append(classic)
        
        # Dark Professional Theme
        dark = AutoFireTheme(
            metadata=ThemeMetadata(
                name="dark_professional",
                display_name="Dark Professional",
                description="Dark theme for professional CAD work",
                category=ThemeCategory.PROFESSIONAL
            ),
            colors=ColorScheme(
                background_primary="#2B2B2B",
                background_secondary="#3C3C3C",
                background_tertiary="#4A4A4A",
                text_primary="#FFFFFF",
                text_secondary="#CCCCCC",
                text_inverse="#000000",
                border="#555555",
                input_background="#404040",
                input_border="#666666",
                cad_background="#1E1E1E"
            )
        )
        themes.append(dark)
        
        # Fire Department Red Theme
        fire_dept = AutoFireTheme(
            metadata=ThemeMetadata(
                name="fire_department",
                display_name="Fire Department Red",
                description="Bold red theme inspired by fire department colors",
                category=ThemeCategory.FIRE_ALARM
            ),
            colors=ColorScheme(
                primary="#DC143C",
                secondary="#B22222",
                background_secondary="#FFF5F5",
                background_tertiary="#FFE4E1"
            )
        )
        themes.append(fire_dept)
        
        # High Contrast Theme
        high_contrast = AutoFireTheme(
            metadata=ThemeMetadata(
                name="high_contrast",
                display_name="High Contrast",
                description="High contrast theme for accessibility",
                category=ThemeCategory.HIGH_CONTRAST
            ),
            colors=ColorScheme(
                primary="#000000",
                secondary="#FFFFFF",
                background_primary="#FFFFFF",
                background_secondary="#F0F0F0",
                text_primary="#000000",
                text_secondary="#000000",
                border="#000000",
                success="#008000",
                warning="#FF8C00",
                danger="#FF0000"
            )
        )
        themes.append(high_contrast)
        
        # Ocean Blue Theme
        ocean = AutoFireTheme(
            metadata=ThemeMetadata(
                name="ocean_blue",
                display_name="Ocean Blue",
                description="Calming blue theme for long design sessions",
                category=ThemeCategory.PROFESSIONAL
            ),
            colors=ColorScheme(
                primary="#1E88E5",
                secondary="#1565C0",
                accent="#42A5F5",
                background_secondary="#E3F2FD",
                background_tertiary="#BBDEFB"
            )
        )
        themes.append(ocean)
        
        # Safety Orange Theme
        safety = AutoFireTheme(
            metadata=ThemeMetadata(
                name="safety_orange",
                display_name="Safety Orange",
                description="High-visibility orange theme for safety applications",
                category=ThemeCategory.FIRE_ALARM
            ),
            colors=ColorScheme(
                primary="#FF6600",
                secondary="#CC5200",
                accent="#FF8533",
                background_secondary="#FFF3E0",
                background_tertiary="#FFE0B2"
            )
        )
        themes.append(safety)
        
        return themes


class ColorPicker(QWidget):
    """Advanced color picker with presets and custom colors."""
    
    color_changed = Signal(str)  # hex color
    
    def __init__(self, initial_color: str = "#FFFFFF"):
        super().__init__()
        self.current_color = initial_color
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup color picker UI."""
        layout = QVBoxLayout(self)
        
        # Current color display
        self.color_display = QFrame()
        self.color_display.setFixedHeight(40)
        self.color_display.setStyleSheet(f"background-color: {self.current_color}; border: 2px solid #ccc;")
        layout.addWidget(self.color_display)
        
        # Color value input
        input_layout = QHBoxLayout()
        
        self.hex_input = QLineEdit(self.current_color)
        self.hex_input.setPlaceholderText("#RRGGBB")
        self.hex_input.textChanged.connect(self._on_hex_changed)
        
        self.pick_btn = QPushButton("🎨 Pick Color")
        self.pick_btn.clicked.connect(self._pick_color)
        
        input_layout.addWidget(QLabel("Hex:"))
        input_layout.addWidget(self.hex_input)
        input_layout.addWidget(self.pick_btn)
        
        layout.addLayout(input_layout)
        
        # Color presets
        presets_group = QGroupBox("Quick Colors")
        presets_layout = QGridLayout(presets_group)
        
        presets = [
            "#FFFFFF", "#F8F9FA", "#E9ECEF", "#DEE2E6", "#CED4DA",
            "#ADB5BD", "#6C757D", "#495057", "#343A40", "#212529",
            "#C41E3A", "#8B0000", "#FF6B35", "#28A745", "#FFC107",
            "#DC3545", "#17A2B8", "#6F42C1", "#E83E8C", "#FD7E14"
        ]
        
        for i, color in enumerate(presets):
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background-color: {color}; border: 1px solid #ccc;")
            btn.clicked.connect(lambda checked, c=color: self.set_color(c))
            presets_layout.addWidget(btn, i // 5, i % 5)
        
        layout.addWidget(presets_group)
    
    def _on_hex_changed(self, hex_color):
        """Handle hex input change."""
        if hex_color.startswith('#') and len(hex_color) == 7:
            try:
                # Validate hex color
                QColor(hex_color)
                self.set_color(hex_color)
            except:
                pass
    
    def _pick_color(self):
        """Open color dialog."""
        color = QColorDialog.getColor(QColor(self.current_color), self)
        if color.isValid():
            self.set_color(color.name())
    
    def set_color(self, hex_color: str):
        """Set the current color."""
        self.current_color = hex_color
        self.color_display.setStyleSheet(f"background-color: {hex_color}; border: 2px solid #ccc;")
        self.hex_input.setText(hex_color)
        self.color_changed.emit(hex_color)
    
    def get_color(self) -> str:
        """Get current color."""
        return self.current_color


class ThemeEditor(QWidget):
    """Theme editor for creating and modifying themes."""
    
    theme_saved = Signal(AutoFireTheme)
    
    def __init__(self, theme: AutoFireTheme | None = None):
        super().__init__()
        self.current_theme = theme or AutoFireTheme(
            metadata=ThemeMetadata(
                name="custom_theme",
                display_name="Custom Theme",
                description="User-created custom theme",
                category=ThemeCategory.CUSTOM,
                author="User"
            ),
            colors=ColorScheme()
        )
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup theme editor UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🎨 Theme Editor")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #C41E3A; padding: 10px;")
        layout.addWidget(header)
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        
        self._setup_metadata_tab()
        self._setup_colors_tab()
        self._setup_advanced_tab()
        self._setup_preview_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save Theme")
        self.save_btn.clicked.connect(self._save_theme)
        
        self.export_btn = QPushButton("📤 Export Theme")
        self.export_btn.clicked.connect(self._export_theme)
        
        self.reset_btn = QPushButton("🔄 Reset to Default")
        self.reset_btn.clicked.connect(self._reset_theme)
        
        button_layout.addStretch()
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def _setup_metadata_tab(self):
        """Setup theme metadata tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Basic info
        info_group = QGroupBox("Theme Information")
        info_layout = QGridLayout(info_group)
        
        self.name_input = QLineEdit(self.current_theme.metadata.name)
        self.display_name_input = QLineEdit(self.current_theme.metadata.display_name)
        self.author_input = QLineEdit(self.current_theme.metadata.author)
        self.description_input = QTextEdit(self.current_theme.metadata.description)
        self.description_input.setMaximumHeight(80)
        
        info_layout.addWidget(QLabel("Internal Name:"), 0, 0)
        info_layout.addWidget(self.name_input, 0, 1)
        info_layout.addWidget(QLabel("Display Name:"), 1, 0)
        info_layout.addWidget(self.display_name_input, 1, 1)
        info_layout.addWidget(QLabel("Author:"), 2, 0)
        info_layout.addWidget(self.author_input, 2, 1)
        info_layout.addWidget(QLabel("Description:"), 3, 0)
        info_layout.addWidget(self.description_input, 3, 1)
        
        layout.addWidget(info_group)
        
        # Category selection
        category_group = QGroupBox("Theme Category")
        category_layout = QHBoxLayout(category_group)
        
        self.category_combo = QComboBox()
        categories = [cat.value.replace('_', ' ').title() for cat in ThemeCategory]
        self.category_combo.addItems(categories)
        category_layout.addWidget(self.category_combo)
        
        layout.addWidget(category_group)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "📝 Info")
    
    def _setup_colors_tab(self):
        """Setup color configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area for color options
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        self.color_pickers = {}
        
        # Group colors by category
        color_groups = {
            "Primary Colors": ["primary", "secondary", "accent"],
            "Background Colors": ["background_primary", "background_secondary", "background_tertiary"],
            "Text Colors": ["text_primary", "text_secondary", "text_inverse", "text_disabled"],
            "UI Element Colors": ["border", "border_active", "input_background", "input_border"],
            "Status Colors": ["success", "warning", "danger", "info"],
            "CAD Colors": ["cad_background", "cad_grid", "cad_cursor", "cad_selection"],
            "Device Colors": ["smoke_detector", "heat_detector", "pull_station", "horn_strobe", "panel"],
            "Circuit Colors": ["slc_circuit", "nac_circuit", "power_circuit"]
        }
        
        for group_name, color_names in color_groups.items():
            group = QGroupBox(group_name)
            group_layout = QGridLayout(group)
            
            for i, color_name in enumerate(color_names):
                # Get current color value
                current_color = getattr(self.current_theme.colors, color_name)
                
                # Create color picker
                picker = ColorPicker(current_color)
                picker.color_changed.connect(lambda color, name=color_name: self._on_color_changed(name, color))
                self.color_pickers[color_name] = picker
                
                # Create label
                label = QLabel(color_name.replace('_', ' ').title() + ":")
                label.setMinimumWidth(150)
                
                group_layout.addWidget(label, i, 0)
                group_layout.addWidget(picker, i, 1)
            
            scroll_layout.addWidget(group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(widget, "🎨 Colors")
    
    def _setup_advanced_tab(self):
        """Setup advanced theme settings."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Font settings
        font_group = QGroupBox("Font Settings")
        font_layout = QGridLayout(font_group)
        
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "Segoe UI", "Arial", "Helvetica", "Calibri", "Tahoma",
            "Verdana", "Consolas", "Monaco", "Courier New"
        ])
        self.font_family_combo.setCurrentText(self.current_theme.metadata.font_family)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 20)
        self.font_size_spin.setValue(self.current_theme.metadata.font_size)
        
        font_layout.addWidget(QLabel("Font Family:"), 0, 0)
        font_layout.addWidget(self.font_family_combo, 0, 1)
        font_layout.addWidget(QLabel("Font Size:"), 1, 0)
        font_layout.addWidget(self.font_size_spin, 1, 1)
        
        layout.addWidget(font_group)
        
        # UI settings
        ui_group = QGroupBox("Interface Settings")
        ui_layout = QGridLayout(ui_group)
        
        self.ui_scale_slider = QSlider(Qt.Horizontal)
        self.ui_scale_slider.setRange(80, 150)
        self.ui_scale_slider.setValue(int(self.current_theme.metadata.ui_scale * 100))
        self.ui_scale_label = QLabel(f"{self.current_theme.metadata.ui_scale:.1f}x")
        self.ui_scale_slider.valueChanged.connect(lambda v: self.ui_scale_label.setText(f"{v/100:.1f}x"))
        
        self.animations_cb = QCheckBox("Enable Animations")
        self.animations_cb.setChecked(self.current_theme.metadata.use_animations)
        
        self.rounded_corners_cb = QCheckBox("Rounded Corners")
        self.rounded_corners_cb.setChecked(self.current_theme.metadata.rounded_corners)
        
        self.shadows_cb = QCheckBox("Shadow Effects")
        self.shadows_cb.setChecked(self.current_theme.metadata.shadow_effects)
        
        ui_layout.addWidget(QLabel("UI Scale:"), 0, 0)
        ui_layout.addWidget(self.ui_scale_slider, 0, 1)
        ui_layout.addWidget(self.ui_scale_label, 0, 2)
        ui_layout.addWidget(self.animations_cb, 1, 0, 1, 3)
        ui_layout.addWidget(self.rounded_corners_cb, 2, 0, 1, 3)
        ui_layout.addWidget(self.shadows_cb, 3, 0, 1, 3)
        
        layout.addWidget(ui_group)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "⚙️ Advanced")
    
    def _setup_preview_tab(self):
        """Setup theme preview."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        preview_label = QLabel("🔍 Theme Preview")
        preview_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(preview_label)
        
        # Create preview components
        self.preview_area = QFrame()
        self.preview_area.setMinimumHeight(400)
        self.preview_area.setStyleSheet("border: 2px solid #ccc;")
        
        preview_layout = QVBoxLayout(self.preview_area)
        
        # Mock AutoFire interface elements
        header = QLabel("AutoFire - Fire Alarm Design")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        preview_layout.addWidget(header)
        
        # Mock toolbar
        toolbar = QFrame()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.addWidget(QPushButton("File"))
        toolbar_layout.addWidget(QPushButton("Edit"))
        toolbar_layout.addWidget(QPushButton("Tools"))
        toolbar_layout.addWidget(QPushButton("Calculate"))
        toolbar_layout.addStretch()
        toolbar.setLayout(toolbar_layout)
        preview_layout.addWidget(toolbar)
        
        # Mock CAD area
        cad_area = QFrame()
        cad_area.setMinimumHeight(200)
        cad_layout = QVBoxLayout(cad_area)
        cad_layout.addWidget(QLabel("CAD Drawing Area"))
        cad_layout.addWidget(QLabel("🔥 Sample fire alarm layout"))
        preview_layout.addWidget(cad_area)
        
        layout.addWidget(self.preview_area)
        
        # Update preview button
        self.update_preview_btn = QPushButton("🔄 Update Preview")
        self.update_preview_btn.clicked.connect(self._update_preview)
        layout.addWidget(self.update_preview_btn)
        
        self.tab_widget.addTab(widget, "👁️ Preview")
    
    def _on_color_changed(self, color_name: str, color_value: str):
        """Handle color change."""
        setattr(self.current_theme.colors, color_name, color_value)
        self._update_preview()
    
    def _update_preview(self):
        """Update theme preview."""
        # Apply current theme to preview area
        colors = self.current_theme.colors
        
        style = f"""
        QFrame#preview {{
            background-color: {colors.background_primary};
            color: {colors.text_primary};
        }}
        QLabel {{
            color: {colors.text_primary};
            background-color: {colors.background_primary};
        }}
        QPushButton {{
            background-color: {colors.primary};
            color: {colors.text_inverse};
            border: 1px solid {colors.border};
            padding: 5px 10px;
            border-radius: 3px;
        }}
        QPushButton:hover {{
            background-color: {colors.secondary};
        }}
        """
        
        self.preview_area.setStyleSheet(style)
    
    def _save_theme(self):
        """Save the current theme."""
        # Update theme metadata from form
        self.current_theme.metadata.name = self.name_input.text()
        self.current_theme.metadata.display_name = self.display_name_input.text()
        self.current_theme.metadata.author = self.author_input.text()
        self.current_theme.metadata.description = self.description_input.toPlainText()
        self.current_theme.metadata.font_family = self.font_family_combo.currentText()
        self.current_theme.metadata.font_size = self.font_size_spin.value()
        self.current_theme.metadata.ui_scale = self.ui_scale_slider.value() / 100.0
        self.current_theme.metadata.use_animations = self.animations_cb.isChecked()
        self.current_theme.metadata.rounded_corners = self.rounded_corners_cb.isChecked()
        self.current_theme.metadata.shadow_effects = self.shadows_cb.isChecked()
        
        self.theme_saved.emit(self.current_theme)
        QMessageBox.information(self, "Theme Saved", 
                              f"Theme '{self.current_theme.metadata.display_name}' has been saved!")
    
    def _export_theme(self):
        """Export theme to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Theme", 
            f"{self.current_theme.metadata.name}.autofire_theme", 
            "AutoFire Theme Files (*.autofire_theme);;JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.current_theme.to_dict(), f, indent=2)
                QMessageBox.information(self, "Export Complete", 
                                      f"Theme exported to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", f"Error: {str(e)}")
    
    def _reset_theme(self):
        """Reset theme to default."""
        reply = QMessageBox.question(self, "Reset Theme", 
                                   "Reset all colors to default values?")
        if reply == QMessageBox.Yes:
            self.current_theme.colors = ColorScheme()
            
            # Update color pickers
            for color_name, picker in self.color_pickers.items():
                color_value = getattr(self.current_theme.colors, color_name)
                picker.set_color(color_value)
            
            self._update_preview()


class ThemeManager(QWidget):
    """Main theme management interface."""
    
    theme_applied = Signal(AutoFireTheme)
    
    def __init__(self):
        super().__init__()
        self.current_theme = None
        self.available_themes = ThemeLibrary.get_built_in_themes()
        self._setup_ui()
        self._load_themes()
    
    def _setup_ui(self):
        """Setup theme manager UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🎨 AutoFire Theme Manager")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #C41E3A; padding: 15px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        subtitle = QLabel("Personalize your AutoFire workspace with themes and custom skins")
        subtitle.setStyleSheet("color: #666; text-align: center; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Main content area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - theme list
        left_panel = self._create_theme_list_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - theme details and preview
        right_panel = self._create_theme_details_panel()
        content_splitter.addWidget(right_panel)
        
        content_splitter.setSizes([300, 500])
        layout.addWidget(content_splitter)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("📥 Import Theme")
        self.import_btn.clicked.connect(self._import_theme)
        
        self.create_btn = QPushButton("✨ Create Custom Theme")
        self.create_btn.clicked.connect(self._create_custom_theme)
        
        self.apply_btn = QPushButton("✅ Apply Theme")
        self.apply_btn.clicked.connect(self._apply_theme)
        self.apply_btn.setEnabled(False)
        
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.create_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)
    
    def _create_theme_list_panel(self) -> QWidget:
        """Create theme list panel."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout(panel)
        
        # Category filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Category:"))
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Themes")
        for category in ThemeCategory:
            self.category_filter.addItem(category.value.replace('_', ' ').title())
        self.category_filter.currentTextChanged.connect(self._filter_themes)
        
        filter_layout.addWidget(self.category_filter)
        layout.addLayout(filter_layout)
        
        # Theme list
        self.theme_list = QListWidget()
        self.theme_list.itemSelectionChanged.connect(self._on_theme_selected)
        layout.addWidget(self.theme_list)
        
        return panel
    
    def _create_theme_details_panel(self) -> QWidget:
        """Create theme details panel."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout(panel)
        
        # Theme info
        self.theme_info = QGroupBox("Theme Details")
        info_layout = QVBoxLayout(self.theme_info)
        
        self.theme_name = QLabel("Select a theme")
        self.theme_name.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.theme_description = QLabel("")
        self.theme_description.setWordWrap(True)
        
        self.theme_author = QLabel("")
        self.theme_category = QLabel("")
        
        info_layout.addWidget(self.theme_name)
        info_layout.addWidget(self.theme_description)
        info_layout.addWidget(self.theme_author)
        info_layout.addWidget(self.theme_category)
        
        layout.addWidget(self.theme_info)
        
        # Color preview
        self.color_preview = QGroupBox("Color Scheme Preview")
        preview_layout = QGridLayout(self.color_preview)
        
        self.color_swatches = {}
        color_names = ["primary", "secondary", "success", "warning", "danger", "info"]
        
        for i, color_name in enumerate(color_names):
            swatch = QFrame()
            swatch.setFixedSize(50, 30)
            swatch.setFrameStyle(QFrame.Box)
            self.color_swatches[color_name] = swatch
            
            label = QLabel(color_name.title())
            label.setAlignment(Qt.AlignCenter)
            
            preview_layout.addWidget(swatch, 0, i)
            preview_layout.addWidget(label, 1, i)
        
        layout.addWidget(self.color_preview)
        
        # Edit button
        self.edit_btn = QPushButton("✏️ Edit Theme")
        self.edit_btn.clicked.connect(self._edit_theme)
        self.edit_btn.setEnabled(False)
        layout.addWidget(self.edit_btn)
        
        layout.addStretch()
        
        return panel
    
    def _load_themes(self):
        """Load themes into the list."""
        self.theme_list.clear()
        
        for theme in self.available_themes:
            item = QListWidgetItem(f"🎨 {theme.metadata.display_name}")
            item.setData(Qt.UserRole, theme)
            self.theme_list.addItem(item)
    
    def _filter_themes(self, category_text: str):
        """Filter themes by category."""
        self.theme_list.clear()
        
        for theme in self.available_themes:
            if (category_text == "All Themes" or 
                theme.metadata.category.value.replace('_', ' ').title() == category_text):
                
                item = QListWidgetItem(f"🎨 {theme.metadata.display_name}")
                item.setData(Qt.UserRole, theme)
                self.theme_list.addItem(item)
    
    def _on_theme_selected(self):
        """Handle theme selection."""
        current_item = self.theme_list.currentItem()
        if current_item:
            theme = current_item.data(Qt.UserRole)
            self._display_theme_details(theme)
            self.current_theme = theme
            self.apply_btn.setEnabled(True)
            self.edit_btn.setEnabled(True)
    
    def _display_theme_details(self, theme: AutoFireTheme):
        """Display theme details in the right panel."""
        self.theme_name.setText(theme.metadata.display_name)
        self.theme_description.setText(theme.metadata.description)
        self.theme_author.setText(f"Author: {theme.metadata.author}")
        self.theme_category.setText(f"Category: {theme.metadata.category.value.replace('_', ' ').title()}")
        
        # Update color swatches
        colors = {
            "primary": theme.colors.primary,
            "secondary": theme.colors.secondary,
            "success": theme.colors.success,
            "warning": theme.colors.warning,
            "danger": theme.colors.danger,
            "info": theme.colors.info
        }
        
        for color_name, color_value in colors.items():
            if color_name in self.color_swatches:
                self.color_swatches[color_name].setStyleSheet(
                    f"background-color: {color_value}; border: 1px solid #ccc;"
                )
    
    def _import_theme(self):
        """Import theme from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Theme", "",
            "AutoFire Theme Files (*.autofire_theme);;JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    theme_data = json.load(f)
                
                theme = AutoFireTheme.from_dict(theme_data)
                theme.metadata.category = ThemeCategory.CUSTOM
                
                self.available_themes.append(theme)
                self._load_themes()
                
                QMessageBox.information(self, "Import Complete", 
                                      f"Theme '{theme.metadata.display_name}' imported successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Import Failed", f"Error: {str(e)}")
    
    def _create_custom_theme(self):
        """Create a new custom theme."""
        editor = ThemeEditor()
        editor.theme_saved.connect(self._on_theme_created)
        
        dialog = QMainWindow()
        dialog.setWindowTitle("Create Custom Theme")
        dialog.setCentralWidget(editor)
        dialog.setGeometry(100, 100, 800, 600)
        dialog.show()
    
    def _edit_theme(self):
        """Edit the selected theme."""
        if self.current_theme:
            editor = ThemeEditor(self.current_theme)
            editor.theme_saved.connect(self._on_theme_updated)
            
            dialog = QMainWindow()
            dialog.setWindowTitle(f"Edit Theme - {self.current_theme.metadata.display_name}")
            dialog.setCentralWidget(editor)
            dialog.setGeometry(100, 100, 800, 600)
            dialog.show()
    
    def _on_theme_created(self, theme: AutoFireTheme):
        """Handle new theme creation."""
        self.available_themes.append(theme)
        self._load_themes()
    
    def _on_theme_updated(self, theme: AutoFireTheme):
        """Handle theme update."""
        self._display_theme_details(theme)
    
    def _apply_theme(self):
        """Apply the selected theme."""
        if self.current_theme:
            self.theme_applied.emit(self.current_theme)
            QMessageBox.information(self, "Theme Applied", 
                                  f"Theme '{self.current_theme.metadata.display_name}' has been applied to AutoFire!")


def create_theme_manager_demo():
    """Create demo of the theme manager."""
    import sys
    
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("🎨 AutoFire - Theme Manager")
            self.setGeometry(100, 100, 1000, 700)
            
            self.theme_manager = ThemeManager()
            self.setCentralWidget(self.theme_manager)
            
            self.theme_manager.theme_applied.connect(self._on_theme_applied)
        
        def _on_theme_applied(self, theme: AutoFireTheme):
            """Handle theme application."""
            print(f"🎨 Applied theme: {theme.metadata.display_name}")
            print(f"   Primary color: {theme.colors.primary}")
            print(f"   Background: {theme.colors.background_primary}")
            
            # Here you would apply the theme to the entire application
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {theme.colors.background_primary};
                    color: {theme.colors.text_primary};
                }}
                QWidget {{
                    background-color: {theme.colors.background_primary};
                    color: {theme.colors.text_primary};
                }}
                QPushButton {{
                    background-color: {theme.colors.primary};
                    color: {theme.colors.text_inverse};
                    border: 1px solid {theme.colors.border};
                    padding: 8px 16px;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {theme.colors.secondary};
                }}
            """)
    
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    print("🚀 AutoFire Theme Manager")
    print("=" * 30)
    print("✅ Built-in professional themes")
    print("✅ Custom theme creation")
    print("✅ Theme import/export")
    print("✅ Live color preview")
    print("✅ Complete workspace personalization")
    print("✅ Fire alarm industry-specific themes")
    
    return app.exec()


if __name__ == "__main__":
    create_theme_manager_demo()