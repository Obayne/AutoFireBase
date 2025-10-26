"""
AutoFire Design System - Professional UI/UX Standards

This module defines the comprehensive design system for AutoFire to ensure
consistent, professional appearance across all UI components.

Competitive positioning: Surpass FireCAD/AlarmCAD with modern, clean design
that professionals expect from premium CAD software.
"""

from dataclasses import dataclass
from enum import Enum
from importlib.util import find_spec
from typing import TYPE_CHECKING

# Only detect availability; avoid importing Qt types to keep this module lightweight
PYSIDE6_AVAILABLE = find_spec("PySide6") is not None

if TYPE_CHECKING:
    # For type hints only; avoids runtime import cost
    from PySide6.QtWidgets import QApplication  # pragma: no cover

# No runtime Qt imports here; functions import lazily as needed.


class AutoFireColor(Enum):
    """FlameCAD color palette - professional dark theme for fire alarm industry."""

    # Primary Brand Colors (Dark Theme)
    PRIMARY = "#FF4444"  # Bright fire red - high visibility
    SECONDARY = "#CC2222"  # Darker red for accents
    ACCENT = "#FF6B35"  # Orange - call-to-action elements

    # Dark Theme Background Colors
    BACKGROUND = "#1A1A1A"  # Very dark gray - main background
    BACKGROUND_PRIMARY = "#1A1A1A"  # Alias for main background
    BACKGROUND_SECONDARY = "#2A2A2A"  # Secondary background
    BACKGROUND_ACCENT = "#333333"  # Accent background
    SURFACE_PRIMARY = "#2D2D2D"  # Dark gray - primary surfaces/panels
    SURFACE_SECONDARY = "#3A3A3A"  # Medium gray - secondary surfaces
    SURFACE_OVERLAY = "#454545"  # Lighter gray - overlays/modals

    # Text Colors (High Contrast)
    TEXT_PRIMARY = "#FFFFFF"  # White - primary text
    TEXT_SECONDARY = "#D1D5DB"  # Light gray - secondary text
    TEXT_MUTED = "#9CA3AF"  # Muted gray - disabled/hint text
    TEXT_ON_PRIMARY = "#FFFFFF"  # White text on primary colors

    # Border and Separator Colors
    BORDER_PRIMARY = "#525252"  # Medium gray - main borders
    BORDER_SECONDARY = "#404040"  # Darker gray - subtle borders
    BORDER_LIGHT = "#666666"  # Light gray - light borders
    BORDER_MEDIUM = "#555555"  # Medium gray - medium borders
    DIVIDER = "#383838"  # Dark gray - section dividers

    # Interactive Element Colors
    BUTTON_HOVER = "#555555"  # Hover state for buttons
    BUTTON_PRESSED = "#666666"  # Pressed state for buttons
    BUTTON_PRIMARY = "#FF4444"  # Primary button color
    BUTTON_SECONDARY = "#666666"  # Secondary button color
    HOVER_LIGHT = "#4A4A4A"  # Light hover state
    SELECTION_BG = "#FF4444"  # Selection background
    SELECTION_TEXT = "#FFFFFF"  # Selection text

    # Fire Alarm Circuit Colors (High Contrast Dark Theme)
    CIRCUIT_NAC = "#FFC107"  # NAC circuits - yellow
    CIRCUIT_SLC = "#DC3545"  # SLC circuits - red
    CIRCUIT_POWER = "#FF6B35"  # Power circuits - orange
    CIRCUIT_CONTROL = "#FF8844"  # Control circuits - orange
    CIRCUIT_TELEPHONE = "#44DD88"  # Telephone circuits - green

    # Compliance Status Colors (Dark Theme)
    COMPLIANCE_PASS = "#22C55E"  # Bright green - NFPA compliant
    COMPLIANCE_WARNING = "#F59E0B"  # Bright amber - review required
    COMPLIANCE_FAIL = "#EF4444"  # Bright red - code violation

    # Input Field Colors
    INPUT_BG = "#404040"  # Dark gray - input backgrounds
    INPUT_BORDER = "#666666"  # Medium gray - input borders
    INPUT_FOCUS = "#FF6B35"  # Orange - focused input border
    INPUT_TEXT = "#FFFFFF"  # White - input text

    SELECTION_PRIMARY = "#DBEAFE"  # Primary selection - light blue
    SELECTION_SECONDARY = "#FEF3C7"  # Secondary selection - light amber


