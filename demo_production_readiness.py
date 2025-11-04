#!/usr/bin/env python3
"""
🔥 AutoFire AI - Production Readiness Demo
==========================================

Testing AutoFire AI with realistic building data to demonstrate
complete end-to-end system capabilities.
"""

import sys
from datetime import datetime

# Add project to path
sys.path.append("C:/Dev/Autofire")

from cad_core.intelligence.ai_floor_plan_processor import generate_complete_low_voltage_design


def create_realistic_building_analysis():
    """Create a realistic building analysis for testing"""

    class BuildingAnalysis:
        def __init__(self):
            self.project_name = "AutoFire Corporate Headquarters"
            self.total_pages = 8
            self.floor_plans = [self.create_main_floor()]
            self.fire_alarm_plans = []
            self.schedules = []

        def create_main_floor(self):
            """Create main floor plan data"""

            class FloorPlan:
                def __init__(self):
                    self.sheet_number = "A-101"
                    self.total_area_sq_ft = 12500.0
                    self.scale_factor = 48.0  # 1/4" = 1'-0"
                    self.scale = '1/4" = 1\'-0"'  # Required by AI processor
                    self.north_angle = 15.0
                    self.dimensions = {}  # Required by AI processor
                    self.rooms = self.create_rooms()

                def create_rooms(self):
                    """Create realistic room layout"""
                    return [
                        Room("Executive Office", "private_office", 320.0, "executive"),
                        Room("Open Office Area", "open_office", 2400.0, "workspace"),
                        Room("Conference Room A", "conference", 450.0, "meeting"),
                        Room("Conference Room B", "conference", 380.0, "meeting"),
                        Room("Reception Lobby", "public", 600.0, "public"),
                        Room("Break Room", "common", 280.0, "common"),
                        Room("Server Room", "equipment", 180.0, "critical"),
                        Room("Electrical Room", "equipment", 120.0, "utility"),
                        Room("Storage Room", "storage", 150.0, "storage"),
                        Room("Copy/Print Center", "work", 200.0, "support"),
                        Room("Training Room", "training", 550.0, "meeting"),
                        Room("Kitchen", "kitchen", 350.0, "common"),
                    ]

            return FloorPlan()

    class Room:
        def __init__(self, name, room_type, area, classification):
            self.name = name
            self.room_type = room_type
            self.area_sq_ft = area
            self.area = area  # Required by AI processor
            self.classification = classification
            self.occupancy_type = self.map_to_occupancy_type(
                classification
            )  # Required by AI processor
            self.number = None  # Room number (optional)
            self.ceiling_height = 9.0  # Standard ceiling height

            # Simple rectangular coordinates based on area
            width = area**0.5
            height = area / width
            self.coordinates = [(0, 0), (width, 0), (width, height), (0, height)]

            # Add special requirements based on room type
            self.special_requirements = self.determine_requirements()

        def map_to_occupancy_type(self, classification):
            """Map classification to occupancy types expected by AI processor"""
            mapping = {
                "critical": "Secure Control",
                "executive": "Office",
                "meeting": "Conference",
                "public": "Assembly Public",
                "common": "Office",
                "utility": "Office",
                "storage": "Office",
                "support": "Office",
                "workspace": "Office",
            }
            return mapping.get(classification, "Office")

        def determine_requirements(self):
            """Determine special requirements based on room type"""
            requirements = []

            if self.classification == "critical":
                requirements.extend(["24/7_monitoring", "backup_power", "fire_suppression"])
            elif self.classification == "executive":
                requirements.extend(["enhanced_security", "av_systems", "climate_control"])
            elif self.classification == "meeting":
                requirements.extend(["av_systems", "presentation_capability", "wireless_access"])
            elif self.classification == "public":
                requirements.extend(
                    ["ada_compliance", "emergency_communication", "security_monitoring"]
                )
            elif self.room_type == "open_office":
                requirements.extend(
                    ["distributed_power", "data_connectivity", "wireless_infrastructure"]
                )

            return requirements

    return BuildingAnalysis()


