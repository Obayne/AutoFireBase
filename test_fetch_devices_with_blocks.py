#!/usr/bin/env python3
"""
Script to test the fetch_devices_with_blocks function.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect, fetch_devices_with_blocks

def test_fetch_devices_with_blocks():
    """Test the fetch_devices_with_blocks function."""
    print("Testing fetch_devices_with_blocks function...")
    
    try:
        con = connect()
        devices = fetch_devices_with_blocks(con)
        print(f"Total devices with blocks: {len(devices)}")
        
        print("First 10 devices with blocks:")
        for i, device in enumerate(devices[:10]):
            block_name = device.get('block_name', 'None')
            print(f"  {i+1}. {device['name']} - Block: {block_name}")
        
        # Count devices with NFPA blocks specifically
        nfpa_devices = [d for d in devices if d.get('block_name') and d.get('block_name', '').startswith('NFPA_')]
        print(f"\nDevices with NFPA blocks: {len(nfpa_devices)}")
        
        print("First 5 NFPA devices:")
        for i, device in enumerate(nfpa_devices[:5]):
            print(f"  {i+1}. {device['name']} - Block: {device['block_name']}")
        
        con.close()
        print("\n=== FETCH_DEVICES_WITH_BLOCKS TEST COMPLETE ===")
        
    except Exception as e:
        print(f"Error testing fetch_devices_with_blocks: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fetch_devices_with_blocks()