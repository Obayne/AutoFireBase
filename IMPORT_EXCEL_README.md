# Excel to Database Importer for AutoFire

This document explains how to use the Excel import script to populate the AutoFire device catalog database.

## Overview

The `import_excel_to_db.py` script reads device data from an Excel file and imports it into the AutoFire SQLite database. This allows you to populate your device catalog from spreadsheet data.

## Prerequisites

Make sure you have the required Python packages installed:

```bash
pip install pandas openpyxl
```

## Usage

### 1. Import an Excel file

```bash
python import_excel_to_db.py "Database Export.xlsx"
```

### 2. Import with specific sheet name

```bash
python import_excel_to_db.py "Database Export.xlsx" "Devices"
```

### 3. Create a sample template

```bash
python import_excel_to_db.py --template
```

This creates a `Device_Catalog_Template.xlsx` file that you can use as a starting point.

## Expected Excel Format

The script expects an Excel file with the following structure:

### Sheet Name
- Default: "Devices" (can be specified as second parameter)

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

## Example Data

| manufacturer | type | model | name | symbol | system_category | max_current_ma | voltage_v | slc_compatible | nac_compatible | addressable | candela_options |
|--------------|------|-------|------|--------|-----------------|----------------|-----------|----------------|----------------|-------------|-----------------|
| Generic | Detector | GEN-SD-1 | Smoke Detector | SD | Fire Alarm | 0.3 | 24.0 | TRUE | FALSE | TRUE | |
| Generic | Notification | GEN-HS-1 | Horn Strobe | HS | Fire Alarm | 3.5 | 24.0 | TRUE | TRUE | TRUE | 15,30,75,95,110,135,185 |
| Generic | Sensor | GEN-MD-1 | Motion Detector | MD | Security | 0.0 | 12.0 | FALSE | FALSE | FALSE | |

## Database Structure

The script populates the following database tables:

1. `manufacturers` - Device manufacturers
2. `device_types` - Device type codes and descriptions
3. `system_categories` - System categories (Fire Alarm, Security, etc.)
4. `devices` - Main device catalog
5. `fire_alarm_device_specs` - Fire alarm specific specifications

## Troubleshooting

### File Not Found
Make sure the Excel file path is correct and the file exists.

### Unknown Device Types
The script will warn about unknown device types and default to "Detector".

### Database Connection Issues
Ensure the database path is accessible. The database is located at `~/AutoFire/catalog.db`.

## Customization

You can modify the script to handle different Excel formats by adjusting:
- Sheet name parsing
- Column mapping
- Data validation and normalization