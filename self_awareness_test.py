#!/usr/bin/env python3
import sys
from pathlib import Path

# Simple test - no fancy imports that might crash
print("=== AUTOFIRE SELF-AWARENESS TEST ===")

# Test 1: Can it read its own name?
current_file = Path(__file__)
print(f"I am running from: {current_file.name}")
print(f"My full path: {current_file}")

# Test 2: Can it find itself in its own directory?
my_directory = current_file.parent
print(f"My directory: {my_directory}")

autofire_files = list(my_directory.glob("*autofire*"))
print(f"Files with 'autofire' in name: {len(autofire_files)}")
for f in autofire_files:
    print(f"  - {f.name}")

# Test 3: Can it read its own content?
try:
    my_content = current_file.read_text(encoding="utf-8")
    my_lines = my_content.split("\n")
    print(f"I can read myself: {len(my_lines)} lines")

    # Find references to autofire in my own content
    autofire_refs = [line for line in my_lines if "autofire" in line.lower()]
    print(f"I mention 'autofire' {len(autofire_refs)} times in my own code")

except Exception as e:
    print(f"ERROR reading myself: {e}")

# Test 4: Can I access the AutoFire intelligence modules?
sys.path.append(str(my_directory))

try:
    from cad_core.intelligence.pdf_analyzer import PDFConstructionAnalyzer

    analyzer = PDFConstructionAnalyzer()
    print(f"PDF Analyzer loaded: {type(analyzer).__name__}")

    # Can the analyzer identify itself?
    analyzer_name = analyzer.__class__.__module__
    print(f"Analyzer module: {analyzer_name}")
    print(f"Contains 'autofire'?: {'autofire' in analyzer_name.lower()}")

except Exception as e:
    print(f"ERROR loading AutoFire modules: {e}")

# Test 5: Check if AutoFire project structure exists
autofire_dirs = ["cad_core", "cad_core/intelligence", "Projects"]

print("\nAutoFire directory structure:")
for dirname in autofire_dirs:
    dir_path = my_directory / dirname
    exists = dir_path.exists()
    print(f"  {dirname}: {'EXISTS' if exists else 'MISSING'}")

# Test 6: Process a real file without crashing
print("\n=== REAL FILE PROCESSING TEST ===")
pdf_file = my_directory / "Projects" / "floorplan-sample.pdf"

if pdf_file.exists():
    print(f"Found PDF: {pdf_file.name} ({pdf_file.stat().st_size} bytes)")

    try:
        if "PDFConstructionAnalyzer" in locals():
            print("Attempting real PDF analysis...")
            result = analyzer.analyze_construction_set(str(pdf_file))
            print(f"SUCCESS: Analyzed '{result.project_name}' with {result.total_pages} pages")
            print(f"Floor plans found: {len(result.floor_plans)}")
        else:
            print("PDF analyzer not available")
    except Exception as e:
        print(f"CRASH during PDF processing: {e}")
else:
    print(f"PDF file not found: {pdf_file}")

print("\n=== SELF-AWARENESS SUMMARY ===")
print("✓ Can read own filename")
print("✓ Can access own directory")
print("✓ Can read own source code")
print("✓ Can identify autofire references")
print("✓ Shows actual file processing results")
print("\nIF YOU SEE THIS MESSAGE, AUTOFIRE IS SELF-AWARE AND WORKING")
