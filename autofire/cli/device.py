"""
AutoFire Device Manager CLI Tool

A command-line interface for managing AutoFire device catalog and database.
"""

import argparse
import csv
import json
import os
import sqlite3
import sys

# Import from the main project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from db import connection as db_connection
from db import loader as db_loader


def list_devices(device_type: str | None = None, manufacturer: str | None = None) -> None:
    """List devices from the catalog with optional filters."""
    # Initialize database connection
    db_connection.initialize_database(in_memory=False)
    con = db_connection.get_connection()
    con.row_factory = sqlite3.Row  # Enable dict-like access to rows

    try:
        # Ensure database is seeded
        db_loader.ensure_schema(con)
        db_loader.seed_demo(con)

        devices = db_loader.search_devices(
            con,
            device_type=device_type or "",
            manufacturer=manufacturer or "",
        )

        # Filter devices (additional client-side filtering if needed)
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
        header = f"{'ID':<5} {'Name':<30} {'Type':<15} {'Manufacturer':<15} {'Part #':<12}"
        print(header)
        print("-" * len(header))

        for device in sorted(filtered, key=lambda x: (x.get("type", ""), x.get("name", ""))):
            dev_id = device.get("id", "N/A")
            name = device.get("name", "Unknown")
            dev_type = device.get("type", "Unknown")
            mfg = device.get("manufacturer", "Unknown")
            part = device.get("model", "")
            print(f"{dev_id:<5} {name:<30} {dev_type:<15} {mfg:<15} {part:<12}")
    finally:
        db_connection.close_connection()


def list_types_cli() -> None:
    """List available device types (read-only)."""
    # Initialize database connection
    db_connection.initialize_database(in_memory=False)
    con = db_connection.get_connection()
    try:
        db_loader.ensure_schema(con)
        db_loader.seed_demo(con)
        cur = con.cursor()
        cur.execute("SELECT DISTINCT code FROM device_types ORDER BY code")
        types = [r[0] for r in cur.fetchall()]
    finally:
        db_connection.close_connection()
    print("Device types:")
    for t in types:
        print(f"  {t}")


def list_manufacturers_cli() -> None:
    """List available manufacturers (read-only)."""
    # Initialize database connection
    db_connection.initialize_database(in_memory=False)
    con = db_connection.get_connection()
    try:
        db_loader.ensure_schema(con)
        db_loader.seed_demo(con)
        cur = con.cursor()
        cur.execute("SELECT DISTINCT name FROM manufacturers ORDER BY name")
        mfrs = [r[0] for r in cur.fetchall()]
    finally:
        db_connection.close_connection()
    print("Manufacturers:")
    for m in mfrs:
        print(f"  {m}")


def search_devices(query: str) -> None:
    """Search devices by name, type, or manufacturer."""
    # Initialize database connection
    db_connection.initialize_database(in_memory=False)
    con = db_connection.get_connection()
    con.row_factory = sqlite3.Row  # Enable dict-like access to rows

    try:
        # Ensure database is seeded
        db_loader.ensure_schema(con)
        db_loader.seed_demo(con)

        results = db_loader.search_devices(con, search_text=query)

        if not results:
            print(f"No devices found matching '{query}'.")
            return

        print(f"Found {len(results)} device(s) matching '{query}':")
        header = f"{'ID':<5} {'Name':<30} {'Type':<15} {'Manufacturer':<15} {'Part #':<12}"
        print(header)
        print("-" * len(header))

        for device in sorted(results, key=lambda x: x.get("name", "")):
            dev_id = device.get("id", "N/A")
            name = device.get("name", "Unknown")
            dev_type = device.get("type", "Unknown")
            mfg = device.get("manufacturer", "Unknown")
            part = device.get("model", "")
            print(f"{dev_id:<5} {name:<30} {dev_type:<15} {mfg:<15} {part:<12}")
    finally:
        db_connection.close_connection()


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
    # Initialize database connection
    db_connection.initialize_database(in_memory=False)
    con = db_connection.get_connection()
    con.row_factory = sqlite3.Row  # Enable dict-like access to rows

    try:
        # Ensure database is seeded
        db_loader.ensure_schema(con)
        db_loader.seed_demo(con)

        devices = db_loader.fetch_devices(con)

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
                            "part_number": device.get("model", ""),
                            "symbol": device.get("symbol", ""),
                        }
                    )

            print(f"Exported {len(devices)} devices to {output_file}")

        else:
            print(f"Unsupported format: {format_type}")
    finally:
        db_connection.close_connection()


