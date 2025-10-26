"""
AutoFire AI System Recommendations Engine
Intelligent suggestions for panels, expansion boards, wire gauges, and system architecture

This module provides AI-powered recommendations that analyze project requirements
and suggest optimal fire alarm system components and configurations.
"""

import logging
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class BuildingType(Enum):
    """Building occupancy classifications."""
    OFFICE = "office"
    RETAIL = "retail" 
    INDUSTRIAL = "industrial"
    HEALTHCARE = "healthcare"
    EDUCATIONAL = "educational"
    RESIDENTIAL = "residential"
    ASSEMBLY = "assembly"
    MIXED_USE = "mixed_use"


class SystemComplexity(Enum):
    """Fire alarm system complexity levels."""
    SIMPLE = "simple"          # Basic detection and notification
    MODERATE = "moderate"      # Multiple zones, some automation
    COMPLEX = "complex"        # Extensive automation, integration
    ENTERPRISE = "enterprise"  # Multi-building, advanced features


@dataclass
class ProjectRequirements:
    """Project requirements for system recommendation analysis."""
    building_type: BuildingType
    total_area_sqft: float
    floor_count: int
    occupant_load: int
    special_hazards: List[str] = field(default_factory=list)
    code_requirements: List[str] = field(default_factory=list)
    budget_range: Tuple[float, float] = (0.0, 0.0)  # Min, Max
    timeline_weeks: int = 12
    integration_requirements: List[str] = field(default_factory=list)
    accessibility_required: bool = True
    
    @property
    def complexity_score(self) -> float:
        """Calculate project complexity score (0.0 to 1.0)."""
        score = 0.0
        
        # Base score from building type
        type_scores = {
            BuildingType.RESIDENTIAL: 0.2,
            BuildingType.OFFICE: 0.3,
            BuildingType.RETAIL: 0.4,
            BuildingType.EDUCATIONAL: 0.6,
            BuildingType.HEALTHCARE: 0.8,
            BuildingType.INDUSTRIAL: 0.7,
            BuildingType.ASSEMBLY: 0.5,
            BuildingType.MIXED_USE: 0.6
        }
        score += type_scores.get(self.building_type, 0.3)
        
        # Area factor
        if self.total_area_sqft > 100000:
            score += 0.2
        elif self.total_area_sqft > 50000:
            score += 0.1
        
        # Floor count factor
        if self.floor_count > 5:
            score += 0.1
        
        # Special hazards
        score += len(self.special_hazards) * 0.05
        
        # Integration requirements
        score += len(self.integration_requirements) * 0.03
        
        return min(score, 1.0)


@dataclass
class PanelRecommendation:
    """Fire alarm panel recommendation with justification."""
    manufacturer: str
    model: str
    capacity_zones: int
    capacity_devices: int
    expansion_slots: int
    estimated_cost: float
    confidence_score: float
    reasoning: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)


@dataclass
class ExpansionRecommendation:
    """Expansion board recommendation."""
    board_type: str
    quantity: int
    purpose: str
    estimated_cost: float
    priority: str  # "essential", "recommended", "optional"


@dataclass
class WireRecommendation:
    """Wire gauge and type recommendations."""
    circuit_type: str
    wire_type: str
    gauge: str
    estimated_footage: int
    cost_per_foot: float
    total_cost: float
    reasoning: str


@dataclass
class SystemRecommendation:
    """Complete system recommendation package."""
    project_id: str
    panel_recommendations: List[PanelRecommendation]
    expansion_recommendations: List[ExpansionRecommendation]
    wire_recommendations: List[WireRecommendation]
    total_estimated_cost: float
    complexity_level: SystemComplexity
    implementation_phases: List[Dict[str, Any]]
    risk_factors: List[str]
    success_factors: List[str]
    timeline_estimate_weeks: int
    confidence_score: float


