# Plan Set Analyzer - Usage Guide

## Overview

The Plan Set Analyzer enables comprehensive analysis of multiple DXF files as a coordinated construction plan set. This allows the AI assistant to view and analyze data from all sheets simultaneously.

## Features

- **Multi-File Import**: Load multiple DXF files in one operation
- **Batch Layer Analysis**: Combine layer data across all sheets
- **AI Integration**: Get intelligent insights from complete plan sets
- **Comprehensive Reports**: Formatted analysis with layer summaries

## Quick Start

### From UI (AI Assistant Panel)

1. **Load Plan Set**
   - Click "Load Plan Set" button in AI Assistant
   - Select multiple DXF files (Ctrl+Click or Shift+Click)
   - Files are loaded and listed in the assistant log

2. **Analyze Plan Set**
   - Click "Analyze Plan Set" button
   - View detailed report of all sheets:
     - Total layers across all files
     - Fire protection layers identified
     - Device counts per sheet
     - Layer frequency summary
   - AI provides additional insights if Ollama is running

3. **Clear Plan Set**
   - Click "Clear Plan Set" to remove loaded files
   - Ready to load a different plan set

### Programmatic Use

```python
from app.plan_set_analyzer import PlanSetAnalyzer, import_plan_set, analyze_layers_batch

# Method 1: Full analysis with detailed report
analyzer = PlanSetAnalyzer()
analysis = analyzer.analyze_plan_set([
    "floor_plan.dxf",
    "electrical.dxf",
    "fire_protection.dxf"
])
report = analyzer.format_analysis_report(analysis)
print(report)

# Method 2: Quick import
plan_set = import_plan_set(["sheet1.dxf", "sheet2.dxf"])
print(f"Found {plan_set.total_devices} devices across {plan_set.sheet_count} sheets")

# Method 3: Batch layer analysis (returns dict)
batch_results = analyze_layers_batch(["file1.dxf", "file2.dxf"])
print(f"Total layers: {batch_results['total_layers']}")
print(f"Fire protection layers: {batch_results['fire_protection_layers']}")
```

### AI Assistant Integration

```python
from app.assistant import AssistantDock

# In your application
assistant = AssistantDock(parent_window=main_window)

# Load plan set programmatically
assistant.load_plan_set([
    "basement.dxf",
    "ground_floor.dxf",
    "second_floor.dxf"
])

# Analyze with custom query
result = assistant.analyze_plan_set(
    ["floor1.dxf", "floor2.dxf"],
    query="What is the total coverage area for fire protection?"
)
print(result)

# Get plan set context for custom processing
context = assistant._get_plan_set_context()
print(f"Sheets: {context['sheet_count']}")
print(f"Devices: {context['total_devices']}")
print(f"Layers: {', '.join(context['all_layers'][:10])}")
```

## Analysis Output

### Sheet Analysis

Each sheet includes:

- Filename
- Total layer count
- Fire protection layers identified
- Device count (entities in fire layers)
- Bounding box
- Any errors encountered

### Plan Set Summary

Combined analysis provides:

- Total sheet count
- Aggregated layer count
- Total fire protection layers
- Total device count
- Layer frequency (which layers appear in multiple sheets)
- Combined bounding box

### Example Report

```
🏗️ PLAN SET ANALYSIS REPORT
============================================================

📊 Overview:
   • Total Sheets: 3
   • Total Layers: 45
   • Fire Protection Layers: 12
   • Total Devices Detected: 156

📋 Sheets Analyzed:

   BASEMENT_FIRE_PLAN.dxf
      Layers: 18
      Fire Layers: 4
      Devices: 42
      Fire Layer Names: FA-DEVICES, FA-WIRE, SMOKE-DET

   GROUND_FLOOR_FIRE_PLAN.dxf
      Layers: 15
      Fire Layers: 4
      Devices: 67
      Fire Layer Names: FA-DEVICES, FA-WIRE, SMOKE-DET

   SECOND_FLOOR_FIRE_PLAN.dxf
      Layers: 12
      Fire Layers: 4
      Devices: 47
      Fire Layer Names: FA-DEVICES, FA-WIRE, SMOKE-DET

🔥 Fire Protection Layer Summary:
   • FA-DEVICES: appears in 3 sheet(s)
   • FA-WIRE: appears in 3 sheet(s)
   • SMOKE-DET: appears in 3 sheet(s)
   • PULL-STATIONS: appears in 2 sheet(s)
```

## Fire Protection Layer Detection

The analyzer automatically identifies fire protection layers by looking for these patterns:

- FIRE
- FA (Fire Alarm)
- ALARM
- SPRINKLER
- SMOKE
- DETECTOR
- STROBE
- HORN
- PULL
- PANEL
- ANNUNCIATOR

Custom patterns can be added to the `PlanSetAnalyzer.fire_layer_patterns` list.

## Error Handling

- Invalid files are logged but don't stop processing
- Missing DXF files are reported with clear error messages
- Individual sheet errors don't affect other sheets
- All errors are collected in the analysis results

## Integration Points

### With AI Assistant

- Plan set context automatically available to AI queries
- Multi-sheet coverage analysis
- Cross-sheet layer coordination checks
- Comprehensive system design insights

### With DXF Import

- Uses existing `app/dxf_import.py` for layer reading
- Compatible with ezdxf library
- Respects drawing units and scaling
- Handles layer colors and properties

### With CAD Core

- Bounding box calculations for viewport fitting
- Layer organization and filtering
- Device detection and counting

## Future Enhancements

Planned features:

- [ ] Cross-sheet reference detection
- [ ] Coordinate system alignment
- [ ] Sheet matching and correlation
- [ ] Multi-floor vertical alignment
- [ ] Plan set export/packaging
- [ ] Custom layer pattern management UI

## Testing

Run regression tests:

```powershell
pytest tests/regression/test_plan_set_analyzer.py -v
```

Unit tests ensure:

- Module imports correctly
- Classes instantiate without errors
- Core functions are accessible
- Data structures match expectations
