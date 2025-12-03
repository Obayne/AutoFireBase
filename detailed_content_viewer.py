#!/usr/bin/env python3
"""
AutoFire Detailed Content Viewer
Shows exact text content and specific fire protection details extracted from PDFs
"""

import re
from pathlib import Path

import fitz  # PyMuPDF


class DetailedContentViewer:
    """
    Shows the actual text content AutoFire reads from construction drawings
    Displays specific fire protection specifications, room details, and hazard information
    """

    def __init__(self):
        self.detailed_patterns = {
            "fire_specifications": [
                r"FIRE\s+RATING\s*:\s*[\d\w\s-]+",
                r"FIRE\s+RESISTANT\s*[\d\w\s-]+",
                r"UL\s+LISTED\s*[\d\w\s-]+",
                r"NFPA\s+\d+\s*[\w\s-]*",
                r"SPRINKLER\s+HEAD\s*[\w\s\d-]*",
                r"SMOKE\s+DETECTOR\s*[\w\s\d-]*",
            ],
            "room_specifications": [
                r"OCCUPANCY\s*:\s*[\w\s\d-]+",
                r"OCCUPANT\s+LOAD\s*:\s*\d+",
                r"EGRESS\s*[\w\s\d-]*",
                r"ROOM\s+\d+\s*[\w\s-]*",
                r"AREA\s*:\s*[\d,\s]+\s*SF",
                r"CEILING\s+HEIGHT\s*:\s*[\d\'-\"]+",
            ],
            "fire_protection_details": [
                r"FIRE\s+EXTINGUISHER\s+TYPE\s*[\w\s\d-]*",
                r"SPRINKLER\s+COVERAGE\s*[\w\s\d-]*",
                r"ALARM\s+SYSTEM\s*[\w\s\d-]*",
                r"EMERGENCY\s+LIGHTING\s*[\w\s\d-]*",
                r"EXIT\s+SIGN\s*[\w\s\d-]*",
                r"FIRE\s+DOOR\s*[\w\s\d-]*",
            ],
            "hazardous_materials": [
                r"CHEMICAL\s+STORAGE\s*[\w\s\d-]*",
                r"FLAMMABLE\s*[\w\s\d-]*",
                r"COMBUSTIBLE\s*[\w\s\d-]*",
                r"HAZARDOUS\s*[\w\s\d-]*",
                r"POOL\s+CHEMICALS\s*[\w\s\d-]*",
                r"CHLORINE\s*[\w\s\d-]*",
            ],
        }

    def show_detailed_extraction(self, pdf_path: str, max_pages: int = 3):
        """Show detailed content extraction from a specific PDF"""
        path = Path(pdf_path)

        print("\n📋 DETAILED CONTENT EXTRACTION")
        print("=" * 50)
        print(f"File: {path.name}")
        print(f"Path: {pdf_path}")
        print()

        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)

            print(f"📄 Total Pages: {total_pages}")
            print(f"🔍 Analyzing first {min(max_pages, total_pages)} pages in detail")
            print()

            for page_num in range(min(max_pages, total_pages)):
                print(f"--- PAGE {page_num + 1} ANALYSIS ---")
                page = doc.load_page(page_num)
                text = page.get_text()

                # Show raw text sample
                self._show_raw_text_sample(text)

                # Extract and show specific details
                self._extract_and_show_details(text)

                print()

            doc.close()

        except Exception as e:
            print(f"❌ Error: {str(e)}")

    def _show_raw_text_sample(self, text: str):
        """Show a sample of the raw text extracted"""
        print("📝 RAW TEXT SAMPLE (first 300 characters):")
        print("-" * 40)
        sample = text[:300].replace("\n", " ").strip()
        print(f'"{sample}..."')
        print()

    def _extract_and_show_details(self, text: str):
        """Extract and display specific fire protection details"""

        for category, patterns in self.detailed_patterns.items():
            matches = []

            for pattern in patterns:
                found = re.finditer(pattern, text, re.IGNORECASE)
                for match in found:
                    # Get full line context
                    lines = text.split("\n")
                    match_line = None
                    for line in lines:
                        if match.group() in line:
                            match_line = line.strip()
                            break

                    if match_line:
                        matches.append({"match": match.group(), "full_line": match_line})

            if matches:
                category_name = category.replace("_", " ").title()
                print(f"🎯 {category_name}:")

                # Remove duplicates and show unique matches
                unique_matches = []
                seen = set()
                for match in matches:
                    key = match["full_line"]
                    if key not in seen and len(key.strip()) > 5:
                        unique_matches.append(match)
                        seen.add(key)

                for i, match in enumerate(unique_matches[:5]):  # Show first 5
                    print(f"   {i+1}. {match['full_line']}")

                if len(unique_matches) > 5:
                    print(f"   ... and {len(unique_matches) - 5} more")
                print()

    def analyze_specific_file(self, project_path: str, filename_pattern: str):
        """Analyze a specific file matching the pattern"""
        path = Path(project_path)

        # Find files matching pattern
        matching_files = []
        for pdf_file in path.glob("**/*.pdf"):
            if filename_pattern.lower() in pdf_file.name.lower():
                matching_files.append(pdf_file)

        if not matching_files:
            print(f"❌ No files found matching pattern: {filename_pattern}")
            return

        print(f"🔍 Found {len(matching_files)} files matching '{filename_pattern}':")
        for i, file in enumerate(matching_files[:3]):  # Show first 3
            print(f"   {i+1}. {file.name}")

        # Analyze the first matching file in detail
        if matching_files:
            self.show_detailed_extraction(str(matching_files[0]), max_pages=2)

    def show_fire_protection_summary(self, project_path: str):
        """Show a summary of fire protection information across multiple files"""
        path = Path(project_path)

        print("\n🔥 FIRE PROTECTION SUMMARY")
        print("=" * 35)
        print(f"Project: {path.name}")
        print()

        # Look for fire protection specific files
        fire_files = []
        for pdf_file in path.glob("**/*.pdf"):
            filename_lower = pdf_file.name.lower()
            if any(term in filename_lower for term in ["fire", "fp", "life safety", "alarm"]):
                fire_files.append(pdf_file)

        print(f"📄 Fire Protection Files Found: {len(fire_files)}")

        if fire_files:
            print("\nFire Protection Drawings:")
            for i, file in enumerate(fire_files[:10]):
                print(f"   {i+1}. {file.name}")

            # Analyze first fire protection file
            if fire_files:
                print(f"\n🔍 Detailed Analysis of: {fire_files[0].name}")
                self.show_detailed_extraction(str(fire_files[0]), max_pages=1)

        else:
            print("Looking in general files for fire protection content...")
            # Analyze general files for fire content
            all_files = list(path.glob("**/*.pdf"))
            if all_files:
                self.show_detailed_extraction(str(all_files[0]), max_pages=1)


