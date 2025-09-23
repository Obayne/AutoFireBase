#!/usr/bin/env python3
"""
Script to identify key fire alarm devices for NFPA-compliant block diagrams.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect

def identify_fire_alarm_devices():
    """Identify key fire alarm devices for NFPA-compliant block diagrams."""
    print("Identifying key fire alarm devices...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Get fire alarm system categories
        cur.execute("""
            SELECT sc.name, COUNT(d.id) as device_count
            FROM system_categories sc
            JOIN devices d ON sc.id = d.category_id
            WHERE sc.name LIKE '%Fire%' OR sc.name LIKE '%Alarm%' OR sc.name LIKE '%Detector%' 
               OR sc.name LIKE '%Strobe%' OR sc.name LIKE '%Horn%' OR sc.name LIKE '%Speaker%'
            GROUP BY sc.name
            ORDER BY device_count DESC
        """)
        
        categories = cur.fetchall()
        print("Key fire alarm device categories:")
        for cat in categories:
            print(f"  - {cat[0]}: {cat[1]} devices")
            
        # Get specific fire alarm device types that are most common
        cur.execute("""
            SELECT d.symbol, COUNT(d.id) as device_count
            FROM devices d
            JOIN system_categories sc ON d.category_id = sc.id
            WHERE sc.name LIKE '%Fire%' OR sc.name LIKE '%Alarm%' OR sc.name LIKE '%Detector%' 
               OR sc.name LIKE '%Strobe%' OR sc.name LIKE '%Horn%' OR sc.name LIKE '%Speaker%'
            GROUP BY d.symbol
            ORDER BY device_count DESC
            LIMIT 15
        """)
        
        symbols = cur.fetchall()
        print("\nMost common fire alarm device symbols:")
        for symbol in symbols:
            print(f"  - {symbol[0]}: {symbol[1]} devices")
            
        # Get sample devices for each key category
        key_categories = ['Smoke Detector', 'Heat Detector', 'Strobe', 'Horn/Strobe', 'Speaker', 'Fire Alarm Control Unit', 'Manual Station']
        
        print("\nSample devices for key categories:")
        for category in key_categories:
            cur.execute("""
                SELECT d.name, d.symbol, m.name as manufacturer
                FROM devices d
                JOIN system_categories sc ON d.category_id = sc.id
                JOIN manufacturers m ON d.manufacturer_id = m.id
                WHERE sc.name = ?
                LIMIT 3
            """, (category,))
            
            devices = cur.fetchall()
            if devices:
                print(f"\n  {category}:")
                for device in devices:
                    print(f"    - {device[0]} ({device[1]}) by {device[2]}")
                    
        con.close()
        print("\n=== FIRE ALARM DEVICE IDENTIFICATION COMPLETE ===")
        
    except Exception as e:
        print(f"Error identifying fire alarm devices: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    identify_fire_alarm_devices()