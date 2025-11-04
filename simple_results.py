#!/usr/bin/env python3
"""
Simple Results Test - No Unicode Issues
"""

import sys
sys.path.append('C:/Dev/Autofire')

def show_actual_results():
    """Show the actual working results"""
    
    print("=== AUTOFIRE AI ACTUAL RESULTS ===")
    
    try:
        from cad_core.intelligence.pdf_analyzer import PDFConstructionAnalyzer
        from cad_core.intelligence.rfi_engine import RFIIntelligenceEngine
        from pathlib import Path
        
        # Process real PDF
        analyzer = PDFConstructionAnalyzer()
        rfi_engine = RFIIntelligenceEngine()
        
        pdf_path = Path('C:/Dev/Autofire/Projects/floorplan-sample.pdf')
        
        print(f"Processing: {pdf_path}")
        print(f"File exists: {pdf_path.exists()}")
        print(f"File size: {pdf_path.stat().st_size} bytes")
        
        # Real processing
        analysis = analyzer.analyze_construction_set(pdf_path)
        
        print("\n=== PDF ANALYSIS RESULTS ===")
        print(f"Project: {analysis.project_name}")
        print(f"Pages: {analysis.total_pages}")
        print(f"Floor plans: {len(analysis.floor_plans)}")
        print(f"Specifications: {len(analysis.specifications)}")
        
        # Test the fixed RFI engine
        print("\n=== RFI ENGINE TEST (THE FIX) ===")
        print("Calling: rfi_engine.analyze_project_issues(analysis)")
        print("Before fix this crashed with: 'str' object has no attribute 'floor_plans'")
        
        rfi_result = rfi_engine.analyze_project_issues(analysis)
        
        print("SUCCESS - No crash!")
        print(f"RFI result type: {type(rfi_result)}")
        print(f"RFI result length: {len(rfi_result) if hasattr(rfi_result, '__len__') else 'N/A'}")
        
        # Show floor plan details
        if analysis.floor_plans:
            fp = analysis.floor_plans[0]
            print(f"\n=== FLOOR PLAN DETAILS ===")
            print(f"Sheet: {fp.sheet_number}")
            print(f"Rooms: {len(fp.rooms)}")
            print(f"Has scale: {hasattr(fp, 'scale')}")
            print(f"Floor plan type: {type(fp)}")
        
        print(f"\n=== WORKING FILES CREATED ===")
        working_files = [
            "process_real_construction_pdf_REAL_FIX.py",
            "demo_complete_autofire_system.py",
            "live_demonstration.py",
            "AUTOFIRE_AI_FULLY_OPERATIONAL.md"
        ]
        
        for filename in working_files:
            filepath = Path(filename)
            if filepath.exists():
                print(f"{filename}: {filepath.stat().st_size} bytes")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    show_actual_results()