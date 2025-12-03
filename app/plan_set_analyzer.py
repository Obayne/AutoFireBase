"""Plan Set Analyzer - Multi-File DXF Analysis.

Enables AI assistant to analyze complete construction plan sets
by combining data from multiple DXF sheets.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

from PySide6 import QtCore

logger = logging.getLogger(__name__)


@dataclass
class SheetAnalysis:
    """Analysis results for a single DXF sheet."""

    filename: str
    layer_count: int
    fire_layers: list[str]
    device_count: int
    bounds: QtCore.QRectF | None
    errors: list[str]


@dataclass
class PlanSetAnalysis:
    """Combined analysis of multiple DXF sheets."""

    sheet_count: int
    sheets: list[SheetAnalysis]
    total_layers: int
    total_fire_layers: int
    total_devices: int
    combined_bounds: QtCore.QRectF | None
    layer_summary: dict[str, int]  # layer_name -> count across sheets
    errors: list[str]


class PlanSetAnalyzer:
    """Analyze multiple DXF files as a coordinated plan set."""

    def __init__(self):
        """Initialize the plan set analyzer."""
        self.fire_layer_patterns = [
            "FIRE",
            "FA",
            "ALARM",
            "SPRINKLER",
            "SMOKE",
            "DETECTOR",
            "STROBE",
            "HORN",
            "PULL",
            "PANEL",
            "ANNUNCIATOR",
        ]

    def analyze_plan_set(self, file_paths: list[str]) -> PlanSetAnalysis:
        """
        Analyze multiple DXF files as a complete plan set.

        Args:
            file_paths: List of paths to DXF files

        Returns:
            Combined analysis of all sheets
        """
        logger.info(f"Analyzing plan set with {len(file_paths)} sheets")

        sheets = []
        total_layers = 0
        total_fire_layers = 0
        total_devices = 0
        layer_summary = {}
        errors = []
        combined_bounds = None

        for path in file_paths:
            try:
                sheet = self._analyze_single_sheet(path)
                sheets.append(sheet)

                total_layers += sheet.layer_count
                total_fire_layers += len(sheet.fire_layers)
                total_devices += sheet.device_count

                # Track layer names across sheets
                for layer in sheet.fire_layers:
                    layer_summary[layer] = layer_summary.get(layer, 0) + 1

                # Combine bounds
                if sheet.bounds:
                    if combined_bounds is None:
                        combined_bounds = sheet.bounds
                    else:
                        combined_bounds = combined_bounds.united(sheet.bounds)

            except Exception as e:
                error_msg = f"Error analyzing {Path(path).name}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        return PlanSetAnalysis(
            sheet_count=len(sheets),
            sheets=sheets,
            total_layers=total_layers,
            total_fire_layers=total_fire_layers,
            total_devices=total_devices,
            combined_bounds=combined_bounds,
            layer_summary=layer_summary,
            errors=errors,
        )

    def _analyze_single_sheet(self, file_path: str) -> SheetAnalysis:
        """
        Analyze a single DXF sheet.

        Args:
            file_path: Path to DXF file

        Returns:
            Sheet analysis results
        """

        path = Path(file_path)
        logger.debug(f"Analyzing sheet: {path.name}")

        try:
            # Try to load DXF file
            import ezdxf

            doc = ezdxf.readfile(file_path)
            msp = doc.modelspace()

            # Get all layers
            all_layers = [layer.dxf.name for layer in doc.layers]
            layer_count = len(all_layers)

            # Identify fire protection layers
            fire_layers = [
                layer
                for layer in all_layers
                if any(pattern in layer.upper() for pattern in self.fire_layer_patterns)
            ]

            # Count devices (entities in fire layers)
            device_count = 0
            for layer_name in fire_layers:
                try:
                    entities = list(msp.query(f'*[layer=="{layer_name}"]'))
                    device_count += len(entities)
                except Exception as e:
                    logger.warning(f"Error counting devices in layer {layer_name}: {e}")

            # Get bounds
            bounds = None
            try:
                extents = msp.extents()
                if extents:
                    min_pt, max_pt = extents
                    bounds = QtCore.QRectF(
                        min_pt[0], -max_pt[1], max_pt[0] - min_pt[0], max_pt[1] - min_pt[1]
                    )
            except Exception as e:
                logger.warning(f"Could not determine bounds for {path.name}: {e}")

            return SheetAnalysis(
                filename=path.name,
                layer_count=layer_count,
                fire_layers=fire_layers,
                device_count=device_count,
                bounds=bounds,
                errors=[],
            )

        except Exception as e:
            logger.error(f"Error analyzing {path.name}: {e}")
            return SheetAnalysis(
                filename=path.name,
                layer_count=0,
                fire_layers=[],
                device_count=0,
                bounds=None,
                errors=[str(e)],
            )

    def format_analysis_report(self, analysis: PlanSetAnalysis) -> str:
        """
        Format plan set analysis as a readable report.

        Args:
            analysis: Plan set analysis results

        Returns:
            Formatted text report
        """
        lines = [
            "🏗️ PLAN SET ANALYSIS REPORT",
            "=" * 60,
            "\n📊 Overview:",
            f"   • Total Sheets: {analysis.sheet_count}",
            f"   • Total Layers: {analysis.total_layers}",
            f"   • Fire Protection Layers: {analysis.total_fire_layers}",
            f"   • Total Devices Detected: {analysis.total_devices}",
        ]

        if analysis.errors:
            lines.append(f"\n⚠️ Errors: {len(analysis.errors)}")
            for error in analysis.errors[:5]:  # Show first 5 errors
                lines.append(f"   • {error}")

        lines.append("\n📋 Sheets Analyzed:")
        for sheet in analysis.sheets:
            lines.append(f"\n   {sheet.filename}")
            lines.append(f"      Layers: {sheet.layer_count}")
            lines.append(f"      Fire Layers: {len(sheet.fire_layers)}")
            lines.append(f"      Devices: {sheet.device_count}")
            if sheet.fire_layers:
                lines.append(f"      Fire Layer Names: {', '.join(sheet.fire_layers[:3])}")

        if analysis.layer_summary:
            lines.append("\n🔥 Fire Protection Layer Summary:")
            sorted_layers = sorted(analysis.layer_summary.items(), key=lambda x: x[1], reverse=True)
            for layer_name, count in sorted_layers[:10]:  # Top 10 layers
                lines.append(f"   • {layer_name}: appears in {count} sheet(s)")

        return "\n".join(lines)


def import_plan_set(file_paths: list[str]) -> PlanSetAnalysis:
    """
    Import and analyze multiple DXF files as a plan set.

    Args:
        file_paths: List of paths to DXF files

    Returns:
        Combined plan set analysis
    """
    analyzer = PlanSetAnalyzer()
    return analyzer.analyze_plan_set(file_paths)


def analyze_layers_batch(file_paths: list[str]) -> dict:
    """
    Analyze layers across multiple DXF files.

    Args:
        file_paths: List of paths to DXF files

    Returns:
        Dictionary with batch analysis results
    """
    analyzer = PlanSetAnalyzer()
    analysis = analyzer.analyze_plan_set(file_paths)

    return {
        "total_layers": analysis.total_layers,
        "fire_protection_layers": analysis.total_fire_layers,
        "devices_detected": analysis.total_devices,
        "sheet_count": analysis.sheet_count,
        "layer_summary": analysis.layer_summary,
        "errors": analysis.errors,
    }
