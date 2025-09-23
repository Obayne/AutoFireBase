#!/usr/bin/env python3
"""
Script to verify the AutoFire database structure and content.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect

def verify_database():
    """Verify the database structure and content."""
    print("Connecting to AutoFire database...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Check table structure
        print("\n=== DATABASE STRUCTURE ===")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        print(f"Tables: {tables}")
        
        # Check row counts
        print("\n=== ROW COUNTS ===")
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            count = cur.fetchone()[0]
            print(f"{table}: {count} rows")
            
        # Check manufacturers
        print("\n=== MANUFACTURERS ===")
        cur.execute("SELECT id, name FROM manufacturers ORDER BY name LIMIT 10;")
        manufacturers = cur.fetchall()
        for manufacturer in manufacturers:
            print(f"  {manufacturer[0]}: {manufacturer[1]}")
            
        # Check device types
        print("\n=== DEVICE TYPES ===")
        cur.execute("SELECT id, code, description FROM device_types ORDER BY code;")
        device_types = cur.fetchall()
        for device_type in device_types:
            print(f"  {device_type[0]}: {device_type[1]} - {device_type[2]}")
            
        # Check system categories
        print("\n=== SYSTEM CATEGORIES ===")
        cur.execute("SELECT id, name FROM system_categories ORDER BY name;")
        categories = cur.fetchall()
        for category in categories:
            print(f"  {category[0]}: {category[1]}")
            
        # Check sample devices
        print("\n=== SAMPLE DEVICES ===")
        cur.execute("""
            SELECT d.id, m.name as manufacturer, dt.code as type, sc.name as category, 
                   d.model, d.name, d.symbol
            FROM devices d
            LEFT JOIN manufacturers m ON d.manufacturer_id = m.id
            LEFT JOIN device_types dt ON d.type_id = dt.id
            LEFT JOIN system_categories sc ON d.category_id = sc.id
            ORDER BY d.id
            LIMIT 10;
        """)
        devices = cur.fetchall()
        for device in devices:
            print(f"  {device[0]}: {device[1]} {device[2]} ({device[3]}) - {device[4]} ({device[5]}) [{device[6]}]")
            
        # Check fire alarm device specs
        print("\n=== FIRE ALARM DEVICE SPECS ===")
        cur.execute("""
            SELECT fas.device_id, d.name, fas.device_class, fas.max_current_ma, fas.voltage_v
            FROM fire_alarm_device_specs fas
            JOIN devices d ON fas.device_id = d.id
            ORDER BY fas.device_id
            LIMIT 10;
        """)
        specs = cur.fetchall()
        for spec in specs:
            print(f"  {spec[0]}: {spec[1]} ({spec[2]}) - {spec[3]}mA @ {spec[4]}V")
            
        con.close()
        print("\n=== DATABASE VERIFICATION COMPLETE ===")
        
    except Exception as e:
        print(f"Error verifying database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_database()