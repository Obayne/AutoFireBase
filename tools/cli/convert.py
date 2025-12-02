#!/usr/bin/env python3
"""
CLI tool for batch file format conversion.

Supports: DXF ↔ DWG ↔ AutoFire (.autofire JSON)

Usage:
    python tools/cli/convert.py dwg-to-dxf input.dwg
    python tools/cli/convert.py dxf-to-autofire input.dxf
    python tools/cli/convert.py batch Projects/*.dwg --to dxf
    python tools/cli/convert.py detect file.dwg
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.file_converter import (
    ConversionError,
    FileConverter,
    FileFormatError,
    detect_format,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout)
logger = logging.getLogger(__name__)


def cmd_dwg_to_dxf(args):
    """Convert DWG to DXF."""
    converter = FileConverter()
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.with_suffix(".dxf")

    try:
        result = converter.convert(input_path, output_path)
        print(f"✓ Converted: {result}")
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_dxf_to_dwg(args):
    """Convert DXF to DWG."""
    converter = FileConverter()
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.with_suffix(".dwg")

    try:
        result = converter.convert(input_path, output_path)
        print(f"✓ Converted: {result}")
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_dxf_to_autofire(args):
    """Convert DXF to AutoFire format."""
    converter = FileConverter()
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.with_suffix(".autofire")

    try:
        result = converter.convert(input_path, output_path)
        print(f"✓ Converted: {result}")
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_autofire_to_dxf(args):
    """Convert AutoFire to DXF."""
    converter = FileConverter()
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.with_suffix(".dxf")

    try:
        result = converter.convert(input_path, output_path)
        print(f"✓ Converted: {result}")
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_batch(args):
    """Batch convert multiple files."""
    converter = FileConverter()
    input_files = []

    # Expand wildcards
    for pattern in args.inputs:
        if "*" in pattern or "?" in pattern:
            # Glob pattern
            parts = Path(pattern).parts
            if "*" in parts[0] or "?" in parts[0]:
                # Relative pattern
                matches = list(Path.cwd().glob(pattern))
            else:
                # Absolute or has fixed prefix
                matches = list(Path(pattern).parent.glob(Path(pattern).name))
            input_files.extend(matches)
        else:
            # Direct path
            input_files.append(Path(pattern))

    if not input_files:
        print(f"✗ No files found matching: {args.inputs}", file=sys.stderr)
        sys.exit(1)

    print(f"Converting {len(input_files)} files to {args.to} format...")

    try:
        results = converter.batch_convert(input_files, args.to)
        print(f"\n✓ Successfully converted {len(results)} files:")
        for inp, out in results:
            print(f"  {inp.name} → {out.name}")

    except ConversionError as e:
        print(f"\n✗ Batch conversion failed:\n{e}", file=sys.stderr)
        sys.exit(1)


def cmd_detect(args):
    """Detect file format."""
    try:
        fmt = detect_format(args.file)
        print(f"{args.file}: {fmt}")
    except FileFormatError as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)


def cmd_info(args):
    """Show converter information."""
    converter = FileConverter()

    print("AutoFire File Converter")
    print("=" * 50)
    print(f"Supported input formats:  {', '.join(converter.SUPPORTED_FORMATS['input'])}")
    print(f"Supported output formats: {', '.join(converter.SUPPORTED_FORMATS['output'])}")
    print()

    if converter.has_dwg_support:
        print("✓ DWG support available via ODA File Converter")
        print(f"  Location: {converter.oda_path}")
    else:
        print("✗ DWG support unavailable (ODA File Converter not found)")
        print("  Download: https://www.opendesign.com/guestfiles/oda_file_converter")


def main():
    parser = argparse.ArgumentParser(
        description="AutoFire file format converter",
        epilog="Examples:\n"
        "  %(prog)s dwg-to-dxf drawing.dwg\n"
        "  %(prog)s dxf-to-autofire floorplan.dxf\n"
        "  %(prog)s batch Projects/*.dwg --to .dxf\n"
        "  %(prog)s detect file.dwg\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # dwg-to-dxf
    p = subparsers.add_parser("dwg-to-dxf", help="Convert DWG to DXF")
    p.add_argument("input", help="Input DWG file")
    p.add_argument("-o", "--output", help="Output DXF file (default: same name)")
    p.set_defaults(func=cmd_dwg_to_dxf)

    # dxf-to-dwg
    p = subparsers.add_parser("dxf-to-dwg", help="Convert DXF to DWG")
    p.add_argument("input", help="Input DXF file")
    p.add_argument("-o", "--output", help="Output DWG file (default: same name)")
    p.set_defaults(func=cmd_dxf_to_dwg)

    # dxf-to-autofire
    p = subparsers.add_parser("dxf-to-autofire", help="Convert DXF to AutoFire")
    p.add_argument("input", help="Input DXF file")
    p.add_argument("-o", "--output", help="Output .autofire file (default: same name)")
    p.set_defaults(func=cmd_dxf_to_autofire)

    # autofire-to-dxf
    p = subparsers.add_parser("autofire-to-dxf", help="Convert AutoFire to DXF")
    p.add_argument("input", help="Input .autofire file")
    p.add_argument("-o", "--output", help="Output DXF file (default: same name)")
    p.set_defaults(func=cmd_autofire_to_dxf)

    # batch
    p = subparsers.add_parser("batch", help="Batch convert multiple files")
    p.add_argument("inputs", nargs="+", help="Input files (supports wildcards)")
    p.add_argument(
        "--to",
        required=True,
        choices=[".dxf", ".dwg", ".autofire"],
        help="Target format",
    )
    p.set_defaults(func=cmd_batch)

    # detect
    p = subparsers.add_parser("detect", help="Detect file format")
    p.add_argument("file", help="File to detect")
    p.set_defaults(func=cmd_detect)

    # info
    p = subparsers.add_parser("info", help="Show converter information")
    p.set_defaults(func=cmd_info)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