def main():
    """Interactive content viewer"""
    viewer = DetailedContentViewer()

    print("🔍 AUTOFIRE DETAILED CONTENT VIEWER")
    print("=" * 40)
    print("Shows exactly what AutoFire extracts from your construction drawings")
    print()

    # Available projects
    projects = {
        "1": ("C:/Dev/diventures full", "Diventures Aquatic Center"),
        "2": ("C:/Dev/hilton full spec", "Hilton Hotel Project"),
    }

    print("Available Projects:")
    for key, (path, name) in projects.items():
        if Path(path).exists():
            print(f"   {key}. {name}")

    print()

    # For demonstration, show detailed analysis of both projects

    # 1. Show fire protection summary for Diventures
    print("🏊 DIVENTURES AQUATIC CENTER - FIRE PROTECTION ANALYSIS")
    viewer.show_fire_protection_summary("C:/Dev/diventures full")

    # 2. Show specific file analysis for Hilton
    print("\n" + "=" * 60)
    print("🏨 HILTON HOTEL - FIRE PROTECTION ANALYSIS")
    viewer.show_fire_protection_summary("C:/Dev/hilton full spec")

    # 3. Show specific pattern analysis
    print("\n" + "=" * 60)
    print("🎯 SPECIFIC FILE ANALYSIS")
    print("Looking for electrical fire protection in Diventures...")
    viewer.analyze_specific_file("C:/Dev/diventures full", "electrical")

    print("\n✅ EXTRACTION COMPLETE!")
    print("This shows the actual text content and specifications")
    print("that AutoFire processes to generate fire protection designs.")


if __name__ == "__main__":
    main()
