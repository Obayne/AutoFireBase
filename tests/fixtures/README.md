# Test Fixtures

This directory contains test files for automated testing and validation.

## Structure

```
tests/fixtures/
├── dxf/              # DXF test files (fire protection floorplans)
├── autofire/         # .autofire project test files
└── pdf/              # PDF underlay test files
```

## DXF Test Files (`tests/fixtures/dxf/`)

**Purpose**: Real-world fire protection floorplans for testing Layer Intelligence and device detection.

**Required Test Cases**:
- `simple_office.dxf` - Small office with basic fire devices (smoke detectors, pull stations)
- `commercial_building.dxf` - Multi-room commercial space with comprehensive fire protection
- `warehouse.dxf` - Large open space with sprinkler system
- `multi_floor.dxf` - Multi-story building with stacked systems
- `edge_cases.dxf` - Complex layer naming, unusual device blocks, stress test

**Layer Naming Conventions to Test**:
- Standard: `FP-DEVICES`, `FP-WIRING`, `FIRE-ALARM`
- Variations: `E-FIRE-SMOK`, `E-FIRE-DEVICES`, `A-FIRE-PROT`
- Edge cases: `fire`, `FA`, `SMOKE_DET`, etc.

**What to Include in Each File**:
- Smoke detectors (ceiling and wall mounted)
- Manual pull stations
- Horn/strobes
- Heat detectors
- Sprinkler heads
- Control panels
- Wiring/conduit paths
- Room labels/numbers
- Architectural context (walls, doors)

## AutoFire Project Files (`tests/fixtures/autofire/`)

**Purpose**: Test project serialization, save/load, and backward compatibility.

**Test Cases**:
- `minimal.autofire` - Empty project with default settings
- `basic_devices.autofire` - Project with a few placed devices
- `full_project.autofire` - Complete project with devices, wiring, coverage overlays
- `legacy_v0.4.autofire` - Older format for migration testing

## PDF Files (`tests/fixtures/pdf/`)

**Purpose**: Test PDF underlay import and rendering.

**Test Cases**:
- `simple_floorplan.pdf` - Basic architectural drawing
- `scaled_drawing.pdf` - Known scale for calibration testing
- `multi_page.pdf` - Multiple sheets

## Usage in Tests

```python
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
DXF_DIR = FIXTURES_DIR / "dxf"

def test_dxf_import():
    test_file = DXF_DIR / "simple_office.dxf"
    # Use test_file in your test
```

## Adding New Fixtures

1. **Place file** in appropriate subdirectory
2. **Document** what it tests in this README
3. **Add test** that uses the fixture
4. **Keep files small** (<1MB if possible)
5. **Use realistic data** (real layer names, typical device counts)

## Fixture Requirements

**DXF Files MUST Include**:
- Valid DXF format (AutoCAD 2018 or compatible)
- At least one fire protection layer
- Device blocks with meaningful names
- Room/space labels
- Realistic coordinates and scale

**AutoFire Project Files MUST**:
- Be valid JSON inside ZIP container
- Include `project.json` at root
- Test specific serialization features

## Integration with CI

- Automated analysis runs on all DXF fixtures daily
- Reports generated in `docs/analysis/`
- Validates Layer Intelligence accuracy
- Tracks performance benchmarks

## Do NOT Commit

- Real client projects (privacy)
- Files >5MB (use external storage)
- Proprietary drawings (copyright)
- Personal/sensitive data

Use synthetic test data or anonymized samples only.
