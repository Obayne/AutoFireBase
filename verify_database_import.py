#!/usr/bin/env python3
"""
Script to verify database import and display imported device data.
"""

import os
import sys
import sqlite3
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect, fetch_devices

def verify_database_import():
    """Verify that devices have been imported into the database."""
    print("Verifying database import...")
    
    try:
        # Connect to database
        con = connect()
        print("Connected to database successfully")
        
        # Check database schema
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        print(f"Database tables: {[t[0] for t in tables]}")
        
        # Count devices
        cur.execute("SELECT COUNT(*) AS count FROM devices;")
        device_count = cur.fetchone()[0]
        print(f"Total devices in database: {device_count}")
        
        # Show sample devices
        if device_count > 0:
            print("\nSample devices:")
            devices = fetch_devices(con)
            for i, device in enumerate(devices[:10]):  # Show first 10 devices
                print(f"  {i+1}. {device['name']} ({device['symbol']}) - {device['manufacturer']} {device['part_number']}")
                
            if device_count > 10:
                print(f"  ... and {device_count - 10} more devices")
                
        # Check fire alarm specs
        cur.execute("SELECT COUNT(*) AS count FROM fire_alarm_device_specs;")
        specs_count = cur.fetchone()[0]
        print(f"\nDevices with fire alarm specs: {specs_count}")
        
        # Close connection
        con.close()
        
        print("\nDatabase verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error verifying database: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_database_stats():
    """Show detailed database statistics."""
    print("Database Statistics:")
    
    try:
        # Connect to database
        con = connect()
        cur = con.cursor()
        
        # Table counts
        tables = ['manufacturers', 'device_types', 'devices', 'fire_alarm_device_specs']
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) AS count FROM {table};")
                count = cur.fetchone()[0]
                print(f"  {table}: {count} records")
            except:
                print(f"  {table}: Table not found or error accessing")
        
        # Device types
        print("\nDevice types:")
        try:
            cur.execute("SELECT code, description FROM device_types;")
            types = cur.fetchall()
            for t in types:
                print(f"  {t[0]}: {t[1]}")
        except Exception as e:
            print(f"  Error fetching device types: {e}")
            
        # Manufacturers
        print("\nManufacturers:")
        try:
            cur.execute("SELECT name FROM manufacturers ORDER BY name;")
            manufacturers = cur.fetchall()
            for m in manufacturers[:10]:  # Show first 10
                print(f"  {m[0]}")
            if len(manufacturers) > 10:
                print(f"  ... and {len(manufacturers) - 10} more")
        except Exception as e:
            print(f"  Error fetching manufacturers: {e}")
        
        # Close connection
        con.close()
        
    except Exception as e:
        print(f"Error showing database stats: {e}")

if __name__ == "__main__":
    verify_database_import()
    print()
    show_database_stats()