class AISystemRecommendationEngine:
    """AI-powered system recommendation engine."""
    
    # Panel database with specifications
    PANEL_DATABASE = {
        "simple": [
            {
                "manufacturer": "System Sensor",
                "model": "i3 Series",
                "capacity_zones": 8,
                "capacity_devices": 159,
                "expansion_slots": 2,
                "base_cost": 1200,
                "features": ["Basic detection", "Manual control", "LED indicators"],
                "best_for": ["Small office", "Retail", "Simple residential"]
            }
        ],
        "moderate": [
            {
                "manufacturer": "Honeywell",
                "model": "NOTIFIER NFS2-3030",
                "capacity_zones": 30,
                "capacity_devices": 636,
                "expansion_slots": 8,
                "base_cost": 3500,
                "features": ["Graphic display", "Network capable", "Voice evacuation"],
                "best_for": ["Office buildings", "Schools", "Healthcare"]
            },
            {
                "manufacturer": "Siemens",
                "model": "Cerberus PRO FC722",
                "capacity_zones": 32,
                "capacity_devices": 504,
                "expansion_slots": 10,
                "base_cost": 4200,
                "features": ["Advanced graphics", "Building automation", "IP networking"],
                "best_for": ["Complex buildings", "Industrial", "High-tech facilities"]
            }
        ],
        "complex": [
            {
                "manufacturer": "Edwards",
                "model": "EST3X",
                "capacity_zones": 99,
                "capacity_devices": 1980,
                "expansion_slots": 20,
                "base_cost": 8500,
                "features": ["Distributed intelligence", "Advanced integration", "Redundancy"],
                "best_for": ["Hospitals", "Universities", "Large complexes"]
            }
        ]
    }
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.recommendation_history: List[SystemRecommendation] = []
    
    def recommend_system(self, requirements: ProjectRequirements) -> SystemRecommendation:
        """
        Generate comprehensive system recommendations based on project requirements.
        
        Args:
            requirements: Project requirements and constraints
            
        Returns:
            Complete system recommendation with panels, expansion, and wiring
        """
        self.logger.info(f"Generating recommendations for {requirements.building_type.value} project")
        
        # Determine system complexity
        complexity = self._determine_system_complexity(requirements)
        
        # Generate panel recommendations
        panel_recs = self._recommend_panels(requirements, complexity)
        
        # Generate expansion recommendations
        expansion_recs = self._recommend_expansions(requirements, panel_recs[0] if panel_recs else None)
        
        # Generate wire recommendations
        wire_recs = self._recommend_wiring(requirements)
        
        # Calculate total cost
        total_cost = self._calculate_total_cost(panel_recs, expansion_recs, wire_recs)
        
        # Generate implementation plan
        implementation_phases = self._create_implementation_plan(requirements, complexity)
        
        # Assess risks and success factors
        risk_factors = self._assess_risk_factors(requirements, complexity)
        success_factors = self._identify_success_factors(requirements, complexity)
        
        # Estimate timeline
        timeline = self._estimate_timeline(requirements, complexity)
        
        # Calculate overall confidence
        confidence = self._calculate_confidence_score(requirements, panel_recs, total_cost)
        
        recommendation = SystemRecommendation(
            project_id=f"PROJ_{hash(str(requirements)) % 10000:04d}",
            panel_recommendations=panel_recs,
            expansion_recommendations=expansion_recs,
            wire_recommendations=wire_recs,
            total_estimated_cost=total_cost,
            complexity_level=complexity,
            implementation_phases=implementation_phases,
            risk_factors=risk_factors,
            success_factors=success_factors,
            timeline_estimate_weeks=timeline,
            confidence_score=confidence
        )
        
        # Store in history for learning
        self.recommendation_history.append(recommendation)
        
        return recommendation
    
    def _determine_system_complexity(self, requirements: ProjectRequirements) -> SystemComplexity:
        """Determine appropriate system complexity level."""
        complexity_score = requirements.complexity_score
        
        if complexity_score < 0.3:
            return SystemComplexity.SIMPLE
        elif complexity_score < 0.6:
            return SystemComplexity.MODERATE
        elif complexity_score < 0.8:
            return SystemComplexity.COMPLEX
        else:
            return SystemComplexity.ENTERPRISE
    
    def _recommend_panels(
        self, 
        requirements: ProjectRequirements, 
        complexity: SystemComplexity
    ) -> List[PanelRecommendation]:
        """Recommend appropriate fire alarm panels."""
        recommendations = []
        
        # Estimate device count
        estimated_devices = self._estimate_device_count(requirements)
        
        # Select appropriate panel category
        if complexity == SystemComplexity.SIMPLE:
            panel_category = "simple"
        elif complexity == SystemComplexity.MODERATE:
            panel_category = "moderate"
        else:
            panel_category = "complex"
        
        # Get panels from database
        panel_options = self.PANEL_DATABASE.get(panel_category, [])
        
        for panel_data in panel_options:
            # Check if panel meets capacity requirements
            if panel_data["capacity_devices"] >= estimated_devices:
                confidence = self._calculate_panel_confidence(panel_data, requirements)
                
                reasoning = self._generate_panel_reasoning(panel_data, requirements, estimated_devices)
                
                recommendation = PanelRecommendation(
                    manufacturer=panel_data["manufacturer"],
                    model=panel_data["model"],
                    capacity_zones=panel_data["capacity_zones"],
                    capacity_devices=panel_data["capacity_devices"],
                    expansion_slots=panel_data["expansion_slots"],
                    estimated_cost=panel_data["base_cost"],
                    confidence_score=confidence,
                    reasoning=reasoning,
                    features=panel_data["features"].copy(),
                    pros=self._generate_panel_pros(panel_data, requirements),
                    cons=self._generate_panel_cons(panel_data, requirements)
                )
                
                recommendations.append(recommendation)
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _estimate_device_count(self, requirements: ProjectRequirements) -> int:
        """Estimate total device count based on project requirements."""
        base_devices_per_1000sqft = {
            BuildingType.OFFICE: 8,
            BuildingType.RETAIL: 6,
            BuildingType.INDUSTRIAL: 4,
            BuildingType.HEALTHCARE: 12,
            BuildingType.EDUCATIONAL: 10,
            BuildingType.RESIDENTIAL: 5,
            BuildingType.ASSEMBLY: 7,
            BuildingType.MIXED_USE: 8
        }
        
        base_density = base_devices_per_1000sqft.get(requirements.building_type, 8)
        estimated_devices = int((requirements.total_area_sqft / 1000.0) * base_density)
        
        # Add devices for special hazards
        estimated_devices += len(requirements.special_hazards) * 3
        
        # Add notification devices (roughly 30% of detection devices)
        estimated_devices = int(estimated_devices * 1.3)
        
        return max(estimated_devices, 20)  # Minimum 20 devices
    
    def _calculate_panel_confidence(
        self, 
        panel_data: Dict[str, Any], 
        requirements: ProjectRequirements
    ) -> float:
        """Calculate confidence score for panel recommendation."""
        confidence = 0.7  # Base confidence
        
        # Capacity utilization (sweet spot is 60-80%)
        estimated_devices = self._estimate_device_count(requirements)
        utilization = estimated_devices / panel_data["capacity_devices"]
        
        if 0.6 <= utilization <= 0.8:
            confidence += 0.2
        elif 0.4 <= utilization <= 0.9:
            confidence += 0.1
        elif utilization > 0.9:
            confidence -= 0.2
        
        # Building type match
        building_match = any(
            requirements.building_type.value.lower() in best_for.lower()
            for best_for in panel_data.get("best_for", [])
        )
        if building_match:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_panel_reasoning(
        self, 
        panel_data: Dict[str, Any], 
        requirements: ProjectRequirements, 
        estimated_devices: int
    ) -> List[str]:
        """Generate reasoning for panel recommendation."""
        reasoning = []
        
        utilization = estimated_devices / panel_data["capacity_devices"]
        reasoning.append(f"Capacity utilization: {utilization:.1%} ({estimated_devices}/{panel_data['capacity_devices']} devices)")
        
        if requirements.building_type.value in [bf.lower() for bf in panel_data.get("best_for", [])]:
            reasoning.append(f"Optimized for {requirements.building_type.value} buildings")
        
        if panel_data["expansion_slots"] >= 4:
            reasoning.append("Excellent expansion capability for future growth")
        
        return reasoning
    
    def _generate_panel_pros(
        self, 
        panel_data: Dict[str, Any], 
        requirements: ProjectRequirements
    ) -> List[str]:
        """Generate pros for panel recommendation."""
        pros = []
        
        if panel_data["capacity_devices"] > 500:
            pros.append("High device capacity")
        
        if panel_data["expansion_slots"] >= 6:
            pros.append("Excellent expandability")
        
        if "Network capable" in panel_data.get("features", []):
            pros.append("Network integration ready")
        
        if panel_data["base_cost"] < 3000:
            pros.append("Cost effective solution")
        
        return pros
    
    def _generate_panel_cons(
        self, 
        panel_data: Dict[str, Any], 
        requirements: ProjectRequirements
    ) -> List[str]:
        """Generate cons for panel recommendation."""
        cons = []
        
        if panel_data["base_cost"] > 7000:
            cons.append("Higher initial investment")
        
        estimated_devices = self._estimate_device_count(requirements)
        utilization = estimated_devices / panel_data["capacity_devices"]
        
        if utilization < 0.3:
            cons.append("May be oversized for current needs")
        elif utilization > 0.9:
            cons.append("Limited room for expansion")
        
        return cons
    
    def _recommend_expansions(
        self, 
        requirements: ProjectRequirements, 
        primary_panel: Optional[PanelRecommendation]
    ) -> List[ExpansionRecommendation]:
        """Recommend expansion boards and modules."""
        expansions = []
        
        if not primary_panel:
            return expansions
        
        # Voice evacuation for larger buildings
        if requirements.total_area_sqft > 10000:
            expansions.append(ExpansionRecommendation(
                board_type="Voice Evacuation Module",
                quantity=1,
                purpose="Mass notification and voice evacuation",
                estimated_cost=2500,
                priority="recommended"
            ))
        
        # Network interface for complex buildings
        if requirements.complexity_score > 0.6:
            expansions.append(ExpansionRecommendation(
                board_type="Network Interface Module",
                quantity=1,
                purpose="Building automation integration",
                estimated_cost=1200,
                priority="recommended"
            ))
        
        # Additional SLC loops for large systems
        estimated_devices = self._estimate_device_count(requirements)
        if estimated_devices > 300:
            additional_loops = math.ceil((estimated_devices - 300) / 200)
            expansions.append(ExpansionRecommendation(
                board_type="SLC Expansion Loop",
                quantity=additional_loops,
                purpose="Additional device capacity",
                estimated_cost=800 * additional_loops,
                priority="essential"
            ))
        
        return expansions
    
    def _recommend_wiring(self, requirements: ProjectRequirements) -> List[WireRecommendation]:
        """Recommend wire types and quantities."""
        recommendations = []
        
        # Estimate wire footage based on building size
        estimated_slc_footage = int(requirements.total_area_sqft * 0.15)  # 0.15 ft per sq ft
        estimated_nac_footage = int(requirements.total_area_sqft * 0.08)  # 0.08 ft per sq ft
        estimated_power_footage = int(requirements.total_area_sqft * 0.05)  # 0.05 ft per sq ft
        
        # SLC wiring
        recommendations.append(WireRecommendation(
            circuit_type="SLC",
            wire_type="FPLR",
            gauge="14 AWG",
            estimated_footage=estimated_slc_footage,
            cost_per_foot=1.25,
            total_cost=estimated_slc_footage * 1.25,
            reasoning="Fire power limited cable for detection circuits"
        ))
        
        # NAC wiring
        recommendations.append(WireRecommendation(
            circuit_type="NAC",
            wire_type="FPLR",
            gauge="12 AWG",
            estimated_footage=estimated_nac_footage,
            cost_per_foot=1.45,
            total_cost=estimated_nac_footage * 1.45,
            reasoning="Higher capacity for notification appliances"
        ))
        
        # Power wiring
        recommendations.append(WireRecommendation(
            circuit_type="Power",
            wire_type="THHN",
            gauge="12 AWG",
            estimated_footage=estimated_power_footage,
            cost_per_foot=0.85,
            total_cost=estimated_power_footage * 0.85,
            reasoning="Standard power wiring for panel and equipment"
        ))
        
        return recommendations
    
    def _calculate_total_cost(
        self, 
        panel_recs: List[PanelRecommendation],
        expansion_recs: List[ExpansionRecommendation],
        wire_recs: List[WireRecommendation]
    ) -> float:
        """Calculate total estimated system cost."""
        total = 0.0
        
        # Primary panel cost
        if panel_recs:
            total += panel_recs[0].estimated_cost
        
        # Expansion costs
        for expansion in expansion_recs:
            if expansion.priority in ["essential", "recommended"]:
                total += expansion.estimated_cost
        
        # Wire costs
        for wire in wire_recs:
            total += wire.total_cost
        
        # Add installation and commissioning (typically 40-60% of material cost)
        installation_multiplier = 1.5
        total *= installation_multiplier
        
        return total
    
    def _create_implementation_plan(
        self, 
        requirements: ProjectRequirements, 
        complexity: SystemComplexity
    ) -> List[Dict[str, Any]]:
        """Create phased implementation plan."""
        phases = []
        
        # Phase 1: Design and Engineering
        phases.append({
            "phase": 1,
            "name": "Design & Engineering",
            "duration_weeks": 2 if complexity == SystemComplexity.SIMPLE else 4,
            "activities": [
                "Detailed system design",
                "Permit applications",
                "Equipment procurement",
                "Construction drawings"
            ]
        })
        
        # Phase 2: Installation
        install_weeks = {
            SystemComplexity.SIMPLE: 2,
            SystemComplexity.MODERATE: 4,
            SystemComplexity.COMPLEX: 6,
            SystemComplexity.ENTERPRISE: 8
        }
        
        phases.append({
            "phase": 2,
            "name": "Installation",
            "duration_weeks": install_weeks.get(complexity, 4),
            "activities": [
                "Device installation",
                "Wiring and connections",
                "Panel programming",
                "Initial testing"
            ]
        })
        
        # Phase 3: Commissioning
        phases.append({
            "phase": 3,
            "name": "Commissioning & Testing",
            "duration_weeks": 1 if complexity == SystemComplexity.SIMPLE else 2,
            "activities": [
                "System commissioning",
                "Acceptance testing",
                "Training",
                "Documentation"
            ]
        })
        
        return phases
    
    def _assess_risk_factors(
        self, 
        requirements: ProjectRequirements, 
        complexity: SystemComplexity
    ) -> List[str]:
        """Assess project risk factors."""
        risks = []
        
        if requirements.timeline_weeks < 8:
            risks.append("Aggressive timeline may impact quality")
        
        if complexity == SystemComplexity.ENTERPRISE:
            risks.append("Complex system requires experienced integrator")
        
        if requirements.total_area_sqft > 100000:
            risks.append("Large project scope increases coordination challenges")
        
        if "existing system integration" in requirements.integration_requirements:
            risks.append("Legacy system integration may have compatibility issues")
        
        return risks
    
    def _identify_success_factors(
        self, 
        requirements: ProjectRequirements, 
        complexity: SystemComplexity
    ) -> List[str]:
        """Identify project success factors."""
        factors = []
        
        if requirements.timeline_weeks > 12:
            factors.append("Adequate timeline allows for quality implementation")
        
        if requirements.budget_range[1] > 0:
            factors.append("Defined budget enables optimal equipment selection")
        
        factors.append("Early contractor engagement improves coordination")
        factors.append("Comprehensive testing ensures reliable operation")
        
        return factors
    
    def _estimate_timeline(
        self, 
        requirements: ProjectRequirements, 
        complexity: SystemComplexity
    ) -> int:
        """Estimate project timeline in weeks."""
        base_timeline = {
            SystemComplexity.SIMPLE: 6,
            SystemComplexity.MODERATE: 10,
            SystemComplexity.COMPLEX: 14,
            SystemComplexity.ENTERPRISE: 18
        }
        
        timeline = base_timeline.get(complexity, 10)
        
        # Adjust for special factors
        if requirements.total_area_sqft > 50000:
            timeline += 2
        
        if len(requirements.special_hazards) > 3:
            timeline += 1
        
        return timeline
    
    def _calculate_confidence_score(
        self, 
        requirements: ProjectRequirements,
        panel_recs: List[PanelRecommendation],
        total_cost: float
    ) -> float:
        """Calculate overall recommendation confidence."""
        base_confidence = 0.8
        
        # Panel recommendation quality
        if panel_recs and panel_recs[0].confidence_score > 0.8:
            base_confidence += 0.1
        
        # Budget alignment
        if requirements.budget_range[1] > 0:
            if requirements.budget_range[0] <= total_cost <= requirements.budget_range[1]:
                base_confidence += 0.1
            elif total_cost > requirements.budget_range[1]:
                base_confidence -= 0.2
        
        return min(base_confidence, 1.0)


