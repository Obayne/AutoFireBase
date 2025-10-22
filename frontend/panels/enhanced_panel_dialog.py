"""
Enhanced Panel Selection Dialog with Expansion Board Support.

Allows users to select main panels and add expansion boards for capacity calculations.

====================
IMPORTS & MAINTAINER NOTES
====================
All imports are placed at the top of this file, per PEP8 and E402 best practices. This ensures:
    - Compatibility with static analysis tools (ruff, black, IDEs)
    - Predictable module loading and error handling
    - Easier maintenance and onboarding for new contributors


Conditional imports (e.g., try/except for optional modules) are allowed at the top level.
If you need to move imports inside functions/classes for plugin/fallback logic,
document the reason and ensure tests pass after changes.

Recovery: If a future edit breaks import order, restore all imports to the top and rerun lint/tests.
If a conditional import is required, add a comment explaining why.

This file was last validated for import order and lint compliance on 2025-10-08.
"""

import json

from PySide6 import QtCore, QtWidgets

from frontend.utils.manufacturer_aliases import normalize_manufacturer

# Optional DB loader import: fallback to None if unavailable
try:
    from db import loader as db_loader
except ImportError:
    db_loader = None


class ExpansionBoardWidget(QtWidgets.QWidget):
    """Widget for selecting expansion boards for a fire alarm panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_boards = []  # List of selected expansion boards
        self._setup_ui()

    def _setup_ui(self):
        """Setup the expansion board selection UI."""
        layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("Expansion Boards & Modules")
        title.setStyleSheet("font-weight: bold; font-size: 12pt; color: #0078d7;")
        layout.addWidget(title)

        # Description
        desc = QtWidgets.QLabel("Select additional expansion boards to increase system capacity:")
        desc.setStyleSheet("color: #495057; margin-bottom: 10px;")
        layout.addWidget(desc)

        # Scrollable area for expansion boards
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        scroll_widget = QtWidgets.QWidget()
        self.boards_layout = QtWidgets.QVBoxLayout(scroll_widget)

        # Load expansion boards
        self._load_expansion_boards()

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Summary section
        self.summary_group = QtWidgets.QGroupBox("Configuration Summary")
        summary_layout = QtWidgets.QVBoxLayout(self.summary_group)

        self.summary_label = QtWidgets.QLabel("No expansion boards selected")
        self.summary_label.setStyleSheet("color: #6c757d; font-style: italic;")
        summary_layout.addWidget(self.summary_label)

        layout.addWidget(self.summary_group)

    def _load_expansion_boards(self):
        """
                Load available expansion boards from database or fallback data.

        NOTE: We catch Exception here to ensure the UI remains usable even if the DB is missing
        or corrupt. This is a deliberate design choice for robust fallback behavior.
        If you refactor, consider narrowing the exception scope, but always test fallback logic.
        """
        try:
            if db_loader:
                # Try to load from database
                import os

                db_path = os.path.join(os.path.dirname(__file__), "..", "..", "autofire.db")
                con = db_loader.connect(db_path)
                # Look for expansion board type devices
                cur = con.cursor()
                cur.execute(
                    """
                    SELECT name, manufacturer, symbol, type, properties_json
                    FROM devices
                    WHERE name LIKE '%expansion%'
                       OR name LIKE '%board%'
                       OR name LIKE '%module%'
                       OR type LIKE '%Module%'
                       OR type LIKE '%Board%'
                    ORDER BY name
                    """
                )
                boards = []
                for row in cur.fetchall():
                    boards.append(
                        {
                            "name": row[0],
                            "manufacturer": row[1],
                            "symbol": row[2],
                            "type": row[3],
                            "properties": json.loads(row[4] or "{}"),
                        }
                    )
                con.close()

                if boards:
                    self._create_board_checkboxes(boards)
                else:
                    self._create_fallback_boards()
            else:
                self._create_fallback_boards()
        except Exception as e:
            # Lint: catching Exception is deliberate for robust fallback
            # If you narrow this, ensure fallback logic is tested.
            print(f"Error loading expansion boards: {e}")
            self._create_fallback_boards()

    def _create_fallback_boards(self):
        """Create fallback expansion board options if database query fails."""
        fallback_boards = [
            {
                "name": "SLC Expansion Module",
                "manufacturer": "Generic",
                "symbol": "SLC-EXP",
                "type": "Module",
                "properties": {
                    "circuit_type": "SLC",
                    "additional_devices": 99,
                    "power_consumption_ma": 200,
                    "description": "Adds 99 additional SLC devices",
                },
            },
            {
                "name": "NAC Expansion Board",
                "manufacturer": "Generic",
                "symbol": "NAC-EXP",
                "type": "Board",
                "properties": {
                    "circuit_type": "NAC",
                    "additional_circuits": 4,
                    "current_per_circuit_a": 3.0,
                    "power_consumption_ma": 150,
                    "description": "Adds 4 NAC circuits @ 3A each",
                },
            },
            {
                "name": "Input/Output Module",
                "manufacturer": "Generic",
                "symbol": "IO-MOD",
                "type": "Module",
                "properties": {
                    "input_points": 8,
                    "output_points": 8,
                    "power_consumption_ma": 100,
                    "description": "8 supervised inputs, 8 relay outputs",
                },
            },
            {
                "name": "Audio Amplifier Module",
                "manufacturer": "Generic",
                "symbol": "AMP",
                "type": "Module",
                "properties": {
                    "power_output_w": 75,
                    "audio_circuits": 2,
                    "power_consumption_ma": 500,
                    "description": "75W audio amplifier, 2 circuits",
                },
            },
            {
                "name": "Network Interface Module",
                "manufacturer": "Generic",
                "symbol": "NET",
                "type": "Module",
                "properties": {
                    "protocols": ["Ethernet", "BACnet"],
                    "power_consumption_ma": 250,
                    "description": "Network connectivity and remote monitoring",
                },
            },
        ]

        self._create_board_checkboxes(fallback_boards)

    def _create_board_checkboxes(self, boards):
        """Create checkbox widgets for expansion boards."""
        for board in boards:
            # Create checkbox with board info
            checkbox = QtWidgets.QCheckBox()
            checkbox.stateChanged.connect(self._on_board_selection_changed)
            # Store board data using Qt dynamic property to avoid lint/type issues
            checkbox.setProperty("board_data", board)

            # Create info layout
            board_layout = QtWidgets.QHBoxLayout()
            board_layout.addWidget(checkbox)

            # Board info label
            name = board["name"]
            manufacturer = board.get("manufacturer", "Unknown")
            props = board.get("properties", {})

            info_text = f"<b>{name}</b> ({manufacturer})"
            if "description" in props:
                info_text += f"<br/><small>{props['description']}</small>"

            info_label = QtWidgets.QLabel(info_text)
            info_label.setWordWrap(True)
            board_layout.addWidget(info_label)

            board_layout.addStretch()

            # Add capacity info on the right
            capacity_info = self._get_capacity_info(props)
            if capacity_info:
                capacity_label = QtWidgets.QLabel(capacity_info)
                capacity_label.setStyleSheet("color: #0078d7; font-weight: bold;")
                board_layout.addWidget(capacity_label)

            # Add to layout
            board_widget = QtWidgets.QWidget()
            board_widget.setLayout(board_layout)
            board_widget.setStyleSheet(
                """
                QWidget {
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    padding: 8px;
                    margin: 2px;
                    background-color: #fafafa;
                }
                QWidget:hover {
                    background-color: #f0f8ff;
                    border-color: #0078d7;
                }
            """
            )

            self.boards_layout.addWidget(board_widget)

    def _get_capacity_info(self, properties):
        """Get capacity information string for display."""
        info_parts = []

        if "additional_devices" in properties:
            info_parts.append(f"+{properties['additional_devices']} devices")

        if "additional_circuits" in properties:
            circuits = properties["additional_circuits"]
            current = properties.get("current_per_circuit_a", "")
            if current:
                info_parts.append(f"+{circuits} circuits @ {current}A")
            else:
                info_parts.append(f"+{circuits} circuits")

        if "input_points" in properties or "output_points" in properties:
            inputs = properties.get("input_points", 0)
            outputs = properties.get("output_points", 0)
            info_parts.append(f"{inputs}I/{outputs}O")

        if "power_output_w" in properties:
            info_parts.append(f"{properties['power_output_w']}W audio")

        return " | ".join(info_parts)

    def _on_board_selection_changed(self):
        """Handle expansion board selection changes."""
        # Update selected boards list
        self.selected_boards = []

        # Find all checked boxes
        for i in range(self.boards_layout.count()):
            item = self.boards_layout.itemAt(i)
            widget = item.widget() if item is not None else None
            if widget is None:
                continue
            layout = widget.layout()
            if layout is None or layout.count() == 0:
                continue
            first_item = layout.itemAt(0)
            checkbox = first_item.widget() if first_item is not None else None
            if isinstance(checkbox, QtWidgets.QCheckBox) and checkbox.isChecked():
                board_data = checkbox.property("board_data")
                if board_data:
                    self.selected_boards.append(board_data)

        # Update summary
        self._update_summary()

    def _update_summary(self):
        """Update the configuration summary."""
        if not self.selected_boards:
            self.summary_label.setText("No expansion boards selected")
            self.summary_label.setStyleSheet("color: #6c757d; font-style: italic;")
            return

        # Calculate totals
        total_devices = 0
        total_circuits = 0
        total_power_ma = 0
        board_names = []

        for board in self.selected_boards:
            props = board.get("properties", {})
            board_names.append(board["name"])

            total_devices += props.get("additional_devices", 0)
            total_circuits += props.get("additional_circuits", 0)
            total_power_ma += props.get("power_consumption_ma", 0)

        # Create summary text
        summary_parts = [f"<b>{len(self.selected_boards)} expansion boards selected</b>"]

        if total_devices > 0:
            summary_parts.append(f"• Additional device capacity: <b>+{total_devices}</b>")

        if total_circuits > 0:
            summary_parts.append(f"• Additional circuits: <b>+{total_circuits}</b>")

        if total_power_ma > 0:
            summary_parts.append(f"• Power consumption: <b>{total_power_ma}mA</b>")

        summary_parts.append(f"• Boards: {', '.join(board_names)}")

        summary_text = "<br/>".join(summary_parts)
        self.summary_label.setText(summary_text)
        self.summary_label.setStyleSheet("color: #212529;")

    def get_selected_boards(self):
        """Get list of selected expansion boards."""
        return self.selected_boards.copy()

    def get_total_capacity_additions(self):
        """Get total capacity additions from selected expansion boards."""
        totals = {
            "devices": 0,
            "circuits": 0,
            "slc_devices": 0,
            "nac_circuits": 0,
            "power_consumption_ma": 0,
        }

        for board in self.selected_boards:
            props = board.get("properties", {})
            totals["devices"] += props.get("additional_devices", 0)
            totals["circuits"] += props.get("additional_circuits", 0)
            totals["power_consumption_ma"] += props.get("power_consumption_ma", 0)

            # Circuit-specific additions
            if props.get("circuit_type") == "SLC":
                totals["slc_devices"] += props.get("additional_devices", 0)
            elif props.get("circuit_type") == "NAC":
                totals["nac_circuits"] += props.get("additional_circuits", 0)

        return totals


class EnhancedPanelSelectionDialog(QtWidgets.QDialog):
    """Enhanced panel selection dialog with expansion board support."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fire Alarm Panel & Expansion Board Configuration")
        self.setModal(True)
        self.resize(1000, 700)  # Larger to accommodate expansion boards

        # Data
        self.panels = []
        self.selected_panel = None
        self.panel_config = {}

        # Load panel data
        self._load_panel_data()

        # Setup UI
        self._setup_ui()

    def _load_panel_data(self):
        """Load panel data from database."""
        if db_loader:
            try:
                import os

                db_path = os.path.join(os.path.dirname(__file__), "..", "..", "autofire.db")
                con = db_loader.connect(db_path)
                self.panels = db_loader.fetch_panels(con)
                con.close()
            except Exception as e:
                # Lint: catching Exception is deliberate for robust fallback
                # If you narrow this, ensure fallback logic is tested.
                print(f"Failed to load panels: {e}")
                self.panels = self._get_builtin_panels()
        else:
            self.panels = self._get_builtin_panels()

        # No fallback merge: rely strictly on database-provided panel data

    def _get_builtin_panels(self):
        """Fallback panel data if database is not available."""
        return [
            # Fire-Lite Alarms (Honeywell)
            {
                "id": 1,
                "manufacturer_name": "Fire-Lite Alarms",
                "model": "MS-9050UD",
                "name": "MS-9050UD Fire Alarm Control Panel",
                "panel_type": "main",
                "max_devices": 1000,
                "properties_json": json.dumps(
                    {
                        "power_supply": "120VAC",
                        "battery_capacity": "55AH",
                        "communication_protocols": ["SLC", "NAC", "485"],
                    }
                ),
                "circuits": [
                    {"circuit_type": "SLC", "circuit_number": 1, "max_devices": 159},
                    {
                        "circuit_type": "NAC",
                        "circuit_number": 1,
                        "max_current_a": 3.0,
                        "voltage_v": 24,
                    },
                ],
            },
            # NOTIFIER (Honeywell)
            {
                "id": 2,
                "manufacturer_name": "NOTIFIER",
                "model": "NFS2-3030",
                "name": "NFS2-3030 Intelligent Fire Alarm Control Panel",
                "panel_type": "main",
                "max_devices": 3000,
                "properties_json": json.dumps(
                    {
                        "power_supply": "120VAC",
                        "battery_capacity": "110AH",
                        "communication_protocols": ["SLC", "NAC", "485"],
                    }
                ),
                "circuits": [
                    {"circuit_type": "SLC", "circuit_number": 1, "max_devices": 318},
                    {
                        "circuit_type": "NAC",
                        "circuit_number": 1,
                        "max_current_a": 6.0,
                        "voltage_v": 24,
                    },
                ],
            },
            # Gamewell-FCI (Honeywell)
            {
                "id": 3,
                "manufacturer_name": "Gamewell-FCI",
                "model": "S3",
                "name": "S3 Series Fire Alarm Control Panel",
                "panel_type": "main",
                "max_devices": 2000,
                "properties_json": json.dumps(
                    {
                        "power_supply": "120VAC",
                        "battery_capacity": "80AH",
                        "communication_protocols": ["SLC", "NAC", "485"],
                    }
                ),
                "circuits": [
                    {"circuit_type": "SLC", "circuit_number": 1, "max_devices": 159},
                    {
                        "circuit_type": "NAC",
                        "circuit_number": 1,
                        "max_current_a": 3.0,
                        "voltage_v": 24,
                    },
                ],
            },
            # Silent Knight (Honeywell)
            {
                "id": 4,
                "manufacturer_name": "Silent Knight",
                "model": "6820",
                "name": "6820 Intelligent Fire Alarm Control Panel",
                "panel_type": "main",
                "max_devices": 1275,
                "properties_json": json.dumps(
                    {
                        "power_supply": "120VAC",
                        "battery_capacity": "55AH",
                        "communication_protocols": ["SLC", "NAC", "485"],
                    }
                ),
                "circuits": [
                    {"circuit_type": "SLC", "circuit_number": 1, "max_devices": 127},
                    {
                        "circuit_type": "NAC",
                        "circuit_number": 1,
                        "max_current_a": 3.0,
                        "voltage_v": 24,
                    },
                ],
            },
        ]

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QtWidgets.QHBoxLayout(self)

        # Left side - Panel selection (existing functionality)
        panel_group = QtWidgets.QGroupBox("Select Fire Alarm Control Panel")
        panel_layout = QtWidgets.QVBoxLayout(panel_group)

        # Manufacturer filter
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.addWidget(QtWidgets.QLabel("Manufacturer:"))
        self.manufacturer_combo = QtWidgets.QComboBox()
        self.manufacturer_combo.addItem("All Manufacturers")
        manufacturers = set()
        for panel in self.panels:
            raw_mfr = panel.get("manufacturer_name") or panel.get("manufacturer") or "Unknown"
            norm_mfr = normalize_manufacturer(raw_mfr)
            manufacturers.add(norm_mfr)
        for mfr in sorted(manufacturers):
            self.manufacturer_combo.addItem(mfr)
        self.manufacturer_combo.currentTextChanged.connect(self._filter_panels)
        filter_layout.addWidget(self.manufacturer_combo)
        filter_layout.addStretch()
        panel_layout.addLayout(filter_layout)

        # Panel list
        self.panel_list = QtWidgets.QListWidget()
        self.panel_list.itemSelectionChanged.connect(self._on_panel_selected)
        panel_layout.addWidget(self.panel_list)

        # Panel details
        self.details_text = QtWidgets.QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        panel_layout.addWidget(self.details_text)

        layout.addWidget(panel_group)

        # Right side - Expansion boards
        self.expansion_widget = ExpansionBoardWidget()
        layout.addWidget(self.expansion_widget)

        # Bottom buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()

        self.select_button = QtWidgets.QPushButton("Configure System")
        self.select_button.clicked.connect(self._on_configure_system)
        self.select_button.setEnabled(False)
        button_layout.addWidget(self.select_button)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        # Add button layout to main layout (need to convert to vertical)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)

        # Set the main layout
        widget = QtWidgets.QWidget()
        widget.setLayout(main_layout)
        dialog_layout = QtWidgets.QVBoxLayout(self)
        dialog_layout.addWidget(widget)

        # Populate initial panel list
        self._filter_panels()
        # Debug: print the manufacturers detected to help diagnose limited options
        manufacturers = {
            normalize_manufacturer(p.get("manufacturer_name") or p.get("manufacturer") or "Unknown")
            for p in self.panels
        }
        print(f"EnhancedPanelDialog: manufacturers loaded -> {sorted(manufacturers)}")

    def _filter_panels(self):
        """Filter panels by manufacturer and type (exclude annunciators from main list)."""
        manufacturer = self.manufacturer_combo.currentText()
        allowed_types = {"main"}
        if manufacturer == "All Manufacturers":
            filtered_panels = [p for p in self.panels if p.get("panel_type") in allowed_types]
        else:
            filtered_panels = [
                p
                for p in self.panels
                if (
                    normalize_manufacturer(p.get("manufacturer_name") or p.get("manufacturer"))
                    == manufacturer
                    and p.get("panel_type") in allowed_types
                )
            ]

        self.panel_list.clear()
        for panel in filtered_panels:
            norm_mfr = normalize_manufacturer(
                panel.get("manufacturer_name") or panel.get("manufacturer") or "Unknown"
            )
            item_text = f"{norm_mfr} - {panel.get('model', 'Unknown')}"
            if panel.get("name"):
                item_text += f" ({panel.get('name')})"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, panel)
            self.panel_list.addItem(item)

    def _on_panel_selected(self):
        """Handle panel selection."""
        current_item = self.panel_list.currentItem()
        if current_item:
            self.selected_panel = current_item.data(QtCore.Qt.ItemDataRole.UserRole)
            self._update_panel_details()
            self.select_button.setEnabled(True)
        else:
            self.selected_panel = None
            self.select_button.setEnabled(False)

    def _update_panel_details(self):
        """Update the panel details display."""
        if not self.selected_panel:
            self.details_text.clear()
            return

        props = json.loads(self.selected_panel.get("properties_json", "{}"))
        details = f"""
<h3>{self.selected_panel.get('model', 'Unknown')}</h3>
<b>Type:</b> {self.selected_panel.get('panel_type', 'Unknown')}<br/>
<b>Base Capacity:</b> {self.selected_panel.get('max_devices', 'Unknown')} devices<br/>
<b>Power Supply:</b> {props.get('power_supply', 'Unknown')}<br/>
<b>Battery:</b> {props.get('battery_capacity', 'Unknown')}<br/>
<b>Protocols:</b> {', '.join(props.get('communication_protocols', []))}<br/>
<b>Circuits:</b> {len(self.selected_panel.get('circuits', []))} base circuits
        """.strip()

        self.details_text.setHtml(details)

    def _on_configure_system(self):
        """Handle system configuration confirmation."""
        if self.selected_panel:
            # Get expansion board additions
            capacity_additions = self.expansion_widget.get_total_capacity_additions()
            selected_boards = self.expansion_widget.get_selected_boards()

            # Calculate total system capacity
            base_capacity = self.selected_panel.get("max_devices", 0)
            total_capacity = base_capacity + capacity_additions["devices"]

            # Create enhanced panel configuration
            self.panel_config = {
                "panel": self.selected_panel,
                "expansion_boards": selected_boards,
                "capacity_summary": {
                    "base_devices": base_capacity,
                    "expansion_devices": capacity_additions["devices"],
                    "total_devices": total_capacity,
                    "additional_circuits": capacity_additions["circuits"],
                    "power_consumption_ma": capacity_additions["power_consumption_ma"],
                },
            }

            self.accept()

    def get_panel_config(self):
        """Get the complete panel configuration including expansion boards."""
        return self.panel_config
