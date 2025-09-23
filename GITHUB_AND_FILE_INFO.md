# GitHub Repository and File Information

## Repository Information
- **Repository Path**: c:\Dev\Autofire
- **Branch**: master
- **Latest Commit**: e662f2c - "Implement NFPA-compliant fire alarm block diagrams - Complete implementation of NFPA standards for fire alarm devices with SVG symbols and database integration"
- **Initial Commit**: b5266ea - "Initial commit: AutoFire CAD application with Excel import and build capabilities"

## GitHub Configuration
- **Workflows Directory**: [.github/workflows/](file://c:\Dev\Autofire\.github\workflows)
  - [ci.yml](file://c:\Dev\Autofire\.github\workflows\ci.yml) - Continuous Integration workflow
  - [labeler.yml](file://c:\Dev\Autofire\.github\workflows\labeler.yml) - Issue labeling workflow
  - [release.yml](file://c:\Dev\Autofire\.github\workflows\release.yml) - Release workflow

- **Issue Templates**: [.github/ISSUE_TEMPLATE/](file://c:\Dev\Autofire\.github\ISSUE_TEMPLATE)
  - [bug_report.md](file://c:\Dev\Autofire\.github\ISSUE_TEMPLATE\bug_report.md) - Bug report template
  - [feature_request.md](file://c:\Dev\Autofire\.github\ISSUE_TEMPLATE\feature_request.md) - Feature request template

- **Pull Request Template**: [.github/PULL_REQUEST_TEMPLATE.md](file://c:\Dev\Autofire\.github\PULL_REQUEST_TEMPLATE.md)

## Key Implementation Files

### Database Files
- [db/](file://c:\Dev\Autofire\db) - Database implementation directory
  - [db/loader.py](file://c:\Dev\Autofire\db\loader.py) - Main database loader with enhanced CAD block integration
  - [db/schema.py](file://c:\Dev\Autofire\db\schema.py) - Database schema definition
  - [db/fire_alarm_seeder.py](file://c:\Dev\Autofire\db\fire_alarm_seeder.py) - Fire alarm device seeder
  - [db/firelite_catalog.py](file://c:\Dev\Autofire\db\firelite_catalog.py) - FireLite device catalog

### NFPA Implementation Files
- [register_all_nfpa_blocks.py](file://c:\Dev\Autofire\register_all_nfpa_blocks.py) - Script to register NFPA blocks for all fire alarm devices
- [register_nfpa_blocks.py](file://c:\Dev\Autofire\register_nfpa_blocks.py) - Script to register sample NFPA blocks
- [identify_fire_alarm_devices.py](file://c:\Dev\Autofire\identify_fire_alarm_devices.py) - Script to identify fire alarm devices
- [demonstrate_block_linking.py](file://c:\Dev\Autofire\demonstrate_block_linking.py) - Demonstration of block linking
- [demonstrate_nfpa_retrieval.py](file://c:\Dev\Autofire\demonstrate_nfpa_retrieval.py) - Demonstration of NFPA block retrieval

### Documentation Files
- [NFPA_BLOCK_DIAGRAMS.md](file://c:\Dev\Autofire\NFPA_BLOCK_DIAGRAMS.md) - NFPA standards documentation
- [NFPA_IMPLEMENTATION_SUMMARY.md](file://c:\Dev\Autofire\NFPA_IMPLEMENTATION_SUMMARY.md) - Summary of NFPA implementation
- [BLOCK_IMPLEMENTATION_STATUS.md](file://c:\Dev\Autofire\BLOCK_IMPLEMENTATION_STATUS.md) - Status of block implementation
- [FIRE_ALARM_BLOCK_INTEGRATION.md](file://c:\Dev\Autofire\FIRE_ALARM_BLOCK_INTEGRATION.md) - Fire alarm block integration documentation

### Test Files
- [test_fire_alarm_nfpa.py](file://c:\Dev\Autofire\test_fire_alarm_nfpa.py) - NFPA implementation test
- [test_fetch_devices_with_blocks.py](file://c:\Dev\Autofire\test_fetch_devices_with_blocks.py) - Test for fetching devices with blocks
- [test_block_registration.py](file://c:\Dev\Autofire\test_block_registration.py) - Block registration test

### SVG Symbol Files
- [svg/](file://c:\Dev\Autofire\svg) - Directory containing SVG representations of NFPA symbols
  - [nfpa_smoke_detector.svg](file://c:\Dev\Autofire\svg\nfpa_smoke_detector.svg)
  - [nfpa_heat_detector.svg](file://c:\Dev\Autofire\svg\nfpa_heat_detector.svg)
  - [nfpa_manual_station.svg](file://c:\Dev\Autofire\svg\nfpa_manual_station.svg)
  - [nfpa_strobe.svg](file://c:\Dev\Autofire\svg\nfpa_strobe.svg)
  - [nfpa_horn_strobe.svg](file://c:\Dev\Autofire\svg\nfpa_horn_strobe.svg)
  - [nfpa_speaker.svg](file://c:\Dev\Autofire\svg\nfpa_speaker.svg)
  - [nfpa_facp.svg](file://c:\Dev\Autofire\svg\nfpa_facp.svg)
  - [nfpa_symbols_combined.svg](file://c:\Dev\Autofire\svg\nfpa_symbols_combined.svg)

### CAD Block Files
- [Blocks/](file://c:\Dev\Autofire\Blocks) - Directory containing DWG block files
  - [NFPA_SYMBOLS.dwg](file://c:\Dev\Autofire\Blocks\NFPA_SYMBOLS.dwg) - Placeholder DWG file with NFPA symbols
  - Various other DWG files from FireCad

## Configuration Files
- [.gitignore](file://c:\Dev\Autofire\.gitignore) - Git ignore file
- [.pre-commit-config.yaml](file://c:\Dev\Autofire\.pre-commit-config.yaml) - Pre-commit configuration
- [pyproject.toml](file://c:\Dev\Autofire\pyproject.toml) - Python project configuration
- [requirements.txt](file://c:\Dev\Autofire\requirements.txt) - Python dependencies
- [requirements-dev.txt](file://c:\Dev\Autofire\requirements-dev.txt) - Development dependencies

## Build Files
- [Build_AutoFire.ps1](file://c:\Dev\Autofire\Build_AutoFire.ps1) - Main build script
- [Build_AutoFire_Debug.ps1](file://c:\Dev\Autofire\Build_AutoFire_Debug.ps1) - Debug build script
- [Build_Clean.ps1](file://c:\Dev\Autofire\Build_Clean.ps1) - Clean build artifacts script
- [AutoFire.spec](file://c:\Dev\Autofire\AutoFire.spec) - PyInstaller spec file
- [AutoFire_Debug.spec](file://c:\Dev\Autofire\AutoFire_Debug.spec) - Debug PyInstaller spec file

## Excel Import Files
- [import_excel_to_db.py](file://c:\Dev\Autofire\import_excel_to_db.py) - Main Excel import script
- [simple_excel_import.py](file://c:\Dev\Autofire\simple_excel_import.py) - Simplified Excel import script
- [parse_excel.py](file://c:\Dev\Autofire\parse_excel.py) - Excel parsing utility
- [Database Export.xlsx](file://c:\Dev\Autofire\Database%20Export.xlsx) - FireCad database export
- [Device import.xlsx](file://c:\Dev\Autofire\Device%20import.xlsx) - Device import file

## Utility Scripts
- [populate_device_types.py](file://c:\Dev\Autofire\populate_device_types.py) - Script to populate device types
- [check_actual_device_types.py](file://c:\Dev\Autofire\check_actual_device_types.py) - Device type checking
- [check_fire_categories.py](file://c:\Dev\Autofire\check_fire_categories.py) - Fire category checking
- [debug_query.py](file://c:\Dev\Autofire\debug_query.py) - Database query debugging
- [diagnose_database.py](file://c:\Dev\Autofire\diagnose_database.py) - Database diagnostics

This structure represents a complete implementation of NFPA-compliant fire alarm block diagrams in the AutoFire CAD system, with all necessary files organized in a logical directory structure and integrated with GitHub workflows for CI/CD.