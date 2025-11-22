#!/usr/bin/env python3
"""
AutoFire CLI Geometry Operations Tool - Clean Version
====================================================

Command-line interface for CAD geometry operations.
Provides trim, extend, and intersect operations for fire protection system design.
"""

import argparse
import json
import logging

logger = logging.getLogger(__name__)


def geom_trim(segment: dict, cutter: dict, output_format: str = "json") -> str:
    """Trim segment by cutter geometry (simulation)"""
    try:
        # Simulate trim operation
        start_x = segment["start"]["x"] 
        start_y = segment["start"]["y"]
        end_x = (segment["end"]["x"] + cutter["start"]["x"]) / 2  # Simulate trim point
        end_y = (segment["end"]["y"] + cutter["start"]["y"]) / 2

        if output_format == "json":
            return json.dumps({
                "operation": "trim",
                "success": True,
                "result": {
                    "start": {"x": start_x, "y": start_y},
                    "end": {"x": end_x, "y": end_y}
                }
            }, indent=2)
        else:
            return f"Trimmed segment: ({start_x:.2f}, {start_y:.2f}) to ({end_x:.2f}, {end_y:.2f})"

    except Exception as e:
        error_result = {"operation": "trim", "success": False, "error": str(e)}
        return json.dumps(error_result, indent=2) if output_format == "json" else f"Error: {e}"


def geom_extend(segment: dict, target: dict, output_format: str = "json") -> str:
    """Extend segment to target geometry (simulation)"""
    try:
        # Simulate extend operation
        start_x = segment["start"]["x"]
        start_y = segment["start"]["y"]
        # Extend toward target
        end_x = target["end"]["x"] 
        end_y = target["end"]["y"]

        if output_format == "json":
            return json.dumps({
                "operation": "extend",
                "success": True,
                "result": {
                    "start": {"x": start_x, "y": start_y},
                    "end": {"x": end_x, "y": end_y}
                }
            }, indent=2)
        else:
            return f"Extended segment: ({start_x:.2f}, {start_y:.2f}) to ({end_x:.2f}, {end_y:.2f})"

    except Exception as e:
        error_result = {"operation": "extend", "success": False, "error": str(e)}
        return json.dumps(error_result, indent=2) if output_format == "json" else f"Error: {e}"


def geom_intersect(segment1: dict, segment2: dict, output_format: str = "json") -> str:
    """Find intersection of two segments (simulation)"""
    try:
        # Simulate intersection calculation
        x1_avg = (segment1["start"]["x"] + segment1["end"]["x"]) / 2
        y1_avg = (segment1["start"]["y"] + segment1["end"]["y"]) / 2
        x2_avg = (segment2["start"]["x"] + segment2["end"]["x"]) / 2
        y2_avg = (segment2["start"]["y"] + segment2["end"]["y"]) / 2
        
        # Simulate intersection point
        intersection_x = (x1_avg + x2_avg) / 2
        intersection_y = (y1_avg + y2_avg) / 2

        if output_format == "json":
            return json.dumps({
                "operation": "intersect",
                "success": True,
                "intersections": [
                    {"x": intersection_x, "y": intersection_y}
                ]
            }, indent=2)
        else:
            return f"Intersection point: ({intersection_x:.2f}, {intersection_y:.2f})"

    except Exception as e:
        error_result = {"operation": "intersect", "success": False, "error": str(e)}
        return json.dumps(error_result, indent=2) if output_format == "json" else f"Error: {e}"


def main():
    parser = argparse.ArgumentParser(description="AutoFire CLI Geometry Operations")
    subparsers = parser.add_subparsers(dest="operation", help="Geometry operations")

    # Trim command
    trim_parser = subparsers.add_parser("trim", help="Trim segment by cutter")
    trim_parser.add_argument("--segment", required=True, help="Segment as JSON")
    trim_parser.add_argument("--cutter", required=True, help="Cutter as JSON")
    trim_parser.add_argument("--format", choices=["json", "text"], default="json")

    # Extend command
    extend_parser = subparsers.add_parser("extend", help="Extend segment to target")
    extend_parser.add_argument("--segment", required=True, help="Segment as JSON")
    extend_parser.add_argument("--target", required=True, help="Target as JSON")
    extend_parser.add_argument("--format", choices=["json", "text"], default="json")

    # Intersect command
    intersect_parser = subparsers.add_parser("intersect", help="Find segment intersection")
    intersect_parser.add_argument("--segment1", required=True, help="First segment as JSON")
    intersect_parser.add_argument("--segment2", required=True, help="Second segment as JSON")
    intersect_parser.add_argument("--format", choices=["json", "text"], default="json")

    args = parser.parse_args()

    if not args.operation:
        parser.print_help()
        return

    try:
        if args.operation == "trim":
            segment = json.loads(args.segment)
            cutter = json.loads(args.cutter)
            result = geom_trim(segment, cutter, args.format)
        elif args.operation == "extend":
            segment = json.loads(args.segment)
            target = json.loads(args.target)
            result = geom_extend(segment, target, args.format)
        elif args.operation == "intersect":
            segment1 = json.loads(args.segment1)
            segment2 = json.loads(args.segment2)
            result = geom_intersect(segment1, segment2, args.format)
        else:
            print(f"Unknown operation: {args.operation}")
            return

        print(result)

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
    except Exception as e:
        print(f"Operation failed: {e}")


if __name__ == "__main__":
    main()