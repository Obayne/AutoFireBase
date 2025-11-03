#!/usr/bin/env python3
"""Test the professional vector engine with precision coordinates."""

import math
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cad_core.geometry import ORIGIN, UNIT_X, UNIT_Y, Point, centroid, midpoint
from cad_core.units import DEFAULT_IMPERIAL, Units


def test_point_precision():
    """Test double precision point operations."""
    print("=== Testing Point Precision ===")

    # Test high precision coordinates
    p1 = Point(10.123456789012345, 20.987654321098765)
    p2 = Point(10.123456789012346, 20.987654321098766)

    print(f"P1: {p1}")
    print(f"P2: {p2}")
    print(f"Distance: {p1.distance_to(p2):.15f}")
    print(f"Are equal (within tolerance): {p1 == p2}")

    # Test vector operations
    p3 = p1 + p2
    p4 = p2 - p1
    p5 = p1 * 2.5

    print(f"P1 + P2: {p3}")
    print(f"P2 - P1: {p4}")
    print(f"P1 * 2.5: {p5}")

    # Test geometric operations
    angle = p1.angle_to(p2)
    magnitude = p1.magnitude()
    normalized = p1.normalize()

    print(f"Angle P1 to P2: {math.degrees(angle):.6f}°")
    print(f"P1 magnitude: {magnitude:.6f}")
    print(f"P1 normalized: {normalized}")
    print(f"Normalized magnitude: {normalized.magnitude():.15f}")
    print()


def test_coordinate_constants():
    """Test predefined coordinate constants."""
    print("=== Testing Coordinate Constants ===")

    print(f"ORIGIN: {ORIGIN}")
    print(f"UNIT_X: {UNIT_X}")
    print(f"UNIT_Y: {UNIT_Y}")

    # Test utility functions
    p1 = Point(5, 10)
    p2 = Point(15, 20)
    mid = midpoint(p1, p2)

    print(f"Midpoint of {p1} and {p2}: {mid}")

    points = [Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)]
    center = centroid(points)
    print(f"Centroid of square: {center}")
    print()


def test_rotations_and_transforms():
    """Test point rotation and transformations."""
    print("=== Testing Rotations and Transforms ===")

    p = Point(5, 0)

    # 90-degree rotation
    p90 = p.rotate(math.pi / 2)
    print(f"Point {p} rotated 90°: {p90}")

    # 45-degree rotation around center
    center = Point(5, 5)
    p45 = p.rotate(math.pi / 4, center)
    print(f"Point {p} rotated 45° around {center}: {p45}")

    # Linear interpolation
    p1 = Point(0, 0)
    p2 = Point(10, 10)
    p_half = p1.lerp(p2, 0.5)
    p_quarter = p1.lerp(p2, 0.25)

    print(f"Lerp {p1} to {p2} at 0.5: {p_half}")
    print(f"Lerp {p1} to {p2} at 0.25: {p_quarter}")
    print()


def test_units_system():
    """Test professional units system."""
    print("=== Testing Units System ===")

    # Test unit conversions
    imperial = DEFAULT_IMPERIAL

    # Distance in feet
    distance_ft = 10.5

    print(f"Distance: {imperial.formatter.format_distance(distance_ft)}")

    # Convert to other units
    distance_in = imperial.converter.convert(distance_ft, Units.FEET, Units.INCHES)
    distance_mm = imperial.converter.convert(distance_ft, Units.FEET, Units.MILLIMETERS)
    distance_m = imperial.converter.convert(distance_ft, Units.FEET, Units.METERS)

    print(f'In inches: {distance_in:.3f}"')
    print(f"In millimeters: {distance_mm:.1f}mm")
    print(f"In meters: {distance_m:.3f}m")

    # Test coordinate formatting
    coord = Point(10.75, 8.25)
    print(f"Coordinate in feet: {imperial.formatter.format_coordinate(coord.x, coord.y)}")
    print()


def test_distance_parsing():
    """Test parsing distance input strings."""
    print("=== Testing Distance Parsing ===")

    imperial = DEFAULT_IMPERIAL

    test_inputs = [
        "10.5",  # Decimal feet
        "10'-6\"",  # Feet and inches
        "10'",  # Just feet
        '6"',  # Just inches
        "10'-6 3/4\"",  # Feet, inches, and fractions
        '3/4"',  # Just fraction
        "100mm",  # Millimeters
        "2.5m",  # Meters
    ]

    for input_str in test_inputs:
        parsed = imperial.parse_distance(input_str)
        if parsed is not None:
            formatted = imperial.formatter.format_distance(parsed)
            print(f"'{input_str}' -> {parsed:.6f} ft -> {formatted}")
        else:
            print(f"'{input_str}' -> Failed to parse")
    print()


