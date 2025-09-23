#!/usr/bin/env python3
"""
Debug script to understand the query results.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect

def debug_query():
    """Debug the query to understand what's happening."""
    print("Debugging query...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Check total device count
        cur.execute('SELECT COUNT(*) FROM devices')
        total_count = cur.fetchone()[0]
        print(f"Total devices: {total_count}")
        
        # Try the exact query we're using
        query = '''
            SELECT d.id, d.name, d.symbol, dt.code as type, sc.name as category
            FROM devices d 
            JOIN system_categories sc ON d.category_id = sc.id 
            JOIN device_types dt ON d.type_id = dt.id
            WHERE sc.name LIKE '%Fire%' OR sc.name LIKE '%Smoke%' OR sc.name LIKE '%Heat%' 
            OR sc.name LIKE '%Strobe%' OR sc.name LIKE '%Horn%' OR sc.name LIKE '%Speaker%'
            OR sc.name LIKE '%Manual%' OR sc.name LIKE '%Panel%' OR sc.name LIKE '%Control%'
        '''
        
        cur.execute(query)
        devices = cur.fetchall()
        print(f"Query returned {len(devices)} devices")
        
        # Show first 10 devices
        print("\nFirst 10 devices from query:")
        for i, device in enumerate(devices[:10]):
            print(f"  {i+1}. ID: {device[0]}, Name: {device[1]}, Type: {device[3]}, Category: {device[4]}")
            
        # Check if there are any issues with the joins
        print("\nChecking joins...")
        cur.execute('SELECT COUNT(*) FROM devices d JOIN system_categories sc ON d.category_id = sc.id')
        join_count = cur.fetchone()[0]
        print(f"Devices with valid category join: {join_count}")
        
        cur.execute('SELECT COUNT(*) FROM devices d JOIN device_types dt ON d.type_id = dt.id')
        type_join_count = cur.fetchone()[0]
        print(f"Devices with valid type join: {type_join_count}")
        
        # Check a simple query without joins
        cur.execute("SELECT COUNT(*) FROM system_categories WHERE name LIKE '%Fire%'")
        fire_categories = cur.fetchone()[0]
        print(f"Fire categories: {fire_categories}")
        
        cur.execute("SELECT name FROM system_categories WHERE name LIKE '%Fire%' LIMIT 5")
        fire_category_names = cur.fetchall()
        print("Sample fire categories:")
        for cat in fire_category_names:
            print(f"  {cat[0]}")
        
        con.close()
        
    except Exception as e:
        print(f"Error in debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_query()