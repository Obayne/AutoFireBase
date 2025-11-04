"""
AutoFire Construction Intelligence System - Comprehensive Demo
Demonstrates complete workflow: PDF analysis → RFI generation → Cost estimation → Project intelligence
"""

import json
import sys
from pathlib import Path
from typing import List

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from cad_core.intelligence import (
    DEVICE_COST_ESTIMATES,
    INSTALLATION_LABOR_HOURS,
    ConstructionAnalysis,
    CostEstimate,
    CostLineItem,
    DeviceType,
    FireAlarmAnalysis,
    FireAlarmDevice,
    FloorPlanAnalysis,
    Priority,
    ProjectIntelligence,
    RFIItem,
    Room,
    ScheduleAnalysis,
    datetime,
)
from cad_core.intelligence.rfi_engine import RFIIntelligenceEngine


def create_sample_construction_analysis() -> ConstructionAnalysis:
    """Create a realistic sample construction analysis for demonstration"""
    print("📋 Creating sample construction analysis...")

    # Create sample rooms
    rooms = [
        Room(
            name="Office 101",
            number="101",
            area=250.0,
            occupancy_type="Business",
            ceiling_height=9.0,
            coordinates=[(0, 0), (20, 0), (20, 12.5), (0, 12.5)],
        ),
        Room(
            name="Conference Room",
            number="102",
            area=400.0,
            occupancy_type="Assembly",
            ceiling_height=10.0,
            coordinates=[
                (20, 0),
                (40, 0),
                (
                    40,
                    20,
                ),
                (20, 20),
            ],
        ),
        Room(
            name="Corridor",
            number=None,
            area=300.0,
            occupancy_type="Means of Egress",
            ceiling_height=9.0,
            coordinates=[(0, 12.5), (40, 12.5), (40, 20), (0, 20)],
        ),
        Room(
            name="Storage Room",
            number="103",
            area=150.0,
            occupancy_type="Storage",
            ceiling_height=9.0,
            coordinates=[(40, 0), (50, 0), (50, 12.5), (40, 12.5)],
        ),
        Room(
            name="Data Center",
            number="104",
            area=600.0,
            occupancy_type="Special",
            ceiling_height=9.0,
            coordinates=[(50, 0), (80, 0), (80, 20), (50, 20)],
        ),
    ]

    # Create sample fire alarm devices
    devices = [
        FireAlarmDevice(
            device_type=DeviceType.SMOKE_DETECTOR,
            location=(10, 6),
            model="SD-355",
            address="01",
            circuit="SLC-1",
            room="Office 101",
            notes=None,
        ),
        FireAlarmDevice(
            device_type=DeviceType.SMOKE_DETECTOR,
            location=(30, 10),
            model="SD-355",
            address="02",
            circuit="SLC-1",
            room="Conference Room",
            notes=None,
        ),
        # Missing smoke detector in corridor - will trigger RFI
        FireAlarmDevice(
            device_type=DeviceType.PULL_STATION,
            location=(5, 20),
            model="P2R",
            address="01",
            circuit="SLC-1",
            room="Corridor",
            notes="Near main exit",
        ),
        # Missing devices in Storage Room and Data Center - will trigger RFIs
        FireAlarmDevice(
            device_type=DeviceType.HORN_STROBE,
            location=(20, 16),
            model="HS-24",
            address="01",
            circuit="NAC-1",
            room="Corridor",
            notes="ADA compliant",
        ),
    ]

    # Create floor plan analysis
    floor_plan = FloorPlanAnalysis(
        sheet_number="A-101",
        rooms=rooms,
        dimensions={"overall_length": 80.0, "overall_width": 20.0},
        scale='1/4" = 1\'-0"',
        architectural_features={"exits": 2, "corridors": 1},
        coordinate_system={"origin": (0, 0), "units": "feet"},
    )

    # Create fire alarm plan analysis
    fa_plan = FireAlarmAnalysis(
        sheet_number="FA-101",
        devices=devices,
        circuits=[],
        annotations=["See device schedule for complete specifications"],
        panel_locations=[(5, 5)],
        coverage_analysis=None,
    )

    # Create device schedule
    device_schedule = [
        {
            "device_type": "Smoke Detector",
            "model": "SD-355",
            "quantity": "2",
            "description": "Photoelectric with sounder base",
        },
        {
            "device_type": "Pull Station",
            "model": "P2R",
            "quantity": "1",
            "description": "Single action, key reset",
        },
        {
            "device_type": "Horn/Strobe",
            "model": "HS-24",
            "quantity": "1",
            "description": "24VDC, 75/95 cd",
        },
    ]

    schedule = ScheduleAnalysis(
        sheet_number="FA-201",
        device_schedule=device_schedule,
        panel_schedule=[],
        specifications={"manufacturer": "Simplex", "nfpa_compliance": "NFPA 72 2019 Edition"},
    )

    # Create complete analysis
    analysis = ConstructionAnalysis(
        project_name="Corporate Office Building - Fire Alarm System",
        analyzed_date=datetime.now(),
        pdf_path="sample_construction_set.pdf",
        total_pages=25,
        floor_plans=[floor_plan],
        fire_alarm_plans=[fa_plan],
        schedules=[schedule],
        specifications=[
            {
                "sheet_number": "SPEC-01",
                "content": "Fire alarm system shall comply with NFPA 72 2019 Edition",
                "nfpa_references": ["NFPA 72"],
                "manufacturer_specs": ["Simplex 4120", "Edwards EST3X"],
            }
        ],
    )

    print(f"✓ Created analysis for {analysis.project_name}")
    print(f"  📏 Building area: {analysis.total_building_area:.0f} sq ft")
    print(f"  🔥 Fire alarm devices: {analysis.total_devices}")
    print(f"  🏠 Rooms: {len(rooms)}")

    return analysis


