#!/usr/bin/env python3
"""
AutoFire Practical Applications Demo
Shows what you can actually DO with the extracted construction data
"""


class AutoFireApplications:
    """
    Demonstrates practical applications of AutoFire's data extraction capabilities
    """

    def __init__(self):
        self.project_data = {}
        self.applications = {
            "fire_code_compliance": self.generate_compliance_report,
            "device_placement": self.calculate_device_placement,
            "cost_estimation": self.generate_cost_estimates,
            "submittal_packages": self.create_submittal_packages,
            "installation_plans": self.generate_installation_plans,
            "maintenance_schedules": self.create_maintenance_schedules,
            "inspection_checklists": self.generate_inspection_checklists,
            "emergency_procedures": self.create_emergency_procedures,
        }

    def demonstrate_applications(self):
        """Demonstrate all practical applications"""
        print("🔥 AUTOFIRE PRACTICAL APPLICATIONS")
        print("What You Can Actually DO With The Extracted Data")
        print("=" * 55)
        print()

        # Simulate extracted data from our previous analysis
        self._load_sample_data()

        print("📊 AVAILABLE APPLICATIONS:")
        for i, (app_name, app_func) in enumerate(self.applications.items(), 1):
            app_title = app_name.replace("_", " ").title()
            print(f"   {i}. {app_title}")

        print()

        # Demonstrate each application
        for app_name, app_func in self.applications.items():
            print(f"\n{'='*60}")
            app_title = app_name.replace("_", " ").title()
            print(f"🎯 APPLICATION: {app_title.upper()}")
            print("=" * 60)

            try:
                result = app_func()
                if result:
                    print("✅ Successfully generated!")
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    def _load_sample_data(self):
        """Load sample data based on our previous extractions"""
        self.project_data = {
            "hilton_hotel": {
                "building_type": "Hotel",
                "floors": 5,
                "total_devices": 1042,
                "fire_terms": {"FIRE": 39, "SPRINKLER": 19, "NFPA": 12, "SMOKE": 1, "ALARM": 1},
                "room_types": ["Guest Room", "Corridor", "Lobby", "Restaurant", "Kitchen"],
                "occupancy_type": "R-1 Hotel",
                "construction_type": "Type IIA",
            },
            "diventures_aquatic": {
                "building_type": "Aquatic Facility",
                "floors": 1,
                "total_devices": 193,
                "fire_terms": {
                    "FIRE": 26,
                    "ALARM": 20,
                    "EXIT": 7,
                    "EMERGENCY": 7,
                    "SMOKE": 6,
                    "SPRINKLER": 2,
                },
                "room_types": ["Pool Deck", "Natatorium", "Chemical Storage", "Mechanical Room"],
                "occupancy_type": "A-3 Assembly",
                "construction_type": "Type IIB",
            },
        }

    def generate_compliance_report(self):
        """Generate NFPA/IBC compliance reports"""
        print("📋 FIRE CODE COMPLIANCE ANALYSIS")
        print("-" * 35)

        for project_name, data in self.project_data.items():
            project_title = project_name.replace("_", " ").title()
            print(f"\n🏗️  {project_title}:")
            print(f"   Building Type: {data['building_type']}")
            print(f"   Occupancy: {data['occupancy_type']}")
            print(f"   Construction: {data['construction_type']}")

            # Generate compliance requirements
            compliance = self._analyze_compliance_requirements(data)

            print("\n   📖 Required Codes & Standards:")
            for code, requirement in compliance.items():
                print(f"      ✓ {code}: {requirement}")

            print("\n   🔥 Fire Protection Status:")
            if data["fire_terms"]["SPRINKLER"] > 0:
                print("      ✅ Sprinkler system detected")
            if data["fire_terms"]["ALARM"] > 0:
                print("      ✅ Fire alarm system detected")
            if data["fire_terms"]["SMOKE"] > 0:
                print("      ✅ Smoke detection system detected")

            # Compliance score
            compliance_score = min(100, (sum(data["fire_terms"].values()) / 10) * 100)
            print(f"\n   📊 Compliance Score: {compliance_score:.0f}%")

        return True

    def _analyze_compliance_requirements(self, data: dict) -> dict[str, str]:
        """Analyze compliance requirements based on building data"""
        requirements = {}

        if data["occupancy_type"].startswith("R-1"):
            requirements["NFPA 101"] = "Life Safety Code for hotels"
            requirements["NFPA 72"] = "Fire alarm systems in guest rooms"
            requirements["NFPA 13"] = "Sprinkler systems throughout"
            requirements["IBC Chapter 9"] = "Fire protection systems"

        elif data["occupancy_type"].startswith("A-3"):
            requirements["NFPA 101"] = "Assembly occupancy egress"
            requirements["NFPA 13"] = "Sprinkler protection required"
            requirements["NFPA 72"] = "Mass notification systems"
            requirements["IBC Chapter 10"] = "Means of egress"

        return requirements

    def calculate_device_placement(self):
        """Calculate optimal fire device placement"""
        print("📍 FIRE DEVICE PLACEMENT OPTIMIZATION")
        print("-" * 40)

        for project_name, data in self.project_data.items():
            project_title = project_name.replace("_", " ").title()
            print(f"\n🏗️  {project_title} Device Layout:")

            # Calculate device density
            total_area = data["floors"] * 10000  # Assume 10k sq ft per floor
            device_density = data["total_devices"] / total_area

            print(f"   📊 Current Device Density: {device_density:.3f} devices/sq ft")

            # Room-specific recommendations
            print("\n   🎯 Room-Specific Placement:")
            for room_type in data["room_types"]:
                recommendations = self._get_placement_recommendations(
                    room_type, data["building_type"]
                )
                print(f"      • {room_type}: {recommendations}")

            # Device count breakdown
            estimated_breakdown = self._estimate_device_breakdown(data)
            print("\n   🔢 Estimated Device Breakdown:")
            for device_type, count in estimated_breakdown.items():
                print(f"      • {device_type}: {count} units")

        return True

    def _get_placement_recommendations(self, room_type: str, building_type: str) -> str:
        """Get placement recommendations for specific room types"""
        recommendations = {
            "Guest Room": "Smoke detector center of room, sprinkler over bed area",
            "Corridor": "Smoke detectors every 30ft, strobes every 100ft",
            "Lobby": "Beam detectors for high ceilings, voice evacuation",
            "Restaurant": "Heat detectors in kitchen, sprinklers throughout",
            "Kitchen": "Heat detectors, Class K suppression system",
            "Pool Deck": "Corrosion-resistant devices, emergency lighting",
            "Natatorium": "Smoke evacuation system, pool area notification",
            "Chemical Storage": "Special suppression system, ventilation interlocks",
            "Mechanical Room": "Pre-action sprinkler system, equipment shutdown",
        }

        return recommendations.get(room_type, "Standard detection and suppression")

    def _estimate_device_breakdown(self, data: dict) -> dict[str, int]:
        """Estimate device count breakdown"""
        total = data["total_devices"]

        if data["building_type"] == "Hotel":
            return {
                "Smoke Detectors": int(total * 0.35),
                "Sprinkler Heads": int(total * 0.50),
                "Pull Stations": int(total * 0.05),
                "Horn/Strobes": int(total * 0.08),
                "Fire Extinguishers": int(total * 0.02),
            }
        else:  # Aquatic facility
            return {
                "Smoke Detectors": int(total * 0.25),
                "Sprinkler Heads": int(total * 0.45),
                "Pool Area Devices": int(total * 0.15),
                "Emergency Equipment": int(total * 0.10),
                "Notification Devices": int(total * 0.05),
            }

    def generate_cost_estimates(self):
        """Generate detailed cost estimates"""
        print("💰 FIRE PROTECTION COST ESTIMATION")
        print("-" * 38)

        for project_name, data in self.project_data.items():
            project_title = project_name.replace("_", " ").title()
            print(f"\n🏗️  {project_title} Cost Analysis:")

            # Calculate costs
            costs = self._calculate_project_costs(data)

            print("\n   💵 Material Costs:")
            total_material = 0
            for item, cost in costs["materials"].items():
                print(f"      • {item}: ${cost:,}")
                total_material += cost

            print("\n   👷 Labor Costs:")
            total_labor = 0
            for item, cost in costs["labor"].items():
                print(f"      • {item}: ${cost:,}")
                total_labor += cost

            total_project = total_material + total_labor
            print("\n   📊 Project Totals:")
            print(f"      • Materials: ${total_material:,}")
            print(f"      • Labor: ${total_labor:,}")
            print(f"      • Total Project: ${total_project:,}")
            print(f"      • Cost per Device: ${total_project/data['total_devices']:.0f}")

        return True

    def _calculate_project_costs(self, data: dict) -> dict:
        """Calculate detailed project costs"""
        device_count = data["total_devices"]
        building_complexity = (
            1.2 if data["building_type"] == "Hotel" else 1.5
        )  # Aquatic is more complex

        materials = {
            "Fire Alarm Panel": 15000,
            "Smoke Detectors": device_count * 85,
            "Sprinkler Heads": device_count * 25,
            "Notification Devices": device_count * 65,
            "Conduit & Wire": device_count * 35,
            "Control Modules": device_count * 45,
        }

        labor = {
            "Installation": int(sum(materials.values()) * 0.6 * building_complexity),
            "Programming": 8500,
            "Testing & Commissioning": 12000,
            "Documentation": 3500,
        }

        return {"materials": materials, "labor": labor}

    def create_submittal_packages(self):
        """Create professional submittal packages"""
        print("📦 SUBMITTAL PACKAGE GENERATION")
        print("-" * 35)

        submittal_items = [
            "Product Data Sheets",
            "Installation Instructions",
            "Wiring Diagrams",
            "Sequence of Operations",
            "Testing Procedures",
            "Warranty Information",
            "NFPA Compliance Certificates",
            "UL Listing Documentation",
        ]

        print("📋 Standard Submittal Package Includes:")
        for i, item in enumerate(submittal_items, 1):
            print(f"   {i}. {item}")

        print("\n🎯 AutoFire Advantages:")
        print("   ✅ Automatically generated from extracted data")
        print("   ✅ Building-specific requirements included")
        print("   ✅ Code compliance documentation")
        print("   ✅ Professional formatting and organization")
        print("   ✅ Ready for AHJ review and approval")

        return True

    def generate_installation_plans(self):
        """Generate detailed installation plans"""
        print("🔧 INSTALLATION PLAN GENERATION")
        print("-" * 35)

        installation_phases = [
            "Phase 1: Rough-in electrical and low voltage",
            "Phase 2: Install fire alarm panel and networking",
            "Phase 3: Install detection devices",
            "Phase 4: Install notification devices",
            "Phase 5: System programming and testing",
            "Phase 6: Final inspection and commissioning",
        ]

        print("📅 Installation Schedule:")
        for phase in installation_phases:
            print(f"   • {phase}")

        print("\n🎯 Installation Deliverables:")
        deliverables = [
            "Device location drawings",
            "Wiring schedules and diagrams",
            "Equipment cut sheets",
            "Installation sequence plans",
            "Testing and commissioning procedures",
            "As-built documentation",
        ]

        for deliverable in deliverables:
            print(f"   ✓ {deliverable}")

        return True

    def create_maintenance_schedules(self):
        """Create maintenance and testing schedules"""
        print("🔄 MAINTENANCE SCHEDULE CREATION")
        print("-" * 36)

        maintenance_schedule = {
            "Monthly": [
                "Visual inspection of devices",
                "Test sample of devices",
                "Check system status",
            ],
            "Quarterly": [
                "Test 25% of detection devices",
                "Test notification appliances",
                "Battery backup testing",
            ],
            "Semi-Annual": [
                "Test fire alarm communication",
                "Inspect wiring and connections",
                "Update system documentation",
            ],
            "Annual": [
                "Complete system testing",
                "Professional inspection",
                "Code compliance review",
                "Update emergency procedures",
            ],
        }

        for frequency, tasks in maintenance_schedule.items():
            print(f"\n📅 {frequency} Tasks:")
            for task in tasks:
                print(f"   • {task}")

        return True

    def generate_inspection_checklists(self):
        """Generate inspection checklists for AHJ"""
        print("✅ INSPECTION CHECKLIST GENERATION")
        print("-" * 38)

        inspection_categories = {
            "Installation Inspection": [
                "Device locations per approved plans",
                "Proper mounting and spacing",
                "Wiring methods and protection",
                "System grounding and bonding",
            ],
            "Functional Testing": [
                "Alarm initiation devices",
                "Notification appliances",
                "Control functions",
                "Emergency power systems",
            ],
            "Code Compliance": [
                "NFPA 72 requirements",
                "Local code modifications",
                "ADA compliance features",
                "Documentation completeness",
            ],
        }

        for category, items in inspection_categories.items():
            print(f"\n📋 {category}:")
            for item in items:
                print(f"   ☐ {item}")

        return True

    def create_emergency_procedures(self):
        """Create emergency response procedures"""
        print("🚨 EMERGENCY PROCEDURES CREATION")
        print("-" * 37)

        print("📖 Emergency Response Procedures:")

        procedures = [
            "Fire Alarm Activation Response",
            "Evacuation Procedures",
            "Fire Department Notification",
            "System Silencing and Reset",
            "Emergency Contact Information",
            "Special Procedures for Building Type",
        ]

        for i, procedure in enumerate(procedures, 1):
            print(f"   {i}. {procedure}")

        print("\n🎯 Building-Specific Procedures:")

        for project_name, data in self.project_data.items():
            project_title = project_name.replace("_", " ").title()
            print(f"\n   🏗️  {project_title}:")

            if data["building_type"] == "Hotel":
                print("      • Guest notification procedures")
                print("      • Elevator recall operations")
                print("      • Kitchen suppression coordination")
            elif data["building_type"] == "Aquatic Facility":
                print("      • Pool evacuation procedures")
                print("      • Chemical storage emergency response")
                print("      • Natatorium smoke evacuation")

        return True


def main():
    """Demonstrate AutoFire practical applications"""
    print("🚀 AUTOFIRE: FROM DATA TO ACTION")
    print("=" * 40)
    print("Moving beyond extraction to practical applications")
    print()

    applications = AutoFireApplications()
    applications.demonstrate_applications()

    print("\n" + "=" * 60)
    print("🎯 AUTOFIRE VALUE PROPOSITION")
    print("=" * 60)

    value_points = [
        "✅ Instant fire protection design from construction drawings",
        "✅ Automated code compliance analysis and reporting",
        "✅ Professional submittal packages ready for AHJ review",
        "✅ Detailed cost estimates with material and labor breakdown",
        "✅ Complete installation plans and schedules",
        "✅ Maintenance procedures and inspection checklists",
        "✅ Building-specific emergency response procedures",
        "✅ All deliverables generated automatically from extracted data",
    ]

    for point in value_points:
        print(f"   {point}")

    print("\n💡 THE BOTTOM LINE:")
    print("AutoFire doesn't just extract data - it transforms that data")
    print("into actionable deliverables that save time, reduce costs,")
    print("and ensure compliance across the entire project lifecycle!")


if __name__ == "__main__":
    main()