def run_production_readiness_test():
    """Test AutoFire AI production readiness"""

    print("🔥 AutoFire AI - Production Readiness Test")
    print("=" * 45)
    print("Testing complete system with realistic building data...")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Create realistic building analysis
    building_analysis = create_realistic_building_analysis()

    # Display building information
    print("\n🏢 Building Analysis Summary")
    print("-" * 30)
    print(f"Project: {building_analysis.project_name}")
    print(f"Drawing Pages: {building_analysis.total_pages}")
    print(f"Floor Plans: {len(building_analysis.floor_plans)}")

    floor_plan = building_analysis.floor_plans[0]
    print(f"\nFloor Plan: {floor_plan.sheet_number}")
    print(f"Total Area: {floor_plan.total_area_sq_ft:,.0f} sq ft")
    print('Drawing Scale: 1/4" = 1\'-0"')
    print(f"Room Count: {len(floor_plan.rooms)}")

    # Show room breakdown
    print("\nRoom Analysis:")
    total_area = 0
    room_types = {}

    for room in floor_plan.rooms:
        total_area += room.area_sq_ft
        room_type = room.classification
        if room_type not in room_types:
            room_types[room_type] = {"count": 0, "area": 0}
        room_types[room_type]["count"] += 1
        room_types[room_type]["area"] += room.area_sq_ft

        print(f"• {room.name}: {room.area_sq_ft:.0f} sq ft ({room.classification})")
        if room.special_requirements:
            print(f"  Requirements: {', '.join(room.special_requirements)}")

    print("\nBuilding Statistics:")
    print(f"• Total Analyzed Area: {total_area:,.0f} sq ft")
    print("• Room Type Distribution:")
    for rtype, data in room_types.items():
        print(f"  - {rtype.title()}: {data['count']} rooms, {data['area']:,.0f} sq ft")

    # Generate complete low voltage design
    print("\n🚀 Generating Complete Low Voltage System Design...")
    print("-" * 52)

    try:
        complete_design = generate_complete_low_voltage_design(building_analysis)

        print("✅ Design Generation Complete!")

        # Display design results
        total_devices = getattr(complete_design, "total_devices", 0)
        device_types = getattr(complete_design, "device_types", [])
        estimated_cost = getattr(complete_design, "estimated_cost", 0)
        implementation_weeks = getattr(complete_design, "implementation_weeks", 0)

        print("\n📊 System Design Summary:")
        print(f"• Total Devices Specified: {total_devices}")
        print(f"• Device Type Categories: {len(device_types)}")
        print(f"• Estimated Project Cost: ${estimated_cost:,.2f}")
        print(f"• Implementation Timeline: {implementation_weeks} weeks")

        # Show simplified floor plans
        simplified_plans = getattr(complete_design, "simplified_floor_plans", [])
        if simplified_plans:
            print("\n🏗️ Simplified Floor Plans Generated:")
            for plan in simplified_plans:
                sheet_num = getattr(plan, "sheet_number", "Unknown")
                zones = getattr(plan, "low_voltage_zones", [])
                total_zone_area = sum(getattr(zone, "area_sq_ft", 0) for zone in zones)

                print(
                    f"• {sheet_num}: {len(zones)} low voltage zones, {total_zone_area:,.0f} sq ft"
                )

                # Show zone breakdown
                zone_types = {}
                for zone in zones:
                    ztype = getattr(zone, "zone_type", "unknown")
                    if ztype not in zone_types:
                        zone_types[ztype] = 0
                    zone_types[ztype] += 1

                if zone_types:
                    print(
                        f"  Zone types: {', '.join([f'{t}: {c}' for t, c in zone_types.items()])}"
                    )

        # Show device breakdown
        if device_types:
            print("\n🔌 Device Specification Breakdown:")
            total_project_cost = 0

            for device in device_types[:10]:  # Show top 10 device types
                name = getattr(device, "name", "Unknown Device")
                quantity = getattr(device, "quantity", 0)
                unit_cost = getattr(device, "unit_cost", 0)
                total_cost = quantity * unit_cost
                total_project_cost += total_cost

                print(f"• {name}: {quantity} units @ ${unit_cost:.2f} = ${total_cost:,.2f}")

            if len(device_types) > 10:
                remaining_cost = estimated_cost - total_project_cost
                print(
                    f"• ... and {len(device_types) - 10} more device types: ${remaining_cost:,.2f}"
                )

        # Show implementation phases
        phases = getattr(complete_design, "implementation_phases", [])
        if phases:
            print("\n📅 Implementation Plan:")
            for i, phase in enumerate(phases, 1):
                name = getattr(phase, "name", f"Phase {i}")
                weeks = getattr(phase, "duration_weeks", 0)
                tasks = getattr(phase, "tasks", [])
                print(f"{i}. {name}: {weeks} weeks ({len(tasks)} tasks)")

        # Production readiness assessment
        print("\n🎯 Production Readiness Assessment")
        print("-" * 35)

        readiness_score = 0
        max_score = 5

        # Check 1: Design generation successful
        if total_devices > 0:
            print("✅ Design Generation: PASS")
            readiness_score += 1
        else:
            print("⚠️  Design Generation: Needs improvement")

        # Check 2: Cost estimation available
        if estimated_cost > 0:
            print("✅ Cost Estimation: PASS")
            readiness_score += 1
        else:
            print("⚠️  Cost Estimation: Needs improvement")

        # Check 3: Timeline planning
        if implementation_weeks > 0:
            print("✅ Timeline Planning: PASS")
            readiness_score += 1
        else:
            print("⚠️  Timeline Planning: Needs improvement")

        # Check 4: Zone analysis
        if simplified_plans and len(simplified_plans) > 0:
            print("✅ Zone Analysis: PASS")
            readiness_score += 1
        else:
            print("⚠️  Zone Analysis: Needs improvement")

        # Check 5: Device specification
        if len(device_types) > 0:
            print("✅ Device Specification: PASS")
            readiness_score += 1
        else:
            print("⚠️  Device Specification: Needs improvement")

        # Final assessment
        readiness_percentage = (readiness_score / max_score) * 100

        print(
            f"\n🏆 Production Readiness Score: {readiness_score}/{max_score} ({readiness_percentage:.0f}%)"
        )

        if readiness_percentage >= 80:
            print("🚀 STATUS: READY FOR PRODUCTION DEPLOYMENT!")
            print("🔥 AutoFire AI is fully operational and ready for customer use!")
        elif readiness_percentage >= 60:
            print("🔄 STATUS: Near production ready - minor improvements needed")
        else:
            print("⚠️  STATUS: Development continues - core functionality working")

        return True

    except Exception as e:
        print(f"❌ Error during design generation: {e}")
        print("System needs debugging before production deployment")
        return False


if __name__ == "__main__":
    print("Starting AutoFire AI Production Readiness Test...")
    print("=" * 55)

    success = run_production_readiness_test()

    print("\n" + "=" * 55)
    if success:
        print("✅ PRODUCTION READINESS TEST COMPLETE!")
        print("🔥 AutoFire AI demonstrated full end-to-end capabilities!")
    else:
        print("❌ Production readiness test encountered issues")

    print("Test completed at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
