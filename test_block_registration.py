#!/usr/bin/env python3
"""
Script to test block registration functionality.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect, register_block_for_device, get_block_for_device, fetch_devices_with_blocks

def test_block_registration():
    """Test block registration functionality."""
    print("Testing block registration functionality...")
    
    try:
        con = connect()
        
        # Get a sample device ID
        cur = con.cursor()
        cur.execute("SELECT id FROM devices LIMIT 1")
        row = cur.fetchone()
        
        if row:
            device_id = row[0]
            print(f"Using device ID: {device_id}")
            
            # Register a block for this device
            block_name = "SMOKE_DETECTOR"
            block_path = "Blocks/DEVICE DETAILBLOCKS.dwg"
            attributes = {
                "PartNo": "C2M-PD1",
                "Manufacturer": "Edwards",
                "Type": "Smoke Detector"
            }
            
            block_id = register_block_for_device(con, device_id, block_name, block_path, attributes)
            print(f"Registered block with ID: {block_id}")
            
            # Retrieve the block information
            block_info = get_block_for_device(con, device_id)
            if block_info:
                print(f"Retrieved block info: {block_info}")
            else:
                print("No block info found for device")
                
            # Test fetching devices with blocks
            print("\nFetching devices with blocks (first 5):")
            devices_with_blocks = fetch_devices_with_blocks(con)
            for i, device in enumerate(devices_with_blocks[:5]):
                print(f"  {i+1}. {device['name']} - Block: {device['block_name'] or 'None'}")
                
        else:
            print("No devices found in database")
            
        con.close()
        print("\n=== BLOCK REGISTRATION TEST COMPLETE ===")
        
    except Exception as e:
        print(f"Error testing block registration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_block_registration()