@dataclass
class AutoFireTypography:
    """Typography system with professional font hierarchy."""

    # Font Families
    PRIMARY_FONT = "Segoe UI"  # Windows default - clean, readable
    MONOSPACE_FONT = "Consolas"  # Code/data - monospaced
    FALLBACK_FONTS = ["Arial", "Helvetica", "sans-serif"]

    # Font Sizes (in points)
    DISPLAY_LARGE = 24  # Major headings
    DISPLAY_MEDIUM = 20  # Section headings
    DISPLAY_SMALL = 18  # Subsection headings

    TITLE_LARGE = 16  # Panel titles
    TITLE_MEDIUM = 14  # Group titles
    TITLE_SMALL = 12  # Widget labels

    BODY_LARGE = 11  # Primary body text
    BODY_MEDIUM = 10  # Secondary body text
    BODY_SMALL = 9  # Helper text

    CAPTION = 8  # Captions, footnotes

    # Font Weights
    WEIGHT_LIGHT = 300
    WEIGHT_NORMAL = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700


@dataclass
class AutoFireSpacing:
    """Spacing system for consistent layouts."""

    # Base unit (pixels) - all spacing derives from this
    BASE_UNIT = 8

    # Spacing scale
    XS = BASE_UNIT // 2  # 4px - tight spacing
    SM = BASE_UNIT  # 8px - small spacing
    MD = BASE_UNIT * 2  # 16px - medium spacing
    LG = BASE_UNIT * 3  # 24px - large spacing
    XL = BASE_UNIT * 4  # 32px - extra large spacing
    XXL = BASE_UNIT * 6  # 48px - section spacing

    # Specific use cases
    WIDGET_PADDING = MD  # 16px - standard widget padding
    PANEL_PADDING = LG  # 24px - panel padding
    SECTION_SPACING = XXL  # 48px - between major sections

    BUTTON_PADDING_X = LG  # 24px - horizontal button padding
    BUTTON_PADDING_Y = SM  # 8px - vertical button padding

    TAB_PADDING = MD  # 16px - tab padding
    GROUPBOX_PADDING = LG  # 24px - groupbox padding


@dataclass
class AutoFireBorderRadius:
    """Border radius system for modern appearance."""

    NONE = 0  # Sharp corners
    SM = 4  # Small radius - buttons, inputs
    MD = 6  # Medium radius - panels
    LG = 8  # Large radius - major containers
    XL = 12  # Extra large radius - modals
    PILL = 9999  # Fully rounded - pills, badges


