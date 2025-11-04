#!/usr/bin/env python3
"""
NO BULLSHIT AUTOFIRE TEST
Just run the damn thing and show results
"""

import sys
import os
from pathlib import Path

def no_bullshit_test():
    print("=== NO BULLSHIT AUTOFIRE TEST ===")
    
    # Add path
    sys.path.append('C:/Dev/Autofire')
    
    # Test 1: Import without crashing
    print("1. Importing AutoFire modules...")
    try:
        from cad_core.intelligence.pdf_analyzer import PDFConstructionAnalyzer
        from cad_core.intelligence.rfi_engine import RFIIntelligenceEngine
        print("   SUCCESS: Modules imported")
    except Exception as e:
        print(f"   FAILED: {e}")
        return False
    
    # Test 2: Create objects
    print("2. Creating AI objects...")
    try:
        analyzer = PDFConstructionAnalyzer()
        rfi_engine = RFIIntelligenceEngine()
        print("   SUCCESS: Objects created")
    except Exception as e:
        print(f"   FAILED: {e}")
        return False
    
    # Test 3: Check if PDF exists
    print("3. Checking for PDF file...")
    pdf_path = "C:/Dev/Autofire/Projects/floorplan-sample.pdf"
    if os.path.exists(pdf_path):
        size = os.path.getsize(pdf_path)
        print(f"   SUCCESS: Found PDF ({size} bytes)")
    else:
        print("   FAILED: No PDF file")
        return False
    
    # Test 4: Process the PDF
    print("4. Processing PDF...")
    try:
        result = analyzer.analyze_construction_set(pdf_path)
        print(f"   SUCCESS: Project '{result.project_name}' analyzed")
        print(f"   Pages: {result.total_pages}")
        print(f"   Floor plans: {len(result.floor_plans)}")
    except Exception as e:
        print(f"   FAILED: {e}")
        return False
    
    # Test 5: Test RFI engine (the critical fix)
    print("5. Testing RFI engine...")
    try:
        rfi_result = rfi_engine.analyze_project_issues(result)
        print(f"   SUCCESS: RFI analysis complete")
        print(f"   Issues found: {len(rfi_result)}")
        print("   NO CRASH - FIX WORKING!")
    except Exception as e:
        print(f"   FAILED: {e}")
        return False
    
    # Test 6: Write proof file
    print("6. Writing proof file...")
    try:
        with open('NO_BULLSHIT_PROOF.txt', 'w') as f:
            f.write("AUTOFIRE NO BULLSHIT PROOF\n")
            f.write("=========================\n")
            f.write(f"Project: {result.project_name}\n")
            f.write(f"Pages: {result.total_pages}\n")
            f.write(f"Floor plans: {len(result.floor_plans)}\n")
            f.write(f"RFI issues: {len(rfi_result)}\n")
            f.write("Status: WORKING\n")
        print("   SUCCESS: Proof file written")
    except Exception as e:
        print(f"   FAILED: {e}")
        return False
    
    print("\n=== FINAL RESULT ===")
    print("AUTOFIRE IS WORKING - NO BULLSHIT")
    return True

if __name__ == "__main__":
    success = no_bullshit_test()
    if not success:
        print("AUTOFIRE FAILED")
        sys.exit(1)
    else:
        print("AUTOFIRE PASSED ALL TESTS")