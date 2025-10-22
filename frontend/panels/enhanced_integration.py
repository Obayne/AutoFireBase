"""
Integration patch for enhanced panel selection with expansion boards.
This file shows how to integrate the new enhanced panel dialog into the existing system builder.
"""

from PySide6 import QtWidgets

from frontend.panels.enhanced_panel_dialog import EnhancedPanelSelectionDialog


def create_enhanced_system_builder_patch():
    """
    Example of how to integrate the enhanced panel dialog into the system builder.
    This replaces the old panel selection with the new expansion board capable version.
    """

    # This would replace the _select_panel method in SystemBuilderPanel class
    def enhanced_select_panel(self):
        """Open enhanced panel selection dialog with expansion board support."""
        dialog = EnhancedPanelSelectionDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.panel_config = dialog.get_panel_config()
            self._update_enhanced_panel_display()
            self._load_compatible_devices()

            # Enable buttons if we have a valid panel config
            has_panel = self.panel_config and self.panel_config.get("panel")
            if hasattr(self, "export_button"):
                self.export_button.setEnabled(bool(has_panel))
            if hasattr(self, "addressing_button"):
                self.addressing_button.setEnabled(bool(has_panel))

    def enhanced_update_panel_display(self):
        """Update panel display to show expansion board information."""
        if not hasattr(self, "panel_config") or not self.panel_config:
            if hasattr(self, "panel_label"):
                self.panel_label.setText("No panel selected")
            if hasattr(self, "panel_details"):
                self.panel_details.clear()
            return

        panel = self.panel_config.get("panel", {})
        expansion_boards = self.panel_config.get("expansion_boards", [])
        capacity_summary = self.panel_config.get("capacity_summary", {})

        # Update panel label
        panel_text = f"{panel.get('manufacturer_name', 'Unknown')} {panel.get('model', 'Unknown')}"
        if expansion_boards:
            panel_text += f" + {len(expansion_boards)} expansion boards"

        if hasattr(self, "panel_label"):
            self.panel_label.setText(panel_text)

        # Update detailed information
        if hasattr(self, "panel_details"):
            # build details_html in smaller segments to avoid long source lines
            details_html = (
                "<h3>Fire Alarm Control Panel Configuration</h3>"
                + f"<p><b>Main Panel:</b> {panel.get('manufacturer_name', 'Unknown')} "
                + f"{panel.get('model', 'Unknown')}</p>"
                + f"<p><b>Panel Type:</b> {panel.get('panel_type', 'Unknown')}</p>"
                + "<h4>System Capacity</h4>"
                + "<p><b>Base Device Capacity:</b> "
                + str(capacity_summary.get("base_devices", 0))
                + " devices</p>"
            )

            if expansion_boards:
                _exp_count = len(expansion_boards)
                _exp_devices = capacity_summary.get("expansion_devices", 0)
                _total = capacity_summary.get("total_devices", 0)

                details_html += "<p><b>Expansion Boards:</b> " + str(_exp_count) + " selected</p>"

                details_html += (
                    "<p><b>Additional Device Capacity:</b> +" + str(_exp_devices) + " devices</p>"
                )

                details_html += (
                    "<p><b>Total System Capacity:</b> "
                    + '<span style="color: #0078d7; font-weight: bold;">'
                    + str(_total)
                    + " devices</span></p>"
                )

                if capacity_summary.get("additional_circuits", 0) > 0:
                    details_html += (
                        "<p><b>Additional Circuits:</b> +"
                        + str(capacity_summary.get("additional_circuits", 0))
                        + "</p>"
                    )

                if capacity_summary.get("power_consumption_ma", 0) > 0:
                    details_html += (
                        "<p><b>Expansion Power Draw:</b> "
                        + str(capacity_summary.get("power_consumption_ma", 0))
                        + "mA</p>"
                    )

                details_html += "<h4>Selected Expansion Boards</h4><ul>"
                for board in expansion_boards:
                    board_name = board.get("name", "Unknown Board")
                    board_mfr = board.get("manufacturer", "Unknown")
                    details_html += "<li>" + board_name + " (" + board_mfr + ")</li>"
                details_html += "</ul>"
            else:
                details_html += (
                    "<p><b>Total System Capacity:</b> "
                    + '<span style="color: #0078d7; font-weight: bold;">'
                    + str(capacity_summary.get("total_devices", 0))
                    + " devices</span></p>"
                )

            self.panel_details.setHtml(details_html)

    return enhanced_select_panel, enhanced_update_panel_display


