#!/usr/bin/env python3
"""
Script to check devices and their categories in the database.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect

def check_devices():
    """Check devices and their categories."""
    print("Checking devices and categories...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Get total device count
        cur.execute('SELECT COUNT(*) FROM devices')
        total_count = cur.fetchone()[0]
        print(f"Total devices: {total_count}")
        
        # Get sample devices with categories
        cur.execute('''
            SELECT d.name, sc.name as category 
            FROM devices d 
            JOIN system_categories sc ON d.category_id = sc.id 
            LIMIT 10
        ''')
        devices = cur.fetchall()
        print("\nSample devices:")
        for device in devices:
            print(f"  {device[0]} -> {device[1]}")
            
        # Get all unique categories
        cur.execute('SELECT DISTINCT sc.name FROM system_categories sc JOIN devices d ON d.category_id = sc.id ORDER BY sc.name')
        categories = cur.fetchall()
        print(f"\nTotal unique categories: {len(categories)}")
        print("First 20 categories:")
        for i, category in enumerate(categories[:20]):
            print(f"  {i+1}. {category[0]}")
            
        con.close()
        
    except Exception as e:
        print(f"Error checking devices: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_devices()