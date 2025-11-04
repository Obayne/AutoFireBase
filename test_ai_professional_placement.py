"""
Test AI Device Placement with Professional Model/Paper Space

Comprehensive validation of AI-powered device placement integrated with
professional CAD architecture for real-world fire alarm design.
"""

import math
import os
import sys
import time

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from cad_core.ai.device_placement import DeviceType, SpaceType
from cad_core.ai.professional_placement import (
    FireAlarmEntity,
    create_professional_ai_engine,
)
from cad_core.geometry import Point
from cad_core.spaces import ModelSpace, PageSize, PaperSpace
from cad_core.spaces.model_space import Line
from cad_core.units import Units, UnitSystem


def test_ai_placement_integration():
    """Test AI placement engine integration with model space."""
    print("Testing AI Placement Integration...")

    # Create professional model space
    model = ModelSpace(UnitSystem(Units.FEET))

    # Add building outline (office building 100' x 60')
    walls = [
        Line(Point(0, 0), Point(100, 0)),  # South wall
        Line(Point(100, 0), Point(100, 60)),  # East wall
        Line(Point(100, 60), Point(0, 60)),  # North wall
        Line(Point(0, 60), Point(0, 0)),  # West wall
    ]

    for wall in walls:
        model.add_entity(wall, "WALLS")

    # Create AI placement engine
    ai_engine = create_professional_ai_engine(model)

    # Test building analysis
    building_bounds = model.get_bounds()
    assert building_bounds is not None

    room = ai_engine.analyze_building_layout(building_bounds)
    assert room.space_type == SpaceType.OFFICE
    assert abs(room.area_sqft - 6000.0) < 1.0  # 100 x 60 = 6000 sq ft

    print("✓ AI placement integration validated")


def test_smoke_detector_placement():
    """Test AI smoke detector placement with professional coordinates."""
    print("Testing AI Smoke Detector Placement...")

    # Create model space and building
    model = ModelSpace(UnitSystem(Units.FEET))

    # Office building 80' x 50'
    walls = [
        Line(Point(0, 0), Point(80, 0)),
        Line(Point(80, 0), Point(80, 50)),
        Line(Point(80, 50), Point(0, 50)),
        Line(Point(0, 50), Point(0, 0)),
    ]

    for wall in walls:
        model.add_entity(wall, "BUILDING-WALLS")

    # Add interior corridor
    corridor = Line(Point(0, 25), Point(80, 25))
    model.add_entity(corridor, "INTERIOR-WALLS")

    # Create AI engine and place smoke detectors
    ai_engine = create_professional_ai_engine(model)

    result = ai_engine.place_devices_ai_optimized(
        device_type=DeviceType.SMOKE_DETECTOR, target_coverage=0.95
    )

    # Validate results
    assert result.total_devices > 0, "No devices were placed"
    assert result.coverage_percentage >= 90.0, f"Coverage too low: {result.coverage_percentage}%"
    assert result.compliance_score >= 70.0, f"Compliance too low: {result.compliance_score}%"

    # Check devices were added to model space
    smoke_detectors = model.get_entities_on_layer("FA-DETECTORS")
    assert len(smoke_detectors) == result.total_devices

    # Validate device properties
    for device in result.devices_placed:
        assert isinstance(device, FireAlarmEntity)
        assert device.device_type == DeviceType.SMOKE_DETECTOR
        assert "confidence_score" in device.properties
        assert "coverage_area" in device.properties
        assert device.properties["model"] == "FSP-851"

    # Check NFPA spacing compliance
    building_area = 80 * 50  # 4000 sq ft
    expected_devices = math.ceil(building_area / 900)  # 30' x 30' coverage
    assert result.total_devices >= expected_devices * 0.8  # Allow some optimization

    print(
        f"✓ AI placed {result.total_devices} smoke detectors with {result.coverage_percentage:.1f}% coverage"
    )


