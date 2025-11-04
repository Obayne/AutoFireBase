"""
OSHA & MSHA Construction Intelligence Demo - Simplified
Demonstrates workplace safety and mining safety compliance analysis
"""

import sys
from pathlib import Path

from cad_core.intelligence import (
    Circuit,
    ConstructionAnalysis,
    DeviceType,
    FireAlarmAnalysis,
    FireAlarmDevice,
    FloorPlanAnalysis,
    Room,
    datetime,
)
from cad_core.intelligence.multi_code_engine import MultiCodeComplianceEngine

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def create_workplace_safety_analysis() -> ConstructionAnalysis:
    """Create construction analysis for workplace safety scenarios"""
    print("🏭 Creating workplace safety analysis for OSHA compliance...")

    # Industrial facility with various workplace areas
    rooms = [
        Room(
            name="Manufacturing Floor",
            number="MF-100",
            area=5000.0,
            occupancy_type="Industrial Manufacturing",  # OSHA workplace
            ceiling_height=20.0,
            coordinates=[(0, 0), (100, 0), (100, 50), (0, 50)],
        ),
        Room(
            name="Chemical Storage",
            number="CS-400",
            area=600.0,
            occupancy_type="Chemical Hazmat",  # HAZWOPER requirements
            ceiling_height=12.0,
            coordinates=[(50, 50), (80, 50), (80, 70), (50, 70)],
        ),
        Room(
            name="Exit Corridor A",
            number="EC-500",
            area=400.0,
            occupancy_type="Corridor",  # OSHA egress requirements
            ceiling_height=9.0,
            coordinates=[(80, 50), (100, 50), (100, 80), (80, 80)],
        ),
    ]

    # Create simple floor plan
    floor_plan = FloorPlanAnalysis(
        sheet_number="A101",
        rooms=rooms,
        scale='1/8" = 1\'-0"',
        dimensions={"length": 100.0, "width": 80.0},
        architectural_features={"building_type": "Industrial"},
        coordinate_system={"origin": (0, 0), "units": "feet"},
    )

    # Create minimal devices (intentionally sparse to trigger OSHA issues)
    devices = [
        FireAlarmDevice(
            device_type=DeviceType.SMOKE_DETECTOR,
            location=(50.0, 25.0),
            model="Basic Smoke",
            address="001",
            circuit="SLC-1",
            room="Manufacturing Floor",
            notes="Minimal coverage - missing audible/visual devices",
        ),
    ]

    # Create simple circuit
    circuits = [
        Circuit(
            circuit_id="SLC-1",
            circuit_type="SLC",
            wire_type="FPLR",
            devices=devices,
            route_points=[(0, 0), (50, 25)],
        ),
    ]

    # Create fire alarm plan
    fa_plan = FireAlarmAnalysis(
        sheet_number="FP101",
        devices=devices,
        circuits=circuits,
        annotations=["Minimal coverage - intentional gaps for OSHA testing"],
        panel_locations=[(10.0, 10.0)],
        coverage_analysis={"status": "incomplete", "missing": "audible/visual devices"},
    )

    return ConstructionAnalysis(
        project_name="Industrial Workplace Safety Demo",
        analyzed_date=datetime.now(),
        pdf_path="workplace_demo.pdf",
        total_pages=3,
        fire_alarm_plans=[fa_plan],
        floor_plans=[floor_plan],
        schedules=[],
        specifications=[],
    )


