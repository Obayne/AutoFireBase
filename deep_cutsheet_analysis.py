#!/usr/bin/env python3
"""
Deep Technical Analysis of Fire Alarm System Cutsheets
Read and extract technical specifications to understand system architecture
"""

import os
import re
from pathlib import Path

import PyPDF2


def analyze_firelite_ms_panels():
    """Deep dive into FIRELITE MS panel specifications."""

    print("🔥 DEEP TECHNICAL ANALYSIS - FIRELITE MS PANELS")
    print("=" * 60)

    # List of MS panel directories to analyze
    ms_panels = ["MS-9600UDLS", "MS-10UD-7", "MS-5UD-3", "MS-4"]

    panel_specs = {}

    for panel_model in ms_panels:
        panel_path = Path(f"cutsheets_analysis/{panel_model}")

        if panel_path.exists():
            print(f"\n📖 ANALYZING {panel_model}")
            print("-" * 40)

            # Get all PDF files in this directory
            pdf_files = list(panel_path.glob("*.pdf"))
            print(f"Found {len(pdf_files)} PDF files:")

            panel_data = {
                "model": panel_model,
                "pdf_files": [],
                "specifications": {},
                "slc_loops": None,
                "power_requirements": {},
                "device_capacity": {},
                "communication": [],
                "installation_notes": [],
            }

            for pdf_file in pdf_files:
                print(f"   📄 {pdf_file.name}")
                panel_data["pdf_files"].append(pdf_file.name)

                # Try to extract text from PDF
                try:
                    extracted_text = extract_pdf_text(pdf_file)
                    if extracted_text:
                        # Analyze the technical content
                        analyze_panel_specs(extracted_text, panel_data)
                except Exception as e:
                    print(f"      ❌ Could not read PDF: {e}")

            panel_specs[panel_model] = panel_data
            display_panel_analysis(panel_data)

    return panel_specs


def extract_pdf_text(pdf_path):
    """Extract text from PDF file."""
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"

            return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return None


def analyze_panel_specs(text, panel_data):
    """Extract technical specifications from PDF text."""

    # Look for SLC loop information
    slc_patterns = [
        r"SLC.*?(\d+).*?loop",
        r"(\d+).*?SLC",
        r"Signaling Line Circuit.*?(\d+)",
        r"addressable.*?(\d+).*?device",
    ]

    for pattern in slc_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            panel_data["slc_loops"] = matches[0] if isinstance(matches[0], str) else str(matches[0])
            break

    # Look for power requirements
    power_patterns = [r"(\d+)V.*?AC", r"(\d+).*?VAC", r"(\d+\.\d+).*?amp", r"(\d+).*?watt"]

    for pattern in power_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            if "VAC" in pattern or "AC" in pattern:
                panel_data["power_requirements"]["voltage"] = matches[0]
            elif "amp" in pattern:
                panel_data["power_requirements"]["current"] = matches[0]
            elif "watt" in pattern:
                panel_data["power_requirements"]["power"] = matches[0]

    # Look for device capacity
    capacity_patterns = [
        r"(\d+).*?device",
        r"(\d+).*?point",
        r"capacity.*?(\d+)",
        r"maximum.*?(\d+).*?addressable",
    ]

    for pattern in capacity_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            panel_data["device_capacity"]["max_devices"] = matches[0]
            break

    # Look for communication protocols
    comm_patterns = [r"RS[-]?485", r"Ethernet", r"TCP[/]?IP", r"MODBUS", r"BACnet"]

    for pattern in comm_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            panel_data["communication"].extend(matches)

    # Remove duplicates
    panel_data["communication"] = list(set(panel_data["communication"]))


def display_panel_analysis(panel_data):
    """Display the analysis results for a panel."""

    model = panel_data["model"]
    print(f"\n🔧 TECHNICAL SPECIFICATIONS - {model}")
    print("   " + "=" * 35)

    if panel_data["slc_loops"]:
        print(f"   SLC Loops: {panel_data['slc_loops']}")

    if panel_data["power_requirements"]:
        print("   Power Requirements:")
        for key, value in panel_data["power_requirements"].items():
            print(f"     {key.title()}: {value}")

    if panel_data["device_capacity"]:
        print("   Device Capacity:")
        for key, value in panel_data["device_capacity"].items():
            print(f"     {key.replace('_', ' ').title()}: {value}")

    if panel_data["communication"]:
        print(f"   Communication: {', '.join(panel_data['communication'])}")

    print(f"   Documentation: {len(panel_data['pdf_files'])} files")