def import_devices(input_file: str, format_type: str = "json") -> None:
    """Import device catalog from file."""
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return

    # Initialize database connection
    db_connection.initialize_database(in_memory=False)
    con = db_connection.get_connection()
    con.row_factory = sqlite3.Row  # Enable dict-like access to rows

    try:
        # Ensure database is seeded (for schema)
        db_loader.ensure_schema(con)

        devices = []
        if format_type == "json":
            with open(input_file, encoding="utf-8") as f:
                devices = json.load(f)
        elif format_type == "csv":
            with open(input_file, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                devices = list(reader)
        else:
            print(f"Unsupported format: {format_type}")
            return

        if not devices:
            print("No devices found in file.")
            return

        imported_count = 0
        for device in devices:
            try:
                # Get or create manufacturer
                manufacturer = device.get("manufacturer", "(Any)")
                mfr_id = db_loader._id_for(con.cursor(), "manufacturers", "name", manufacturer)

                # Get or create device type
                device_type = device.get("type", "Unknown")
                type_id = db_loader._id_for(con.cursor(), "device_types", "code", device_type)

                # Add device
                cur = con.cursor()
                cur.execute(
                    (
                        "INSERT OR REPLACE INTO devices("
                        "manufacturer_id,type_id,model,name,symbol,properties_json) "
                        "VALUES(?,?,?,?,?,?)"
                    ),
                    (
                        mfr_id,
                        type_id,
                        device.get("part_number", device.get("model", "")),
                        device.get("name", "Unknown"),
                        device.get("symbol", device.get("name", "Unknown")[:3].upper()),
                        json.dumps(device.get("props", {})),
                    ),
                )
                imported_count += 1
            except Exception as e:
                print(f"Error importing device {device.get('name', 'Unknown')}: {e}")
                continue

        con.commit()
        print(f"Successfully imported {imported_count} devices from {input_file}")

    finally:
        db_connection.close_connection()


def update_device(
    device_id: int,
    name: str | None = None,
    device_type: str | None = None,
    manufacturer: str | None = None,
    part_number: str | None = None,
) -> None:
    """Update an existing device."""
    # Initialize database connection
    db_connection.initialize_database(in_memory=False)
    con = db_connection.get_connection()
    con.row_factory = sqlite3.Row  # Enable dict-like access to rows

    try:
        # Ensure database is seeded (for schema)
        db_loader.ensure_schema(con)

        # Check if device exists
        cur = con.cursor()
        cur.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        device = cur.fetchone()
        if not device:
            print(f"Device with ID {device_id} not found.")
            return

        # Prepare update data
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if device_type is not None:
            # Get or create device type
            type_id = db_loader._id_for(cur, "device_types", "code", device_type)
            update_data["type_id"] = type_id
        if manufacturer is not None:
            # Get or create manufacturer
            mfr_id = db_loader._id_for(cur, "manufacturers", "name", manufacturer)
            update_data["manufacturer_id"] = mfr_id
        if part_number is not None:
            update_data["model"] = part_number

        if not update_data:
            print("No fields to update.")
            return

        # Build update query
        set_clause = ", ".join(f"{k} = ?" for k in update_data.keys())
        values = list(update_data.values()) + [device_id]

        cur.execute(f"UPDATE devices SET {set_clause} WHERE id = ?", values)
        con.commit()

        print(f"Device {device_id} updated successfully.")

    finally:
        db_connection.close_connection()


def delete_device(device_id: int, confirm: bool = True) -> None:
    """Delete a device from the catalog."""
    if confirm:
        response = input(f"Are you sure you want to delete device {device_id}? (y/N): ")
        if response.lower() not in ("y", "yes"):
            print("Operation cancelled.")
            return

    # Initialize database connection
    db_connection.initialize_database(in_memory=False)
    con = db_connection.get_connection()
    con.row_factory = sqlite3.Row  # Enable dict-like access to rows

    try:
        # Check if device exists
        cur = con.cursor()
        cur.execute("SELECT name FROM devices WHERE id = ?", (device_id,))
        device = cur.fetchone()
        if not device:
            print(f"Device with ID {device_id} not found.")
            return

        # Delete the device
        cur.execute("DELETE FROM devices WHERE id = ?", (device_id,))
        con.commit()

        print(f"Device '{device['name']}' (ID: {device_id}) deleted successfully.")

    finally:
        db_connection.close_connection()


def db_init() -> None:
    """Initialize/reset the database schema."""
    # Initialize database connection
    db_connection.initialize_database(in_memory=False)
    con = db_connection.get_connection()

    try:
        print("Initializing database schema...")
        db_loader.ensure_schema(con)
        print("Database schema initialized successfully.")
    finally:
        db_connection.close_connection()


def db_seed() -> None:
    """Seed the database with demo data."""
    # Initialize database connection
    db_connection.initialize_database(in_memory=False)
    con = db_connection.get_connection()
    con.row_factory = sqlite3.Row  # Enable dict-like access to rows

    try:
        print("Seeding database with demo data...")
        db_loader.ensure_schema(con)
        db_loader.seed_demo(con)
        print("Database seeded successfully.")
    finally:
        db_connection.close_connection()


def db_backup(output_file: str) -> None:
    """Backup the database to a file."""
    import shutil

    db_path = os.path.join(os.path.expanduser("~"), "AutoFire", "catalog.db")
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    try:
        shutil.copy2(db_path, output_file)
        print(f"Database backed up to {output_file}")
    except Exception as e:
        print(f"Error backing up database: {e}")


def db_restore(input_file: str) -> None:
    """Restore the database from a backup file."""
    import shutil

    if not os.path.exists(input_file):
        print(f"Backup file not found: {input_file}")
        return

    db_path = os.path.join(os.path.expanduser("~"), "AutoFire", "catalog.db")
    db_dir = os.path.dirname(db_path)
    os.makedirs(db_dir, exist_ok=True)

    try:
        shutil.copy2(input_file, db_path)
        print(f"Database restored from {input_file}")
    except Exception as e:
        print(f"Error restoring database: {e}")


def show_stats() -> None:
    """Show catalog statistics."""
    # Initialize database connection
    db_connection.initialize_database(in_memory=False)
    con = db_connection.get_connection()
    con.row_factory = sqlite3.Row  # Enable dict-like access to rows

    try:
        # Ensure database is seeded
        db_loader.ensure_schema(con)
        db_loader.seed_demo(con)

        devices = db_loader.fetch_devices(con)

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
    finally:
        db_connection.close_connection()


def show_device(
    device_id: int | None = None,
    name: str | None = None,
    part_number: str | None = None,
    contains: str | None = None,
    *,
    first_only: bool = True,
    all_matches: bool = False,
) -> None:
    # Show device details by id, or exact name/part number
    db_connection.initialize_database(in_memory=False)
    con = db_connection.get_connection()
    con.row_factory = sqlite3.Row

    try:
        db_loader.ensure_schema(con)
        db_loader.seed_demo(con)
        cur = con.cursor()
        rows: list[sqlite3.Row] = []
        if device_id is not None:
            cur.execute(
                (
                    "SELECT d.id, d.name, d.symbol, dt.code AS type, "
                    "m.name AS manufacturer, d.model AS part_number "
                    "FROM devices d "
                    "LEFT JOIN manufacturers m ON m.id=d.manufacturer_id "
                    "LEFT JOIN device_types dt ON dt.id=d.type_id "
                    "WHERE d.id = ?"
                ),
                (device_id,),
            )
            r = cur.fetchone()
            rows = [r] if r else []
        elif part_number:
            cur.execute(
                (
                    "SELECT d.id, d.name, d.symbol, dt.code AS type, "
                    "m.name AS manufacturer, d.model AS part_number "
                    "FROM devices d "
                    "LEFT JOIN manufacturers m ON m.id=d.manufacturer_id "
                    "LEFT JOIN device_types dt ON dt.id=d.type_id "
                    "WHERE d.model = ? ORDER BY d.id"
                ),
                (part_number,),
            )
            rows = cur.fetchall()
        elif name:
            cur.execute(
                (
                    "SELECT d.id, d.name, d.symbol, dt.code AS type, "
                    "m.name AS manufacturer, d.model AS part_number "
                    "FROM devices d "
                    "LEFT JOIN manufacturers m ON m.id=d.manufacturer_id "
                    "LEFT JOIN device_types dt ON dt.id=d.type_id "
                    "WHERE d.name = ? ORDER BY d.id"
                ),
                (name,),
            )
            rows = cur.fetchall()
        elif contains:
            like = f"%{contains}%"
            cur.execute(
                (
                    "SELECT d.id, d.name, d.symbol, dt.code AS type, "
                    "m.name AS manufacturer, d.model AS part_number "
                    "FROM devices d "
                    "LEFT JOIN manufacturers m ON m.id=d.manufacturer_id "
                    "LEFT JOIN device_types dt ON dt.id=d.type_id "
                    "WHERE d.name LIKE ? OR d.model LIKE ? OR m.name LIKE ? "
                    "ORDER BY d.id"
                ),
                (like, like, like),
            )
            rows = cur.fetchall()

        if not rows:
            print("No matching device found.")
            return

        use_all = all_matches or not first_only
        items = rows if use_all else [rows[0]]
        for row in items:
            d = dict(row)
            print("Device:")
            print(f"  ID           : {d.get('id','')}")
            print(f"  Name         : {d.get('name','')}")
            print(f"  Type         : {d.get('type','')}")
            print(f"  Manufacturer : {d.get('manufacturer','')}")
            print(f"  Part #       : {d.get('part_number','')}")
            print(f"  Symbol       : {d.get('symbol','')}")
    finally:
        db_connection.close_connection()


def count_cli(
    group_by: str = "type", *, json_output: bool = False, output_file: str | None = None
) -> None:
    # Show counts grouped by type or manufacturer
    group_by = (group_by or "type").lower().strip()
    if group_by not in {"type", "manufacturer"}:
        print("Unsupported group. Use 'type' or 'manufacturer'.")
        return

    db_connection.initialize_database(in_memory=False)
    con = db_connection.get_connection()
    con.row_factory = sqlite3.Row
    try:
        db_loader.ensure_schema(con)
        db_loader.seed_demo(con)
        cur = con.cursor()
        if group_by == "type":
            cur.execute(
                "SELECT dt.code AS label, COUNT(*) AS c "
                "FROM devices d "
                "LEFT JOIN device_types dt ON dt.id=d.type_id "
                "GROUP BY dt.code ORDER BY dt.code"
            )
            header = "Counts by type:"
        else:
            cur.execute(
                "SELECT m.name AS label, COUNT(*) AS c "
                "FROM devices d "
                "LEFT JOIN manufacturers m ON m.id=d.manufacturer_id "
                "GROUP BY m.name ORDER BY m.name"
            )
            header = "Counts by manufacturer:"

        rows = cur.fetchall()
        if json_output:
            payload = {r["label"]: int(r["c"]) for r in rows}
            if output_file:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2, ensure_ascii=False)
                print(f"Exported counts to {output_file}")
            else:
                print(json.dumps(payload, indent=2))
        else:
            print(header)
            for r in rows:
                print(f"  {r['label']}: {r['c']}")
    finally:
        db_connection.close_connection()


