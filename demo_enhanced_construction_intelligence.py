"""
Enhanced Construction Intelligence Demo with Multi-Code Compliance
Demonstrates IBC, ADA, IMC compliance analysis plus specification gotchas and trade coordination
"""

import json
import sys
from pathlib import Path
from typing import List

from cad_core.intelligence import (
    ConstructionAnalysis,
    DeviceType,
    FireAlarmAnalysis,
    FireAlarmDevice,
    FloorPlanAnalysis,
    Priority,
    RFIItem,
    Room,
    ScheduleAnalysis,
    datetime,
)
from cad_core.intelligence.multi_code_engine import MultiCodeComplianceEngine
from cad_core.intelligence.rfi_engine import RFIIntelligenceEngine

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def create_comprehensive_construction_analysis() -> ConstructionAnalysis:
    """Create a comprehensive construction analysis that will trigger multiple code issues"""
    print("📋 Creating comprehensive construction analysis with multi-code scenarios...")

    # Create sample rooms with various occupancy types
    rooms = [
        Room(
            name="Main Lobby",
            number="100",
            area=800.0,
            occupancy_type="Assembly",  # Will trigger IBC assembly requirements
            ceiling_height=12.0,
            coordinates=[(0, 0), (40, 0), (40, 20), (0, 20)],
        ),
        Room(
            name="Office Suite A",
            number="101",
            area=1200.0,
            occupancy_type="Business",
            ceiling_height=9.0,
            coordinates=[(40, 0), (80, 0), (80, 20), (40, 20)],
        ),
        Room(
            name="Mechanical Room",
            number="M-1",
            area=300.0,
            occupancy_type="Utility",  # Will trigger IMC requirements
            ceiling_height=10.0,
            coordinates=[(80, 0), (100, 0), (100, 15), (80, 15)],
        ),
        Room(
            name="Data Center",
            number="DC-1",
            area=600.0,
            occupancy_type="Special",  # Will trigger special protection requirements
            ceiling_height=9.0,
            coordinates=[(0, 20), (30, 20), (30, 40), (0, 40)],
        ),
        Room(
            name="Main Corridor",
            number=None,
            area=400.0,
            occupancy_type="Means of Egress",  # Will trigger ADA/IBC requirements
            ceiling_height=9.0,
            coordinates=[(30, 20), (100, 20), (100, 30), (30, 30)],
        ),
        Room(
            name="Conference Center",
            number="200",
            area=1500.0,
            occupancy_type="Assembly",  # Large assembly space
            ceiling_height=14.0,
            coordinates=[(0, 40), (60, 40), (60, 65), (0, 65)],
        ),
    ]

    # Create fire alarm devices with intentional gaps and issues
    devices = [
        # Main Lobby - Missing visual notification (ADA issue)
        FireAlarmDevice(
            device_type=DeviceType.SMOKE_DETECTOR,
            location=(20, 10),
            model="SD-355",
            address="01",
            circuit="SLC-1",
            room="Main Lobby",
            notes=None,
        ),
        FireAlarmDevice(
            device_type=DeviceType.HORN_STROBE,  # Good - has visual
            location=(10, 15),
            model="HS-24-75",
            address="01",
            circuit="NAC-1",
            room="Main Lobby",
            notes="Wall mounted",
        ),
        # Office Suite - Basic coverage
        FireAlarmDevice(
            device_type=DeviceType.SMOKE_DETECTOR,
            location=(60, 10),
            model="SD-355",
            address="02",
            circuit="SLC-1",
            room="Office Suite A",
            notes=None,
        ),
        # Mechanical Room - No duct detectors specified (BIG coordination issue)
        FireAlarmDevice(
            device_type=DeviceType.HEAT_DETECTOR,
            location=(90, 7),
            model="HD-135",
            address="03",
            circuit="SLC-1",
            room="Mechanical Room",
            notes="High temperature space",
        ),
        # NOTE: Missing duct detectors - will trigger coordination RFI
        # Data Center - Missing special protection
        FireAlarmDevice(
            device_type=DeviceType.SMOKE_DETECTOR,
            location=(15, 30),
            model="SD-355",
            address="04",
            circuit="SLC-1",
            room="Data Center",
            notes=None,
        ),
        # NOTE: Missing aspirating detection for data center
        # Corridor - Missing notification (ADA/IBC issue)
        FireAlarmDevice(
            device_type=DeviceType.PULL_STATION,
            location=(65, 25),
            model="P2R",
            address="01",
            circuit="SLC-1",
            room="Main Corridor",
            notes="Near main exit",
        ),
        # NOTE: Missing strobes in corridor - ADA violation
        # Conference Center - Missing mass notification
        FireAlarmDevice(
            device_type=DeviceType.SMOKE_DETECTOR,
            location=(30, 52),
            model="SD-355",
            address="05",
            circuit="SLC-1",
            room="Conference Center",
            notes=None,
        ),
        # NOTE: Large assembly space needs mass notification system
    ]

    # Create floor plan analysis
    floor_plan = FloorPlanAnalysis(
        sheet_number="A-101",
        rooms=rooms,
        dimensions={"overall_length": 100.0, "overall_width": 65.0},
        scale='1/8" = 1\'-0"',  # Large building scale
        architectural_features={"exits": 4, "corridors": 1, "assembly_spaces": 2},
        coordinate_system={"origin": (0, 0), "units": "feet"},
    )

    # Create fire alarm plan analysis
    fa_plan = FireAlarmAnalysis(
        sheet_number="FA-101",
        devices=devices,
        circuits=[],
        annotations=[
            "See device schedule for complete specifications",
            "Coordinate duct detectors with mechanical contractor",
            "Mass notification system may be required for assembly spaces",
        ],
        panel_locations=[(5, 5)],
        coverage_analysis=None,
    )

    # Create enhanced device schedule
    device_schedule = [
        {
            "device_type": "Smoke Detector",
            "model": "SD-355",
            "quantity": "4",
            "description": "Photoelectric with sounder base",
        },
        {
            "device_type": "Heat Detector",
            "model": "HD-135",
            "quantity": "1",
            "description": "135°F fixed temperature",
        },
        {
            "device_type": "Pull Station",
            "model": "P2R",
            "quantity": "1",
            "description": "Single action, key reset",
        },
        {
            "device_type": "Horn/Strobe",
            "model": "HS-24-75",
            "quantity": "1",
            "description": "24VDC, 75/95 cd",
        },
        {
            "device_type": "Duct Detector",
            "model": "TBD",
            "quantity": "TBD",
            "description": "Coordinate with mechanical contractor",
        },
    ]

    schedule = ScheduleAnalysis(
        sheet_number="FA-201",
        device_schedule=device_schedule,
        panel_schedule=[],
        specifications={
            "manufacturer": "Simplex primary, Edwards approved equal",
            "nfpa_compliance": "NFPA 72 2019 Edition",
            "testing": "Acceptance testing per NFPA 72 Chapter 14",
        },
    )

    # Create specifications with gotchas
    specifications = [
        {
            "sheet_number": "SPEC-283100",
            "content": """
Fire Alarm System Specification

1.1 GENERAL
Fire alarm system shall comply with NFPA 72 latest version and all applicable codes.
System shall be Simplex 4120 or pre-approved equal.

1.2 PRODUCTS
A. Control Panel: Simplex 4120 with integrated mass notification capability
B. Devices: Edwards EST or approved equal
C. Duct Detectors: Coordinate installation with other trades

1.3 EXECUTION
Contractor shall coordinate with mechanical contractor for HVAC integration.
All work shall be performed by NICET certified technicians.
Provide 5 year warranty on all components.

1.4 TESTING
Complete acceptance testing per NFPA 72 current edition.
Witness testing by Authority Having Jurisdiction required.
            """,
            "nfpa_references": ["NFPA 72"],
            "manufacturer_specs": ["Simplex 4120", "Edwards EST"],
        }
    ]

    # Create complete analysis
    analysis = ConstructionAnalysis(
        project_name="Corporate Campus Building - Multi-Code Compliance Demo",
        analyzed_date=datetime.now(),
        pdf_path="multi_code_construction_set.pdf",
        total_pages=45,
        floor_plans=[floor_plan],
        fire_alarm_plans=[fa_plan],
        schedules=[schedule],
        specifications=specifications,
    )

    print(f"✓ Created analysis for {analysis.project_name}")
    print(f"  📏 Building area: {analysis.total_building_area:.0f} sq ft")
    print(f"  🔥 Fire alarm devices: {analysis.total_devices}")
    print(f"  🏠 Rooms: {len(rooms)} (including Assembly, Mechanical, Data Center)")
    print("  🏗️ Occupancy types: Assembly, Business, Utility, Special, Egress")

    return analysis


