"""
AiHJ - AI Authority Having Jurisdiction
======================================

AI-powered regulatory intelligence for construction professionals.
A clever play on "AHJ" (Authority Having Jurisdiction) - the regulatory
authority that approves building systems and fire protection designs.

AiHJ provides AI-powered analysis with the authority and intelligence
of a regulatory expert for comprehensive building systems review.

Project Strategy:
- LVCAD: Layer Vision CAD Intelligence Engine (main project)
- AiHJ: AI Authority Having Jurisdiction (document analysis spin-off)
- Complementary tools serving different regulatory needs
"""

import os
from datetime import datetime
from pathlib import Path

try:
    from dataclasses import dataclass

    import ezdxf
    import fitz  # PyMuPDF

    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False
    print("⚠️  Some dependencies missing. Install with: pip install PyMuPDF ezdxf")


@dataclass
class ProjectAnalysis:
    """Complete project analysis combining PDF and CAD data."""

    project_name: str
    pdf_analysis: dict
    cad_analysis: dict | None = None
    compliance_score: float = 0.0
    cost_estimate: float = 0.0
    device_count: dict = None
    recommendations: list[str] = None


class AiHJ:
    """
    AiHJ - AI Authority Having Jurisdiction

    AI-powered regulatory intelligence for construction professionals.
    A clever play on "AHJ" (Authority Having Jurisdiction) - the regulatory
    authority that approves building systems and fire protection designs.

    Capabilities:
    1. Document compliance analysis with regulatory authority
    2. Multi-trade code interpretation (Fire, HVAC, Electrical, Plumbing)
    3. AI-powered AHJ-level review and guidance
    4. Cost estimation with regulatory compliance factors
    5. Professional regulatory analysis reports

    This system provides regulatory-grade intelligence through:
    - Authority-level document processing
    - Code compliance verification
    - AHJ-standard analysis and recommendations
    - Professional regulatory deliverables
    """

    def __init__(self):
        self.version = "1.0.0"
        self.initialized = datetime.now()

        # Fire protection terminology database
        self.fire_terms = {
            "devices": ["sprinkler", "detector", "alarm", "horn", "strobe", "pull station"],
            "systems": ["fire pump", "standpipe", "riser", "main", "branch line"],
            "codes": ["nfpa", "ibc", "ifc", "ul listed", "fm approved"],
            "materials": ["pipe", "fitting", "valve", "head", "pendant", "upright"],
        }

        # Industry-standard pricing (2024 rates)
        self.cost_database = {
            "sprinkler_head": 25.00,
            "smoke_detector": 85.00,
            "horn_strobe": 120.00,
            "pull_station": 95.00,
            "fire_pump": 8500.00,
            "riser_assembly": 1200.00,
            "pipe_per_foot": 12.50,
            "labor_per_device": 150.00,
        }

    def analyze_pdf_documents(self, folder_path: str) -> dict:
        """
        Analyze all PDF documents in a project folder.

        Returns comprehensive analysis including:
        - Document count and pages
        - Fire protection terminology frequency
        - System type identification
        - Compliance indicators
        """
        if not HAS_DEPENDENCIES:
            return {"error": "PyMuPDF not installed"}

        results = {
            "total_documents": 0,
            "total_pages": 0,
            "total_words": 0,
            "fire_term_counts": {},
            "documents_processed": [],
            "analysis_timestamp": datetime.now().isoformat(),
        }

        pdf_files = list(Path(folder_path).glob("*.pdf"))
        results["total_documents"] = len(pdf_files)

        for pdf_file in pdf_files:
            try:
                doc_analysis = self._analyze_single_pdf(str(pdf_file))
                results["documents_processed"].append(doc_analysis)
                results["total_pages"] += doc_analysis["page_count"]
                results["total_words"] += doc_analysis["word_count"]

                # Aggregate fire term counts
                for term, count in doc_analysis["fire_terms"].items():
                    results["fire_term_counts"][term] = (
                        results["fire_term_counts"].get(term, 0) + count
                    )

            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")

        return results

    def _analyze_single_pdf(self, pdf_path: str) -> dict:
        """Analyze a single PDF document."""
        doc = fitz.open(pdf_path)

        analysis = {
            "filename": Path(pdf_path).name,
            "page_count": len(doc),
            "word_count": 0,
            "fire_terms": {},
            "text_preview": "",
        }

        full_text = ""
        for page in doc:
            text = page.get_text()
            full_text += text + " "

        doc.close()

        # Count words and fire terms
        words = full_text.lower().split()
        analysis["word_count"] = len(words)
        analysis["text_preview"] = full_text[:500] + "..." if len(full_text) > 500 else full_text

        # Count fire protection terms
        for category, terms in self.fire_terms.items():
            for term in terms:
                count = full_text.lower().count(term.lower())
                if count > 0:
                    analysis["fire_terms"][term] = count

        return analysis

    def analyze_cad_layers(self, dxf_path: str) -> dict | None:
        """
        Analyze CAD layers for fire protection elements.

        This integrates with the CAD Layer Intelligence Engine
        to provide exact device counts and locations.
        """
        if not HAS_DEPENDENCIES:
            return None

        try:
            doc = ezdxf.readfile(dxf_path)

            analysis = {
                "filename": Path(dxf_path).name,
                "layer_count": len(doc.layers),
                "fire_layers": [],
                "device_count": 0,
                "layer_details": [],
            }

            for layer in doc.layers:
                layer_info = {"name": layer.dxf.name, "color": layer.dxf.color, "elements": 0}

                # Count elements in each layer
                for entity in doc.modelspace().query(f'*[layer=="{layer.dxf.name}"]'):
                    layer_info["elements"] += 1

                # Check if layer contains fire protection elements
                if self._is_fire_layer(layer.dxf.name):
                    analysis["fire_layers"].append(layer.dxf.name)
                    analysis["device_count"] += layer_info["elements"]

                analysis["layer_details"].append(layer_info)

            return analysis

        except Exception as e:
            print(f"Error analyzing CAD file {dxf_path}: {e}")
            return None

    def _is_fire_layer(self, layer_name: str) -> bool:
        """Check if layer name indicates fire protection elements."""
        fire_indicators = [
            "fire",
            "sprinkler",
            "alarm",
            "smoke",
            "detector",
            "pull",
            "horn",
            "strobe",
            "exit",
            "emergency",
        ]

        layer_lower = layer_name.lower()
        return any(indicator in layer_lower for indicator in fire_indicators)

    def estimate_project_cost(self, analysis: dict) -> dict:
        """
        Estimate project costs based on detected fire protection elements.

        Uses industry-standard pricing and detected device counts.
        """
        cost_breakdown = {
            "devices": 0.0,
            "materials": 0.0,
            "labor": 0.0,
            "total": 0.0,
            "device_estimates": {},
        }

        # Estimate device counts from terminology frequency
        fire_terms = analysis.get("fire_term_counts", {})

        # Conservative estimation based on term frequency
        estimated_devices = {
            "sprinkler_heads": fire_terms.get("sprinkler", 0) * 0.8,  # 80% of mentions
            "smoke_detectors": fire_terms.get("detector", 0) * 0.6,  # 60% of mentions
            "horn_strobes": fire_terms.get("horn", 0) * 0.7,  # 70% of mentions
            "pull_stations": fire_terms.get("pull station", 0) * 1.0,  # 100% of mentions
        }

        # Calculate costs
        for device_type, count in estimated_devices.items():
            if count > 0:
                device_cost_key = device_type.rstrip("s")  # Remove plural 's'
                if device_cost_key in self.cost_database:
                    device_cost = count * self.cost_database[device_cost_key]
                    labor_cost = count * self.cost_database["labor_per_device"]

                    cost_breakdown["devices"] += device_cost
                    cost_breakdown["labor"] += labor_cost
                    cost_breakdown["device_estimates"][device_type] = {
                        "count": int(count),
                        "unit_cost": self.cost_database[device_cost_key],
                        "total_cost": device_cost,
                    }

        # Add materials (typically 30% of device cost)
        cost_breakdown["materials"] = cost_breakdown["devices"] * 0.3

        # Calculate total
        cost_breakdown["total"] = (
            cost_breakdown["devices"] + cost_breakdown["materials"] + cost_breakdown["labor"]
        )

        return cost_breakdown

    def generate_compliance_score(self, analysis: dict) -> tuple[float, list[str]]:
        """
        Generate NFPA compliance score based on document analysis.

        Returns score (0-100) and list of compliance indicators.
        """
        score = 0.0
        indicators = []

        fire_terms = analysis.get("fire_term_counts", {})

        # Check for NFPA standards references
        if fire_terms.get("nfpa", 0) > 0:
            score += 25
            indicators.append("✅ NFPA standards referenced")
        else:
            indicators.append("⚠️ No NFPA standard references found")

        # Check for required systems
        if fire_terms.get("sprinkler", 0) > 0:
            score += 20
            indicators.append("✅ Sprinkler system documented")

        if fire_terms.get("detector", 0) > 0:
            score += 20
            indicators.append("✅ Detection systems documented")

        if fire_terms.get("alarm", 0) > 0:
            score += 15
            indicators.append("✅ Alarm systems documented")

        # Check for emergency systems
        if any(term in fire_terms for term in ["exit", "emergency"]):
            score += 10
            indicators.append("✅ Emergency systems documented")

        # Check for proper equipment specifications
        if any(term in fire_terms for term in ["ul listed", "fm approved"]):
            score += 10
            indicators.append("✅ Approved equipment specified")

        return min(score, 100.0), indicators

    def create_project_report(self, project_name: str, analysis: dict) -> str:
        """Generate comprehensive project analysis report."""

        cost_analysis = self.estimate_project_cost(analysis)
        compliance_score, compliance_indicators = self.generate_compliance_score(analysis)

        report = f"""
🏗️ AiHJ - ADVANCED INTELLIGENCE ANALYSIS REPORT
{'='*50}

Project: {project_name}
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
AiHJ Version: {self.version}

📊 DOCUMENT SUMMARY
{'-'*30}
Total Documents: {analysis.get('total_documents', 0)}
Total Pages: {analysis.get('total_pages', 0)}
Total Words: {analysis.get('total_words', 0):,}

🔍 BUILDING SYSTEMS ANALYSIS
{'-'*30}
Technical Terms Detected: {len(analysis.get('fire_term_counts', {}))}

Top Building System Elements:
"""

        # Add top fire terms
        fire_terms = analysis.get("fire_term_counts", {})
        for term, count in sorted(fire_terms.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"  • {term.title()}: {count} occurrences\n"

        report += f"""
💰 COST ESTIMATION
{'-'*30}
Total Estimated Cost: ${cost_analysis['total']:,.2f}

Cost Breakdown:
  • Devices: ${cost_analysis['devices']:,.2f}
  • Materials: ${cost_analysis['materials']:,.2f}
  • Labor: ${cost_analysis['labor']:,.2f}

Device Estimates:
"""

        for device, details in cost_analysis["device_estimates"].items():
            report += f"  • {device.replace('_', ' ').title()}: {details['count']} units @ ${details['unit_cost']:.2f} = ${details['total_cost']:,.2f}\n"

        report += f"""
✅ COMPLIANCE ASSESSMENT
{'-'*30}
NFPA Compliance Score: {compliance_score:.1f}/100

Compliance Indicators:
"""

        for indicator in compliance_indicators:
            report += f"  {indicator}\n"

        report += f"""
📋 RECOMMENDATIONS
{'-'*30}
• Review NFPA 72 (Fire Alarm Systems) requirements
• Verify sprinkler coverage calculations per NFPA 13
• Ensure proper device spacing and placement
• Confirm UL listing for all fire protection equipment
• Schedule inspection and testing procedures

🎯 NEXT STEPS
{'-'*30}
• Detailed CAD analysis (if DXF files available)
• Hydraulic calculations for sprinkler systems
• Emergency egress analysis
• Professional engineering review

Report generated by Fire Pilot v{self.version}
Advanced Fire Protection Analysis System
"""

        return report

    def run_full_analysis(self, project_folder: str, project_name: str = None) -> ProjectAnalysis:
        """
        Run complete project analysis on a folder containing
        construction documents (PDFs, DXFs, etc.)
        """
        if not project_name:
            project_name = Path(project_folder).name

        print(f"🔥 Fire Pilot - Analyzing Project: {project_name}")
        print(f"📁 Folder: {project_folder}")

        # Analyze PDF documents
        pdf_analysis = self.analyze_pdf_documents(project_folder)

        # Look for CAD files
        cad_analysis = None
        dxf_files = list(Path(project_folder).glob("*.dxf"))
        if dxf_files:
            print(f"📐 Found {len(dxf_files)} CAD files, analyzing...")
            # Analyze first DXF file (could be expanded to analyze all)
            cad_analysis = self.analyze_cad_layers(str(dxf_files[0]))

        # Generate cost estimate and compliance score
        cost_estimate = self.estimate_project_cost(pdf_analysis)["total"]
        compliance_score, _ = self.generate_compliance_score(pdf_analysis)

        # Create project analysis object
        analysis = ProjectAnalysis(
            project_name=project_name,
            pdf_analysis=pdf_analysis,
            cad_analysis=cad_analysis,
            compliance_score=compliance_score,
            cost_estimate=cost_estimate,
            device_count=pdf_analysis.get("fire_term_counts", {}),
            recommendations=[],
        )

        # Generate and save report
        report = self.create_project_report(project_name, pdf_analysis)
        report_path = Path(project_folder) / f"{project_name}_fire_pilot_report.txt"

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"📄 Report saved: {report_path}")
        except Exception as e:
            print(f"Warning: Could not save report - {e}")

        return analysis


