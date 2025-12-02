# CLI Agent Guide - Autonomous Batch Analysis

This guide shows how to use AutoFire's CLI agents for automated batch processing and analysis.

---

## 🤖 GitHub Copilot CLI Agent Integration

The CLI agents are designed to be used by GitHub Copilot's autonomous coding agent for automated tasks.

### **Recommended Workflow for Copilot Agent**

When you want Copilot to run automated analysis:

1. **Open a new conversation with Copilot**
2. **Use the hashtag trigger**: `#github-pull-request_copilot-coding-agent`
3. **Provide the task description** (see examples below)

---

## 📋 Task Templates for Copilot Agent

### **Task 1: Batch DXF Analysis**

**Prompt for Copilot:**

```
#github-pull-request_copilot-coding-agent

Run batch DXF analysis on all files in the Projects/ directory using the automated CLI agent.

Steps:
1. Navigate to the AutoFire repository
2. Activate the Python virtual environment
3. Run: python tools/cli/batch_analysis_agent.py --analyze
4. Review the generated reports in docs/analysis/
5. Commit the reports with message: "docs: Add automated batch DXF analysis report"

Expected output:
- JSON report: docs/analysis/batch_analysis_YYYYMMDD_HHMMSS.json
- Markdown report: docs/analysis/batch_analysis_YYYYMMDD_HHMMSS.md
- Console summary with key metrics
```

---

### **Task 2: Layer Intelligence Validation**

**Prompt for Copilot:**

```
#github-pull-request_copilot-coding-agent

Validate Layer Intelligence engine by analyzing all DXF files and comparing results.

Steps:
1. Run batch analysis: python tools/cli/batch_analysis_agent.py --analyze
2. Extract device counts from each file
3. Create validation report comparing against expected values (if available)
4. Generate summary of layer naming patterns discovered
5. Commit results with message: "test: Validate Layer Intelligence on project DXF files"

Output:
- Analysis reports in docs/analysis/
- Validation summary in docs/analysis/validation_summary.md
```

---

### **Task 3: Coverage Optimization Benchmarking**

**Prompt for Copilot:**

```
#github-pull-request_copilot-coding-agent

Run coverage optimization benchmarks using the Layer Intelligence CLI.

Steps:
1. For each DXF file with detected devices:
   - Run: python tools/cli/intel_cli.py optimize --devices '[...]'
   - Capture optimization results
2. Generate benchmark report showing:
   - Optimization runtime
   - Device placement recommendations
   - Coverage percentages achieved
3. Save results to docs/analysis/coverage_optimization_benchmark.md
4. Commit with message: "perf: Add coverage optimization benchmarks"

Expected metrics:
- Average optimization time per file
- Coverage improvement percentages
- Device placement efficiency scores
```

---

### **Task 4: Geometry Operations Validation**

**Prompt for Copilot:**

```
#github-pull-request_copilot-coding-agent

Validate geometry operations (trim, extend, intersect) using the CLI tool.

Steps:
1. Create test dataset of geometry operations
2. For each test case:
   - Run: python tools/cli/geom_ops.py [operation] --segment {...} --cutter {...}
   - Verify results match expected values
3. Generate validation report
4. Commit test results with message: "test: Validate geometry operations via CLI"

Test coverage:
- Line-line trim operations
- Circle-line extend operations
- Arc-line intersect operations
```

---

### **Task 5: DXF Export/Import Roundtrip Test**

**Prompt for Copilot:**

```
#github-pull-request_copilot-coding-agent

Test DXF export/import roundtrip integrity.

Steps:
1. For each .autofire project file:
   - Export to DXF
   - Re-import DXF
   - Compare geometry integrity
2. Run Layer Intelligence analysis on exported DXF
3. Verify device counts match original
4. Generate roundtrip test report
5. Commit with message: "test: DXF roundtrip integrity validation"

Validation checks:
- Geometry preservation (vertices, arc centers)
- Layer structure preservation
- Device detection consistency
```

---

## 🛠️ Manual CLI Usage (For Testing)

