#!/usr/bin/env python3
"""
Script to demonstrate linking devices to CAD blocks.
"""

import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect, register_block_for_device, get_block_for_device, fetch_devices

def demonstrate_block_linking():
    """Demonstrate linking devices to CAD blocks."""
    print("Demonstrating device to block linking...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Get a few sample devices by manufacturer
        manufacturers = ['Edwards', 'System Sensor', 'Honeywell']
        
        for manufacturer in manufacturers:
            print(f"\n=== Linking blocks for {manufacturer} devices ===")
            
            # Get devices for this manufacturer
            cur.execute("""
                SELECT d.id, d.name, d.model, dt.code as type, sc.name as category
                FROM devices d
                JOIN manufacturers m ON d.manufacturer_id = m.id
                JOIN device_types dt ON d.type_id = dt.id
                JOIN system_categories sc ON d.category_id = sc.id
                WHERE m.name = ?
                LIMIT 3
            """, (manufacturer,))
            
            devices = cur.fetchall()
            
            for device in devices:
                device_id = device[0]
                device_name = device[1]
                device_model = device[2]
                device_type = device[3]
                device_category = device[4]
                
                print(f"  Linking: {device_name} ({device_model})")
                
                # Create block information based on device data
                block_name = device_model or device_name.replace(" ", "_").upper()
                block_path = f"Blocks/{manufacturer.upper()}_BLOCKS.dwg"
                
                # Create attributes mapping
                attributes = {
                    "PartNo": device_model,
                    "Manufacturer": manufacturer,
                    "Type": device_type,
                    "Category": device_category,
                    "Description": device_name
                }
                
                # Register the block
                block_id = register_block_for_device(con, device_id, block_name, block_path, attributes)
                print(f"    Registered block '{block_name}' with ID: {block_id}")
                
                # Verify the registration
                block_info = get_block_for_device(con, device_id)
                if block_info:
                    print(f"    Verified: {block_info['block_name']} -> {block_info['block_path']}")
        
        # Show some devices with their blocks
        print("\n=== Devices with Blocks ===")
        cur.execute("""
            SELECT d.name, m.name as manufacturer, cb.block_name, cb.block_path
            FROM devices d
            JOIN manufacturers m ON d.manufacturer_id = m.id
            LEFT JOIN cad_blocks cb ON d.id = cb.device_id
            WHERE cb.block_name IS NOT NULL
            ORDER BY d.name
            LIMIT 10
        """)
        
        linked_devices = cur.fetchall()
        for device in linked_devices:
            print(f"  {device[0]} by {device[1]} -> {device[2]} ({device[3]})")
            
        con.close()
        print("\n=== BLOCK LINKING DEMONSTRATION COMPLETE ===")
        
    except Exception as e:
        print(f"Error demonstrating block linking: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demonstrate_block_linking()