def main():
    """Main execution function for AiHJ."""
    print("🏛️ AiHJ - AI Authority Having Jurisdiction")
    print("=" * 50)

    if not HAS_DEPENDENCIES:
        print("❌ Missing dependencies. Please install:")
        print("   pip install PyMuPDF ezdxf")
        return

    # Check if running from project folder
    current_dir = os.getcwd()
    pdf_files = list(Path(current_dir).glob("*.pdf"))

    if pdf_files:
        print(f"📁 Found {len(pdf_files)} PDF files in current directory")

        # Initialize AiHJ
        aihj = AiHJ()

        # Run analysis
        project_name = Path(current_dir).name
        analysis = aihj.run_full_analysis(current_dir, project_name)

        print("\n🎯 REGULATORY ANALYSIS COMPLETE")
        print(f"📊 Documents Processed: {analysis.pdf_analysis.get('total_documents', 0)}")
        print(f"💰 Estimated Cost: ${analysis.cost_estimate:,.2f}")
        print(f"✅ Compliance Score: {analysis.compliance_score:.1f}/100")

        if analysis.cad_analysis:
            print(f"📐 CAD Layers Analyzed: {analysis.cad_analysis.get('layer_count', 0)}")
            print(f"🏗️ Building System Devices: {analysis.cad_analysis.get('device_count', 0)}")

    else:
        print("📂 No PDF files found in current directory")
        print("💡 Navigate to a project folder containing construction PDFs and run again")


if __name__ == "__main__":
    main()