def demonstrate_rfi_intelligence(analysis: ConstructionAnalysis) -> List[RFIItem]:
    """Demonstrate RFI intelligence engine"""
    print("\n🤖 Running RFI Intelligence Analysis...")

    rfi_engine = RFIIntelligenceEngine()
    rfis = rfi_engine.analyze_project_issues(analysis)

    print(f"✓ RFI analysis complete: {len(rfis)} issues identified")

    # Categorize and display RFIs
    priority_counts = {}
    category_counts = {}

    for rfi in rfis:
        priority = rfi.priority.value
        category = rfi.category

        priority_counts[priority] = priority_counts.get(priority, 0) + 1
        category_counts[category] = category_counts.get(category, 0) + 1

    print("\n📊 RFI Summary:")
    print("  Priority breakdown:")
    for priority, count in sorted(priority_counts.items()):
        print(f"    {priority.capitalize()}: {count}")

    print("  Category breakdown:")
    for category, count in sorted(category_counts.items()):
        print(f"    {category}: {count}")

    print("\n📋 Sample RFI Items:")
    for i, rfi in enumerate(rfis[:3], 1):  # Show first 3 RFIs
        print(f"  {i}. {rfi.category} ({rfi.priority.value.upper()})")
        print(f"     {rfi.description}")
        print(f"     Suggested: {rfi.suggested_resolution}")
        print()

    return rfis


