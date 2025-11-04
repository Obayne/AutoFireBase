"""
Example: Using CAD Layer Intelligence in AutoFire
================================================

This example shows how to use the new CAD layer intelligence
capabilities to analyze construction drawings with exact precision.
"""

import sys
from pathlib import Path

# Add project root to path for examples
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cad_core.intelligence import (
    EZDXF_AVAILABLE,
    CADLayerIntelligence,
    enhance_autofire_with_layer_intelligence,
)


def example_basic_usage():
    """Basic usage of layer intelligence engine."""
    print("Example 1: Basic Layer Analysis")
    print("=" * 50)

    # Initialize the engine
    engine = CADLayerIntelligence()

    # Check if ezdxf is available
    if not engine.is_available():
        print("⚠️  ezdxf not installed")
        print("Install with: pip install ezdxf")
        return

    # Analyze a CAD file
    cad_file = "construction_plan.dxf"
    print(f"\nAnalyzing {cad_file}...")

    analysis = engine.analyze_cad_file_layers(cad_file)

    if "error" not in analysis:
        print(f"✅ Found {analysis['total_layers']} layers")
        print(f"✅ Found {analysis['fire_safety_layer_count']} fire safety layers")
        print(f"✅ Device summary: {analysis['device_summary']}")
    else:
        print(f"❌ Error: {analysis['error']}")


def example_device_extraction():
    """Extract fire safety devices from CAD layers."""
    print("\nExample 2: Fire Safety Device Extraction")
    print("=" * 50)

    engine = CADLayerIntelligence()

    if not engine.is_available():
        print("⚠️  ezdxf not installed")
        return

    cad_file = "fire_alarm_plan.dxf"
    print(f"\nExtracting devices from {cad_file}...")

    devices = engine.extract_precise_fire_devices(cad_file)

    print(f"✅ Found {len(devices)} fire safety devices")

    for device in devices:
        print(f"  - {device.device_type} at {device.coordinates}")
        print(f"    Layer: {device.layer_name}, Block: {device.block_name}")


def example_integration_with_visual_analysis():
    """Enhance visual analysis with layer intelligence."""
    print("\nExample 3: Hybrid Visual + Layer Analysis")
    print("=" * 50)

    # Simulated visual analysis results
    visual_results = {
        "method": "computer_vision",
        "devices": [
            {"type": "smoke_detector", "location": "approx", "confidence": 0.85},
            {"type": "smoke_detector", "location": "approx", "confidence": 0.73},
        ],
        "total_detected": 2,
    }

    print("\nVisual analysis detected: 2 devices")

    # Enhance with layer intelligence
    cad_file = "construction_plan.dxf"
    enhanced_results = enhance_autofire_with_layer_intelligence(cad_file, visual_results)

    print("\nEnhanced results:")
    print(f"  Original method: {enhanced_results['method']}")
    print(f"  Visual detection: {enhanced_results.get('device_count_comparison', {}).get('visual_detection', 'N/A')} devices")
    print(f"  Layer extraction: {enhanced_results.get('device_count_comparison', {}).get('layer_extraction', 'N/A')} devices")

    if "layer_intelligence" in enhanced_results:
        layer_info = enhanced_results["layer_intelligence"]
        if "error" not in layer_info:
            print(f"\n✅ Layer intelligence enhancement successful!")
        else:
            print(f"\n⚠️  {layer_info.get('note', 'Layer intelligence not available')}")


def example_validation():
    """Validate CAD file organization against standards."""
    print("\nExample 4: AIA Standards Validation")
    print("=" * 50)

    engine = CADLayerIntelligence()

    if not engine.is_available():
        print("⚠️  ezdxf not installed")
        return

    cad_file = "construction_plan.dxf"
    print(f"\nValidating {cad_file} against AIA standards...")

    validation = engine.validate_layer_organization(cad_file)

    if "error" not in validation:
        print("\n✅ Validation complete")

        # Show AIA compliance
        compliant_count = sum(
            1 for v in validation["aia_compliance"].values() if v.get("compliant", False)
        )
        total_layers = len(validation["aia_compliance"])
        print(f"  AIA Compliant layers: {compliant_count}/{total_layers}")

        # Show fire safety organization
        fire_org = validation["fire_safety_organization"]
        if fire_org.get("organized", False):
            print(f"  Fire safety layers found: {len(fire_org.get('found_layers', []))}")

        # Show recommendations
        print("\n  Recommendations:")
        for rec in validation.get("recommendations", []):
            print(f"    • {rec}")
    else:
        print(f"❌ Error: {validation['error']}")


def example_layer_classification():
    """Demonstrate layer classification capabilities."""
    print("\nExample 5: Layer Classification")
    print("=" * 50)

    engine = CADLayerIntelligence()

    test_layers = [
        "E-FIRE",
        "E-SPKR",
        "A-WALL",
        "A-DOOR",
        "M-HVAC",
        "S-BEAM",
        "NOTES",
    ]

    print("\nClassifying layers:")
    for layer_name in test_layers:
        classification = engine._classify_layer(layer_name)
        relevance = engine._assess_fire_safety_relevance(layer_name)
        print(f"  {layer_name:15} -> {classification.value:15} (relevance: {relevance})")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("CAD Layer Intelligence - Usage Examples")
    print("=" * 60)

    if not EZDXF_AVAILABLE:
        print("\n⚠️  Note: ezdxf library not installed")
        print("Some examples will show how to handle this gracefully.")
        print("Install with: pip install ezdxf\n")

    # Run examples
    example_basic_usage()
    example_device_extraction()
    example_integration_with_visual_analysis()
    example_validation()
    example_layer_classification()

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
