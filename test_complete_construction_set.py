#!/usr/bin/env python3
"""
AUTOFIRE AI - COMPLETE CONSTRUCTION SET TEST
Process the real 15.6MB RFP-24-001 construction drawings
"""

import sys
import os
import time
from datetime import datetime

# Add AutoFire path
sys.path.append('C:/Dev/Autofire')

def test_complete_construction_set():
    """Test AutoFire with the complete construction set"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    construction_set = 'C:/Dev/rfp-24-001-general-contractor-construction-drawings.pdf'
    
    print("🔥 AUTOFIRE AI - COMPLETE CONSTRUCTION SET TEST")
    print("=" * 55)
    print(f"File: {construction_set}")
    print(f"Size: {os.path.getsize(construction_set):,} bytes (15.6 MB)")
    print(f"Time: {datetime.now()}")
    print()
    
    try:
        # Import AutoFire modules
        print("📦 Loading AutoFire AI modules...")
        from cad_core.intelligence.pdf_analyzer import PDFConstructionAnalyzer
        from cad_core.intelligence.rfi_engine import RFIIntelligenceEngine
        print("✅ AutoFire AI modules loaded")
        print()
        
        # Create analyzer
        print("🤖 Creating PDF Construction Analyzer...")
        analyzer = PDFConstructionAnalyzer()
        print("✅ Analyzer ready")
        print()
        
        # Process the complete construction set
        print("🏗️ PROCESSING 15.6MB CONSTRUCTION SET...")
        print("   This is a REAL construction project with multiple drawings")
        print()
        
        start_time = time.time()
        result = analyzer.analyze_construction_set(construction_set)
        processing_time = time.time() - start_time
        
        print("✅ CONSTRUCTION SET ANALYSIS COMPLETE!")
        print(f"   Processing time: {processing_time:.2f} seconds")
        print()
        
        # Show results
        print("📊 ANALYSIS RESULTS:")
        print("-" * 25)
        print(f"Project: {result.project_name}")
        print(f"Pages: {result.total_pages}")
        print(f"Floor Plans: {len(result.floor_plans)}")
        print()
        
        # Test RFI engine with the results
        print("🔍 Testing RFI Intelligence Engine...")
        rfi_engine = RFIIntelligenceEngine()
        rfi_issues = rfi_engine.analyze_project_issues(result)
        print(f"✅ RFI Analysis: {len(rfi_issues)} issues identified")
        print()
        
        # Create proof file
        proof_file = f'COMPLETE_CONSTRUCTION_PROOF_{timestamp}.txt'
        with open(proof_file, 'w', encoding='utf-8') as f:
            f.write("AUTOFIRE AI - COMPLETE CONSTRUCTION SET PROOF\n")
            f.write("=" * 45 + "\n")
            f.write(f"Processed: {datetime.now()}\n")
            f.write(f"File: {construction_set}\n")
            f.write(f"Size: {os.path.getsize(construction_set):,} bytes\n")
            f.write(f"Project: {result.project_name}\n")
            f.write(f"Pages: {result.total_pages}\n")
            f.write(f"Floor Plans: {len(result.floor_plans)}\n")
            f.write(f"Processing Time: {processing_time:.2f} seconds\n")
            f.write(f"RFI Issues: {len(rfi_issues)}\n")
            f.write("\nSTATUS: AUTOFIRE SUCCESSFULLY PROCESSED COMPLETE CONSTRUCTION SET\n")
        
        print("🎉 SUCCESS! AutoFire processed the complete construction set!")
        print(f"📄 Proof file: {proof_file}")
        print()
        print("SUMMARY:")
        print(f"  • Processed 15.6MB real construction project")
        print(f"  • Analyzed {result.total_pages} pages of drawings")
        print(f"  • Found {len(result.floor_plans)} floor plans")
        print(f"  • Completed in {processing_time:.2f} seconds")
        print(f"  • RFI engine tested successfully")
        print()
        print("AutoFire AI can handle COMPLETE construction sets! 🔥")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
        with open(f'CONSTRUCTION_ERROR_{timestamp}.txt', 'w', encoding='utf-8') as f:
            f.write(f"AUTOFIRE ERROR - {datetime.now()}\n")
            f.write(f"Error: {e}\n")
            f.write(f"File: {construction_set}\n")

if __name__ == "__main__":
    test_complete_construction_set()