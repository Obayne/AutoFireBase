"""
OSHA & MSHA Construction Intelligence Demo
Demonstrates workplace safety and mining safety compliance analysis
"""

import json
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
            name="Warehouse Storage",
            number="WH-200",
            area=8000.0,
            occupancy_type="Warehouse",  # OSHA workplace
            ceiling_height=25.0,
            coordinates=[(100, 0), (200, 0), (200, 50), (100, 50)],
        ),
        Room(
            name="Office Administrative",
            number="OF-300",
            area=1500.0,
            occupancy_type="Office",  # OSHA workplace
            ceiling_height=9.0,
            coordinates=[(0, 50), (50, 50), (50, 80), (0, 80)],
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
        Room(
            name="Laboratory Testing",
            number="LAB-600",
            area=800.0,
            occupancy_type="Laboratory",  # HAZWOPER + specialized requirements
            ceiling_height=10.0,
            coordinates=[(100, 50), (150, 50), (150, 80), (100, 80)],
        ),
    ]

    # Create floor plan
    floor_plan = FloorPlanAnalysis(
        sheet_number="A101",
        rooms=rooms,
        scale='1/8" = 1\'-0"',
        dimensions={"length": 200.0, "width": 80.0, "total_area": sum(room.area for room in rooms)},
        architectural_features={"level": "Ground Floor", "building_type": "Industrial"},
        coordinate_system={"origin": (0, 0), "units": "feet"},
    )

    # Create minimal fire alarm devices (intentionally sparse to trigger OSHA issues)
    devices = [
        FireAlarmDevice(
            device_type=DeviceType.SMOKE_DETECTOR,
            location=(50.0, 25.0),  # Manufacturing Floor center
            model="System Sensor 2W-B",
            address="001",
            circuit="SLC-1",
            room="Manufacturing Floor",
            notes="Smoke detection in manufacturing area",
        ),
        FireAlarmDevice(
            device_type=DeviceType.PULL_STATION,
            location=(90.0, 65.0),  # Exit corridor
            model="Edwards 270-SPO",
            address="002",
            circuit="SLC-1",
            room="Exit Corridor A",
            notes="Manual pull station at main exit",
        ),
        # Notably missing: Adequate audible/visual devices for workplace areas
    ]

    # Create circuits
    circuits = [
        Circuit(
            circuit_id="SLC-1",
            circuit_type="Signaling Line Circuit",
            wire_type="18 AWG FPLR",
            device_count=2,
            total_length=500.0,
        ),
    ]

    # Create fire alarm plan
    fa_plan = FireAlarmAnalysis(
        sheet_number="FP101",
        devices=devices,
        circuits=circuits,
        annotations=["Minimal coverage - intentional gaps for testing"],
        panel_locations=[(10.0, 10.0)],  # Panel location
        coverage_analysis={"status": "incomplete", "gaps": "Missing audible/visual devices"},
    )

    return ConstructionAnalysis(
        project_name="Industrial Workplace Safety Demo",
        analyzed_date=datetime.now(),
        pdf_path="workplace_safety_demo.pdf",
        total_pages=5,
        fire_alarm_plans=[fa_plan],
        floor_plans=[floor_plan],
        schedules=[],
        specifications=[{"section": "Fire Alarm", "description": "Basic fire alarm system"}],
    )


def create_mining_facility_analysis() -> ConstructionAnalysis:
    """Create construction analysis for mining safety scenarios"""
    print("⛏️ Creating mining facility analysis for MSHA compliance...")

    # Mining facility with underground and surface operations
    rooms = [
        Room(
            name="Mine Control Center",
            number="CC-100",
            area=800.0,
            occupancy_type="Control Office",  # MSHA emergency communication
            ceiling_height=9.0,
            coordinates=[(0, 0), (40, 0), (40, 20), (0, 20)],
        ),
        Room(
            name="Surface Processing",
            number="SP-200",
            area=3000.0,
            occupancy_type="Processing Equipment",  # MSHA equipment area
            ceiling_height=30.0,
            coordinates=[(40, 0), (100, 0), (100, 50), (40, 50)],
        ),
        Room(
            name="Underground Shaft Entry",
            number="US-300",
            area=400.0,
            occupancy_type="Underground Mine",  # MSHA underground requirements
            ceiling_height=8.0,
            coordinates=[(0, 20), (20, 20), (20, 40), (0, 40)],
        ),
        Room(
            name="Coal Conveyor System",
            number="CV-400",
            area=1200.0,
            occupancy_type="Coal Conveyor",  # MSHA + methane detection
            ceiling_height=15.0,
            coordinates=[(20, 20), (60, 20), (60, 40), (20, 40)],
        ),
        Room(
            name="Equipment Maintenance",
            number="EM-500",
            area=600.0,
            occupancy_type="Equipment Maintenance",  # MSHA equipment area
            ceiling_height=12.0,
            coordinates=[(60, 20), (80, 20), (80, 40), (60, 40)],
        ),
        Room(
            name="Mine Dispatch Office",
            number="MD-600",
            area=300.0,
            occupancy_type="Dispatch Control",  # MSHA emergency communication
            ceiling_height=9.0,
            coordinates=[(80, 20), (100, 20), (100, 40), (80, 40)],
        ),
    ]

    # Create floor plan
    floor_plan = FloorPlanAnalysis(
        level="Surface Level",
        sheet_number="M101",
        scale='1/16" = 1\'-0"',
        rooms=rooms,
        total_area=sum(room.area for room in rooms),
    )

    # Create basic fire alarm devices (mining requires specialized systems)
    devices = [
        FireAlarmDevice(
            device_id="MS-1",
            device_type=DeviceType.SMOKE_DETECTOR,
            location_description="Control Center",
            room="Mine Control Center",
            zone="Surface Zone",
            circuit="SLC 1",
            device_address="001",
        ),
        FireAlarmDevice(
            device_id="MS-2",
            device_type=DeviceType.MANUAL_PULL_STATION,
            location_description="Shaft Entry",
            room="Underground Shaft Entry",
            zone="Underground Zone",
            circuit="SLC 2",
            device_address="002",
            notes="Standard fire alarm - MSHA intrinsically safe required",
        ),
        # Mining facilities need specialized MSHA-approved equipment
    ]

    # Create fire alarm plan
    fa_plan = FireAlarmAnalysis(
        sheet_number="FP201",
        panel_type="Addressable - MSHA Approval Required",
        total_devices=len(devices),
        devices=devices,
        zones=["Surface Zone", "Underground Zone"],
        coverage_analysis="Standard fire alarm - MSHA compliance review required",
    )

    return ConstructionAnalysis(
        project_name="Coal Mining Facility Safety Demo",
        project_address="456 Mining Road, Coal Valley, WV",
        analysis_date=datetime.now(),
        fire_alarm_plans=[fa_plan],
        floor_plans=[floor_plan],
        schedules=[],
        total_area=sum(room.area for room in rooms),
        total_devices=len(devices),
        compliance_notes="MSHA mining safety compliance analysis with coal/methane indicators",
    )


