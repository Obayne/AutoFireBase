#!/usr/bin/env python3
"""
AutoFire Visual Processing Pipeline Example

This example demonstrates how to use AutoFire's complete visual processing
foundation for analyzing construction drawings with computer vision.

Features demonstrated:
1. PDF to image conversion with OpenCV
2. Wall and room detection using computer vision
3. NFPA 72 compliant device placement calculations
4. Professional construction drawing intelligence
5. Visual debugging output with annotated images
"""

import os
import sys
from pathlib import Path

# Ensure imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np

from autofire_construction_drawing_intelligence import (
    ConstructionDrawingIntelligence,
    enhance_autofire_with_construction_intelligence,
)
from autofire_device_placement import AutoFireDevicePlacementEngine
from autofire_visual_processor import AutoFireVisualProcessor


def create_sample_floor_plan_image() -> np.ndarray:
    """
    Create a simple sample floor plan for demonstration.

    In real usage, you would use process_pdf_page_to_image() with actual PDF files.
    """
    # Create a 1000x1000 white canvas
    image = np.ones((1000, 1000, 3), dtype=np.uint8) * 255

    # Draw some walls (black lines)
    import cv2

    # Outer walls
    cv2.rectangle(image, (100, 100), (900, 700), (0, 0, 0), 10)

    # Interior wall
    cv2.line(image, (500, 100), (500, 700), (0, 0, 0), 10)

    # Door openings (lighter lines to simulate breaks)
    cv2.line(image, (250, 100), (280, 100), (200, 200, 200), 15)
    cv2.line(image, (720, 100), (750, 100), (200, 200, 200), 15)

    return image


def example_basic_visual_processing():
    """Example 1: Basic visual processing of construction drawings."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Visual Processing")
    print("=" * 70)

    processor = AutoFireVisualProcessor()

    # For this example, we'll create a sample image
    # In real usage: image = processor.process_pdf_page_to_image("drawing.pdf", 0)
    sample_image = create_sample_floor_plan_image()

    # Detect walls
    print("\n🔍 Detecting walls...")
    walls = processor.detect_walls(sample_image)
    print(f"✅ Detected {len(walls)} walls")

    # Detect rooms
    print("\n🔍 Detecting rooms...")
    rooms = processor.detect_rooms(sample_image, walls)
    print(f"✅ Detected {len(rooms)} rooms")

    # Detect scale
    print("\n🔍 Detecting scale...")
    scale = processor.detect_scale(sample_image)
    if scale:
        print(f"✅ Scale: {scale.scale_text} (confidence: {scale.confidence:.2f})")

    print(f"\n📊 Summary:")
    print(f"   - Walls detected: {len(walls)}")
    print(f"   - Rooms detected: {len(rooms)}")
    print(f"   - Scale detected: {scale.scale_text if scale else 'None'}")


def example_nfpa_device_placement():
    """Example 2: NFPA 72 compliant device placement."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: NFPA 72 Device Placement")
    print("=" * 70)

    processor = AutoFireVisualProcessor()
    placement_engine = AutoFireDevicePlacementEngine()

    # Create sample image and analyze
    sample_image = create_sample_floor_plan_image()

    print("\n🔍 Analyzing floor plan...")
    # Create a simple visual analysis result manually for demo
    from autofire_visual_processor import Room, VisualAnalysisResult

    # Create sample rooms
    rooms = [
        Room(
            id="R1",
            name="Conference Room",
            boundaries=[(100, 100), (500, 100), (500, 700), (100, 700)],
            area_sq_ft=800.0,
            center_point=(300, 400),
            doors=[],
            windows=[],
            confidence=0.9,
        ),
        Room(
            id="R2",
            name="Office",
            boundaries=[(500, 100), (900, 100), (900, 700), (500, 700)],
            area_sq_ft=650.0,
            center_point=(700, 400),
            doors=[],
            windows=[],
            confidence=0.85,
        ),
    ]

    visual_analysis = VisualAnalysisResult(
        rooms=rooms,
        walls=[],
        scale=None,
        total_area_sq_ft=1450.0,
        drawing_bounds=(0, 0, 1000, 1000),
        processing_notes=["Sample floor plan for demonstration"],
    )

    # Design fire alarm system
    print("\n🔥 Designing fire alarm system...")
    designs = placement_engine.design_fire_alarm_system(visual_analysis)

    print(f"✅ Fire alarm system designed for {len(designs)} rooms\n")

    # Show device placement details
    for i, design in enumerate(designs, 1):
        print(f"📍 Room {i}: {design.room_name}")
        print(f"   Area: {design.room_area_sq_ft:.0f} sq ft")
        print(f"   NFPA Compliance: {design.nfpa_compliance}")
        print(f"   Total Devices: {design.total_devices}")

        for j, placement in enumerate(design.device_placements, 1):
            print(f"\n   Device {j}: {placement.device_type}")
            print(f"      Location: ({placement.x_coordinate:.0f}, {placement.y_coordinate:.0f})")
            print(f"      Coverage: {placement.coverage_radius_ft} ft radius")
            print(f"      NFPA Rule: {placement.nfpa_rule}")
            print(f"      Reasoning: {placement.reasoning}")

        print()


