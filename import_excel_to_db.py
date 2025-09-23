#!/usr/bin/env python3
"""
Script to import device data from Excel file to AutoFire database.

This script reads an Excel file containing fire alarm and security device data
and imports it into the AutoFire SQLite database.

Expected Excel format:
- Sheet name: "Devices" (or configurable)
- Columns should include:
  - manufacturer: Device manufacturer name
  - type: Device type code (Detector, Notification, Initiating, Control, Sensor, Camera, Recorder)
  - model: Model/part number
  - name: Device display name
  - symbol: CAD symbol abbreviation
  - system_category: Fire Alarm, Security, CCTV, Access Control
  - part_number: (optional, same as model)
  - max_current_ma: (optional) Maximum current in milliamps
  - voltage_v: (optional) Operating voltage
  - slc_compatible: (optional) True/False
  - nac_compatible: (optional) True/False
  - addressable: (optional) True/False
  - candela_options: (optional) Comma-separated list of candela values
"""

import os
import sys
import sqlite3
import json
import pandas as pd
import openpyxl
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect, ensure_schema

def normalize_boolean(value):
    """Convert various boolean representations to Python boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'y', 't')
    if isinstance(value, (int, float)):
        return bool(value)
    return False

def parse_candela_options(value):
    """Parse candela options from string to list of integers."""
    if not value:
        return []
    if isinstance(value, list):
        return [int(x) for x in value if x]
    if isinstance(value, str):
        # Split by comma and convert to integers
        return [int(x.strip()) for x in str(value).split(',') if x.strip().isdigit()]
    return []

def import_excel_to_database(excel_file_path, sheet_name='Devices'):
    """
    Import device data from Excel file to database.
    
    Args:
        excel_file_path (str): Path to the Excel file
        sheet_name (str): Name of the sheet containing device data
    """
    print(f"Importing data from: {excel_file_path}")
    
    # Check if file exists
    if not os.path.exists(excel_file_path):
        print(f"Error: File not found: {excel_file_path}")
        return False
    
    # Read Excel file
    try:
        print("Reading Excel file...")
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        print(f"Found {len(df)} rows in sheet '{sheet_name}'")
        print(f"Columns: {list(df.columns)}")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False
    
    # Connect to database
    try:
        print("Connecting to database...")
        con = connect()
        ensure_schema(con)
        cur = con.cursor()
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False
    
    # Import data
    imported_count = 0
    error_count = 0
    
    for index, row in df.iterrows():
        try:
            # Extract required fields
            manufacturer = row.get('manufacturer', '(Unknown)')
            device_type = row.get('type', 'Detector')
            model = row.get('model', row.get('part_number', ''))
            name = row.get('name', 'Unknown Device')
            symbol = row.get('symbol', '')
            system_category = row.get('system_category', 'Fire Alarm')
            
            # Handle missing model
            if not model:
                model = f"{manufacturer}-{symbol}"
            
            # Insert or get manufacturer ID
            cur.execute("INSERT OR IGNORE INTO manufacturers(name) VALUES(?)", (manufacturer,))
            cur.execute("SELECT id FROM manufacturers WHERE name=?", (manufacturer,))
            manufacturer_id = cur.fetchone()[0]
            
            # Get or verify device type ID
            cur.execute("SELECT id FROM device_types WHERE code=?", (device_type,))
            type_row = cur.fetchone()
            if not type_row:
                print(f"Warning: Unknown device type '{device_type}' in row {index+1}. Using 'Detector' instead.")
                device_type = 'Detector'
                cur.execute("SELECT id FROM device_types WHERE code=?", (device_type,))
                type_row = cur.fetchone()
            type_id = type_row[0]
            
            # Insert or get system category ID
            cur.execute("INSERT OR IGNORE INTO system_categories(name) VALUES(?)", (system_category,))
            cur.execute("SELECT id FROM system_categories WHERE name=?", (system_category,))
            category_row = cur.fetchone()
            category_id = category_row[0] if category_row else None
            
            # Insert device
            cur.execute("""
                INSERT INTO devices(manufacturer_id, type_id, category_id, model, name, symbol, properties_json) 
                VALUES(?,?,?,?,?,?,?)""",
                (manufacturer_id, type_id, category_id, model, name, symbol, json.dumps({}))
            )
            device_id = cur.lastrowid
            
            # Handle fire alarm specific specs
            if system_category == 'Fire Alarm':
                max_current_ma = float(row.get('max_current_ma', 0.0) or 0.0)
                voltage_v = float(row.get('voltage_v', 24.0) or 24.0)
                slc_compatible = normalize_boolean(row.get('slc_compatible', True))
                nac_compatible = normalize_boolean(row.get('nac_compatible', True))
                addressable = normalize_boolean(row.get('addressable', True))
                candela_options = parse_candela_options(row.get('candela_options', ''))
                candela_json = json.dumps(candela_options) if candela_options else None
                
                cur.execute("""
                    INSERT OR REPLACE INTO fire_alarm_device_specs 
                    (device_id, device_class, max_current_ma, voltage_v, slc_compatible, nac_compatible, addressable, candela_options)
                    VALUES(?,?,?,?,?,?,?,?)""",
                    (device_id, device_type, max_current_ma, voltage_v, slc_compatible, nac_compatible, addressable, candela_json)
                )
            
            imported_count += 1
            if imported_count % 50 == 0:
                print(f"Imported {imported_count} devices...")
                
        except Exception as e:
            print(f"Error importing row {index+1}: {e}")
            error_count += 1
            continue
    
    # Commit changes
    con.commit()
    con.close()
    
    print(f"Import completed. Successfully imported: {imported_count}, Errors: {error_count}")
    return error_count == 0

def create_sample_excel_template(output_file='Device_Catalog_Template.xlsx'):
    """Create a sample Excel template for device data."""
    print(f"Creating sample Excel template: {output_file}")
    
    # Sample data
    sample_data = [
        {
            'manufacturer': 'Generic',
            'type': 'Detector',
            'model': 'GEN-SD-1',
            'name': 'Smoke Detector',
            'symbol': 'SD',
            'system_category': 'Fire Alarm',
            'max_current_ma': 0.3,
            'voltage_v': 24.0,
            'slc_compatible': True,
            'nac_compatible': False,
            'addressable': True,
            'candela_options': ''
        },
        {
            'manufacturer': 'Generic',
            'type': 'Notification',
            'model': 'GEN-HS-1',
            'name': 'Horn Strobe',
            'symbol': 'HS',
            'system_category': 'Fire Alarm',
            'max_current_ma': 3.5,
            'voltage_v': 24.0,
            'slc_compatible': True,
            'nac_compatible': True,
            'addressable': True,
            'candela_options': '15,30,75,95,110,135,185'
        },
        {
            'manufacturer': 'Generic',
            'type': 'Sensor',
            'model': 'GEN-MD-1',
            'name': 'Motion Detector',
            'symbol': 'MD',
            'system_category': 'Security',
            'max_current_ma': 0.0,
            'voltage_v': 12.0,
            'slc_compatible': False,
            'nac_compatible': False,
            'addressable': False,
            'candela_options': ''
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Write to Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Devices', index=False)
    
    print("Sample template created successfully!")

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
        sheet_name = sys.argv[2] if len(sys.argv) > 2 else 'Devices'
        
        if excel_file == '--template':
            create_sample_excel_template()
        else:
            import_excel_to_database(excel_file, sheet_name)
    else:
        print("Usage:")
        print("  python import_excel_to_db.py <excel_file> [sheet_name]")
        print("  python import_excel_to_db.py --template")
        print("\nIf no arguments provided, will try to import 'Database Export.xlsx'")
        
        # Default file
        default_file = r"c:\Dev\Autofire\Database Export.xlsx"
        if os.path.exists(default_file):
            import_excel_to_database(default_file)
        else:
            print(f"Default file not found: {default_file}")
            create_sample_excel_template()