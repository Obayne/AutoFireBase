#!/usr/bin/env python3
"""
AutoFire Multi-Project Content Extractor
Shows real extracted data from different project types with specific hazards
"""

import re
from pathlib import Path

import fitz  # PyMuPDF


class MultiProjectExtractor:
    """
    Extracts content from multiple project types showing building-specific hazards
    """

    def __init__(self):
        self.projects = {}

        # Building-specific hazard patterns
        self.hazard_patterns = {
            "hotel_hazards": [
                r"GUEST\s+ROOM",
                r"SLEEPING\s+ROOM",
                r"CORRIDOR",
                r"EGRESS",
                r"ASSEMBLY\s+OCCUPANCY",
            ],
            "pool_hazards": [
                r"POOL\s+DECK",
                r"NATATORIUM",
                r"CHEMICAL\s+STORAGE",
                r"POOL\s+EQUIPMENT",
                r"AQUATIC",
                r"CHLORINE",
            ],
            "electrical_hazards": [
                r"ELECTRICAL\s+ROOM",
                r"PANEL\s+BOARD",
                r"TRANSFORMER",
                r"HIGH\s+VOLTAGE",
                r"SWITCHGEAR",
            ],
            "mechanical_hazards": [
                r"BOILER\s+ROOM",
                r"MECHANICAL\s+ROOM",
                r"HVAC",
                r"GAS\s+LINE",
                r"FUEL",
            ],
            "storage_hazards": [
                r"STORAGE",
                r"WAREHOUSE",
                r"HAZARDOUS\s+MATERIAL",
                r"FLAMMABLE",
                r"COMBUSTIBLE",
            ],
        }

        # Fire protection system types
        self.system_patterns = {
            "detection_systems": [
                r"FIRE\s+DETECTION",
                r"SMOKE\s+DETECTION\s+SYSTEM",
                r"HEAT\s+DETECTOR",
                r"BEAM\s+DETECTOR",
            ],
            "suppression_systems": [
                r"SPRINKLER\s+SYSTEM",
                r"DELUGE\s+SYSTEM",
                r"FOAM\s+SYSTEM",
                r"CO2\s+SYSTEM",
                r"CLEAN\s+AGENT",
            ],
            "notification_systems": [
                r"MASS\s+NOTIFICATION",
                r"VOICE\s+EVACUATION",
                r"EMERGENCY\s+COMMUNICATION",
            ],
        }

    def extract_project_content(self, project_path: str, project_name: str, max_files: int = 3):
        """Extract content from a specific project"""
        print(f"\n🏗️  ANALYZING PROJECT: {project_name.upper()}")
        print("=" * 60)

        path = Path(project_path)
        if not path.exists():
            print(f"❌ Project path not found: {project_path}")
            return

        # Find PDF files
        pdf_files = list(path.glob("**/*.pdf"))
        print(f"📄 Found {len(pdf_files)} PDF files in {project_name}")

        project_data = {
            "name": project_name,
            "path": project_path,
            "total_files": len(pdf_files),
            "files_analyzed": [],
            "hazards_identified": {},
            "fire_systems": {},
            "specific_risks": [],
        }

        # Analyze select files
        for i, pdf_file in enumerate(pdf_files[:max_files]):
            print(f"\n📋 Analyzing: {pdf_file.name}")

            try:
                doc = fitz.open(str(pdf_file))
                full_text = ""

                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    full_text += text

                doc.close()

                # Extract project-specific data
                file_data = self._analyze_file_content(pdf_file.name, full_text)
                project_data["files_analyzed"].append(file_data)

                # Show immediate findings
                self._display_file_findings(pdf_file.name, file_data)

            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

        # Aggregate project hazards
        self._aggregate_project_hazards(project_data)

        # Display project summary
        self._display_project_summary(project_data)

        self.projects[project_name] = project_data
        return project_data

    def _analyze_file_content(self, filename: str, text: str):
        """Analyze content of a single file"""
        text_upper = text.upper()

        file_data = {
            "filename": filename,
            "hazards": {},
            "fire_systems": {},
            "critical_areas": [],
            "special_requirements": [],
        }

        # Check for specific hazards
        for hazard_type, patterns in self.hazard_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.finditer(pattern, text_upper)
                for match in found:
                    start = max(0, match.start() - 40)
                    end = min(len(text), match.end() + 40)
                    context = text[start:end].strip()
                    matches.append({"term": match.group(), "context": context})

            if matches:
                file_data["hazards"][hazard_type] = matches

        # Check for fire protection systems
        for system_type, patterns in self.system_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.finditer(pattern, text_upper)
                for match in found:
                    start = max(0, match.start() - 40)
                    end = min(len(text), match.end() + 40)
                    context = text[start:end].strip()
                    matches.append({"system": match.group(), "context": context})

            if matches:
                file_data["fire_systems"][system_type] = matches

        return file_data

    def _display_file_findings(self, filename: str, file_data: dict):
        """Display findings for a single file"""
        if file_data["hazards"]:
            print("   🚨 HAZARDS IDENTIFIED:")
            for hazard_type, matches in file_data["hazards"].items():
                hazard_name = hazard_type.replace("_", " ").title()
                print(f"      • {hazard_name}: {len(matches)} references")
                # Show first match as example
                if matches:
                    print(f"        Example: \"{matches[0]['context'][:60]}...\"")

        if file_data["fire_systems"]:
            print("   🔥 FIRE SYSTEMS DETECTED:")
            for system_type, matches in file_data["fire_systems"].items():
                system_name = system_type.replace("_", " ").title()
                print(f"      • {system_name}: {len(matches)} references")

    def _aggregate_project_hazards(self, project_data: dict):
        """Aggregate hazards across all files in project"""
        all_hazards = {}
        all_systems = {}

        for file_data in project_data["files_analyzed"]:
            for hazard_type, matches in file_data["hazards"].items():
                if hazard_type not in all_hazards:
                    all_hazards[hazard_type] = 0
                all_hazards[hazard_type] += len(matches)

            for system_type, matches in file_data["fire_systems"].items():
                if system_type not in all_systems:
                    all_systems[system_type] = 0
                all_systems[system_type] += len(matches)

        project_data["hazards_identified"] = all_hazards
        project_data["fire_systems"] = all_systems

    def _display_project_summary(self, project_data: dict):
        """Display summary for the project"""
        print(f"\n📊 PROJECT SUMMARY: {project_data['name'].upper()}")
        print("-" * 40)

        if project_data["hazards_identified"]:
            print("🚨 PRIMARY HAZARDS IDENTIFIED:")
            for hazard_type, count in project_data["hazards_identified"].items():
                hazard_name = hazard_type.replace("_", " ").title()
                print(f"   • {hazard_name}: {count} references")

        if project_data["fire_systems"]:
            print("\n🔥 FIRE PROTECTION SYSTEMS:")
            for system_type, count in project_data["fire_systems"].items():
                system_name = system_type.replace("_", " ").title()
                print(f"   • {system_name}: {count} references")

        # Project-specific recommendations
        self._generate_project_recommendations(project_data)

    def _generate_project_recommendations(self, project_data: dict):
        """Generate project-specific fire protection recommendations"""
        print("\n💡 AUTOFIRE RECOMMENDATIONS:")

        hazards = project_data["hazards_identified"]

        if "hotel_hazards" in hazards:
            print("   🏨 HOTEL OCCUPANCY DETECTED:")
            print("      • Install smoke detectors in all guest rooms")
            print("      • Corridor sprinkler coverage required")
            print("      • Emergency voice communication system")
            print("      • Guest room notification devices (ADA compliant)")

        if "pool_hazards" in hazards:
            print("   🏊 AQUATIC FACILITY DETECTED:")
            print("      • Pool deck fire protection required")
            print("      • Chemical storage fire suppression")
            print("      • Natatorium smoke evacuation system")
            print("      • Pool equipment room sprinklers")

        if "electrical_hazards" in hazards:
            print("   ⚡ ELECTRICAL HAZARDS DETECTED:")
            print("      • Electrical room fire suppression")
            print("      • Arc flash protection required")
            print("      • Class C fire extinguishers")
            print("      • Emergency electrical shutdown")

        if "mechanical_hazards" in hazards:
            print("   🔧 MECHANICAL HAZARDS DETECTED:")
            print("      • Boiler room fire protection")
            print("      • HVAC fire/smoke dampers")
            print("      • Fuel storage fire suppression")
            print("      • Emergency shutdown systems")

    def compare_projects(self):
        """Compare hazards across different projects"""
        if len(self.projects) < 2:
            return

        print("\n" + "=" * 70)
        print("🔍 MULTI-PROJECT HAZARD COMPARISON")
        print("=" * 70)

        for project_name, project_data in self.projects.items():
            print(f"\n🏗️  {project_name.upper()}:")
            print(
                f"   📄 Files: {project_data['total_files']} total, {len(project_data['files_analyzed'])} analyzed"
            )

            if project_data["hazards_identified"]:
                print("   🚨 Top Hazards:")
                sorted_hazards = sorted(
                    project_data["hazards_identified"].items(), key=lambda x: x[1], reverse=True
                )
                for hazard, count in sorted_hazards[:3]:
                    print(f"      • {hazard.replace('_', ' ').title()}: {count}")

        print("\n✅ AutoFire identifies building-specific hazards and recommends")
        print("   appropriate fire protection systems for each project type!")


def main():
    """Analyze multiple projects showing different hazard types"""
    extractor = MultiProjectExtractor()

    print("🔍 AUTOFIRE MULTI-PROJECT HAZARD ANALYSIS")
    print("=" * 50)
    print("Analyzing different building types to show specific hazards")

    # Analyze Diventures (Aquatic Facility)
    extractor.extract_project_content(
        "C:/Dev/diventures full", "Diventures Aquatic Center", max_files=2
    )

    # Analyze Hilton (Hotel)
    extractor.extract_project_content("C:/Dev/hilton full spec", "Hilton Hotel", max_files=2)

    # Compare projects
    extractor.compare_projects()

    print("\n🎯 CONCLUSION:")
    print("AutoFire automatically identifies building-specific hazards")
    print("and provides tailored fire protection recommendations!")


if __name__ == "__main__":
    main()
