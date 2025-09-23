#!/usr/bin/env python3
"""
Script to check all device types in the database.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect

def check_all_device_types():
    """Check all device types in the database."""
    print("Checking all device types...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Get all device types
        cur.execute("SELECT code FROM device_types ORDER BY code")
        types = cur.fetchall()
        print("All device types:")
        for i, t in enumerate(types):
            print(f"  {i+1}. {t[0]}")
            if i >= 30:  # Limit output
                print("  ... (more)")
                break
            
        con.close()
        
    except Exception as e:
        print(f"Error checking device types: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_all_device_types()