def create_standard_office_analysis() -> ConstructionAnalysis:
    """Create standard office building for comparison (should have minimal OSHA/MSHA issues)"""
    print("🏢 Creating standard office building analysis for comparison...")

    rooms = [
        Room(
            name="Reception Area",
            number="R-100",
            area=400.0,
            occupancy_type="Office Reception",
            ceiling_height=9.0,
            coordinates=[(0, 0), (20, 0), (20, 20), (0, 20)],
        ),
        Room(
            name="Conference Room",
            number="C-200",
            area=300.0,
            occupancy_type="Business Meeting",
            ceiling_height=9.0,
            coordinates=[(20, 0), (35, 0), (35, 20), (20, 20)],
        ),
    ]

    floor_plan = FloorPlanAnalysis(
        level="First Floor",
        sheet_number="O101",
        scale='1/8" = 1\'-0"',
        rooms=rooms,
        total_area=sum(room.area for room in rooms),
    )

    devices = [
        FireAlarmDevice(
            device_id="SM-1",
            device_type=DeviceType.SMOKE_DETECTOR,
            location_description="Reception",
            room="Reception Area",
            zone="Zone 1",
            circuit="SLC 1",
            device_address="001",
        ),
        FireAlarmDevice(
            device_id="HS-1",
            device_type=DeviceType.HORN_STROBE,
            location_description="Main Area",
            room="Reception Area",
            zone="Zone 1",
            circuit="NAC 1",
            device_address="002",
        ),
    ]

    fa_plan = FireAlarmAnalysis(
        sheet_number="FP301",
        panel_type="Conventional",
        total_devices=len(devices),
        devices=devices,
        zones=["Zone 1"],
        coverage_analysis="Standard office fire alarm system",
    )

    return ConstructionAnalysis(
        project_name="Standard Office Building",
        project_address="789 Business Parkway, Office City, OC",
        analysis_date=datetime.now(),
        fire_alarm_plans=[fa_plan],
        floor_plans=[floor_plan],
        schedules=[],
        total_area=sum(room.area for room in rooms),
        total_devices=len(devices),
        compliance_notes="Standard office building - minimal OSHA/MSHA applicability",
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
        ("Standard Office (Comparison)", create_standard_office_analysis()),
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

        # Save detailed results for this scenario
        output_filename = f"osha_msha_analysis_{scenario_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}.json"

        try:
            with open(output_filename, "w") as f:
                # Convert to JSON-serializable format
                json_results = {
                    "scenario": scenario_name,
                    "project": analysis.project_name,
                    "osha": {
                        "status": osha_results.get("compliance_status"),
                        "issue_count": len(osha_results.get("issues", [])),
                        "issues": [
                            {
                                "category": issue.category,
                                "description": issue.description,
                                "priority": issue.priority,
                                "resolution": issue.suggested_resolution,
                            }
                            for issue in osha_results.get("issues", [])
                        ],
                    },
                    "msha": {
                        "status": msha_results.get("compliance_status"),
                        "issue_count": len(msha_results.get("issues", [])),
                        "issues": [
                            {
                                "category": issue.category,
                                "description": issue.description,
                                "priority": issue.priority,
                                "resolution": issue.suggested_resolution,
                            }
                            for issue in msha_results.get("issues", [])
                        ],
                    },
                }
                json.dump(json_results, f, indent=2)
            print(f"📄 Detailed results saved to: {output_filename}")
        except Exception as e:
            print(f"⚠️ Could not save results: {e}")

    print("\n✅ OSHA & MSHA compliance analysis complete!")
    print("🎯 Key findings:")
    print("   • Industrial facilities trigger multiple OSHA workplace safety requirements")
    print("   • Mining facilities require specialized MSHA compliance analysis")
    print("   • Standard offices have minimal OSHA/MSHA applicability")
    print("   • Hazardous areas (chemical, underground) require specialized alarm systems")
    print("   • Coal mining facilities need methane detection integration")


if __name__ == "__main__":
    demo_osha_msha_compliance()