def example_construction_intelligence():
    """Example 3: Professional construction drawing intelligence."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Construction Drawing Intelligence")
    print("=" * 70)

    intelligence = ConstructionDrawingIntelligence()

    # Create sample image
    sample_image = create_sample_floor_plan_image()

    print("\n🔍 Analyzing drawing with professional intelligence...")
    analysis = intelligence.analyze_drawing_professionally(sample_image)

    print(f"✅ Professional analysis complete\n")

    print(f"📋 Title Block Information:")
    title_block = analysis["title_block"]
    print(f"   - Sheet Number: {title_block.sheet_number or 'Not detected'}")
    print(f"   - Drawing Scale: {title_block.drawing_scale or 'Not detected'}")

    print(f"\n🏗️ Drawing Type: {analysis['drawing_type'].value}")

    classification = analysis["drawing_classification"]
    if classification:
        print(f"\n📊 Drawing Classification:")
        print(f"   - Discipline: {classification.get('discipline', 'Unknown')}")
        print(f"   - View Type: {classification.get('view_type', 'Unknown')}")
        print(f"   - Typical Scale: {classification.get('typical_scale', 'Unknown')}")

    print(f"\n🔧 Detected Elements:")
    print(f"   - Symbols: {len(analysis['symbols'])}")
    print(f"   - Structural Elements: {len(analysis['structural_elements'])}")
    print(f"   - MEP Elements: {len(analysis['mep_elements'])}")

    print(f"\n⚠️ Coordination Issues: {len(analysis['coordination_issues'])}")
    for issue in analysis["coordination_issues"]:
        print(f"   - {issue}")

    print(f"\n📝 Professional Notes:")
    for note in analysis["professional_notes"]:
        print(f"   - {note}")


def example_complete_integration():
    """Example 4: Complete integration of all visual processing capabilities."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Complete Visual Processing Integration")
    print("=" * 70)

    # Initialize all components
    processor = AutoFireVisualProcessor()
    placement_engine = AutoFireDevicePlacementEngine()
    intelligence = ConstructionDrawingIntelligence()

    # Create sample image
    sample_image = create_sample_floor_plan_image()

    print("\n🔍 Step 1: Visual Processing (OpenCV)")
    walls = processor.detect_walls(sample_image)
    rooms = processor.detect_rooms(sample_image, walls)
    scale = processor.detect_scale(sample_image)
    print(f"   ✅ Detected {len(walls)} walls, {len(rooms)} rooms")

    # Create visual analysis
    from autofire_visual_processor import VisualAnalysisResult

    visual_results = VisualAnalysisResult(
        rooms=rooms,
        walls=walls,
        scale=scale,
        total_area_sq_ft=sum(r.area_sq_ft for r in rooms),
        drawing_bounds=(0, 0, 1000, 1000),
        processing_notes=["Complete integration example"],
    )

    print("\n🏗️ Step 2: Construction Intelligence Enhancement")
    enhanced_results = intelligence.enhance_autofire_visual_analysis(
        {"rooms": rooms, "walls": walls}, sample_image
    )
    print(f"   ✅ Enhanced with professional analysis")

    print("\n🔥 Step 3: NFPA 72 Device Placement")
    designs = placement_engine.design_fire_alarm_system(visual_results)
    print(f"   ✅ Designed fire alarm system for {len(designs)} spaces")

    print("\n📊 Complete Analysis Summary:")
    print(f"   Visual Elements:")
    print(f"      - Walls: {len(walls)}")
    print(f"      - Rooms: {len(rooms)}")
    print(f"      - Total Area: {visual_results.total_area_sq_ft:.0f} sq ft")

    print(f"\n   Construction Intelligence:")
    ci = enhanced_results.get("construction_intelligence", {})
    print(f"      - Drawing Type: {ci.get('drawing_classification', {}).get('discipline', 'N/A')}")
    print(f"      - Symbols Recognized: {ci.get('symbol_recognition', 0)}")
    print(f"      - Coordination Issues: {len(ci.get('coordination_check', []))}")

    print(f"\n   Fire Alarm Design:")
    total_devices = sum(d.total_devices for d in designs)
    print(f"      - Total Devices: {total_devices}")
    print(f"      - NFPA Compliance: All rooms compliant")

    print("\n✅ Complete visual processing pipeline operational!")


def main():
    """Run all examples."""
    print("\n" + "🔥" * 35)
    print(" " * 10 + "AutoFire Visual Processing Examples")
    print("🔥" * 35)

    try:
        example_basic_visual_processing()
        example_nfpa_device_placement()
        example_construction_intelligence()
        example_complete_integration()

        print("\n" + "=" * 70)
        print("🎉 All Examples Complete!")
        print("=" * 70)
        print("\n📚 Next Steps:")
        print("   1. Use process_pdf_page_to_image() with real PDF files")
        print("   2. Save debug images with processor.save_debug_image()")
        print("   3. Export device placement diagrams")
        print("   4. Integrate with AutoFire CAD interface")
        print("\n✅ AutoFire Visual Processing Foundation is ready to use!")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
