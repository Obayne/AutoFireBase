#!/usr/bin/env python3
"""
AUTOFIRE VISIBLE CONSOLE APP
Shows AutoFire actually running with real-time output
"""

import sys
import time
import os
from datetime import datetime

def print_banner():
    print("=" * 60)
    print("    🔥 AUTOFIRE AI - LIVE CONSOLE APPLICATION 🔥")
    print("=" * 60)
    print()

def print_step(step_num, description):
    print(f"STEP {step_num}: {description}")
    print("-" * 40)

def show_autofire_running():
    print_banner()
    
    # Step 1: Show environment
    print_step(1, "AUTOFIRE ENVIRONMENT CHECK")
    print(f"Current Directory: {os.getcwd()}")
    print(f"Python Path: {sys.executable}")
    print(f"Current Time: {datetime.now()}")
    print()
    time.sleep(1)
    
    # Step 2: Add AutoFire to path and import
    print_step(2, "LOADING AUTOFIRE AI MODULES")
    sys.path.append('C:/Dev/Autofire')
    
    try:
        print("Importing PDFConstructionAnalyzer...")
        from cad_core.intelligence.pdf_analyzer import PDFConstructionAnalyzer
        print("✅ PDFConstructionAnalyzer imported successfully")
        
        print("Importing RFIIntelligenceEngine...")
        from cad_core.intelligence.rfi_engine import RFIIntelligenceEngine
        print("✅ RFIIntelligenceEngine imported successfully")
        
        print("Importing AI Floor Plan Processor...")
        from cad_core.intelligence.ai_floor_plan_processor import generate_complete_low_voltage_design
        print("✅ AI Floor Plan Processor imported successfully")
        
    except Exception as e:
        print(f"❌ FAILED TO IMPORT: {e}")
        return False
    
    print()
    time.sleep(1)
    
    # Step 3: Create AI objects
    print_step(3, "INITIALIZING AUTOFIRE AI OBJECTS")
    try:
        print("Creating PDF Analyzer...")
        pdf_analyzer = PDFConstructionAnalyzer()
        print(f"✅ PDF Analyzer created: {type(pdf_analyzer)}")
        
        print("Creating RFI Engine...")
        rfi_engine = RFIIntelligenceEngine()
        print(f"✅ RFI Engine created: {type(rfi_engine)}")
        
    except Exception as e:
        print(f"❌ FAILED TO CREATE OBJECTS: {e}")
        return False
    
    print()
    time.sleep(1)
    
    # Step 4: Check for PDF file
    print_step(4, "LOCATING CONSTRUCTION DOCUMENTS")
    pdf_path = "C:/Dev/Autofire/Projects/floorplan-sample.pdf"
    
    if os.path.exists(pdf_path):
        file_size = os.path.getsize(pdf_path)
        print(f"✅ Found PDF: {pdf_path}")
        print(f"✅ File Size: {file_size:,} bytes")
    else:
        print(f"❌ PDF not found: {pdf_path}")
        return False
    
    print()
    time.sleep(1)
    
    # Step 5: ACTUAL PDF PROCESSING (LIVE)
    print_step(5, "🔥 AUTOFIRE AI PROCESSING PDF - LIVE 🔥")
    print("AutoFire AI is now analyzing the construction document...")
    print("You will see real AutoFire AI log messages:")
    print()
    
    try:
        # This is REAL AutoFire processing
        result = pdf_analyzer.analyze_construction_set(pdf_path)
        
        print()
        print("✅ AUTOFIRE AI ANALYSIS COMPLETE!")
        print(f"   Project Name: {result.project_name}")
        print(f"   Total Pages: {result.total_pages}")
        print(f"   Floor Plans: {len(result.floor_plans)}")
        print(f"   Analysis Object: {type(result)}")
        
    except Exception as e:
        print(f"❌ PDF PROCESSING FAILED: {e}")
        return False
    
    print()
    time.sleep(1)
    
    # Step 6: CRITICAL RFI TEST (THE FIX)
    print_step(6, "🔍 TESTING CRITICAL RFI FIX - LIVE 🔍")
    print("Testing the RFI engine with analysis object (not string)...")
    print("Before fix: This would crash with 'str' object has no attribute 'floor_plans'")
    print("After fix: Should work without crashing...")
    print()
    
    try:
        # This is the REAL test of the fix
        rfi_result = rfi_engine.analyze_project_issues(result)
        
        print()
        print("✅ RFI ENGINE TEST PASSED!")
        print("✅ NO CRASH - CRITICAL FIX IS WORKING!")
        print(f"   Issues Found: {len(rfi_result)}")
        print(f"   Result Type: {type(rfi_result)}")
        
    except Exception as e:
        print(f"❌ RFI ENGINE FAILED: {e}")
        return False
    
    print()
    time.sleep(1)
    
    # Step 7: Generate live proof
    print_step(7, "GENERATING LIVE PROOF FILE")
    proof_file = f"autofire_live_proof_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    try:
        with open(proof_file, 'w') as f:
            f.write("AUTOFIRE AI LIVE PROOF\n")
            f.write("=====================\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Project: {result.project_name}\n")
            f.write(f"Pages: {result.total_pages}\n")
            f.write(f"Floor Plans: {len(result.floor_plans)}\n")
            f.write(f"RFI Issues: {len(rfi_result)}\n")
            f.write("Status: AUTOFIRE AI IS RUNNING AND WORKING\n")
        
        print(f"✅ Proof file created: {proof_file}")
        
    except Exception as e:
        print(f"❌ PROOF FILE FAILED: {e}")
        return False
    
    print()
    
    # Final status
    print("=" * 60)
    print("    🎉 AUTOFIRE AI LIVE DEMONSTRATION COMPLETE 🎉")
    print("=" * 60)
    print("✅ AutoFire AI successfully loaded and initialized")
    print("✅ Real PDF document processed without errors")
    print("✅ RFI engine working without crashes (critical fix verified)")
    print("✅ Live proof file generated with real results")
    print()
    print("AUTOFIRE AI IS CONFIRMED WORKING!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    print("Starting AutoFire AI Live Console Application...")
    success = show_autofire_running()
    
    if success:
        print("\nPress Enter to exit...")
        input()
    else:
        print("\nAutoFire AI demonstration failed!")
        input("Press Enter to exit...")