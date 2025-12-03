#!/usr/bin/env python3
"""
AutoFire Real PDF Content Extractor
Actually extracts and displays specific information from construction drawings
"""

import re
from datetime import datetime
from pathlib import Path

import fitz  # PyMuPDF


class RealPDFContentExtractor:
    """
    Extracts actual text content and fire protection information from PDFs
    Shows what AutoFire really sees in the construction drawings
    """

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.extracted_data = {}

        # Fire protection patterns to search for
        self.fire_patterns = {
            "smoke_detectors": [
                r"SMOKE\s+DETECTOR",
                r"SMOKE\s+DET",
                r"SD\b",
                r"PHOTOELECTRIC",
                r"IONIZATION",
            ],
            "sprinklers": [
                r"SPRINKLER",
                r"SPR\b",
                r"FIRE\s+SPRINKLER",
                r"PENDANT",
                r"UPRIGHT",
                r"SIDEWALL",
            ],
            "fire_extinguishers": [
                r"FIRE\s+EXTINGUISHER",
                r"EXTINGUISHER",
                r"FE\b",
                r"CLASS\s+A",
                r"CLASS\s+B",
                r"CLASS\s+C",
            ],
            "fire_alarm": [
                r"FIRE\s+ALARM",
                r"PULL\s+STATION",
                r"HORN\s+STROBE",
                r"NOTIFICATION",
                r"FACP",
                r"FIRE\s+PANEL",
            ],
            "exit_signs": [r"EXIT\s+SIGN", r"EXIT\s+LIGHT", r"EMERGENCY\s+LIGHT", r"EGRESS"],
            "fire_doors": [r"FIRE\s+DOOR", r"FIRE\s+RATED", r"\d+\s*HR\s+FIRE", r"SELF\s+CLOSING"],
        }

        # NFPA and code patterns
        self.code_patterns = {
            "nfpa_codes": [r"NFPA\s*\d+", r"NATIONAL\s+FIRE\s+PROTECTION"],
            "building_codes": [
                r"IBC\s*\d*",
                r"INTERNATIONAL\s+BUILDING\s+CODE",
                r"UBC\s*\d*",
                r"UNIFORM\s+BUILDING\s+CODE",
            ],
            "electrical_codes": [r"NEC\s*\d*", r"NATIONAL\s+ELECTRICAL\s+CODE", r"ARTICLE\s+\d+"],
        }

    def extract_from_single_pdf(self, pdf_path: Path) -> dict:
        """Extract content from a single PDF file"""
        print(f"\n🔍 ANALYZING: {pdf_path.name}")
        print("=" * 50)

        extracted = {
            "filename": pdf_path.name,
            "full_text": "",
            "fire_devices": {},
            "codes_found": {},
            "room_labels": [],
            "dimensions": [],
            "notes": [],
            "page_count": 0,
        }

        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(str(pdf_path))
            extracted["page_count"] = len(doc)

            full_text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                full_text += f"\n--- PAGE {page_num + 1} ---\n{text}"

            extracted["full_text"] = full_text
            doc.close()

            # Extract fire protection devices
            self._extract_fire_devices(full_text, extracted)

            # Extract codes and standards
            self._extract_codes(full_text, extracted)

            # Extract room labels and notes
            self._extract_room_info(full_text, extracted)

            # Display findings
            self._display_extracted_content(extracted)

        except Exception as e:
            print(f"❌ Error processing {pdf_path.name}: {str(e)}")
            extracted["error"] = str(e)

        return extracted

    def _extract_fire_devices(self, text: str, extracted: dict):
        """Extract fire protection devices from text"""
        text_upper = text.upper()

        for device_type, patterns in self.fire_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.finditer(pattern, text_upper)
                for match in found:
                    # Get surrounding context
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end].strip()
                    matches.append({"pattern": pattern, "match": match.group(), "context": context})

            if matches:
                extracted["fire_devices"][device_type] = matches

    def _extract_codes(self, text: str, extracted: dict):
        """Extract building codes and standards"""
        text_upper = text.upper()

        for code_type, patterns in self.code_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.finditer(pattern, text_upper)
                for match in found:
                    start = max(0, match.start() - 30)
                    end = min(len(text), match.end() + 30)
                    context = text[start:end].strip()
                    matches.append({"code": match.group(), "context": context})

            if matches:
                extracted["codes_found"][code_type] = matches

    def _extract_room_info(self, text: str, extracted: dict):
        """Extract room labels, dimensions, and notes"""
        lines = text.split("\n")

        # Look for room labels (typically in caps)
        room_patterns = [
            r"^[A-Z\s]{3,20}$",  # All caps room names
            r"ROOM\s+\d+",
            r"SPACE\s+\d+",
            r"AREA\s+[A-Z]+",
        ]

        for line in lines:
            line = line.strip()
            if len(line) > 2 and len(line) < 50:
                for pattern in room_patterns:
                    if re.match(pattern, line.upper()):
                        extracted["room_labels"].append(line)

        # Look for dimensions
        dimension_patterns = [
            r"\d+\'\s*-?\s*\d*\"?",  # Feet and inches
            r"\d+\.\d+\'",  # Decimal feet
            r"\d+\s*x\s*\d+",  # Length x width
        ]

        for pattern in dimension_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                extracted["dimensions"].append(match.group())

        # Look for notes (lines starting with NOTE:, GENERAL:, etc.)
        note_patterns = [r"NOTE:.*", r"GENERAL:.*", r"FIRE\s+PROTECTION:.*", r"SAFETY:.*"]

        for pattern in note_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                extracted["notes"].append(match.group())

    def _display_extracted_content(self, extracted: dict):
        """Display the extracted content in organized format"""
        print(f"📄 Pages: {extracted['page_count']}")

        # Show fire devices found
        if extracted["fire_devices"]:
            print("\n🔥 FIRE PROTECTION DEVICES FOUND:")
            for device_type, matches in extracted["fire_devices"].items():
                print(f"\n   {device_type.replace('_', ' ').title()}:")
                for i, match in enumerate(matches[:3]):  # Show first 3 matches
                    print(f"      {i+1}. {match['match']} - {match['context'][:100]}...")
                if len(matches) > 3:
                    print(f"      ... and {len(matches) - 3} more")

        # Show codes found
        if extracted["codes_found"]:
            print("\n📋 CODES & STANDARDS FOUND:")
            for code_type, matches in extracted["codes_found"].items():
                print(f"\n   {code_type.replace('_', ' ').title()}:")
                for i, match in enumerate(matches[:3]):
                    print(f"      {i+1}. {match['code']} - {match['context'][:80]}...")

        # Show room labels
        if extracted["room_labels"]:
            print("\n🏠 ROOM LABELS DETECTED:")
            unique_rooms = list(set(extracted["room_labels"][:10]))  # Show first 10 unique
            for i, room in enumerate(unique_rooms):
                print(f"      {i+1}. {room}")

        # Show dimensions
        if extracted["dimensions"]:
            print("\n📏 DIMENSIONS FOUND:")
            unique_dims = list(set(extracted["dimensions"][:10]))
            for i, dim in enumerate(unique_dims):
                print(f"      {i+1}. {dim}")

        # Show notes
        if extracted["notes"]:
            print("\n📝 NOTES & SPECIFICATIONS:")
            for i, note in enumerate(extracted["notes"][:5]):
                print(f"      {i+1}. {note[:100]}...")

        print()

    def analyze_project(self, max_files: int = 5):
        """Analyze multiple PDFs from the project"""
        print("🔍 AUTOFIRE REAL PDF CONTENT EXTRACTION")
        print("=" * 45)
        print(f"📁 Project: {self.project_path}")
        print(f"⏰ Analysis Time: {datetime.now().strftime('%H:%M:%S')}")

        # Find PDF files
        pdf_files = list(self.project_path.glob("**/*.pdf"))

        if not pdf_files:
            print("❌ No PDF files found in project directory")
            return {}

        print(f"📋 Found {len(pdf_files)} PDF files")
        print(
            f"🎯 Analyzing first {min(max_files, len(pdf_files))} files for detailed content extraction"
        )

        # Process selected files
        for i, pdf_file in enumerate(pdf_files[:max_files]):
            print(f"\n📄 File {i+1}/{min(max_files, len(pdf_files))}")
            extracted = self.extract_from_single_pdf(pdf_file)
            self.extracted_data[pdf_file.name] = extracted

        # Summary
        self._generate_project_summary()

        return self.extracted_data

    def _generate_project_summary(self):
        """Generate summary of all extracted data"""
        print("\n" + "=" * 60)
        print("🎯 PROJECT EXTRACTION SUMMARY")
        print("=" * 60)

        total_devices = 0
        total_codes = 0
        total_rooms = 0

        for filename, data in self.extracted_data.items():
            if "fire_devices" in data:
                for device_type, matches in data["fire_devices"].items():
                    total_devices += len(matches)

            if "codes_found" in data:
                for code_type, matches in data["codes_found"].items():
                    total_codes += len(matches)

            if "room_labels" in data:
                total_rooms += len(data["room_labels"])

        print(f"📊 Total Fire Devices Detected: {total_devices}")
        print(f"📋 Total Code References Found: {total_codes}")
        print(f"🏠 Total Room Labels Found: {total_rooms}")
        print(f"📄 Files Processed: {len(self.extracted_data)}")

        print("\n✅ This is the REAL data AutoFire extracts from your construction drawings!")


def main():
    """Main function to run PDF content extraction"""
    # You can change this path to analyze different projects
    project_paths = [
        "C:/Dev/diventures full",
        "C:/Dev/hilton full spec",
        # Add more project paths here
    ]

    print("🔍 AUTOFIRE REAL CONTENT EXTRACTION")
    print("=" * 40)
    print("Select project to analyze:")

    for i, path in enumerate(project_paths):
        if Path(path).exists():
            print(f"   {i+1}. {Path(path).name}")

    # For demo, analyze the diventures project
    extractor = RealPDFContentExtractor("C:/Dev/diventures full")
    results = extractor.analyze_project(max_files=3)  # Analyze first 3 PDFs in detail

    print("\n🎯 EXTRACTION COMPLETE!")
    print("This shows exactly what AutoFire sees in your construction drawings.")


if __name__ == "__main__":
    main()