class AutoFireStyleSheet:
    """CSS stylesheet generator for consistent styling."""

    @staticmethod
    def get_button_style(
        bg_color: str = AutoFireColor.PRIMARY.value,
        text_color: str = AutoFireColor.TEXT_ON_PRIMARY.value,
        size: str = "medium",
    ) -> str:
        """Generate button stylesheet with FlameCAD dark theme design standards."""

        padding_map = {
            "small": f"{AutoFireSpacing.SM}px {AutoFireSpacing.MD}px",
            "medium": f"{AutoFireSpacing.SM}px {AutoFireSpacing.LG}px",
            "large": f"{AutoFireSpacing.MD}px {AutoFireSpacing.XL}px",
        }

        font_map = {
            "small": f"{AutoFireTypography.BODY_SMALL}pt",
            "medium": f"{AutoFireTypography.BODY_MEDIUM}pt",
            "large": f"{AutoFireTypography.BODY_LARGE}pt",
        }

        return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            border: none;
            border-radius: {AutoFireBorderRadius.SM}px;
            padding: {padding_map.get(size, padding_map["medium"])};
            font-family: {AutoFireTypography.PRIMARY_FONT};
            font-size: {font_map.get(size, font_map["medium"])};
            font-weight: {AutoFireTypography.WEIGHT_MEDIUM};
            min-height: 32px;
        }}

        QPushButton:hover {{
            background-color: {AutoFireColor.BUTTON_HOVER.value};
        }}

        QPushButton:pressed {{
            background-color: {AutoFireColor.BUTTON_PRESSED.value};
        }}

        QPushButton:disabled {{
            background-color: {AutoFireColor.BORDER_PRIMARY.value};
            color: {AutoFireColor.TEXT_MUTED.value};
        }}
        """

    @staticmethod
    def get_panel_style() -> str:
        """Generate panel stylesheet with FlameCAD dark theme design standards."""
        return f"""
        QGroupBox {{
            font-family: {AutoFireTypography.PRIMARY_FONT};
            font-size: {AutoFireTypography.TITLE_MEDIUM}pt;
            font-weight: {AutoFireTypography.WEIGHT_SEMIBOLD};
            color: {AutoFireColor.TEXT_PRIMARY.value};
            border: 2px solid {AutoFireColor.BORDER_PRIMARY.value};
            border-radius: {AutoFireBorderRadius.MD}px;
            margin-top: 12px;
            padding-top: {AutoFireSpacing.MD}px;
            background-color: {AutoFireColor.SURFACE_PRIMARY.value};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {AutoFireSpacing.MD}px;
            padding: 0 {AutoFireSpacing.SM}px;
            background-color: {AutoFireColor.SURFACE_PRIMARY.value};
            color: {AutoFireColor.TEXT_PRIMARY.value};
        }}
        """

    @staticmethod
    def get_table_style() -> str:
        """Generate table stylesheet with AutoFire design standards."""
        return f"""
        QTableWidget, QTableView {{
            font-family: {AutoFireTypography.PRIMARY_FONT};
            font-size: {AutoFireTypography.BODY_MEDIUM}pt;
            color: {AutoFireColor.TEXT_PRIMARY.value};
            background-color: {AutoFireColor.BACKGROUND_PRIMARY.value};
            border: 1px solid {AutoFireColor.BORDER_LIGHT.value};
            border-radius: {AutoFireBorderRadius.SM}px;
            gridline-color: {AutoFireColor.BORDER_LIGHT.value};
            selection-background-color: {AutoFireColor.SELECTION_PRIMARY.value};
        }}

        QTableWidget::item, QTableView::item {{
            padding: {AutoFireSpacing.SM}px;
            border: none;
        }}

        QTableWidget::item:hover, QTableView::item:hover {{
            background-color: {AutoFireColor.HOVER_LIGHT.value};
        }}

        QHeaderView::section {{
            background-color: {AutoFireColor.BACKGROUND_ACCENT.value};
            color: {AutoFireColor.TEXT_PRIMARY.value};
            font-weight: {AutoFireTypography.WEIGHT_SEMIBOLD};
            padding: {AutoFireSpacing.SM}px {AutoFireSpacing.MD}px;
            border: none;
            border-right: 1px solid {AutoFireColor.BORDER_LIGHT.value};
            border-bottom: 1px solid {AutoFireColor.BORDER_LIGHT.value};
        }}
        """

    @staticmethod
    def get_input_style() -> str:
        """Generate input field stylesheet with AutoFire design standards."""
        return f"""
        QLineEdit, QTextEdit, QComboBox {{
            font-family: {AutoFireTypography.PRIMARY_FONT};
            font-size: {AutoFireTypography.BODY_MEDIUM}pt;
            color: {AutoFireColor.TEXT_PRIMARY.value};
            background-color: {AutoFireColor.BACKGROUND_PRIMARY.value};
            border: 2px solid {AutoFireColor.BORDER_LIGHT.value};
            border-radius: {AutoFireBorderRadius.SM}px;
            padding: {AutoFireSpacing.SM}px {AutoFireSpacing.MD}px;
            min-height: 20px;
        }}

        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border-color: {AutoFireColor.BUTTON_PRIMARY.value};
        }}

        QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled {{
            background-color: {AutoFireColor.BACKGROUND_SECONDARY.value};
            color: {AutoFireColor.TEXT_MUTED.value};
        }}

        QSpinBox, QDoubleSpinBox {{
            font-family: {AutoFireTypography.PRIMARY_FONT};
            font-size: {AutoFireTypography.BODY_MEDIUM}pt;
            color: {AutoFireColor.TEXT_PRIMARY.value};
            background-color: {AutoFireColor.BACKGROUND_PRIMARY.value};
            border: 2px solid {AutoFireColor.BORDER_LIGHT.value};
            border-radius: {AutoFireBorderRadius.SM}px;
            padding: {AutoFireSpacing.SM}px;
            min-height: 20px;
        }}
        """

    @staticmethod
    def get_tab_style() -> str:
        """Generate tab widget stylesheet with AutoFire design standards."""
        return f"""
        QTabWidget::pane {{
            border: 2px solid {AutoFireColor.BORDER_LIGHT.value};
            border-radius: {AutoFireBorderRadius.MD}px;
            background-color: {AutoFireColor.BACKGROUND_PRIMARY.value};
            margin-top: -1px;
        }}

        QTabBar::tab {{
            font-family: {AutoFireTypography.PRIMARY_FONT};
            font-size: {AutoFireTypography.BODY_MEDIUM}pt;
            font-weight: {AutoFireTypography.WEIGHT_MEDIUM};
            color: {AutoFireColor.TEXT_SECONDARY.value};
            background-color: {AutoFireColor.BACKGROUND_SECONDARY.value};
            border: 2px solid {AutoFireColor.BORDER_LIGHT.value};
            border-bottom: none;
            border-radius: {AutoFireBorderRadius.SM}px {AutoFireBorderRadius.SM}px 0 0;
            padding: {AutoFireSpacing.SM}px {AutoFireSpacing.LG}px;
            margin-right: 2px;
            min-width: 80px;
        }}

        QTabBar::tab:selected {{
            color: {AutoFireColor.TEXT_PRIMARY.value};
            background-color: {AutoFireColor.BACKGROUND_PRIMARY.value};
            border-color: {AutoFireColor.BUTTON_PRIMARY.value};
            border-bottom: 2px solid {AutoFireColor.BACKGROUND_PRIMARY.value};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {AutoFireColor.HOVER_LIGHT.value};
        }}
        """

    @staticmethod
    def get_application_style() -> str:
        """Generate main application stylesheet."""
        return f"""
        QMainWindow {{
            background-color: {AutoFireColor.BACKGROUND_PRIMARY.value};
            color: {AutoFireColor.TEXT_PRIMARY.value};
            font-family: {AutoFireTypography.PRIMARY_FONT};
            font-size: {AutoFireTypography.BODY_MEDIUM}pt;
        }}

        QWidget {{
            background-color: {AutoFireColor.BACKGROUND_PRIMARY.value};
            color: {AutoFireColor.TEXT_PRIMARY.value};
        }}

        QLabel {{
            font-family: {AutoFireTypography.PRIMARY_FONT};
            color: {AutoFireColor.TEXT_PRIMARY.value};
        }}

        QFrame {{
            border: 1px solid {AutoFireColor.BORDER_LIGHT.value};
            border-radius: {AutoFireBorderRadius.SM}px;
        }}

        QSplitter::handle {{
            background-color: {AutoFireColor.BORDER_MEDIUM.value};
        }}

        QSplitter::handle:horizontal {{
            width: 4px;
        }}

        QSplitter::handle:vertical {{
            height: 4px;
        }}
        """

    @staticmethod
    def _darken_color(hex_color: str, factor: float) -> str:
        """Darken a hex color by the given factor (0.0 to 1.0)."""
        # Simple darkening - multiply RGB values by (1 - factor)
        hex_color = hex_color.lstrip("#")
        rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * (1 - factor)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    @staticmethod
    def button_primary() -> str:
        """Primary button stylesheet - dark theme."""
        return f"""
            QPushButton {{
                background-color: {AutoFireColor.PRIMARY.value};
                color: {AutoFireColor.TEXT_ON_PRIMARY.value};
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {AutoFireColor.SECONDARY.value};
            }}
            QPushButton:pressed {{
                background-color: {AutoFireColor.ACCENT.value};
            }}
            QPushButton:disabled {{
                background-color: {AutoFireColor.BORDER_PRIMARY.value};
                color: {AutoFireColor.TEXT_MUTED.value};
            }}
        """

    @staticmethod
    def button_secondary() -> str:
        """Secondary button stylesheet - dark theme."""
        return f"""
            QPushButton {{
                background-color: {AutoFireColor.SURFACE_SECONDARY.value};
                color: {AutoFireColor.TEXT_PRIMARY.value};
                border: 2px solid {AutoFireColor.BORDER_PRIMARY.value};
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {AutoFireColor.BUTTON_HOVER.value};
                border-color: {AutoFireColor.ACCENT.value};
            }}
            QPushButton:pressed {{
                background-color: {AutoFireColor.BUTTON_PRESSED.value};
            }}
        """

    @staticmethod
    def button_success() -> str:
        """Success button stylesheet - dark theme."""
        return f"""
            QPushButton {{
                background-color: {AutoFireColor.COMPLIANCE_PASS.value};
                color: {AutoFireColor.TEXT_ON_PRIMARY.value};
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #1E8B3E;
            }}
        """

    @staticmethod
    def group_box() -> str:
        """Group box stylesheet - dark theme."""
        return f"""
            QGroupBox {{
                color: {AutoFireColor.TEXT_PRIMARY.value};
                border: 2px solid {AutoFireColor.BORDER_PRIMARY.value};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: {AutoFireColor.SURFACE_PRIMARY.value};
                font-weight: 600;
                font-size: 14px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: {AutoFireColor.ACCENT.value};
                font-weight: 700;
                background-color: {AutoFireColor.SURFACE_PRIMARY.value};
            }}
        """

    @staticmethod
    def input_field() -> str:
        """Input field stylesheet - dark theme."""
        return f"""
            QLineEdit, QComboBox, QSpinBox {{
                background-color: {AutoFireColor.INPUT_BG.value};
                color: {AutoFireColor.INPUT_TEXT.value};
                border: 2px solid {AutoFireColor.INPUT_BORDER.value};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                selection-background-color: {AutoFireColor.SELECTION_BG.value};
                selection-color: {AutoFireColor.SELECTION_TEXT.value};
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border-color: {AutoFireColor.INPUT_FOCUS.value};
                background-color: {AutoFireColor.SURFACE_SECONDARY.value};
            }}
            QComboBox::drop-down {{
                border: none;
                background-color: {AutoFireColor.ACCENT.value};
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                width: 25px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid white;
                margin: 2px;
            }}
        """


class AutoFireIconTheme:
    """Icon theme for consistent iconography."""

    # Icon mappings for common functions
    ICONS = {
        # Navigation
        "add": "➕",
        "remove": "🗑️",
        "edit": "✏️",
        "duplicate": "📋",
        "refresh": "🔄",
        "export": "📊",
        "import": "📥",
        "save": "💾",
        "open": "📂",
        # Circuit Types
        "circuit_slc": "🔵",
        "circuit_nac": "🔴",
        "circuit_power": "⚡",
        "circuit_control": "🎛️",
        "circuit_telephone": "📞",
        # Status
        "status_pass": "✅",
        "status_warning": "⚠️",
        "status_fail": "❌",
        "status_info": "ℹ️",
        # Tools
        "calculate": "🧮",
        "measure": "📏",
        "search": "🔍",
        "filter": "🔽",
        "settings": "⚙️",
        "help": "❓",
        # Fire Alarm Specific
        "detector": "🔥",
        "speaker": "🔊",
        "strobe": "💡",
        "panel": "📦",
        "annunciator": "📺",
        "pull_station": "🚨",
    }

    @staticmethod
    def get_icon(name: str) -> str:
        """Get icon character for the given name."""
        return AutoFireIconTheme.ICONS.get(name, "❓")


def apply_autofire_theme(app: "QApplication") -> None:
    """Apply the complete AutoFire theme to the application."""
    if not PYSIDE6_AVAILABLE:
        return

    # Combine all stylesheets
    complete_style = (
        AutoFireStyleSheet.get_application_style()
        + AutoFireStyleSheet.get_button_style()
        + AutoFireStyleSheet.get_panel_style()
        + AutoFireStyleSheet.get_table_style()
        + AutoFireStyleSheet.get_input_style()
        + AutoFireStyleSheet.get_tab_style()
    )

    app.setStyleSheet(complete_style)


def create_professional_font(
    size: int = AutoFireTypography.BODY_MEDIUM, weight: int = AutoFireTypography.WEIGHT_NORMAL
):
    """Create a professional font with AutoFire standards."""
    if not PYSIDE6_AVAILABLE:
        return None
    # Import within function to keep module import-light and typing happy
    try:
        from PySide6.QtGui import QFont as _QFont  # type: ignore
    except Exception:
        return None

    font = _QFont(AutoFireTypography.PRIMARY_FONT, size)
    try:
        font.setWeight(_QFont.Weight(weight))  # PySide6>=6.6 style
    except Exception:
        pass
    return font


def create_title_font(size: int = AutoFireTypography.TITLE_LARGE):
    """Create a title font with AutoFire standards."""
    return create_professional_font(size, AutoFireTypography.WEIGHT_SEMIBOLD)


def create_heading_font(size: int = AutoFireTypography.DISPLAY_MEDIUM):
    """Create a heading font with AutoFire standards."""
    return create_professional_font(size, AutoFireTypography.WEIGHT_BOLD)


# Pre-defined color functions for easy access
def get_circuit_color(circuit_type: str) -> str:
    """Get the standard color for a circuit type."""
    color_map = {
        "SLC": AutoFireColor.CIRCUIT_SLC.value,
        "NAC": AutoFireColor.CIRCUIT_NAC.value,
        "Power": AutoFireColor.CIRCUIT_POWER.value,
        "Control": AutoFireColor.CIRCUIT_CONTROL.value,
        "Telephone": AutoFireColor.CIRCUIT_TELEPHONE.value,
    }
    return color_map.get(circuit_type, AutoFireColor.TEXT_PRIMARY.value)


def get_compliance_color(status: str) -> str:
    """Get the standard color for compliance status."""
    color_map = {
        "PASS": AutoFireColor.COMPLIANCE_PASS.value,
        "WARNING": AutoFireColor.COMPLIANCE_WARNING.value,
        "FAIL": AutoFireColor.COMPLIANCE_FAIL.value,
    }
    return color_map.get(status, AutoFireColor.TEXT_SECONDARY.value)


if __name__ == "__main__":
    # Demo the design system
    print("🔥 FlameCAD Design System - Dark Theme")
    print("=" * 50)
    # Demo the design system
    primary_colors = [AutoFireColor.PRIMARY, AutoFireColor.SECONDARY, AutoFireColor.ACCENT]
    print(f"Primary Colors: {[color.value for color in primary_colors]}")
    print(f"Background: {AutoFireColor.BACKGROUND.value}")
    print(f"Surface: {AutoFireColor.SURFACE_PRIMARY.value}")
    print(f"Text: {AutoFireColor.TEXT_PRIMARY.value}")
    print(f"Typography: {AutoFireTypography.PRIMARY_FONT} at {AutoFireTypography.BODY_MEDIUM}pt")
    print(f"Spacing: {AutoFireSpacing.BASE_UNIT}px base unit")
    print("✅ Design system ready for application")
