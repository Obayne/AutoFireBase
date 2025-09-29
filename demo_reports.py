#!/usr/bin/env python3
"""
Demonstration of AutoFire Reports Dialog with Battery Calculations
Shows how the reports system integrates with the battery calculator.
"""

import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from PySide6 import QtWidgets
from reports_dialog import ReportsDialog


def create_sample_system_data():
    """Create sample system data for demonstration."""
    return {
        "name": "Sample Fire Alarm System",
        "devices": {
            "smoke_detectors": [
                {
                    "name": "Smoke Detector",
                    "properties": {"standby_current_a": 0.00035, "alarm_current_a": 0.035},
                }
            ]
            * 50,  # 50 smoke detectors
            "heat_detectors": [
                {
                    "name": "Heat Detector",
                    "properties": {"standby_current_a": 0.00035, "alarm_current_a": 0.035},
                }
            ]
            * 20,  # 20 heat detectors
            "horn_strobes": [
                {
                    "name": "Horn Strobe",
                    "properties": {"standby_current_a": 0.0001, "alarm_current_a": 0.150},
                }
            ]
            * 30,  # 30 notification appliances
            "pull_stations": [
                {
                    "name": "Pull Station",
                    "properties": {"standby_current_a": 0.00005, "alarm_current_a": 0.00005},
                }
            ]
            * 5,  # 5 pull stations
        },
        "power_requirements": {
            "primary_voltage": 120,
            "secondary_voltage": 24.0,
            "battery_backup_hours": 24,
            "calculated_load": 2.8,
        },
        "coverage_areas": [
            {"name": "Main Building", "area_sqft": 10000},
            {"name": "Annex", "area_sqft": 5000},
        ],
    }


def demo_reports_dialog():
    """Demonstrate the reports dialog with battery calculations."""
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("AutoFire Reports Demo")

    # Create sample system data
    system_data = create_sample_system_data()

    # Create and show reports dialog
    dialog = ReportsDialog(system_data)
    dialog.show()

    # Set to battery calculations report
    dialog.report_type_combo.setCurrentText("Battery Calculations")

    print("AutoFire Reports Dialog Demo")
    print("=" * 30)
    print("Showing battery calculations report...")
    print("Close the dialog window to exit the demo.")

    sys.exit(app.exec())


if __name__ == "__main__":
    demo_reports_dialog()
