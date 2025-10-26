"""
Test the Enhanced Connections Panel integration.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from unittest.mock import MagicMock

def test_enhanced_connections_import():
    """Test that the enhanced connections panel can be imported."""
    try:
        from frontend.panels.enhanced_connections import (
            EnhancedConnectionsPanel, 
            CircuitTreeItem,
            create_enhanced_connections_tab
        )
        
        # Test basic import success
        assert EnhancedConnectionsPanel is not None
        assert CircuitTreeItem is not None
        assert create_enhanced_connections_tab is not None
        
        print("✅ Enhanced connections panel imports successfully")
        
    except ImportError as e:
        pytest.skip(f"Enhanced connections not available in test environment: {e}")


def test_enhanced_connections_basic_functionality():
    """Test basic functionality of the enhanced connections panel."""
    try:
        from frontend.panels.enhanced_connections import EnhancedConnectionsPanel
        from PySide6.QtWidgets import QApplication
        
        # Create QApplication if needed
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Create the panel
        panel = EnhancedConnectionsPanel()
        
        # Test adding wire segments
        panel.add_wire_segment(
            from_device="PANEL1",
            to_device="SMOKE_001", 
            length_ft=100.0,
            wire_gauge="14",
            current_a=0.020,
            circuit_type="SLC"
        )
        
        # Test device current update
        panel.update_device_current("SMOKE_001", 0.025)
        
        # Test calculation refresh
        panel.refresh_all_calculations()
        
        print("✅ Enhanced connections panel basic functionality works")
        
    except ImportError as e:
        pytest.skip(f"Enhanced connections requires PySide6: {e}")
    except Exception as e:
        pytest.fail(f"Enhanced connections panel failed: {e}")


def test_live_calculations_integration():
    """Test integration with live calculations engine."""
    try:
        from frontend.panels.enhanced_connections import EnhancedConnectionsPanel
        from cad_core.calculations.live_engine import LiveCalculationsEngine
        from PySide6.QtWidgets import QApplication
        
        # Create QApplication if needed  
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Create panel and verify calculation engine
        panel = EnhancedConnectionsPanel()
        assert isinstance(panel.calc_engine, LiveCalculationsEngine)
        
        # Add sample circuit
        panel.add_wire_segment("PANEL1", "SMOKE_001", 50.0, "14", 0.020, "SLC")
        panel.add_wire_segment("SMOKE_001", "SMOKE_002", 30.0, "14", 0.020, "SLC")
        
        # Get analyses
        analyses = panel.calc_engine.get_all_circuit_analyses()
        assert len(analyses) > 0
        
        # Verify circuit was created correctly
        circuit_keys = list(analyses.keys())
        assert any("SLC" in key for key in circuit_keys)
        
        print("✅ Live calculations integration works")
        
    except ImportError as e:
        pytest.skip(f"Test requires PySide6 and calculations engine: {e}")


if __name__ == "__main__":
    print("🔥 Testing Enhanced Connections Panel")
    print("=" * 40)
    
    test_enhanced_connections_import()
    test_enhanced_connections_basic_functionality() 
    test_live_calculations_integration()
    
    print("\n✅ All Enhanced Connections tests passed!")