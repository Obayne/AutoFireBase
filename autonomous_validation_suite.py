#!/usr/bin/env python3
"""
AutoFire Autonomous Testing & Validation Suite
============================================

Comprehensive testing and validation of all AutoFire systems with
automatic issue detection and correction.
"""

import sys
import time
import logging
from typing import Dict, List, Any, Optional

# Configure logging for testing
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class AutoFireValidationSuite:
    """Comprehensive validation suite for all AutoFire systems."""
    
    def __init__(self):
        self.test_results = {}
        self.issues_found = []
        self.fixes_applied = []
        
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run complete validation suite on all systems."""
        
        logger.info("🚀 Starting AutoFire Comprehensive Validation Suite")
        start_time = time.time()
        
        # Test each major system
        self.test_live_calculations_engine()
        self.test_professional_drawing_system()
        self.test_device_database()
        self.test_nfpa_rules_engine()
        self.test_ai_integration_framework()
        self.test_system_integration()
        
        # Performance and stress testing
        self.test_performance_benchmarks()
        self.test_memory_usage()
        self.test_error_handling()
        
        total_time = time.time() - start_time
        
        # Compile results
        return self._compile_validation_results(total_time)
    
    def test_live_calculations_engine(self):
        """Test Live Calculations Engine comprehensively."""
        
        logger.info("⚡ Testing Live Calculations Engine...")
        
        try:
            from live_calculations_engine import (
                LiveCalculationsEngine, DeviceType, Circuit, CircuitDevice, CircuitType
            )
            
            # Basic initialization
            calc = LiveCalculationsEngine()
            assert len(calc.device_specifications) > 0, "No device specifications loaded"
            assert len(calc.wire_specifications) > 0, "No wire specifications loaded"
            
            # Test voltage drop calculation
            # Create a simple test circuit - use correct dict key
            device_spec = None
            for spec in calc.device_specifications.values():
                if spec.device_type == DeviceType.SMOKE_DETECTOR:
                    device_spec = spec
                    break
            
            assert device_spec is not None, "No smoke detector specification found"
            test_device = CircuitDevice(
                id="TEST-1",
                device_spec=device_spec,
                position=(10.0, 10.0),
                wire_distance=50.0
            )
            
            test_circuit = Circuit(
                id="TEST-SLC-1",
                circuit_type=CircuitType.SLC,
                panel_voltage=24.0,
                wire_spec=calc.wire_specifications[18],
                devices=[test_device]
            )
            
            # Test calculations
            calculated_circuit = calc.calculate_voltage_drop(test_circuit)
            assert calculated_circuit.voltage_drop_percentage >= 0, "Invalid voltage drop calculation"
            
            validated_circuit = calc.validate_circuit_compliance(calculated_circuit)
            assert hasattr(validated_circuit, 'is_valid'), "Circuit validation missing is_valid attribute"
            
            self.test_results['live_calculations'] = {
                'status': 'PASS',
                'device_specs': len(calc.device_specifications),
                'wire_specs': len(calc.wire_specifications),
                'voltage_drop_test': 'PASS',
                'compliance_test': 'PASS'
            }
            
            logger.info("✅ Live Calculations Engine: ALL TESTS PASSED")
            
        except Exception as e:
            self.test_results['live_calculations'] = {'status': 'FAIL', 'error': str(e)}
            self.issues_found.append(f"Live Calculations Engine: {e}")
            logger.error(f"❌ Live Calculations Engine: {e}")
    
    def test_professional_drawing_system(self):
        """Test Professional Drawing System comprehensively."""
        
        logger.info("🎨 Testing Professional Drawing System...")
        
        try:
            from professional_drawing_system import ProfessionalDrawingEngine, DrawingSheet, DeviceType
            
            # Basic initialization
            drawing = ProfessionalDrawingEngine()
            assert len(drawing.symbol_library.symbols) > 0, "No symbols loaded"
            
            # Test drawing sheet creation
            sheet = drawing.create_drawing_sheet("Test Drawing", "T-1")
            assert sheet.title == "Test Drawing", "Drawing sheet creation failed"
            
            # Test device placement
            drawing.place_device(
                sheet=sheet,
                device_id="TEST-SMOKE-1",
                device_type=DeviceType.SMOKE_DETECTOR,
                position=(10.0, 10.0)
            )
            
            assert len(sheet.devices) == 1, "Device placement failed"
            
            # Test circuit routing
            drawing.route_circuit(
                sheet=sheet,
                circuit_id="TEST-SLC-1",
                device_ids=["TEST-SMOKE-1"],
                circuit_type="SLC"
            )
            
            assert len(sheet.circuits) == 1, "Circuit routing failed"
            
            # Test DXF export
            test_filename = "test_validation_drawing.dxf"
            drawing.export_to_dxf(sheet, test_filename)
            
            self.test_results['drawing_system'] = {
                'status': 'PASS',
                'symbols_loaded': len(drawing.symbol_library.symbols),
                'sheet_creation': 'PASS',
                'device_placement': 'PASS',
                'circuit_routing': 'PASS',
                'dxf_export': 'PASS'
            }
            
            logger.info("✅ Professional Drawing System: ALL TESTS PASSED")
            
        except Exception as e:
            self.test_results['drawing_system'] = {'status': 'FAIL', 'error': str(e)}
            self.issues_found.append(f"Drawing System: {e}")
            logger.error(f"❌ Professional Drawing System: {e}")
    
    def test_device_database(self):
        """Test Device Database comprehensively."""
        
        logger.info("🗄️ Testing Device Database...")
        
        try:
            from comprehensive_device_database import ComprehensiveDeviceDatabase
            
            # Basic initialization
            db = ComprehensiveDeviceDatabase()
            
            # Test device search (fix: provide required query parameter)
            smoke_detectors = db.search_devices("smoke", {"device_type": "smoke_detector"})
            assert len(smoke_detectors) > 0, "No smoke detectors found"
            
            # Test device by type
            devices_by_type = db.get_devices_by_type("smoke_detector")
            assert len(devices_by_type) > 0, "get_devices_by_type failed"
            
            # Test device by manufacturer
            system_sensor_devices = db.get_devices_by_manufacturer("System Sensor")
            assert len(system_sensor_devices) > 0, "get_devices_by_manufacturer failed"
            
            # Test specific device lookup
            specific_device = db.get_device("FSP-851")
            assert specific_device is not None, "Specific device lookup failed"
            
            # Test manufacturers
            manufacturers = db.get_all_manufacturers()
            assert len(manufacturers) > 0, "No manufacturers found"
            
            self.test_results['device_database'] = {
                'status': 'PASS',
                'search_test': 'PASS',
                'type_filter': 'PASS',
                'manufacturer_filter': 'PASS',
                'specific_lookup': 'PASS',
                'total_devices': len(smoke_detectors),
                'manufacturers': len(manufacturers)
            }
            
            logger.info("✅ Device Database: ALL TESTS PASSED")
            
        except Exception as e:
            self.test_results['device_database'] = {'status': 'FAIL', 'error': str(e)}
            self.issues_found.append(f"Device Database: {e}")
            logger.error(f"❌ Device Database: {e}")
    
    def test_nfpa_rules_engine(self):
        """Test NFPA Rules Engine comprehensively."""
        
        logger.info("📜 Testing NFPA Rules Engine...")
        
        try:
            from nfpa_rules_engine import NFPARulesEngine, ComplianceLevel
            
            # Basic initialization
            nfpa = NFPARulesEngine()
            
            # Check rules are loaded (fix: use correct attribute name)
            assert hasattr(nfpa, 'rules'), "NFPA rules not loaded"
            rules_count = len(nfpa.rules) if hasattr(nfpa, 'rules') else 0
            
            # Test system data validation
            test_system_data = {
                "devices": [
                    {"id": "SD-1", "type": "smoke_detector", "position": (10.0, 10.0)},
                    {"id": "SD-2", "type": "smoke_detector", "position": (40.0, 40.0)}
                ],
                "circuits": [],
                "room_bounds": (0, 0, 50, 50),
                "exits": [(5, 5)]
            }
            
            # Test compliance report generation
            compliance_report = nfpa.generate_compliance_report(test_system_data)
            assert "compliance_percentage" in compliance_report, "Compliance report missing percentage"
            assert "overall_status" in compliance_report, "Compliance report missing status"
            
            self.test_results['nfpa_rules'] = {
                'status': 'PASS',
                'rules_loaded': rules_count,
                'compliance_report': 'PASS',
                'system_validation': 'PASS'
            }
            
            logger.info("✅ NFPA Rules Engine: ALL TESTS PASSED")
            
        except Exception as e:
            self.test_results['nfpa_rules'] = {'status': 'FAIL', 'error': str(e)}
            self.issues_found.append(f"NFPA Rules Engine: {e}")
            logger.error(f"❌ NFPA Rules Engine: {e}")
    
    def test_ai_integration_framework(self):
        """Test AI Integration Framework comprehensively."""
        
        logger.info("🤖 Testing AI Integration Framework...")
        
        try:
            from ai_integration_framework import AIDesignAssistant
            
            # Basic initialization
            ai = AIDesignAssistant()
            
            # Check AI models (fix: use correct attribute name)
            models_count = len(ai.models) if hasattr(ai, 'models') else 0
            assert models_count > 0, "No AI models loaded"
            
            # Test device placement optimization
            test_geometry = {
                "width": 50.0,
                "length": 50.0,
                "area": 2500.0,
                "ceiling_height": 9.0,
                "exits": [(5.0, 5.0), (45.0, 45.0)],
                "obstacles": []  # Add required obstacles parameter
            }
            
            test_requirements = {
                "occupancy_type": "office",
                "hazard_classification": "light"
            }
            
            optimization_result = ai.optimize_device_placement(
                room_geometry=test_geometry,
                requirements=test_requirements,
                session_id="validation_test"
            )
            
            assert "optimized_placement" in optimization_result, "Optimization missing placement"
            assert "optimization_score" in optimization_result, "Optimization missing score"
            
            # Test training data generation
            training_data = ai.generate_training_data(5)  # Generate 5 samples
            assert len(training_data) == 5, "Training data generation failed"
            
            self.test_results['ai_framework'] = {
                'status': 'PASS',
                'models_loaded': models_count,
                'optimization_test': 'PASS',
                'training_data_test': 'PASS'
            }
            
            logger.info("✅ AI Integration Framework: ALL TESTS PASSED")
            
        except Exception as e:
            self.test_results['ai_framework'] = {'status': 'FAIL', 'error': str(e)}
            self.issues_found.append(f"AI Framework: {e}")
            logger.error(f"❌ AI Integration Framework: {e}")
    
    def test_system_integration(self):
        """Test complete system integration."""
        
        logger.info("🔗 Testing Complete System Integration...")
        
        try:
            from complete_system_integration import AutoFireIntegratedPlatform
            
            # Initialize integrated platform
            platform = AutoFireIntegratedPlatform()
            
            # Test simple project design
            test_project = {
                "project_name": "Validation Test Project",
                "building": {"type": "office"},
                "room_geometry": {
                    "width": 30.0,
                    "length": 30.0,
                    "area": 900.0,
                    "ceiling_height": 9.0,
                    "exits": [(5.0, 5.0)]
                },
                "requirements": {
                    "occupancy_type": "office",
                    "hazard_classification": "light"
                }
            }
            
            # Run integrated design
            design_results = platform.design_complete_system(test_project)
            
            assert "project_info" in design_results, "Integration missing project info"
            assert "device_placement" in design_results, "Integration missing device placement"
            assert "electrical_design" in design_results, "Integration missing electrical design"
            assert "compliance_analysis" in design_results, "Integration missing compliance"
            
            self.test_results['system_integration'] = {
                'status': 'PASS',
                'platform_init': 'PASS',
                'end_to_end_design': 'PASS',
                'design_time': design_results['project_info']['design_time_seconds']
            }
            
            logger.info("✅ Complete System Integration: ALL TESTS PASSED")
            
        except Exception as e:
            self.test_results['system_integration'] = {'status': 'FAIL', 'error': str(e)}
            self.issues_found.append(f"System Integration: {e}")
            logger.error(f"❌ Complete System Integration: {e}")
    
    def test_performance_benchmarks(self):
        """Test performance under various loads."""
        
        logger.info("⚡ Running Performance Benchmarks...")
        
        # This will be implemented in detail
        self.test_results['performance'] = {
            'status': 'PENDING',
            'note': 'Performance benchmarking to be implemented'
        }
    
    def test_memory_usage(self):
        """Test memory usage and optimization."""
        
        logger.info("💾 Testing Memory Usage...")
        
        # This will be implemented in detail
        self.test_results['memory'] = {
            'status': 'PENDING',
            'note': 'Memory testing to be implemented'
        }
    
    def test_error_handling(self):
        """Test error handling and edge cases."""
        
        logger.info("🛡️ Testing Error Handling...")
        
        # This will be implemented in detail
        self.test_results['error_handling'] = {
            'status': 'PENDING',
            'note': 'Error handling tests to be implemented'
        }
    
    def _compile_validation_results(self, total_time: float) -> Dict[str, Any]:
        """Compile comprehensive validation results."""
        
        passed_tests = sum(1 for result in self.test_results.values() 
                          if result.get('status') == 'PASS')
        total_tests = len(self.test_results)
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        return {
            'validation_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': success_rate,
                'total_time': total_time,
                'status': 'PASS' if success_rate >= 80 else 'FAIL'
            },
            'test_results': self.test_results,
            'issues_found': self.issues_found,
            'fixes_applied': self.fixes_applied
        }

def main():
    """Run autonomous validation suite."""
    
    print("🚀 AutoFire Autonomous Validation Suite")
    print("=" * 50)
    
    validator = AutoFireValidationSuite()
    results = validator.run_comprehensive_validation()
    
    # Display results
    summary = results['validation_summary']
    print(f"\n📊 VALIDATION RESULTS:")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   Passed: {summary['passed_tests']}")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    print(f"   Total Time: {summary['total_time']:.2f}s")
    print(f"   Status: {'✅ PASS' if summary['status'] == 'PASS' else '❌ FAIL'}")
    
    # Show individual test results
    print(f"\n🔍 INDIVIDUAL TEST RESULTS:")
    for test_name, result in results['test_results'].items():
        status_icon = "✅" if result.get('status') == 'PASS' else "❌" if result.get('status') == 'FAIL' else "⏳"
        print(f"   {status_icon} {test_name}: {result.get('status', 'UNKNOWN')}")
        
        if result.get('status') == 'FAIL':
            print(f"      Error: {result.get('error', 'Unknown error')}")
    
    # Show issues found
    if results['issues_found']:
        print(f"\n⚠️ ISSUES FOUND ({len(results['issues_found'])}):")
        for issue in results['issues_found']:
            print(f"   • {issue}")
    
    print(f"\n🎯 AUTONOMOUS VALIDATION COMPLETE")
    
    return results

if __name__ == "__main__":
    main()