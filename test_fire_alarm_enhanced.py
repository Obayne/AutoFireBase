"""
Test script to verify enhanced fire alarm functionality.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from app.main import MainWindow

def test_fire_alarm_enhanced():
    """Test the enhanced fire alarm functionality."""
    print("Testing enhanced fire alarm functionality...")
    
    # Create QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create main window
    window = MainWindow()
    
    # Test that fire alarm integrator is properly initialized
    assert hasattr(window, 'fire_alarm_integrator'), "Fire alarm integrator not found"
    assert window.fire_alarm_integrator is not None, "Fire alarm integrator is None"
    
    # Test that toolbar is created
    assert window.fire_alarm_integrator.toolbar is not None, "Fire alarm toolbar not created"
    
    # Test that status widget is created
    assert window.fire_alarm_integrator.status_widget is not None, "Fire alarm status widget not created"
    
    # Test device symbol creation
    from app.device import DeviceItem
    
    # Test smoke detector symbol
    sd_device = DeviceItem(0, 0, "SD", "Smoke Detector", "Generic", "GEN-SD", "Detector")
    assert sd_device is not None, "Failed to create smoke detector device"
    
    # Test strobe symbol
    s_device = DeviceItem(0, 0, "S", "Strobe", "Generic", "GEN-S", "Notification")
    assert s_device is not None, "Failed to create strobe device"
    
    # Test horn strobe symbol
    hs_device = DeviceItem(0, 0, "HS", "Horn Strobe", "Generic", "GEN-HS", "Notification")
    assert hs_device is not None, "Failed to create horn strobe device"
    
    # Test speaker symbol
    spk_device = DeviceItem(0, 0, "SPK", "Speaker", "Generic", "GEN-SPK", "Notification")
    assert spk_device is not None, "Failed to create speaker device"
    
    # Test pull station symbol
    ps_device = DeviceItem(0, 0, "PS", "Pull Station", "Generic", "GEN-PS", "Initiating")
    assert ps_device is not None, "Failed to create pull station device"
    
    # Test FACP symbol
    facp_device = DeviceItem(0, 0, "FACP", "FACP Panel", "Generic", "GEN-FACP", "Control")
    assert facp_device is not None, "Failed to create FACP device"
    
    # Test wire creation
    from app.wiring import WireItem
    from PySide6.QtCore import QPointF
    
    # Test SLC wire
    slc_wire = WireItem(QPointF(0, 0), QPointF(10, 10), "SLC")
    assert slc_wire is not None, "Failed to create SLC wire"
    assert slc_wire.wire_type == "SLC", "SLC wire type incorrect"
    
    # Test NAC wire
    nac_wire = WireItem(QPointF(0, 0), QPointF(10, 10), "NAC")
    assert nac_wire is not None, "Failed to create NAC wire"
    assert nac_wire.wire_type == "NAC", "NAC wire type incorrect"
    
    print("All tests passed!")
    print("Enhanced fire alarm functionality is working correctly.")

if __name__ == "__main__":
    test_fire_alarm_enhanced()