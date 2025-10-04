from typing import Any

from PySide6 import QtGui

# Modern color schemes
THEMES = {
    "dark": {
        "name": "Dark Professional",
        "colors": {
            "window": "#2d2d30",
            "window_text": "#ffffff",
            "base": "#1e1e1e",
            "alternate_base": "#2d2d30",
            "text": "#ffffff",
            "button": "#3c3c3c",
            "button_text": "#ffffff",
            "highlight": "#0078d4",
            "highlighted_text": "#ffffff",
            "border": "#555555",
            "grid": "#404040",
            "grid_minor": "#333333",
            "device_glyph": "#d8d8d8",
            "device_label": "#eaeaea",
            "wire": "#2aa36b",
            "selection": "#60a5fa",
        },
    },
    "light": {
        "name": "Light Professional",
        "colors": {
            "window": "#f8f9fa",
            "window_text": "#212529",
            "base": "#ffffff",
            "alternate_base": "#f8f9fa",
            "text": "#212529",
            "button": "#e9ecef",
            "button_text": "#212529",
            "highlight": "#0078d4",
            "highlighted_text": "#ffffff",
            "border": "#dee2e6",
            "grid": "#e9ecef",
            "grid_minor": "#f8f9fa",
            "device_glyph": "#6c757d",
            "device_label": "#495057",
            "wire": "#28a745",
            "selection": "#0078d4",
        },
    },
    "blue": {
        "name": "Blue Professional",
        "colors": {
            "window": "#1a365d",
            "window_text": "#ffffff",
            "base": "#2d3748",
            "alternate_base": "#1a365d",
            "text": "#ffffff",
            "button": "#2b6cb0",
            "button_text": "#ffffff",
            "highlight": "#3182ce",
            "highlighted_text": "#ffffff",
            "border": "#4a5568",
            "grid": "#4a5568",
            "grid_minor": "#2d3748",
            "device_glyph": "#e2e8f0",
            "device_label": "#f7fafc",
            "wire": "#38b2ac",
            "selection": "#63b3ed",
        },
    },
    "high_contrast": {
        "name": "High Contrast",
        "colors": {
            "window": "#000000",
            "window_text": "#ffffff",
            "base": "#000000",
            "alternate_base": "#1a1a1a",
            "text": "#ffffff",
            "button": "#000000",
            "button_text": "#ffffff",
            "highlight": "#ffff00",
            "highlighted_text": "#000000",
            "border": "#ffffff",
            "grid": "#666666",
            "grid_minor": "#333333",
            "device_glyph": "#ffffff",
            "device_label": "#ffffff",
            "wire": "#00ff00",
            "selection": "#ffff00",
        },
    },
}


