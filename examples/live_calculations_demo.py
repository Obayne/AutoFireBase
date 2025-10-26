"""
Example integration of Live Calculations Engine with AutoFire circuits.

This demonstrates how to integrate the live calculations engine with
the existing circuit management system for real-time calculations.
"""

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cad_core.calculations.live_engine import LiveCalculationsEngine, WireSegment


def demo_live_calculations():
    """Demonstrate live calculation features."""
    print("🔥 AutoFire Live Calculations Engine Demo")
    print("=" * 50)
    
    # Create the live calculations engine
    engine = LiveCalculationsEngine()
    
    # Create a sample fire alarm circuit
    print("\n📋 Creating sample SLC circuit...")
    segments = [
        # Panel to first device
        WireSegment(
            from_device="PANEL1",
            to_device="SMOKE_001", 
            length_ft=85.0,
            wire_gauge="14",
            current_a=0.020,
            circuit_type="SLC"
        ),
        # Device to device connections (Class A wiring)
        WireSegment(
            from_device="SMOKE_001",
            to_device="SMOKE_002",
            length_ft=45.0, 
            wire_gauge="14",
            current_a=0.020,
            circuit_type="SLC"
        ),
        WireSegment(
            from_device="SMOKE_002", 
            to_device="PULL_001",
            length_ft=60.0,
            wire_gauge="14", 
            current_a=0.001,  # Pull stations draw less current
            circuit_type="SLC"
        ),
        WireSegment(
            from_device="PULL_001",
            to_device="SMOKE_003",
            length_ft=75.0,
            wire_gauge="14",
            current_a=0.020,
            circuit_type="SLC"
        ),
        # Return to panel (Class A loop completion)
        WireSegment(
            from_device="SMOKE_003",
            to_device="PANEL1",
            length_ft=95.0,
            wire_gauge="14", 
            current_a=0.020,
            circuit_type="SLC"
        ),
    ]
    
    # Add all segments to the engine
    for segment in segments:
        engine.add_wire_segment(segment)
    
    # Set device current loads
    engine.update_device_load("SMOKE_001", 0.020)  # 20mA
    engine.update_device_load("SMOKE_002", 0.020)  # 20mA  
    engine.update_device_load("SMOKE_003", 0.020)  # 20mA
    engine.update_device_load("PULL_001", 0.001)   # 1mA
    
    print(f"   Added {len(segments)} wire segments")
    print(f"   Total wire length: {sum(s.length_ft for s in segments):.1f} feet")
    
    # Analyze the circuit
    print("\n⚡ Circuit Analysis Results:")
    analyses = engine.get_all_circuit_analyses()
    
    for circuit_id, analysis in analyses.items():
        print(f"\n🔌 {circuit_id}:")
        print(f"   Type: {analysis.circuit_type}")
        print(f"   Devices: {analysis.device_count}")
        print(f"   Total Length: {analysis.total_length_ft:.1f} ft")
        print(f"   Current Draw: {analysis.current_draw_a:.3f} A")
        print(f"   Voltage Drop: {analysis.total_voltage_drop:.3f} V")
        print(f"   VD Percentage: {analysis.voltage_drop_percent:.1f}%")
        print(f"   Compliance: {analysis.compliance_status}")
        
        if analysis.warnings:
            print("   ⚠️  Warnings:")
            for warning in analysis.warnings:
                print(f"      • {warning}")
    
    # Calculate battery requirements
    print("\n🔋 Battery Sizing Analysis:")
    battery_calc = engine.calculate_battery_requirements("PANEL1")
    
    print(f"   Standby Current: {battery_calc.standby_current_a:.3f} A")
    print(f"   Alarm Current: {battery_calc.alarm_current_a:.3f} A")
    print(f"   Required Standby AH: {battery_calc.required_standby_ah:.1f} AH")
    print(f"   Required Alarm AH: {battery_calc.required_alarm_ah:.1f} AH")
    print(f"   Recommended Battery: {battery_calc.recommended_ah} AH")
    print(f"   Battery SKU: {battery_calc.battery_sku}")
    print(f"   Derating Factor: {battery_calc.derating_factor:.1f}")
    
    # Demonstrate compliance checking
    print("\n📏 NFPA 72 Compliance Checking:")
    print(f"   Max Voltage Drop: {engine.max_voltage_drop_percent}%")
    print(f"   Max SLC Devices: {engine.max_slc_devices}")
    print(f"   Max SLC Length: {engine.max_slc_length_ft} ft")
    
    # Test adding a problematic segment
    print("\n⚠️  Testing Compliance Limits:")
    problem_segment = WireSegment(
        from_device="PANEL1",
        to_device="REMOTE_DEVICE",
        length_ft=8000.0,  # Very long run
        wire_gauge="18",   # Small wire
        current_a=0.100,   # High current
        circuit_type="SLC"
    )
    
    engine.add_wire_segment(problem_segment)
    
    # Check the new circuit analysis
    new_analyses = engine.get_all_circuit_analyses()
    for circuit_id, analysis in new_analyses.items():
        if analysis.warnings:
            print(f"\n🚨 Circuit {circuit_id} Compliance Issues:")
            for warning in analysis.warnings:
                print(f"   • {warning}")
    
    print("\n✅ Live Calculations Engine Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("• Real-time voltage drop calculations")
    print("• Battery sizing with proper derating")
    print("• NFPA 72 compliance checking") 
    print("• Circuit connectivity analysis")
    print("• Professional calculation accuracy")


def demo_qt_integration():
    """Demonstrate Qt integration for live calculations."""
    print("\n🖥️  Qt Integration Demo")
    print("=" * 30)
    
    try:
        # Import the Qt integration module
        from cad_core.calculations.live_integration import LiveCalculationsManager
        
        # This would normally be integrated into the main AutoFire UI
        _manager = LiveCalculationsManager()
        
        print("✅ LiveCalculationsManager created successfully")
        print("   • Real-time calculation updates")
        print("   • Qt signal/slot integration") 
        print("   • Professional UI widgets")
        print("   • Debounced recalculation")
        
    except (ImportError, ModuleNotFoundError, NameError) as e:
        print(f"⚠️  Qt integration requires full AutoFire environment: {e}")


if __name__ == "__main__":
    demo_live_calculations()
    demo_qt_integration()