def test_multi_device_type_placement():
    """Test placement of multiple device types with AI coordination."""
    print("Testing Multi-Device Type AI Placement...")

    # Create large office complex
    model = ModelSpace(UnitSystem(Units.FEET))

    # L-shaped building
    main_building = [
        Line(Point(0, 0), Point(120, 0)),  # South wall
        Line(Point(120, 0), Point(120, 80)),  # East wall
        Line(Point(120, 80), Point(60, 80)),  # North wall (partial)
        Line(Point(60, 80), Point(60, 40)),  # Interior wall
        Line(Point(60, 40), Point(0, 40)),  # North wall (main)
        Line(Point(0, 40), Point(0, 0)),  # West wall
    ]

    for wall in main_building:
        model.add_entity(wall, "BUILDING")

    ai_engine = create_professional_ai_engine(model)

    # Place smoke detectors first
    smoke_result = ai_engine.place_devices_ai_optimized(
        device_type=DeviceType.SMOKE_DETECTOR, target_coverage=0.95
    )

    # Place manual pull stations
    pull_result = ai_engine.place_devices_ai_optimized(
        device_type=DeviceType.PULL_STATION,
        target_coverage=1.0,  # Full coverage required
    )

    # Place notification appliances
    notification_result = ai_engine.place_devices_ai_optimized(
        device_type=DeviceType.HORN_STROBE, target_coverage=0.90
    )

    # Validate coordination between device types
    total_devices = (
        smoke_result.total_devices + pull_result.total_devices + notification_result.total_devices
    )

    assert total_devices > 10, "Not enough devices placed for large building"

    # Check layer organization
    detectors = model.get_entities_on_layer("FA-DETECTORS")
    pulls = model.get_entities_on_layer("FA-PULL-STATIONS")
    notification = model.get_entities_on_layer("FA-NOTIFICATION")

    assert len(detectors) == smoke_result.total_devices
    assert len(pulls) == pull_result.total_devices
    assert len(notification) == notification_result.total_devices

    # Validate no device conflicts (devices too close)
    all_devices = detectors + pulls + notification
    for i, device1 in enumerate(all_devices):
        for device2 in all_devices[i + 1 :]:
            if hasattr(device1, "center") and hasattr(device2, "center"):
                distance = device1.center.distance_to(device2.center)
                assert distance > 1.0, f"Devices too close: {distance:.2f}'"

    print(
        f"✓ AI placed {smoke_result.total_devices} detectors, "
        f"{pull_result.total_devices} pull stations, "
        f"{notification_result.total_devices} notification devices"
    )


def test_ai_paper_space_integration():
    """Test AI placement with paper space construction documents."""
    print("Testing AI + Paper Space Integration...")

    # Create model space with building
    model = ModelSpace(UnitSystem(Units.FEET))

    # Modern office building 150' x 100'
    building = [
        Line(Point(0, 0), Point(150, 0)),
        Line(Point(150, 0), Point(150, 100)),
        Line(Point(150, 100), Point(0, 100)),
        Line(Point(0, 100), Point(0, 0)),
    ]

    for wall in building:
        model.add_entity(wall, "ARCHITECTURE")

    # Add some interior elements
    corridor1 = Line(Point(0, 30), Point(150, 30))  # Main corridor
    corridor2 = Line(Point(75, 0), Point(75, 100))  # Cross corridor
    model.add_entity(corridor1, "ARCHITECTURE")
    model.add_entity(corridor2, "ARCHITECTURE")

    # Create AI engine and place comprehensive system
    ai_engine = create_professional_ai_engine(model)

    # Place all device types
    smoke_result = ai_engine.place_devices_ai_optimized(DeviceType.SMOKE_DETECTOR)
    pull_result = ai_engine.place_devices_ai_optimized(DeviceType.PULL_STATION)
    horn_result = ai_engine.place_devices_ai_optimized(DeviceType.HORN_STROBE)

    # Create paper space layout
    paper = PaperSpace("AI Fire Alarm Plan", PageSize.ANSI_D)

    # Generate AI-enhanced construction documents
    enhanced_paper, ai_stats = ai_engine.create_ai_enhanced_layout(paper)

    # Validate paper space integration
    assert len(enhanced_paper.viewports) > 0, "No viewports created"
    viewport = enhanced_paper.viewports[0]

    # Test that AI-placed devices are visible in viewport
    building_center = Point(75, 50)  # Center of building
    paper_center = viewport.model_to_paper(building_center)
    assert viewport.is_point_in_viewport(paper_center), "Building not visible in viewport"

    # Check AI statistics
    assert ai_stats["ai_device_placement"] == True
    assert ai_stats["total_devices"] > 0
    assert "smoke_detector" in ai_stats["device_breakdown"]
    assert ai_stats["estimated_cost"] > 0

    # Validate device coordinates in viewport
    for entity in model.entities.values():
        if isinstance(entity, FireAlarmEntity):
            model_pos = entity.center
            paper_pos = viewport.model_to_paper(model_pos)

            # Should be within viewport bounds
            assert viewport.is_point_in_viewport(
                paper_pos
            ), f"Device at {model_pos} not visible in viewport"

    total_devices = (
        smoke_result.total_devices + pull_result.total_devices + horn_result.total_devices
    )

    print(f"✓ AI-enhanced layout created with {total_devices} devices")
    print(f"  Estimated cost: ${ai_stats['estimated_cost']:,.0f}")
    print(f"  Building area: {150*100:,} sq ft")


