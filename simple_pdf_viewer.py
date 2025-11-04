#!/usr/bin/env python3
"""
Simple PDF Text Extractor - Shows Raw Content
Displays the actual text content AutoFire reads from construction drawings
"""

from pathlib import Path

import fitz  # PyMuPDF


class SimplePDFViewer:
    """Simple viewer to show actual PDF text content"""

    def show_pdf_content(self, pdf_path: str, max_lines: int = 50):
        """Show the actual text content from a PDF"""
        path = Path(pdf_path)

        print("\n📄 PDF CONTENT ANALYSIS")
        print("=" * 50)
        print(f"File: {path.name}")
        print()

        try:
            doc = fitz.open(pdf_path)
            print(f"📋 Total Pages: {len(doc)}")

            # Get text from first page
            if len(doc) > 0:
                page = doc.load_page(0)
                text = page.get_text()

                # Split into lines and show
                lines = text.split("\n")
                print(f"📝 First {min(max_lines, len(lines))} lines of text:")
                print("-" * 40)

                for i, line in enumerate(lines[:max_lines]):
                    if line.strip():  # Only show non-empty lines
                        print(f"{i+1:3d}: {line.strip()}")

                if len(lines) > max_lines:
                    print(f"... and {len(lines) - max_lines} more lines")

                print()

                # Look for specific fire protection terms
                self._highlight_fire_terms(text)

            doc.close()

        except Exception as e:
            print(f"❌ Error reading PDF: {str(e)}")

    def _highlight_fire_terms(self, text: str):
        """Highlight fire protection related terms found in text"""
        print("🔥 FIRE PROTECTION TERMS FOUND:")
        print("-" * 35)

        fire_terms = [
            "FIRE",
            "SMOKE",
            "SPRINKLER",
            "EXTINGUISHER",
            "ALARM",
            "EXIT",
            "EMERGENCY",
            "NFPA",
            "IBC",
            "DETECTION",
            "SUPPRESSION",
            "EGRESS",
            "SAFETY",
        ]

        text_upper = text.upper()
        found_terms = {}

        for term in fire_terms:
            count = text_upper.count(term)
            if count > 0:
                found_terms[term] = count

        if found_terms:
            # Sort by frequency
            sorted_terms = sorted(found_terms.items(), key=lambda x: x[1], reverse=True)
            for term, count in sorted_terms:
                print(f"   • {term}: {count} occurrences")
        else:
            print("   No fire protection terms found on first page")

        print()

    def analyze_fire_protection_file(self, project_path: str):
        """Find and analyze fire protection specific files"""
        path = Path(project_path)

        print("🔍 SEARCHING FOR FIRE PROTECTION FILES")
        print("=" * 45)
        print(f"Project: {path.name}")
        print()

        # Find fire-related files
        fire_files = []
        all_files = list(path.glob("**/*.pdf"))

        for pdf_file in all_files:
            filename_lower = pdf_file.name.lower()
            if any(
                term in filename_lower
                for term in ["fire", "fp", "life safety", "ls", "alarm", "sprinkler"]
            ):
                fire_files.append(pdf_file)

        print(f"📄 Found {len(fire_files)} fire protection related files:")
        for i, file in enumerate(fire_files[:10]):
            print(f"   {i+1}. {file.name}")

        # Show content from first fire protection file
        if fire_files:
            print(f"\n🔍 Analyzing: {fire_files[0].name}")
            self.show_pdf_content(str(fire_files[0]), max_lines=30)
        else:
            print("\n🔍 No dedicated fire protection files found.")
            print("Analyzing general project file...")
            if all_files:
                self.show_pdf_content(str(all_files[0]), max_lines=20)

    def compare_building_types(self):
        """Compare content from different building types"""
        projects = [
            ("C:/Dev/diventures full", "Aquatic Center"),
            ("C:/Dev/hilton full spec", "Hotel Project"),
        ]

        print("🏗️  BUILDING TYPE COMPARISON")
        print("=" * 35)

        for project_path, project_name in projects:
            if Path(project_path).exists():
                print(f"\n📊 {project_name.upper()}:")
                self.analyze_fire_protection_file(project_path)
                print("\n" + "-" * 60)


def main():
    """Show actual PDF content from construction drawings"""
    viewer = SimplePDFViewer()

    print("📖 AUTOFIRE PDF CONTENT VIEWER")
    print("=" * 35)
    print("Shows the actual text AutoFire reads from your construction drawings")
    print()

    # Show content comparison between building types
    viewer.compare_building_types()

    # Specific file analysis
    print("\n🎯 SPECIFIC FILE ANALYSIS")
    print("=" * 28)

    # Show detailed content from a specific electrical file
    elec_file = "C:/Dev/diventures full/Drawings/088 E000 - ELECTRICAL COVER SHEET.pdf"
    if Path(elec_file).exists():
        print("📋 ELECTRICAL COVER SHEET CONTENT:")
        viewer.show_pdf_content(elec_file, max_lines=25)

    # Show content from a fire protection file
    fire_file = "C:/Dev/hilton full spec/Drawings/08 Fire Protection/FP0.1 - GENERAL NOTES SCHEDULES AND LEGEND.pdf"
    if Path(fire_file).exists():
        print("📋 FIRE PROTECTION LEGEND CONTENT:")
        viewer.show_pdf_content(fire_file, max_lines=25)

    print("\n✅ CONTENT EXTRACTION COMPLETE!")
    print("This is the REAL text data AutoFire processes to understand")
    print("fire protection requirements and generate appropriate designs.")


if __name__ == "__main__":
    main()
