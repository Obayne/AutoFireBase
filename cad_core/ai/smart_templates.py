"""
AutoFire Smart Project Templates
===============================

Intelligent project templates that adapt based on building type, size, occupancy
classification, and local code requirements. Templates learn from previous
successful projects and continuously improve suggestions.

Features:
- Building type classification and analysis
- Occupancy-based template selection
- Adaptive device placement patterns
- Code-compliant layouts
- Cost-optimized system designs
- Learning from project history
- Local jurisdiction customization

Author: AutoFire AI Team
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum
import json
import math
from datetime import datetime
import copy

class BuildingType(Enum):
    """Standard building classifications"""
    OFFICE = "office"
    RETAIL = "retail"
    WAREHOUSE = "warehouse"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    HOSPITALITY = "hospitality"
    RESIDENTIAL = "residential"
    INDUSTRIAL = "industrial"
    ASSEMBLY = "assembly"
    MIXED_USE = "mixed_use"

class OccupancyClass(Enum):
    """Occupancy classifications per building codes"""
    A_ASSEMBLY = "assembly"           # Theaters, stadiums, churches
    B_BUSINESS = "business"           # Offices, banks, stores
    E_EDUCATIONAL = "educational"     # Schools, day care
    F_FACTORY = "factory"             # Manufacturing, processing
    H_HAZARDOUS = "hazardous"         # Chemical storage, labs
    I_INSTITUTIONAL = "institutional" # Hospitals, prisons
    M_MERCANTILE = "mercantile"       # Retail, malls
    R_RESIDENTIAL = "residential"     # Hotels, apartments
    S_STORAGE = "storage"             # Warehouses, parking
    U_UTILITY = "utility"             # Agricultural, miscellaneous

class TemplateAdaptation(Enum):
    """How templates adapt to project requirements"""
    STRICT = "strict"           # Follow template exactly
    ADAPTIVE = "adaptive"       # Modify based on specific needs
    LEARNING = "learning"       # Learn from user modifications
    CUSTOM = "custom"           # Heavily customized for unique needs

@dataclass
class DevicePattern:
    """Device placement pattern for templates"""
    device_type: str
    spacing_rules: Dict[str, float]
    coverage_area: float
    height_requirements: Dict[str, float]
    placement_priority: int = 1
    code_references: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'device_type': self.device_type,
            'spacing_rules': self.spacing_rules,
            'coverage_area': self.coverage_area,
            'height_requirements': self.height_requirements,
            'placement_priority': self.placement_priority,
            'code_references': self.code_references
        }

@dataclass
class SystemTemplate:
    """Complete fire alarm system template"""
    template_id: str
    name: str
    description: str
    building_type: BuildingType
    occupancy_class: OccupancyClass
    size_range: Tuple[float, float]  # Min/max square footage
    device_patterns: List[DevicePattern] = field(default_factory=list)
    panel_specifications: Dict[str, Any] = field(default_factory=dict)
    circuit_layouts: List[Dict[str, Any]] = field(default_factory=list)
    code_requirements: Dict[str, Any] = field(default_factory=dict)
    cost_estimates: Dict[str, float] = field(default_factory=dict)
    success_metrics: Dict[str, float] = field(default_factory=dict)
    adaptation_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def calculate_fit_score(self, project_requirements: Dict[str, Any]) -> float:
        """Calculate how well this template fits project requirements"""
        score = 0.0
        max_score = 100.0
        
        # Building type match
        req_building_type = project_requirements.get('building_type')
        if req_building_type == self.building_type.value:
            score += 30.0
        elif req_building_type in ['mixed_use', 'other']:
            score += 15.0
        
        # Occupancy class match
        req_occupancy = project_requirements.get('occupancy_class')
        if req_occupancy == self.occupancy_class.value:
            score += 25.0
        
        # Size range match
        req_size = project_requirements.get('building_area', 0)
        if self.size_range[0] <= req_size <= self.size_range[1]:
            score += 25.0
        elif req_size < self.size_range[0]:
            # Penalty for undersized
            ratio = req_size / self.size_range[0]
            score += 25.0 * max(0, ratio)
        else:
            # Penalty for oversized
            ratio = self.size_range[1] / req_size
            score += 25.0 * max(0, ratio)
        
        # Code requirements match
        req_codes = set(project_requirements.get('applicable_codes', []))
        template_codes = set(self.code_requirements.keys())
        if req_codes and template_codes:
            overlap = len(req_codes.intersection(template_codes))
            total = len(req_codes.union(template_codes))
            score += 20.0 * (overlap / total) if total > 0 else 0
        else:
            score += 10.0  # Partial credit if no specific codes listed
        
        return min(score, max_score)

@dataclass 
class AdaptedTemplate:
    """Template adapted to specific project requirements"""
    base_template: SystemTemplate
    project_requirements: Dict[str, Any]
    adaptations: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0
    estimated_devices: Dict[str, int] = field(default_factory=dict)
    layout_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'base_template_id': self.base_template.template_id,
            'template_name': self.base_template.name,
            'adaptations': self.adaptations,
            'confidence_score': self.confidence_score,
            'estimated_devices': self.estimated_devices,
            'layout_suggestions': self.layout_suggestions
        }

class TemplateLibrary:
    """Library of standard fire alarm system templates"""
    
    def __init__(self):
        self.templates: List[SystemTemplate] = []
        self._initialize_standard_templates()
    
    def _initialize_standard_templates(self):
        """Initialize standard industry templates"""
        
        # Office Building Template
        office_template = SystemTemplate(
            template_id="TPL_OFFICE_STANDARD",
            name="Standard Office Building",
            description="Typical commercial office building with standard NFPA 72 compliance",
            building_type=BuildingType.OFFICE,
            occupancy_class=OccupancyClass.B_BUSINESS,
            size_range=(5000, 100000),  # 5K to 100K sq ft
            device_patterns=[
                DevicePattern(
                    device_type="smoke_detector",
                    spacing_rules={"max_spacing": 30, "min_wall_distance": 4},
                    coverage_area=900,  # 30x30 ft
                    height_requirements={"min_height": 8, "max_height": 10},
                    placement_priority=1,
                    code_references=["NFPA 72 Section 17.7"]
                ),
                DevicePattern(
                    device_type="manual_pull_station",
                    spacing_rules={"max_travel_distance": 200},
                    coverage_area=40000,  # 200 ft radius
                    height_requirements={"mounting_height": 3.5},
                    placement_priority=2,
                    code_references=["NFPA 72 Section 17.14"]
                ),
                DevicePattern(
                    device_type="notification_appliance",
                    spacing_rules={"max_spacing": 100},
                    coverage_area=10000,
                    height_requirements={"min_height": 8},
                    placement_priority=3,
                    code_references=["NFPA 72 Section 18"]
                )
            ],
            panel_specifications={
                "recommended_type": "addressable",
                "min_device_capacity": 159,
                "backup_power_hours": 24,
                "alarm_power_minutes": 15
            },
            circuit_layouts=[
                {
                    "circuit_type": "SLC",
                    "max_devices": 159,
                    "wire_gauge": "18_AWG",
                    "topology": "class_A"
                },
                {
                    "circuit_type": "NAC", 
                    "max_devices": 20,
                    "wire_gauge": "14_AWG",
                    "supervision": "EOLR"
                }
            ],
            code_requirements={
                "NFPA_72": ["17.7", "17.14", "18", "23"],
                "IBC": ["907"],
                "ADA": ["4.28"]
            },
            cost_estimates={
                "devices_per_sqft": 0.08,
                "installation_per_device": 150.0,
                "panel_base_cost": 5000.0
            },
            success_metrics={
                "device_utilization": 0.75,
                "coverage_efficiency": 0.95,
                "code_compliance": 1.0
            }
        )
        
        # Warehouse Template
        warehouse_template = SystemTemplate(
            template_id="TPL_WAREHOUSE_STANDARD",
            name="Industrial Warehouse",
            description="Large warehouse with high ceilings and storage areas",
            building_type=BuildingType.WAREHOUSE,
            occupancy_class=OccupancyClass.S_STORAGE,
            size_range=(20000, 500000),
            device_patterns=[
                DevicePattern(
                    device_type="beam_smoke_detector",
                    spacing_rules={"max_spacing": 60, "beam_length": 300},
                    coverage_area=3600,  # 60x60 ft
                    height_requirements={"min_height": 20, "max_height": 40},
                    placement_priority=1,
                    code_references=["NFPA 72 Section 17.7.3.5"]
                ),
                DevicePattern(
                    device_type="heat_detector",
                    spacing_rules={"max_spacing": 50},
                    coverage_area=2500,  # 50x50 ft
                    height_requirements={"min_height": 15},
                    placement_priority=2,
                    code_references=["NFPA 72 Section 17.6"]
                )
            ],
            panel_specifications={
                "recommended_type": "addressable",
                "min_device_capacity": 318,
                "backup_power_hours": 60,
                "alarm_power_minutes": 5
            },
            cost_estimates={
                "devices_per_sqft": 0.04,  # Lower density for warehouse
                "installation_per_device": 200.0,  # Higher due to height
                "panel_base_cost": 8000.0
            }
        )
        
        # Healthcare Template
        healthcare_template = SystemTemplate(
            template_id="TPL_HEALTHCARE_STANDARD",
            name="Healthcare Facility",
            description="Hospital or clinic with special life safety requirements",
            building_type=BuildingType.HEALTHCARE,
            occupancy_class=OccupancyClass.I_INSTITUTIONAL,
            size_range=(10000, 200000),
            device_patterns=[
                DevicePattern(
                    device_type="smoke_detector",
                    spacing_rules={"max_spacing": 30, "corridor_spacing": 15},
                    coverage_area=900,
                    height_requirements={"min_height": 8, "max_height": 12},
                    placement_priority=1
                ),
                DevicePattern(
                    device_type="visual_strobe",
                    spacing_rules={"max_spacing": 50},
                    coverage_area=2500,
                    height_requirements={"mounting_height": 8},
                    placement_priority=2
                )
            ],
            panel_specifications={
                "recommended_type": "addressable_voice",
                "min_device_capacity": 318,
                "backup_power_hours": 24,
                "alarm_power_minutes": 15,
                "voice_capability": True
            },
            code_requirements={
                "NFPA_72": ["17.7", "18", "24"],
                "NFPA_101": ["18.3", "19.3"],
                "CMS": ["Life_Safety_Code"],
                "ADA": ["4.28"]
            },
            cost_estimates={
                "devices_per_sqft": 0.12,  # Higher density for healthcare
                "installation_per_device": 175.0,
                "panel_base_cost": 12000.0
            }
        )
        
        self.templates = [office_template, warehouse_template, healthcare_template]
    
    def find_matching_templates(self, project_requirements: Dict[str, Any], max_results: int = 3) -> List[Tuple[SystemTemplate, float]]:
        """Find templates that best match project requirements"""
        scored_templates = []
        
        for template in self.templates:
            fit_score = template.calculate_fit_score(project_requirements)
            scored_templates.append((template, fit_score))
        
        # Sort by fit score (highest first)
        scored_templates.sort(key=lambda x: x[1], reverse=True)
        
        return scored_templates[:max_results]

class TemplateAdapter:
    """Adapts templates to specific project requirements"""
    
    def adapt_template(self, template: SystemTemplate, project_requirements: Dict[str, Any]) -> AdaptedTemplate:
        """Adapt a template to specific project requirements"""
        adapted = AdaptedTemplate(
            base_template=template,
            project_requirements=project_requirements
        )
        
        # Calculate device counts
        building_area = project_requirements.get('building_area', 50000)
        adapted.estimated_devices = self._calculate_device_counts(template, building_area)
        
        # Generate layout suggestions
        adapted.layout_suggestions = self._generate_layout_suggestions(template, project_requirements)
        
        # Track adaptations made
        adaptations = []
        
        # Area-based adaptations
        template_size_mid = (template.size_range[0] + template.size_range[1]) / 2
        if building_area < template_size_mid * 0.7:
            adaptations.append({
                'type': 'size_reduction',
                'description': f'Reduced system size for {building_area:,.0f} sq ft building',
                'impact': 'Fewer circuits and smaller panel may be sufficient'
            })
        elif building_area > template_size_mid * 1.3:
            adaptations.append({
                'type': 'size_expansion',
                'description': f'Expanded system for {building_area:,.0f} sq ft building',
                'impact': 'Additional circuits and larger panel capacity required'
            })
        
        # Special requirements adaptations
        special_requirements = project_requirements.get('special_requirements', [])
        for requirement in special_requirements:
            if requirement == 'high_ceiling':
                adaptations.append({
                    'type': 'high_ceiling_adaptation',
                    'description': 'Modified for high ceiling environment',
                    'impact': 'Beam detectors and special mounting recommended'
                })
            elif requirement == 'corrosive_environment':
                adaptations.append({
                    'type': 'environmental_adaptation',
                    'description': 'Specified corrosion-resistant devices',
                    'impact': 'Special device ratings and enclosures required'
                })
        
        adapted.adaptations = adaptations
        adapted.confidence_score = self._calculate_adaptation_confidence(template, project_requirements, adaptations)
        
        return adapted
    
    def _calculate_device_counts(self, template: SystemTemplate, building_area: float) -> Dict[str, int]:
        """Calculate estimated device counts based on template and area"""
        device_counts = {}
        
        for pattern in template.device_patterns:
            if pattern.coverage_area > 0:
                # Basic area-based calculation
                base_count = math.ceil(building_area / pattern.coverage_area)
                
                # Apply minimum requirements
                if pattern.device_type == "manual_pull_station":
                    min_count = max(2, math.ceil(building_area / 40000))  # At least every 200 ft travel
                    base_count = max(base_count, min_count)
                elif pattern.device_type in ["smoke_detector", "heat_detector"]:
                    # Ensure reasonable coverage
                    min_count = max(4, base_count)
                    base_count = min_count
                
                device_counts[pattern.device_type] = base_count
        
        return device_counts
    
    def _generate_layout_suggestions(self, template: SystemTemplate, project_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate layout suggestions based on template and requirements"""
        suggestions = []
        
        building_shape = project_requirements.get('building_shape', 'rectangular')
        
        if building_shape == 'rectangular':
            suggestions.append({
                'type': 'grid_layout',
                'description': 'Regular grid pattern for optimal coverage',
                'devices': 'smoke_detectors',
                'pattern': 'orthogonal_grid'
            })
        elif building_shape == 'irregular':
            suggestions.append({
                'type': 'adaptive_layout',
                'description': 'Custom placement following building geometry',
                'devices': 'all_devices',
                'pattern': 'building_adaptive'
            })
        
        # Corridor suggestions
        has_corridors = project_requirements.get('has_corridors', True)
        if has_corridors:
            suggestions.append({
                'type': 'corridor_placement',
                'description': 'Additional devices in corridors per NFPA requirements',
                'devices': 'smoke_detectors',
                'spacing': '15_ft_max'
            })
        
        return suggestions
    
    def _calculate_adaptation_confidence(self, template: SystemTemplate, project_requirements: Dict[str, Any], adaptations: List[Dict[str, Any]]) -> float:
        """Calculate confidence in template adaptation"""
        base_confidence = template.calculate_fit_score(project_requirements)
        
        # Reduce confidence for each major adaptation
        adaptation_penalty = len([a for a in adaptations if a['type'] in ['size_expansion', 'environmental_adaptation']]) * 10
        
        # Boost confidence for successful historical adaptations
        success_bonus = template.success_metrics.get('code_compliance', 0.8) * 10
        
        final_confidence = min(100, max(0, base_confidence - adaptation_penalty + success_bonus))
        return final_confidence

