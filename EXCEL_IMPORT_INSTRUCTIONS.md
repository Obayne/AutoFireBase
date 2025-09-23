# Excel Database Import Instructions

This document provides instructions on how to import device data from Excel files into the AutoFire database.

## Overview

The AutoFire application uses a SQLite database to store device catalog information. This guide explains how to populate that database using Excel spreadsheet data.

## Provided Scripts

Two scripts have been created to help with Excel import:

1. `import_excel_to_db.py` - Full-featured script using pandas and openpyxl
2. `simple_excel_import.py` - Simplified script using only openpyxl

## Prerequisites

Before using either script, ensure you have the required Python packages installed:

```bash
pip install pandas openpyxl
```

Or for the simple version:

```bash
pip install openpyxl
```

## Expected Excel Format

The scripts expect an Excel file with the following structure:

### Sheet Name
- Default: "Devices" (can be specified as a parameter)

### Required Columns
- `manufacturer`: Device manufacturer name (e.g., "System Sensor", "Notifier")
- `type`: Device type code (Detector, Notification, Initiating, Control, Sensor, Camera, Recorder)
- `model`: Model/part number
- `name`: Device display name
- `symbol`: CAD symbol abbreviation (e.g., "SD", "HS", "MD")
- `system_category`: Fire Alarm, Security, CCTV, Access Control

### Optional Columns (Fire Alarm Specific)
- `max_current_ma`: Maximum current in milliamps
- `voltage_v`: Operating voltage
- `slc_compatible`: True/False for Signaling Line Circuit compatibility
- `nac_compatible`: True/False for Notification Appliance Circuit compatibility
- `addressable`: True/False for addressable devices
- `candela_options`: Comma-separated list of candela values (for strobes)

## Usage

### Using the Full-Featured Script

```bash
# Import the default Excel file
python import_excel_to_db.py

# Import a specific Excel file
python import_excel_to_db.py "Database Export.xlsx"

# Import with specific sheet name
python import_excel_to_db.py "Database Export.xlsx" "Devices"

# Create a sample template
python import_excel_to_db.py --template
```

### Using the Simple Script

```bash
# Import the default Excel file
python simple_excel_import.py

# Import a specific Excel file
python simple_excel_import.py "Database Export.xlsx"

# Import with specific sheet name
python simple_excel_import.py "Database Export.xlsx" "Devices"
```

## Database Structure

The import scripts populate the following database tables:

1. `manufacturers` - Device manufacturers
2. `device_types` - Device type codes and descriptions
3. `system_categories` - System categories (Fire Alarm, Security, etc.)
4. `devices` - Main device catalog
5. `fire_alarm_device_specs` - Fire alarm specific specifications

## Troubleshooting

### File Not Found
- Ensure the Excel file path is correct
- Use absolute paths if relative paths don't work
- Check file permissions

### Unknown Device Types
- The script will warn about unknown device types and default to "Detector"
- Valid device types: Detector, Notification, Initiating, Control, Sensor, Camera, Recorder

### Database Connection Issues
- The database is located at `~/AutoFire/catalog.db`
- Ensure the directory is writable
- Check if the database file is locked by another process

## Example Data Format

| manufacturer | type | model | name | symbol | system_category | max_current_ma | voltage_v | slc_compatible | nac_compatible | addressable | candela_options |
|--------------|------|-------|------|--------|-----------------|----------------|-----------|----------------|----------------|-------------|-----------------|
| Generic | Detector | GEN-SD-1 | Smoke Detector | SD | Fire Alarm | 0.3 | 24.0 | TRUE | FALSE | TRUE | |
| Generic | Notification | GEN-HS-1 | Horn Strobe | HS | Fire Alarm | 3.5 | 24.0 | TRUE | TRUE | TRUE | 15,30,75,95,110,135,185 |
| Generic | Sensor | GEN-MD-1 | Motion Detector | MD | Security | 0.0 | 12.0 | FALSE | FALSE | FALSE | |

## Customization

Both scripts can be modified to handle different Excel formats:

1. Adjust sheet name parsing
2. Modify column mapping
3. Add data validation and normalization
4. Handle different data types

## Verification

After importing, you can verify the data was imported correctly by:

1. Running the AutoFire application
2. Checking if devices appear in the catalog
3. Verifying device properties in the database directly using SQLite tools

## Support

If you encounter issues with the import process:

1. Check the console output for error messages
2. Verify the Excel file format matches the expected structure
3. Ensure all required Python packages are installed
4. Check database file permissions