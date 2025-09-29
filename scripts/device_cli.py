#!/usr/bin/env python3
"""
AutoFire Device Manager CLI Tool

A command-line interface for managing AutoFire device catalog and database.

Usage:
    python device_cli.py list [--type TYPE] [--manufacturer MFG]
    python device_cli.py search QUERY
    python device_cli.py add --name NAME --type TYPE [--manufacturer MFG] [--part-number PN]
    python device_cli.py export [--format json|csv] [--output FILE]
    python device_cli.py stats

Examples:
    python device_cli.py list --type "Detector"
    python device_cli.py search "smoke"
    python device_cli.py add --name "New Device" --type "Notification" --manufacturer "Generic"
    python device_cli.py export --format csv --output devices.csv
    python device_cli.py stats
"""

import argparse
import csv
import json
import os
import sys

# Add the app directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import catalog


def list_devices(device_type: str | None = None, manufacturer: str | None = None) -> None:
    """List devices from the catalog with optional filters."""
    devices = catalog.load_catalog()

    # Filter devices
    filtered = devices
    if device_type:
        filtered = [d for d in filtered if d.get("type", "").lower() == device_type.lower()]
    if manufacturer:
        filtered = [
            d for d in filtered if d.get("manufacturer", "").lower() == manufacturer.lower()
        ]

    if not filtered:
        print("No devices found matching criteria.")
        return

    print(f"Found {len(filtered)} device(s):")
    header = f"{'Name':<30} {'Type':<15} {'Manufacturer':<15} {'Part #':<12}"
    print(header)
    print("-" * len(header))

    for device in sorted(filtered, key=lambda x: (x.get("type", ""), x.get("name", ""))):
        name = device.get("name", "Unknown")
        dev_type = device.get("type", "Unknown")
        mfg = device.get("manufacturer", "Unknown")
        part = device.get("part_number", "")
        print(f"{name:<30} {dev_type:<15} {mfg:<15} {part:<12}")


def search_devices(query: str) -> None:
    """Search devices by name, type, or manufacturer."""
    devices = catalog.load_catalog()

    # Simple text search
    query_lower = query.lower()
    results: list[dict] = []
    for device in devices:
        searchable = " ".join(
            [
                device.get("name", ""),
                device.get("type", ""),
                device.get("manufacturer", ""),
                device.get("part_number", ""),
                device.get("symbol", ""),
            ]
        ).lower()

        if query_lower in searchable:
            results.append(device)

    if not results:
        print(f"No devices found matching '{query}'.")
        return

    print(f"Found {len(results)} device(s) matching '{query}':")
    header = f"{'Name':<30} {'Type':<15} {'Manufacturer':<15} {'Part #':<12}"
    print(header)
    print("-" * len(header))

    for device in sorted(results, key=lambda x: x.get("name", "")):
        name = device.get("name", "Unknown")
        dev_type = device.get("type", "Unknown")
        mfg = device.get("manufacturer", "Unknown")
        part = device.get("part_number", "")
        print(f"{name:<30} {dev_type:<15} {mfg:<15} {part:<12}")


def add_device(
    name: str, device_type: str, manufacturer: str | None = None, part_number: str | None = None
) -> None:
    """Add a new device to the database."""
    try:
        # Import database loader
        import sqlite3  # noqa: F401  # used for types and exceptions if needed

        from db import loader as db_loader

        # Connect to database
        con = db_loader.connect()
        db_loader.ensure_schema(con)

        # Get or create manufacturer
        if manufacturer:
            mfr_id = db_loader._id_for(con.cursor(), "manufacturers", "name", manufacturer)
        else:
            mfr_id = db_loader._id_for(con.cursor(), "manufacturers", "name", "(Any)")

        # Get or create device type
        type_id = db_loader._id_for(con.cursor(), "device_types", "code", device_type)

        # Generate symbol from name if not provided
        symbol = name[:3].upper() if len(name) >= 3 else name.upper()

        # Add device
        cur = con.cursor()
        cur.execute(
            "INSERT INTO devices(manufacturer_id,type_id,model,name,symbol) VALUES(?,?,?,?,?)",
            (mfr_id, type_id, part_number or "", name, symbol),
        )

        con.commit()
        con.close()

        print(f"Added device: {name} ({device_type})")
    except Exception as e:  # noqa: BLE001 - surface error in CLI
        print(f"Error adding device: {e}")


def export_devices(format_type: str = "json", output_file: str | None = None) -> None:
    """Export device catalog to file or stdout."""
    devices = catalog.load_catalog()

    if format_type == "json":
        data = devices
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Exported {len(devices)} devices to {output_file}")
        else:
            # Use ASCII escapes on stdout to avoid Windows console encoding issues
            print(json.dumps(data, indent=2))

    elif format_type == "csv":
        if not output_file:
            output_file = "devices.csv"

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["name", "type", "manufacturer", "part_number", "symbol"]
            )
            writer.writeheader()
            for device in devices:
                writer.writerow(
                    {
                        "name": device.get("name", ""),
                        "type": device.get("type", ""),
                        "manufacturer": device.get("manufacturer", ""),
                        "part_number": device.get("part_number", ""),
                        "symbol": device.get("symbol", ""),
                    }
                )

        print(f"Exported {len(devices)} devices to {output_file}")

    else:
        print(f"Unsupported format: {format_type}")


def show_stats() -> None:
    """Show catalog statistics."""
    devices = catalog.load_catalog()

    # Count by type
    types: dict[str, int] = {}
    manufacturers: dict[str, int] = {}
    total = len(devices)

    for device in devices:
        dev_type = device.get("type", "Unknown")
        mfg = device.get("manufacturer", "Unknown")

        types[dev_type] = types.get(dev_type, 0) + 1
        manufacturers[mfg] = manufacturers.get(mfg, 0) + 1

    print("AutoFire Device Catalog Statistics")
    print("===================================")
    print(f"Total devices: {total}")
    print()

    print("Devices by type:")
    for dev_type, count in sorted(types.items()):
        print(f"  {dev_type}: {count}")
    print()

    print("Devices by manufacturer:")
    for mfg, count in sorted(manufacturers.items()):
        print(f"  {mfg}: {count}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AutoFire Device Manager CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List devices")
    list_parser.add_argument("--type", help="Filter by device type")
    list_parser.add_argument("--manufacturer", help="Filter by manufacturer")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search devices")
    search_parser.add_argument("query", help="Search query")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add new device")
    add_parser.add_argument("--name", required=True, help="Device name")
    add_parser.add_argument("--type", required=True, help="Device type")
    add_parser.add_argument("--manufacturer", help="Device manufacturer")
    add_parser.add_argument("--part-number", help="Part number/model")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export device catalog")
    export_parser.add_argument(
        "--format", choices=["json", "csv"], default="json", help="Export format"
    )
    export_parser.add_argument("--output", help="Output file path")

    # Stats command
    subparsers.add_parser("stats", help="Show catalog statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "list":
        list_devices(args.type, args.manufacturer)
    elif args.command == "search":
        search_devices(args.query)
    elif args.command == "add":
        add_device(args.name, args.type, args.manufacturer, args.part_number)
    elif args.command == "export":
        export_devices(args.format, args.output)
    elif args.command == "stats":
        show_stats()


if __name__ == "__main__":
    main()