class SmartProjectTemplateEngine:
    """Main AI-powered project template engine"""
    
    def __init__(self):
        self.template_library = TemplateLibrary()
        self.template_adapter = TemplateAdapter()
        self.usage_history = []
        self.learning_data = {}
    
    def recommend_templates(self, project_requirements: Dict[str, Any]) -> List[AdaptedTemplate]:
        """Recommend and adapt templates for project requirements"""
        # Find matching templates
        matching_templates = self.template_library.find_matching_templates(project_requirements)
        
        # Adapt each template
        adapted_templates = []
        for template, fit_score in matching_templates:
            adapted = self.template_adapter.adapt_template(template, project_requirements)
            adapted_templates.append(adapted)
        
        # Sort by confidence score
        adapted_templates.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return adapted_templates
    
    def generate_project_from_template(self, adapted_template: AdaptedTemplate) -> Dict[str, Any]:
        """Generate complete project configuration from adapted template"""
        project = {
            'project_id': f"PROJ_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'template_used': adapted_template.base_template.template_id,
            'building_info': adapted_template.project_requirements,
            'devices': [],
            'circuits': [],
            'panel_config': {},
            'estimated_cost': 0.0,
            'compliance_notes': []
        }
        
        # Generate device list
        devices_list = project['devices']
        if isinstance(devices_list, list):
            for device_type, count in adapted_template.estimated_devices.items():
                for i in range(count):
                    device = {
                        'id': f"{device_type.upper()}_{i+1:03d}",
                        'type': device_type,
                        'location': {'x': 0, 'y': 0},  # To be placed by user
                        'address': i + 1,
                        'circuit': 'SLC1',  # Default assignment
                        'notes': f'Generated from template {adapted_template.base_template.name}'
                    }
                    devices_list.append(device)
        
        # Generate circuit configuration
        template = adapted_template.base_template
        circuits_list = project['circuits']
        if isinstance(circuits_list, list):
            for circuit_layout in template.circuit_layouts:
                circuit = {
                    'id': f"{circuit_layout['circuit_type']}1",
                    'type': circuit_layout['circuit_type'],
                    'wire_gauge': circuit_layout.get('wire_gauge', '18_AWG'),
                    'devices': [],
                    'max_capacity': circuit_layout.get('max_devices', 159)
                }
                circuits_list.append(circuit)
        
        # Estimate project cost
        building_area = adapted_template.project_requirements.get('building_area', 50000)
        device_cost = sum(adapted_template.estimated_devices.values()) * 100  # $100 per device average
        installation_cost = sum(adapted_template.estimated_devices.values()) * template.cost_estimates.get('installation_per_device', 150)
        panel_cost = template.cost_estimates.get('panel_base_cost', 5000)
        
        project['estimated_cost'] = device_cost + installation_cost + panel_cost
        
        # Add compliance notes
        compliance_notes = project['compliance_notes']
        if isinstance(compliance_notes, list):
            for code, sections in template.code_requirements.items():
                compliance_notes.append(f"{code}: Sections {', '.join(sections)}")
        
        return project
    
    def learn_from_project(self, project_data: Dict[str, Any], user_feedback: Dict[str, Any]):
        """Learn from completed projects to improve templates"""
        template_id = project_data.get('template_used')
        if template_id:
            if template_id not in self.learning_data:
                self.learning_data[template_id] = {
                    'usage_count': 0,
                    'success_rate': 0.0,
                    'common_modifications': {},
                    'user_satisfaction': []
                }
            
            learning_entry = self.learning_data[template_id]
            learning_entry['usage_count'] += 1
            
            # Track user satisfaction
            satisfaction = user_feedback.get('satisfaction_rating', 3)  # 1-5 scale
            learning_entry['user_satisfaction'].append(satisfaction)
            
            # Track common modifications
            modifications = user_feedback.get('modifications_made', [])
            for mod in modifications:
                mod_type = mod.get('type', 'unknown')
                learning_entry['common_modifications'][mod_type] = learning_entry['common_modifications'].get(mod_type, 0) + 1
            
            # Update template success metrics
            self._update_template_metrics(template_id, user_feedback)
    
    def _update_template_metrics(self, template_id: str, feedback: Dict[str, Any]):
        """Update template success metrics based on feedback"""
        for template in self.template_library.templates:
            if template.template_id == template_id:
                # Update success metrics
                if 'code_compliance_achieved' in feedback:
                    template.success_metrics['code_compliance'] = feedback['code_compliance_achieved']
                
                if 'device_utilization' in feedback:
                    template.success_metrics['device_utilization'] = feedback['device_utilization']
                
                # Record adaptation in history
                template.adaptation_history.append({
                    'date': datetime.now().isoformat(),
                    'feedback': feedback,
                    'adaptations_successful': feedback.get('template_worked_well', True)
                })
                break
    
    def get_template_analytics(self) -> Dict[str, Any]:
        """Get analytics on template usage and performance"""
        analytics = {
            'total_templates': len(self.template_library.templates),
            'template_performance': {},
            'most_used_templates': [],
            'common_adaptations': {},
            'success_rates': {}
        }
        
        for template_id, data in self.learning_data.items():
            if isinstance(analytics['template_performance'], dict):
                analytics['template_performance'][template_id] = {
                    'usage_count': data['usage_count'],
                    'avg_satisfaction': sum(data['user_satisfaction']) / len(data['user_satisfaction']) if data['user_satisfaction'] else 0,
                    'common_modifications': data['common_modifications']
                }
        
        # Sort templates by usage
        sorted_usage = sorted(self.learning_data.items(), key=lambda x: x[1]['usage_count'], reverse=True)
        analytics['most_used_templates'] = [(tid, data['usage_count']) for tid, data in sorted_usage[:5]]
        
        return analytics

