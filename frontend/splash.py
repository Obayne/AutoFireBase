"""
AutoFire Splash Screen
Shows version info, recent projects, and project creation options.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SplashScreen(QDialog):
    """AutoFire splash screen with project selection."""

    # Signals
    new_project_requested = Signal()
    project_opened = Signal(str)  # project path

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("AutoFire - Fire Alarm CAD")
        self.setModal(True)
        self.setFixedSize(700, 500)

        self._setup_ui()
        self._load_recent_projects()

    def _setup_ui(self) -> None:
        """Set up the splash screen UI."""
        # Apply dark theme styling - cleaner and more spacious
        self.setStyleSheet(
            """
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #0078d4;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
            }
            QListWidget {
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                selection-background-color: #0078d4;
                alternate-background-color: #252526;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #404040;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #404040;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
                border-color: #666666;
            }
            QPushButton:pressed {
                background-color: #2c2c2c;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title section - more spacious
        title_layout = QVBoxLayout()
        title_layout.setSpacing(10)

        title_label = QLabel("AutoFire")
        title_font = QFont()
        title_font.setPointSize(32)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #0078d4; margin-bottom: 5px;")
        title_layout.addWidget(title_label)

        subtitle_label = QLabel("Professional Fire Alarm CAD System")
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #cccccc;")
        title_layout.addWidget(subtitle_label)

        version_label = QLabel("Version 0.8.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #888888; font-size: 11px;")
        title_layout.addWidget(version_label)

        layout.addLayout(title_layout)

        layout.addSpacing(30)

        # Recent projects section - less cramped
        recent_label = QLabel("Recent Projects")
        recent_label.setStyleSheet(
            "font-weight: bold; font-size: 16px; color: #ffffff; margin-bottom: 15px;"
        )
        layout.addWidget(recent_label)

        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(150)
        self.recent_list.setAlternatingRowColors(True)
        self.recent_list.setStyleSheet(
            """
            QListWidget {
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #404040;
                border-radius: 3px;
                margin-bottom: 2px;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
            }
            QListWidget::item:hover {
                background-color: #404040;
                border: 1px solid #666666;
            }
            QListWidget::item:alternate {
                background-color: #252526;
            }
        """
        )
        self.recent_list.itemDoubleClicked.connect(self._on_project_selected)
        layout.addWidget(self.recent_list)

        layout.addSpacing(40)

        # Buttons - more spaced out and prominent
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)

        self.new_button = QPushButton("New Project")
        self.new_button.setMinimumHeight(45)
        self.new_button.setStyleSheet(
            """
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 15px 30px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 160px;
            }
            QPushButton:hover {
                background-color: #106ebe;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #005a9e;
                transform: translateY(0px);
            }
        """
        )
        self.new_button.clicked.connect(self._on_new_project)
        button_layout.addWidget(self.new_button)

        self.open_button = QPushButton("Open Project")
        self.open_button.setMinimumHeight(45)
        self.open_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 15px 30px;
                border-radius: 6px;
                font-size: 14px;
                min-width: 160px;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
                border-color: #666666;
            }
            QPushButton:pressed {
                background-color: #2c2c2c;
            }
        """
        )
        self.open_button.clicked.connect(self._on_open_project)
        button_layout.addWidget(self.open_button)

        layout.addLayout(button_layout)

        layout.addStretch()

        # Footer - less prominent
        footer_label = QLabel("© 2025 AutoFire - Professional Fire Alarm CAD System")
        footer_label.setStyleSheet("color: #666666; font-size: 10px; margin-top: 30px;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer_label)

    def _load_recent_projects(self) -> None:
        """Load recent projects from settings."""
        try:
            settings_file = Path.home() / ".autofire" / "settings.json"
            if settings_file.exists():
                with open(settings_file) as f:
                    settings = json.load(f)
                    recent_projects = settings.get("recent_projects", [])

                    for project_path in recent_projects[:5]:  # Show last 5
                        if os.path.exists(project_path):
                            item = QListWidgetItem(os.path.basename(project_path))
                            item.setData(Qt.ItemDataRole.UserRole, project_path)
                            self.recent_list.addItem(item)
        except Exception:
            # If settings can't be loaded, just continue
            pass

    def _on_new_project(self) -> None:
        """Handle new project button click."""
        self.new_project_requested.emit()
        self.accept()

    def _on_open_project(self) -> None:
        """Handle open project button click."""
        # For now, just emit new project - we'll implement file dialog later
        self.new_project_requested.emit()
        self.accept()

    def _on_project_selected(self, item: QListWidgetItem) -> None:
        """Handle project selection from recent list."""
        project_path = item.data(Qt.ItemDataRole.UserRole)
        self.project_opened.emit(project_path)
        self.accept()


def show_splash_screen() -> str | None:
    """
    Show the splash screen and return the selected project path.
    Returns None if new project requested.
    """
    splash = SplashScreen()

    result = None

    def on_new_project():
        nonlocal result
        result = None

    def on_project_opened(path: str):
        nonlocal result
        result = path

    splash.new_project_requested.connect(on_new_project)
    splash.project_opened.connect(on_project_opened)

    splash.exec()

    return result
