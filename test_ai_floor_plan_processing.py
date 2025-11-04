#!/usr/bin/env python3
"""
TEST ACTUAL AI FLOOR PLAN PROCESSING
Test what the AI Floor Plan Processor actually does with real construction drawings
"""

import sys

sys.path.append("C:/Dev/Autofire")


def test_real_floor_plan_processing():
    """Test AI floor plan processing with the 15.6MB construction set"""

    print("🔍 TESTING AI FLOOR PLAN PROCESSING")
    print("=" * 50)

    try:
        # Get construction analysis from the real construction set
        from cad_core.intelligence.ai_floor_plan_processor import AIFloorPlanProcessor
        from cad_core.intelligence.pdf_analyzer import PDFConstructionAnalyzer

        analyzer = PDFConstructionAnalyzer()
        construction_set = "C:/Dev/rfp-24-001-general-contractor-construction-drawings.pdf"

        print("📄 Analyzing construction set...")
        result = analyzer.analyze_construction_set(construction_set)
        print(f"✅ Found {len(result.floor_plans)} floor plans")

        if not result.floor_plans:
            print("❌ No floor plans to process")
            return

        # Test the AI Floor Plan Processor
        processor = AIFloorPlanProcessor()

        # Process the first floor plan
        fp = result.floor_plans[0]
        print(f"\n🏗️ Processing floor plan: {fp.sheet_number}")

        try:
            # This is the key test - what does it actually produce?
            simplified = processor.process_floor_plan_for_low_voltage(fp, result)

            print("\n📊 PROCESSING RESULTS:")
            print("-" * 30)
            print(f"Sheet: {simplified.sheet_number}")
            print(f"Area: {simplified.total_area_sq_ft} sq ft")
            print(f"Scale: {simplified.scale_factor}")
            print(f"Structural Elements: {len(simplified.structural_elements)}")
            print(f"Low Voltage Zones: {len(simplified.low_voltage_zones)}")

            # Examine what's in the structural elements
            if simplified.structural_elements:
                print("\n🏗️ STRUCTURAL ELEMENTS:")
                for i, elem in enumerate(simplified.structural_elements[:3]):
                    print(f"  {i+1}. Type: {elem.element_type}")
                    print(f"     Coordinates: {len(elem.coordinates)} points")
                    print(f"     Properties: {elem.properties}")
                    print(f"     Impact: {elem.low_voltage_impact}")

            # Examine low voltage zones
            if simplified.low_voltage_zones:
                print("\n⚡ LOW VOLTAGE ZONES:")
                for i, zone in enumerate(simplified.low_voltage_zones[:3]):
                    print(f"  {i+1}. ID: {zone.zone_id}")
                    print(f"     Type: {zone.zone_type}")
                    print(f"     Area: {zone.area_sq_ft} sq ft")
                    print(f"     Devices: {len(zone.device_requirements)}")
                    print(f"     Requirements: {zone.special_requirements}")

            # THE KEY QUESTION: Does this show real architectural understanding?
            print("\n🤔 ANALYSIS:")
            print("Does this show real architectural understanding?")

            if simplified.structural_elements:
                has_walls = any(
                    elem.element_type == "wall" for elem in simplified.structural_elements
                )
                has_doors = any(
                    elem.element_type == "door" for elem in simplified.structural_elements
                )
                has_coords = any(
                    len(elem.coordinates) > 0 for elem in simplified.structural_elements
                )

                print(f"  Walls detected: {has_walls}")
                print(f"  Doors detected: {has_doors}")
                print(f"  Real coordinates: {has_coords}")

                if has_walls and has_doors and has_coords:
                    print("  ✅ Shows architectural understanding")
                else:
                    print("  ❌ Limited architectural understanding")
            else:
                print("  ❌ No structural elements found")

        except Exception as e:
            print(f"❌ Processing failed: {e}")
            import traceback

            traceback.print_exc()

    except Exception as e:
        print(f"❌ Setup failed: {e}")


if __name__ == "__main__":
    test_real_floor_plan_processing()
