#!/usr/bin/env python3
"""
Script to register NFPA-compliant blocks for ALL fire alarm devices.
"""

import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect, register_block_for_device, DB_DEFAULT

def register_all_nfpa_blocks():
    """Register NFPA-compliant blocks for all fire alarm devices."""
    print("Registering NFPA-compliant blocks for ALL fire alarm devices...")
    print(f"Using database: {DB_DEFAULT}")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Check if database has data
        cur.execute('SELECT COUNT(*) FROM devices')
        total_count = cur.fetchone()[0]
        print(f"Total devices in database: {total_count}")
        
        if total_count == 0:
            print("Database is empty. Please import data first.")
            return
            
        # Get all fire alarm devices without requiring device_types join
        cur.execute('''
            SELECT d.id, d.name, d.symbol, sc.name as category
            FROM devices d 
            JOIN system_categories sc ON d.category_id = sc.id 
            WHERE sc.name LIKE '%Fire%' OR sc.name LIKE '%Smoke%' OR sc.name LIKE '%Heat%' 
            OR sc.name LIKE '%Strobe%' OR sc.name LIKE '%Horn%' OR sc.name LIKE '%Speaker%'
            OR sc.name LIKE '%Manual%' OR sc.name LIKE '%Panel%' OR sc.name LIKE '%Control%'
        ''')
        devices = cur.fetchall()
        print(f"Found {len(devices)} fire alarm devices to register")
        
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
        
        registered_count = 0
        skipped_count = 0
        
        # Create a mapping of category keywords to NFPA block templates
        category_mapping = {
            'Smoke Detector': nfpa_blocks['Smoke Detector'],
            'Heat Detector': nfpa_blocks['Heat Detector'],
            'Manual Station': nfpa_blocks['Manual Station'],
            'Strobe': nfpa_blocks['Strobe'],
            'Horn/Strobe': nfpa_blocks['Horn/Strobe'],
            'Speaker': nfpa_blocks['Speaker'],
            'Fire Alarm Control Unit': nfpa_blocks['Fire Alarm Control Unit'],
            'Horn': nfpa_blocks['Horn/Strobe'],  # Map to Horn/Strobe
            'Notification Appliance': nfpa_blocks['Horn/Strobe'],  # Default to Horn/Strobe
            'Fire Alarm Panel': nfpa_blocks['Fire Alarm Control Unit'],
            'Control Panel': nfpa_blocks['Fire Alarm Control Unit'],
            'Voice Evac Control Unit': nfpa_blocks['Fire Alarm Control Unit'],
            'Multi Criteria Detector': nfpa_blocks['Smoke Detector'],  # Default to Smoke Detector
            'Air Sampling Detection': nfpa_blocks['Smoke Detector'],
            'Beam Detector': nfpa_blocks['Smoke Detector'],
            'Flame Detector': nfpa_blocks['Heat Detector'],  # Map to Heat Detector
            'Glass Break Detector': nfpa_blocks['Manual Station'],  # Map to Manual Station
            'Duct Smoke Detector': nfpa_blocks['Smoke Detector'],
            'Speaker/Strobe': nfpa_blocks['Horn/Strobe'],  # Map to Horn/Strobe
            'Smoke/Heat Detector': nfpa_blocks['Smoke Detector'],  # Default to Smoke Detector
            'Smoke/CO Detector': nfpa_blocks['Smoke Detector'],
            'Smoke/Heat/CO Detector': nfpa_blocks['Smoke Detector'],
            'Heat/CO Detector': nfpa_blocks['Heat Detector'],
            'Fire Fighter Interface': nfpa_blocks['Fire Alarm Control Unit'],
            'Mass Notificacation Interface': nfpa_blocks['Horn/Strobe'],
            'Emergency Visual': nfpa_blocks['Strobe'],
            'Beacon': nfpa_blocks['Strobe']
        }
        
        for device in devices:
            device_id = device[0]
            device_name = device[1]
            device_symbol = device[2]
            device_category = device[3]
            
            # Determine which NFPA block template to use
            block_template = None
            
            # First try to match by exact category name
            if device_category in category_mapping:
                block_template = category_mapping[device_category]
            else:
                # Try to match by partial category name
                for category_keyword, template in category_mapping.items():
                    if category_keyword in device_category:
                        block_template = template
                        break
            
            # If still no match, try to determine by device name keywords
            if not block_template:
                device_name_lower = device_name.lower()
                if 'smoke' in device_name_lower:
                    block_template = nfpa_blocks['Smoke Detector']
                elif 'heat' in device_name_lower:
                    block_template = nfpa_blocks['Heat Detector']
                elif 'pull' in device_name_lower or 'manual' in device_name_lower or 'station' in device_name_lower:
                    block_template = nfpa_blocks['Manual Station']
                elif 'strobe' in device_name_lower and 'horn' not in device_name_lower:
                    block_template = nfpa_blocks['Strobe']
                elif 'horn' in device_name_lower and 'strobe' in device_name_lower:
                    block_template = nfpa_blocks['Horn/Strobe']
                elif 'horn' in device_name_lower:
                    block_template = nfpa_blocks['Horn/Strobe']
                elif 'speaker' in device_name_lower:
                    block_template = nfpa_blocks['Speaker']
                elif 'panel' in device_name_lower or 'control' in device_name_lower or 'facp' in device_name_lower:
                    block_template = nfpa_blocks['Fire Alarm Control Unit']
                else:
                    # Print first 5 skipped devices for debugging
                    if skipped_count < 5:
                        print(f"  Skipping device with unknown type: {device_name} ({device_category})")
                    skipped_count += 1
                    continue
            
            if block_template:
                # Register the NFPA block for this device
                block_id = register_block_for_device(
                    con, 
                    device_id, 
                    block_template['block_name'], 
                    block_template['block_path'], 
                    block_template['attributes']
                )
                
                # Print progress for first 10 devices
                if registered_count < 10:
                    print(f"  Registered {block_template['block_name']} for {device_name}")
                
                # Print progress every 1000 devices
                if registered_count % 1000 == 0 and registered_count > 0:
                    print(f"  Registered {registered_count} devices...")
                
                registered_count += 1
        
        print(f"\n=== REGISTRATION COMPLETE ===")
        print(f"  Successfully registered: {registered_count} devices")
        print(f"  Skipped: {skipped_count} devices")
        print(f"  Total fire alarm devices: {len(devices)}")
        
        con.close()
        
    except Exception as e:
        print(f"Error registering NFPA blocks: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    register_all_nfpa_blocks()