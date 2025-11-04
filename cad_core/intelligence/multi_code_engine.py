"""
Multi-Code Compliance & Specification Intelligence Engine
Handles IBC, ADA, IMC, and other building codes with specification summarization and gotcha identification
"""

import re
from datetime import datetime
from typing import Any, Dict, List

from . import (
    ConstructionAnalysis,
    ConstructionIntelligenceBase,
    DeviceType,
    Priority,
    RFIItem,
    create_rfi_item,
)


class BuildingCode:
    """Building code reference definitions"""

    # Fire & Life Safety Codes
    NFPA_72 = "NFPA 72"  # Fire Alarm and Signaling Code
    NFPA_101 = "NFPA 101"  # Life Safety Code
    NFPA_1221 = "NFPA 1221"  # Emergency Communications Systems

    # Building Codes
    IBC = "IBC"  # International Building Code
    IFC = "IFC"  # International Fire Code
    IEBC = "IEBC"  # International Existing Building Code
    IMC = "IMC"  # International Mechanical Code

    # Electrical & Low Voltage Codes
    NEC = "NEC"  # National Electrical Code (NFPA 70)
    NFPA_780 = "NFPA 780"  # Lightning Protection Systems
    IEEE_802_11 = "IEEE 802.11"  # Wireless LAN Standards
    TIA_568 = "TIA-568"  # Commercial Building Telecommunications Cabling
    TIA_569 = "TIA-569"  # Commercial Building Pathways and Spaces
    TIA_606 = "TIA-606"  # Administration Standard for Telecommunications Infrastructure

    # BICSI (Building Industry Consulting Service International) Standards
    BICSI_TDMM = "BICSI TDMM"  # Telecommunications Distribution Methods Manual
    BICSI_OSP = "BICSI OSP"  # Outside Plant Design Reference Manual
    BICSI_ITS = "BICSI ITS"  # Information Transport Systems Installation Methods Manual
    BICSI_DDM = "BICSI DDM"  # Data Center Design and Implementation Best Practices
    BICSI_WDS = "BICSI WDS"  # Wireless Design Standards and Practices
    BICSI_ITSIMM = "BICSI ITSIMM"  # Information Transport Systems Installation Methods Manual
    BICSI_001 = "BICSI-001"  # Data Center Design Certification
    BICSI_002 = "BICSI-002"  # Data Center Operations Certification
    BICSI_003 = "BICSI-003"  # Network Transport Systems Installation
    BICSI_004 = "BICSI-004"  # Emergency Responder Communication Enhancement Systems

    # NICET (National Institute for Certification in Engineering Technologies)
    NICET_FIRE_1 = "NICET Fire Level I"  # Fire Alarm Systems Level I
    NICET_FIRE_2 = "NICET Fire Level II"  # Fire Alarm Systems Level II
    NICET_FIRE_3 = "NICET Fire Level III"  # Fire Alarm Systems Level III
    NICET_FIRE_4 = "NICET Fire Level IV"  # Fire Alarm Systems Level IV
    NICET_SPECIAL_HAZARDS = "NICET Special Hazards"  # Special Hazards Suppression Systems

    # Related Low Voltage Industry Standards (Mike Holtz & Industry References)
    ANSI_TIA_942 = "ANSI/TIA-942"  # Data Center Standards
    ISO_11801 = "ISO/IEC 11801"  # Generic Cabling for Customer Premises
    J_STD_607_A = "J-STD-607-A"  # Commercial Building Grounding and Bonding
    TIA_TSB_162 = "TIA-TSB-162"  # Telecommunications Cabling Guidelines for Wireless Access Points
    ANSI_TIA_526 = "ANSI/TIA-526"  # Optical Fiber Measurement Methods
    IPC_WHMA_620 = (
        "IPC/WHMA-A-620"  # Requirements and Acceptance for Cable and Wire Harness Assemblies
    )

    # Fiber Optic Standards
    TIA_598 = "TIA-598"  # Optical Fiber Cable Color Coding
    TIA_455 = "TIA-455"  # Fiber Optic Test Procedures
    IEC_61300 = "IEC 61300"  # Fiber Optic Interconnecting Devices and Passive Components

    # Audio/Visual Standards (AV Industry)
    AVIXA_F101 = "AVIXA F101"  # Audio Systems Design and Integration
    AVIXA_F201 = "AVIXA F201"  # Digital Signage Certified Technology Specialist
    CEA_2006 = "CEA-2006"  # Digital Audio
    SMPTE_ST_2110 = "SMPTE ST 2110"  # Professional Media Over Managed IP Networks
    IEEE_802_3 = "IEEE 802.3"  # Ethernet Standards
    FCC_PART_15 = "FCC Part 15"  # Radio Frequency Devices
    CENELEC_EN_50173 = "CENELEC EN 50173"  # European Cabling Standards

    # Security & Access Control Codes
    SIA_DC_09 = "SIA DC-09"  # Application of IEEE 802 Standards to Security Systems
    ASIS_GDL = "ASIS GDL"  # General Security Risk Assessment Guidelines
    UL_294 = "UL 294"  # Access Control System Units
    UL_1076 = "UL 1076"  # Proprietary Burglar Alarm Units and Systems

    # Federal Government Standards
    GSA_PBS = "GSA PBS"  # General Services Administration Public Buildings Service
    VA_STANDARDS = "VA"  # Department of Veterans Affairs Standards
    DOD_UFC = "DOD UFC"  # Department of Defense Unified Facilities Criteria
    FBI_CJIS = "FBI CJIS"  # Criminal Justice Information Services Security Policy
    FIPS_199 = "FIPS 199"  # Standards for Security Categorization
    NIST_800_53 = "NIST 800-53"  # Security Controls for Federal Information Systems

    # Accessibility & Safety
    ADA = "ADA"  # Americans with Disabilities Act
    OSHA = "OSHA"  # Occupational Safety and Health Administration
    MSHA = "MSHA"  # Mine Safety and Health Administration

    # Local & Regional
    LOCAL = "LOCAL"  # Local amendments and codes


class TradeCoordination:
    """Trade coordination issues and responsibilities"""

    FIRE_ALARM = "fire_alarm"
    MECHANICAL = "mechanical"
    ELECTRICAL = "electrical"
    GENERAL = "general"
    DISPUTED = "disputed"


