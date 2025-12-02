# File Format Conversion Guide

AutoFire now supports **unified multi-format conversion** for all CAD workflows.

## Supported Formats

### Input Formats

- **DXF** (.dxf) - AutoCAD Drawing Exchange Format
- **DWG** (.dwg) - AutoCAD Drawing (requires ODA File Converter)
- **AutoFire** (.autofire, .json) - Native AutoFire project format
- **PDF** (.pdf) - PDF underlays (import only, no conversion yet)

### Output Formats

- **DXF** (.dxf) - Universal CAD exchange format
- **DWG** (.dwg) - AutoCAD native format (requires ODA File Converter)
- **AutoFire** (.autofire) - Native project format with Layer Intelligence

## GUI Usage

### Import CAD Files

1. **File → Import → DXF Underlay**
   - Now supports both `.dxf` and `.dwg` files
   - Auto-detects format and converts as needed
   - DWG files automatically converted to DXF on-the-fly

2. **File → Import → PDF Underlay**
   - Imports PDF as raster underlay
   - Useful for tracing architectural plans

### Auto-Detection

- Drop any supported CAD file into import dialog
- AutoFire automatically detects format
- Converts DWG → DXF transparently (requires ODA)

## CLI Usage

### Batch Conversion Tool

Located at `tools/cli/convert.py`

#### Show Converter Info

```powershell
python tools/cli/convert.py info
```

Output shows:

- Supported formats
- DWG support status (ODA availability)
- ODA File Converter location

#### Convert Single Files

**DWG to DXF:**

```powershell
python tools/cli/convert.py dwg-to-dxf "C:\Projects\floorplan.dwg"
# Output: floorplan.dxf
```

**DXF to AutoFire (with Layer Intelligence):**

```powershell
python tools/cli/convert.py dxf-to-autofire "C:\Projects\floorplan.dxf"
# Output: floorplan.autofire (JSON with detected devices)
```

**AutoFire to DXF (export):**

```powershell
python tools/cli/convert.py autofire-to-dxf "C:\Projects\project.autofire"
# Output: project.dxf
```

#### Batch Convert Multiple Files

```powershell
# Convert all DWG files in a folder to DXF
python tools/cli/convert.py batch "C:\Projects\*.dwg" --to .dxf

# Convert all DXF files to AutoFire format
python tools/cli/convert.py batch "C:\Projects\*.dxf" --to .autofire
```

#### Detect Format

```powershell
python tools/cli/convert.py detect "C:\Projects\unknown_file.dwg"
# Output: .dwg
```

## DWG Support (Optional)

### Install ODA File Converter

AutoFire uses the free **ODA File Converter** for DWG support.

1. **Download ODA File Converter**
   - URL: <https://www.opendesign.com/guestfiles/oda_file_converter>
   - Version: Latest (currently 25.6.0)
   - Platform: Windows 64-bit

2. **Install**
   - Run installer (`ODAFileConverter_QT6_win_X.X.X_vc14.exe`)
   - Default location: `C:\Program Files\ODA\ODAFileConverter\`
   - AutoFire auto-detects installation

3. **Verify Installation**

   ```powershell
   python tools/cli/convert.py info
   ```

   Should show: `✓ DWG support available via ODA File Converter`

### Alternative Locations

If ODA is installed elsewhere, AutoFire searches:

- `C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe`
- `C:\Program Files (x86)\ODA\ODAFileConverter\ODAFileConverter.exe`
- `%USERPROFILE%\ODA\ODAFileConverter.exe`
- System PATH

## Python API Usage

### Programmatic Conversion

```python
from backend.file_converter import FileConverter, convert_file

# Quick conversion
convert_file("input.dwg", "output.dxf")

# Advanced usage
converter = FileConverter()

# Single file
converter.convert("floorplan.dwg", "floorplan.dxf")

# Batch convert
files = ["file1.dwg", "file2.dwg", "file3.dwg"]
results = converter.batch_convert(files, ".dxf")

# Detect format
fmt = converter.detect_format("mystery_file.cad")
print(f"Detected format: {fmt}")
```

### DXF to AutoFire (with Layer Intelligence)

```python
from backend.file_converter import FileConverter

converter = FileConverter()

# Convert DXF → AutoFire (extracts devices via layer patterns)
converter.convert(
    "commercial_building.dxf",
    "commercial_building.autofire"
)

# Resulting .autofire JSON contains:
# - Detected fire devices (sprinklers, alarms, etc.)
# - Geometry (walls, rooms, etc.)
# - Layer information
# - Units and metadata
```

### Error Handling

```python
from backend.file_converter import (
    FileConverter,
    ConversionError,
    FileFormatError
)

try:
    converter = FileConverter()
    converter.convert("input.dwg", "output.dxf")
except FileFormatError as e:
    print(f"Unsupported format: {e}")
