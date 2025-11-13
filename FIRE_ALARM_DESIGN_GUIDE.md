# LV CAD - NFPA 72 Compliant Fire Alarm System Design Tool

## Overview

LV CAD is a professional CAD application for designing NFPA 72 compliant fire alarm systems. It provides real engineering calculations for device placement, wiring, and power requirements.

## Key Features

- **Real NFPA 72 Calculations**: Device spacing, coverage analysis, and occupancy factors
- **Electrical Engineering**: Voltage drop, wire sizing per NEC, battery calculations
- **CAD Interface**: Modern PySide6 GUI with drawing tools and device placement
- **System Builder**: Automated design generation with procurement lists

## System Design Process

### 1. Building Parameters

- Total area (sq ft)
- Number of stories
- Occupancy type (Business, Residential, Healthcare, etc.)

### 2. Device Requirements (NFPA 72)

- Smoke detectors: Based on area and spacing requirements
- Heat detectors: For areas where smoke detection is inappropriate
- Manual stations: Per floor and exit requirements
- Notification appliances: Horns/strobes per coverage area

### 3. Electrical Calculations (NEC)

- Circuit design: Primary, SLC, NAC circuits
- Wire sizing: Based on current draw and voltage drop limits
- Conduit sizing: Per conductor count and installation method
- Power supply: Primary and battery backup requirements

### 4. Installation & Testing

- Cable spool lists with quantities and lengths
- Conduit requirements
- Testing procedures per NFPA 72

## Usage Guide

### Starting a New Design

1. Open the System Builder dock
2. Enter building parameters:
   - Total area
   - Stories
   - Occupancy type
3. Click "Design System" to generate device requirements
4. Click "Calculate Wiring" for electrical design
5. Click "Generate Wire Spool" for installation materials

### Device Placement

1. Select devices from the device palette
2. Click in the model space to place devices
3. Use CAD tools for drawing walls, conduits, etc.
4. System validates placement against NFPA requirements

## NFPA 72 Compliance

### Device Spacing

- Smoke detectors: 30 ft spacing, 21 ft from walls
- Heat detectors: 50 ft spacing for ordinary hazards
- Strobes: 15 ft mounting height, 75 cd minimum
- Speakers: 10 ft mounting height, 2-8 W power

### Coverage Requirements

- 100% coverage for life safety areas
- Spacing reductions allowed for smooth ceilings
- Obstruction considerations per NFPA 72

### Power Requirements

- Primary power: 2 hours minimum
- Battery backup: 24 hours for emergency systems
- Voltage drop: Maximum 10% for notification circuits

## Installation Standards

### Wiring Methods

- Fire alarm cable: FPLR, FPLP, FPL
- Conduit: EMT, RMC per NEC 300.22
- Grounding: Per NEC 250.118

### Testing Requirements

- Circuit testing: Continuity, insulation, ground
- Device testing: Sensitivity, operation
- System testing: Full functional test

## Troubleshooting

### Common Issues

- **App won't start**: Ensure PySide6 is installed, check QApplication initialization
- **Syntax errors**: Check for Unicode characters in f-strings
- **Tool not working**: Ensure _initialize_tools() has been called
- **SystemBuilder errors**: Check building parameters are valid

### Error Messages

- `QWidget: Must construct a QApplication before a QWidget`: Import order issue
- `AttributeError: 'DrawController' object has no attribute 'select_tool'`: Missing method
- `SyntaxError: invalid syntax`: Check quotes in strings

## Development

### Architecture

- `app/system_builder.py`: Core engineering calculations
- `app/model_space_window.py`: CAD interface and UI
- `app/app_controller.py`: Application coordination
- `app/tools/`: CAD drawing tools

### Adding New Features

1. Implement calculations in SystemBuilder
2. Add UI controls to model_space_window.py
3. Connect signals and update display
4. Test with real NFPA scenarios

### Testing

- Unit tests in `tests/` directory
- Integration tests for full system design
- Validation against NFPA 72 requirements

## References

- NFPA 72: National Fire Alarm and Signaling Code
- NEC: National Electrical Code (NFPA 70)
- UL Standards for fire alarm equipment
- Manufacturer installation manuals

## Support

For questions about fire alarm system design or NFPA compliance, consult:

- Local Authority Having Jurisdiction (AHJ)
- Fire protection engineer
- NFPA technical committees
