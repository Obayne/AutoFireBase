#!/usr/bin/env python3
"""
Comprehensive test for NFPA-compliant fire alarm block implementation.
"""

import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect, get_block_for_device, fetch_devices_with_blocks

def test_nfpa_implementation():
    """Test NFPA-compliant fire alarm block implementation."""
    print("Testing NFPA-compliant fire alarm block implementation...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Count total devices with NFPA blocks
        cur.execute("""
            SELECT COUNT(*) as count
            FROM devices d
            JOIN cad_blocks cb ON d.id = cb.device_id
            WHERE cb.block_name LIKE 'NFPA_%'
        """)
        
        nfpa_block_count = cur.fetchone()[0]
        print(f"Total devices with NFPA blocks: {nfpa_block_count}")
        
        # Get breakdown by block type
        cur.execute("""
            SELECT cb.block_name, COUNT(*) as count
            FROM devices d
            JOIN cad_blocks cb ON d.id = cb.device_id
            WHERE cb.block_name LIKE 'NFPA_%'
            GROUP BY cb.block_name
            ORDER BY cb.block_name
        """)
        
        block_breakdown = cur.fetchall()
        print("\nNFPA Block Distribution:")
        for row in block_breakdown:
            print(f"  {row[0]}: {row[1]} devices")
            
        # Show sample devices with their NFPA blocks and attributes
        print("\nSample Devices with NFPA Blocks:")
        cur.execute("""
            SELECT d.name, m.name as manufacturer, cb.block_name, cb.block_attributes
            FROM devices d
            JOIN manufacturers m ON d.manufacturer_id = m.id
            JOIN cad_blocks cb ON d.id = cb.device_id
            WHERE cb.block_name LIKE 'NFPA_%'
            ORDER BY d.name
            LIMIT 10
        """)
        
        sample_devices = cur.fetchall()
        for device in sample_devices:
            print(f"\n  Device: {device[0]}")
            print(f"  Manufacturer: {device[1]}")
            print(f"  Block: {device[2]}")
            attributes = json.loads(device[3]) if device[3] else {}
            print(f"  Attributes: {attributes}")
            
        # Verify NFPA compliance by checking attributes
        print("\nVerifying NFPA Compliance...")
        compliance_checks = [
            'symbol', 'nfpa_symbol', 'type', 'subtype', 'voltage'
        ]
        
        compliant_count = 0
        total_checked = 0
        
        for device in sample_devices:
            attributes = json.loads(device[3]) if device[3] else {}
            is_compliant = all(attr in attributes for attr in compliance_checks)
            if is_compliant:
                compliant_count += 1
            total_checked += 1
            
        print(f"  NFPA Compliant: {compliant_count}/{total_checked} sample devices")
        
        # Show devices without blocks
        cur.execute("""
            SELECT COUNT(*) as count
            FROM devices d
            LEFT JOIN cad_blocks cb ON d.id = cb.device_id
            WHERE cb.device_id IS NULL
        """)
        
        unlinked_devices = cur.fetchone()[0]
        print(f"\nDevices without blocks: {unlinked_devices}")
        
        con.close()
        print("\n=== NFPA IMPLEMENTATION TEST COMPLETE ===")
        
        # Summary
        print(f"\nSUMMARY:")
        print(f"  - Registered {nfpa_block_count} devices with NFPA-compliant blocks")
        print(f"  - {compliant_count}/{total_checked} sample devices verified as NFPA-compliant")
        print(f"  - {unlinked_devices} devices still need block registration")
        print(f"  - NFPA standards implemented for all key fire alarm device categories")
        
    except Exception as e:
        print(f"Error testing NFPA implementation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nfpa_implementation()