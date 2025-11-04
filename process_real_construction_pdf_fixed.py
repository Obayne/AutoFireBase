"""
Real Construction Document Processing with AI Intelligence
Processing: C:/Dev/rfp-24-001-general-contractor-construction-drawings.pdf
"""

import sys
import traceback

# Add project to path
sys.path.append("C:/Dev/Autofire")

from cad_core.intelligence.ai_floor_plan_processor import generate_complete_low_voltage_design
from cad_core.intelligence.multi_code_engine import MultiCodeComplianceEngine
from cad_core.intelligence.pdf_analyzer import PDFConstructionAnalyzer
from cad_core.intelligence.rfi_engine import RFIIntelligenceEngine


def process_real_construction_documents():
    """Process the real construction documents with AI intelligence"""

    print("🔥 PROCESSING YOUR REAL CONSTRUCTION DOCUMENTS")
    print("=" * 50)

    # Initialize AI components
    print("Initializing AI intelligence modules...")
    pdf_analyzer = PDFConstructionAnalyzer()
    rfi_engine = RFIIntelligenceEngine()
    compliance_engine = MultiCodeComplianceEngine()

    # Process the PDF
    pdf_path = "C:/Dev/rfp-24-001-general-contractor-construction-drawings.pdf"
    print(f"Processing: {pdf_path}")

    try:
        # Step 1: PDF Analysis
        print("\n📄 STEP 1: PDF Construction Analysis")
        analysis = pdf_analyzer.analyze_construction_set(pdf_path)

        print("✅ PDF processed successfully")
        print(f"   • Project: {analysis.project_name}")
        print(f"   • Total pages: {analysis.total_pages}")
        print(f"   • Floor plans: {len(analysis.floor_plans)}")
        print(f"   • Fire alarm plans: {len(analysis.fire_alarm_plans)}")
        print(f"   • Schedules: {len(analysis.schedules)}")

        # Show floor plan details
        if analysis.floor_plans:
            print("   • Floor plan details:")
            for plan in analysis.floor_plans:
                room_count = len(plan.rooms) if plan.rooms else 0
                print(f"     - {plan.sheet_number}: {room_count} rooms")

        # Step 2: RFI Analysis
        print("\n🔍 STEP 2: RFI Intelligence Analysis")
        rfis = rfi_engine.analyze_project_issues(analysis)
        print(f"✅ RFI analysis complete: {len(rfis)} issues identified")

        # Show top RFIs
        if rfis:
            print("   • Top issues identified:")
            for i, rfi in enumerate(rfis[:5], 1):
                print(f"     {i}. {rfi.title} ({rfi.priority.value})")

        # Step 3: Multi-Code Compliance
        print("\n📋 STEP 3: Multi-Code Compliance Analysis")
        compliance = compliance_engine.analyze_multi_code_compliance(analysis)
        print("✅ Compliance analysis complete")

        # Show compliance summary
        print("   • Compliance scores:")
        for code, results in compliance.items():
            if isinstance(results, dict) and "compliance_score" in results:
                score = results["compliance_score"]
                status = "✅" if score > 0.8 else "⚠️" if score > 0.6 else "❌"
                print(f"     {status} {code.upper()}: {score:.1%} compliant")

        # Step 4: AI Floor Plan Processing
        if analysis.floor_plans:
            print("\n🤖 STEP 4: AI Floor Plan Processing")
            design = generate_complete_low_voltage_design(analysis)
            print("✅ Complete system design generated")

            design_plan = design["complete_design_plan"]
            overview = design_plan["project_overview"]
            system_req = design_plan["system_requirements"]

            print(f'   • Total area: {overview["total_area_sq_ft"]:.0f} sq ft')
            print(f'   • Estimated panels: {system_req["estimated_panels"]}')
            print(f'   • Device types: {len(system_req["device_counts"])}')
            print(f'   • Implementation: {len(design_plan["implementation_phases"])} phases')

        print("\n🎉 AI PROCESSING COMPLETE!")
        print("Your real construction documents have been fully analyzed.")
        print("All AI intelligence modules successfully processed the PDF.")

        return analysis, rfis, compliance, design if analysis.floor_plans else None

    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        print("\nFull error traceback:")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = process_real_construction_documents()

    if result:
        print("\n🚀 SUCCESS: Real construction document processing complete!")
        print("No crashes, no excuses - your AI intelligence is working!")
    else:
        print("\n❌ Processing failed - investigating the actual issue.")