def demonstrate_multi_code_compliance(analysis: ConstructionAnalysis) -> dict:
    """Demonstrate comprehensive multi-code compliance analysis"""
    print("\n🏛️ Running Multi-Code Compliance Analysis...")
    print("  📋 Analyzing NFPA 72, IBC, ADA, IMC compliance")
    print("  🔍 Identifying specification gotchas")
    print("  ⚙️ Analyzing trade coordination issues")

    engine = MultiCodeComplianceEngine()
    compliance_results = engine.analyze_multi_code_compliance(analysis)

    print("\n✓ Multi-code compliance analysis complete")

    # Display results by code
    for code_name, results in compliance_results.items():
        if isinstance(results, dict) and "issues" in results:
            issue_count = len(results["issues"])
            if issue_count > 0:
                print(f"  📖 {code_name.upper()}: {issue_count} issues identified")

    # Display specification gotchas
    gotchas = compliance_results.get("gotchas", [])
    if gotchas:
        print(f"\n⚠️ Specification Gotchas Identified ({len(gotchas)}):")
        for gotcha in gotchas[:3]:  # Show first 3
            print(f"  🚨 {gotcha['type'].upper()}: {gotcha['description']}")

    # Display trade coordination issues
    coordination = compliance_results.get("coordination", {})
    critical_items = coordination.get("critical_items", [])
    if critical_items:
        print(f"\n🚨 Critical Trade Coordination Issues ({len(critical_items)}):")
        for item in critical_items:
            print(f"  ⚡ {item.category}: {item.description}")

    return compliance_results