class MultiCodeComplianceEngine(ConstructionIntelligenceBase):
    """Comprehensive building code compliance and specification intelligence"""

    def __init__(self):
        super().__init__()
        self.code_database = self._load_code_database()
        self.specification_patterns = self._load_specification_patterns()
        self.coordination_issues = self._load_coordination_issues()

    def analyze_multi_code_compliance(self, analysis: ConstructionAnalysis) -> Dict[str, Any]:
        """
        Comprehensive multi-code compliance analysis

        Args:
            analysis: Construction document analysis

        Returns:
            Dictionary containing compliance analysis for all codes
        """
        self.log_analysis("Starting multi-code compliance analysis")

        compliance_results = {
            "nfpa_72": self._analyze_nfpa_compliance(analysis),
            "ibc": self._analyze_ibc_compliance(analysis),
            "ada": self._analyze_ada_compliance(analysis),
            "imc": self._analyze_imc_compliance(analysis),
            "nec": self._analyze_nec_compliance(analysis),
            "bicsi": self._analyze_bicsi_compliance(analysis),
            "nicet": self._analyze_nicet_compliance(analysis),
            "osha": self._analyze_osha_compliance(analysis),
            "msha": self._analyze_msha_compliance(analysis),
            "coordination": self._analyze_trade_coordination(analysis),
            "specifications": self._analyze_specifications(analysis),
            "gotchas": self._identify_specification_gotchas(analysis),
        }

        # Count total issues safely
        total_issues = 0
        for v in compliance_results.values():
            if isinstance(v, dict) and "issues" in v:
                total_issues += len(v["issues"])
            elif isinstance(v, list):
                total_issues += len(v)

        self.log_analysis(f"Multi-code analysis complete: {total_issues} total issues")

        return compliance_results

    def _analyze_nfpa_compliance(self, analysis: ConstructionAnalysis) -> Dict[str, Any]:
        """Enhanced NFPA 72 compliance analysis"""
        issues = []

        # Existing NFPA analysis plus additional checks
        for fa_plan in analysis.fire_alarm_plans:
            # Check for accessible device placement (ADA coordination)
            devices = fa_plan.devices

            # Visual notification appliance requirements
            visual_devices = [d for d in devices if "strobe" in str(d.device_type).lower()]
            if not visual_devices:
                issues.append(
                    create_rfi_item(
                        category="NFPA 72 Visual Notification",
                        description="No visual notification appliances found - ADA compliance required",
                        priority="high",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Add visual notification per NFPA 72 Chapter 18 and ADA requirements",
                    )
                )

            # Mass notification requirements for certain occupancies
            for floor_plan in analysis.floor_plans:
                assembly_rooms = [
                    r for r in floor_plan.rooms if "assembly" in r.occupancy_type.lower()
                ]
                if assembly_rooms and not any(
                    "speaker" in str(d.device_type).lower() for d in devices
                ):
                    issues.append(
                        create_rfi_item(
                            category="NFPA 72 Mass Notification",
                            description="Assembly occupancy may require mass notification system",
                            priority="medium",
                            reference_drawing=fa_plan.sheet_number,
                            suggested_resolution="Verify mass notification requirements per NFPA 72 Chapter 24",
                        )
                    )

        return {
            "code": BuildingCode.NFPA_72,
            "issues": issues,
            "compliance_status": "requires_review" if issues else "compliant",
        }

    def _analyze_ibc_compliance(self, analysis: ConstructionAnalysis) -> Dict[str, Any]:
        """International Building Code compliance analysis"""
        issues = []

        for floor_plan in analysis.floor_plans:
            building_area = sum(room.area for room in floor_plan.rooms)

            # IBC occupancy classification requirements
            high_rise_threshold = 75  # feet (simplified)
            large_building_threshold = 12000  # sq ft

            if building_area > large_building_threshold:
                # Large buildings may require additional fire alarm features
                issues.append(
                    create_rfi_item(
                        category="IBC Large Building Requirements",
                        description=f"Building area {building_area:.0f} sq ft exceeds {large_building_threshold} sq ft threshold",
                        priority="medium",
                        reference_drawing=floor_plan.sheet_number,
                        suggested_resolution="Verify IBC Section 903 requirements for large buildings",
                    )
                )

            # Egress path notification requirements
            corridors = [r for r in floor_plan.rooms if "corridor" in r.name.lower()]
            if corridors:
                # Check for notification devices in egress paths
                corridor_notification = False
                for fa_plan in analysis.fire_alarm_plans:
                    corridor_devices = [
                        d for d in fa_plan.devices if d.room and "corridor" in d.room.lower()
                    ]
                    if any(
                        "strobe" in str(d.device_type).lower()
                        or "horn" in str(d.device_type).lower()
                        for d in corridor_devices
                    ):
                        corridor_notification = True

                if not corridor_notification:
                    issues.append(
                        create_rfi_item(
                            category="IBC Egress Notification",
                            description="Corridors require notification appliances per IBC egress requirements",
                            priority="high",
                            reference_drawing=floor_plan.sheet_number,
                            suggested_resolution="Add notification appliances in egress corridors per IBC Section 1006",
                        )
                    )

        return {
            "code": BuildingCode.IBC,
            "issues": issues,
            "compliance_status": "requires_review" if issues else "compliant",
        }

    def _analyze_ada_compliance(self, analysis: ConstructionAnalysis) -> Dict[str, Any]:
        """Americans with Disabilities Act compliance analysis"""
        issues = []

        for fa_plan in analysis.fire_alarm_plans:
            # ADA visual notification requirements
            notification_devices = [
                d for d in fa_plan.devices if "strobe" in str(d.device_type).lower()
            ]
            horn_only_devices = [
                d
                for d in fa_plan.devices
                if "horn" in str(d.device_type).lower()
                and "strobe" not in str(d.device_type).lower()
            ]

            if horn_only_devices and not notification_devices:
                issues.append(
                    create_rfi_item(
                        category="ADA Visual Notification",
                        description="Audible-only notification devices found - visual notification required for ADA compliance",
                        priority="high",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Replace horn-only devices with horn/strobe combinations per ADA requirements",
                    )
                )

            # Pull station height requirements
            pull_stations = [d for d in fa_plan.devices if "pull" in str(d.device_type).lower()]
            if pull_stations:
                issues.append(
                    create_rfi_item(
                        category="ADA Pull Station Height",
                        description='Verify pull station mounting heights comply with ADA (15" min, 48" max to operable part)',
                        priority="medium",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Confirm pull station heights meet ADA Section 205 reach range requirements",
                    )
                )

            # Accessible route coverage
            for floor_plan in analysis.floor_plans:
                corridor_rooms = [
                    r
                    for r in floor_plan.rooms
                    if "corridor" in r.name.lower() or "hallway" in r.name.lower()
                ]
                if corridor_rooms:
                    issues.append(
                        create_rfi_item(
                            category="ADA Accessible Route Notification",
                            description="Verify notification appliances provide adequate coverage along accessible routes",
                            priority="medium",
                            reference_drawing=floor_plan.sheet_number,
                            suggested_resolution="Ensure 75 cd minimum in corridors and accessible routes per ADA",
                        )
                    )

        return {
            "code": BuildingCode.ADA,
            "issues": issues,
            "compliance_status": "requires_review" if issues else "compliant",
        }

    def _analyze_imc_compliance(self, analysis: ConstructionAnalysis) -> Dict[str, Any]:
        """International Mechanical Code compliance analysis"""
        issues = []

        # Look for HVAC-related fire alarm requirements
        for floor_plan in analysis.floor_plans:
            mechanical_rooms = [
                r
                for r in floor_plan.rooms
                if any(
                    term in r.name.lower() for term in ["mechanical", "hvac", "fan", "air handler"]
                )
            ]

            if mechanical_rooms:
                # Check for duct detector requirements
                duct_detectors_found = False
                for fa_plan in analysis.fire_alarm_plans:
                    duct_related = [
                        d for d in fa_plan.devices if "duct" in str(d.notes or "").lower()
                    ]
                    if duct_related:
                        duct_detectors_found = True

                if not duct_detectors_found:
                    issues.append(
                        create_rfi_item(
                            category="IMC Duct Detector Requirements",
                            description="Mechanical rooms present but no duct detectors specified",
                            priority="high",
                            reference_drawing=floor_plan.sheet_number,
                            suggested_resolution="Verify duct detector requirements per IMC Section 606.2 and coordinate installation trade",
                        )
                    )

        # Data center/computer room requirements
        for floor_plan in analysis.floor_plans:
            computer_rooms = [
                r
                for r in floor_plan.rooms
                if any(term in r.name.lower() for term in ["data", "computer", "server", "telecom"])
            ]

            if computer_rooms:
                issues.append(
                    create_rfi_item(
                        category="IMC Computer Room Protection",
                        description="Computer/data rooms may require special fire protection systems",
                        priority="medium",
                        reference_drawing=floor_plan.sheet_number,
                        suggested_resolution="Verify IMC requirements for computer rooms and coordinate with mechanical systems",
                    )
                )

        return {
            "code": BuildingCode.IMC,
            "issues": issues,
            "compliance_status": "requires_review" if issues else "compliant",
        }

    def _analyze_osha_compliance(self, analysis: ConstructionAnalysis) -> Dict[str, Any]:
        """OSHA (Occupational Safety and Health Administration) compliance analysis"""
        issues = []

        # Analyze workplace safety requirements
        for fa_plan in analysis.fire_alarm_plans:
            devices = fa_plan.devices

            for floor_plan in analysis.floor_plans:
                # OSHA 1910.165 - Employee alarm systems
                for room in floor_plan.rooms:
                    if any(
                        workplace_type in room.occupancy_type.lower()
                        for workplace_type in ["office", "warehouse", "manufacturing", "industrial"]
                    ):
                        # Check for adequate audible alarm coverage in workplaces
                        audible_devices = [
                            d
                            for d in devices
                            if (
                                "horn" in str(d.device_type).lower()
                                or "speaker" in str(d.device_type).lower()
                            )
                            and d.room
                            and room.name.lower() in d.room.lower()
                        ]

                        # OSHA requires audible alarms in employee work areas
                        if not audible_devices and room.area > 500:  # sq ft threshold
                            issues.append(
                                create_rfi_item(
                                    category="OSHA Employee Alarm System",
                                    description=f"Workplace area {room.name} may require employee alarm system per OSHA 1910.165",
                                    priority="high",
                                    reference_drawing=fa_plan.sheet_number,
                                    suggested_resolution="Install audible alarm devices per OSHA 1910.165 employee alarm requirements",
                                )
                            )

                    # OSHA 1910.37 - Means of egress requirements
                    if "exit" in room.name.lower() or "corridor" in room.name.lower():
                        # Exit route alarm requirements
                        visual_devices = [
                            d
                            for d in devices
                            if (
                                "strobe" in str(d.device_type).lower()
                                or "visual" in str(d.device_type).lower()
                            )
                            and d.room
                            and room.name.lower() in d.room.lower()
                        ]

                        if not visual_devices:
                            issues.append(
                                create_rfi_item(
                                    category="OSHA Means of Egress",
                                    description=f"Exit route {room.name} may require visual alarm notification per OSHA 1910.37",
                                    priority="medium",
                                    reference_drawing=fa_plan.sheet_number,
                                    suggested_resolution="Verify OSHA egress route alarm requirements and coordinate with ADA compliance",
                                )
                            )

                    # OSHA 1910.120 - Hazardous waste operations (HAZWOPER)
                    if any(
                        hazard_type in room.occupancy_type.lower()
                        for hazard_type in ["chemical", "hazmat", "waste", "laboratory"]
                    ):
                        issues.append(
                            create_rfi_item(
                                category="OSHA HAZWOPER Requirements",
                                description=f"Hazardous area {room.name} may require specialized alarm systems per OSHA 1910.120",
                                priority="high",
                                reference_drawing=fa_plan.sheet_number,
                                suggested_resolution="Coordinate with safety officer for HAZWOPER alarm requirements and emergency response procedures",
                            )
                        )

        return {
            "code": BuildingCode.OSHA,
            "issues": issues,
            "compliance_status": "requires_review" if issues else "compliant",
        }

    def _analyze_msha_compliance(self, analysis: ConstructionAnalysis) -> Dict[str, Any]:
        """MSHA (Mine Safety and Health Administration) compliance analysis"""
        issues = []

        # Check if this is a mining-related facility
        mining_indicators = ["mine", "shaft", "tunnel", "quarry", "pit", "extraction", "processing"]
        is_mining_facility = False

        for floor_plan in analysis.floor_plans:
            for room in floor_plan.rooms:
                if any(
                    indicator in room.name.lower() or indicator in room.occupancy_type.lower()
                    for indicator in mining_indicators
                ):
                    is_mining_facility = True
                    break

        if is_mining_facility:
            # MSHA Part 75 - Underground coal mines
            # MSHA Part 57 - Metal and nonmetal underground mines
            for fa_plan in analysis.fire_alarm_plans:
                for floor_plan in analysis.floor_plans:
                    for room in floor_plan.rooms:
                        # Underground mine alarm requirements
                        if "underground" in room.name.lower() or "below" in room.name.lower():
                            issues.append(
                                create_rfi_item(
                                    category="MSHA Underground Mine Alarms",
                                    description=f"Underground area {room.name} requires MSHA-compliant alarm systems per 30 CFR 75/57",
                                    priority="critical",
                                    reference_drawing=fa_plan.sheet_number,
                                    suggested_resolution="Design intrinsically safe alarm system per MSHA underground mine requirements",
                                )
                            )

                        # Mine rescue and emergency response
                        if any(
                            area_type in room.name.lower()
                            for area_type in ["control", "dispatch", "office", "surface"]
                        ):
                            issues.append(
                                create_rfi_item(
                                    category="MSHA Emergency Communication",
                                    description=f"Mining facility {room.name} requires emergency communication systems per MSHA",
                                    priority="high",
                                    reference_drawing=fa_plan.sheet_number,
                                    suggested_resolution="Install MSHA-approved emergency communication and alarm systems",
                                )
                            )

                        # Conveyor and equipment areas
                        if any(
                            equipment_type in room.name.lower()
                            for equipment_type in [
                                "conveyor",
                                "crusher",
                                "mill",
                                "processing",
                                "equipment",
                            ]
                        ):
                            issues.append(
                                create_rfi_item(
                                    category="MSHA Equipment Area Alarms",
                                    description=f"Mining equipment area {room.name} requires specialized alarm systems per MSHA",
                                    priority="high",
                                    reference_drawing=fa_plan.sheet_number,
                                    suggested_resolution="Coordinate with mining engineer for MSHA equipment area alarm requirements",
                                )
                            )

                # Methane detection requirements for coal mines
                coal_mine_indicators = ["coal", "methane", "gas"]
                if any(indicator in str(analysis).lower() for indicator in coal_mine_indicators):
                    issues.append(
                        create_rfi_item(
                            category="MSHA Methane Detection",
                            description="Coal mining facility may require methane detection and alarm systems",
                            priority="critical",
                            reference_drawing=fa_plan.sheet_number,
                            suggested_resolution="Install MSHA-approved methane detection system with integrated fire alarm notification",
                        )
                    )

                # Mine rescue chamber requirements
                issues.append(
                    create_rfi_item(
                        category="MSHA Mine Rescue Chambers",
                        description="Mining facility may require mine rescue chamber alarm integration",
                        priority="high",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Coordinate rescue chamber alarm systems with main fire alarm panel per MSHA requirements",
                    )
                )

        else:
            # Not a mining facility - add informational note
            issues.append(
                create_rfi_item(
                    category="MSHA Applicability",
                    description="No mining operations detected - MSHA requirements may not apply",
                    priority="low",
                    reference_drawing="N/A",
                    suggested_resolution="Confirm facility type and MSHA applicability with project stakeholders",
                )
            )

        return {
            "code": BuildingCode.MSHA,
            "issues": issues,
            "compliance_status": "requires_review" if issues else "compliant",
        }

    def _analyze_nec_compliance(self, analysis: ConstructionAnalysis) -> Dict[str, Any]:
        """NEC (National Electrical Code - NFPA 70) compliance analysis for low voltage systems"""
        issues = []

        # NEC compliance analysis for low voltage systems
        for fa_plan in analysis.fire_alarm_plans:
            devices = fa_plan.devices
            circuits = fa_plan.circuits

            # NEC Article 760 - Fire Alarm Systems
            for circuit in circuits:
                # Check for proper circuit classification
                if "power limited" not in circuit.circuit_type.lower():
                    issues.append(
                        create_rfi_item(
                            category="NEC 760 Circuit Classification",
                            description=f"Circuit {circuit.circuit_id} classification needs verification per NEC 760",
                            priority="medium",
                            reference_drawing=fa_plan.sheet_number,
                            suggested_resolution="Verify power-limited vs non-power-limited classification per NEC 760.121",
                        )
                    )

                # NEC 760.136 - Installation of conductors and equipment in raceways
                if len(circuit.devices) > 20:  # Large circuit - check installation requirements
                    issues.append(
                        create_rfi_item(
                            category="NEC 760.136 Raceway Installation",
                            description=f"Large circuit {circuit.circuit_id} with {len(circuit.devices)} devices requires raceway verification",
                            priority="medium",
                            reference_drawing=fa_plan.sheet_number,
                            suggested_resolution="Verify raceway installation and conductor separation per NEC 760.136",
                        )
                    )

            # NEC Article 725 - Class 1, Class 2, and Class 3 Remote-Control, Signaling, and Power-Limited Circuits
            for floor_plan in analysis.floor_plans:
                for room in floor_plan.rooms:
                    # Access control and security system wiring (Class 2 circuits)
                    if any(
                        access_type in room.occupancy_type.lower()
                        for access_type in ["office", "secure", "control", "data"]
                    ):
                        issues.append(
                            create_rfi_item(
                                category="NEC 725 Class 2 Circuits",
                                description=f"Room {room.name} may require Class 2 circuit analysis for access control systems",
                                priority="medium",
                                reference_drawing=fa_plan.sheet_number,
                                suggested_resolution="Coordinate access control wiring with NEC 725 requirements for Class 2 circuits",
                            )
                        )

            # NEC Article 800 - Communications Circuits
            communications_rooms = [
                room
                for room in analysis.floor_plans[0].rooms
                if any(
                    comm_type in room.name.lower()
                    for comm_type in ["telecom", "data", "server", "network", "comm"]
                )
            ]
            if communications_rooms:
                for room in communications_rooms:
                    issues.append(
                        create_rfi_item(
                            category="NEC 800 Communications Circuits",
                            description=f"Communications room {room.name} requires NEC 800 compliance verification",
                            priority="high",
                            reference_drawing=fa_plan.sheet_number,
                            suggested_resolution="Verify communications circuit installation per NEC 800 and coordinate with fire alarm systems",
                        )
                    )

            # NEC Article 770 - Optical Fiber Cables and Raceways
            fiber_indicators = ["fiber", "optical", "backbone", "network"]
            for device in devices:
                if device.notes and any(
                    indicator in device.notes.lower() for indicator in fiber_indicators
                ):
                    issues.append(
                        create_rfi_item(
                            category="NEC 770 Fiber Optic Systems",
                            description=f"Device {device.circuit} appears to use fiber optic connections",
                            priority="medium",
                            reference_drawing=fa_plan.sheet_number,
                            suggested_resolution="Verify fiber optic installation per NEC 770 and fire stopping requirements",
                        )
                    )

            # NEC 760.3(G) - Fire alarm circuit integrity
            # Check for fire alarm circuit protection and monitoring
            monitoring_devices = [
                d
                for d in devices
                if "monitor" in str(d.device_type).lower()
                or "supervision" in str(d.notes or "").lower()
            ]
            if len(monitoring_devices) < len(circuits):
                issues.append(
                    create_rfi_item(
                        category="NEC 760.3(G) Circuit Integrity",
                        description="Fire alarm circuit integrity monitoring may be insufficient",
                        priority="high",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Verify circuit integrity monitoring per NEC 760.3(G) for all fire alarm circuits",
                    )
                )

            # NEC 760.43 - Fire alarm circuit grounding
            issues.append(
                create_rfi_item(
                    category="NEC 760.43 Grounding",
                    description="Fire alarm system grounding requires verification",
                    priority="medium",
                    reference_drawing=fa_plan.sheet_number,
                    suggested_resolution="Verify fire alarm system grounding and bonding per NEC 760.43",
                )
            )

            # NEC 110.26 - Working space around electrical equipment
            panel_locations = fa_plan.panel_locations or []
            for panel_location in panel_locations:
                issues.append(
                    create_rfi_item(
                        category="NEC 110.26 Working Space",
                        description=f"Fire alarm panel at {panel_location} requires working space verification",
                        priority="high",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Verify 3-foot minimum working space in front of fire alarm panel per NEC 110.26",
                    )
                )

            # Low voltage power supplies and battery backup
            # NEC 760.121 - Power sources for PLFA circuits
            issues.append(
                create_rfi_item(
                    category="NEC 760.121 Power Sources",
                    description="Power-limited fire alarm circuit power sources require verification",
                    priority="medium",
                    reference_drawing=fa_plan.sheet_number,
                    suggested_resolution="Verify power supply compliance with NEC 760.121 for power-limited circuits",
                )
            )

            # Emergency power requirements
            # NEC Article 700 - Emergency Systems (if applicable)
            emergency_indicators = ["emergency", "egress", "exit", "life safety"]
            emergency_devices = [
                d
                for d in devices
                if d.room and any(indicator in d.room.lower() for indicator in emergency_indicators)
            ]
            if emergency_devices:
                issues.append(
                    create_rfi_item(
                        category="NEC 700 Emergency Systems",
                        description="Emergency lighting and fire alarm coordination may require NEC 700 compliance",
                        priority="high",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Coordinate emergency systems with fire alarm per NEC 700 requirements",
                    )
                )

        return {
            "code": BuildingCode.NEC,
            "issues": issues,
            "compliance_status": "requires_review" if issues else "compliant",
        }

    def _analyze_bicsi_compliance(self, analysis: ConstructionAnalysis) -> Dict[str, Any]:
        """BICSI (Building Industry Consulting Service International) compliance analysis"""
        issues = []

        # BICSI compliance analysis for telecommunications and data systems
        for fa_plan in analysis.fire_alarm_plans:
            devices = fa_plan.devices
            circuits = fa_plan.circuits

            # BICSI TDMM (Telecommunications Distribution Methods Manual) compliance
            telecom_circuits = [
                c
                for c in circuits
                if "data" in c.circuit_type.lower() or "cat" in c.wire_type.lower()
            ]
            for circuit in telecom_circuits:
                # BICSI cable management and pathway requirements
                if len(circuit.route_points) < 2:
                    issues.append(
                        create_rfi_item(
                            category="BICSI TDMM Pathway Design",
                            description=f"Circuit {circuit.circuit_id} requires proper pathway documentation per BICSI TDMM",
                            priority="medium",
                            reference_drawing=fa_plan.sheet_number,
                            suggested_resolution="Document cable pathways and routing per BICSI TDMM guidelines",
                        )
                    )

                # BICSI cable bend radius requirements
                if "cat6" in circuit.wire_type.lower() or "fiber" in circuit.wire_type.lower():
                    issues.append(
                        create_rfi_item(
                            category="BICSI Cable Bend Radius",
                            description=f"Circuit {circuit.circuit_id} requires bend radius verification per BICSI standards",
                            priority="medium",
                            reference_drawing=fa_plan.sheet_number,
                            suggested_resolution="Verify minimum bend radius: 4x cable diameter for UTP, 10x for fiber per BICSI",
                        )
                    )

            # BICSI ITS (Information Transport Systems) Installation Methods
            network_devices = [
                d
                for d in devices
                if d.device_type
                in [
                    DeviceType.WIRELESS_AP,
                    DeviceType.SWITCH,
                    DeviceType.ROUTER,
                    DeviceType.PATCH_PANEL,
                ]
            ]
            for device in network_devices:
                issues.append(
                    create_rfi_item(
                        category="BICSI ITS Installation",
                        description=f"Network device {device.address} installation requires BICSI ITS compliance verification",
                        priority="medium",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Verify installation methods per BICSI ITS manual for network equipment",
                    )
                )

            # BICSI DDM (Data Center Design) for data/telecom rooms
            for floor_plan in analysis.floor_plans:
                data_rooms = [
                    room
                    for room in floor_plan.rooms
                    if any(
                        data_type in room.name.lower()
                        for data_type in ["data", "server", "telecom", "comm", "network"]
                    )
                ]
                for room in data_rooms:
                    # BICSI environmental requirements
                    issues.append(
                        create_rfi_item(
                            category="BICSI DDM Environmental",
                            description=f"Data room {room.name} requires environmental controls per BICSI DDM",
                            priority="high",
                            reference_drawing=fa_plan.sheet_number,
                            suggested_resolution="Verify temperature/humidity controls, ventilation per BICSI DDM data center standards",
                        )
                    )

                    # BICSI power and grounding
                    issues.append(
                        create_rfi_item(
                            category="BICSI DDM Power & Grounding",
                            description=f"Data room {room.name} requires proper power and grounding per BICSI DDM",
                            priority="high",
                            reference_drawing=fa_plan.sheet_number,
                            suggested_resolution="Verify isolated ground, dedicated circuits, and grounding per BICSI DDM",
                        )
                    )

                    # BICSI cable management
                    if room.area > 100:  # Larger data rooms
                        issues.append(
                            create_rfi_item(
                                category="BICSI DDM Cable Management",
                                description=f"Large data room {room.name} requires structured cable management per BICSI DDM",
                                priority="medium",
                                reference_drawing=fa_plan.sheet_number,
                                suggested_resolution="Install cable trays, J-hooks, and management systems per BICSI DDM",
                            )
                        )

            # BICSI WDS (Wireless Design Standards) for wireless systems
            wireless_devices = [d for d in devices if d.device_type == DeviceType.WIRELESS_AP]
            if wireless_devices:
                issues.append(
                    create_rfi_item(
                        category="BICSI WDS Site Survey",
                        description="Wireless access points require RF site survey per BICSI WDS",
                        priority="high",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Conduct RF site survey and heat mapping per BICSI WDS wireless design standards",
                    )
                )

                # BICSI PoE power requirements
                poe_devices = [d for d in devices if "poe" in str(d.circuit).lower()]
                if poe_devices:
                    issues.append(
                        create_rfi_item(
                            category="BICSI WDS PoE Requirements",
                            description="PoE devices require power budget analysis per BICSI WDS",
                            priority="medium",
                            reference_drawing=fa_plan.sheet_number,
                            suggested_resolution="Calculate PoE power budget and heat dissipation per BICSI WDS",
                        )
                    )

            # BICSI-001 Data Center certification requirements
            data_center_rooms = [
                room
                for room in analysis.floor_plans[0].rooms
                if "data center" in room.name.lower() or room.area > 1000
            ]
            if data_center_rooms:
                issues.append(
                    create_rfi_item(
                        category="BICSI-001 Data Center Design",
                        description="Data center requires BICSI-001 design certification compliance",
                        priority="high",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Engage BICSI-certified designer for data center design per BICSI-001",
                    )
                )

        return {
            "code": BuildingCode.BICSI_TDMM,
            "issues": issues,
            "compliance_status": "requires_review" if issues else "compliant",
        }

    def _analyze_nicet_compliance(self, analysis: ConstructionAnalysis) -> Dict[str, Any]:
        """NICET (National Institute for Certification in Engineering Technologies) compliance analysis"""
        issues = []

        # NICET Fire Alarm Systems compliance (Mike Holtz standards)
        for fa_plan in analysis.fire_alarm_plans:
            devices = fa_plan.devices
            circuits = fa_plan.circuits

            # NICET Level I - Basic fire alarm installation requirements
            basic_devices = [
                d
                for d in devices
                if d.device_type
                in [DeviceType.SMOKE_DETECTOR, DeviceType.HEAT_DETECTOR, DeviceType.PULL_STATION]
            ]
            for device in basic_devices:
                if not device.address or not device.circuit:
                    issues.append(
                        create_rfi_item(
                            category="NICET Level I Device Addressing",
                            description=f"Device {device.device_type.value} missing address or circuit assignment",
                            priority="high",
                            reference_drawing=fa_plan.sheet_number,
                            suggested_resolution="Assign proper device addressing per NICET Level I requirements",
                        )
                    )

            # NICET Level II - Circuit design and calculations
            for circuit in circuits:
                if len(circuit.devices) > 99:  # Common addressable limit
                    issues.append(
                        create_rfi_item(
                            category="NICET Level II Circuit Loading",
                            description=f"Circuit {circuit.circuit_id} may exceed device capacity per NICET Level II",
                            priority="high",
                            reference_drawing=fa_plan.sheet_number,
                            suggested_resolution="Verify circuit loading calculations per NICET Level II standards",
                        )
                    )

                # NICET voltage drop calculations
                if len(circuit.route_points) > 2:  # Long circuit runs
                    issues.append(
                        create_rfi_item(
                            category="NICET Level II Voltage Drop",
                            description=f"Circuit {circuit.circuit_id} requires voltage drop calculation per NICET Level II",
                            priority="medium",
                            reference_drawing=fa_plan.sheet_number,
                            suggested_resolution="Calculate voltage drop for circuit length per NICET Level II methods",
                        )
                    )

            # NICET Level III - System design and engineering
            system_complexity = len(devices) + len(circuits)
            if system_complexity > 50:  # Complex system threshold
                issues.append(
                    create_rfi_item(
                        category="NICET Level III System Design",
                        description="Complex fire alarm system requires NICET Level III design review",
                        priority="high",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Engage NICET Level III certified technician for system design review",
                    )
                )

                # NICET documentation requirements
                issues.append(
                    create_rfi_item(
                        category="NICET Level III Documentation",
                        description="System requires comprehensive documentation per NICET Level III",
                        priority="medium",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Provide sequence of operations, battery calculations, and system specifications",
                    )
                )

            # NICET Level IV - Advanced system engineering and special applications
            special_devices = [
                d
                for d in devices
                if d.device_type in [DeviceType.BEAM_DETECTOR, DeviceType.DUCT_DETECTOR]
                or (
                    d.notes
                    and any(
                        special in d.notes.lower() for special in ["intelligent", "multi", "analog"]
                    )
                )
            ]
            if special_devices:
                issues.append(
                    create_rfi_item(
                        category="NICET Level IV Special Applications",
                        description="Special detection devices require NICET Level IV expertise",
                        priority="high",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Engage NICET Level IV certified engineer for special applications",
                    )
                )

            # NICET installation workmanship standards (Mike Holtz emphasis)
            installation_issues = []

            # Device mounting requirements
            for device in devices:
                if device.device_type == DeviceType.SMOKE_DETECTOR:
                    installation_issues.append(
                        "Smoke detector spacing and mounting height verification"
                    )
                elif device.device_type == DeviceType.PULL_STATION:
                    installation_issues.append(
                        'Pull station mounting height 42" to centerline per NICET'
                    )
                elif device.device_type == DeviceType.HORN_STROBE:
                    installation_issues.append(
                        "Horn/strobe mounting and candela rating verification"
                    )

            if installation_issues:
                issues.append(
                    create_rfi_item(
                        category="NICET Installation Standards",
                        description="Fire alarm devices require NICET installation standard compliance",
                        priority="medium",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution=f"Verify installation per NICET standards: {', '.join(installation_issues[:3])}",
                    )
                )

            # NICET testing and commissioning requirements
            issues.append(
                create_rfi_item(
                    category="NICET Testing & Commissioning",
                    description="Fire alarm system requires NICET-standard testing and commissioning",
                    priority="high",
                    reference_drawing=fa_plan.sheet_number,
                    suggested_resolution="Develop testing procedures per NICET standards and NFPA 72 Chapter 14",
                )
            )

            # NICET ongoing maintenance requirements
            issues.append(
                create_rfi_item(
                    category="NICET Maintenance Documentation",
                    description="System requires maintenance documentation per NICET standards",
                    priority="medium",
                    reference_drawing=fa_plan.sheet_number,
                    suggested_resolution="Provide maintenance manual and inspection/testing schedules per NICET",
                )
            )

        return {
            "code": BuildingCode.NICET_FIRE_2,  # Representative NICET standard
            "issues": issues,
            "compliance_status": "requires_review" if issues else "compliant",
        }

    def _analyze_trade_coordination(self, analysis: ConstructionAnalysis) -> Dict[str, Any]:
        """Analyze trade coordination issues and responsibilities"""
        coordination_issues = []

        # Duct detector installation coordination - THE BIG ONE!
        duct_detector_issue = self._analyze_duct_detector_coordination(analysis)
        if duct_detector_issue:
            coordination_issues.append(duct_detector_issue)

        # Electrical coordination
        electrical_issues = self._analyze_electrical_coordination(analysis)
        coordination_issues.extend(electrical_issues)

        # Mechanical coordination
        mechanical_issues = self._analyze_mechanical_coordination(analysis)
        coordination_issues.extend(mechanical_issues)

        # General contractor coordination
        general_issues = self._analyze_general_coordination(analysis)
        coordination_issues.extend(general_issues)

        return {
            "trade": "multi_trade",
            "issues": coordination_issues,
            "critical_items": [
                issue for issue in coordination_issues if issue.priority == Priority.CRITICAL
            ],
        }

    def _analyze_duct_detector_coordination(self, analysis: ConstructionAnalysis) -> RFIItem | None:
        """Analyze the classic duct detector coordination issue"""
        # Look for evidence of duct detectors
        duct_detectors_mentioned = False

        for fa_plan in analysis.fire_alarm_plans:
            for device in fa_plan.devices:
                if device.notes and "duct" in device.notes.lower():
                    duct_detectors_mentioned = True
                    break

        # Check specifications for duct detector mentions
        for spec in analysis.specifications:
            if isinstance(spec, dict) and "content" in spec:
                if "duct detector" in spec["content"].lower():
                    duct_detectors_mentioned = True
                    break

        if duct_detectors_mentioned:
            return create_rfi_item(
                category="Trade Coordination - Duct Detectors",
                description="CRITICAL: Duct detector installation responsibility unclear - Mechanical or Fire Alarm contractor?",
                priority="critical",
                reference_drawing="General",
                location="HVAC systems",
                suggested_resolution="""Clarify duct detector installation responsibility:
- Option 1: Mechanical contractor installs, FA contractor wires/programs
- Option 2: FA contractor furnishes and installs complete
- Coordinate access, mounting, and wiring requirements
- Specify shutdown relay locations and responsibilities""",
            )

        return None

    def _analyze_electrical_coordination(self, analysis: ConstructionAnalysis) -> List[RFIItem]:
        """Analyze electrical trade coordination issues"""
        issues = []

        # Power supply coordination
        if analysis.fire_alarm_plans:
            issues.append(
                create_rfi_item(
                    category="Electrical Coordination - Power",
                    description="Fire alarm panel power supply coordination required with electrical contractor",
                    priority="medium",
                    reference_drawing="General",
                    suggested_resolution="Coordinate dedicated 20A circuit, surge protection, and emergency power requirements",
                )
            )

        # Conduit and wiring coordination
        device_count = sum(len(plan.devices) for plan in analysis.fire_alarm_plans)
        if device_count > 10:
            issues.append(
                create_rfi_item(
                    category="Electrical Coordination - Conduit",
                    description="Fire alarm conduit routing and electrical room coordination required",
                    priority="medium",
                    reference_drawing="General",
                    suggested_resolution="Coordinate fire alarm conduit routing with electrical contractor - avoid conflicts",
                )
            )

        return issues

    def _analyze_mechanical_coordination(self, analysis: ConstructionAnalysis) -> List[RFIItem]:
        """Analyze mechanical trade coordination issues"""
        issues = []

        # HVAC shutdown coordination
        for floor_plan in analysis.floor_plans:
            mechanical_rooms = [r for r in floor_plan.rooms if "mechanical" in r.name.lower()]
            if mechanical_rooms:
                issues.append(
                    create_rfi_item(
                        category="Mechanical Coordination - HVAC Shutdown",
                        description="HVAC system shutdown coordination required for fire alarm activation",
                        priority="high",
                        reference_drawing=floor_plan.sheet_number,
                        suggested_resolution="Coordinate HVAC shutdown relays, fan control, and damper operation with mechanical contractor",
                    )
                )

        return issues

    def _analyze_general_coordination(self, analysis: ConstructionAnalysis) -> List[RFIItem]:
        """Analyze general contractor coordination issues"""
        issues = []

        # Ceiling coordination
        device_count = sum(len(plan.devices) for plan in analysis.fire_alarm_plans)
        if device_count > 5:
            issues.append(
                create_rfi_item(
                    category="General Coordination - Ceiling Access",
                    description="Fire alarm device installation requires ceiling coordination",
                    priority="medium",
                    reference_drawing="General",
                    suggested_resolution="Coordinate ceiling grid modifications, access panels, and patching requirements",
                )
            )

        return issues

    def _analyze_specifications(self, analysis: ConstructionAnalysis) -> Dict[str, Any]:
        """Analyze and summarize specifications with cliff notes"""
        spec_analysis = {
            "summary": [],
            "key_requirements": [],
            "manufacturer_restrictions": [],
            "testing_requirements": [],
            "warranty_requirements": [],
        }

        for spec in analysis.specifications:
            if isinstance(spec, dict) and "content" in spec:
                content = spec["content"]

                # Extract key manufacturer information
                manufacturers = self._extract_manufacturers(content)
                if manufacturers:
                    spec_analysis["manufacturer_restrictions"].extend(manufacturers)

                # Extract testing requirements
                testing = self._extract_testing_requirements(content)
                if testing:
                    spec_analysis["testing_requirements"].extend(testing)

                # Extract warranty information
                warranty = self._extract_warranty_requirements(content)
                if warranty:
                    spec_analysis["warranty_requirements"].extend(warranty)

                # Generate summary
                summary = self._generate_specification_summary(content)
                if summary:
                    spec_analysis["summary"].append(summary)

        return spec_analysis

    def _identify_specification_gotchas(
        self, analysis: ConstructionAnalysis
    ) -> List[Dict[str, Any]]:
        """Identify specification gotchas and potential problems"""
        gotchas = []

        for spec in analysis.specifications:
            if isinstance(spec, dict) and "content" in spec:
                content = spec["content"].lower()

                # Common gotchas
                if "or equal" in content and "pre-approved" in content:
                    gotchas.append(
                        {
                            "type": "specification_conflict",
                            "description": 'Specification contains both "or equal" and "pre-approved" language - potential conflict',
                            "severity": "medium",
                            "recommendation": "Clarify if substitutions are allowed and approval process",
                        }
                    )

                if "proprietary" in content or "sole source" in content:
                    gotchas.append(
                        {
                            "type": "proprietary_specification",
                            "description": "Proprietary specification detected - may limit competition",
                            "severity": "low",
                            "recommendation": "Verify proprietary specification is justified",
                        }
                    )

                if "latest version" in content or "current edition" in content:
                    gotchas.append(
                        {
                            "type": "version_ambiguity",
                            "description": 'Specification references "latest version" without specific edition',
                            "severity": "medium",
                            "recommendation": "Specify exact code edition and standard versions",
                        }
                    )

                if "coordinate" in content and "other trades" in content:
                    gotchas.append(
                        {
                            "type": "coordination_required",
                            "description": "Specification requires coordination with other trades",
                            "severity": "high",
                            "recommendation": "Identify specific coordination requirements and responsible parties",
                        }
                    )

                # Duct detector gotcha
                if "duct detector" in content and "furnished by" not in content:
                    gotchas.append(
                        {
                            "type": "duct_detector_responsibility",
                            "description": "GOTCHA: Duct detector responsibility not clearly specified",
                            "severity": "critical",
                            "recommendation": "Clarify if mechanical or fire alarm contractor provides and installs duct detectors",
                        }
                    )

        return gotchas

    def _extract_manufacturers(self, content: str) -> List[str]:
        """Extract manufacturer requirements from specifications"""
        manufacturers = []

        # Common fire alarm manufacturers
        mfg_patterns = [
            r"(Simplex|Edwards|Gamewell|Notifier|Fire-Lite|Honeywell|Johnson Controls|Siemens|Bosch)",
            r"(EST|FCI|Mircom|Potter|Kidde|Hochiki|Apollo|Tyco)",
        ]

        for pattern in mfg_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                manufacturers.append(match.group(1))

        return list(set(manufacturers))  # Remove duplicates

    def _extract_testing_requirements(self, content: str) -> List[str]:
        """Extract testing requirements from specifications"""
        testing = []

        testing_patterns = [
            r"(acceptance test|commissioning|functional test|installation test)",
            r"(witness test|performance test|final test)",
            r"(NFPA 72.*test|code compliance test)",
        ]

        for pattern in testing_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                testing.append(match.group(1))

        return list(set(testing))

    def _extract_warranty_requirements(self, content: str) -> List[str]:
        """Extract warranty requirements from specifications"""
        warranty = []

        warranty_patterns = [
            r"(\d+)\s*year\s*warranty",
            r"warranty.*(\d+).*years?",
            r"(manufacturer.*warranty|factory warranty)",
        ]

        for pattern in warranty_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                warranty.append(match.group(0))

        return warranty

    def _generate_specification_summary(self, content: str) -> str:
        """Generate cliff notes summary of specification"""
        # This is a simplified version - in practice would use more sophisticated NLP
        summary_points = []

        if "fire alarm" in content.lower():
            summary_points.append("Fire alarm system specification")

        if "addressable" in content.lower():
            summary_points.append("Addressable system required")

        if "conventional" in content.lower():
            summary_points.append("Conventional system specified")

        if len(summary_points) > 0:
            return "; ".join(summary_points)

        return "General fire protection specification"

    def _load_code_database(self) -> Dict[str, Any]:
        """Load building code database"""
        return {
            "nfpa_72": {
                "spacing_requirements": {"smoke_detector": 30.0, "heat_detector": 50.0},
                "notification_requirements": {"corridor_min_candela": 15, "room_min_candela": 75},
            },
            "ibc": {
                "occupancy_requirements": {
                    "assembly": "special_requirements",
                    "business": "standard_requirements",
                }
            },
            "ada": {
                "mounting_heights": {
                    "pull_station_min": 15,  # inches
                    "pull_station_max": 48,  # inches
                },
                "notification_requirements": {"visual_required": True, "corridor_min_candela": 75},
            },
        }

    def _load_specification_patterns(self) -> Dict[str, List[str]]:
        """Load specification analysis patterns"""
        return {
            "gotcha_patterns": [
                r"or equal.*pre-approved",
                r"latest version",
                r"coordinate.*other trades",
                r"duct detector.*furnished",
            ],
            "manufacturer_patterns": [
                r"(Simplex|Edwards|Gamewell|Notifier)",
                r"(Fire-Lite|Honeywell|Johnson Controls)",
            ],
        }

    def _load_coordination_issues(self) -> Dict[str, Dict[str, Any]]:
        """Load common trade coordination issues"""
        return {
            "duct_detectors": {
                "description": "Duct detector installation responsibility",
                "trades_involved": [TradeCoordination.MECHANICAL, TradeCoordination.FIRE_ALARM],
                "typical_resolution": "Mechanical furnishes and installs, FA contractor wires",
                "priority": Priority.CRITICAL,
            },
            "hvac_shutdown": {
                "description": "HVAC system shutdown coordination",
                "trades_involved": [TradeCoordination.MECHANICAL, TradeCoordination.FIRE_ALARM],
                "typical_resolution": "Mechanical provides shutdown relays, FA provides control signal",
                "priority": Priority.HIGH,
            },
            "electrical_power": {
                "description": "Fire alarm panel power supply",
                "trades_involved": [TradeCoordination.ELECTRICAL, TradeCoordination.FIRE_ALARM],
                "typical_resolution": "Electrical provides dedicated circuit to FA panel location",
                "priority": Priority.MEDIUM,
            },
        }

    def export_compliance_report(
        self,
        compliance_results: Dict[str, Any],
        output_path: str,
        project_name: str = "Unknown Project",
    ):
        """Export comprehensive compliance report"""
        with open(output_path, "w") as f:
            f.write("# MULTI-CODE COMPLIANCE ANALYSIS\n\n")
            f.write(f"**Project:** {project_name}\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")

            # Code compliance summary
            f.write("## Code Compliance Summary\n\n")
            for code_name, results in compliance_results.items():
                if isinstance(results, dict) and "code" in results:
                    status = results.get("compliance_status", "unknown")
                    issue_count = len(results.get("issues", []))
                    f.write(f"- **{results['code']}**: {status} ({issue_count} issues)\n")

            # Specification analysis
            if "specifications" in compliance_results:
                spec_analysis = compliance_results["specifications"]
                f.write("\n## Specification Analysis\n")
                f.write(
                    f"- Manufacturers: {', '.join(spec_analysis.get('manufacturer_restrictions', ['None specified']))}\n"
                )
                f.write(
                    f"- Testing requirements: {len(spec_analysis.get('testing_requirements', []))}\n"
                )
                f.write(
                    f"- Warranty requirements: {len(spec_analysis.get('warranty_requirements', []))}\n"
                )

            # Gotchas
            if "gotchas" in compliance_results:
                gotchas = compliance_results["gotchas"]
                f.write(f"\n## Specification Gotchas ({len(gotchas)})\n")
                for gotcha in gotchas:
                    f.write(f"- **{gotcha['type'].upper()}**: {gotcha['description']}\n")
                    f.write(f"  - Severity: {gotcha['severity']}\n")
                    f.write(f"  - Recommendation: {gotcha['recommendation']}\n\n")

            # Trade coordination
            if "coordination" in compliance_results:
                coord_issues = compliance_results["coordination"]["issues"]
                critical_items = compliance_results["coordination"]["critical_items"]

                f.write(f"## Trade Coordination Issues ({len(coord_issues)})\n")
                if critical_items:
                    f.write(f"### CRITICAL ITEMS ({len(critical_items)})\n")
                    for item in critical_items:
                        f.write(f"- **{item.category}**: {item.description}\n")
                        f.write(f"  - Resolution: {item.suggested_resolution}\n\n")


# Factory function for easy usage
def analyze_multi_code_compliance(analysis: ConstructionAnalysis) -> Dict[str, Any]:
    """
    Convenient function for multi-code compliance analysis

    Args:
        analysis: Construction document analysis

    Returns:
        Multi-code compliance results
    """
    engine = MultiCodeComplianceEngine()
    return engine.analyze_multi_code_compliance(analysis)