If you want to test CLI agents manually before handing off to Copilot:

### **Batch Analysis**

```powershell
# Activate virtual environment
. .venv/Scripts/Activate.ps1

# Run batch analysis
python tools/cli/batch_analysis_agent.py --analyze

# Dry run (preview without saving)
python tools/cli/batch_analysis_agent.py --analyze --dry-run

# Custom search path
python tools/cli/batch_analysis_agent.py --analyze --search-path "path/to/dxf/files"
```

### **Layer Intelligence CLI**

```powershell
# Analyze single file
python tools/cli/intel_cli.py analyze Projects/sample.dxf

# Analyze multiple files
python tools/cli/intel_cli.py analyze-set Projects/*.dxf

# Run coverage optimization
python tools/cli/intel_cli.py optimize --devices '[{"type":"smoke","x":10,"y":20}]'
```

### **Geometry Operations**

```powershell
# Trim operation
python tools/cli/geom_ops.py trim --segment '{"type":"line","start":[0,0],"end":[10,10]}' --cutter '{"type":"line","start":[5,0],"end":[5,10]}'

# Extend operation
python tools/cli/geom_ops.py extend --segment '{"type":"line","start":[0,0],"end":[5,5]}' --target '{"type":"line","start":[10,0],"end":[10,10]}'

# Intersect operation
python tools/cli/geom_ops.py intersect --segment1 '{"type":"line","start":[0,0],"end":[10,10]}' --segment2 '{"type":"line","start":[0,10],"end":[10,0]}'
```

---

## 📊 Expected Outputs

### **Batch Analysis JSON Report Structure**

```json
{
  "timestamp": "2025-12-02T10:30:00",
  "files_analyzed": [
    {
      "status": "success",
      "file": "Projects/sample.dxf",
      "analysis": {
        "file_name": "sample.dxf",
        "total_layers": 25,
        "fire_layers": ["FP-DEVICES", "FP-WIRING"],
        "precision_data": {
          "total_fire_devices": 12,
          "confidence_score": 0.95
        }
      }
    }
  ],
  "summary": {
    "total_files": 5,
    "successful_analyses": 5,
    "total_fire_devices": 47,
    "average_devices_per_file": 9.4
  }
}
```

### **Markdown Report Preview**

```markdown
# Batch DXF Analysis Report

**Generated**: 2025-12-02T10:30:00

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Files Analyzed | 5 |
| Successful Analyses | 5 |
| Total Fire Protection Devices | 47 |

## Analysis Results

### ✅ sample.dxf
- Fire Protection Devices: 12
- Confidence Score: 95.0%
```

---

## 🚀 Quick Start for Copilot Agent

**Simplest prompt to get started:**

```
#github-pull-request_copilot-coding-agent

Run the automated batch DXF analysis:
python tools/cli/batch_analysis_agent.py --analyze

Then commit the reports to docs/analysis/ with message:
"docs: Automated batch DXF analysis report"
```

That's it! Copilot will:
1. Set up the environment
2. Run the analysis
3. Generate reports
4. Commit and push results

---

## 📝 Notes for Copilot Agent

- **Virtual environment**: Always activate `.venv` before running Python scripts
- **Dry run first**: Use `--dry-run` flag to preview before committing
- **Error handling**: If analysis fails, check DXF file integrity and layer naming
- **Report location**: All reports go to `docs/analysis/` by default
- **Commit messages**: Use conventional commit format (docs:, test:, perf:)

---

## 🔍 Troubleshooting

### **No DXF files found**
- Check `Projects/` directory exists
- Verify DXF files have `.dxf` extension
- Try custom search path: `--search-path "path/to/files"`

### **Analysis fails**
- Verify DXF file is valid (open in CAD software)
- Check for corrupted files
- Review error messages in console output

### **No devices detected**
- Verify layer names match expected patterns (FP-, FIRE-, etc.)
- Check `autofire_layer_intelligence.py` layer detection logic
- Add custom layer patterns if needed

---

*Last Updated: December 2, 2025*
