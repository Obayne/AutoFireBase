"""
AI Knowledge Base for AutoFire
==============================

Centralized knowledge repository for AI assistants and automation.
Contains domain expertise, training materials, and contextual information
for fire protection and low voltage design systems.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class AIKnowledgeBase:
    """
    Comprehensive knowledge base for AutoFire AI systems.

    Contains training materials, domain expertise, and contextual information
    for fire protection design, low voltage systems, and building automation.
    """

    def __init__(self):
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

    def calculate_system_requirements(
        self, building_area: float, occupancy_type: str, ceiling_height: float = 10.0
    ) -> dict[str, Any]:
        """
        Calculate system requirements based on building characteristics.

        Args:
            building_area: Building area in square feet
            occupancy_type: Building occupancy classification
            ceiling_height: Average ceiling height in feet

        Returns:
            System requirements and recommendations
        """
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

        return {
            "building_characteristics": {
                "area_sq_ft": building_area,
                "occupancy_type": occupancy_type,
                "ceiling_height_ft": ceiling_height,
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
