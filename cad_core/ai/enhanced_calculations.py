"""
AutoFire Enhanced Live Calculations AI
=====================================

AI-enhanced live calculations with predictive analysis, 'what-if' scenarios,
and automatic optimization suggestions for fire alarm system design.

Features:
- Predictive voltage drop analysis
- What-if scenario modeling 
- Automatic optimization suggestions
- Battery sizing predictions
- Circuit loading optimization
- Cost-performance analysis
- Real-time design feedback

Author: AutoFire AI Team
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable, cast
from enum import Enum
import json
import math
from datetime import datetime, timedelta

class OptimizationType(Enum):
    """Types of optimization analysis"""
    COST = "cost"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    EFFICIENCY = "efficiency"
    MAINTENANCE = "maintenance"

class PredictionConfidence(Enum):
    """Confidence levels for AI predictions"""
    HIGH = "high"      # 90%+ confidence
    MEDIUM = "medium"  # 70-90% confidence  
    LOW = "low"        # 50-70% confidence

@dataclass
class OptimizationSuggestion:
    """Single optimization suggestion"""
    type: OptimizationType
    title: str
    description: str
    impact: str
    effort: str  # Low, Medium, High
    cost_savings: Optional[float] = None
    performance_gain: Optional[float] = None
    confidence: PredictionConfidence = PredictionConfidence.MEDIUM
    implementation_steps: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type.value,
            'title': self.title,
            'description': self.description,
            'impact': self.impact,
            'effort': self.effort,
            'cost_savings': self.cost_savings,
            'performance_gain': self.performance_gain,
            'confidence': self.confidence.value,
            'implementation_steps': self.implementation_steps
        }

@dataclass
class WhatIfScenario:
    """What-if scenario analysis"""
    name: str
    description: str
    changes: Dict[str, Any]
    predicted_outcomes: Dict[str, Any] = field(default_factory=dict)
    confidence: PredictionConfidence = PredictionConfidence.MEDIUM
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'changes': self.changes,
            'predicted_outcomes': self.predicted_outcomes,
            'confidence': self.confidence.value
        }

@dataclass
class PredictiveAnalysis:
    """Predictive analysis results"""
    voltage_drop_prediction: Dict[str, float]
    battery_life_prediction: Dict[str, float]
    failure_probability: Dict[str, float]
    maintenance_schedule: Dict[str, datetime]
    performance_trends: Dict[str, List[float]]
    confidence_scores: Dict[str, float]

class VoltageDropPredictor:
    """AI-enhanced voltage drop prediction and optimization"""
    
    def __init__(self):
        self.wire_resistance_data = {
            '18': 6.5e-3,  # ohms per foot
            '16': 4.1e-3,
            '14': 2.6e-3,
            '12': 1.6e-3,
            '10': 1.0e-3
        }
        
        self.historical_patterns = {
            'temperature_coefficient': 0.004,  # resistance change per °C
            'aging_factor': 0.02,              # annual resistance increase
            'connection_degradation': 0.01     # connection resistance increase
        }
    
    def predict_voltage_drop(self, circuit_data: Dict, future_years: int = 5) -> Dict[str, Any]:
        """Predict voltage drop over time with aging effects"""
        wire_gauge = circuit_data.get('wire_gauge', '18')
        length = circuit_data.get('length', 100)  # feet
        current = circuit_data.get('current', 1.0)  # amps
        
        base_resistance = self.wire_resistance_data.get(wire_gauge, 6.5e-3)
        
        predictions = {}
        for year in range(future_years + 1):
            # Apply aging effects
            aged_resistance = base_resistance * (1 + year * self.historical_patterns['aging_factor'])
            
            # Temperature effects (assume worst case +25°C)
            temp_resistance = aged_resistance * (1 + 25 * self.historical_patterns['temperature_coefficient'])
            
            # Connection degradation
            connection_resistance = year * self.historical_patterns['connection_degradation']
            
            total_resistance = (temp_resistance * length) + connection_resistance
            voltage_drop = current * total_resistance
            
            predictions[f'year_{year}'] = {
                'voltage_drop': voltage_drop,
                'resistance': total_resistance,
                'efficiency': max(0, 100 - (voltage_drop / 24.0 * 100))  # Assume 24V system
            }
        
        # Determine trending based on available data
        max_year_key = f'year_{future_years}'
        trending = 'stable'
        if max_year_key in predictions and 'year_0' in predictions:
            if predictions[max_year_key]['voltage_drop'] > predictions['year_0']['voltage_drop'] * 1.1:
                trending = 'degrading'
        
        return {
            'predictions': predictions,
            'confidence': PredictionConfidence.HIGH.value,
            'trending': trending
        }
    
    def suggest_wire_optimization(self, circuit_data: Dict) -> List[OptimizationSuggestion]:
        """Suggest wire gauge optimizations"""
        suggestions = []
        current_gauge = circuit_data.get('wire_gauge', '18')
        current_drop = self.predict_voltage_drop(circuit_data, 0)['predictions']['year_0']['voltage_drop']
        
        # Test larger wire gauges
        for test_gauge in ['16', '14', '12', '10']:
            if test_gauge == current_gauge:
                continue
                
            test_circuit = circuit_data.copy()
            test_circuit['wire_gauge'] = test_gauge
            test_drop = self.predict_voltage_drop(test_circuit, 0)['predictions']['year_0']['voltage_drop']
            
            improvement = (current_drop - test_drop) / current_drop * 100
            
            if improvement > 10:  # Significant improvement
                wire_cost_increase = self._calculate_wire_cost_difference(current_gauge, test_gauge, circuit_data.get('length', 100))
                
                suggestions.append(OptimizationSuggestion(
                    type=OptimizationType.PERFORMANCE,
                    title=f"Upgrade to {test_gauge} AWG Wire",
                    description=f"Reduce voltage drop by {improvement:.1f}% ({current_drop:.2f}V → {test_drop:.2f}V)",
                    impact=f"Improved reliability and {improvement:.1f}% better efficiency",
                    effort="Low" if improvement < 20 else "Medium",
                    cost_savings=wire_cost_increase * -1,  # Negative because it's additional cost
                    performance_gain=improvement,
                    confidence=PredictionConfidence.HIGH,
                    implementation_steps=[
                        f"Replace {current_gauge} AWG wire with {test_gauge} AWG",
                        "Update circuit documentation",
                        "Verify connections and terminations"
                    ]
                ))
        
        return suggestions
    
    def _calculate_wire_cost_difference(self, current_gauge: str, new_gauge: str, length: float) -> float:
        """Calculate cost difference for wire upgrade"""
        wire_costs = {  # Cost per foot
            '18': 0.50,
            '16': 0.65,
            '14': 0.85,
            '12': 1.20,
            '10': 1.65
        }
        
        current_cost = wire_costs.get(current_gauge, 0.50) * length
        new_cost = wire_costs.get(new_gauge, 0.50) * length
        
        return new_cost - current_cost

class BatteryLifePredictor:
    """AI-enhanced battery life prediction and optimization"""
    
    def __init__(self):
        self.battery_characteristics = {
            'sealed_lead_acid': {
                'capacity_degradation_rate': 0.05,  # 5% per year
                'temperature_coefficient': -0.005,  # capacity change per °C
                'cycle_life': 300,
                'float_life_years': 5
            },
            'lithium': {
                'capacity_degradation_rate': 0.03,  # 3% per year
                'temperature_coefficient': -0.002,
                'cycle_life': 2000,
                'float_life_years': 10
            }
        }
    
    def predict_battery_performance(self, battery_data: Dict, usage_pattern: Dict) -> Dict[str, Any]:
        """Predict battery performance over time"""
        battery_type = battery_data.get('type', 'sealed_lead_acid')
        initial_capacity = battery_data.get('capacity_ah', 12)
        avg_temperature = battery_data.get('avg_temperature_c', 25)
        
        characteristics = self.battery_characteristics.get(battery_type, self.battery_characteristics['sealed_lead_acid'])
        
        predictions = {}
        for year in range(6):  # 5 years + current
            # Capacity degradation
            degradation = year * characteristics['capacity_degradation_rate']
            
            # Temperature effects
            temp_effect = (avg_temperature - 20) * characteristics['temperature_coefficient']
            
            # Current capacity
            current_capacity = initial_capacity * (1 - degradation + temp_effect)
            
            # Standby time calculation
            standby_current = usage_pattern.get('standby_current_ma', 100) / 1000  # Convert to amps
            standby_hours = current_capacity / standby_current if standby_current > 0 else float('inf')
            
            # Alarm time calculation
            alarm_current = usage_pattern.get('alarm_current_a', 2.0)
            alarm_hours = current_capacity / alarm_current if alarm_current > 0 else 0
            
            predictions[f'year_{year}'] = {
                'capacity_ah': max(0, current_capacity),
                'standby_hours': min(standby_hours, 8760),  # Max 1 year
                'alarm_hours': alarm_hours,
                'replacement_recommended': current_capacity < initial_capacity * 0.8
            }
        
        return {
            'predictions': predictions,
            'replacement_timeline': self._calculate_replacement_timeline(predictions),
            'confidence': PredictionConfidence.HIGH.value
        }
    
    def _calculate_replacement_timeline(self, predictions: Dict) -> Dict[str, Any]:
        """Calculate optimal battery replacement timeline"""
        replacement_year = None
        for year_key, data in predictions.items():
            if data['replacement_recommended']:
                replacement_year = int(year_key.split('_')[1])
                break
        
        return {
            'recommended_replacement_year': replacement_year or 5,
            'early_warning_year': max(1, (replacement_year or 5) - 1),
            'cost_optimal_year': replacement_year or 4  # Replace slightly early for cost optimization
        }

class CircuitOptimizer:
    """AI-powered circuit optimization engine"""
    
    def analyze_circuit_loading(self, circuits: List[Dict]) -> List[OptimizationSuggestion]:
        """Analyze and optimize circuit loading"""
        suggestions = []
        
        for circuit in circuits:
            devices = circuit.get('devices', [])
            max_capacity = circuit.get('max_capacity', 159)  # Default SLC capacity
            current_load = len(devices)
            
            utilization = current_load / max_capacity
            
            if utilization > 0.9:  # Over 90% utilized
                suggestions.append(OptimizationSuggestion(
                    type=OptimizationType.RELIABILITY,
                    title=f"Circuit {circuit.get('id', 'Unknown')} Near Capacity",
                    description=f"Circuit is {utilization*100:.1f}% utilized ({current_load}/{max_capacity} devices)",
                    impact="Reduced expansion capability and increased failure risk",
                    effort="Medium",
                    performance_gain=20.0,
                    confidence=PredictionConfidence.HIGH,
                    implementation_steps=[
                        "Add additional circuit for expansion",
                        "Redistribute devices across circuits",
                        "Consider higher capacity panel if needed"
                    ]
                ))
            
            elif utilization < 0.3:  # Under 30% utilized
                # Look for opportunities to consolidate
                underutilized_circuits = [c for c in circuits if len(c.get('devices', [])) / c.get('max_capacity', 159) < 0.3]
                
                if len(underutilized_circuits) > 1:
                    total_devices = sum(len(c.get('devices', [])) for c in underutilized_circuits)
                    if total_devices < max_capacity * 0.8:  # Can consolidate
                        suggestions.append(OptimizationSuggestion(
                            type=OptimizationType.COST,
                            title="Consolidate Underutilized Circuits",
                            description=f"Combine {len(underutilized_circuits)} circuits to reduce hardware costs",
                            impact="Reduced panel size and installation costs",
                            effort="Medium",
                            cost_savings=500.0 * (len(underutilized_circuits) - 1),  # Estimate savings
                            confidence=PredictionConfidence.MEDIUM,
                            implementation_steps=[
                                "Verify wire run compatibility",
                                "Reconfigure circuit assignments", 
                                "Update panel programming"
                            ]
                        ))
        
        return suggestions

class WhatIfAnalyzer:
    """What-if scenario analysis engine"""
    
    def __init__(self):
        self.voltage_predictor = VoltageDropPredictor()
        self.battery_predictor = BatteryLifePredictor()
    
    def analyze_scenarios(self, base_system: Dict, scenarios: List[Dict]) -> List[WhatIfScenario]:
        """Analyze multiple what-if scenarios"""
        analyzed_scenarios = []
        
        for scenario_data in scenarios:
            scenario = WhatIfScenario(
                name=scenario_data['name'],
                description=scenario_data['description'],
                changes=scenario_data['changes']
            )
            
            # Apply changes to base system
            modified_system = self._apply_changes(base_system, scenario.changes)
            
            # Predict outcomes
            outcomes = self._predict_scenario_outcomes(base_system, modified_system)
            scenario.predicted_outcomes = outcomes
            
            analyzed_scenarios.append(scenario)
        
        return analyzed_scenarios
    
    def _apply_changes(self, base_system: Dict, changes: Dict) -> Dict:
        """Apply scenario changes to base system"""
        modified = base_system.copy()
        
        for change_type, change_data in changes.items():
            if change_type == 'wire_gauge':
                for circuit_id, new_gauge in change_data.items():
                    for circuit in modified.get('circuits', []):
                        if circuit.get('id') == circuit_id:
                            circuit['wire_gauge'] = new_gauge
            
            elif change_type == 'battery_type':
                modified['battery_type'] = change_data
            
            elif change_type == 'add_devices':
                for circuit_id, device_count in change_data.items():
                    for circuit in modified.get('circuits', []):
                        if circuit.get('id') == circuit_id:
                            current_devices = circuit.get('devices', [])
                            new_devices = [f'NEW_DEV_{i}' for i in range(device_count)]
                            circuit['devices'] = current_devices + new_devices
        
        return modified
    
    def _predict_scenario_outcomes(self, base_system: Dict, modified_system: Dict) -> Dict[str, Any]:
        """Predict outcomes of scenario changes"""
        outcomes = {}
        
        # Voltage drop comparison
        base_circuits = base_system.get('circuits', [])
        modified_circuits = modified_system.get('circuits', [])
        
        voltage_improvements = []
        for base_circuit, mod_circuit in zip(base_circuits, modified_circuits):
            base_vd = self.voltage_predictor.predict_voltage_drop(base_circuit, 0)
            mod_vd = self.voltage_predictor.predict_voltage_drop(mod_circuit, 0)
            
            base_drop = base_vd['predictions']['year_0']['voltage_drop']
            mod_drop = mod_vd['predictions']['year_0']['voltage_drop']
            
            improvement = (base_drop - mod_drop) / base_drop * 100 if base_drop > 0 else 0
            voltage_improvements.append(improvement)
        
        outcomes['voltage_improvement_percent'] = sum(voltage_improvements) / len(voltage_improvements) if voltage_improvements else 0
        
        # Cost analysis
        outcomes['estimated_cost_change'] = self._estimate_cost_change(base_system, modified_system)
        
        # Performance impact
        outcomes['performance_score'] = self._calculate_performance_score(modified_system)
        
        return outcomes
    
    def _estimate_cost_change(self, base_system: Dict, modified_system: Dict) -> float:
        """Estimate cost change for scenario"""
        # Simplified cost estimation
        cost_change = 0.0
        
        # Wire cost changes
        base_circuits = base_system.get('circuits', [])
        mod_circuits = modified_system.get('circuits', [])
        
        for base_circuit, mod_circuit in zip(base_circuits, mod_circuits):
            base_gauge = base_circuit.get('wire_gauge', '18')
            mod_gauge = mod_circuit.get('wire_gauge', '18')
            
            if base_gauge != mod_gauge:
                cost_change += self.voltage_predictor._calculate_wire_cost_difference(
                    base_gauge, mod_gauge, base_circuit.get('length', 100)
                )
        
        return cost_change
    
    def _calculate_performance_score(self, system: Dict) -> float:
        """Calculate overall system performance score"""
        score = 100.0
        
        circuits = system.get('circuits', [])
        for circuit in circuits:
            utilization = len(circuit.get('devices', [])) / circuit.get('max_capacity', 159)
            if utilization > 0.9:
                score -= 10  # Penalty for over-utilization
            elif utilization < 0.3:
                score -= 5   # Penalty for under-utilization
        
        return max(0, score)

class EnhancedLiveCalculationsAI:
    """Main AI-enhanced live calculations engine"""
    
    def __init__(self):
        self.voltage_predictor = VoltageDropPredictor()
        self.battery_predictor = BatteryLifePredictor()
        self.circuit_optimizer = CircuitOptimizer()
        self.whatif_analyzer = WhatIfAnalyzer()
        
        self.calculation_history = []
        self.optimization_cache = {}
    
    def perform_enhanced_analysis(self, system_data: Dict) -> Dict[str, Any]:
        """Perform comprehensive AI-enhanced analysis"""
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'system_id': system_data.get('id', 'Unknown'),
            'predictions': {},
            'optimizations': [],
            'scenarios': [],
            'recommendations': []
        }
        
        # Voltage drop predictions
        circuits = system_data.get('circuits', [])
        for circuit in circuits:
            circuit_id = circuit.get('id', 'unknown')
            analysis_results['predictions'][f'{circuit_id}_voltage'] = self.voltage_predictor.predict_voltage_drop(circuit)
        
        # Battery life predictions
        battery_data = system_data.get('battery', {})
        if battery_data:
            usage_pattern = system_data.get('usage_pattern', {})
            analysis_results['predictions']['battery_life'] = self.battery_predictor.predict_battery_performance(
                battery_data, usage_pattern
            )
        
        # Optimization suggestions
        optimization_suggestions = []
        
        # Wire optimization
        for circuit in circuits:
            wire_suggestions = self.voltage_predictor.suggest_wire_optimization(circuit)
            optimization_suggestions.extend(wire_suggestions)
        
        # Circuit optimization
        circuit_suggestions = self.circuit_optimizer.analyze_circuit_loading(circuits)
        optimization_suggestions.extend(circuit_suggestions)
        
        analysis_results['optimizations'] = [s.to_dict() for s in optimization_suggestions]
        
        # Generate high-level recommendations
        analysis_results['recommendations'] = self._generate_recommendations(analysis_results)
        
        # Store in history
        self.calculation_history.append(analysis_results)
        
        return analysis_results
    
    def run_whatif_scenarios(self, system_data: Dict, scenarios: List[Dict]) -> List[Dict]:
        """Run what-if scenario analysis"""
        analyzed_scenarios = self.whatif_analyzer.analyze_scenarios(system_data, scenarios)
        return [s.to_dict() for s in analyzed_scenarios]
    
    def get_real_time_feedback(self, system_data: Dict, recent_change: Dict) -> Dict[str, Any]:
        """Provide real-time feedback on system changes"""
        feedback = {
            'change_impact': 'positive',
            'confidence': PredictionConfidence.MEDIUM.value,
            'immediate_effects': [],
            'long_term_predictions': [],
            'suggestions': []
        }
        
        # Quick analysis of the change
        if recent_change.get('type') == 'wire_gauge_change':
            circuit_id = recent_change.get('circuit_id')
            new_gauge = recent_change.get('new_gauge')
            
            # Find the affected circuit
            for circuit in system_data.get('circuits', []):
                if circuit.get('id') == circuit_id:
                    # Quick voltage drop calculation
                    old_prediction = self.voltage_predictor.predict_voltage_drop(circuit, 0)
                    
                    circuit['wire_gauge'] = new_gauge
                    new_prediction = self.voltage_predictor.predict_voltage_drop(circuit, 0)
                    
                    old_drop = old_prediction['predictions']['year_0']['voltage_drop']
                    new_drop = new_prediction['predictions']['year_0']['voltage_drop']
                    
                    improvement = (old_drop - new_drop) / old_drop * 100 if old_drop > 0 else 0
                    
                    effects_list = feedback['immediate_effects']
                    if isinstance(effects_list, list):
                        effects_list.append(f"Voltage drop reduced by {improvement:.1f}%")
                    feedback['change_impact'] = 'positive' if improvement > 0 else 'neutral'
                    feedback['confidence'] = PredictionConfidence.HIGH.value
                    
                    break
        
        return feedback
    
    def _generate_recommendations(self, analysis_results: Dict) -> List[str]:
        """Generate high-level recommendations based on analysis"""
        recommendations = []
        
        optimizations = analysis_results.get('optimizations', [])
        high_impact_optimizations = [opt for opt in optimizations if (opt.get('performance_gain') or 0) > 15]
        
        if high_impact_optimizations:
            recommendations.append(
                f"🚀 {len(high_impact_optimizations)} high-impact optimizations available"
            )
        
        # Check voltage drop predictions
        predictions = analysis_results.get('predictions', {})
        voltage_issues = []
        for key, prediction in predictions.items():
            if 'voltage' in key and prediction.get('trending') == 'degrading':
                voltage_issues.append(key)
        
        if voltage_issues:
            recommendations.append(
                f"⚠️ {len(voltage_issues)} circuits showing voltage degradation trends"
            )
        
        # Battery recommendations
        battery_prediction = predictions.get('battery_life', {})
        if battery_prediction:
            replacement_year = battery_prediction.get('replacement_timeline', {}).get('recommended_replacement_year', 5)
            if replacement_year <= 2:
                recommendations.append(f"🔋 Battery replacement recommended within {replacement_year} years")
        
        if not recommendations:
            recommendations.append("✅ System performance is optimal - no immediate actions needed")
        
        return recommendations

def demo_enhanced_calculations():
    """Demonstrate enhanced live calculations AI capabilities"""
    print("🧠 AutoFire Enhanced Live Calculations AI Demo")
    print("=" * 50)
    
    # Sample system data
    sample_system = {
        'id': 'SYSTEM_ENHANCED_TEST',
        'circuits': [
            {
                'id': 'SLC1',
                'wire_gauge': '18',
                'length': 150,
                'current': 0.8,
                'devices': ['SD001', 'SD002', 'SD003'],
                'max_capacity': 159
            },
            {
                'id': 'NAC1', 
                'wire_gauge': '14',
                'length': 200,
                'current': 2.2,
                'devices': ['STR001', 'STR002', 'HORN001'],
                'max_capacity': 20
            }
        ],
        'battery': {
            'type': 'sealed_lead_acid',
            'capacity_ah': 18,
            'avg_temperature_c': 25
        },
        'usage_pattern': {
            'standby_current_ma': 120,
            'alarm_current_a': 2.5
        }
    }
    
    # Create enhanced calculations engine
    calc_ai = EnhancedLiveCalculationsAI()
    
    # Perform enhanced analysis
    print("🔍 Performing Enhanced Analysis...")
    analysis = calc_ai.perform_enhanced_analysis(sample_system)
    
    print(f"\n📊 Analysis Results for {analysis['system_id']}:")
    print(f"Timestamp: {analysis['timestamp']}")
    print(f"Recommendations: {len(analysis['recommendations'])}")
    print(f"Optimizations Found: {len(analysis['optimizations'])}")
    
    print("\n💡 AI Recommendations:")
    for rec in analysis['recommendations']:
        print(f"   {rec}")
    
    print("\n🔧 Top Optimizations:")
    for opt in analysis['optimizations'][:3]:  # Show top 3
        print(f"   • {opt['title']}")
        print(f"     {opt['description']}")
        print(f"     Impact: {opt['impact']}")
        if opt.get('cost_savings'):
            print(f"     Savings: ${opt['cost_savings']:.2f}")
        print()
    
    # What-if scenarios
    print("🎯 What-If Scenario Analysis:")
    scenarios = [
        {
            'name': 'Upgrade Wire Gauge',
            'description': 'Upgrade SLC1 from 18 AWG to 14 AWG',
            'changes': {
                'wire_gauge': {'SLC1': '14'}
            }
        }
    ]
    
    scenario_results = calc_ai.run_whatif_scenarios(sample_system, scenarios)
    for scenario in scenario_results:
        print(f"   Scenario: {scenario['name']}")
        print(f"   Voltage Improvement: {scenario['predicted_outcomes']['voltage_improvement_percent']:.1f}%")
        print(f"   Cost Change: ${scenario['predicted_outcomes']['estimated_cost_change']:.2f}")
        print(f"   Performance Score: {scenario['predicted_outcomes']['performance_score']:.1f}")
    
    print("\n✅ Enhanced calculations AI demo completed!")

if __name__ == "__main__":
    demo_enhanced_calculations()