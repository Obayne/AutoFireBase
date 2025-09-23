#!/usr/bin/env python3
"""
Script to register NFPA-compliant blocks for key fire alarm devices.
"""

import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect, register_block_for_device

def register_nfpa_blocks():
    """Register NFPA-compliant blocks for key fire alarm devices."""
    print("Registering NFPA-compliant blocks for fire alarm devices...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Define NFPA block templates for key device categories
        nfpa_blocks = {
            'Smoke Detector': {
                'block_name': 'NFPA_SMOKE_DETECTOR',
                'block_path': 'Blocks/NFPA_SYMBOLS.dwg',
                'attributes': {
                    'symbol': 'SD',
                    'nfpa_symbol': 'Diamond with diagonal',
                    'type': 'Detector',
                    'subtype': 'Smoke',
                    'technology': 'Photoelectric/Ionization',
                    'voltage': '24V DC',
                    'current': '0.3mA',
                    'addressable': True,
                    'mounting': 'Ceiling/Wall'
                }
            },
            'Heat Detector': {
                'block_name': 'NFPA_HEAT_DETECTOR',
                'block_path': 'Blocks/NFPA_SYMBOLS.dwg',
                'attributes': {
                    'symbol': 'HD',
                    'nfpa_symbol': 'Diamond',
                    'type': 'Detector',
                    'subtype': 'Heat',
                    'technology': 'Fixed Temperature/Rate-of-rise',
                    'voltage': '24V DC',
                    'current': '0.3mA',
                    'addressable': True,
                    'mounting': 'Ceiling/Wall'
                }
            },
            'Manual Station': {
                'block_name': 'NFPA_MANUAL_STATION',
                'block_path': 'Blocks/NFPA_SYMBOLS.dwg',
                'attributes': {
                    'symbol': 'MPS',
                    'nfpa_symbol': 'Rectangle',
                    'type': 'Initiating',
                    'subtype': 'Manual Station',
                    'action': 'Single/Dual',
                    'voltage': '24V DC',
                    'current': '0.1mA',
                    'addressable': True,
                    'mounting': 'Wall'
                }
            },
            'Strobe': {
                'block_name': 'NFPA_STROBE',
                'block_path': 'Blocks/NFPA_SYMBOLS.dwg',
                'attributes': {
                    'symbol': 'S',
                    'nfpa_symbol': 'Circle',
                    'type': 'Notification',
                    'subtype': 'Strobe',
                    'candela': '15-185',
                    'voltage': '24V DC',
                    'current': '2.0mA',
                    'addressable': True,
                    'mounting': 'Ceiling/Wall'
                }
            },
            'Horn/Strobe': {
                'block_name': 'NFPA_HORN_STROBE',
                'block_path': 'Blocks/NFPA_SYMBOLS.dwg',
                'attributes': {
                    'symbol': 'HS',
                    'nfpa_symbol': 'Circle with combined notation',
                    'type': 'Notification',
                    'subtype': 'Horn/Strobe',
                    'candela': '15-185',
                    'decibels': '85-95',
                    'voltage': '24V DC',
                    'current': '3.5mA',
                    'addressable': True,
                    'mounting': 'Ceiling/Wall'
                }
            },
            'Speaker': {
                'block_name': 'NFPA_SPEAKER',
                'block_path': 'Blocks/NFPA_SYMBOLS.dwg',
                'attributes': {
                    'symbol': 'SPK',
                    'nfpa_symbol': 'Circle with sound notation',
                    'type': 'Notification',
                    'subtype': 'Speaker',
                    'wattage': '15W',
                    'impedance': '8Ω',
                    'voltage': '24V DC',
                    'current': '1.0mA',
                    'addressable': True,
                    'mounting': 'Ceiling/Wall'
                }
            },
            'Fire Alarm Control Unit': {
                'block_name': 'NFPA_FACP',
                'block_path': 'Blocks/NFPA_SYMBOLS.dwg',
                'attributes': {
                    'symbol': 'FACP',
                    'nfpa_symbol': 'Large rectangle',
                    'type': 'Control',
                    'subtype': 'Fire Alarm Control Panel',
                    'loops': '1-4',
                    'addresses': '1000 max',
                    'nac_circuits': '4 Class B',
                    'voltage': '120V AC/24V DC',
                    'mounting': 'Wall/Cabinet'
                }
            }
        }
        
        # Register blocks for sample devices in each category
        registered_count = 0
        
        for category, block_info in nfpa_blocks.items():
            print(f"\nRegistering blocks for {category}...")
            
            # Get sample devices for this category
            cur.execute("""
                SELECT d.id, d.name, d.symbol, m.name as manufacturer
                FROM devices d
                JOIN system_categories sc ON d.category_id = sc.id
                JOIN manufacturers m ON d.manufacturer_id = m.id
                WHERE sc.name = ?
                LIMIT 5
            """, (category,))
            
            devices = cur.fetchall()
            
            for device in devices:
                device_id = device[0]
                device_name = device[1]
                device_symbol = device[2]
                manufacturer = device[3]
                
                # Register the NFPA block for this device
                block_id = register_block_for_device(
                    con, 
                    device_id, 
                    block_info['block_name'], 
                    block_info['block_path'], 
                    block_info['attributes']
                )
                
                print(f"  Registered {block_info['block_name']} for {manufacturer} {device_name}")
                registered_count += 1
                
        print(f"\n=== REGISTERED {registered_count} NFPA BLOCKS ===")
        con.close()
        
    except Exception as e:
        print(f"Error registering NFPA blocks: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    register_nfpa_blocks()