def apply_theme(app, name: str) -> dict[str, Any]:
    """Apply a theme to the application and return the theme colors."""
    name = (name or "dark").lower()
    theme_data = THEMES.get(name, THEMES["dark"])

    pal = app.palette()
    colors = theme_data["colors"]

    # Apply palette colors
    pal.setColor(pal.ColorRole.Window, QtGui.QColor(colors["window"]))
    pal.setColor(pal.ColorRole.WindowText, QtGui.QColor(colors["window_text"]))
    pal.setColor(pal.ColorRole.Base, QtGui.QColor(colors["base"]))
    pal.setColor(pal.ColorRole.AlternateBase, QtGui.QColor(colors["alternate_base"]))
    pal.setColor(pal.ColorRole.Text, QtGui.QColor(colors["text"]))
    pal.setColor(pal.ColorRole.Button, QtGui.QColor(colors["button"]))
    pal.setColor(pal.ColorRole.ButtonText, QtGui.QColor(colors["button_text"]))
    pal.setColor(pal.ColorRole.Highlight, QtGui.QColor(colors["highlight"]))
    pal.setColor(pal.ColorRole.HighlightedText, QtGui.QColor(colors["highlighted_text"]))

    app.setPalette(pal)

    # Apply modern stylesheet
    stylesheet = f"""
    /* Modern Professional Styling */

    /* Main Window */
    QMainWindow {{
        background-color: {colors["window"]};
        color: {colors["window_text"]};
    }}

    /* Toolbars */
    QToolBar {{
        background-color: {colors["button"]};
        border: 1px solid {colors["border"]};
        border-radius: 4px;
        margin: 2px;
        padding: 2px;
        spacing: 4px;
    }}

    QToolBar::separator {{
        background-color: {colors["border"]};
        width: 1px;
        margin: 4px;
    }}

    /* Menus */
    QMenu {{
        background-color: {colors["base"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        border-radius: 4px;
        padding: 4px;
    }}

    QMenu::item {{
        padding: 6px 20px;
        border-radius: 3px;
        margin: 1px;
    }}

    QMenu::item:selected {{
        background-color: {colors["highlight"]};
        color: {colors["highlighted_text"]};
    }}

    QMenu::item:pressed {{
        background-color: {colors["button"]};
    }}

    /* Menu Bar */
    QMenuBar {{
        background-color: {colors["window"]};
        color: {colors["window_text"]};
        border-bottom: 1px solid {colors["border"]};
    }}

    QMenuBar::item {{
        background-color: transparent;
        padding: 6px 12px;
        border-radius: 3px;
    }}

    QMenuBar::item:selected {{
        background-color: {colors["highlight"]};
        color: {colors["highlighted_text"]};
    }}

    /* Buttons */
    QPushButton {{
        background-color: {colors["button"]};
        color: {colors["button_text"]};
        border: 1px solid {colors["border"]};
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: 500;
    }}

    QPushButton:hover {{
        background-color: {colors["highlight"]};
        color: {colors["highlighted_text"]};
        border-color: {colors["highlight"]};
    }}

    QPushButton:pressed {{
        background-color: {colors["button"]};
        border-color: {colors["highlight"]};
    }}

    /* Tree Widget (Device Palette) */
    QTreeWidget {{
        background-color: {colors["base"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        border-radius: 4px;
        alternate-background-color: {colors["alternate_base"]};
        selection-background-color: {colors["highlight"]};
        selection-color: {colors["highlighted_text"]};
    }}

    QTreeWidget::item {{
        padding: 4px;
        border-radius: 2px;
    }}

    QTreeWidget::item:selected {{
        background-color: {colors["highlight"]};
        color: {colors["highlighted_text"]};
    }}

    QTreeWidget::item:hover {{
        background-color: {colors["button"]};
    }}

    /* Dock Widgets */
    QDockWidget {{
        titlebar-close-icon: url(close.png);
        titlebar-normal-icon: url(float.png);
    }}

    QDockWidget::title {{
        background-color: {colors["button"]};
        color: {colors["button_text"]};
        border: 1px solid {colors["border"]};
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        padding: 6px 8px;
        font-weight: 600;
        text-align: left;
    }}

    /* Status Bar */
    QStatusBar {{
        background-color: {colors["button"]};
        color: {colors["button_text"]};
        border-top: 1px solid {colors["border"]};
    }}

    QStatusBar QLabel {{
        padding: 2px 8px;
    }}

    /* Scroll Bars */
    QScrollBar:vertical {{
        background-color: {colors["base"]};
        width: 16px;
        border-radius: 8px;
        margin: 2px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {colors["border"]};
        border-radius: 6px;
        min-height: 20px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {colors["highlight"]};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
    }}

    /* Graphics View (Canvas) */
    QGraphicsView {{
        background-color: {colors["base"]};
        border: 1px solid {colors["border"]};
        border-radius: 2px;
    }}

    /* Custom styling for CAD elements */
    /* These will be applied programmatically to graphics items */
    """

    app.setStyleSheet(stylesheet)

    return theme_data


def get_available_themes() -> dict[str, str]:
    """Get dictionary of available theme names and display names."""
    return {key: theme["name"] for key, theme in THEMES.items()}


def get_theme_colors(theme_name: str) -> dict[str, str]:
    """Get the color dictionary for a specific theme."""
    theme_data = THEMES.get(theme_name.lower(), THEMES["dark"])
    return theme_data["colors"]
