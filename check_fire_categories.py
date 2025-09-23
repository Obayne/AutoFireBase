#!/usr/bin/env python3
"""
Script to check fire-related categories in the database.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect

def check_fire_categories():
    """Check fire-related categories in the database."""
    print("Checking fire-related categories...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Get fire-related categories
        cur.execute("""
            SELECT DISTINCT sc.name 
            FROM system_categories sc 
            JOIN devices d ON sc.id = d.category_id 
            WHERE sc.name LIKE '%Fire%' OR sc.name LIKE '%Alarm%' OR sc.name LIKE '%Detector%' OR sc.name LIKE '%Strobe%' OR sc.name LIKE '%Horn%' OR sc.name LIKE '%Speaker%'
            ORDER BY sc.name
        """)
        
        categories = cur.fetchall()
        print("Fire-related categories:")
        for cat in categories:
            print(f"  - {cat[0]}")
            
        # Get count of devices in each category
        print("\nDevice counts by category:")
        for cat in categories:
            cur.execute("""
                SELECT COUNT(*) 
                FROM devices d 
                JOIN system_categories sc ON d.category_id = sc.id 
                WHERE sc.name = ?
            """, (cat[0],))
            
            count = cur.fetchone()[0]
            print(f"  - {cat[0]}: {count} devices")
            
        con.close()
        
    except Exception as e:
        print(f"Error checking fire categories: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_fire_categories()