def demonstrate_cost_estimation(analysis: ConstructionAnalysis) -> CostEstimate:
    """Demonstrate automated cost estimation"""
    print("💰 Generating Cost Estimate...")

    # Create material takeoff from analysis
    line_items = []

    # Process devices from fire alarm plans
    device_counts = {}
    for fa_plan in analysis.fire_alarm_plans:
        for device in fa_plan.devices:
            device_type = device.device_type
            model = device.model or f"Generic {device_type.value}"

            key = (device_type, model)
            device_counts[key] = device_counts.get(key, 0) + 1

    # Create cost line items
    for (device_type, model), quantity in device_counts.items():
        material_cost = DEVICE_COST_ESTIMATES.get(device_type, 100.0)
        labor_hours = INSTALLATION_LABOR_HOURS.get(device_type, 1.0)

        line_item = CostLineItem(
            description=f"{model} {device_type.value.replace('_', ' ').title()}",
            quantity=float(quantity),
            unit="EA",
            material_cost=material_cost,
            labor_hours=labor_hours,
            labor_rate=75.0,  # $75/hour electrician rate
        )
        line_items.append(line_item)

    # Add control panel
    panel_item = CostLineItem(
        description="Fire Alarm Control Panel",
        quantity=1.0,
        unit="EA",
        material_cost=DEVICE_COST_ESTIMATES[DeviceType.PANEL],
        labor_hours=INSTALLATION_LABOR_HOURS[DeviceType.PANEL],
        labor_rate=85.0,  # Higher rate for panel installation
    )
    line_items.append(panel_item)

    # Estimate wire footage (simplified)
    total_devices = sum(device_counts.values())
    estimated_wire_footage = total_devices * 50  # 50 feet average per device

    wire_item = CostLineItem(
        description="Fire Alarm Cable (12 AWG, 2-conductor)",
        quantity=float(estimated_wire_footage),
        unit="LF",
        material_cost=1.25,  # $1.25 per linear foot
        labor_hours=estimated_wire_footage * 0.05,  # 0.05 hours per foot
        labor_rate=75.0,
    )
    line_items.append(wire_item)

    # Create cost estimate
    estimate = CostEstimate(
        project_name=analysis.project_name,
        line_items=line_items,
        material_markup=0.15,  # 15% markup
        overhead=0.10,  # 10% overhead
        profit=0.08,  # 8% profit
    )

    print("✓ Cost estimate generated")
    print(f"  📦 Material subtotal: ${estimate.subtotal_material:,.2f}")
    print(f"  👷 Labor subtotal: ${estimate.subtotal_labor:,.2f}")
    print(f"  📈 Material markup: ${estimate.material_markup_amount:,.2f}")
    print(f"  🏢 Overhead: ${estimate.overhead_amount:,.2f}")
    print(f"  💼 Profit: ${estimate.profit_amount:,.2f}")
    print(f"  💰 TOTAL COST: ${estimate.total_cost:,.2f}")

    return estimate


def demonstrate_project_intelligence(
    analysis: ConstructionAnalysis, rfis: List[RFIItem], estimate: CostEstimate
) -> ProjectIntelligence:
    """Demonstrate project intelligence dashboard"""
    print("\n📈 Generating Project Intelligence Report...")

    # Executive summary
    executive_summary = {
        "project_scope": f"{analysis.total_building_area:.0f} sq ft office building with {analysis.total_devices} fire alarm devices",
        "estimated_cost": estimate.total_cost,
        "project_complexity": "Medium",  # Based on device count and RFI issues
        "estimated_duration": "3-4 weeks",  # Based on scope
        "key_challenges": [
            f"{len(rfis)} design issues requiring resolution",
            "NFPA 72 compliance verification needed",
            "Coordination with other trades required",
        ],
    }

    # Technical analysis
    technical_analysis = {
        "system_size": f"{analysis.total_devices} devices across {len(analysis.floor_plans)} floors",
        "detection_coverage": f"{analysis.total_building_area / max(analysis.total_devices, 1):.0f} sq ft per device",
        "compliance_status": "Requires review" if rfis else "Compliant",
        "manufacturer": "Simplex (primary), mixed specifications noted",
        "special_requirements": ["Data center protection", "ADA compliance"],
    }

    # Risk assessment
    risk_assessment = {
        "schedule_risk": "Medium - RFI resolution may delay construction",
        "cost_risk": "Low - Standard fire alarm installation",
        "compliance_risk": "Medium - NFPA spacing violations identified",
        "coordination_risk": "Medium - Missing coverage in some areas",
        "mitigation_strategies": [
            "Resolve RFIs before permit submission",
            "Conduct NFPA 72 compliance review",
            "Coordinate with architectural team on coverage gaps",
        ],
    }

    # Cost analysis
    cost_analysis = {
        "cost_per_device": estimate.total_cost / max(analysis.total_devices, 1),
        "cost_per_sq_ft": estimate.total_cost / analysis.total_building_area,
        "material_percentage": (estimate.subtotal_material / estimate.total_cost) * 100,
        "labor_percentage": (estimate.subtotal_labor / estimate.total_cost) * 100,
        "markup_percentage": (
            (estimate.material_markup_amount + estimate.overhead_amount + estimate.profit_amount)
            / estimate.total_cost
        )
        * 100,
    }

    # Recommendations
    recommendations = [
        "Address critical RFI items before proceeding with installation",
        "Verify NFPA 72 spacing compliance in all areas",
        "Complete device specifications for missing areas",
        "Coordinate fire alarm design with architectural plans",
        "Consider value engineering for cost optimization",
    ]

    intelligence = ProjectIntelligence(
        project_name=analysis.project_name,
        executive_summary=executive_summary,
        technical_analysis=technical_analysis,
        risk_assessment=risk_assessment,
        cost_analysis=cost_analysis,
        recommendations=recommendations,
        generated_date=datetime.now(),
    )

    print("✓ Project intelligence generated")
    print(f"  🎯 Project complexity: {executive_summary['project_complexity']}")
    print(f"  ⏱️ Estimated duration: {executive_summary['estimated_duration']}")
    print(f"  💰 Cost per sq ft: ${cost_analysis['cost_per_sq_ft']:.2f}")
    print(f"  ⚠️ Risk level: {risk_assessment['schedule_risk'].split(' -')[0]}")

    return intelligence


