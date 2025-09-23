from PySide6 import QtWidgets, QtCore

class CalculationsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculations")
        self.setModal(True)
        self.resize(600, 400)

        layout = QtWidgets.QVBoxLayout(self)

        self.results_text = QtWidgets.QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.perform_calculations()

    def perform_calculations(self):
import math
from PySide6 import QtWidgets, QtCore
from app import calculations
from db import loader as db_loader

class CalculationsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculations")
        self.setModal(True)
        self.resize(800, 600)

        self.parent = parent # MainWindow instance

        layout = QtWidgets.QVBoxLayout(self)

        self.results_text = QtWidgets.QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.perform_calculations()

    def perform_calculations(self):
        results = ""
        total_standby_current_ma = 0.0
        total_alarm_current_ma = 0.0

        # Fetch wire specs from DB
        wire_specs = {}
        try:
            con = db_loader.connect()
            cur = con.cursor()
            cur.execute("SELECT gauge, resistance_per_1000ft FROM wire_specs")
            for row in cur.fetchall():
                wire_specs[row['gauge']] = row['resistance_per_1000ft']
            con.close()
        except Exception as e:
            results += f"Error fetching wire specs: {e}\n\n"

        # Iterate through devices to sum up current draws and identify circuits
        circuits_data = {}
        for item in self.parent.layer_devices.childItems():
            if isinstance(item, self.parent.DeviceItem): # Use parent's DeviceItem class
                device = item # This is the DeviceItem instance
                
                # Sum up total standby and alarm currents for battery calculation
                total_standby_current_ma += getattr(device, 'standby_current_ma', 0.0)
                total_alarm_current_ma += getattr(device, 'alarm_current_ma', 0.0)

                # Get circuit information for voltage drop
                if device.circuit_id:
                    if device.circuit_id not in circuits_data:
                        circuits_data[device.circuit_id] = {
                            "devices": [],
                            "total_current_ma": 0.0, # Sum of max_current_ma for voltage drop
                            "circuit_type": "",
                            "panel_id": None,
                            "cable_length": 0.0 # Additional length
                        }
                    circuits_data[device.circuit_id]["devices"].append(device)
                    circuits_data[device.circuit_id]["total_current_ma"] += getattr(device, 'max_current_ma', 0.0)

        # Add FACP panel current to total battery calculation
        for item in self.parent.layer_devices.childItems():
            if isinstance(item, self.parent.DeviceItem) and item.symbol == "FACP":
                total_standby_current_ma += getattr(item, 'panel_standby_current_ma', 0.0)
                total_alarm_current_ma += getattr(item, 'panel_alarm_current_ma', 0.0)
                break # Assuming only one FACP for now

        # Perform Voltage Drop Calculations per circuit
        results += "Voltage Drop Calculation Results:\n"
        results += "----------------------------------\n"
        for circuit_id, data in circuits_data.items():
            results += f"Circuit ID: {circuit_id} (Type: {data['circuit_type']})\n"
            
            # For simplicity, assuming a single wire type for the circuit for now
            # In a real scenario, this would involve tracing the actual wire path
            # and summing up voltage drops across different wire segments.
            # Here, we'll use a placeholder wire gauge and length.
            
            # Placeholder: Get wire gauge from first device in circuit or from circuit properties
            wire_gauge = "18/2" # Default
            if data['devices']:
                # In a real system, wire gauge would be associated with the wire segments
                # For now, let's assume a default or get from a device property if available
                pass 

            # Placeholder: Get total length. This should come from actual wire segments on canvas + additional length
            total_circuit_length_ft = data['cable_length'] # Use additional length from circuit properties
            
            # Sum up actual wire lengths from canvas (placeholder for now)
            # This would involve iterating through wire items connected to devices in this circuit
            # For now, let's assume some default length per device or per connection
            
            # Example: Assume 50ft per device connection for calculation purposes
            total_circuit_length_ft += len(data['devices']) * 50.0 

            try:
                voltage_drop = calculations.calculate_voltage_drop(
                    data['total_current_ma'],
                    total_circuit_length_ft,
                    wire_gauge
                )
                results += f"  Total Current: {data['total_current_ma']:.2f} mA\n"
                results += f"  Total Length (est.): {total_circuit_length_ft:.2f} ft\n"
                results += f"  Calculated Voltage Drop: {voltage_drop:.2f} V\n"
                results += f"  Voltage Drop Limit ({calculations.VOLTAGE_DROP_LIMIT_PERCENT}%): {24 * (calculations.VOLTAGE_DROP_LIMIT_PERCENT/100.0):.2f} V\n"
                if voltage_drop > (24 * (calculations.VOLTAGE_DROP_LIMIT_PERCENT/100.0)):
                    results += "  STATUS: EXCEEDS LIMIT!\n"
                else:
                    results += "  STATUS: OK\n"
            except ValueError as ve:
                results += f"  Error: {ve}\n"
            results += "\n"

        # Perform Battery Size Calculation
        results += "Battery Size Calculation Results:\n"
        results += "----------------------------------\n"
        try:
            required_ah = calculations.calculate_battery_size(
                total_standby_current_ma,
                total_alarm_current_ma
            )
            results += f"Total Standby Current: {total_standby_current_ma:.2f} mA\n"
            results += f"Total Alarm Current: {total_alarm_current_ma:.2f} mA\n"
            results += f"Required Battery Size: {required_ah:.2f} Ah\n"
            results += f"  (Based on {calculations.BATTERY_STANDBY_HOURS} hrs standby and {calculations.BATTERY_ALARM_MINUTES} min alarm)\n"
        except Exception as e:
            results += f"Error calculating battery size: {e}\n"
        results += "\n"

        self.results_text.setText(results)
