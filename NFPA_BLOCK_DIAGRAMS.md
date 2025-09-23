# NFPA-Compliant Fire Alarm Block Diagrams

## Overview
This document outlines the standard NFPA-compliant symbols and block diagrams for fire alarm system components. These symbols will be used to create professional, code-compliant block diagrams for fire alarm system layouts.

## Key Fire Alarm Device Categories

### 1. Initiating Devices

#### Smoke Detectors
- **Symbol**: Circle with "SMOKE" or "SD" inside
- **NFPA Standard**: Diamond shape with diagonal line
- **Attributes**: 
  - Addressable/Conventional
  - Photoelectric/Ionization
  - Voltage: 24V DC
  - Current: 0.3mA typical

#### Heat Detectors
- **Symbol**: Circle with "HEAT" or "HD" inside
- **NFPA Standard**: Diamond shape
- **Attributes**:
  - Fixed temperature/Rate-of-rise
  - Voltage: 24V DC
  - Current: 0.3mA typical

#### Manual Pull Stations
- **Symbol**: Rectangle with "PULL" or "MPS" inside
- **NFPA Standard**: Rectangle with specific labeling
- **Attributes**:
  - Single/Dual action
  - Voltage: 24V DC
  - Current: 0.1mA typical

#### Duct Detectors
- **Symbol**: Circle with "DUCT" inside
- **NFPA Standard**: Diamond with specific notation
- **Attributes**:
  - Air sampling type
  - Voltage: 24V DC

### 2. Notification Appliances

#### Strobes
- **Symbol**: Circle with "STROBE" or "S" inside
- **NFPA Standard**: Circle with specific candela rating
- **Attributes**:
  - Candela rating (15, 30, 75, 95, 110, 135, 185)
  - Voltage: 24V DC
  - Current: 2.0mA typical

#### Horns
- **Symbol**: Circle with "HORN" or "H" inside
- **NFPA Standard**: Circle with sound notation
- **Attributes**:
  - Decibel rating
  - Voltage: 24V DC
  - Current: 1.5mA typical

#### Horn/Strobes
- **Symbol**: Circle with "HS" inside
- **NFPA Standard**: Circle with combined notation
- **Attributes**:
  - Candela rating
  - Decibel rating
  - Voltage: 24V DC
  - Current: 3.5mA typical

#### Speakers
- **Symbol**: Circle with "SPK" or "SPEAKER" inside
- **NFPA Standard**: Circle with sound notation
- **Attributes**:
  - Wattage rating
  - Impedance
  - Voltage: 24V DC
  - Current: 1.0mA typical

### 3. Control Equipment

#### Fire Alarm Control Panels (FACP)
- **Symbol**: Rectangle with "FACP" inside
- **NFPA Standard**: Large rectangle with multiple connection points
- **Attributes**:
  - Number of loops
  - Number of addresses
  - NAC circuits
  - Voltage: 120V AC/24V DC

#### Notification Appliance Circuits (NAC)
- **Symbol**: Line with NAC designation
- **NFPA Standard**: Specific line styling
- **Attributes**:
  - Class A/Class B
  - Voltage: 24V DC
  - Current capacity

#### Signaling Line Circuits (SLC)
- **Symbol**: Line with SLC designation
- **NFPA Standard**: Specific line styling
- **Attributes**:
  - Class A/Class B
  - Addressable/Conventional
  - Voltage: 24V DC

## Block Diagram Standards

### Line Styles
- **SLC**: Heavy solid line
- **NAC**: Medium solid line
- **Power**: Light solid line
- **Ground**: Dashed line

### Connection Points
- **Terminal Strips**: Small circles
- **Device Connections**: Standard junction points
- **Loop Isolators**: Diamond shapes on SLC lines

### Annotation Standards
- **Device Addressing**: Numeric labels
- **Circuit Identification**: Alphabetic prefixes
- **Power Requirements**: Voltage/current specifications

## Implementation Plan

### Phase 1: Core Device Blocks
1. Smoke Detector block with NFPA symbol
2. Heat Detector block with NFPA symbol
3. Manual Pull Station block with NFPA symbol
4. Strobe block with candela rating
5. Horn/Strobe block with combined ratings
6. FACP block with connection points

### Phase 2: Circuit Representation
1. SLC line styling
2. NAC line styling
3. Power distribution representation
4. Grounding symbols

### Phase 3: Professional Layout Features
1. Title blocks with project information
2. Legend with device symbols
3. Scale indicators
4. North arrow

## Block Attributes for Database Integration

Each block will have the following attributes linked to the database:

### Smoke Detector
```json
{
  "symbol": "SD",
  "nfpa_symbol": "Diamond with diagonal",
  "type": "Detector",
  "subtype": "Smoke",
  "technology": "Photoelectric/Ionization",
  "voltage": "24V DC",
  "current": "0.3mA",
  "addressable": true,
  "mounting": "Ceiling/Wall"
}
```

### Horn/Strobe
```json
{
  "symbol": "HS",
  "nfpa_symbol": "Circle with combined notation",
  "type": "Notification",
  "subtype": "Horn/Strobe",
  "candela": "15-185",
  "decibels": "85-95",
  "voltage": "24V DC",
  "current": "3.5mA",
  "mounting": "Ceiling/Wall"
}
```

### FACP
```json
{
  "symbol": "FACP",
  "nfpa_symbol": "Large rectangle",
  "type": "Control",
  "subtype": "Fire Alarm Control Panel",
  "loops": "1-4",
  "addresses": "1000 max",
  "nac_circuits": "4 Class B",
  "voltage": "120V AC/24V DC",
  "mounting": "Wall/Cabinet"
}
```

## Next Steps

1. Create SVG representations of NFPA-compliant symbols
2. Implement block registration for key fire alarm devices
3. Develop circuit drawing capabilities
4. Create professional layout templates
5. Integrate with existing database attributes

This approach will ensure that AutoFire produces code-compliant, professional fire alarm system layouts that meet NFPA standards while maintaining the creative flexibility for other system types.