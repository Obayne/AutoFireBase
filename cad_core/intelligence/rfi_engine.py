"""
RFI Intelligence Engine
Automatically identifies and generates Request for Information materials
"""

from datetime import datetime
from typing import Any, Dict, List

from . import (
    NFPA_72_SPACING,
    ConstructionAnalysis,
    ConstructionIntelligenceBase,
    DeviceType,
    Priority,
    RFIItem,
    create_rfi_item,
)


class RFIIntelligenceEngine(ConstructionIntelligenceBase):
    """Automatically identify and generate RFI materials from construction analysis"""

    def __init__(self):
        super().__init__()
        self.nfpa_rules = self._load_nfpa_rules()

    def analyze_project_issues(self, analysis: ConstructionAnalysis) -> List[RFIItem]:
        """
        Identify all issues requiring clarification

        Args:
            analysis: Construction document analysis

        Returns:
            List of RFI items requiring attention
        """
        self.log_analysis("Starting RFI analysis")

        rfis: List[RFIItem] = []

        # Check device placement conflicts
        rfis.extend(self._check_device_conflicts(analysis))

        # Check NFPA compliance issues
        rfis.extend(self._check_nfpa_compliance(analysis))

        # Check missing specifications
        rfis.extend(self._check_missing_specs(analysis))

        # Check coordination conflicts
        rfis.extend(self._check_coordination_conflicts(analysis))

        # Check coverage gaps
        rfis.extend(self._check_coverage_gaps(analysis))

        # Check specification conflicts
        rfis.extend(self._check_specification_conflicts(analysis))

        self.log_analysis(f"RFI analysis complete: {len(rfis)} issues identified")

        return sorted(rfis, key=lambda x: (x.priority.value, x.category))

    def _check_device_conflicts(self, analysis: ConstructionAnalysis) -> List[RFIItem]:
        """Check for device placement conflicts"""
        conflicts = []

        for floor_plan in analysis.floor_plans:
            for room in floor_plan.rooms:
                # Check if fire alarm devices match architectural layout
                devices_in_room = self._get_devices_in_room(room, analysis.fire_alarm_plans)

                if not devices_in_room and self._requires_detection(room):
                    conflicts.append(
                        create_rfi_item(
                            category="Missing Detection",
                            description=f"Room '{room.name}' requires fire detection but none shown on fire alarm plans",
                            priority="high",
                            reference_drawing=floor_plan.sheet_number,
                            location=room.name,
                            suggested_resolution="Add appropriate smoke or heat detector per NFPA 72 requirements",
                        )
                    )

                # Check for over-detection
                smoke_detectors = [
                    d for d in devices_in_room if d.device_type == DeviceType.SMOKE_DETECTOR
                ]
                if (
                    len(smoke_detectors) > 1 and room.area < 400
                ):  # Small room with multiple detectors
                    conflicts.append(
                        create_rfi_item(
                            category="Possible Over-Detection",
                            description=f"Room '{room.name}' ({room.area:.0f} sq ft) has {len(smoke_detectors)} smoke detectors",
                            priority="medium",
                            reference_drawing=floor_plan.sheet_number,
                            location=room.name,
                            suggested_resolution="Verify detector count meets design intent without over-coverage",
                        )
                    )

        return conflicts

    def _check_nfpa_compliance(self, analysis: ConstructionAnalysis) -> List[RFIItem]:
        """Check for NFPA 72 compliance issues"""
        compliance_issues = []

        for fa_plan in analysis.fire_alarm_plans:
            # Check detector spacing
            smoke_detectors = [
                d for d in fa_plan.devices if d.device_type == DeviceType.SMOKE_DETECTOR
            ]

            for i, detector in enumerate(smoke_detectors):
                # Check spacing to nearby detectors
                nearby_detectors = [
                    d
                    for j, d in enumerate(smoke_detectors)
                    if j != i
                    and self._calculate_distance(detector.location, d.location)
                    < NFPA_72_SPACING[DeviceType.SMOKE_DETECTOR]
                ]

                if len(nearby_detectors) == 0 and i > 0:  # Isolated detector
                    compliance_issues.append(
                        create_rfi_item(
                            category="NFPA Spacing Violation",
                            description=f"Smoke detector at {detector.location} may exceed 30-foot spacing requirement",
                            priority="high",
                            reference_drawing=fa_plan.sheet_number,
                            suggested_resolution="Verify spacing meets NFPA 72 Section 17.7.3.2.3.1",
                        )
                    )

            # Check pull station coverage
            pull_stations = [d for d in fa_plan.devices if d.device_type == DeviceType.PULL_STATION]
            if not pull_stations:
                compliance_issues.append(
                    create_rfi_item(
                        category="Missing Pull Stations",
                        description="No manual pull stations found on fire alarm plan",
                        priority="critical",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Add pull stations at exits per NFPA 72 Section 17.14",
                    )
                )

            # Check notification appliance coverage
            notification_devices = [
                d
                for d in fa_plan.devices
                if d.device_type in [DeviceType.HORN_STROBE, DeviceType.SPEAKER]
            ]
            if not notification_devices:
                compliance_issues.append(
                    create_rfi_item(
                        category="Missing Notification",
                        description="No notification appliances found on fire alarm plan",
                        priority="critical",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Add notification appliances per NFPA 72 Chapter 18",
                    )
                )

        return compliance_issues

    def _check_missing_specs(self, analysis: ConstructionAnalysis) -> List[RFIItem]:
        """Check for missing specifications"""
        missing_specs = []

        # Check for device models
        for fa_plan in analysis.fire_alarm_plans:
            devices_without_models = [d for d in fa_plan.devices if not d.model]

            if devices_without_models:
                device_types = set(d.device_type.value for d in devices_without_models)
                missing_specs.append(
                    create_rfi_item(
                        category="Missing Device Models",
                        description=f"Device models not specified for: {', '.join(device_types)}",
                        priority="medium",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Provide specific device models and part numbers",
                    )
                )

            # Check for missing circuit information
            devices_without_circuits = [d for d in fa_plan.devices if not d.circuit]
            if (
                devices_without_circuits and len(fa_plan.devices) > 5
            ):  # Only flag for larger systems
                missing_specs.append(
                    create_rfi_item(
                        category="Missing Circuit Information",
                        description=f"{len(devices_without_circuits)} devices without circuit assignments",
                        priority="medium",
                        reference_drawing=fa_plan.sheet_number,
                        suggested_resolution="Provide SLC/NAC circuit assignments for all devices",
                    )
                )

        # Check for missing schedules
        if not analysis.schedules:
            missing_specs.append(
                create_rfi_item(
                    category="Missing Device Schedule",
                    description="No device schedules found in construction documents",
                    priority="high",
                    reference_drawing="General",
                    suggested_resolution="Provide device schedule with models, quantities, and specifications",
                )
            )

        return missing_specs

    def _check_coordination_conflicts(self, analysis: ConstructionAnalysis) -> List[RFIItem]:
        """Check for coordination conflicts between trades"""
        conflicts = []

        # Check architectural vs fire alarm plan consistency
        if analysis.floor_plans and analysis.fire_alarm_plans:
            arch_rooms: set[str] = set()
            for floor_plan in analysis.floor_plans:
                arch_rooms.update(room.name for room in floor_plan.rooms)

            fa_rooms: set[str] = set()
            for fa_plan in analysis.fire_alarm_plans:
                fa_rooms.update(device.room for device in fa_plan.devices if device.room)

            # Rooms on architectural plans but not fire alarm plans
            missing_fa_rooms = arch_rooms - fa_rooms
            if missing_fa_rooms:
                conflicts.append(
                    create_rfi_item(
                        category="Room Coordination",
                        description=f"Rooms on architectural plans not addressed in fire alarm design: {', '.join(missing_fa_rooms)}",
                        priority="medium",
                        reference_drawing="Cross-reference",
                        suggested_resolution="Verify fire alarm coverage for all architectural spaces",
                    )
                )

        return conflicts

    def _check_coverage_gaps(self, analysis: ConstructionAnalysis) -> List[RFIItem]:
        """Check for coverage gaps in fire alarm design"""
        gaps = []

        for floor_plan in analysis.floor_plans:
            total_area = sum(room.area for room in floor_plan.rooms)

            if total_area > 0:
                # Estimate required detectors based on area
                required_detectors = int(total_area / 900)  # ~900 sq ft per detector typical

                # Count actual detectors in corresponding fire alarm plans
                actual_detectors = 0
                for fa_plan in analysis.fire_alarm_plans:
                    detection_devices = [
                        d
                        for d in fa_plan.devices
                        if d.device_type in [DeviceType.SMOKE_DETECTOR, DeviceType.HEAT_DETECTOR]
                    ]
                    actual_detectors += len(detection_devices)

                if actual_detectors < required_detectors * 0.7:  # Less than 70% of estimated
                    gaps.append(
                        create_rfi_item(
                            category="Insufficient Coverage",
                            description=f"Building area {total_area:.0f} sq ft may require more detection devices (estimated {required_detectors}, shown {actual_detectors})",
                            priority="medium",
                            reference_drawing=floor_plan.sheet_number,
                            suggested_resolution="Verify detection coverage meets NFPA 72 spacing requirements",
                        )
                    )

        return gaps

    def _check_specification_conflicts(self, analysis: ConstructionAnalysis) -> List[RFIItem]:
        """Check for conflicts in specifications"""
        conflicts = []

        # Check for conflicting manufacturer specifications
        manufacturers = set()
        for spec in analysis.specifications:
            if isinstance(spec, dict) and "manufacturer_specs" in spec:
                for mfg_spec in spec["manufacturer_specs"]:
                    mfg = mfg_spec.split()[0].lower()  # First word is usually manufacturer
                    manufacturers.add(mfg)

        if len(manufacturers) > 1:
            conflicts.append(
                create_rfi_item(
                    category="Mixed Manufacturers",
                    description=f"Multiple manufacturers specified: {', '.join(manufacturers)}",
                    priority="medium",
                    reference_drawing="Specifications",
                    suggested_resolution="Clarify if mixed manufacturer system is acceptable or standardize on single manufacturer",
                )
            )

        return conflicts

    def _get_devices_in_room(self, room, fire_alarm_plans) -> List:
        """Get fire alarm devices located in a specific room"""
        devices = []
        for fa_plan in fire_alarm_plans:
            for device in fa_plan.devices:
                if device.room and device.room.lower() == room.name.lower():
                    devices.append(device)
        return devices

    def _requires_detection(self, room) -> bool:
        """Determine if a room requires fire detection"""
        # Rooms that typically require detection
        detection_required = [
            "office",
            "conference",
            "meeting",
            "storage",
            "lobby",
            "corridor",
            "hallway",
            "break",
            "kitchen",
            "computer",
        ]

        room_name_lower = room.name.lower()
        return any(req_type in room_name_lower for req_type in detection_required)

    def _calculate_distance(self, point1: tuple, point2: tuple) -> float:
        """Calculate distance between two points"""
        return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

    def _load_nfpa_rules(self) -> Dict[str, Any]:
        """Load NFPA 72 rules for automated checking"""
        return {
            "smoke_detector_spacing": 30.0,  # feet
            "heat_detector_spacing": 50.0,  # feet
            "pull_station_travel": 200.0,  # feet maximum travel distance
            "notification_spacing": 100.0,  # feet maximum spacing
            "corridor_spacing": 30.0,  # feet in corridors
        }

    def generate_rfi_document(
        self, rfis: List[RFIItem], project_name: str = "Unknown Project"
    ) -> Dict[str, Any]:
        """
        Generate formal RFI document

        Args:
            rfis: List of RFI items
            project_name: Project name for document header

        Returns:
            Dictionary containing formatted RFI document
        """
        # Categorize RFIs by priority
        critical_rfis = [rfi for rfi in rfis if rfi.priority == Priority.CRITICAL]
        high_rfis = [rfi for rfi in rfis if rfi.priority == Priority.HIGH]
        medium_rfis = [rfi for rfi in rfis if rfi.priority == Priority.MEDIUM]
        low_rfis = [rfi for rfi in rfis if rfi.priority == Priority.LOW]

        # Categorize by type
        categories: Dict[str, List[RFIItem]] = {}
        for rfi in rfis:
            if rfi.category not in categories:
                categories[rfi.category] = []
            categories[rfi.category].append(rfi)

        return {
            "project_name": project_name,
            "generated_date": datetime.now().isoformat(),
            "total_issues": len(rfis),
            "priority_summary": {
                "critical": len(critical_rfis),
                "high": len(high_rfis),
                "medium": len(medium_rfis),
                "low": len(low_rfis),
            },
            "categories": {cat: len(items) for cat, items in categories.items()},
            "rfis": [rfi.to_dict() for rfi in rfis],
            "recommendations": self._generate_rfi_recommendations(rfis),
        }

    def _generate_rfi_recommendations(self, rfis: List[RFIItem]) -> List[str]:
        """Generate high-level recommendations based on RFI analysis"""
        recommendations = []

        critical_count = len([rfi for rfi in rfis if rfi.priority == Priority.CRITICAL])
        if critical_count > 0:
            recommendations.append(
                f"Address {critical_count} critical issues before proceeding with construction"
            )

        missing_detection = len([rfi for rfi in rfis if "Missing Detection" in rfi.category])
        if missing_detection > 0:
            recommendations.append("Review fire alarm coverage in all occupied spaces")

        nfpa_issues = len([rfi for rfi in rfis if "NFPA" in rfi.category])
        if nfpa_issues > 0:
            recommendations.append("Verify all designs meet current NFPA 72 requirements")

        spec_issues = len([rfi for rfi in rfis if "specification" in rfi.category.lower()])
        if spec_issues > 0:
            recommendations.append("Complete device specifications and schedules")

        if len(rfis) > 10:
            recommendations.append("Consider design review meeting to address multiple issues")

        return recommendations

    def export_rfi_report(
        self, rfis: List[RFIItem], output_path: str, project_name: str = "Unknown Project"
    ):
        """Export RFI report to text file"""
        rfi_doc = self.generate_rfi_document(rfis, project_name)

        with open(output_path, "w") as f:
            f.write("# REQUEST FOR INFORMATION (RFI)\n\n")
            f.write(f"**Project:** {rfi_doc['project_name']}\n")
            f.write(f"**Generated:** {rfi_doc['generated_date']}\n")
            f.write(f"**Total Issues:** {rfi_doc['total_issues']}\n\n")

            f.write("## Priority Summary\n")
            f.write(f"- Critical: {rfi_doc['priority_summary']['critical']}\n")
            f.write(f"- High: {rfi_doc['priority_summary']['high']}\n")
            f.write(f"- Medium: {rfi_doc['priority_summary']['medium']}\n")
            f.write(f"- Low: {rfi_doc['priority_summary']['low']}\n\n")

            f.write("## Issues by Category\n")
            for category, count in rfi_doc["categories"].items():
                f.write(f"- {category}: {count}\n")
            f.write("\n")

            f.write("## Detailed Issues\n\n")
            for i, rfi_dict in enumerate(rfi_doc["rfis"], 1):
                f.write(f"### {i}. {rfi_dict['category']} ({rfi_dict['priority'].upper()})\n")
                f.write(f"**Description:** {rfi_dict['description']}\n")
                f.write(f"**Reference:** {rfi_dict['reference_drawing']}\n")
                if rfi_dict["location"]:
                    f.write(f"**Location:** {rfi_dict['location']}\n")
                if rfi_dict["suggested_resolution"]:
                    f.write(f"**Suggested Resolution:** {rfi_dict['suggested_resolution']}\n")
                f.write("\n")

            f.write("## Recommendations\n")
            for rec in rfi_doc["recommendations"]:
                f.write(f"- {rec}\n")


# Factory function for easy usage
def analyze_project_rfis(analysis: ConstructionAnalysis) -> List[RFIItem]:
    """
    Convenient function to analyze project and generate RFIs

    Args:
        analysis: Construction document analysis

    Returns:
        List of RFI items
    """
    engine = RFIIntelligenceEngine()
    return engine.analyze_project_issues(analysis)
