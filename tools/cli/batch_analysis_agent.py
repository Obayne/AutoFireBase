"""
Batch Analysis CLI Agent - Automated DXF Analysis & Coverage Optimization
==========================================================================

**PURPOSE**: Autonomous agent for batch processing CAD files, generating reports,
and validating Layer Intelligence capabilities.

**WORKFLOW**:
1. Discover DXF files in Projects/ directory
2. Run Layer Intelligence analysis on each file
3. Generate coverage optimization recommendations
4. Create comprehensive JSON + Markdown reports
5. Commit results to docs/analysis/

**USAGE** (for GitHub Copilot CLI Agent):
```bash
# Run batch analysis
python tools/cli/batch_analysis_agent.py --analyze

# Generate reports only (skip analysis)
python tools/cli/batch_analysis_agent.py --report-only

# Dry run (no commits)
python tools/cli/batch_analysis_agent.py --analyze --dry-run
```

**OUTPUT**:
- JSON: docs/analysis/batch_analysis_YYYYMMDD_HHMMSS.json
- Markdown: docs/analysis/batch_analysis_YYYYMMDD_HHMMSS.md
- Summary: Prints to console with key metrics

**INTEGRATION**: Works with existing intel_cli.py and autofire_layer_intelligence.py
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from autofire_layer_intelligence import (  # noqa: E402
    CADLayerIntelligence,
    ConstructionDrawingIntelligence,
)

logger = logging.getLogger(__name__)


class BatchAnalysisAgent:
    """Autonomous agent for batch CAD analysis and reporting."""

    def __init__(self, dry_run: bool = False):
        """Initialize the batch analysis agent."""
        self.dry_run = dry_run
        self.layer_intel = CADLayerIntelligence()
        self.construction_intel = ConstructionDrawingIntelligence(self.layer_intel)
        self.results: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "files_analyzed": [],
            "summary": {},
            "errors": [],
        }

    def discover_dxf_files(self, search_path: Path = Path("Projects")) -> list[Path]:
        """
        Discover all DXF files in the specified directory.

        Args:
            search_path: Directory to search for DXF files

        Returns:
            List of DXF file paths
        """
        if not search_path.exists():
            logger.warning("Search path does not exist: %s", search_path)
            return []

        dxf_files = list(search_path.rglob("*.dxf")) + list(search_path.rglob("*.DXF"))
        logger.info("📁 Discovered %d DXF files in %s", len(dxf_files), search_path)
        return dxf_files

    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """
        Analyze a single DXF file.

        Args:
            file_path: Path to DXF file

        Returns:
            Analysis results dictionary
        """
        logger.info("🔍 Analyzing: %s", file_path.name)

        try:
            # Run Layer Intelligence analysis (use absolute path)
            abs_path = file_path.resolve()
            analysis = self.layer_intel.analyze_cad_file(str(abs_path))

            # Add file metadata
            analysis["file_name"] = file_path.name
            analysis["file_size_bytes"] = file_path.stat().st_size if file_path.exists() else 0
            try:
                analysis["relative_path"] = str(file_path.relative_to(_ROOT))
            except ValueError:
                analysis["relative_path"] = str(file_path)

            return {
                "status": "success",
                "file": str(file_path),
                "analysis": analysis,
            }

        except Exception as e:  # noqa: BLE001
            logger.error("❌ Failed to analyze %s: %s", file_path.name, e)
            return {
                "status": "error",
                "file": str(file_path),
                "error": str(e),
            }

    def run_batch_analysis(self, search_path: Path = Path("Projects")) -> dict[str, Any]:
        """
        Run batch analysis on all DXF files.

        Args:
            search_path: Directory to search for DXF files

        Returns:
            Comprehensive batch analysis results
        """
        logger.info("🚀 Starting batch analysis...")

        dxf_files = self.discover_dxf_files(search_path)

        if not dxf_files:
            logger.warning("⚠️  No DXF files found")
            return self.results

        # Analyze each file
        for file_path in dxf_files:
            result = self.analyze_file(file_path)
            self.results["files_analyzed"].append(result)

        # Generate summary statistics
        self.results["summary"] = self._generate_summary()

        logger.info("✅ Batch analysis complete")
        return self.results

    def _generate_summary(self) -> dict[str, Any]:
        """Generate summary statistics from analysis results."""
        successful = [r for r in self.results["files_analyzed"] if r["status"] == "success"]
        failed = [r for r in self.results["files_analyzed"] if r["status"] == "error"]

        total_devices = sum(
            r.get("analysis", {}).get("precision_data", {}).get("total_fire_devices", 0)
            for r in successful
        )

        total_fire_layers = sum(
            len(r.get("analysis", {}).get("fire_layers", [])) for r in successful
        )

        return {
            "total_files": len(self.results["files_analyzed"]),
            "successful_analyses": len(successful),
            "failed_analyses": len(failed),
            "total_fire_devices": total_devices,
            "total_fire_layers": total_fire_layers,
            "average_devices_per_file": total_devices / len(successful) if successful else 0,
        }

    def generate_json_report(self, output_dir: Path = Path("docs/analysis")) -> Path:
        """
        Generate JSON report of batch analysis.

        Args:
            output_dir: Directory to save report

        Returns:
            Path to generated report
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = output_dir / f"batch_analysis_{timestamp}.json"

        if self.dry_run:
            logger.info("[DRY RUN] Would save JSON report to: %s", report_path)
            return report_path

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)

        logger.info("💾 JSON report saved: %s", report_path)
        return report_path

    def generate_markdown_report(self, output_dir: Path = Path("docs/analysis")) -> Path:
        """
        Generate Markdown report of batch analysis.

        Args:
            output_dir: Directory to save report

        Returns:
            Path to generated report
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = output_dir / f"batch_analysis_{timestamp}.md"

        # Build markdown content
        md_content = self._build_markdown_content()

        if self.dry_run:
            logger.info("[DRY RUN] Would save Markdown report to: %s", report_path)
            print("\n" + "=" * 80)
            print("PREVIEW OF MARKDOWN REPORT:")
            print("=" * 80)
            print(md_content)
            print("=" * 80 + "\n")
            return report_path

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        logger.info("📄 Markdown report saved: %s", report_path)
        return report_path

    def _build_markdown_content(self) -> str:
        """Build markdown report content."""
        summary = self.results["summary"]
        timestamp = self.results["timestamp"]

        md = f"""# Batch DXF Analysis Report