def demo_smart_templates():
    """Demonstrate smart project template capabilities"""
    print("🏗️ AutoFire Smart Project Templates Demo")
    print("=" * 45)
    
    # Sample project requirements
    project_requirements = {
        'building_type': 'office',
        'occupancy_class': 'business',
        'building_area': 25000,  # 25,000 sq ft
        'building_shape': 'rectangular',
        'has_corridors': True,
        'ceiling_height': 9,
        'special_requirements': [],
        'applicable_codes': ['NFPA_72', 'IBC', 'ADA'],
        'budget_range': 'standard',
        'timeline': 'normal'
    }
    
    # Create template engine
    template_engine = SmartProjectTemplateEngine()
    
    print("📋 Project Requirements:")
    print(f"   Building Type: {project_requirements['building_type'].title()}")
    print(f"   Area: {project_requirements['building_area']:,} sq ft")
    print(f"   Occupancy: {project_requirements['occupancy_class'].title()}")
    print()
    
    # Get template recommendations
    print("🎯 Finding Matching Templates...")
    recommended_templates = template_engine.recommend_templates(project_requirements)
    
    print(f"\n📝 Template Recommendations ({len(recommended_templates)} found):")
    for i, adapted in enumerate(recommended_templates, 1):
        template = adapted.base_template
        print(f"\n{i}. {template.name}")
        print(f"   Description: {template.description}")
        print(f"   Confidence: {adapted.confidence_score:.1f}%")
        print(f"   Estimated Devices: {sum(adapted.estimated_devices.values())}")
        
        if adapted.adaptations:
            print("   Adaptations:")
            for adaptation in adapted.adaptations[:2]:  # Show first 2
                print(f"     • {adaptation['description']}")
    
    # Generate project from best template
    project = None
    if recommended_templates:
        best_template = recommended_templates[0]
        print(f"\n🚀 Generating Project from '{best_template.base_template.name}'...")
        
        project = template_engine.generate_project_from_template(best_template)
        
        print(f"\n📊 Generated Project Summary:")
        print(f"   Project ID: {project['project_id']}")
        print(f"   Total Devices: {len(project['devices'])}")
        print(f"   Circuits: {len(project['circuits'])}")
        print(f"   Estimated Cost: ${project['estimated_cost']:,.2f}")
        
        print(f"\n🔍 Device Breakdown:")
        device_summary = {}
        for device in project['devices']:
            device_type = device['type']
            device_summary[device_type] = device_summary.get(device_type, 0) + 1
        
        for device_type, count in device_summary.items():
            print(f"   • {device_type.replace('_', ' ').title()}: {count}")
        
        print(f"\n📜 Compliance Notes:")
        for note in project['compliance_notes'][:3]:  # Show first 3
            print(f"   • {note}")
    
    # Simulate learning from feedback
    print(f"\n🧠 Learning Simulation:")
    sample_feedback = {
        'satisfaction_rating': 4,  # 1-5 scale
        'template_worked_well': True,
        'modifications_made': [
            {'type': 'device_relocation', 'count': 3},
            {'type': 'additional_devices', 'count': 2}
        ],
        'code_compliance_achieved': True,
        'device_utilization': 0.82
    }
    
    if recommended_templates and project:
        template_engine.learn_from_project(project, sample_feedback)
        print("   ✓ User feedback recorded for template improvement")
        
        analytics = template_engine.get_template_analytics()
        print(f"   📈 Analytics: {analytics['total_templates']} templates tracked")
    
    print("\n✅ Smart project templates demo completed!")

if __name__ == "__main__":
    demo_smart_templates()