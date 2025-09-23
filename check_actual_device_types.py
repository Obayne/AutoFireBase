#!/usr/bin/env python3
"""
Script to check actual device types being used in the database.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect

def check_actual_device_types():
    """Check actual device types being used in the database."""
    print("Checking actual device types...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Check if device_types table has data
        cur.execute("SELECT COUNT(*) FROM device_types")
        count = cur.fetchone()[0]
        print(f"Device types table count: {count}")
        
        # Check what's in the devices table
        cur.execute("SELECT COUNT(*) FROM devices")
        device_count = cur.fetchone()[0]
        print(f"Total devices: {device_count}")
        
        # Check a sample device
        cur.execute("SELECT * FROM devices LIMIT 1")
        sample_device = cur.fetchone()
        print(f"Sample device: {dict(sample_device) if sample_device else 'None'}")
        
        con.close()
        
    except Exception as e:
        print(f"Error checking device types: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_actual_device_types()