def create_mining_facility_analysis() -> ConstructionAnalysis:
    """Create construction analysis for mining safety scenarios"""
    print("⛏️ Creating mining facility analysis for MSHA compliance...")

    # Mining facility rooms
    rooms = [
        Room(
            name="Mine Control Center",
            number="CC-100",
            area=800.0,
            occupancy_type="Control Office",
            ceiling_height=9.0,
            coordinates=[(0, 0), (40, 0), (40, 20), (0, 20)],
        ),
        Room(
            name="Underground Shaft Entry",
            number="US-300",
            area=400.0,
            occupancy_type="Underground Mine",  # MSHA underground
            ceiling_height=8.0,
            coordinates=[(0, 20), (20, 20), (20, 40), (0, 40)],
        ),
        Room(
            name="Coal Conveyor System",
            number="CV-400",
            area=1200.0,
            occupancy_type="Coal Conveyor",  # MSHA + methane
            ceiling_height=15.0,
            coordinates=[(20, 20), (60, 20), (60, 40), (20, 40)],
        ),
    ]

    floor_plan = FloorPlanAnalysis(
        sheet_number="M101",
        rooms=rooms,
        scale='1/16" = 1\'-0"',
        dimensions={"length": 60.0, "width": 40.0},
        architectural_features={"building_type": "Mining"},
        coordinate_system={"origin": (0, 0), "units": "feet"},
    )

    devices = [
        FireAlarmDevice(
            device_type=DeviceType.SMOKE_DETECTOR,
            location=(20.0, 10.0),
            model="Standard Smoke",
            address="001",
            circuit="SLC-1",
            room="Mine Control Center",
            notes="Standard fire alarm - MSHA approval needed",
        ),
    ]

    circuits = [
        Circuit(
            circuit_id="SLC-1",
            circuit_type="SLC",
            wire_type="FPLR",
            devices=devices,
            route_points=[(0, 0), (20, 10)],
        ),
    ]

    fa_plan = FireAlarmAnalysis(
        sheet_number="FP201",
        devices=devices,
        circuits=circuits,
        annotations=["MSHA compliance review required"],
        panel_locations=[(5.0, 5.0)],
        coverage_analysis={"status": "needs_msha_approval"},
    )

    return ConstructionAnalysis(
        project_name="Coal Mining Facility Safety Demo",
        analyzed_date=datetime.now(),
        pdf_path="mining_demo.pdf",
        total_pages=4,
        fire_alarm_plans=[fa_plan],
        floor_plans=[floor_plan],
        schedules=[],
        specifications=[],
    )


def demo_osha_msha_compliance():
    """Demonstrate OSHA and MSHA compliance analysis"""
    print("🚨 OSHA & MSHA Construction Intelligence Demo")
    print("=" * 60)

    # Initialize the multi-code compliance engine
    compliance_engine = MultiCodeComplianceEngine()

    # Test scenarios
    scenarios = [
        ("Industrial Workplace (OSHA Focus)", create_workplace_safety_analysis()),
        ("Mining Facility (MSHA Focus)", create_mining_facility_analysis()),
    ]

    for scenario_name, analysis in scenarios:
        print(f"\n🔍 Analyzing: {scenario_name}")
        print("-" * 40)

        # Run multi-code compliance analysis (includes OSHA and MSHA)
        compliance_results = compliance_engine.analyze_multi_code_compliance(analysis)

        # Extract OSHA and MSHA specific results
        osha_results = compliance_results.get("osha", {})
        msha_results = compliance_results.get("msha", {})

        print("🏭 OSHA Analysis:")
        print(f"   Status: {osha_results.get('compliance_status', 'unknown')}")
        print(f"   Issues: {len(osha_results.get('issues', []))}")

        for issue in osha_results.get("issues", [])[:3]:  # Show first 3 issues
            print(f"   • {issue.category}: {issue.description}")

        print("\n⛏️ MSHA Analysis:")
        print(f"   Status: {msha_results.get('compliance_status', 'unknown')}")
        print(f"   Issues: {len(msha_results.get('issues', []))}")

        for issue in msha_results.get("issues", [])[:3]:  # Show first 3 issues
            print(f"   • {issue.category}: {issue.description}")

        # Summary statistics
        osha_issues = len(osha_results.get("issues", []))
        msha_issues = len(msha_results.get("issues", []))
        total_safety_issues = osha_issues + msha_issues

        print("\n📊 Safety Compliance Summary:")
        print(f"   OSHA Issues: {osha_issues}")
        print(f"   MSHA Issues: {msha_issues}")
        print(f"   Total Safety Issues: {total_safety_issues}")

        # Priority breakdown
        all_safety_issues = osha_results.get("issues", []) + msha_results.get("issues", [])
        critical_count = len([i for i in all_safety_issues if i.priority == "critical"])
        high_count = len([i for i in all_safety_issues if i.priority == "high"])
        medium_count = len([i for i in all_safety_issues if i.priority == "medium"])

        if total_safety_issues > 0:
            print(
                f"   Priority: {critical_count} Critical, {high_count} High, {medium_count} Medium"
            )

        print(f"\n🎯 Key Issues for {scenario_name}:")
        for issue in all_safety_issues[:5]:  # Show top 5 issues
            priority_str = (
                issue.priority if isinstance(issue.priority, str) else issue.priority.value
            )
            print(f"   {priority_str.upper()}: {issue.category}")
            print(f"      {issue.description}")

    print("\n✅ OSHA & MSHA compliance analysis complete!")
    print("🎯 Key findings:")
    print("   • Industrial facilities trigger OSHA workplace safety requirements")
    print("   • Mining facilities require specialized MSHA compliance analysis")
    print("   • Hazardous areas need specialized alarm systems")
    print("   • Coal mining facilities need methane detection integration")
    print("   • Underground areas require intrinsically safe equipment")


if __name__ == "__main__":
    demo_osha_msha_compliance()