def test_nfpa_compliance_validation():
    """Test NFPA compliance validation with AI placement."""
    print("Testing NFPA Compliance Validation...")

    # Create model space
    model = ModelSpace(UnitSystem(Units.FEET))

    # Small office 40' x 30' (should need 2 smoke detectors minimum)
    office = [
        Line(Point(0, 0), Point(40, 0)),
        Line(Point(40, 0), Point(40, 30)),
        Line(Point(40, 30), Point(0, 30)),
        Line(Point(0, 30), Point(0, 0)),
    ]

    for wall in office:
        model.add_entity(wall, "WALLS")

    ai_engine = create_professional_ai_engine(model)

    # Test insufficient coverage (force low target)
    result_low = ai_engine.place_devices_ai_optimized(
        device_type=DeviceType.SMOKE_DETECTOR,
        target_coverage=0.5,  # Intentionally low
    )

    # Should generate recommendations for more devices
    assert len(result_low.recommendations) > 0, "No recommendations generated"
    assert any("more devices" in rec.lower() for rec in result_low.recommendations)

    # Test proper coverage
    result_proper = ai_engine.place_devices_ai_optimized(
        device_type=DeviceType.SMOKE_DETECTOR, target_coverage=0.95
    )

    # Should have good coverage and compliance
    assert result_proper.coverage_percentage >= 90.0
    assert result_proper.compliance_score >= 80.0

    # Validate NFPA spacing (30' maximum for smoke detectors)
    area = 40 * 30  # 1200 sq ft
    max_coverage_per_device = 900  # 30' x 30'
    min_devices = math.ceil(area / max_coverage_per_device)

    assert (
        result_proper.total_devices >= min_devices
    ), f"Need at least {min_devices} devices, got {result_proper.total_devices}"

    # Check device spacing
    devices = result_proper.devices_placed
    if len(devices) > 1:
        for i, device1 in enumerate(devices):
            for device2 in devices[i + 1 :]:
                distance = device1.center.distance_to(device2.center)
                assert distance <= 30.0, f"Devices too far apart: {distance:.1f}' (max 30')"
                assert distance >= 5.0, f"Devices too close: {distance:.1f}' (min 5')"

    print(
        f"✓ NFPA compliance validated - {result_proper.total_devices} devices, "
        f"{result_proper.coverage_percentage:.1f}% coverage"
    )


def test_performance_and_statistics():
    """Test AI placement performance and statistics tracking."""
    print("Testing AI Performance & Statistics...")

    # Create model space
    model = ModelSpace(UnitSystem(Units.FEET))

    # Large building for performance test
    building = [
        Line(Point(0, 0), Point(200, 0)),
        Line(Point(200, 0), Point(200, 150)),
        Line(Point(200, 150), Point(0, 150)),
        Line(Point(0, 150), Point(0, 0)),
    ]

    for wall in building:
        model.add_entity(wall, "BUILDING")

    ai_engine = create_professional_ai_engine(model)

    # Time multiple placement operations
    start_time = time.time()

    # Place devices with timing
    smoke_result = ai_engine.place_devices_ai_optimized(DeviceType.SMOKE_DETECTOR)
    pull_result = ai_engine.place_devices_ai_optimized(DeviceType.PULL_STATION)

    total_time = time.time() - start_time

    # Should be reasonably fast (under 5 seconds for large building)
    assert total_time < 5.0, f"AI placement too slow: {total_time:.2f}s"

    # Check statistics tracking
    stats = ai_engine.get_placement_statistics()

    assert stats["total_sessions"] == 2  # Two placement operations
    assert stats["total_devices_placed"] > 0
    assert "smoke_detector" in stats["device_type_breakdown"]
    assert "pull_station" in stats["device_type_breakdown"]
    assert stats["average_coverage_percentage"] > 0
    assert stats["total_estimated_cost"] > 0

    # Validate coordinate precision
    building_area = 200 * 150  # 30,000 sq ft
    expected_smoke_devices = building_area / 900  # Rough estimate

    actual_smoke = stats["device_type_breakdown"]["smoke_detector"]
    assert (
        abs(actual_smoke - expected_smoke_devices) < expected_smoke_devices * 0.5
    ), "Device count significantly different from NFPA estimates"

    print(
        f"✓ Performance validated - {total_time:.2f}s for {stats['total_devices_placed']} devices"
    )
    print(f"  Large building: {building_area:,} sq ft")
    print(f"  Average coverage: {stats['average_coverage_percentage']:.1f}%")


def run_all_tests():
    """Run all AI device placement tests."""
    print("🤖 Testing AI Device Placement with Professional CAD")
    print("=" * 65)

    try:
        test_ai_placement_integration()
        test_smoke_detector_placement()
        test_multi_device_type_placement()
        test_ai_paper_space_integration()
        test_nfpa_compliance_validation()
        test_performance_and_statistics()

        print("\n" + "=" * 65)
        print("🎉 ALL AI TESTS PASSED - Professional AI Placement System!")
        print("\n✅ AI + Professional CAD Integration:")
        print("   - AI device placement with real-world coordinates")
        print("   - NFPA 72 compliance validation and optimization")
        print("   - Multi-device type coordination and spacing")
        print("   - Professional model/paper space integration")
        print("   - Construction document generation with AI statistics")
        print("   - Performance optimized for large buildings")
        print("\n🤖 AI Features Validated:")
        print("   - Intelligent device positioning based on room analysis")
        print("   - Coverage optimization with budget constraints")
        print("   - NFPA compliance checking and recommendations")
        print("   - Professional entity creation with metadata")
        print("   - Real-time statistics and session tracking")
        print("\n🎯 Ready for professional AI-powered fire alarm design!")

    except Exception as e:
        print(f"\n❌ AI TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
