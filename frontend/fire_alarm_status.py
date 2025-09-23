"""
System Status Widget for AutoFire Application.
Displays real-time status information for multiple system types including fire alarm, security, access control, and CCTV.
"""

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QTimer
from typing import Dict, List, Optional

class SystemStatusWidget(QtWidgets.QWidget):
    """Widget to display system status information for multiple system types."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Status")
        self.setMinimumWidth(400)
        self.setMaximumHeight(250)
        
        # System data for different system types
        self.project_info = {
            "project_id": "",
            "project_name": "",
            "client": "",
            "location": ""
        }
        
        self.system_status = {
            "fire_alarm": {"panels": 0, "circuits": 0, "devices": 0, "connections": 0},
            "security": {"panels": 0, "zones": 0, "devices": 0, "cameras": 0},
            "access_control": {"panels": 0, "doors": 0, "readers": 0, "cards": 0},
            "cctv": {"nvr": 0, "cameras": 0, "recorders": 0, "monitors": 0}
        }
        
        # Setup UI
        self._setup_ui()
        
        # Update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_status)
        self.update_timer.start(5000)  # Update every 5 seconds
        
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Project info group
        project_group = QtWidgets.QGroupBox("Project Information")
        project_layout = QtWidgets.QFormLayout(project_group)
        
        self.project_id_label = QtWidgets.QLabel("N/A")
        self.project_name_label = QtWidgets.QLabel("N/A")
        self.client_label = QtWidgets.QLabel("N/A")
        self.location_label = QtWidgets.QLabel("N/A")
        
        project_layout.addRow("Project ID:", self.project_id_label)
        project_layout.addRow("Project Name:", self.project_name_label)
        project_layout.addRow("Client:", self.client_label)
        project_layout.addRow("Location:", self.location_label)
        
        layout.addWidget(project_group)
        
        # Tab widget for different system types
        self.tab_widget = QtWidgets.QTabWidget()
        
        # Fire Alarm tab
        fire_alarm_widget = self._create_fire_alarm_tab()
        self.tab_widget.addTab(fire_alarm_widget, "Fire Alarm")
        
        # Security tab
        security_widget = self._create_security_tab()
        self.tab_widget.addTab(security_widget, "Security")
        
        # Access Control tab
        access_control_widget = self._create_access_control_tab()
        self.tab_widget.addTab(access_control_widget, "Access Control")
        
        # CCTV tab
        cctv_widget = self._create_cctv_tab()
        self.tab_widget.addTab(cctv_widget, "CCTV")
        
        layout.addWidget(self.tab_widget)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
    def _create_fire_alarm_tab(self):
        """Create the fire alarm system tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        
        self.fa_panels_label = QtWidgets.QLabel("0")
        self.fa_circuits_label = QtWidgets.QLabel("0")
        self.fa_devices_label = QtWidgets.QLabel("0")
        self.fa_connections_label = QtWidgets.QLabel("0")
        
        layout.addRow("Panels:", self.fa_panels_label)
        layout.addRow("Circuits:", self.fa_circuits_label)
        layout.addRow("Devices:", self.fa_devices_label)
        layout.addRow("Connections:", self.fa_connections_label)
        
        return widget
        
    def _create_security_tab(self):
        """Create the security system tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        
        self.sec_panels_label = QtWidgets.QLabel("0")
        self.sec_zones_label = QtWidgets.QLabel("0")
        self.sec_devices_label = QtWidgets.QLabel("0")
        self.sec_cameras_label = QtWidgets.QLabel("0")
        
        layout.addRow("Panels:", self.sec_panels_label)
        layout.addRow("Zones:", self.sec_zones_label)
        layout.addRow("Devices:", self.sec_devices_label)
        layout.addRow("Cameras:", self.sec_cameras_label)
        
        return widget
        
    def _create_access_control_tab(self):
        """Create the access control system tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        
        self.ac_panels_label = QtWidgets.QLabel("0")
        self.ac_doors_label = QtWidgets.QLabel("0")
        self.ac_readers_label = QtWidgets.QLabel("0")
        self.ac_cards_label = QtWidgets.QLabel("0")
        
        layout.addRow("Panels:", self.ac_panels_label)
        layout.addRow("Doors:", self.ac_doors_label)
        layout.addRow("Readers:", self.ac_readers_label)
        layout.addRow("Cards:", self.ac_cards_label)
        
        return widget
        
    def _create_cctv_tab(self):
        """Create the CCTV system tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        
        self.cctv_nvr_label = QtWidgets.QLabel("0")
        self.cctv_cameras_label = QtWidgets.QLabel("0")
        self.cctv_recorders_label = QtWidgets.QLabel("0")
        self.cctv_monitors_label = QtWidgets.QLabel("0")
        
        layout.addRow("NVR:", self.cctv_nvr_label)
        layout.addRow("Cameras:", self.cctv_cameras_label)
        layout.addRow("Recorders:", self.cctv_recorders_label)
        layout.addRow("Monitors:", self.cctv_monitors_label)
        
        return widget
        
    def set_project_info(self, project_id: str, project_name: str, client: str, location: str):
        """Set project information."""
        self.project_info.update({
            "project_id": project_id,
            "project_name": project_name,
            "client": client,
            "location": location
        })
        self._update_project_display()
        
    def set_system_status(self, system_type: str, **kwargs):
        """Set system status for a specific system type."""
        if system_type in self.system_status:
            self.system_status[system_type].update(kwargs)
            self._update_status_display()
        
    def _update_project_display(self):
        """Update project information display."""
        self.project_id_label.setText(self.project_info["project_id"] or "N/A")
        self.project_name_label.setText(self.project_info["project_name"] or "N/A")
        self.client_label.setText(self.project_info["client"] or "N/A")
        self.location_label.setText(self.project_info["location"] or "N/A")
        
    def _update_status_display(self):
        """Update system status display."""
        # Fire Alarm
        fa = self.system_status["fire_alarm"]
        self.fa_panels_label.setText(str(fa["panels"]))
        self.fa_circuits_label.setText(str(fa["circuits"]))
        self.fa_devices_label.setText(str(fa["devices"]))
        self.fa_connections_label.setText(str(fa["connections"]))
        
        # Security
        sec = self.system_status["security"]
        self.sec_panels_label.setText(str(sec["panels"]))
        self.sec_zones_label.setText(str(sec["zones"]))
        self.sec_devices_label.setText(str(sec["devices"]))
        self.sec_cameras_label.setText(str(sec["cameras"]))
        
        # Access Control
        ac = self.system_status["access_control"]
        self.ac_panels_label.setText(str(ac["panels"]))
        self.ac_doors_label.setText(str(ac["doors"]))
        self.ac_readers_label.setText(str(ac["readers"]))
        self.ac_cards_label.setText(str(ac["cards"]))
        
        # CCTV
        cctv = self.system_status["cctv"]
        self.cctv_nvr_label.setText(str(cctv["nvr"]))
        self.cctv_cameras_label.setText(str(cctv["cameras"]))
        self.cctv_recorders_label.setText(str(cctv["recorders"]))
        self.cctv_monitors_label.setText(str(cctv["monitors"]))
        
    def _update_status(self):
        """Periodic status update."""
        # This would typically query the backend for real-time status
        # For now, we'll just trigger a display refresh
        self._update_project_display()
        self._update_status_display()
        
    def reset(self):
        """Reset all status information."""
        self.project_info = {
            "project_id": "",
            "project_name": "",
            "client": "",
            "location": ""
        }
        self.system_status = {
            "fire_alarm": {"panels": 0, "circuits": 0, "devices": 0, "connections": 0},
            "security": {"panels": 0, "zones": 0, "devices": 0, "cameras": 0},
            "access_control": {"panels": 0, "doors": 0, "readers": 0, "cards": 0},
            "cctv": {"nvr": 0, "cameras": 0, "recorders": 0, "monitors": 0}
        }
        
        self._update_project_display()
        self._update_status_display()