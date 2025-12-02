# AutoFire CLI Tools - Testing & Automation Utilities

**Last Updated**: December 1, 2025
**Status**: Testing/Automation Tools (NOT production LV CAD integration)

## Overview

This directory contains **standalone CLI utilities** for testing, batch processing, and automation workflows. These tools are **NOT integrated with the production LV CAD system** - they serve as development and automation aids.

---

## 📁 Tool Inventory

### 1. `geom_ops.py` - Geometry Operations Testing Tool

**Purpose**: Standalone CLI for testing geometry algorithms
**Integration**: NOT connected to LV CAD - simulation/testing only
**Relationship to Backend**: Mirrors `backend/ops_service.py` operations for testing

**Use Cases**:

- Testing geometry algorithms before backend integration
- Batch processing geometry operations via scripts
- CI/CD validation of geometry calculations
- Quick prototyping and verification

**Example Usage**:

```bash
# Test trim operation
python tools/cli/geom_ops.py trim \
  --segment '{"start":{"x":0,"y":0},"end":{"x":10,"y":10}}' \
  --cutter '{"start":{"x":5,"y":0},"end":{"x":5,"y":10}}' \
  --format json

# Test intersection
python tools/cli/geom_ops.py intersect \
  --segment1 '{"start":{"x":0,"y":0},"end":{"x":10,"y":10}}' \
  --segment2 '{"start":{"x":0,"y":10},"end":{"x":10,"y":0}}' \
  --format text
```

**Output Formats**:

- `--format json`: Machine-readable JSON for automation
- `--format text`: Human-readable text for debugging

---

### 2. `intel_cli.py` - Layer Intelligence Batch Processing

**Purpose**: Headless CLI wrapper for CAD layer analysis
**Integration**: Calls `autofire_layer_intelligence.py` for batch workflows
**Use Case**: Non-GUI automation and batch processing

**Use Cases**:

- Batch analysis of multiple CAD files
- CI/CD pipeline integration
- Scheduled analysis jobs
- Construction set processing automation

**Example Usage**:

```bash
# Analyze single CAD file
python tools/cli/intel_cli.py analyze path/to/drawing.dwg

# Analyze construction set
python tools/cli/intel_cli.py analyze-set file1.dwg file2.dwg file3.dwg

# Run coverage optimization
python tools/cli/intel_cli.py optimize --devices '[{"type":"smoke","x":10,"y":20}]'
```

**Output**: JSON format suitable for automation and logging

---

### 3. `communication_log.py` - Development Activity Logger

**Purpose**: Local logging system for development tracking
**Integration**: Standalone - no external service dependencies
**Use Case**: Development session tracking and automation logging

**Use Cases**:

- Development milestone tracking
- Automation workflow documentation
- Performance metrics logging
- Project status reporting

**Example Usage**:

```python
from tools.cli.communication_log import CommunicationLog

log = CommunicationLog()
log.log_milestone("CLI Testing Complete", importance="high")
log.log_operation("geometry_test", success=True, duration=0.5)
report = log.generate_report(format="markdown")
```

**Output Formats**: JSON, Markdown, Plain Text

---

## 🔄 Relationship to Backend Systems

### Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION SYSTEMS                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  backend/ops_service.py                                     │
│  └─ Production geometry operations                          │
│     └─ Integrates with CAD core                             │
│        └─ Used by LV CAD application                        │
│                                                              │
│  autofire_layer_intelligence.py                             │
│  └─ Core Layer Intelligence engine                          │
│     └─ Device detection & optimization                      │
│        └─ Used by GUI application                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              TESTING & AUTOMATION TOOLS                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  tools/cli/geom_ops.py                                      │
│  └─ MIRRORS backend/ops_service.py for testing             │
│     └─ Standalone simulation (NOT connected)                │
│        └─ JSON/text output for CI/CD                        │
│                                                              │
│  tools/cli/intel_cli.py                                     │
│  └─ WRAPS autofire_layer_intelligence.py                    │
│     └─ Batch processing interface                           │
│        └─ JSON output for automation                        │
│                                                              │
│  tools/cli/communication_log.py                             │
│  └─ Development logging utility                             │
│     └─ Standalone (no dependencies)                         │
│        └─ Multiple output formats                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Distinctions

| Aspect | Backend Services | CLI Tools |
|--------|-----------------|-----------|
| **Purpose** | Production CAD operations | Testing & automation |
| **Integration** | Integrated with CAD core | Standalone utilities |
| **Usage** | GUI application calls | Command-line/scripts |
| **Data** | Real CAD entities | Simulated/test data |
| **Environment** | Production | Development/CI |

---

## 🚀 When to Use These Tools

### ✅ **Use CLI Tools When**

- Running automated tests in CI/CD
- Batch processing multiple CAD files
- Testing geometry algorithms before backend integration
- Prototyping new features quickly
- Generating test data or reports
- Debugging without GUI

### ❌ **Don't Use CLI Tools For**

- Production CAD operations (use `backend/ops_service.py`)
- Interactive LV CAD work (use GUI application)
- Real-time geometry editing (use CAD core)
- Critical production workflows

---

## 📊 Testing Status

| Tool | Test Coverage | Status | Notes |
|------|--------------|--------|-------|
| `geom_ops.py` | Manual validation | ✅ Working | Simulation-based |
| `intel_cli.py` | Integration tests | ⚠️ Partial | Some methods stubbed |
| `communication_log.py` | Unit tested | ✅ Working | Full functionality |

---

## 🔧 Development Guidelines

### Adding New CLI Tools

1. **Document Purpose**: Clearly state if testing/automation tool
2. **Avoid Production Integration**: Keep CLI tools standalone
3. **Provide Examples**: Include usage examples in docstrings
4. **Output Formats**: Support JSON for automation, text for humans
5. **Error Handling**: Comprehensive error messages and exit codes

### Naming Conventions

- `*_cli.py`: Command-line interfaces
- `*_ops.py`: Operation utilities
- `*_log.py`: Logging utilities

---

## 📝 Future Enhancements

- [ ] Add comprehensive unit tests for `geom_ops.py`
- [ ] Implement missing methods in `intel_cli.py`
- [ ] Add performance benchmarking utilities
- [ ] Create unified CLI entry point
- [ ] Add bash/PowerShell completion scripts

---

## 🤝 Contributing

When adding CLI tools:

1. **Document thoroughly** - Explain purpose and use cases
2. **Keep separate** - Don't integrate with production systems
3. **Test well** - Add tests for reliability
4. **Follow patterns** - Use existing tools as templates

---

## 📚 Related Documentation

- **Backend Services**: `backend/README.md` (if exists)
- **Layer Intelligence**: `autofire_layer_intelligence.py` docstrings
- **CAD Core**: `cad_core/` documentation
- **Testing Guide**: `tests/README.md` (if exists)

---

**Questions or Issues?**
These tools are for development/automation support. For production CAD operations, see the main AutoFire application documentation.