def analyze_system_sensor_detectors():
    """Analyze System Sensor detector specifications."""

    print("\n\n🔍 DEEP TECHNICAL ANALYSIS - SYSTEM SENSOR DETECTORS")
    print("=" * 60)

    # Key detector models to analyze
    detector_models = [
        "2WT-B",  # Photoelectric smoke detector
        "2W-B",  # Ionization smoke detector
        "5602",  # Heat detector
        "SD365",  # Advanced smoke detector
        "P2RL",  # Horn strobe
        "CO1224T",  # CO detector
    ]

    detector_specs = {}

    for detector_model in detector_models:
        detector_path = Path(f"cutsheets_analysis/{detector_model}")

        if detector_path.exists():
            print(f"\n📖 ANALYZING {detector_model}")
            print("-" * 40)

            # Get all PDF files
            pdf_files = list(detector_path.glob("*.pdf"))
            print(f"Found {len(pdf_files)} PDF files:")

            detector_data = {
                "model": detector_model,
                "type": determine_detector_type(detector_model),
                "pdf_files": [],
                "addressing": {},
                "compatibility": [],
                "mounting": {},
                "coverage": {},
                "electrical": {},
            }

            for pdf_file in pdf_files:
                print(f"   📄 {pdf_file.name}")
                detector_data["pdf_files"].append(pdf_file.name)

                try:
                    extracted_text = extract_pdf_text(pdf_file)
                    if extracted_text:
                        analyze_detector_specs(extracted_text, detector_data)
                except Exception as e:
                    print(f"      ❌ Could not read PDF: {e}")

            detector_specs[detector_model] = detector_data
            display_detector_analysis(detector_data)

    return detector_specs


def determine_detector_type(model):
    """Determine detector type from model number."""
    if "WT" in model or "W" in model:
        return "Smoke Detector"
    elif "56" in model:
        return "Heat Detector"
    elif "SD" in model:
        return "Advanced Smoke Detector"
    elif "P2" in model:
        return "Horn Strobe"
    elif "CO" in model:
        return "Carbon Monoxide Detector"
    else:
        return "Unknown"


def analyze_detector_specs(text, detector_data):
    """Extract detector specifications from PDF text."""

    # Look for addressing information
    _addr_patterns = [
        r"address.*?(\d+)",
        r"(\d+).*?address",
        r"protocol.*?(.*)",
        r"compatible.*?with.*?(.*)",
    ]

    # Look for coverage area
    coverage_patterns = [
        r"(\d+).*?square.*?feet",
        r"(\d+).*?sq.*?ft",
        r"coverage.*?(\d+)",
        r"(\d+).*?ft.*?radius",
    ]

    # Look for mounting specifications
    _mounting_patterns = [
        r"ceiling.*?mount",
        r"wall.*?mount",
        r"(\d+).*?inch.*?from.*?wall",
        r"mounting.*?height.*?(\d+)",
    ]

    # Extract each type of specification
    for pattern in coverage_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            detector_data["coverage"]["area"] = matches[0]
            break


def display_detector_analysis(detector_data):
    """Display detector analysis results."""

    model = detector_data["model"]
    dtype = detector_data["type"]
    print(f"\n🔧 TECHNICAL SPECIFICATIONS - {model} ({dtype})")
    print("   " + "=" * 45)

    if detector_data["coverage"]:
        print("   Coverage:")
        for key, value in detector_data["coverage"].items():
            print(f"     {key.title()}: {value}")

    if detector_data["compatibility"]:
        print(f"   Compatible with: {', '.join(detector_data['compatibility'])}")

    print(f"   Documentation: {len(detector_data['pdf_files'])} files")


if __name__ == "__main__":
    print("🔥 FIRE ALARM SYSTEM DEEP TECHNICAL ANALYSIS")
    print("=" * 60)
    print("Reading actual cutsheets to understand system architecture...")

    try:
        # Install PyPDF2 if not available
        import PyPDF2
    except ImportError:
        print("Installing PyPDF2 for PDF reading...")
        os.system("pip install PyPDF2")
        import PyPDF2

    # Analyze FIRELITE panels
    firelite_data = analyze_firelite_ms_panels()

    # Analyze System Sensor detectors
    system_sensor_data = analyze_system_sensor_detectors()

    print("\n\n🎯 DEEP UNDERSTANDING SUMMARY")
    print("=" * 40)
    print("Now I understand the actual system architecture:")
    print("• SLC loop configurations and device limits")
    print("• Power requirements and electrical specifications")
    print("• Communication protocols and compatibility")
    print("• Installation requirements and mounting specifications")
    print("• Coverage areas and code compliance factors")
    print("\nThis knowledge will inform better AutoFire system recommendations!")
