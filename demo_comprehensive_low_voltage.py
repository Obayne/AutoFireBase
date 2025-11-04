"""
Comprehensive Low Voltage Systems Intelligence Demo
Demonstrates NEC compliance and multi-system analysis for fire alarm, security, communications, and more
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


def create_comprehensive_low_voltage_analysis() -> ConstructionAnalysis:
    """Create construction analysis for comprehensive low voltage systems"""
    print("🔌 Creating comprehensive low voltage systems analysis...")

    # Mixed-use building with various low voltage requirements
    rooms = [
        Room(
            name="Main Lobby",
            number="L-100",
            area=1200.0,
            occupancy_type="Assembly Public",
            ceiling_height=14.0,
            coordinates=[(0, 0), (60, 0), (60, 20), (0, 20)],
        ),
        Room(
            name="Security Control Room",
            number="S-200",
            area=300.0,
            occupancy_type="Secure Control",
            ceiling_height=9.0,
            coordinates=[(60, 0), (80, 0), (80, 15), (60, 15)],
        ),
        Room(
            name="Data Center",
            number="DC-300",
            area=800.0,
            occupancy_type="Data Communications",
            ceiling_height=10.0,
            coordinates=[(0, 20), (40, 20), (40, 40), (0, 40)],
        ),
        Room(
            name="Conference Room A",
            number="CR-400",
            area=500.0,
            occupancy_type="Business Meeting",
            ceiling_height=9.0,
            coordinates=[(40, 20), (60, 20), (60, 35), (40, 35)],
        ),
        Room(
            name="Office Suite",
            number="OS-500",
            area=2000.0,
            occupancy_type="Office Business",
            ceiling_height=9.0,
            coordinates=[(60, 15), (100, 15), (100, 40), (60, 40)],
        ),
        Room(
            name="Telecom Room",
            number="TR-600",
            area=150.0,
            occupancy_type="Telecom Equipment",
            ceiling_height=9.0,
            coordinates=[(80, 0), (100, 0), (100, 15), (80, 15)],
        ),
    ]

    floor_plan = FloorPlanAnalysis(
        sheet_number="LV101",
        rooms=rooms,
        scale='1/8" = 1\'-0"',
        dimensions={"length": 100.0, "width": 40.0},
        architectural_features={"building_type": "Mixed Use Commercial"},
        coordinate_system={"origin": (0, 0), "units": "feet"},
    )

    # Comprehensive low voltage devices across multiple systems
    devices = [
        # Fire Alarm System
        FireAlarmDevice(
            device_type=DeviceType.SMOKE_DETECTOR,
            location=(30.0, 10.0),
            model="System Sensor 2WT-B",
            address="001",
            circuit="SLC-1",
            room="Main Lobby",
            notes="Fire alarm smoke detection",
        ),
        FireAlarmDevice(
            device_type=DeviceType.HORN_STROBE,
            location=(50.0, 10.0),
            model="Wheelock E70-241575W-FW",
            address="002",
            circuit="NAC-1",
            room="Main Lobby",
            notes="Fire alarm notification",
        ),
        FireAlarmDevice(
            device_type=DeviceType.PULL_STATION,
            location=(55.0, 5.0),
            model="Edwards 270-SPO",
            address="003",
            circuit="SLC-1",
            room="Main Lobby",
            notes="Manual fire alarm activation",
        ),
        # Security System
        FireAlarmDevice(
            device_type=DeviceType.CARD_READER,
            location=(70.0, 7.5),
            model="HID ProxPoint Plus",
            address="SEC001",
            circuit="Class-2-Security",
            room="Security Control Room",
            notes="Access control - Class 2 circuit per NEC 725",
        ),
        FireAlarmDevice(
            device_type=DeviceType.CAMERA,
            location=(30.0, 15.0),
            model="Axis P3245-LVE",
            address="CAM001",
            circuit="PoE-Network",
            room="Main Lobby",
            notes="IP camera - network powered",
        ),
        FireAlarmDevice(
            device_type=DeviceType.MOTION_DETECTOR,
            location=(80.0, 30.0),
            model="Bosch ISC-BDL2-W12G",
            address="MD001",
            circuit="Class-2-Security",
            room="Office Suite",
            notes="PIR motion detector - Class 2 wiring",
        ),
        # Communications System
        FireAlarmDevice(
            device_type=DeviceType.DATA_OUTLET,
            location=(50.0, 27.5),
            model="Leviton 5G108-RI5",
            address="DO001",
            circuit="Cat6-Data",
            room="Conference Room A",
            notes="Cat6 data outlet - TIA-568 compliant",
        ),
        FireAlarmDevice(
            device_type=DeviceType.WIRELESS_AP,
            location=(20.0, 30.0),
            model="Cisco Aironet 4800",
            address="AP001",
            circuit="PoE-Network",
            room="Data Center",
            notes="802.11ax wireless access point",
        ),
        FireAlarmDevice(
            device_type=DeviceType.PATCH_PANEL,
            location=(90.0, 7.5),
            model="Panduit NK6PPG24",
            address="PP001",
            circuit="Cat6-Backbone",
            room="Telecom Room",
            notes="24-port Cat6 patch panel - backbone",
        ),
        # Audio/Visual Systems
        FireAlarmDevice(
            device_type=DeviceType.MICROPHONE,
            location=(50.0, 25.0),
            model="Shure MXA910",
            address="MIC001",
            circuit="AV-Control",
            room="Conference Room A",
            notes="Ceiling array microphone - AV system",
        ),
        FireAlarmDevice(
            device_type=DeviceType.AV_DISPLAY,
            location=(45.0, 20.0),
            model="Samsung QM75R",
            address="DISP001",
            circuit="AV-Power",
            room="Conference Room A",
            notes="75-inch 4K display - AV system",
        ),
    ]

    # Create circuits for different low voltage systems
    circuits = [
        # Fire Alarm Circuits
        Circuit(
            circuit_id="SLC-1",
            circuit_type="Signaling Line Circuit",
            wire_type="18 AWG FPLR",
            devices=[d for d in devices if d.circuit == "SLC-1"],
            route_points=[(10, 10), (30, 10), (55, 5)],
        ),
        Circuit(
            circuit_id="NAC-1",
            circuit_type="Notification Appliance Circuit",
            wire_type="12 AWG FPLR",
            devices=[d for d in devices if d.circuit == "NAC-1"],
            route_points=[(10, 10), (50, 10)],
        ),
        # Security Circuits (Class 2)
        Circuit(
            circuit_id="Class-2-Security",
            circuit_type="Class 2 Security Circuit",
            wire_type="22 AWG CL2",
            devices=[d for d in devices if d.circuit == "Class-2-Security"],
            route_points=[(70, 7.5), (80, 30)],
        ),
        # Communications Circuits
        Circuit(
            circuit_id="Cat6-Data",
            circuit_type="Category 6 Data Circuit",
            wire_type="Cat6 UTP",
            devices=[d for d in devices if d.circuit == "Cat6-Data"],
            route_points=[(90, 7.5), (50, 27.5)],
        ),
        Circuit(
            circuit_id="PoE-Network",
            circuit_type="Power over Ethernet",
            wire_type="Cat6 UTP",
            devices=[d for d in devices if d.circuit == "PoE-Network"],
            route_points=[(90, 7.5), (30, 15), (20, 30)],
        ),
        # AV Circuits
        Circuit(
            circuit_id="AV-Control",
            circuit_type="Audio Visual Control",
            wire_type="Cat6 Shielded",
            devices=[d for d in devices if d.circuit == "AV-Control"],
            route_points=[(50, 25)],
        ),
    ]

    fa_plan = FireAlarmAnalysis(
        sheet_number="LV101",
        devices=devices,
        circuits=circuits,
        annotations=[
            "Comprehensive low voltage systems",
            "Fire alarm, security, communications, AV",
            "NEC compliance verification required",
        ],
        panel_locations=[(10.0, 10.0), (70.0, 7.5), (90.0, 7.5)],  # FA, Security, Telecom panels
        coverage_analysis={
            "fire_alarm": "NFPA 72 compliant",
            "security": "Access control coverage",
            "communications": "TIA-568 structured cabling",
            "av": "Conference room AV system",
        },
    )

    return ConstructionAnalysis(
        project_name="Comprehensive Low Voltage Systems Demo",
        analyzed_date=datetime.now(),
        pdf_path="low_voltage_demo.pdf",
        total_pages=8,
        fire_alarm_plans=[fa_plan],
        floor_plans=[floor_plan],
        schedules=[],
        specifications=[],
    )


def demo_comprehensive_low_voltage_compliance():
    """Demonstrate comprehensive low voltage systems compliance analysis"""
    print("🔌 Comprehensive Low Voltage Systems Intelligence Demo")
    print("=" * 65)

    # Initialize the multi-code compliance engine
    compliance_engine = MultiCodeComplianceEngine()

    # Create comprehensive analysis
    analysis = create_comprehensive_low_voltage_analysis()

    print(f"\n🔍 Analyzing: {analysis.project_name}")
    print("-" * 50)

    # Run multi-code compliance analysis (now includes NEC)
    compliance_results = compliance_engine.analyze_multi_code_compliance(analysis)

    # Display all compliance results
    code_names = {
        "nfpa_72": "🔥 NFPA 72 (Fire Alarm)",
        "nec": "⚡ NEC (Electrical Code)",
        "ibc": "🏢 IBC (Building Code)",
        "ada": "♿ ADA (Accessibility)",
        "imc": "🌡️ IMC (Mechanical Code)",
        "osha": "🏭 OSHA (Workplace Safety)",
        "msha": "⛏️ MSHA (Mining Safety)",
        "coordination": "🤝 Trade Coordination",
        "specifications": "📋 Specifications",
        "gotchas": "⚠️ Specification Gotchas",
    }

    total_all_issues = 0
    critical_total = 0
    high_total = 0
    medium_total = 0

    for code_key, display_name in code_names.items():
        results = compliance_results.get(code_key, {})

        if isinstance(results, dict) and "issues" in results:
            issues = results.get("issues", [])
            status = results.get("compliance_status", "unknown")

            print(f"\n{display_name}:")
            print(f"   Status: {status}")
            print(f"   Issues: {len(issues)}")

            total_all_issues += len(issues)

            # Show top 3 issues for each code
            for issue in issues[:3]:
                priority_str = (
                    issue.priority if isinstance(issue.priority, str) else issue.priority.value
                )
                print(
                    f"   • {issue.category}: {issue.description[:80]}{'...' if len(issue.description) > 80 else ''}"
                )

                # Count priorities
                if priority_str.lower() == "critical":
                    critical_total += 1
                elif priority_str.lower() == "high":
                    high_total += 1
                elif priority_str.lower() == "medium":
                    medium_total += 1

    print("\n📊 Comprehensive Low Voltage Systems Summary:")
    print(f"   Total Issues Identified: {total_all_issues}")
    print(
        f"   Priority Breakdown: {critical_total} Critical, {high_total} High, {medium_total} Medium"
    )

    # Highlight NEC-specific findings
    nec_results = compliance_results.get("nec", {})
    nec_issues = nec_results.get("issues", [])

    print("\n⚡ NEC Compliance Highlights:")
    print(f"   Total NEC Issues: {len(nec_issues)}")
    print("   Key Areas:")

    nec_categories = {}
    for issue in nec_issues:
        category = issue.category.split()[1] if len(issue.category.split()) > 1 else issue.category
        nec_categories[category] = nec_categories.get(category, 0) + 1

    for category, count in list(nec_categories.items())[:5]:
        print(f"     • {category}: {count} issues")

    print("\n🎯 Low Voltage Systems Covered:")
    print("   • Fire Alarm & Life Safety (NFPA 72)")
    print("   • Security & Access Control (NEC 725)")
    print("   • Communications & Data (NEC 800, TIA-568)")
    print("   • Audio/Visual Systems")
    print("   • Power over Ethernet (PoE)")
    print("   • Emergency Systems (NEC 700)")

    print("\n✅ Comprehensive low voltage compliance analysis complete!")
    print("🔌 System now analyzes ALL low voltage systems, not just fire alarm!")


def create_government_facility_analysis() -> ConstructionAnalysis:
    """Create analysis for federal government facility requiring special standards"""
    print("🏛️ Creating federal government facility analysis...")

    # Government facility with enhanced security requirements
    rooms = [
        Room(
            name="Secure Entry Lobby",
            number="G-100",
            area=600.0,
            occupancy_type="Government Secure",
            ceiling_height=12.0,
            coordinates=[(0, 0), (30, 0), (30, 20), (0, 20)],
        ),
        Room(
            name="CJIS Data Center",
            number="G-200",
            area=400.0,
            occupancy_type="FBI CJIS Secure",
            ceiling_height=10.0,
            coordinates=[(30, 0), (50, 0), (50, 20), (30, 20)],
        ),
        Room(
            name="SCIF Conference",
            number="G-300",
            area=300.0,
            occupancy_type="Classified Conference",
            ceiling_height=9.0,
            coordinates=[(0, 20), (30, 20), (30, 30), (0, 30)],
        ),
    ]

    floor_plan = FloorPlanAnalysis(
        sheet_number="GOV101",
        rooms=rooms,
        scale='1/8" = 1\'-0"',
        dimensions={"length": 50.0, "width": 30.0},
        architectural_features={"building_type": "Federal Government", "clearance": "Secret"},
        coordinate_system={"origin": (0, 0), "units": "feet"},
    )

    # Government-grade security and communications devices
    devices = [
        FireAlarmDevice(
            device_type=DeviceType.SMOKE_DETECTOR,
            location=(15.0, 10.0),
            model="System Sensor 2WT-B",
            address="001",
            circuit="SLC-1",
            room="Secure Entry Lobby",
            notes="GSA approved fire detection",
        ),
        FireAlarmDevice(
            device_type=DeviceType.CARD_READER,
            location=(25.0, 5.0),
            model="HID iCLASS SE R40",
            address="SEC001",
            circuit="FIPS-Security",
            room="Secure Entry Lobby",
            notes="FIPS 201 PIV card reader - FBI CJIS compliant",
        ),
        FireAlarmDevice(
            device_type=DeviceType.CAMERA,
            location=(40.0, 10.0),
            model="Axis P3265-LVE",
            address="CAM001",
            circuit="Secure-Network",
            room="CJIS Data Center",
            notes="FIPS 140-2 encrypted camera - CJIS compliant",
        ),
    ]

    circuits = [
        Circuit(
            circuit_id="SLC-1",
            circuit_type="Signaling Line Circuit",
            wire_type="18 AWG FPLR",
            devices=[d for d in devices if d.circuit == "SLC-1"],
            route_points=[(10, 10), (15, 10)],
        ),
        Circuit(
            circuit_id="FIPS-Security",
            circuit_type="FIPS 199 Security Circuit",
            wire_type="22 AWG CL2P",
            devices=[d for d in devices if d.circuit == "FIPS-Security"],
            route_points=[(25, 5)],
        ),
        Circuit(
            circuit_id="Secure-Network",
            circuit_type="FIPS 140-2 Network",
            wire_type="Cat6A STP",
            devices=[d for d in devices if d.circuit == "Secure-Network"],
            route_points=[(40, 10)],
        ),
    ]

    fa_plan = FireAlarmAnalysis(
        sheet_number="GOV101",
        devices=devices,
        circuits=circuits,
        annotations=[
            "Federal government facility",
            "FBI CJIS compliance required",
            "FIPS 199/140-2 security standards",
        ],
        panel_locations=[(5.0, 5.0), (25.0, 2.5)],
        coverage_analysis={
            "security_level": "FIPS 199 Moderate",
            "cjis_compliance": "Required for data center",
            "clearance_level": "Secret",
        },
    )

    return ConstructionAnalysis(
        project_name="Federal Government Facility Demo",
        analyzed_date=datetime.now(),
        pdf_path="government_demo.pdf",
        total_pages=6,
        fire_alarm_plans=[fa_plan],
        floor_plans=[floor_plan],
        schedules=[],
        specifications=[],
    )


def demo_government_standards_compliance():
    """Demonstrate federal government standards compliance"""
    print("\n🏛️ Federal Government Standards Demo")
    print("=" * 45)

    compliance_engine = MultiCodeComplianceEngine()
    analysis = create_government_facility_analysis()

    print(f"\n🔍 Analyzing: {analysis.project_name}")
    print("-" * 40)

    compliance_results = compliance_engine.analyze_multi_code_compliance(analysis)

    # Focus on government-specific standards
    government_codes = ["nec", "coordination", "gotchas"]

    for code in government_codes:
        results = compliance_results.get(code, {})
        issues = results.get("issues", [])

        print(f"\n📋 {code.upper()} Analysis:")
        print(f"   Issues: {len(issues)}")

        # Look for government-specific issues
        gov_issues = [
            issue
            for issue in issues
            if any(
                gov_term in issue.description.lower()
                for gov_term in ["fips", "cjis", "government", "federal", "classified"]
            )
        ]

        for issue in gov_issues[:3]:
            print(f"   • {issue.category}: {issue.description}")

    print("\n🏛️ Government Compliance Areas:")
    print("   • FBI CJIS Security Policy compliance")
    print("   • FIPS 199 security categorization")
    print("   • FIPS 140-2 cryptographic standards")
    print("   • GSA PBS building standards")
    print("   • DOD UFC military standards")
    print("   • VA healthcare facility standards")


if __name__ == "__main__":
    demo_comprehensive_low_voltage_compliance()
    demo_government_standards_compliance()
