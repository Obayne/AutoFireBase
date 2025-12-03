#!/usr/bin/env python3
"""
Test script demonstrating improved AI abstract reasoning capabilities.

This script shows how the AI now handles incomplete information by making
reasonable assumptions and asking clarifying questions when needed.
"""

from ai_knowledge_base import knowledge_base

def test_church_scenario():
    """Test the church scenario that the user mentioned."""
    print("🕍 Testing Church Scenario (User's Example)")
    print("=" * 50)

    # Scenario: User says "I need to design a fire alarm system for a church"
    building_description = "church"
    building_area = 5000  # 5,000 sq ft

    print(f"User input: Building type = '{building_description}', Area = {building_area} sq ft")
    print("AI makes reasonable assumptions instead of asking for occupancy type...")

    # AI now makes the inference automatically
    result = knowledge_base.calculate_system_requirements(
        building_area=building_area,
        building_description=building_description,
        make_assumptions=True
    )

    print("\n✅ AI Response:")
    if "assumptions_made" in result:
        assumptions = result["assumptions_made"]
        if "occupancy_assumptions" in assumptions:
            occ_assumption = assumptions["occupancy_assumptions"]
            print(f"  📋 Occupancy Inference: {occ_assumption['inferred_occupancy']} "
                  f"(confidence: {occ_assumption['confidence']:.0%})")
            print(f"     Reason: {occ_assumption['reason']}")

    print(f"  🏗️  System Design: {result['building_characteristics']['occupancy_type']} occupancy")
    print(f"  🔍 Smoke Detectors: {result['estimated_devices']['smoke_detectors']}")
    print(f"  📣 Notification Appliances: {result['estimated_devices']['notification_appliances']}")
    print(f"  🔋 Battery Capacity: {result['system_sizing']['battery_capacity_ah']} Ah")

    if "clarification_needed" in result.get("assumptions_made", {}).get("occupancy_assumptions", {}):
        if result["assumptions_made"]["occupancy_assumptions"]["clarification_needed"]:
            print("  ❓ Suggested follow-up: May want to confirm occupancy with local AHJ")

def test_unclear_scenario():
    """Test a scenario where AI cannot make clear assumptions."""
    print("\n🏢 Testing Unclear Building Scenario")
    print("=" * 50)

    # Scenario: User says "I need to design for a building"
    building_description = "building"
    building_area = 10000  # 10,000 sq ft

    print(f"User input: Building type = '{building_description}', Area = {building_area} sq ft")
    print("AI recognizes this is too vague and asks for clarification...")

    result = knowledge_base.calculate_system_requirements(
        building_area=building_area,
        building_description=building_description,
        make_assumptions=True
    )

    print("\n❌ AI Response:")
    print(f"  Error: {result.get('error', 'Unknown error')}")
    print(f"  Suggestion: {result.get('suggestion', 'No suggestion provided')}")

    # Show what clarifying questions AI would ask
    inference = knowledge_base.infer_occupancy_from_description(building_description)
    if inference["clarification_needed"]:
        print("  ❓ Suggested questions:")
        for question in inference["suggested_questions"]:
            print(f"     • {question}")

def test_inference_engine():
    """Test the inference engine with various building types."""
    print("\n🧠 Testing AI Inference Engine")
    print("=" * 50)

    test_cases = [
        "church sanctuary",
        "hospital emergency room",
        "school gymnasium",
        "office building",
        "restaurant dining area",
        "warehouse storage",
        "hotel lobby",
        "apartment complex"
    ]

    for building_type in test_cases:
        inference = knowledge_base.infer_occupancy_from_description(building_type)
        confidence_icon = "🟢" if inference["confidence"] >= 0.9 else "🟡" if inference["confidence"] >= 0.8 else "🟠"
        clarification = " (may need confirmation)" if inference["clarification_needed"] else ""

        print(f"  {confidence_icon} '{building_type}' → {inference['inferred_occupancy']} "
              f"({inference['confidence']:.0%}){clarification}")

def test_design_assumptions():
    """Test how AI makes design assumptions."""
    print("\n📐 Testing Design Assumptions")
    print("=" * 50)

    # Test with partial information
    building_info = {
        "building_type": "industrial warehouse",
        # Missing: occupancy_type, ceiling_height, jurisdiction
    }

    assumptions = knowledge_base.get_design_assumptions(building_info)

    print("Building: Industrial Warehouse (partial information)")
    print("AI assumptions made:")

    if assumptions["occupancy_assumptions"]:
        occ = assumptions["occupancy_assumptions"]
        print(f"  📋 Occupancy: {occ['inferred_occupancy']} ({occ['confidence']:.0%} confidence)")

    if assumptions["design_assumptions"]:
        for param, details in assumptions["design_assumptions"].items():
            print(f"  📏 {param.title()}: {details['assumed_value']} "
                  f"({details['confidence']:.0%} confidence)")

    if assumptions["code_assumptions"]:
        for param, details in assumptions["code_assumptions"].items():
            print(f"  📖 {param.title()}: {details['assumed_value']} "
                  f"({details['confidence']:.0%} confidence)")

if __name__ == "__main__":
    print("🤖 AI Abstract Reasoning Improvements Demo")
    print("Demonstrating how AI now handles incomplete information intelligently\n")

    test_church_scenario()
    test_unclear_scenario()
    test_inference_engine()
    test_design_assumptions()

    print("\n🎉 Summary of Improvements:")
    print("  ✓ AI makes reasonable assumptions based on building type")
    print("  ✓ Recognizes when more information is needed")
    print("  ✓ Provides confidence levels for all assumptions")
    print("  ✓ Suggests specific clarifying questions when appropriate")
    print("  ✓ Continues with design calculations using inferred information")
    print("  ✓ Documents all assumptions made for transparency")