def demonstrate_enhanced_rfi_generation(
    analysis: ConstructionAnalysis, compliance_results: dict
) -> List[RFIItem]:
    """Generate enhanced RFIs incorporating multi-code compliance"""
    print("\n📝 Generating Enhanced RFI Package...")

    # Get standard RFIs
    rfi_engine = RFIIntelligenceEngine()
    standard_rfis = rfi_engine.analyze_project_issues(analysis)

    # Add multi-code compliance RFIs
    all_rfis = standard_rfis.copy()

    for code_name, results in compliance_results.items():
        if isinstance(results, dict) and "issues" in results:
            all_rfis.extend(results["issues"])

    # Add coordination RFIs
    coordination = compliance_results.get("coordination", {})
    if "issues" in coordination:
        all_rfis.extend(coordination["issues"])

    print(f"✓ Enhanced RFI package generated: {len(all_rfis)} total issues")

    # Categorize by priority and code
    priority_counts = {}
    code_counts = {}

    for rfi in all_rfis:
        priority = rfi.priority.value
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

        # Determine code type from category
        if "NFPA" in rfi.category:
            code_type = "NFPA 72"
        elif "IBC" in rfi.category:
            code_type = "IBC"
        elif "ADA" in rfi.category:
            code_type = "ADA"
        elif "IMC" in rfi.category:
            code_type = "IMC"
        elif "Trade Coordination" in rfi.category:
            code_type = "Coordination"
        else:
            code_type = "General"

        code_counts[code_type] = code_counts.get(code_type, 0) + 1

    print("\n📊 RFI Analysis:")
    print("  Priority breakdown:")
    for priority, count in sorted(priority_counts.items()):
        print(f"    {priority.capitalize()}: {count}")

    print("  Code breakdown:")
    for code, count in sorted(code_counts.items()):
        print(f"    {code}: {count}")

    # Show sample critical issues
    critical_rfis = [rfi for rfi in all_rfis if rfi.priority == Priority.CRITICAL]
    if critical_rfis:
        print("\n🚨 Critical Issues Requiring Immediate Attention:")
        for rfi in critical_rfis[:2]:  # Show first 2 critical
            print(f"  ⚡ {rfi.category}")
            print(f"     {rfi.description}")
            print(f"     Resolution: {rfi.suggested_resolution}\n")

    return all_rfis


