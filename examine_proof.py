#!/usr/bin/env python3
"""
PROVE WHAT AUTOFIRE ACTUALLY FOUND IN THE CONSTRUCTION SET
"""

import sys

sys.path.append("C:/Dev/Autofire")


def examine_autofire_analysis():
    from cad_core.intelligence.pdf_analyzer import PDFConstructionAnalyzer

    analyzer = PDFConstructionAnalyzer()
    result = analyzer.analyze_construction_set(
        "C:/Dev/rfp-24-001-general-contractor-construction-drawings.pdf"
    )

    print("AUTOFIRE ANALYSIS EXAMINATION:")
    print("=" * 40)
    print(f"Project: {result.project_name}")
    print(f"Pages: {result.total_pages}")
    print(f"Floor Plans: {len(result.floor_plans)}")
    print()

    if result.floor_plans:
        print("FIRST FLOOR PLAN DETAILS:")
        fp = result.floor_plans[0]
        print(f"Type: {type(fp)}")
        print(f"Sheet Number: {fp.sheet_number}")
        print(f"PDF Page: {fp.pdf_page}")
        print()

        print("ALL FLOOR PLAN SHEET NUMBERS:")
        for i, fp in enumerate(result.floor_plans):
            print(f"{i+1:2d}. {fp.sheet_number}")
            if i >= 10:  # Show first 10
                print(f"    ... and {len(result.floor_plans)-10} more")
                break
    else:
        print("NO FLOOR PLANS FOUND")

    print()
    print("QUESTION: Does this prove AutoFire intelligently processed the construction set?")
    print("ANSWER: It shows AutoFire extracted sheet numbers and page references.")
    print("        But does NOT prove it understood the actual architectural content.")


if __name__ == "__main__":
    examine_autofire_analysis()
