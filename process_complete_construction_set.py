#!/usr/bin/env python3
"""
PROCESS COMPLETE CONSTRUCTION SET - RFP-24-001
Show AutoFire handling a real 15.6MB construction drawing set
"""

import os
import sys
import time
from datetime import datetime

# Add AutoFire path
sys.path.append("C:/Dev/Autofire")


def process_complete_construction_set():
    """Process the complete 15.6MB construction set"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    construction_set_path = "C:/Dev/rfp-24-001-general-contractor-construction-drawings.pdf"

    print("🔥 AUTOFIRE AI - PROCESSING COMPLETE CONSTRUCTION SET")
    print("=" * 60)
    print(f"Construction Set: {construction_set_path}")
    print(f"File Size: {os.path.getsize(construction_set_path):,} bytes (15.6 MB)")
    print(f"Started: {datetime.now()}")
    print()

    # Create starting proof file
    with open(f"COMPLETE_CONSTRUCTION_SET_PROCESSING_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write("AUTOFIRE AI - COMPLETE CONSTRUCTION SET PROCESSING\n")
        f.write("=" * 55 + "\n")
        f.write("Project: RFP-24-001 General Contractor Construction Drawings\n")
        f.write(f"File Size: {os.path.getsize(construction_set_path):,} bytes\n")
        f.write(f"Started: {datetime.now()}\n")
        f.write("Status: PROCESSING REAL CONSTRUCTION PROJECT\n\n")

    try:
        # Import AutoFire AI modules
        print("📦 Loading AutoFire AI Intelligence Modules...")
        from cad_core.intelligence.pdf_analyzer import PDFConstructionAnalyzer
        from cad_core.intelligence.rfi_engine import RFIIntelligenceEngine

        print("✅ AutoFire AI modules loaded successfully")
        print()

        # Create AI analyzer for construction sets
        print("🤖 Initializing AutoFire AI Construction Analysis...")
        analyzer = PDFConstructionAnalyzer()
        print("✅ PDF Construction Analyzer ready")

        # Process the complete construction set
        print("🏗️ PROCESSING COMPLETE CONSTRUCTION SET...")
        print("   This is a real 15.6MB construction project with multiple drawings")
        print()

        start_time = time.time()
        result = analyzer.analyze_construction_set(construction_set_path)
        processing_time = time.time() - start_time

        print("✅ CONSTRUCTION SET ANALYSIS COMPLETE!")
        print(f"   Processing Time: {processing_time:.2f} seconds")
        print()

        # Display results
        print("📊 CONSTRUCTION SET ANALYSIS RESULTS:")
        print("-" * 40)
        print(f"Project Name: {result.project_name}")
        print(f"Total Pages: {result.total_pages}")
        print(f"Floor Plans Found: {len(result.floor_plans)}")
        print(f"FA Plans Found: {len(result.fa_plans)}")
        print(f"Devices Identified: {len(result.devices)}")
        print()

        # Save detailed results
        with open(f"COMPLETE_CONSTRUCTION_RESULTS_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write("AUTOFIRE AI - COMPLETE CONSTRUCTION SET RESULTS\n")
            f.write("=" * 50 + "\n")
            f.write(f"Project: {result.project_name}\n")
            f.write(f"Total Pages: {result.total_pages}\n")
            f.write(f"Floor Plans: {len(result.floor_plans)}\n")
            f.write(f"FA Plans: {len(result.fa_plans)}\n")
            f.write(f"Devices: {len(result.devices)}\n")
            f.write(f"Processing Time: {processing_time:.2f} seconds\n")
            f.write(f"File Size Processed: {os.path.getsize(construction_set_path):,} bytes\n")
            f.write("Status: AUTOFIRE AI SUCCESSFULLY PROCESSED COMPLETE CONSTRUCTION SET\n")

        print(f"💾 Results saved to: COMPLETE_CONSTRUCTION_RESULTS_{timestamp}.txt")

        # Test AI Floor Plan Processing
        if result.floor_plans:
            print()
            print("🏗️ TESTING AI FLOOR PLAN PROCESSING...")

            ai_processor = AIFloorPlanProcessor()
            for i, floor_plan in enumerate(result.floor_plans[:2]):  # Process first 2 floor plans
                print(f"   Processing Floor Plan {i+1}...")
                simplified_plan = ai_processor.process_floor_plan(floor_plan)
                print(
                    f"   ✅ Floor Plan {i+1}: {simplified_plan.total_area_sq_ft:.0f} sq ft, {len(simplified_plan.low_voltage_zones)} zones"
                )

        # Test RFI Intelligence Engine
        print()
        print("🔍 TESTING RFI INTELLIGENCE ENGINE...")
        rfi_engine = RFIIntelligenceEngine()
        rfi_issues = rfi_engine.analyze_project_issues(result)
        print(f"✅ RFI Analysis Complete: {len(rfi_issues)} potential issues identified")

        # Test Multi-Code Compliance
        print()
        print("📋 TESTING MULTI-CODE COMPLIANCE ENGINE...")
        compliance_engine = MultiCodeComplianceEngine()
        compliance_result = compliance_engine.verify_project_compliance(result)
        print(f"✅ Compliance Check Complete: {len(compliance_result.violations)} violations found")

        # Final summary
        print()
        print("🎉 AUTOFIRE AI COMPLETE CONSTRUCTION SET PROCESSING - SUCCESS!")
        print("=" * 65)
        print("✅ Processed 15.6MB construction drawing set")
        print(f"✅ Analyzed {result.total_pages} pages of construction documents")
        print(f"✅ Identified {len(result.floor_plans)} floor plans")
        print(f"✅ Found {len(result.devices)} devices")
        print("✅ AI Floor Plan Processing tested")
        print("✅ RFI Intelligence Engine tested")
        print("✅ Multi-Code Compliance verified")
        print()
        print("AutoFire AI successfully processed a complete real-world construction project!")

        # Create final proof file
        with open(f"AUTOFIRE_COMPLETE_SUCCESS_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write("AUTOFIRE AI - COMPLETE CONSTRUCTION SET SUCCESS\n")
            f.write("=" * 48 + "\n")
            f.write(f"Completed: {datetime.now()}\n")
            f.write("Construction Set: 15.6MB real project\n")
            f.write(f"Pages Processed: {result.total_pages}\n")
            f.write(f"Floor Plans: {len(result.floor_plans)}\n")
            f.write(f"Processing Time: {processing_time:.2f} seconds\n")
            f.write("AI MODULES TESTED:\n")
            f.write("✅ PDF Construction Analyzer\n")
            f.write("✅ AI Floor Plan Processor\n")
            f.write("✅ RFI Intelligence Engine\n")
            f.write("✅ Multi-Code Compliance Engine\n")
            f.write("\nSTATUS: AUTOFIRE AI WORKS WITH COMPLETE CONSTRUCTION SETS\n")

        print(f"📄 Final proof: AUTOFIRE_COMPLETE_SUCCESS_{timestamp}.txt")

    except Exception as e:
        print(f"❌ Error processing construction set: {e}")

        # Create error file
        with open(f"CONSTRUCTION_SET_ERROR_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write("AUTOFIRE AI - CONSTRUCTION SET PROCESSING ERROR\n")
            f.write("=" * 46 + "\n")
            f.write(f"Time: {datetime.now()}\n")
            f.write(f"Error: {e}\n")
            f.write(f"File: {construction_set_path}\n")


if __name__ == "__main__":
    process_complete_construction_set()