**Generated**: {timestamp}
**Agent**: Batch Analysis CLI Agent
**Version**: 1.0.0

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Files Analyzed | {summary.get('total_files', 0)} |
| Successful Analyses | {summary.get('successful_analyses', 0)} |
| Failed Analyses | {summary.get('failed_analyses', 0)} |
| Total Fire Protection Devices | {summary.get('total_fire_devices', 0)} |
| Total Fire Protection Layers | {summary.get('total_fire_layers', 0)} |
| Average Devices per File | {summary.get('average_devices_per_file', 0):.1f} |

---

## Analysis Results

"""

        # Add details for each file
        for result in self.results["files_analyzed"]:
            file_name = Path(result["file"]).name
            status = result["status"]

            if status == "success":
                analysis = result.get("analysis", {})
                precision = analysis.get("precision_data", {})
                devices = precision.get("total_fire_devices", 0)
                layers = len(analysis.get("fire_layers", []))
                confidence = precision.get("confidence_score", 0) * 100

                md += f"""### ✅ {file_name}

- **Status**: Success
- **Fire Protection Devices**: {devices}
- **Fire Protection Layers**: {layers}
- **Confidence Score**: {confidence:.1f}%

"""
            else:
                error = result.get("error", "Unknown error")
                md += f"""### ❌ {file_name}

- **Status**: Failed
- **Error**: {error}

"""

        # Add recommendations
        md += """---

## Recommendations

"""

        if summary.get("failed_analyses", 0) > 0:
            md += (
                "- ⚠️  **Some files failed analysis** - "
                "Review error logs and verify file integrity\n"
            )

        if summary.get("total_fire_devices", 0) == 0:
            md += (
                "- ℹ️  **No devices detected** - "
                "Verify DXF layer naming conventions match expected patterns\n"
            )

        md += """
---

## Next Steps

1. Review detailed analysis in JSON report
2. Validate device counts against known project specifications
3. Run coverage optimization for files with detected devices
4. Update layer naming conventions if detection accuracy is low

---

*Generated by AutoFire Batch Analysis Agent*
"""

        return md

    def print_console_summary(self):
        """Print summary to console."""
        summary = self.results["summary"]

        print("\n" + "=" * 80)
        print("BATCH ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Total Files:        {summary.get('total_files', 0)}")
        print(f"Successful:         {summary.get('successful_analyses', 0)}")
        print(f"Failed:             {summary.get('failed_analyses', 0)}")
        print(f"Fire Devices:       {summary.get('total_fire_devices', 0)}")
        print(f"Fire Layers:        {summary.get('total_fire_layers', 0)}")
        print(f"Avg Devices/File:   {summary.get('average_devices_per_file', 0):.1f}")
        print("=" * 80 + "\n")


def main(argv: list[str] | None = None) -> int:
    """Main entry point for batch analysis agent."""
    parser = argparse.ArgumentParser(
        description="Batch Analysis CLI Agent - Automated DXF Analysis"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Run batch analysis on all DXF files",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Generate reports from existing analysis (not implemented)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - don't save files or commit",
    )
    parser.add_argument(
        "--search-path",
        type=Path,
        default=Path("Projects"),
        help="Directory to search for DXF files (default: Projects/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/analysis"),
        help="Output directory for reports (default: docs/analysis/)",
    )

    args = parser.parse_args(argv)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if not args.analyze and not args.report_only:
        parser.error("Must specify --analyze or --report-only")

    # Initialize agent
    agent = BatchAnalysisAgent(dry_run=args.dry_run)

    if args.analyze:
        # Run batch analysis
        agent.run_batch_analysis(args.search_path)

        # Generate reports
        agent.generate_json_report(args.output_dir)
        agent.generate_markdown_report(args.output_dir)

        # Print summary
        agent.print_console_summary()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