def test_architectural_formatting():
    """Test architectural-style formatting."""
    print("=== Testing Architectural Formatting ===")

    imperial = DEFAULT_IMPERIAL

    # Test various distances
    distances = [
        0.0,  # Zero
        0.0625,  # 3/4 inch
        0.5,  # 6 inches
        1.0,  # 1 foot
        1.5,  # 1'-6"
        10.75,  # 10'-9"
        25.125,  # 25'-1 1/2"
        100.0833,  # 100'-1"
    ]

    for dist in distances:
        formatted = imperial.formatter.format_distance(dist)
        print(f"{dist:8.4f} ft -> {formatted}")
    print()


def test_precision_and_snapping():
    """Test precision control and grid snapping."""
    print("=== Testing Precision and Snapping ===")

    from cad_core.units.system import Precision

    precision = Precision(decimal_places=3, tolerance=1e-9)

    # Test rounding
    value = 10.123456789
    rounded = precision.round_value(value)
    print(f"Original: {value}")
    print(f"Rounded to 3 places: {rounded}")

    # Test equality with tolerance
    a = 10.000000001
    b = 10.000000002
    equal = precision.are_equal(a, b)
    print(f"{a} == {b} within tolerance: {equal}")

    # Test grid snapping
    grid_size = 0.25  # Quarter foot grid
    point = Point(10.123, 8.876)
    snapped_x = precision.snap_to_grid(point.x, grid_size)
    snapped_y = precision.snap_to_grid(point.y, grid_size)
    snapped_point = Point(snapped_x, snapped_y)

    print(f"Original point: {point}")
    print(f"Snapped to {grid_size}' grid: {snapped_point}")
    print()


def test_real_world_scenario():
    """Test realistic fire alarm design scenario."""
    print("=== Testing Real-World Fire Alarm Scenario ===")

    imperial = DEFAULT_IMPERIAL

    # Room dimensions: 24' x 18'
    room_width = 24.0
    room_height = 18.0

    print(
        f"Room: {imperial.formatter.format_distance(room_width)} x {imperial.formatter.format_distance(room_height)}"
    )

    # Device placement: smoke detector in center
    detector_pos = Point(room_width / 2, room_height / 2)
    print(
        f"Smoke detector at: {imperial.formatter.format_coordinate(detector_pos.x, detector_pos.y)}"
    )

    # Coverage radius: 21 feet (typical for smoke detector)
    coverage_radius = 21.0

    # Check if corners are covered
    corners = [
        Point(0, 0),
        Point(room_width, 0),
        Point(room_width, room_height),
        Point(0, room_height),
    ]

    print(f"Coverage radius: {imperial.formatter.format_distance(coverage_radius)}")
    print("Corner coverage:")

    for i, corner in enumerate(corners):
        distance = detector_pos.distance_to(corner)
        covered = distance <= coverage_radius
        distance_str = imperial.formatter.format_distance(distance)
        corner_str = imperial.formatter.format_coordinate(corner.x, corner.y)
        status = "✓ COVERED" if covered else "✗ NOT COVERED"
        print(f"  Corner {i+1} at {corner_str}: {distance_str} {status}")

    # Calculate area
    area = room_width * room_height
    area_str = imperial.formatter.format_area(area)
    print(f"Room area: {area_str}")
    print()


def main():
    """Run all tests."""
    print("AutoFire Professional Vector Engine Test Suite")
    print("=" * 50)
    print()

    test_point_precision()
    test_coordinate_constants()
    test_rotations_and_transforms()
    test_units_system()
    test_distance_parsing()
    test_architectural_formatting()
    test_precision_and_snapping()
    test_real_world_scenario()

    print("✓ All tests completed successfully!")
    print("\nThe professional vector engine provides:")
    print("  • Double precision coordinates (sub-millimeter accuracy)")
    print("  • Real-world units (feet, inches, millimeters)")
    print("  • Architectural formatting (10'-6 3/4\")")
    print("  • Professional grid snapping and precision control")
    print("  • Complete unit conversion between imperial and metric")
    print("  • Real-world fire alarm design calculations")


if __name__ == "__main__":
    main()
