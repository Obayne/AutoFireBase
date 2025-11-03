"""
Professional Settings Panel - Simple assistance level control.

Allows fire alarm professionals to:
1. Set assistance level (Off, Minimal, Full)
2. Configure AI suggestion aggressiveness
3. Jump straight into design work
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class ProfessionalSettingsPanel(QWidget):
    """Simple settings panel for professional assistance level."""

    settings_changed = Signal(dict)  # Emit when settings change
    ready_to_work = Signal()  # Emit when user wants to start designing

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = {
            "assistance_level": "minimal",  # off, minimal, full
            "ai_aggressiveness": 2,  # 0-4 scale
            "show_tips": True,
            "auto_compliance": True,
        }
        self._setup_ui()

    def _setup_ui(self):
        """Setup simple, clean interface."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("🔥 AutoFire Professional Setup")
        header.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            color: #C41E3A;
            padding: 10px;
            margin-bottom: 10px;
        """
        )
        layout.addWidget(header)

        # Assistance Level
        assistance_group = QGroupBox("Assistance Level")
        assistance_layout = QVBoxLayout(assistance_group)

        self.assistance_buttons = QButtonGroup()

        # Off - For experts who want zero hand-holding
        off_radio = QRadioButton("🚫 Off - Just let me work")
        off_radio.setObjectName("off")
        self.assistance_buttons.addButton(off_radio, 0)
        assistance_layout.addWidget(off_radio)

        # Minimal - Smart defaults without interruption
        minimal_radio = QRadioButton("⚡ Minimal - Smart defaults, no interruptions")
        minimal_radio.setObjectName("minimal")
        minimal_radio.setChecked(True)  # Default for professionals
        self.assistance_buttons.addButton(minimal_radio, 1)
        assistance_layout.addWidget(minimal_radio)

        # Full - Educational mode
        full_radio = QRadioButton("📚 Full - Educational guidance and tips")
        full_radio.setObjectName("full")
        self.assistance_buttons.addButton(full_radio, 2)
        assistance_layout.addWidget(full_radio)

        self.assistance_buttons.buttonClicked.connect(self._on_assistance_changed)
        layout.addWidget(assistance_group)

        # AI Suggestion Aggressiveness
        ai_group = QGroupBox("AI Suggestion Level")
        ai_layout = QVBoxLayout(ai_group)

        ai_label = QLabel("How aggressive should AI suggestions be?")
        ai_layout.addWidget(ai_label)

        self.ai_slider = QSlider(Qt.Horizontal)
        self.ai_slider.setRange(0, 4)
        self.ai_slider.setValue(2)
        self.ai_slider.setTickPosition(QSlider.TicksBelow)
        self.ai_slider.setTickInterval(1)
        self.ai_slider.valueChanged.connect(self._on_ai_changed)

        # Slider labels
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Silent"))
        slider_layout.addStretch()
        slider_layout.addWidget(QLabel("Moderate"))
        slider_layout.addStretch()
        slider_layout.addWidget(QLabel("Aggressive"))

        ai_layout.addWidget(self.ai_slider)
        ai_layout.addLayout(slider_layout)
        layout.addWidget(ai_group)

        # Action buttons
        button_layout = QHBoxLayout()

        # Start designing button - this is what professionals want
        start_button = QPushButton("🚀 Start Designing")
        start_button.setStyleSheet(
            """
            QPushButton {
                background-color: #C41E3A;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 30px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #A01829;
            }
        """
        )
        start_button.clicked.connect(self._start_designing)

        button_layout.addStretch()
        button_layout.addWidget(start_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        layout.addStretch()

    def _on_assistance_changed(self, button):
        """Handle assistance level change."""
        self.settings["assistance_level"] = button.objectName()
        self.settings_changed.emit(self.settings)

    def _on_ai_changed(self, value):
        """Handle AI aggressiveness change."""
        self.settings["ai_aggressiveness"] = value
        self.settings_changed.emit(self.settings)

    def _start_designing(self):
        """User wants to start designing - emit signal."""
        self.ready_to_work.emit()

    def get_settings(self):
        """Get current settings."""
        return self.settings.copy()