def create_ai_recommendation_engine() -> AISystemRecommendationEngine:
    """Factory function to create AI recommendation engine."""
    return AISystemRecommendationEngine()


# Example usage and testing
if __name__ == "__main__":
    # Create recommendation engine
    ai_engine = create_ai_recommendation_engine()
    
    # Sample project requirements
    office_project = ProjectRequirements(
        building_type=BuildingType.OFFICE,
        total_area_sqft=25000,
        floor_count=3,
        occupant_load=150,
        special_hazards=["Server room", "Kitchen"],
        code_requirements=["NFPA 72", "Local AHJ"],
        budget_range=(15000, 25000),
        timeline_weeks=10,
        integration_requirements=["Security system", "HVAC"],
        accessibility_required=True
    )
    
    # Generate recommendations
    recommendation = ai_engine.recommend_system(office_project)
    
    print("🤖 AutoFire AI System Recommendations")
    print("=" * 50)
    print(f"Project ID: {recommendation.project_id}")
    print(f"Building Type: {office_project.building_type.value.title()}")
    print(f"Area: {office_project.total_area_sqft:,.0f} sq ft")
    print(f"Complexity: {recommendation.complexity_level.value.title()}")
    print(f"Confidence: {recommendation.confidence_score:.1%}")
    print()
    
    # Panel recommendations
    print("🔥 Recommended Fire Alarm Panel:")
    if recommendation.panel_recommendations:
        panel = recommendation.panel_recommendations[0]
        print(f"   {panel.manufacturer} {panel.model}")
        print(f"   Capacity: {panel.capacity_devices} devices, {panel.capacity_zones} zones")
        print(f"   Cost: ${panel.estimated_cost:,.2f}")
        print(f"   Confidence: {panel.confidence_score:.1%}")
        
        for reason in panel.reasoning[:2]:
            print(f"   • {reason}")
    
    # Cost summary
    print(f"\n💰 Total Estimated Cost: ${recommendation.total_estimated_cost:,.2f}")
    print(f"📅 Timeline: {recommendation.timeline_estimate_weeks} weeks")
    
    # Implementation phases
    print(f"\n📋 Implementation Plan:")
    for phase in recommendation.implementation_phases:
        print(f"   Phase {phase['phase']}: {phase['name']} ({phase['duration_weeks']} weeks)")
    
    print(f"\n🎉 AI recommendations generated successfully!")