def main() -> None:
    """Main CLI entry point for device management."""
    parser = argparse.ArgumentParser(
        description="AutoFire Device Manager CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage:
    autofire-cli list [--type TYPE] [--manufacturer MFG]
    autofire-cli search QUERY
    autofire-cli add --name NAME --type TYPE [--manufacturer MFG] [--part-number PN]
    autofire-cli export [--format json|csv] [--output FILE]
    autofire-cli stats

Examples:
    autofire-cli list --type "Detector"
    autofire-cli search "smoke"
    autofire-cli add --name "New Device" --type "Notification" --manufacturer "Generic"
    autofire-cli export --format csv --output devices.csv
    autofire-cli stats
        """,
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

    # Update command
    update_parser = subparsers.add_parser("update", help="Update existing device")
    update_parser.add_argument("id", type=int, help="Device ID")
    update_parser.add_argument("--name", help="New device name")
    update_parser.add_argument("--type", help="New device type")
    update_parser.add_argument("--manufacturer", help="New device manufacturer")
    update_parser.add_argument("--part-number", help="New part number/model")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete device")
    delete_parser.add_argument("id", type=int, help="Device ID")
    delete_parser.add_argument("--force", action="store_true", help="Skip confirmation")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export device catalog")
    export_parser.add_argument(
        "--format", choices=["json", "csv"], default="json", help="Export format"
    )
    export_parser.add_argument("--output", help="Output file path")

    # Import command
    import_parser = subparsers.add_parser("import", help="Import device catalog")
    import_parser.add_argument("input", help="Input file path")
    import_parser.add_argument(
        "--format", choices=["json", "csv"], default="json", help="Import format"
    )

    # Database management commands
    subparsers.add_parser("db-init", help="Initialize/reset database schema")
    subparsers.add_parser("db-seed", help="Seed database with demo data")

    db_backup_parser = subparsers.add_parser("db-backup", help="Backup database")
    db_backup_parser.add_argument("output", help="Output backup file path")

    db_restore_parser = subparsers.add_parser("db-restore", help="Restore database from backup")
    db_restore_parser.add_argument("input", help="Input backup file path")

    # Stats command
    subparsers.add_parser("stats", help="Show catalog statistics")

    # Types and Manufacturers
    subparsers.add_parser("types", help="List available device types")
    subparsers.add_parser("manufacturers", help="List available manufacturers")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show device details")
    mex = show_parser.add_mutually_exclusive_group(required=True)
    mex.add_argument("--id", type=int, help="Device ID")
    mex.add_argument("--name", help="Exact device name")
    mex.add_argument("--part-number", help="Exact part number/model")
    mex.add_argument("--contains", help="Partial match in name/part/manufacturer")
    show_parser.add_argument("--all", action="store_true", help="Print all matches")

    # Count command
    count_parser = subparsers.add_parser("count", help="Count devices by group")
    count_parser.add_argument(
        "--by", choices=["type", "manufacturer"], default="type", help="Group field"
    )
    count_parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    count_parser.add_argument("--output", help="Write JSON to file (UTF-8)")

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
    elif args.command == "update":
        update_device(args.id, args.name, args.type, args.manufacturer, args.part_number)
    elif args.command == "delete":
        delete_device(args.id, not args.force)
    elif args.command == "export":
        export_devices(args.format, args.output)
    elif args.command == "import":
        import_devices(args.input, args.format)
    elif args.command == "db-init":
        db_init()
    elif args.command == "db-seed":
        db_seed()
    elif args.command == "db-backup":
        db_backup(args.output)
    elif args.command == "db-restore":
        db_restore(args.input)
    elif args.command == "stats":
        show_stats()
    elif args.command == "types":
        list_types_cli()
    elif args.command == "manufacturers":
        list_manufacturers_cli()
    elif args.command == "show":
        show_device(
            args.id,
            args.name,
            args.part_number,
            args.contains,
            all_matches=args.all,
        )
    elif args.command == "count":
        count_cli(args.by, json_output=args.json, output_file=args.output)


if __name__ == "__main__":
    main()
