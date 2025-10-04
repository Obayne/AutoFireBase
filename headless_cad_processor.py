#!/usr/bin/env python3
"""
AutoFire CAD Features - Headless Processing
Run overnight to enhance CAD capabilities and drawing generation
"""

import json
import logging
import os
import sqlite3
import time

# Setup logging for overnight processing
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("cad_processing.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class HeadlessCADProcessor:
    """Process CAD features without UI - runs overnight."""

    def __init__(self):
        self.start_time = time.time()
        logger.info("🚀 Starting Headless CAD Processing...")

    def process_device_symbols(self):
        """Generate CAD symbols for all devices in database."""
        logger.info("📐 Processing device symbols...")

        try:
            conn = sqlite3.connect("autofire.db")
            cursor = conn.cursor()

            # Get all devices
            cursor.execute("SELECT id, model, name, symbol FROM devices")
            devices = cursor.fetchall()

            symbol_library = {}

            for device_id, model, name, symbol in devices:
                # Create standardized CAD symbol data
                cad_symbol = {
                    "id": device_id,
                    "model": model,
                    "name": name,
                    "symbol": symbol or self._generate_default_symbol(name),
                    "cad_properties": {
                        "layer": self._determine_layer(name),
                        "color": self._determine_color(name),
                        "line_weight": self._determine_line_weight(name),
                        "block_name": (
                            f"AF_{model.replace('-', '_')}" if model else f"AF_DEVICE_{device_id}"
                        ),
                    },
                    "geometry": self._generate_symbol_geometry(name),
                    "attributes": {
                        "model": model,
                        "description": name,
                        "manufacturer": "TBD",  # Will be filled from manufacturer table
                        "installation_height": self._get_installation_height(name),
                    },
                }

                symbol_library[device_id] = cad_symbol

            conn.close()

            # Save symbol library
            with open("cad_symbol_library.json", "w") as f:
                json.dump(symbol_library, f, indent=2)

            logger.info(f"✅ Generated {len(symbol_library)} CAD symbols")
            return symbol_library

        except Exception as e:
            logger.error(f"❌ Error processing device symbols: {e}")
            return {}

    def _generate_default_symbol(self, device_name):
        """Generate default symbol based on device name."""
        name_lower = device_name.lower()

        if "smoke" in name_lower:
            return "SD"
        elif "heat" in name_lower:
            return "HD"
        elif "pull" in name_lower:
            return "PS"
        elif "horn" in name_lower or "strobe" in name_lower:
            return "HS"
        elif "speaker" in name_lower:
            return "SPK"
        elif "panel" in name_lower:
            return "FACP"
        else:
            return "DEV"

    def _determine_layer(self, device_name):
        """Determine CAD layer for device."""
        name_lower = device_name.lower()

        if "panel" in name_lower:
            return "FIRE-PANEL"
        elif any(word in name_lower for word in ["smoke", "heat", "detector"]):
            return "FIRE-DETECTION"
        elif any(word in name_lower for word in ["horn", "strobe", "speaker"]):
            return "FIRE-NOTIFICATION"
        elif "pull" in name_lower:
            return "FIRE-MANUAL"
        else:
            return "FIRE-MISC"

    def _determine_color(self, device_name):
        """Determine CAD color for device."""
        name_lower = device_name.lower()

        if "panel" in name_lower:
            return "RED"
        elif any(word in name_lower for word in ["smoke", "heat"]):
            return "BLUE"
        elif any(word in name_lower for word in ["horn", "strobe"]):
            return "MAGENTA"
        elif "pull" in name_lower:
            return "GREEN"
        else:
            return "WHITE"

    def _determine_line_weight(self, device_name):
        """Determine line weight for device symbol."""
        name_lower = device_name.lower()

        if "panel" in name_lower:
            return 0.7  # Heavy weight for panels
        else:
            return 0.35  # Standard weight for devices

    def _generate_symbol_geometry(self, device_name):
        """Generate basic geometry for CAD symbol."""
        name_lower = device_name.lower()

        if "smoke" in name_lower:
            return {"type": "circle", "radius": 6, "center": [0, 0], "text": "SD", "text_size": 3}
        elif "heat" in name_lower:
            return {"type": "square", "size": 8, "center": [0, 0], "text": "HD", "text_size": 3}
        elif "pull" in name_lower:
            return {
                "type": "rectangle",
                "width": 12,
                "height": 8,
                "center": [0, 0],
                "text": "PS",
                "text_size": 3,
            }
        elif "horn" in name_lower or "strobe" in name_lower:
            return {"type": "triangle", "size": 10, "center": [0, 0], "text": "HS", "text_size": 3}
        elif "panel" in name_lower:
            return {
                "type": "rectangle",
                "width": 24,
                "height": 16,
                "center": [0, 0],
                "text": "FACP",
                "text_size": 6,
            }
        else:
            return {"type": "circle", "radius": 4, "center": [0, 0], "text": "?", "text_size": 3}

    def _get_installation_height(self, device_name):
        """Get typical installation height for device."""
        name_lower = device_name.lower()

        if any(word in name_lower for word in ["smoke", "heat"]):
            return "CEILING"
        elif "pull" in name_lower:
            return '48" AFF'
        elif any(word in name_lower for word in ["horn", "strobe"]):
            return '80" AFF'
        elif "panel" in name_lower:
            return '60" AFF'
        else:
            return "TBD"

    def generate_drawing_templates(self):
        """Generate AutoCAD drawing templates."""
        logger.info("📋 Generating drawing templates...")

        templates = {
            "fire_alarm_plan": {
                "name": "Fire Alarm Plan Template",
                "layers": [
                    {"name": "FIRE-DETECTION", "color": "BLUE", "linetype": "CONTINUOUS"},
                    {"name": "FIRE-NOTIFICATION", "color": "MAGENTA", "linetype": "CONTINUOUS"},
                    {"name": "FIRE-MANUAL", "color": "GREEN", "linetype": "CONTINUOUS"},
                    {"name": "FIRE-PANEL", "color": "RED", "linetype": "CONTINUOUS"},
                    {"name": "FIRE-WIRING", "color": "CYAN", "linetype": "DASHED"},
                    {"name": "FIRE-TEXT", "color": "WHITE", "linetype": "CONTINUOUS"},
                ],
                "text_styles": [
                    {"name": "FIRE_NOTES", "height": 0.125, "font": "Arial"},
                    {"name": "FIRE_LABELS", "height": 0.1, "font": "Arial"},
                    {"name": "FIRE_TITLE", "height": 0.25, "font": "Arial Bold"},
                ],
                "dimension_style": {"name": "FIRE_DIM", "text_height": 0.125, "arrow_size": 0.125},
            },
            "riser_diagram": {
                "name": "Fire Alarm Riser Diagram Template",
                "layers": [
                    {"name": "RISER-PANELS", "color": "RED", "linetype": "CONTINUOUS"},
                    {"name": "RISER-LOOPS", "color": "BLUE", "linetype": "CONTINUOUS"},
                    {"name": "RISER-NAC", "color": "MAGENTA", "linetype": "CONTINUOUS"},
                    {"name": "RISER-TEXT", "color": "WHITE", "linetype": "CONTINUOUS"},
                ],
            },
        }

        # Save templates
        with open("cad_templates.json", "w") as f:
            json.dump(templates, f, indent=2)

        logger.info(f"✅ Generated {len(templates)} drawing templates")
        return templates

    def process_coverage_calculations(self):
        """Calculate device coverage areas for CAD placement."""
        logger.info("📏 Processing coverage calculations...")

        coverage_data = {
            "smoke_detectors": {
                "standard_spacing": 30,  # feet
                "max_area": 900,  # sq ft (30x30)
                "placement_rules": [
                    "Maximum 30 feet between detectors",
                    "Maximum 15 feet from walls",
                    "Avoid air vents and high airflow areas",
                    "Consider ceiling height adjustments",
                ],
            },
            "heat_detectors": {
                "standard_spacing": 50,  # feet
                "max_area": 2500,  # sq ft (50x50)
                "placement_rules": [
                    "Maximum 50 feet between detectors",
                    "Maximum 25 feet from walls",
                    "Suitable for high heat areas",
                    "Consider temperature rating",
                ],
            },
            "horn_strobes": {
                "coverage_rules": [
                    "75 dB minimum sound level",
                    "15 dB above ambient noise",
                    "Visual notification: 15 cd minimum",
                    "Wall mount: 80 inches AFF typical",
                ]
            },
            "pull_stations": {
                "placement_rules": [
                    "Maximum 200 feet travel distance",
                    "48 inches AFF mounting height",
                    "Near exits and egress paths",
                    "Clearly visible and accessible",
                ]
            },
        }

        # Save coverage data
        with open("coverage_calculations.json", "w") as f:
            json.dump(coverage_data, f, indent=2)

        logger.info("✅ Coverage calculations complete")
        return coverage_data

    def generate_installation_guides(self):
        """Generate installation guides for different complexity levels."""
        logger.info("📖 Generating installation guides...")

        guides = {
            "firelite_simple": {
                "title": "FIRELITE Simple Installation Guide",
                "complexity": 1,
                "steps": [
                    '1. Mount panel 60" AFF in secure location',
                    "2. Run 18 AWG SLC wiring to device locations",
                    "3. Install devices with proper addressing",
                    "4. Connect NAC circuits for notification devices",
                    "5. Program panel using front panel controls",
                    "6. Test system per NFPA 72 requirements",
                ],
                "wiring_notes": [
                    "Use 18-22 AWG wire for SLC circuits",
                    "Install EOL resistors at end of each circuit",
                    "Maintain proper wire supervision",
                    "Label all circuits clearly",
                ],
            },
            "gamewell_advanced": {
                "title": "GAMEWELL Advanced Installation Guide",
                "complexity": 4,
                "steps": [
                    "1. Design system using CamWorks CAD",
                    "2. Configure modular cabinet with interface cards",
                    "3. Install custom interface modules per design",
                    "4. Program complex cause-and-effect logic",
                    "5. Integrate with building management systems",
                    "6. Commission and test advanced features",
                ],
                "camworks_integration": [
                    "3D cabinet design and layout",
                    "Automated wire routing documentation",
                    "Integration with building CAD",
                    "Professional drawing generation",
                ],
            },
        }

        # Save installation guides
        with open("installation_guides.json", "w") as f:
            json.dump(guides, f, indent=2)

        logger.info(f"✅ Generated {len(guides)} installation guides")
        return guides

    def run_overnight_processing(self):
        """Run all CAD processing tasks overnight."""
        logger.info("🌙 Starting overnight CAD processing...")

        tasks = [
            ("Device Symbols", self.process_device_symbols),
            ("Drawing Templates", self.generate_drawing_templates),
            ("Coverage Calculations", self.process_coverage_calculations),
            ("Installation Guides", self.generate_installation_guides),
        ]

        results = {}

        for task_name, task_func in tasks:
            logger.info(f"🔄 Processing: {task_name}")
            try:
                start_time = time.time()
                result = task_func()
                end_time = time.time()

                results[task_name] = {
                    "status": "SUCCESS",
                    "duration": end_time - start_time,
                    "data": result,
                }

                logger.info(f"✅ {task_name} completed in {end_time - start_time:.2f} seconds")

            except Exception as e:
                logger.error(f"❌ {task_name} failed: {e}")
                results[task_name] = {"status": "FAILED", "error": str(e)}

        # Save processing results
        total_time = time.time() - self.start_time

        summary = {
            "start_time": self.start_time,
            "total_duration": total_time,
            "tasks": results,
            "files_generated": [
                "cad_symbol_library.json",
                "cad_templates.json",
                "coverage_calculations.json",
                "installation_guides.json",
            ],
        }

        with open("cad_processing_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"🎉 Overnight processing complete! Total time: {total_time:.2f} seconds")
        logger.info("📁 Generated files:")
        for file in summary["files_generated"]:
            if os.path.exists(file):
                logger.info(f"   ✅ {file}")
            else:
                logger.info(f"   ❌ {file} (missing)")

        return summary


if __name__ == "__main__":
    processor = HeadlessCADProcessor()

    # Check if running as overnight script
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--overnight":
        logger.info("🌙 Running in overnight mode...")
        processor.run_overnight_processing()
    else:
        logger.info("🔧 Running individual tasks...")
        processor.process_device_symbols()
        processor.generate_drawing_templates()
        processor.process_coverage_calculations()
        processor.generate_installation_guides()

    logger.info("🏁 CAD processing complete!")
