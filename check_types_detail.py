#!/usr/bin/env python3
"""
Script to check device types in detail.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect

def check_types_detail():
    """Check device types in detail."""
    print("Checking device types in detail...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Check device types with column names
        cur.execute('SELECT id, code, description FROM device_types')
        types = cur.fetchall()
        print(f"Device types ({len(types)}):")
        for t in types:
            print(f"  ID: {t[0]}, Code: {t[1]}, Description: {t[2]}")
        
        con.close()
        
    except Exception as e:
        print(f"Error checking device types: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_types_detail()