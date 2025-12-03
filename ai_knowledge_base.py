"""
AI Knowledge Base for AutoFire
==============================

Centralized knowledge repository for AI assistants and automation.
Contains domain expertise, training materials, and contextual information
for fire protection and low voltage design systems.
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AIKnowledgeBase:
    """
    Comprehensive knowledge base for AutoFire AI systems.

    Contains training materials, domain expertise, and contextual information
    for fire protection design, low voltage systems, and building automation.
    """

    def __init__(self) -> None:
        """Initialize the knowledge base with training content."""
        self.knowledge_domains = {
            "low_voltage_design": self._load_low_voltage_training(),
            "fire_protection": self._load_fire_protection_knowledge(),
            "building_codes": self._load_building_codes(),
            "system_integration": self._load_system_integration(),
        }

    def _load_low_voltage_training(self) -> dict[str, Any]:
        """Load comprehensive low voltage designer training content."""
        return {
            "overview": {
                "definition": "Low Voltage Design involves electrical and electronic systems operating below 50 volts, focusing on life safety, communication, and building automation systems.",
                "primary_focus": "Fire alarm systems, emergency communications, security integration, and building automation",
                "key_standards": ["NFPA 72", "NFPA 70 (NEC)", "NFPA 101", "IBC/IFC"],
            },
            "system_architecture": {
                "fire_alarm_components": {
                    "control_panel": "Fire Alarm Control Panel (FACP)",
                    "initiating_devices": [
                        "Smoke Detectors",
                        "Heat Detectors",
                        "Manual Pull Stations",
                        "Waterflow Switches",
                    ],
                    "notification_appliances": [
                        "Audible Horns",
                        "Visual Strobes",
                        "Combination Horn/Strobes",
                        "Speakers",
                    ],
                    "power_supplies": [
                        "Primary Power (120/240VAC)",
                        "Secondary Power (Battery Backup)",
                        "Inverter Systems",
                    ],
                    "annunciators": ["Remote Displays", "LED Panels", "LCD Displays"],
                },
                "low_voltage_categories": {
                    "class_1": "Fire Alarm Systems (NEC Article 760)",
                    "class_2": "Limited Energy Systems (NEC Article 725)",
                    "class_3": "Power-Limited Fire Alarm (NEC Article 760)",
                },
            },
            "code_hierarchy": {
                "federal_codes": ["OSHA", "ADA", "Federal Energy Policy Act"],
                "model_codes": ["IBC", "IFC", "NEC/NFPA 70"],
                "industry_standards": ["NFPA 72", "NFPA 101", "UL Standards"],
                "local_amendments": [
                    "State Fire Marshal",
                    "Local Building Department",
                    "AHJ Interpretations",
                ],
            },
            "nfpa_72_deep_dive": {
                "coverage_calculations": {
                    "smoke_detector_spacing": {
                        "smooth_ceiling": 900,  # sq ft max
                        "ceiling_height_10ft": 900,
                        "ceiling_height_14ft": 640,
                        "beam_depth_4ft": 640,
                    },
                    "heat_detector_spacing": {
                        "light_hazard": 50,  # ft spacing
                        "ordinary_hazard": 40,
                        "extra_hazard": 30,
                    },
                },
                "power_calculations": {
                    "battery_formula": "Capacity = (Current × Standby_Time) + (Alarm_Current × Alarm_Time) × Safety_Factor × Temp_Factor",
                    "standby_time": 24,  # hours
                    "alarm_time": 5,  # minutes
                    "safety_factor": 1.25,  # 25%
                    "temperature_factor": 1.1,  # 10% for temperature
                },
                "circuit_design": {
                    "copper_resistivity": 12.9,  # ohm-circular mils per foot at 75°C
                    "voltage_drop_limit": 0.1,  # 10% maximum
                    "conductor_sizing": "NEC Table 310.15(B)(16)",
                },
            },
            "occupancy_classifications": {
                "assembly": {
                    "A-1": "Theater, concert hall (>300 occupants)",
                    "A-2": "Restaurant, bar (>50 occupants)",
                    "A-3": "Church, library, museum",
                    "A-4": "Arena, skating rink",
                    "A-5": "Stadium, amusement park",
                },
                "educational": {"E": "Preschool through grade 12"},
                "healthcare": {
                    "H-1": "Hospital, nursing home",
                    "H-2": "Limited care facilities",
                    "H-3": "Surgery centers, birthing centers",
                },
                "residential": {
                    "R-1": "Hotels, motels",
                    "R-2": "Apartment buildings",
                    "R-3": "One- and two-family dwellings",
                    "R-4": "Assisted living facilities",
                },
            },
            "special_hazard_applications": {
                "hazardous_locations": {
                    "class_I": "Flammable gases/vapors",
                    "class_II": "Combustible dusts",
                    "class_III": "Ignitable fibers/flyings",
                    "division_1": "Hazard present under normal conditions",
                    "division_2": "Hazard present only under abnormal conditions",
                },
                "clean_rooms_laboratories": {
                    "nfpa_45": "Fire Protection for Laboratories Using Chemicals",
                    "air_handling_detection": "Detection in air handling systems",
                    "special_extinguishing": "Special extinguishing system interfaces",
                },
            },
            "system_integration": {
                "hvac_integration": [
                    "Smoke detector inputs to shut down air handlers",
                    "Duct detector monitoring",
                    "Emergency smoke purge activation",
                    "Temperature sensor inputs",
                    "Building automation system (BAS) coordination",
                ],
                "elevator_integration": [
                    "Fire service recall functions",
                    "Emergency voice communication",
                    "Floor indicator displays",
                    "Door hold/open functions",
                    "Priority service for firefighters",
                ],
                "security_integration": [
                    "Access control system coordination",
                    "Video surveillance triggering",
                    "Intrusion detection interfaces",
                    "Mass notification system links",
                    "Emergency communication pathways",
                ],
            },
            "sequence_of_operations": {
                "fire_alarm_sequence": [
                    "1. Initiating device activates",
                    "2. Control panel enters alarm state",
                    "3. Notification appliances activate (temporal pattern)",
                    "4. Emergency communication system activates",
                    "5. Elevator recall initiates",
                    "6. HVAC smoke purge activates",
                    "7. Fire department notification transmits",
                    "8. Building automation system responds",
                ]
            },
            "documentation_requirements": {
                "construction_documents": [
                    "System Layout Plans",
                    "Riser Diagrams",
                    "Wiring Diagrams",
                    "Panel Layouts",
                    "Device Details",
                ],
                "calculations_package": [
                    "Battery capacity calculations",
                    "Voltage drop calculations",
                    "Coverage area verification",
                    "Circuit loading analysis",
                    "Sound pressure level calculations",
                ],
            },
            "testing_commissioning": {
                "acceptance_testing": {
                    "visual_inspection": [
                        "Equipment verification",
                        "Wiring continuity",
                        "Mounting/orientation",
                        "Labels/identification",
                    ],
                    "functional_testing": [
                        "Device sensitivity",
                        "Circuit supervision",
                        "Appliance operation",
                        "Communication testing",
                    ],
                    "performance_testing": [
                        "Battery discharge",
                        "Power failure simulation",
                        "Capacity verification",
                        "End-to-end operation",
                    ],
                },
                "maintenance_frequencies": {
                    "monthly": ["Battery checks", "Lamp tests"],
                    "quarterly": ["Functional tests of initiating devices"],
                    "semi_annually": ["Complete functional test"],
                    "annually": ["Full system test and inspection"],
                },
            },
            "practical_scenarios": {
                "office_building": {
                    "parameters": "5-story, 50,000 sq ft per floor, business occupancy",
                    "smoke_detectors_per_floor": 56,  # 50000/900 = 56
                    "total_system": "280 smoke detectors, 20 manual stations, 560 horn/strobes",
                },
                "hospital_system": {
                    "special_requirements": [
                        "100% patient room coverage",
                        "Emergency communication",
                        "Medical gas integration",
                    ],
                    "corridor_coverage": "Complete coverage per NFPA 72",
                    "staff_assistance": "Emergency call stations at strategic locations",
                },
                "high_rise_residential": {
                    "challenges": [
                        "Vertical transport",
                        "Common area coverage",
                        "Emergency communication",
                    ],
                    "requirements": [
                        "Smoke detectors in corridors/elevator lobbies",
                        "Two-way communication in stairs",
                    ],
                },
                "industrial_warehouse": {
                    "challenges": [
                        "Large open spaces",
                        "High ceilings (40ft)",
                        "Extra hazard classification",
                    ],
                    "solutions": [
                        "Beam detectors",
                        "Aspirating smoke detection",
                        "Extended spacing calculations",
                    ],
                },
            },
            "code_compliance_checklists": {
                "nfpa_72_compliance": [
                    "Building area calculations verified",
                    "Occupancy classification correct (NFPA 101)",
                    "Detector spacing per Table 17.6.3.4.1",
                    "Wall proximity requirements met (17.6.3.4.3)",
                    "Ceiling obstructions evaluated (17.6.3.4.4)",
                    "Beam interference considered (17.6.3.4.5)",
                    "Smooth vs suspended ceiling factors applied",
                ],
                "nec_article_760": [
                    "FPLR cable used for power-limited circuits",
                    "Cable markings verified (760.3)",
                    "Support requirements met (760.24)",
                    "Bending radius observed (760.24)",
                    "Cable tray installations per 760.26",
                ],
                "ada_accessibility": [
                    "Sleeping rooms have visual appliances (ADA 4.28.3)",
                    "Visual appliances within field of view (ADA 4.28.5)",
                    "Candela requirements met (UL 1638)",
                    "Flash rate 1-2 Hz (ADA 4.28.6)",
                    "Sound level 15dB above ambient (NFPA 72 18.4.2)",
                ],
            },
            "troubleshooting_guide": {
                "spacing_coverage_issues": {
                    "detector_spacing_exceeds_limits": {
                        "problem": "Large open office area with 35-foot spacing",
                        "solution": "Add intermediate detectors or use beam detection",
                        "code_reference": "NFPA 72 Table 17.6.3.4.1 allows beam detectors for large areas",
                    },
                    "ceiling_obstructions": {
                        "problem": "HVAC ducts and lighting fixtures blocking coverage",
                        "solution": "Calculate per NFPA 72 17.6.3.4.4 obstruction rules",
                        "alternative": "Use beam detectors or relocate obstructions",
                    },
                },
                "power_supply_issues": {
                    "battery_calculations_inadequate": {
                        "problem": "Calculated capacity below NFPA 72 minimum",
                        "solution": "Review device counts, check for redundant devices",
                        "action": "Add secondary battery or use larger capacity batteries",
                    },
                    "voltage_drop_exceeds_limits": {
                        "problem": "Long cable runs causing >10% voltage drop",
                        "solution": "Increase conductor size or add booster power supplies",
                        "calculation": "Calculate using NEC Chapter 9 Table 8",
                    },
                },
                "ahj_review_responses": {
                    "spacing_justification_required": {
                        "response": "Provide detailed calculations showing equivalent coverage",
                        "reference": "NFPA 72 17.6.3.4.6 engineering analysis",
                        "include": "Ceiling height adjustments and obstruction analysis",
                    },
                    "battery_calculations_incomplete": {
                        "response": "Provide complete load analysis per NFPA 72 Chapter 12",
                        "include": "All devices, communication modules, and network devices",
                        "show": "25% safety factor calculations",
                    },
                },
            },
            "assessment_framework": {
                "knowledge_tests": {
                    "beginner": [
                        "Code identification",
                        "Basic calculations",
                        "Component recognition",
                    ],
                    "intermediate": ["System design", "Code application", "Power calculations"],
                    "advanced": ["Complex integration", "AHJ coordination", "Troubleshooting"],
                },
                "performance_metrics": {
                    "accuracy_standards": {
                        "code_reference_accuracy": 0.95,  # 95%
                        "calculation_accuracy": 1.0,  # 100%
                        "design_compliance": 0.9,  # 90%
                        "ahj_response_quality": 0.85,  # 85%
                    },
                    "response_times": {
                        "basic_queries": 30,  # seconds
                        "design_calculations": 120,  # seconds
                        "complex_design": 600,  # seconds
                        "code_research": 60,  # seconds
                    },
                },
                "certification_levels": {
                    "level_1": "Fire Alarm Design Assistant - Basic code knowledge and calculations",
                    "level_2": "Fire Alarm Design Specialist - Complex system design and AHJ coordination",
                    "level_3": "Fire Alarm Design Expert - Advanced special hazard applications",
                },
            },
            "core_responsibilities": {
                "fire_alarm_systems": {
                    "components": [
                        "Initiating Devices",
                        "Notification Appliances",
                        "Control Panels",
                        "Power Supplies",
                    ],
                    "design_considerations": {
                        "coverage_requirements": "NFPA 72 spacing: smoke detectors max 900 sq ft, heat detectors max 2500 sq ft",
                        "circuit_design": "Power-limited vs non-power-limited circuits",
                        "zoning": "Proper alarm zoning for occupant evacuation",
                        "audibility": "15 dB above ambient noise per NFPA 72",
                    },
                },
                "emergency_communications": {
                    "systems": ["Voice Evacuation", "Mass Notification", "Two-way Communication"],
                    "standards": ["NFPA 72", "UL 864", "ADA Compliance"],
                },
                "security_integration": {
                    "components": ["Access Control", "Video Surveillance", "Intrusion Detection"],
                    "integration_points": ["Door Hardware", "Intercom Systems"],
                },
                "building_automation": {
                    "systems": ["HVAC Control", "Lighting Control", "Energy Management"],
                    "protocols": ["BACnet", "Modbus", "LonWorks"],
                },
            },
            "design_process": {
                "phase_1_site_assessment": [
                    "Building Analysis",
                    "Code Research",
                    "Stakeholder Interviews",
                    "System Requirements",
                ],
                "phase_2_conceptual_design": [
                    "System Architecture",
                    "Equipment Selection",
                    "Cable Pathways",
                    "Power Requirements",
                ],
                "phase_3_detailed_design": [
                    "Circuit Diagrams",
                    "Device Layouts",
                    "Cable Schedules",
                    "Sequence of Operations",
                ],
                "phase_4_specification": [
                    "Technical Specifications",
                    "Bid Documents",
                    "Vendor Coordination",
                    "Cost Estimation",
                ],
                "phase_5_construction_support": [
                    "Shop Drawing Review",
                    "Field Inspections",
                    "Commissioning",
                    "Training",
                ],
            },
            "critical_calculations": {
                "detector_spacing": {
                    "smoke_max_area": 900,  # sq ft
                    "heat_max_area": 2500,  # sq ft
                    "ceiling_height_adjustments": {
                        "under_10ft": 30,  # feet spacing
                        "10_14ft": 25,
                        "over_14ft": 20,
                    },
                },
                "circuit_loading": {
                    "max_devices_slc": 159,  # Signaling Line Circuit
                    "standby_current_per_device": 0.0003,  # amps
                    "alarm_current_per_device": 0.002,  # amps
                    "battery_safety_factor": 1.25,
                },
                "cable_voltage_drop": {
                    "copper_resistivity": 12.9,  # ohm-circular mils per foot at 75°C
                    "round_trip_multiplier": 2,
                },
            },
            "equipment_criteria": {
                "control_panels": {
                    "capacity_factors": ["Device Count", "Zones", "Circuits"],
                    "features": ["Network Capability", "Redundant Power"],
                    "approvals": ["UL Listing", "FM Approval", "CSFM Listing"],
                },
                "initiating_devices": {
                    "smoke_detectors": ["Ionization", "Photoelectric", "Combination"],
                    "heat_detectors": ["Fixed Temperature", "Rate-of-Rise"],
                    "ratings": ["135°F", "155°F", "190°F", "220°F"],
                },
                "notification_appliances": {
                    "audible": {"db_range": "75-110 dB", "patterns": ["Temporal", "Continuous"]},
                    "visual": {"candela_range": "15-177 cd", "ada_compliance": True},
                },
            },
            "code_compliance": {
                "primary_standards": {
                    "nfpa_72": "National Fire Alarm and Signaling Code",
                    "nfpa_70": "National Electrical Code (NEC)",
                    "nfpa_101": "Life Safety Code",
                    "ibc_ifc": "International Building Codes",
                },
                "industry_standards": {
                    "ul_864": "Control Units for Fire Alarm Systems",
                    "ul_1971": "Signaling Devices for Hearing Impaired",
                    "ada": "Americans with Disabilities Act",
                },
            },
            "career_development": {
                "entry_level": ["CAD Drafter", "Field Technician", "Design Assistant"],
                "mid_level": ["Project Designer", "System Programmer", "Code Specialist"],
                "senior_level": ["Senior Designer", "Technical Specialist", "Project Manager"],
                "certifications": ["NICET", "CTS", "RCDD", "CPP"],
            },
        }

    def _load_fire_protection_knowledge(self) -> dict[str, Any]:
        """Load fire protection system knowledge."""
        return {
            "system_types": {
                "fire_alarm": "Detection and notification systems",
                "sprinkler": "Automatic fire suppression",
                "standpipe": "Manual firefighting access",
                "fire_pump": "Water pressure maintenance",
            },
            "detection_methods": {
                "smoke": "Particulate matter detection",
                "heat": "Temperature rise detection",
                "flame": "Radiation detection",
                "gas": "Toxic gas detection",
            },
            "notification_methods": {
                "audible": "Sound-based alerts",
                "visual": "Light-based alerts",
                "tactile": "Vibration-based alerts",
                "voice": "Speech-based messages",
            },
        }

    def _load_building_codes(self) -> dict[str, Any]:
        """Load building code knowledge."""
        return {
            "occupancy_types": {
                "A": "Assembly (churches, restaurants)",
                "B": "Business (offices, schools)",
                "E": "Educational",
                "F": "Factory/Industrial",
                "H": "High Hazard",
                "I": "Institutional (hospitals, nursing)",
                "M": "Mercantile (stores, markets)",
                "R": "Residential",
                "S": "Storage",
            },
            "construction_types": {
                "Type_I": "Fire Resistive (concrete/steel)",
                "Type_II": "Non-Combustible",
                "Type_III": "Ordinary Construction",
                "Type_IV": "Heavy Timber",
                "Type_V": "Wood Frame",
            },
        }

    def _load_system_integration(self) -> dict[str, Any]:
        """Load system integration knowledge."""
        return {
            "protocols": {
                "bacnet": "Building Automation and Control Network",
                "modbus": "Industrial control protocol",
                "lonworks": "Local Operating Network",
                "knx": "Home and building automation",
            },
            "interfaces": {
                "dry_contacts": "Relay-based signaling",
                "analog_signals": "4-20mA, 0-10V",
                "digital_signals": "RS-485, Ethernet",
                "wireless": "Zigbee, Bluetooth, WiFi",
            },
        }

    def query_knowledge(
        self, domain: str, topic: str | None = None, subtopic: str | None = None
    ) -> dict[str, Any]:
        """
        Query knowledge base for specific information.

        Args:
            domain: Knowledge domain (e.g., 'low_voltage_design')
            topic: Specific topic within domain
            subtopic: Specific subtopic within topic

        Returns:
            Relevant knowledge information
        """
        try:
            if domain not in self.knowledge_domains:
                return {"error": f"Unknown domain: {domain}"}

            domain_data = self.knowledge_domains[domain]

            if topic is None:
                return domain_data

            if topic not in domain_data:
                return {"error": f"Unknown topic '{topic}' in domain '{domain}'"}

            topic_data = domain_data[topic]

            if subtopic is None:
                return topic_data

            if subtopic not in topic_data:
                return {"error": f"Unknown subtopic '{subtopic}' in topic '{topic}'"}

            return topic_data[subtopic]

        except Exception as e:
            logger.error(f"Knowledge query failed: {e}")
            return {"error": f"Query failed: {str(e)}"}

    def search_knowledge(self, query: str) -> list[dict[str, Any]]:
        """
        Search knowledge base for relevant information.

        Args:
            query: Search term or phrase

        Returns:
            List of relevant knowledge items
        """
        results = []
        query_lower = query.lower()

        def search_dict(data: dict[str, Any], path: list[str] = []) -> None:
            """Recursively search through nested dictionaries."""
            for key, value in data.items():
                current_path = path + [key]

                # Search in keys
                if query_lower in key.lower():
                    results.append({"path": ".".join(current_path), "key": key, "value": value})

                # Search in string values
                if isinstance(value, str) and query_lower in value.lower():
                    results.append({"path": ".".join(current_path), "key": key, "value": value})

                # Recurse into nested dicts
                elif isinstance(value, dict):
                    search_dict(value, current_path)

                # Search in lists
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, str) and query_lower in item.lower():
                            results.append(
                                {
                                    "path": ".".join(current_path + [str(i)]),
                                    "key": key,
                                    "value": item,
                                }
                            )

        for domain_name, domain_data in self.knowledge_domains.items():
            search_dict(domain_data, [domain_name])

        return results

    def get_design_guidance(
        self, system_type: str, building_info: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Get design guidance for specific system types.

        Args:
            system_type: Type of system (fire_alarm, security, etc.)
            building_info: Optional building characteristics

        Returns:
            Design guidance and recommendations
        """
        guidance = {
            "fire_alarm": {
                "detector_spacing": "30 ft max spacing for ceiling heights under 10 ft",
                "audibility": "15 dB above ambient noise",
                "zoning": "Maximum zone size based on building size",
                "power": "Battery backup for 24 hours standby + 5 min alarm",
            },
            "emergency_communication": {
                "coverage": "100% of building occupiable areas",
                "intelligibility": "Minimum 0.7 STI score",
                "languages": "Multiple language capability for diverse populations",
                "integration": "Seamless integration with fire alarm system",
            },
            "security": {
                "access_control": "Proximity cards, biometrics, or keypads",
                "video_surveillance": "Coverage of all entry points and critical areas",
                "intrusion_detection": "Perimeter protection and interior detection",
                "integration": "Unified security management platform",
            },
        }

        return guidance.get(system_type, {"error": f"No guidance available for {system_type}"})

    def infer_occupancy_from_description(self, building_description: str) -> dict[str, Any]:
        """
        Infer occupancy classification from building description.

        Uses pattern matching and contextual clues to make reasonable assumptions
        about occupancy types when not explicitly stated.

        Args:
            building_description: Description of the building (e.g., "church", "office building")

        Returns:
            Dict with inferred occupancy information and confidence level
        """
        description_lower = building_description.lower()

        # Building type to occupancy mapping with confidence levels
        inference_rules = {
            # High confidence mappings (direct matches)
            "church": {"occupancy": "A-3", "confidence": 0.95, "reason": "Churches are classified as A-3 Assembly per NFPA 101"},
            "school": {"occupancy": "E", "confidence": 0.95, "reason": "Educational facilities are E occupancy"},
            "hospital": {"occupancy": "H-1", "confidence": 0.95, "reason": "Hospitals are H-1 Healthcare occupancy"},
            "hotel": {"occupancy": "R-1", "confidence": 0.95, "reason": "Hotels/motels are R-1 Residential"},
            "apartment": {"occupancy": "R-2", "confidence": 0.95, "reason": "Apartments are R-2 Residential"},
            "office": {"occupancy": "B", "confidence": 0.90, "reason": "Office buildings are typically B Business occupancy"},
            "restaurant": {"occupancy": "A-2", "confidence": 0.90, "reason": "Restaurants are A-2 Assembly occupancy"},
            "store": {"occupancy": "M", "confidence": 0.90, "reason": "Retail stores are M Mercantile occupancy"},
            "warehouse": {"occupancy": "S-1", "confidence": 0.85, "reason": "Warehouses are typically S-1 Storage"},
            "factory": {"occupancy": "F-1", "confidence": 0.85, "reason": "Manufacturing facilities are F Factory occupancy"},

            # Medium confidence patterns
            "worship": {"occupancy": "A-3", "confidence": 0.85, "reason": "Places of worship are typically A-3 Assembly"},
            "residential": {"occupancy": "R-2", "confidence": 0.80, "reason": "Residential buildings are typically R-2"},
            "commercial": {"occupancy": "B", "confidence": 0.75, "reason": "Commercial buildings are often B Business occupancy"},
            "industrial": {"occupancy": "F-1", "confidence": 0.75, "reason": "Industrial buildings are typically F Factory occupancy"},

            # Contextual clues
            "congregation": {"occupancy": "A-3", "confidence": 0.80, "reason": "References to congregation suggest A-3 Assembly (church)"},
            "students": {"occupancy": "E", "confidence": 0.80, "reason": "Student populations suggest E Educational occupancy"},
            "patients": {"occupancy": "H-1", "confidence": 0.85, "reason": "Patient references suggest H Healthcare occupancy"},
        }

        # Check for direct matches first
        for keyword, inference in inference_rules.items():
            if keyword in description_lower:
                return {
                    "inferred_occupancy": inference["occupancy"],
                    "confidence": inference["confidence"],
                    "reason": inference["reason"],
                    "assumption_made": True,
                    "clarification_needed": inference["confidence"] < 0.90,
                }

        # If no direct match, suggest asking for clarification
        return {
            "inferred_occupancy": None,
            "confidence": 0.0,
            "reason": "Building type not clearly identifiable from description",
            "assumption_made": False,
            "clarification_needed": True,
            "suggested_questions": [
                "What type of occupancy is this building (e.g., office, residential, assembly)?",
                "What is the primary use of this building?",
                "How many people typically occupy this building?"
            ]
        }

    def get_design_assumptions(self, building_info: dict[str, Any]) -> dict[str, Any]:
        """
        Generate reasonable design assumptions based on partial building information.

        Args:
            building_info: Partial building information dictionary

        Returns:
            Dictionary with assumptions and confidence levels
        """
        assumptions: dict[str, Any] = {
            "occupancy_assumptions": {},
            "design_assumptions": {},
            "code_assumptions": {},
            "clarification_questions": []
        }

        # Occupancy inference
        if "building_type" in building_info and not building_info.get("occupancy_type"):
            occupancy_inference = self.infer_occupancy_from_description(building_info["building_type"])
            if occupancy_inference["assumption_made"]:
                assumptions["occupancy_assumptions"] = occupancy_inference
                building_info["inferred_occupancy"] = occupancy_inference["inferred_occupancy"]
            else:
                assumptions["clarification_questions"].extend(occupancy_inference["suggested_questions"])

        # Design parameter assumptions
        if not building_info.get("ceiling_height"):
            # Assume standard ceiling height based on building type
            building_type = building_info.get("building_type", "").lower()
            if any(word in building_type for word in ["warehouse", "industrial", "factory"]):
                assumptions["design_assumptions"]["ceiling_height"] = {
                    "assumed_value": 20.0,
                    "confidence": 0.7,
                    "reason": "Industrial buildings typically have higher ceilings"
                }
            else:
                assumptions["design_assumptions"]["ceiling_height"] = {
                    "assumed_value": 10.0,
                    "confidence": 0.8,
                    "reason": "Standard ceiling height for most commercial buildings"
                }

        # Code jurisdiction assumptions
        if not building_info.get("jurisdiction"):
            assumptions["code_assumptions"]["jurisdiction"] = {
                "assumed_value": "IBC 2018 + NFPA 72 2019",
                "confidence": 0.6,
                "reason": "Current widely adopted codes - verify with local AHJ",
                "note": "Local amendments may apply - confirm with Authority Having Jurisdiction"
            }

        return assumptions

    def calculate_system_requirements(
        self, building_area: float, occupancy_type: Optional[str] = None, ceiling_height: float = 10.0,
        building_description: Optional[str] = None, make_assumptions: bool = True
    ) -> dict[str, Any]:
        """
        Calculate system requirements based on building characteristics.

        Enhanced version that can make reasonable assumptions when information is incomplete.

        Args:
            building_area: Building area in square feet
            occupancy_type: Building occupancy classification (optional if building_description provided)
            ceiling_height: Average ceiling height in feet
            building_description: Description of building type for inference
            make_assumptions: Whether to make reasonable assumptions for missing data

        Returns:
            System requirements and recommendations with assumptions noted
        """
        building_info = {
            "area": building_area,
            "occupancy_type": occupancy_type,
            "ceiling_height": ceiling_height,
            "building_type": building_description
        }

        # Make assumptions if enabled and information is incomplete
        assumptions_made = {}
        if make_assumptions:
            assumptions_made = self.get_design_assumptions(building_info)

            # Apply inferred occupancy if available
            if "inferred_occupancy" in building_info:
                occupancy_type = building_info["inferred_occupancy"]
                building_info["occupancy_type"] = occupancy_type

            # Apply assumed ceiling height if needed
            if not ceiling_height and "ceiling_height" in assumptions_made.get("design_assumptions", {}):
                assumed_height = assumptions_made["design_assumptions"]["ceiling_height"]["assumed_value"]
                if isinstance(assumed_height, (int, float)):
                    ceiling_height = float(assumed_height)

        # Validate that we have enough information to proceed
        if not occupancy_type and not make_assumptions:
            return {
                "error": "Insufficient information for system calculation",
                "required_information": ["occupancy_type or building_description"],
                "suggestion": "Provide building type description or occupancy classification"
            }

        if not occupancy_type:
            return {
                "error": "Could not determine occupancy type from description",
                "building_description": building_description,
                "suggestion": "Please specify the occupancy type (A, B, E, H, R, etc.) or provide more building details"
            }

        # Proceed with calculations using available information
        # Smoke detector calculations (NFPA 72)
        smoke_detector_max_area = 900  # sq ft per detector
        estimated_smoke_detectors = max(1, int(building_area / smoke_detector_max_area))

        # Heat detector calculations (NFPA 72)
        heat_detector_max_area = 2500  # sq ft per detector
        estimated_heat_detectors = max(1, int(building_area / heat_detector_max_area))

        # Notification appliance calculations
        # Rule of thumb: 1 appliance per 3000 sq ft, minimum 1 per room/exit
        estimated_appliances = max(4, int(building_area / 3000))

        # Manual pull stations: 1 per 200 ft of exit travel, minimum 1 per exit
        estimated_pull_stations = max(2, int(building_area / 10000))

        result = {
            "building_characteristics": {
                "area_sq_ft": building_area,
                "occupancy_type": occupancy_type,
                "ceiling_height_ft": ceiling_height,
                "building_description": building_description,
            },
            "estimated_devices": {
                "smoke_detectors": estimated_smoke_detectors,
                "heat_detectors": estimated_heat_detectors,
                "notification_appliances": estimated_appliances,
                "manual_pull_stations": estimated_pull_stations,
                "total_initiating_devices": estimated_smoke_detectors
                + estimated_heat_detectors
                + estimated_pull_stations,
            },
            "system_sizing": {
                "recommended_panel_size": self._recommend_panel_size(
                    estimated_smoke_detectors + estimated_heat_detectors
                ),
                "estimated_circuit_count": self._estimate_circuits(estimated_appliances),
                "battery_capacity_ah": self._calculate_battery_capacity(
                    estimated_smoke_detectors + estimated_heat_detectors + estimated_pull_stations
                ),
            },
            "code_requirements": {
                "nfpa_72_compliance": "Automatic detection required for most occupancies",
                "audibility_requirements": "15 dB above ambient noise throughout building",
                "emergency_power": "24 hour standby + 5 minute alarm operation",
            },
        }

        # Include assumptions if any were made
        if assumptions_made:
            result["assumptions_made"] = assumptions_made

        return result

    def _recommend_panel_size(self, device_count: int) -> str:
        """Recommend appropriate fire alarm control panel size."""
        if device_count <= 50:
            return "Small Panel (up to 50 devices)"
        elif device_count <= 200:
            return "Medium Panel (51-200 devices)"
        elif device_count <= 1000:
            return "Large Panel (201-1000 devices)"
        else:
            return "Networked System (1000+ devices)"

    def _estimate_circuits(self, appliance_count: int) -> int:
        """Estimate number of notification appliance circuits."""
        # Typically 10-20 appliances per circuit
        return max(1, (appliance_count + 14) // 15)  # Ceiling division by 15

    def _calculate_battery_capacity(self, device_count: int) -> float:
        """Calculate battery capacity requirements."""
        # Simplified calculation: 24 hour standby + 5 min alarm
        standby_current = device_count * 0.0003  # 0.3mA per device
        alarm_current = device_count * 0.002  # 2mA per device

        standby_capacity = standby_current * 24  # 24 hours
        alarm_capacity = alarm_current * (5 / 60)  # 5 minutes = 5/60 hours

        total_capacity = (standby_capacity + alarm_capacity) * 1.25  # 25% safety factor

        return round(total_capacity, 2)


# Global knowledge base instance
knowledge_base = AIKnowledgeBase()


def query_ai_knowledge(
    domain: str, topic: str | None = None, subtopic: str | None = None
) -> dict[str, Any]:
    """
    Convenience function to query the AI knowledge base.

    Args:
        domain: Knowledge domain
        topic: Specific topic (optional)
        subtopic: Specific subtopic (optional)

    Returns:
        Knowledge base response
    """
    return knowledge_base.query_knowledge(domain, topic, subtopic)


def search_ai_knowledge(query: str) -> list[dict[str, Any]]:
    """
    Convenience function to search the AI knowledge base.

    Args:
        query: Search term or phrase

    Returns:
        List of relevant knowledge items
    """
    return knowledge_base.search_knowledge(query)


def get_design_guidance(
    system_type: str, building_info: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Get design guidance for specific system types.

    Args:
        system_type: Type of system
        building_info: Optional building information

    Returns:
        Design guidance
    """
    return knowledge_base.get_design_guidance(system_type, building_info)


def calculate_system_requirements(
    building_area: float, occupancy_type: str, ceiling_height: float = 10.0
) -> dict[str, Any]:
    """
    Calculate system requirements for a building.

    Args:
        building_area: Building area in square feet
        occupancy_type: Occupancy classification
        ceiling_height: Ceiling height in feet

    Returns:
        System requirements and recommendations
    """
    return knowledge_base.calculate_system_requirements(
        building_area, occupancy_type, ceiling_height
    )