def demo_enhanced_panel_selection():
    """
    Demo function to test the enhanced panel selection dialog.
    Run this to see the expansion board interface in action.
    """
    import sys

    from PySide6.QtWidgets import QApplication, QPushButton, QTextEdit, QVBoxLayout, QWidget

    app = QApplication.instance() or QApplication(sys.argv)

    # Create demo window
    window = QWidget()
    window.setWindowTitle("Enhanced Panel Selection Demo")
    window.resize(600, 400)

    layout = QVBoxLayout(window)

    # Add instruction text
    instructions = QTextEdit()
    instructions.setHtml(
        """
    <h2>Enhanced Fire Alarm Panel Selection Demo</h2>
    <p>This demo shows the new panel selection dialog with expansion board support.</p>
    <p><b>Features:</b></p>
    <ul>
        <li>Select main fire alarm control panel</li>
        <li>Add multiple expansion boards with checkboxes</li>
        <li>Real-time capacity calculations</li>
        <li>Power consumption tracking</li>
        <li>Circuit and device count summaries</li>
    </ul>
    <p>Click the button below to open the enhanced panel selection dialog.</p>
    """
    )
    instructions.setMaximumHeight(200)
    layout.addWidget(instructions)

    # Add test button
    test_button = QPushButton("Open Enhanced Panel Selection")

    # Add result display
    result_text = QTextEdit()
    result_text.setPlaceholderText("Panel configuration will appear here after selection...")

    def open_dialog():
        dialog = EnhancedPanelSelectionDialog(window)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            config = dialog.get_panel_config()

            # Display configuration
            panel = config.get("panel", {})
            expansion_boards = config.get("expansion_boards", [])
            capacity = config.get("capacity_summary", {})

            result_html = (
                "<h3>Selected Configuration</h3>"
                + "<p><b>Panel:</b> "
                + str(panel.get("manufacturer_name", "Unknown"))
                + " "
                + str(panel.get("model", "Unknown"))
                + "</p>"
                + "<p><b>Base Capacity:</b> "
                + str(capacity.get("base_devices", 0))
                + " devices</p>"
                + "<p><b>Expansion Boards:</b> "
                + str(len(expansion_boards))
                + "</p>"
                + (
                    "<p><b>Total Capacity:</b> "
                    + '<span style="color: green; font-weight: bold;">'
                    + str(capacity.get("total_devices", 0))
                    + " devices</span></p>"
                )
            )

            if expansion_boards:
                result_html += "<h4>Expansion Boards:</h4><ul>"
                for board in expansion_boards:
                    result_html += (
                        "<li>"
                        + str(board.get("name", "Unknown"))
                        + " ("
                        + str(board.get("manufacturer", "Unknown"))
                        + ")</li>"
                    )
                result_html += "</ul>"

                if capacity.get("power_consumption_ma", 0) > 0:
                    result_html += (
                        "<p><b>Additional Power Draw:</b> "
                        + str(capacity.get("power_consumption_ma", 0))
                        + "mA</p>"
                    )

            result_text.setHtml(result_html)
        else:
            result_text.setPlainText("Dialog was cancelled.")

    test_button.clicked.connect(open_dialog)
    layout.addWidget(test_button)
    layout.addWidget(result_text)

    window.show()
    return app.exec()


if __name__ == "__main__":
    # Initialize database first
    from db.connection import initialize_database

    initialize_database(in_memory=False)

    # Run demo
    demo_enhanced_panel_selection()
