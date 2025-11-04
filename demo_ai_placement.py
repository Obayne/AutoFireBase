"""
AI Professional Placement Demo - Simple Validation

Quick demonstration of AI device placement with professional CAD integration.
"""

# Basic imports
from cad_core.ai.device_placement import DeviceType
from cad_core.ai.professional_placement import create_professional_ai_engine
from cad_core.geometry import Point
from cad_core.spaces import ModelSpace
from cad_core.spaces.model_space import Line
from cad_core.units import Units, UnitSystem


def demo_ai_placement():
    """Demonstrate AI device placement."""
    print("🤖 AutoFire AI Device Placement Demo")
    print("=" * 40)

    # Create professional model space
    print("Creating professional model space...")
    model = ModelSpace(UnitSystem(Units.FEET))

    # Add simple office building (60' x 40')
    print("Adding building geometry...")
    walls = [
        Line(Point(0, 0), Point(60, 0)),  # South wall
        Line(Point(60, 0), Point(60, 40)),  # East wall
        Line(Point(60, 40), Point(0, 40)),  # North wall
        Line(Point(0, 40), Point(0, 0)),  # West wall
    ]

    for wall in walls:
        model.add_entity(wall, "WALLS")

    print(f"Building area: {60 * 40:,} sq ft")

    # Create AI placement engine
    print("Initializing AI placement engine...")
    ai_engine = create_professional_ai_engine(model)

    # Place smoke detectors with AI
    print("AI placing smoke detectors...")
    smoke_result = ai_engine.place_devices_ai_optimized(
        device_type=DeviceType.SMOKE_DETECTOR, target_coverage=0.95
    )

    print("Results:")
    print(f"  Devices placed: {smoke_result.total_devices}")
    print(f"  Coverage: {smoke_result.coverage_percentage:.1f}%")
    print(f"  Compliance score: {smoke_result.compliance_score:.1f}%")
    print(f"  Estimated cost: ${smoke_result.cost_estimate:,.0f}")
    print(f"  Placement time: {smoke_result.placement_time_seconds:.3f}s")

    if smoke_result.recommendations:
        print("  Recommendations:")
        for rec in smoke_result.recommendations:
            print(f"    - {rec}")

    # Validate devices in model space
    detectors = model.get_entities_on_layer("FA-DETECTORS")
    print(f"  Devices in model space: {len(detectors)}")

    # Show device details
    print("Device details:")
    for i, device in enumerate(smoke_result.devices_placed[:3]):  # Show first 3
        print(
            f"  Device {i+1}: {device.properties['model']} at "
            f"({device.center.x:.1f}, {device.center.y:.1f}) "
            f"- Confidence: {device.properties['confidence_score']:.2f}"
        )

    # Place pull stations
    print("\nAI placing manual pull stations...")
    pull_result = ai_engine.place_devices_ai_optimized(
        device_type=DeviceType.PULL_STATION, target_coverage=1.0
    )

    print(
        f"Pull stations: {pull_result.total_devices} devices, "
        f"{pull_result.coverage_percentage:.1f}% coverage"
    )

    # Get overall statistics
    stats = ai_engine.get_placement_statistics()
    print("\nOverall Statistics:")
    print(f"  Total sessions: {stats['total_sessions']}")
    print(f"  Total devices: {stats['total_devices_placed']}")
    print(f"  Average coverage: {stats['average_coverage_percentage']:.1f}%")
    print(f"  Total cost: ${stats['total_estimated_cost']:,.0f}")

    print("\n✅ AI Device Placement Demo Complete!")
    return True


if __name__ == "__main__":
    try:
        demo_ai_placement()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