except ConversionError as e:
    print(f"Conversion failed: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

## Conversion Workflows

### Workflow 1: Import DWG Floorplans

```powershell
# 1. Batch convert DWG files to DXF
python tools/cli/convert.py batch "C:\Floorplans\*.dwg" --to .dxf

# 2. Analyze DXF files with Layer Intelligence
python tools/cli/batch_analysis_agent.py --analyze

# 3. Open in AutoFire GUI
#    File → Open → select .dxf file
```

### Workflow 2: Export to DWG

```powershell
# 1. Save AutoFire project (.autofire JSON)
#    File → Save As → project.autofire

# 2. Convert to DXF
python tools/cli/convert.py autofire-to-dxf project.autofire

# 3. Convert DXF to DWG
python tools/cli/convert.py dxf-to-dwg project.dxf
```

### Workflow 3: Continuous Integration

Add to CI workflow for automated testing:

```yaml
- name: Convert Test DWG Files
  run: |
    python tools/cli/convert.py batch tests/fixtures/dxf/*.dwg --to .dxf

- name: Analyze Converted Files
  run: |
    python tools/cli/batch_analysis_agent.py --analyze
```

## Layer Intelligence Integration

### DXF → AutoFire Conversion

When converting DXF to AutoFire format, the converter applies **Layer Intelligence** to detect fire protection devices:

**Detected Patterns:**

- Layers containing `FIRE`, `SPRINKLER`, `ALARM`, `DEVICE`, `HEAD`
- Circles on fire layers → sprinklers
- Blocks/inserts on alarm layers → alarm devices
- Complex multi-layer detection via AI (future)

**Example:**

```powershell
# Convert commercial_building.dxf
python tools/cli/convert.py dxf-to-autofire commercial_building.dxf

# Resulting commercial_building.autofire contains:
# {
#   "version": "0.4.7",
#   "devices": [
#     {"type": "sprinkler", "x": 10.5, "y": 20.3, "layer": "FIRE-SPRINKLER"},
#     {"type": "sprinkler", "x": 15.0, "y": 20.3, "layer": "FIRE-SPRINKLER"},
#     ...
#   ],
#   "geometry": [...],
#   "metadata": {
#     "device_count": 47,
#     "confidence": 0.95
#   }
# }
```

## Format Compatibility

### Round-Trip Support

| Source → Destination | Status | Notes |
|---------------------|--------|-------|
| DXF → AutoFire → DXF | ✅ Supported | Full round-trip |
| DWG → DXF → AutoFire | ✅ Supported | Requires ODA |
| AutoFire → DXF → DWG | ✅ Supported | Requires ODA |
| PDF → DXF | ❌ Not yet | Use external vectorizer |

### Supported DXF/DWG Versions

- **DXF:** R12 through R2018 (via ezdxf)
- **DWG:** R13 through R2018 (via ODA File Converter)

### Geometry Support

**Supported Entities:**

- LINE, CIRCLE, ARC
- LWPOLYLINE, POLYLINE
- ELLIPSE, SPLINE (approximated)
- INSERT (blocks/symbols)

**Not Yet Supported:**

- HATCH patterns
- DIMENSION styles
- MTEXT complex formatting
- XREF external references
- 3D solids (ACIS)

## Troubleshooting

### DWG Conversion Fails

**Error:** `DWG conversion requires ODA File Converter`

**Solution:**

1. Download ODA from <https://www.opendesign.com/guestfiles/oda_file_converter>
2. Install to default location
3. Verify: `python tools/cli/convert.py info`

### Conversion Timeout

**Error:** `DWG conversion timed out`

**Solution:**

- Large files may exceed 60s timeout
- Convert manually using ODA GUI
- Or increase timeout in `backend/file_converter.py`

### Missing ezdxf

**Error:** `DXF conversion requires ezdxf`

**Solution:**

```powershell
pip install ezdxf
```

### Layer Detection Issues

**Problem:** Devices not detected in DXF → AutoFire conversion

**Solution:**

1. Check layer names (must contain `FIRE`, `SPRINKLER`, etc.)
2. Verify devices are circles (not blocks/text)
3. Manually adjust layer patterns in `backend/file_converter.py`

## Best Practices

1. **Always keep originals** - Conversions may lose some data
2. **Batch convert early** - Convert all DWG files to DXF at project start
3. **Validate after conversion** - Visually inspect converted files
4. **Use Layer Intelligence** - DXF → AutoFire extracts device data automatically
5. **Standard layer naming** - Use `FIRE-*`, `SPRINKLER-*` naming conventions

## Future Enhancements

- [ ] PDF → DXF vectorization (via Inkscape CLI)
- [ ] IFC (BIM) import/export
- [ ] Revit RVT support (via Dynamo)
- [ ] AI-enhanced layer detection (GPT-4 Vision)
- [ ] Cloud conversion service
- [ ] Real-time DWG preview (no conversion needed)

## Related Documentation

- [Layer Intelligence Guide](LAYER_INTELLIGENCE.md) - Device detection patterns
- [CLI Agent Guide](docs/CLI_AGENT_GUIDE.md) - Batch analysis automation
- [Test Fixtures](tests/fixtures/README.md) - Sample DXF/DWG files
