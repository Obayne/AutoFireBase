#!/usr/bin/env python3
"""
Script to demonstrate retrieving and using NFPA-compliant blocks.
"""

import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect, get_block_for_device

def demonstrate_nfpa_retrieval():
    """Demonstrate retrieving and using NFPA-compliant blocks."""
    print("Demonstrating NFPA block retrieval...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Get devices with NFPA blocks
        cur.execute("""
            SELECT d.id, d.name, m.name as manufacturer, cb.block_name, cb.block_attributes
            FROM devices d
            JOIN manufacturers m ON d.manufacturer_id = m.id
            JOIN cad_blocks cb ON d.id = cb.device_id
            WHERE cb.block_name LIKE 'NFPA_%'
            ORDER BY d.name
            LIMIT 10
        """)
        
        devices = cur.fetchall()
        print(f"Found {len(devices)} devices with NFPA blocks")
        print("\nSample devices with NFPA blocks:")
        
        for i, device in enumerate(devices, 1):
            device_id = device[0]
            device_name = device[1]
            manufacturer = device[2]
            block_name = device[3]
            block_attributes = json.loads(device[4]) if device[4] else {}
            
            print(f"\n{i}. {manufacturer} {device_name}")
            print(f"   Block: {block_name}")
            print(f"   NFPA Symbol: {block_attributes.get('nfpa_symbol', 'N/A')}")
            print(f"   Type: {block_attributes.get('type', 'N/A')}")
            print(f"   Subtype: {block_attributes.get('subtype', 'N/A')}")
            print(f"   Voltage: {block_attributes.get('voltage', 'N/A')}")
            
            # Demonstrate retrieving block information using the API
            block_info = get_block_for_device(con, device_id)
            if block_info:
                print(f"   Retrieved Block Path: {block_info['block_path']}")
                print(f"   Retrieved Attributes: {len(block_info['block_attributes'])} attributes")
        
        # Show how to get a specific device's block
        print("\n" + "="*50)
        print("DEMONSTRATING BLOCK RETRIEVAL FOR SPECIFIC DEVICE")
        print("="*50)
        
        # Get a specific device (first smoke detector)
        cur.execute("""
            SELECT d.id, d.name, m.name as manufacturer
            FROM devices d
            JOIN manufacturers m ON d.manufacturer_id = m.id
            JOIN cad_blocks cb ON d.id = cb.device_id
            WHERE cb.block_name = 'NFPA_SMOKE_DETECTOR'
            LIMIT 1
        """)
        
        smoke_detector = cur.fetchone()
        if smoke_detector:
            device_id = smoke_detector[0]
            device_name = smoke_detector[1]
            manufacturer = smoke_detector[2]
            
            print(f"Device: {manufacturer} {device_name}")
            
            # Retrieve block information
            block_info = get_block_for_device(con, device_id)
            if block_info:
                print(f"Block Name: {block_info['block_name']}")
                print(f"Block Path: {block_info['block_path']}")
                print("Block Attributes:")
                for key, value in block_info['block_attributes'].items():
                    print(f"  {key}: {value}")
            else:
                print("No block information found")
        
        con.close()
        print("\n=== NFPA BLOCK RETRIEVAL DEMONSTRATION COMPLETE ===")
        
    except Exception as e:
        print(f"Error demonstrating NFPA retrieval: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demonstrate_nfpa_retrieval()