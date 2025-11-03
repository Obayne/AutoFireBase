"""
Project Builder Menu - Routes users based on expertise level.

Expert -> Direct to CAD
Intermediate -> Guided instructions
Beginner -> Full educational workflow
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class ProjectBuilderMenu(QWidget):
    """Project builder menu with expertise-based routing."""

    # Signals for different workflows
    expert_mode_requested = Signal()  # Direct to CAD
    intermediate_mode_requested = Signal()  # Guided instructions
    beginner_mode_requested = Signal()  # Full educational

    def __init__(self, parent=None):
        super().__init__(parent)
        self.expertise_level = "intermediate"  # Default
        self._setup_ui()

    def _setup_ui(self):
        """Setup the project builder menu."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("🔥 AutoFire Project Builder")
        header.setStyleSheet(
            """
            font-size: 24px;
            font-weight: bold;
            color: #C41E3A;
            padding: 20px;
            text-align: center;
        """
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Subtitle
        subtitle = QLabel("Choose your experience level to get the right workflow")
        subtitle.setStyleSheet(
            """
            font-size: 14px;
            color: #666;
            padding-bottom: 20px;
            text-align: center;
        """
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Expertise selection
        expertise_group = QGroupBox("Your Fire Alarm Design Experience")
        expertise_layout = QVBoxLayout(expertise_group)

        self.expertise_buttons = QButtonGroup()

        # Expert level
        expert_radio = QRadioButton("🎯 Expert - I know fire alarm design inside and out")
        expert_radio.setObjectName("expert")
        expert_radio.setStyleSheet(
            """
            QRadioButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                color: #2d5a3d;
            }
        """
        )
        self.expertise_buttons.addButton(expert_radio, 0)
        expertise_layout.addWidget(expert_radio)

        expert_desc = QLabel(
            "   → Goes directly to CAD workspace. Load floor plans, place devices, design circuits."
        )
        expert_desc.setStyleSheet(
            "color: #666; font-style: italic; padding-left: 20px; margin-bottom: 10px;"
        )
        expertise_layout.addWidget(expert_desc)

        # Intermediate level
        intermediate_radio = QRadioButton(
            "⚡ Intermediate - I have some experience, but want guidance"
        )
        intermediate_radio.setObjectName("intermediate")
        intermediate_radio.setChecked(True)  # Default
        intermediate_radio.setStyleSheet(
            """
            QRadioButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                color: #1a237e;
            }
        """
        )
        self.expertise_buttons.addButton(intermediate_radio, 1)
        expertise_layout.addWidget(intermediate_radio)

        intermediate_desc = QLabel(
            "   → Provides helpful instructions and tips throughout the design process."
        )
        intermediate_desc.setStyleSheet(
            "color: #666; font-style: italic; padding-left: 20px; margin-bottom: 10px;"
        )
        expertise_layout.addWidget(intermediate_desc)

        # Beginner level
        beginner_radio = QRadioButton("📚 Beginner - I'm new to fire alarm design")
        beginner_radio.setObjectName("beginner")
        beginner_radio.setStyleSheet(
            """
            QRadioButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                color: #8B0000;
            }
        """
        )
        self.expertise_buttons.addButton(beginner_radio, 2)
        expertise_layout.addWidget(beginner_radio)

        beginner_desc = QLabel("   → Full educational workflow with NFPA 72 compliance training.")
        beginner_desc.setStyleSheet(
            "color: #666; font-style: italic; padding-left: 20px; margin-bottom: 10px;"
        )
        expertise_layout.addWidget(beginner_desc)

        self.expertise_buttons.buttonClicked.connect(self._on_expertise_changed)
        layout.addWidget(expertise_group)

        # Project type quick selection (for all levels)
        project_group = QGroupBox("Project Type (Optional)")
        project_layout = QVBoxLayout(project_group)

        project_label = QLabel("What type of building are you designing for?")
        project_layout.addWidget(project_label)

        # Quick project type buttons
        project_buttons_layout = QHBoxLayout()

        self.project_types = [
            ("🏢", "Office"),
            ("🏭", "Industrial"),
            ("🏫", "School"),
            ("🏥", "Healthcare"),
            ("🏨", "Hotel"),
            ("🏪", "Retail"),
        ]

        self.project_buttons = []
        for icon, name in self.project_types:
            btn = QPushButton(f"{icon}\n{name}")
            btn.setStyleSheet(
                """
                QPushButton {
                    padding: 15px;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    background-color: #f8f9fa;
                    font-size: 12px;
                }
                QPushButton:hover {
                    border-color: #C41E3A;
                    background-color: #fff;
                }
                QPushButton:checked {
                    background-color: #C41E3A;
                    color: white;
                    border-color: #C41E3A;
                }
            """
            )
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=name: self._on_project_type_selected(n))
            self.project_buttons.append(btn)
            project_buttons_layout.addWidget(btn)

        project_layout.addLayout(project_buttons_layout)
        layout.addWidget(project_group)

        # Start button
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("🚀 Start Project")
        self.start_button.setStyleSheet(
            """
            QPushButton {
                background-color: #C41E3A;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 15px 40px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #A01829;
            }
        """
        )
        self.start_button.clicked.connect(self._start_project)

        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        layout.addStretch()

        # Initialize default
        self.selected_project_type = None

    def _on_expertise_changed(self, button):
        """Handle expertise level change."""
        self.expertise_level = button.objectName()
        self._update_start_button_text()

    def _on_project_type_selected(self, project_type):
        """Handle project type selection."""
        # Uncheck other buttons
        for btn in self.project_buttons:
            if btn.text().split("\n")[1] != project_type:
                btn.setChecked(False)

        self.selected_project_type = project_type

    def _update_start_button_text(self):
        """Update start button text based on expertise level."""
        if self.expertise_level == "expert":
            self.start_button.setText("🎯 Launch CAD Workspace")
        elif self.expertise_level == "intermediate":
            self.start_button.setText("⚡ Start with Guidance")
        else:  # beginner
            self.start_button.setText("📚 Begin Learning Workflow")

    def _start_project(self):
        """Start project based on expertise level."""
        # Emit appropriate signal based on expertise
        if self.expertise_level == "expert":
            self.expert_mode_requested.emit()
        elif self.expertise_level == "intermediate":
            self.intermediate_mode_requested.emit()
        else:  # beginner
            self.beginner_mode_requested.emit()

    def get_project_info(self):
        """Get selected project information."""
        return {"expertise_level": self.expertise_level, "project_type": self.selected_project_type}