def main():
    """Main enhanced demonstration workflow"""
    print("🚀 AutoFire Enhanced Construction Intelligence System")
    print("🏛️ Multi-Code Compliance + Specification Gotchas + Trade Coordination")
    print("=" * 80)

    # Step 1: Create comprehensive construction analysis
    print("\n🏗️ STEP 1: Comprehensive Construction Document Analysis")
    analysis = create_comprehensive_construction_analysis()

    # Step 2: Multi-code compliance analysis
    print("\n🏛️ STEP 2: Multi-Code Compliance Analysis (NFPA 72, IBC, ADA, IMC)")
    compliance_results = demonstrate_multi_code_compliance(analysis)

    # Step 3: Enhanced RFI generation
    print("\n📝 STEP 3: Enhanced RFI Generation with Multi-Code Issues")
    all_rfis = demonstrate_enhanced_rfi_generation(analysis, compliance_results)

    # Step 4: Export comprehensive reports
    print("\n📄 STEP 4: Export Comprehensive Reports")

    # Export multi-code compliance report
    engine = MultiCodeComplianceEngine()
    engine.export_compliance_report(
        compliance_results, "demo_multi_code_compliance.txt", analysis.project_name
    )
    print("  ✓ Multi-code compliance report: demo_multi_code_compliance.txt")

    # Export enhanced RFI report
    rfi_engine = RFIIntelligenceEngine()
    rfi_engine.export_rfi_report(all_rfis, "demo_enhanced_rfis.txt", analysis.project_name)
    print("  ✓ Enhanced RFI report: demo_enhanced_rfis.txt")

    # Export specification gotchas
    gotchas = compliance_results.get("gotchas", [])
    with open("demo_specification_gotchas.json", "w") as f:
        json.dump(gotchas, f, indent=2)
    print("  ✓ Specification gotchas: demo_specification_gotchas.json")

    # Export trade coordination matrix
    coordination = compliance_results.get("coordination", {})
    with open("demo_trade_coordination.json", "w") as f:
        coordination_data = {
            "critical_items": [item.to_dict() for item in coordination.get("critical_items", [])],
            "all_issues": [item.to_dict() for item in coordination.get("issues", [])],
        }
        json.dump(coordination_data, f, indent=2, default=str)
    print("  ✓ Trade coordination matrix: demo_trade_coordination.json")

    # Final comprehensive summary
    print("\n" + "=" * 80)
    print("🎯 ENHANCED CONSTRUCTION INTELLIGENCE DEMO COMPLETE")
    print("=" * 80)
    print(f"📋 Project: {analysis.project_name}")
    print(f"🏗️ Scope: {analysis.total_building_area:.0f} sq ft, {analysis.total_devices} devices")
    print("🏛️ Codes analyzed: NFPA 72, IBC, ADA, IMC")
    print(f"⚠️ Total issues: {len(all_rfis)} RFIs generated")
    print(
        f"🚨 Critical items: {len([rfi for rfi in all_rfis if rfi.priority == Priority.CRITICAL])}"
    )
    print(f"🚨 Gotchas identified: {len(gotchas)}")

    # Show the biggest gotcha
    critical_gotchas = [g for g in gotchas if g["severity"] == "critical"]
    if critical_gotchas:
        print("\n🎯 BIGGEST GOTCHA IDENTIFIED:")
        biggest = critical_gotchas[0]
        print(f"   {biggest['description']}")
        print(f"   Recommendation: {biggest['recommendation']}")

    print("\n🎉 Enhanced Construction Intelligence System handles real-world complexity!")
    print("\n📁 Reports generated:")
    print("  - demo_multi_code_compliance.txt")
    print("  - demo_enhanced_rfis.txt")
    print("  - demo_specification_gotchas.json")
    print("  - demo_trade_coordination.json")

    print("\n🚀 Ready for production use with multi-code compliance intelligence!")


if __name__ == "__main__":
    main()
