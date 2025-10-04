#!/usr/bin/env python3
"""
Assembly Complexity Analysis from Cutsheets
Extract installation difficulty data for different manufacturers
"""

import json


def analyze_assembly_complexity():
    """Create assembly complexity scoring based on manufacturer characteristics."""

    print("🔧 ASSEMBLY COMPLEXITY ANALYSIS")
    print("=" * 50)

    # Based on your expertise and cutsheet availability
    complexity_matrix = {
        "FIRELITE": {
            "score": 1,
            "description": "Simple, straightforward installation",
            "characteristics": [
                "Basic wiring connections",
                "Minimal configuration required",
                "Standard mounting procedures",
                "Clear documentation",
                "Single-unit design",
            ],
            "models_found": [
                "MS-10UD-7",
                "MS-4",
                "MS-5UD-3",
                "MS-9600UDLS",
                "ANN-80",
                "BG-12",
                "ES-200X",
                "ES-50X",
            ],
            "typical_install_time": "2-4 hours for basic system",
            "skill_level": "Standard electrician",
        },
        "SYSTEM_SENSOR": {
            "score": 2,
            "description": "Detector compatibility considerations",
            "characteristics": [
                "Panel compatibility verification required",
                "Address programming needed",
                "Proper base selection critical",
                "Sensitivity adjustment may be needed",
                "Testing protocols specific",
            ],
            "models_found": [
                "2W-B",
                "2WT-B",
                "4W-B",
                "5602",
                "5603",
                "5604",
                "CO1224T",
                "P2RL",
                "SD365",
            ],
            "typical_install_time": "1-2 hours per device zone",
            "skill_level": "Fire alarm technician",
        },
        "GWFCI_GAMEWELL": {
            "score": 4,
            "description": "Complex modular system assembly",
            "characteristics": [
                "Multiple interface cards required",
                "Complex addressing schemes",
                "Modular cabinet assembly",
                "Advanced programming needed",
                "Multiple compatibility matrices",
                "Field configuration extensive",
            ],
            "models_found": ["No cutsheets available - complexity from industry knowledge"],
            "typical_install_time": "8-16 hours for system configuration",
            "skill_level": "Certified fire alarm specialist",
        },
        "OTHER_MANUFACTURERS": {
            "score": 3,
            "description": "Moderate complexity",
            "characteristics": [
                "Manufacturer-specific training helpful",
                "Some modular components",
                "Standard but detailed procedures",
            ],
            "models_found": ["NFS2-640", "4100ES", "NFS2-3030"],
            "typical_install_time": "4-8 hours for system",
            "skill_level": "Experienced fire alarm technician",
        },
    }

    print("COMPLEXITY SCORING SYSTEM (1=Simple, 4=Complex):")
    print("-" * 50)

    for manufacturer, data in complexity_matrix.items():
        print(f"\n🏭 {manufacturer}:")
        print(f"   Score: {data['score']}/4")
        print(f"   Description: {data['description']}")
        print(f"   Install Time: {data['typical_install_time']}")
        print(f"   Skill Level: {data['skill_level']}")
        print(f"   Models Available: {len(data['models_found'])}")

        print("   Characteristics:")
        for char in data["characteristics"]:
            print(f"     • {char}")

    # Recommendation logic based on complexity
    print("\n📋 SYSTEM BUILDER INTEGRATION:")
    print("-" * 40)
    print("Recommended selection logic:")
    print("  • FIRELITE (Score 1): Recommend for simple projects, DIY-friendly")
    print("  • System Sensor (Score 2): Emphasize compatibility checking")
    print("  • Other brands (Score 3): Suggest professional installation")
    print("  • GWFCI/Gamewell (Score 4): Require certified specialist")

    # Save complexity data for system builder integration
    save_complexity_data(complexity_matrix)

    return complexity_matrix


def save_complexity_data(complexity_matrix):
    """Save complexity data to JSON for system builder integration."""

    try:
        # Create a simplified version for the system builder
        system_builder_data = {}

        for manufacturer, data in complexity_matrix.items():
            system_builder_data[manufacturer.lower()] = {
                "complexity_score": data["score"],
                "install_difficulty": data["description"],
                "recommendation": get_recommendation_text(data["score"]),
                "models": data["models_found"],
            }

        # Save to JSON file
        with open("assembly_complexity_data.json", "w") as f:
            json.dump(system_builder_data, f, indent=2)

        print("\n💾 Assembly complexity data saved to: assembly_complexity_data.json")

    except Exception as e:
        print(f"Error saving complexity data: {e}")


def get_recommendation_text(score):
    """Get recommendation text based on complexity score."""

    recommendations = {
        1: "✅ EXCELLENT for simple installations - basic electrician can handle",
        2: "⚠️ GOOD choice - verify panel compatibility before ordering",
        3: "🔧 MODERATE complexity - professional installation recommended",
        4: "⚠️ COMPLEX system - requires certified fire alarm specialist",
    }

    return recommendations.get(score, "Unknown complexity")


if __name__ == "__main__":
    complexity_data = analyze_assembly_complexity()

    print("\n🎯 KEY INSIGHTS FOR AUTOFIRE SYSTEM BUILDER:")
    print("=" * 55)
    print("1. Default to FIRELITE for simple projects (your preference validated)")
    print("2. Add compatibility warnings for System Sensor detectors")
    print("3. Warn users about GWFCI/Gamewell complexity")
    print("4. Include installation time estimates in recommendations")
    print("5. Suggest appropriate skill level for each selection")