def main():
    """Main demonstration workflow"""
    print("🚀 AutoFire Construction Intelligence System - Comprehensive Demo")
    print("=" * 70)

    # Step 1: Create/analyze construction documents
    print("\n🏗️ STEP 1: Construction Document Analysis")
    analysis = create_sample_construction_analysis()

    # Step 2: Generate RFI materials
    print("\n🔍 STEP 2: RFI Intelligence Analysis")
    rfis = demonstrate_rfi_intelligence(analysis)

    # Step 3: Cost estimation
    print("\n💰 STEP 3: Automated Cost Estimation")
    estimate = demonstrate_cost_estimation(analysis)

    # Step 4: Project intelligence
    print("\n📊 STEP 4: Project Intelligence Dashboard")
    intelligence = demonstrate_project_intelligence(analysis, rfis, estimate)

    # Step 5: Export results
    print("\n📄 STEP 5: Export Results")

    # Export RFI report
    rfi_engine = RFIIntelligenceEngine()
    rfi_engine.export_rfi_report(rfis, "demo_rfi_report.txt", analysis.project_name)
    print("  ✓ RFI report exported to: demo_rfi_report.txt")

    # Export project intelligence
    intelligence.export_json(Path("demo_project_intelligence.json"))
    print("  ✓ Project intelligence exported to: demo_project_intelligence.json")

    # Export summary statistics
    summary = {
        "project_name": analysis.project_name,
        "building_area": analysis.total_building_area,
        "device_count": analysis.total_devices,
        "rfi_count": len(rfis),
        "estimated_cost": estimate.total_cost,
        "cost_per_sq_ft": estimate.total_cost / analysis.total_building_area,
        "critical_issues": len([rfi for rfi in rfis if rfi.priority == Priority.CRITICAL]),
        "recommendations": intelligence.recommendations,
    }

    with open("demo_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("  ✓ Project summary exported to: demo_summary.json")

    # Final summary
    print("\n" + "=" * 70)
    print("🎯 CONSTRUCTION INTELLIGENCE DEMO COMPLETE")
    print("=" * 70)
    print(f"📋 Project: {analysis.project_name}")
    print(f"🏗️ Scope: {analysis.total_building_area:.0f} sq ft, {analysis.total_devices} devices")
    print(f"⚠️ Issues identified: {len(rfis)} RFIs generated")
    print(f"💰 Estimated cost: ${estimate.total_cost:,.2f}")
    print("📈 Intelligence report generated with actionable recommendations")
    print("\n🎉 AutoFire Construction Intelligence System is ready for real-world projects!")
    print("\n📁 Files generated:")
    print("  - demo_rfi_report.txt")
    print("  - demo_project_intelligence.json")
    print("  - demo_summary.json")


if __name__ == "__main__":
    main()
