"""
PDF Construction Set Analyzer
Analyzes complete construction document sets and extracts fire alarm requirements
"""

import re
from datetime import datetime
from typing import Any, Dict, List

try:
    import fitz  # PyMuPDF

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from . import (
    ConstructionAnalysis,
    ConstructionIntelligenceBase,
    DeviceType,
    FireAlarmAnalysis,
    FireAlarmDevice,
    FloorPlanAnalysis,
    PageType,
    Room,
    ScheduleAnalysis,
)


class PDFConstructionAnalyzer(ConstructionIntelligenceBase):
    """Analyzes complete construction document PDFs for fire alarm design"""

    def __init__(self):
        super().__init__()
        if not PYMUPDF_AVAILABLE:
            self.log_analysis("PyMuPDF not available - PDF analysis limited", "warning")

    def analyze_construction_set(self, pdf_path: str) -> ConstructionAnalysis:
        """
        Analyze complete construction document PDF set

        Args:
            pdf_path: Path to construction document PDF

        Returns:
            ConstructionAnalysis with extracted data
        """
        self.log_analysis(f"Starting analysis of construction set: {pdf_path}")

        if not PYMUPDF_AVAILABLE:
            return self._create_placeholder_analysis(pdf_path)

        try:
            doc = fitz.open(pdf_path)
            analysis = ConstructionAnalysis(
                project_name=self._extract_project_name(doc),
                analyzed_date=datetime.now(),
                pdf_path=pdf_path,
                total_pages=len(doc),
                floor_plans=[],
                fire_alarm_plans=[],
                schedules=[],
                specifications=[],
            )

            # Analyze each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_type = self._classify_page(page)

                if page_type == PageType.FLOOR_PLAN:
                    floor_plan = self._analyze_floor_plan(page, page_num)
                    analysis.floor_plans.append(floor_plan)

                elif page_type == PageType.FIRE_ALARM_PLAN:
                    fa_plan = self._analyze_fire_alarm_plan(page, page_num)
                    analysis.fire_alarm_plans.append(fa_plan)

                elif page_type == PageType.SCHEDULE:
                    schedule = self._analyze_schedule(page, page_num)
                    analysis.schedules.append(schedule)

                elif page_type == PageType.SPECIFICATIONS:
                    spec = self._analyze_specifications(page, page_num)
                    analysis.specifications.append(spec)

            doc.close()

            self.log_analysis(
                f"Analysis complete: {len(analysis.floor_plans)} floor plans, "
                f"{len(analysis.fire_alarm_plans)} FA plans, "
                f"{analysis.total_devices} devices found"
            )

            return analysis

        except Exception as e:
            self.log_analysis(f"Error analyzing PDF: {e}", "error")
            return self._create_placeholder_analysis(pdf_path)

    def _classify_page(self, page) -> PageType:
        """Classify page type based on content analysis"""
        text = page.get_text().lower()

        # Fire alarm plan indicators
        if any(
            term in text
            for term in [
                "fire alarm",
                "smoke detector",
                "heat detector",
                "pull station",
                "horn strobe",
                "notification",
            ]
        ):
            return PageType.FIRE_ALARM_PLAN

        # Floor plan indicators
        if any(term in text for term in ["floor plan", "architectural", "room", "door", "window"]):
            return PageType.FLOOR_PLAN

        # Schedule indicators
        if any(term in text for term in ["device schedule", "panel schedule", "equipment list"]):
            return PageType.SCHEDULE

        # Specification indicators
        if any(term in text for term in ["specification", "technical requirements", "nfpa"]):
            return PageType.SPECIFICATIONS

        return PageType.UNKNOWN

    def _extract_project_name(self, doc) -> str:
        """Extract project name from PDF metadata or first page"""
        # Try PDF metadata first
        metadata = doc.metadata
        if metadata.get("title"):
            return metadata["title"]

        # Try first page text
        if len(doc) > 0:
            first_page = doc[0]
            text = first_page.get_text()

            # Look for common project name patterns
            lines = text.split("\n")[:10]  # Check first 10 lines
            for line in lines:
                line = line.strip()
                if len(line) > 10 and not line.islower():
                    # Potential project name
                    return line

        return "Unknown Project"

    def _analyze_floor_plan(self, page, page_num: int) -> FloorPlanAnalysis:
        """Analyze architectural floor plan page"""
        text = page.get_text()

        # Extract rooms (simplified - look for room labels)
        rooms = self._extract_rooms_from_text(text)

        # Extract dimensions (look for dimension text)
        dimensions = self._extract_dimensions_from_text(text)

        # Detect scale
        scale = self._detect_scale_from_text(text)

        return FloorPlanAnalysis(
            sheet_number=f"A-{page_num + 1}",
            rooms=rooms,
            dimensions=dimensions,
            scale=scale,
            architectural_features={},
            coordinate_system=None,
        )

    def _analyze_fire_alarm_plan(self, page, page_num: int) -> FireAlarmAnalysis:
        """Analyze fire alarm plan page"""
        text = page.get_text()

        # Extract devices from text
        devices = self._extract_devices_from_text(text)

        return FireAlarmAnalysis(
            sheet_number=f"FA-{page_num + 1}",
            devices=devices,
            circuits=[],
            annotations=[],
            panel_locations=[],
            coverage_analysis=None,
        )

    def _analyze_schedule(self, page, page_num: int) -> ScheduleAnalysis:
        """Analyze device schedule page"""
        text = page.get_text()

        # Extract device schedule information
        device_schedule = self._extract_device_schedule(text)

        return ScheduleAnalysis(
            sheet_number=f"S-{page_num + 1}",
            device_schedule=device_schedule,
            panel_schedule=[],
            specifications={},
        )

    def _analyze_specifications(self, page, page_num: int) -> Dict[str, Any]:
        """Analyze specifications page"""
        text = page.get_text()

        return {
            "sheet_number": f"SPEC-{page_num + 1}",
            "content": text,
            "nfpa_references": self._extract_nfpa_references(text),
            "manufacturer_specs": self._extract_manufacturer_specs(text),
        }

    def _extract_rooms_from_text(self, text: str) -> List[Room]:
        """Extract room information from text"""
        rooms = []

        # Look for room patterns like "OFFICE 101", "CONFERENCE ROOM", etc.
        room_patterns = [
            r"(OFFICE|CONFERENCE|MEETING|STORAGE|LOBBY|CORRIDOR)\s*(\d*)",
            r"ROOM\s+(\d+)",
            r"(\w+)\s+ROOM",
        ]

        for pattern in room_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                room_name = match.group(0).strip()

                # Create room with default values (would need coordinates from drawing analysis)
                room = Room(
                    name=room_name,
                    number=None,
                    area=400.0,  # Default area - would extract from drawing
                    occupancy_type="Office",  # Default - would determine from context
                    ceiling_height=9.0,  # Default ceiling height
                    coordinates=[],  # Would extract from drawing analysis
                )
                rooms.append(room)

        return rooms

    def _extract_dimensions_from_text(self, text: str) -> Dict[str, float]:
        """Extract dimension information from text"""
        dimensions: Dict[str, float] = {}

        # Look for dimension patterns like "24'-0\"", "100'", "30 FT"
        dim_patterns = [
            r"(\d+)'-(\d+)\"",  # Feet and inches
            r"(\d+)'",  # Feet only
            r"(\d+)\s*FT",  # Feet with FT
            r"(\d+)\s*FEET",  # Feet with FEET
        ]

        for pattern in dim_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract and convert to feet
                if "'" in match.group(0):
                    parts = match.group(0).split("'")
                    feet = float(parts[0])
                    if len(parts) > 1 and '"' in parts[1]:
                        inches = float(parts[1].replace('"', "").replace("-", ""))
                        total_feet = feet + inches / 12.0
                    else:
                        total_feet = feet
                else:
                    total_feet = float(match.group(1))

                dimensions[f"dim_{len(dimensions)}"] = total_feet

        return dimensions

    def _detect_scale_from_text(self, text: str) -> str:
        """Detect drawing scale from text"""
        # Look for scale patterns
        scale_patterns = [
            r'1/4"?\s*=\s*1\'-0"?',  # 1/4" = 1'-0"
            r'1/8"?\s*=\s*1\'-0"?',  # 1/8" = 1'-0"
            r'1/16"?\s*=\s*1\'-0"?',  # 1/16" = 1'-0"
            r"SCALE:\s*([^\\n]+)",  # SCALE: ...
        ]

        for pattern in scale_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()

        return "Unknown Scale"

    def _extract_devices_from_text(self, text: str) -> List[FireAlarmDevice]:
        """Extract fire alarm devices from text"""
        devices = []

        # Device type patterns
        device_patterns = {
            DeviceType.SMOKE_DETECTOR: [r"SMOKE\s+DETECTOR", r"PHOTOELECTRIC", r"IONIZATION"],
            DeviceType.HEAT_DETECTOR: [r"HEAT\s+DETECTOR", r"THERMAL\s+DETECTOR"],
            DeviceType.PULL_STATION: [r"PULL\s+STATION", r"MANUAL\s+PULL", r"FIRE\s+ALARM\s+BOX"],
            DeviceType.HORN_STROBE: [r"HORN\s+STROBE", r"NOTIFICATION", r"SPEAKER\s+STROBE"],
        }

        for device_type, patterns in device_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    device = FireAlarmDevice(
                        device_type=device_type,
                        location=(0.0, 0.0),  # Would need coordinate extraction
                        model=None,
                        address=None,
                        circuit=None,
                        room=None,
                        notes=match.group(0),
                    )
                    devices.append(device)

        return devices

    def _extract_device_schedule(self, text: str) -> List[Dict[str, Any]]:
        """Extract device schedule information from text"""
        schedule = []

        # Look for tabular data patterns
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if any(
                device_term in line.lower()
                for device_term in ["smoke", "heat", "pull", "horn", "strobe"]
            ):
                # Parse schedule line (simplified)
                parts = line.split()
                if len(parts) >= 3:
                    schedule.append(
                        {
                            "device_type": parts[0],
                            "model": parts[1] if len(parts) > 1 else "",
                            "quantity": parts[2] if len(parts) > 2 else "1",
                            "description": " ".join(parts[3:]) if len(parts) > 3 else "",
                        }
                    )

        return schedule

    def _extract_nfpa_references(self, text: str) -> List[str]:
        """Extract NFPA code references from text"""
        references = []

        # NFPA reference patterns
        nfpa_patterns = [
            r"NFPA\s+\d+",
            r"NFPA\s+\d+-\d+",
            r"National\s+Fire\s+Protection\s+Association",
        ]

        for pattern in nfpa_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                references.append(match.group(0))

        return list(set(references))  # Remove duplicates

    def _extract_manufacturer_specs(self, text: str) -> List[str]:
        """Extract manufacturer specifications from text"""
        specs = []

        # Common fire alarm manufacturers
        manufacturers = [
            "Simplex",
            "Edwards",
            "Gamewell",
            "Notifier",
            "Fire-Lite",
            "Honeywell",
            "Johnson Controls",
            "Siemens",
            "Bosch",
        ]

        for manufacturer in manufacturers:
            if manufacturer.lower() in text.lower():
                # Find manufacturer references
                pattern = rf"{manufacturer}\s+[A-Z0-9-]+"
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    specs.append(match.group(0))

        return specs

    def _create_placeholder_analysis(self, pdf_path: str) -> ConstructionAnalysis:
        """Create placeholder analysis when PDF processing isn't available"""
        return ConstructionAnalysis(
            project_name="PDF Analysis Unavailable",
            analyzed_date=datetime.now(),
            pdf_path=pdf_path,
            total_pages=0,
            floor_plans=[],
            fire_alarm_plans=[],
            schedules=[],
            specifications=[],
        )

    def export_analysis_summary(self, analysis: ConstructionAnalysis, output_path: str):
        """Export analysis summary to text file"""
        with open(output_path, "w") as f:
            f.write("# Construction Set Analysis Summary\n\n")
            f.write(f"**Project:** {analysis.project_name}\n")
            f.write(f"**Analyzed:** {analysis.analyzed_date}\n")
            f.write(f"**Source:** {analysis.pdf_path}\n")
            f.write(f"**Total Pages:** {analysis.total_pages}\n\n")

            f.write(f"## Floor Plans ({len(analysis.floor_plans)})\n")
            for plan in analysis.floor_plans:
                f.write(f"- {plan.sheet_number}: {len(plan.rooms)} rooms, Scale: {plan.scale}\n")

            f.write(f"\n## Fire Alarm Plans ({len(analysis.fire_alarm_plans)})\n")
            for fa_plan in analysis.fire_alarm_plans:
                f.write(f"- {fa_plan.sheet_number}: {len(fa_plan.devices)} devices\n")

            f.write(f"\n## Schedules ({len(analysis.schedules)})\n")
            for schedule in analysis.schedules:
                f.write(f"- {schedule.sheet_number}: {len(schedule.device_schedule)} items\n")

            f.write(f"\n## Total Devices: {analysis.total_devices}\n")
            f.write(f"## Total Building Area: {analysis.total_building_area:.0f} sq ft\n")


# Factory function for easy usage
def analyze_construction_pdf(pdf_path: str) -> ConstructionAnalysis:
    """
    Convenient function to analyze a construction PDF

    Args:
        pdf_path: Path to construction document PDF

    Returns:
        ConstructionAnalysis with extracted data
    """
    analyzer = PDFConstructionAnalyzer()
    return analyzer.analyze_construction_set(pdf_path)
