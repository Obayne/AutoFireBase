"""
AutoFire Theme Persistence
=========================

Handles saving, loading, and managing AutoFire themes in user workspace.
Integrates with user preferences and workspace settings.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from PySide6.QtCore import QSettings, QStandardPaths
from PySide6.QtWidgets import QMessageBox

from theme_engine import AutoFireTheme, ThemeLibrary, ThemeCategory


class ThemePersistence:
    """Handles theme persistence and workspace integration."""
    
    def __init__(self):
        self.app_data_dir = self._get_app_data_dir()
        self.themes_dir = self.app_data_dir / "themes"
        self.settings = QSettings("AutoFire", "ThemeManager")
        
        # Ensure directories exist
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize built-in themes if needed
        self._ensure_builtin_themes()
    
    def _get_app_data_dir(self) -> Path:
        """Get AutoFire application data directory."""
        # Use Qt's standard paths for cross-platform compatibility
        app_data = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        return Path(app_data) / "AutoFire"
    
    def _ensure_builtin_themes(self):
        """Ensure built-in themes are available."""
        builtin_dir = self.themes_dir / "builtin"
        builtin_dir.mkdir(exist_ok=True)
        
        # Save built-in themes if they don't exist
        for theme in ThemeLibrary.get_built_in_themes():
            theme_file = builtin_dir / f"{theme.metadata.name}.autofire_theme"
            if not theme_file.exists():
                self.save_theme(theme, str(theme_file))
    
    def save_theme(self, theme: AutoFireTheme, file_path: Optional[str] = None) -> str:
        """Save theme to file."""
        if file_path is None:
            # Auto-generate filename
            category_dir = self.themes_dir / theme.metadata.category.value
            category_dir.mkdir(exist_ok=True)
            file_path = category_dir / f"{theme.metadata.name}.autofire_theme"
        
        # Update creation date if new theme
        if not hasattr(theme.metadata, 'created_date') or not theme.metadata.created_date:
            theme.metadata.created_date = datetime.now().isoformat()
        
        theme_data = theme.to_dict()
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Theme saved: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"❌ Error saving theme: {e}")
            raise
    
    def load_theme(self, file_path: str) -> AutoFireTheme:
        """Load theme from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            theme = AutoFireTheme.from_dict(theme_data)
            print(f"✅ Theme loaded: {theme.metadata.display_name}")
            return theme
            
        except Exception as e:
            print(f"❌ Error loading theme: {e}")
            raise
    
    def get_all_themes(self) -> List[AutoFireTheme]:
        """Get all available themes."""
        themes = []
        
        # Scan all theme directories
        for theme_file in self.themes_dir.rglob("*.autofire_theme"):
            try:
                theme = self.load_theme(str(theme_file))
                themes.append(theme)
            except Exception as e:
                print(f"⚠️ Failed to load theme {theme_file}: {e}")
        
        return themes
    
    def get_themes_by_category(self, category: ThemeCategory) -> List[AutoFireTheme]:
        """Get themes by category."""
        all_themes = self.get_all_themes()
        return [theme for theme in all_themes if theme.metadata.category == category]
    
    def delete_theme(self, theme_name: str) -> bool:
        """Delete a theme."""
        for theme_file in self.themes_dir.rglob("*.autofire_theme"):
            try:
                theme = self.load_theme(str(theme_file))
                if theme.metadata.name == theme_name:
                    theme_file.unlink()
                    print(f"🗑️ Deleted theme: {theme.metadata.display_name}")
                    return True
            except:
                continue
        
        print(f"❌ Theme not found: {theme_name}")
        return False
    
    def export_theme(self, theme: AutoFireTheme, export_path: str) -> bool:
        """Export theme to specified location."""
        try:
            # Create export package with metadata
            export_data = {
                "autofire_theme_version": "1.0",
                "exported_date": datetime.now().isoformat(),
                "theme": theme.to_dict()
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"📤 Theme exported: {export_path}")
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    def import_theme(self, import_path: str) -> Optional[AutoFireTheme]:
        """Import theme from external file."""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Handle different import formats
            if "theme" in import_data:
                # Full export package
                theme_data = import_data["theme"]
            else:
                # Direct theme file
                theme_data = import_data
            
            theme = AutoFireTheme.from_dict(theme_data)
            theme.metadata.category = ThemeCategory.CUSTOM
            
            # Save to custom themes directory
            self.save_theme(theme)
            
            print(f"📥 Theme imported: {theme.metadata.display_name}")
            return theme
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return None
    
    def set_active_theme(self, theme_name: str):
        """Set the active theme."""
        self.settings.setValue("active_theme", theme_name)
        print(f"🎨 Active theme set: {theme_name}")
    
    def get_active_theme(self) -> Optional[AutoFireTheme]:
        """Get the currently active theme."""
        theme_name = self.settings.value("active_theme", "classic")
        
        # Try to load the active theme
        for theme_file in self.themes_dir.rglob("*.autofire_theme"):
            try:
                theme = self.load_theme(str(theme_file))
                if theme.metadata.name == theme_name:
                    return theme
            except:
                continue
        
        # Fallback to classic theme
        for theme in ThemeLibrary.get_built_in_themes():
            if theme.metadata.name == "classic":
                return theme
        
        return None
    
    def backup_themes(self, backup_path: str) -> bool:
        """Create backup of all themes."""
        try:
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy entire themes directory
            shutil.copytree(
                self.themes_dir, 
                backup_dir / "themes", 
                dirs_exist_ok=True
            )
            
            # Create backup metadata
            backup_info = {
                "backup_date": datetime.now().isoformat(),
                "theme_count": len(list(self.themes_dir.rglob("*.autofire_theme"))),
                "autofire_version": "2024.1"
            }
            
            with open(backup_dir / "backup_info.json", 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            print(f"💾 Themes backed up to: {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def restore_themes(self, backup_path: str) -> bool:
        """Restore themes from backup."""
        try:
            backup_dir = Path(backup_path)
            themes_backup = backup_dir / "themes"
            
            if not themes_backup.exists():
                print("❌ No themes found in backup")
                return False
            
            # Create backup of current themes
            current_backup = self.themes_dir.parent / f"themes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree(self.themes_dir, current_backup)
            
            # Restore themes
            shutil.rmtree(self.themes_dir)
            shutil.copytree(themes_backup, self.themes_dir)
            
            print(f"🔄 Themes restored from: {backup_path}")
            print(f"📁 Previous themes backed up to: {current_backup}")
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def get_theme_statistics(self) -> Dict:
        """Get statistics about theme usage."""
        all_themes = self.get_all_themes()
        
        stats = {
            "total_themes": len(all_themes),
            "by_category": {},
            "active_theme": self.settings.value("active_theme", "classic"),
            "themes_directory": str(self.themes_dir),
            "last_updated": datetime.now().isoformat()
        }
        
        # Count by category
        for category in ThemeCategory:
            category_themes = [t for t in all_themes if t.metadata.category == category]
            stats["by_category"][category.value] = len(category_themes)
        
        return stats


class ThemeApplicationService:
    """Service for applying themes to AutoFire application."""
    
    def __init__(self):
        self.persistence = ThemePersistence()
        self.current_theme = None
    
    def apply_theme(self, theme: AutoFireTheme) -> str:
        """Apply theme to AutoFire interface and return stylesheet."""
        self.current_theme = theme
        
        # Save as active theme
        self.persistence.set_active_theme(theme.metadata.name)
        
        # Generate complete stylesheet
        stylesheet = self.generate_application_stylesheet(theme)
        
        print(f"🎨 Applied theme: {theme.metadata.display_name}")
        return stylesheet
    
    def generate_application_stylesheet(self, theme: AutoFireTheme) -> str:
        """Generate complete Qt stylesheet for the theme."""
        colors = theme.colors
        metadata = theme.metadata
        
        # Base styles
        base_font = f"{metadata.font_size}pt '{metadata.font_family}'"
        border_radius = "4px" if metadata.rounded_corners else "0px"
        
        stylesheet = f"""
        /* AutoFire Application Stylesheet */
        /* Theme: {theme.metadata.display_name} */
        
        /* Main Application */
        QApplication {{
            font: {base_font};
            color: {colors.text_primary};
            background-color: {colors.background_primary};
        }}
        
        QMainWindow {{
            background-color: {colors.background_primary};
            color: {colors.text_primary};
        }}
        
        /* General Widgets */
        QWidget {{
            background-color: {colors.background_primary};
            color: {colors.text_primary};
            border: none;
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {colors.primary};
            color: {colors.text_inverse};
            border: 1px solid {colors.border_active};
            padding: 8px 16px;
            border-radius: {border_radius};
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {colors.secondary};
            border-color: {colors.secondary};
        }}
        
        QPushButton:pressed {{
            background-color: {colors.secondary};
            border-color: {colors.text_primary};
        }}
        
        QPushButton:disabled {{
            background-color: {colors.background_tertiary};
            color: {colors.text_disabled};
            border-color: {colors.border};
        }}
        
        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors.input_background};
            color: {colors.text_primary};
            border: 2px solid {colors.input_border};
            padding: 6px;
            border-radius: {border_radius};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {colors.border_active};
        }}
        
        /* Combo Boxes */
        QComboBox {{
            background-color: {colors.input_background};
            color: {colors.text_primary};
            border: 2px solid {colors.input_border};
            padding: 6px;
            border-radius: {border_radius};
        }}
        
        QComboBox:focus {{
            border-color: {colors.border_active};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {colors.text_primary};
        }}
        
        /* Lists and Trees */
        QListWidget, QTreeWidget, QTableWidget {{
            background-color: {colors.background_secondary};
            color: {colors.text_primary};
            border: 1px solid {colors.border};
            alternate-background-color: {colors.background_tertiary};
        }}
        
        QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {{
            background-color: {colors.primary};
            color: {colors.text_inverse};
        }}
        
        QListWidget::item:hover, QTreeWidget::item:hover, QTableWidget::item:hover {{
            background-color: {colors.background_tertiary};
        }}
        
        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {colors.border};
            background-color: {colors.background_secondary};
        }}
        
        QTabBar::tab {{
            background-color: {colors.background_tertiary};
            color: {colors.text_primary};
            padding: 8px 16px;
            margin-right: 2px;
            border: 1px solid {colors.border};
            border-bottom: none;
            border-top-left-radius: {border_radius};
            border-top-right-radius: {border_radius};
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors.background_secondary};
            border-bottom: 2px solid {colors.primary};
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors.background_primary};
        }}
        
        /* Group Boxes */
        QGroupBox {{
            font-weight: bold;
            color: {colors.text_primary};
            border: 2px solid {colors.border};
            border-radius: {border_radius};
            margin-top: 10px;
            padding-top: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}
        
        /* Sliders */
        QSlider::groove:horizontal {{
            border: 1px solid {colors.border};
            height: 8px;
            background: {colors.background_tertiary};
            border-radius: 4px;
        }}
        
        QSlider::handle:horizontal {{
            background: {colors.primary};
            border: 1px solid {colors.border_active};
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {colors.secondary};
        }}
        
        /* Progress Bars */
        QProgressBar {{
            border: 1px solid {colors.border};
            border-radius: {border_radius};
            text-align: center;
            background-color: {colors.background_tertiary};
        }}
        
        QProgressBar::chunk {{
            background-color: {colors.success};
            border-radius: {border_radius};
        }}
        
        /* Scroll Bars */
        QScrollBar:vertical {{
            background: {colors.background_tertiary};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {colors.primary};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {colors.secondary};
        }}
        
        QScrollBar:horizontal {{
            background: {colors.background_tertiary};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {colors.primary};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {colors.secondary};
        }}
        
        /* Status indicators */
        .status-success {{
            background-color: {colors.success};
            color: white;
            border-radius: {border_radius};
            padding: 4px 8px;
        }}
        
        .status-warning {{
            background-color: {colors.warning};
            color: black;
            border-radius: {border_radius};
            padding: 4px 8px;
        }}
        
        .status-danger {{
            background-color: {colors.danger};
            color: white;
            border-radius: {border_radius};
            padding: 4px 8px;
        }}
        
        .status-info {{
            background-color: {colors.info};
            color: white;
            border-radius: {border_radius};
            padding: 4px 8px;
        }}
        
        /* CAD-specific styles */
        .cad-drawing-area {{
            background-color: {colors.cad_background};
            border: 2px solid {colors.border};
        }}
        
        .cad-toolbar {{
            background-color: {colors.background_tertiary};
            border-bottom: 1px solid {colors.border};
        }}
        
        /* Fire alarm device colors */
        .device-smoke {{
            color: {colors.smoke_detector};
        }}
        
        .device-heat {{
            color: {colors.heat_detector};
        }}
        
        .device-pull {{
            color: {colors.pull_station};
        }}
        
        .device-horn-strobe {{
            color: {colors.horn_strobe};
        }}
        
        .device-panel {{
            color: {colors.panel};
        }}
        
        /* Circuit colors */
        .circuit-slc {{
            color: {colors.slc_circuit};
        }}
        
        .circuit-nac {{
            color: {colors.nac_circuit};
        }}
        
        .circuit-power {{
            color: {colors.power_circuit};
        }}
        """
        
        # Add shadow effects if enabled
        if metadata.shadow_effects:
            stylesheet += f"""
            
            /* Shadow Effects */
            QPushButton {{
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }}
            
            QGroupBox {{
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }}
            """
        
        return stylesheet
    
    def get_device_style(self, device_type: str) -> str:
        """Get CSS class for device type."""
        device_classes = {
            "smoke_detector": "device-smoke",
            "heat_detector": "device-heat",
            "pull_station": "device-pull",
            "horn_strobe": "device-horn-strobe",
            "panel": "device-panel"
        }
        return device_classes.get(device_type, "")
    
    def get_circuit_style(self, circuit_type: str) -> str:
        """Get CSS class for circuit type."""
        circuit_classes = {
            "SLC": "circuit-slc",
            "NAC": "circuit-nac",
            "POWER": "circuit-power"
        }
        return circuit_classes.get(circuit_type, "")
    
    def reload_active_theme(self) -> Optional[str]:
        """Reload and apply the active theme."""
        active_theme = self.persistence.get_active_theme()
        if active_theme:
            return self.apply_theme(active_theme)
        return None


def create_theme_persistence_demo():
    """Demo of theme persistence functionality."""
    print("🎨 AutoFire Theme Persistence Demo")
    print("=" * 40)
    
    # Initialize persistence
    persistence = ThemePersistence()
    service = ThemeApplicationService()
    
    # Show theme statistics
    stats = persistence.get_theme_statistics()
    print(f"📊 Theme Statistics:")
    print(f"   Total themes: {stats['total_themes']}")
    print(f"   Active theme: {stats['active_theme']}")
    print(f"   Themes directory: {stats['themes_directory']}")
    
    for category, count in stats["by_category"].items():
        print(f"   {category.replace('_', ' ').title()}: {count}")
    
    print("\n🔧 Available Operations:")
    print("✅ Save custom themes")
    print("✅ Load themes by category")
    print("✅ Import/export theme packages")
    print("✅ Theme backup and restore")
    print("✅ Generate complete Qt stylesheets")
    print("✅ CAD and fire alarm specific styling")
    
    # Test theme application
    active_theme = persistence.get_active_theme()
    if active_theme:
        print(f"\n🎨 Current theme: {active_theme.metadata.display_name}")
        stylesheet = service.apply_theme(active_theme)
        print(f"   Stylesheet generated: {len(stylesheet)} characters")
    
    return True


if __name__ == "__main__":
    create_theme_persistence_demo()