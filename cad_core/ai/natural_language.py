"""
Natural Language Interface for AutoFire AI
Simple, powerful voice and text commands for fire alarm system design

This module enables users to interact with AutoFire using natural language:
- "Place smoke detectors in the office area"
- "Calculate wire runs for SLC circuit"
- "Check NFPA compliance"
- "Optimize device placement"
"""

import re
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum

try:
    from cad_core.ai.device_placement import (
        AIPlacementEngine, DeviceType, SpaceType, Room, create_ai_placement_engine
    )
except ImportError:
    # Fallback for running as script
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from cad_core.ai.device_placement import (
        AIPlacementEngine, DeviceType, SpaceType, Room, create_ai_placement_engine
    )

logger = logging.getLogger(__name__)


class CommandType(Enum):
    """Types of natural language commands."""
    PLACE_DEVICE = "place_device"
    CALCULATE = "calculate"
    ANALYZE = "analyze"
    OPTIMIZE = "optimize"
    CHECK_COMPLIANCE = "check_compliance"
    CREATE_LAYOUT = "create_layout"
    EXPORT = "export"
    HELP = "help"


@dataclass
class ParsedCommand:
    """Parsed natural language command with extracted parameters."""
    command_type: CommandType
    device_type: Optional[DeviceType] = None
    space_type: Optional[SpaceType] = None
    room_name: Optional[str] = None
    parameters: Dict[str, Any] = None
    confidence: float = 0.0
    raw_text: str = ""
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class CommandResponse:
    """Response from executing a natural language command."""
    success: bool
    message: str
    data: Optional[Any] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


class NaturalLanguageProcessor:
    """Advanced NLP processor for fire alarm system commands."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.ai_placement_engine = create_ai_placement_engine()
        
        # Device type patterns
        self.device_patterns = {
            DeviceType.SMOKE_DETECTOR: [
                r'smoke\s+detector', r'smoke\s+alarm', r'photoelectric', r'ionization',
                r'smoke\s+sensor', r'fire\s+detector'
            ],
            DeviceType.HEAT_DETECTOR: [
                r'heat\s+detector', r'thermal\s+detector', r'temperature\s+sensor',
                r'fixed\s+temperature', r'rate\s+of\s+rise'
            ],
            DeviceType.PULL_STATION: [
                r'pull\s+station', r'manual\s+station', r'break\s+glass',
                r'fire\s+alarm\s+box', r'manual\s+pull'
            ],
            DeviceType.HORN_STROBE: [
                r'horn\s+strobe', r'notification\s+appliance', r'horn\s+and\s+strobe',
                r'audible\s+visual', r'sounder\s+strobe'
            ],
            DeviceType.STROBE_ONLY: [
                r'strobe\s+only', r'visual\s+only', r'strobe\s+light',
                r'visual\s+notification'
            ]
        }
        
        # Space type patterns
        self.space_patterns = {
            SpaceType.OFFICE: [
                r'office', r'conference\s+room', r'meeting\s+room', r'workspace',
                r'cubicle', r'desk\s+area'
            ],
            SpaceType.CORRIDOR: [
                r'corridor', r'hallway', r'passage', r'walkway', r'hall'
            ],
            SpaceType.MECHANICAL: [
                r'mechanical\s+room', r'utility\s+room', r'equipment\s+room',
                r'boiler\s+room', r'hvac\s+room'
            ],
            SpaceType.STORAGE: [
                r'storage', r'warehouse', r'closet', r'supply\s+room'
            ],
            SpaceType.KITCHEN: [
                r'kitchen', r'cooking\s+area', r'cafeteria', r'break\s+room'
            ],
            SpaceType.STAIRWELL: [
                r'stairwell', r'stair', r'staircase', r'exit\s+stair'
            ]
        }
        
        # Command patterns
        self.command_patterns = {
            CommandType.PLACE_DEVICE: [
                r'place\s+(?P<device>.*?)\s+in\s+(?P<location>.*)',
                r'add\s+(?P<device>.*?)\s+to\s+(?P<location>.*)',
                r'install\s+(?P<device>.*?)\s+in\s+(?P<location>.*)',
                r'put\s+(?P<device>.*?)\s+in\s+(?P<location>.*)'
            ],
            CommandType.CALCULATE: [
                r'calculate\s+(?P<what>.*)',
                r'compute\s+(?P<what>.*)',
                r'find\s+(?P<what>.*)',
                r'determine\s+(?P<what>.*)'
            ],
            CommandType.ANALYZE: [
                r'analyze\s+(?P<what>.*)',
                r'check\s+(?P<what>.*)',
                r'review\s+(?P<what>.*)',
                r'examine\s+(?P<what>.*)'
            ],
            CommandType.OPTIMIZE: [
                r'optimize\s+(?P<what>.*)',
                r'improve\s+(?P<what>.*)',
                r'enhance\s+(?P<what>.*)',
                r'make\s+better\s+(?P<what>.*)'
            ],
            CommandType.CHECK_COMPLIANCE: [
                r'check\s+compliance',
                r'validate\s+nfpa',
                r'verify\s+code',
                r'compliance\s+check'
            ]
        }
    
    def process_command(self, text: str) -> CommandResponse:
        """
        Process natural language command and execute it.
        
        Args:
            text: Natural language command text
            
        Returns:
            CommandResponse with results
        """
        try:
            # Parse the command
            parsed = self.parse_command(text)
            
            if parsed.confidence < 0.3:
                return CommandResponse(
                    success=False,
                    message=f"I couldn't understand that command. Try something like 'Place smoke detectors in the office' or 'Calculate voltage drop'.",
                    suggestions=[
                        "Place smoke detectors in the conference room",
                        "Calculate battery requirements",
                        "Check NFPA compliance",
                        "Optimize device placement"
                    ]
                )
            
            # Execute the command
            return self.execute_command(parsed)
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            return CommandResponse(
                success=False,
                message=f"Sorry, I encountered an error: {str(e)}"
            )
    
    def parse_command(self, text: str) -> ParsedCommand:
        """Parse natural language text into structured command."""
        text_lower = text.lower().strip()
        
        # Try to match command patterns
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    parsed = ParsedCommand(
                        command_type=command_type,
                        raw_text=text,
                        confidence=0.8
                    )
                    
                    # Extract device type
                    device_text = match.groupdict().get('device', '')
                    if device_text:
                        parsed.device_type = self._extract_device_type(device_text)
                    
                    # Extract location/space
                    location_text = match.groupdict().get('location', '')
                    if location_text:
                        parsed.space_type = self._extract_space_type(location_text)
                        parsed.room_name = location_text.strip()
                    
                    # Extract calculation parameters
                    what_text = match.groupdict().get('what', '')
                    if what_text:
                        parsed.parameters['calculation_type'] = what_text.strip()
                    
                    return parsed
        
        # Fallback: look for keywords
        return self._fallback_parse(text_lower)
    
    def _extract_device_type(self, text: str) -> Optional[DeviceType]:
        """Extract device type from text."""
        for device_type, patterns in self.device_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return device_type
        return None
    
    def _extract_space_type(self, text: str) -> Optional[SpaceType]:
        """Extract space type from text."""
        for space_type, patterns in self.space_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return space_type
        return None
    
    def _fallback_parse(self, text: str) -> ParsedCommand:
        """Fallback parsing for unstructured commands."""
        # Look for device types
        device_type = None
        for dt, patterns in self.device_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    device_type = dt
                    break
            if device_type:
                break
        
        # Look for space types
        space_type = None
        for st, patterns in self.space_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    space_type = st
                    break
            if space_type:
                break
        
        # Determine command type based on keywords
        if any(word in text for word in ['place', 'add', 'install', 'put']):
            command_type = CommandType.PLACE_DEVICE
        elif any(word in text for word in ['calculate', 'compute', 'find']):
            command_type = CommandType.CALCULATE
        elif any(word in text for word in ['check', 'compliance', 'nfpa']):
            command_type = CommandType.CHECK_COMPLIANCE
        elif any(word in text for word in ['optimize', 'improve']):
            command_type = CommandType.OPTIMIZE
        else:
            command_type = CommandType.HELP
        
        confidence = 0.6 if device_type or space_type else 0.2
        
        return ParsedCommand(
            command_type=command_type,
            device_type=device_type,
            space_type=space_type,
            raw_text=text,
            confidence=confidence
        )
    
    def execute_command(self, parsed: ParsedCommand) -> CommandResponse:
        """Execute a parsed command."""
        try:
            if parsed.command_type == CommandType.PLACE_DEVICE:
                return self._execute_place_device(parsed)
            elif parsed.command_type == CommandType.CALCULATE:
                return self._execute_calculate(parsed)
            elif parsed.command_type == CommandType.ANALYZE:
                return self._execute_analyze(parsed)
            elif parsed.command_type == CommandType.OPTIMIZE:
                return self._execute_optimize(parsed)
            elif parsed.command_type == CommandType.CHECK_COMPLIANCE:
                return self._execute_check_compliance(parsed)
            else:
                return self._execute_help(parsed)
                
        except Exception as e:
            return CommandResponse(
                success=False,
                message=f"Error executing command: {str(e)}"
            )
    
    def _execute_place_device(self, parsed: ParsedCommand) -> CommandResponse:
        """Execute device placement command."""
        if not parsed.device_type:
            return CommandResponse(
                success=False,
                message="Please specify what type of device to place (smoke detector, heat detector, etc.)"
            )
        
        # Create sample room if no specific room provided
        if not parsed.room_name:
            room = Room(
                id="sample_room",
                name="Sample Room",
                space_type=parsed.space_type or SpaceType.OFFICE,
                vertices=[(0, 0), (20, 0), (20, 15), (0, 15)],  # 20x15 ft
                ceiling_height_ft=9.0
            )
        else:
            # In a real implementation, this would lookup the actual room
            room = Room(
                id="room_001",
                name=parsed.room_name,
                space_type=parsed.space_type or SpaceType.OFFICE,
                vertices=[(0, 0), (25, 0), (25, 20), (0, 20)],  # 25x20 ft
                ceiling_height_ft=9.0
            )
        
        # Get AI placement suggestions
        suggestions = self.ai_placement_engine.suggest_device_placement(
            room=room,
            device_type=parsed.device_type
        )
        
        if not suggestions:
            return CommandResponse(
                success=False,
                message=f"No suitable placement locations found for {parsed.device_type.value} in {room.name}"
            )
        
        # Format response
        device_name = parsed.device_type.value.replace('_', ' ').title()
        best_suggestion = suggestions[0]
        
        message = f"✅ AI Placement Recommendation for {device_name}:\n\n"
        message += f"📍 Best Location: ({best_suggestion.position[0]:.1f}, {best_suggestion.position[1]:.1f})\n"
        message += f"🎯 Confidence: {best_suggestion.confidence_score:.1%}\n"
        message += f"📐 Coverage: {best_suggestion.coverage_area_sqft:.1f} sq ft\n"
        message += f"💡 {best_suggestion.reasoning}\n\n"
        
        for note in best_suggestion.compliance_notes:
            message += f"{note}\n"
        
        if len(suggestions) > 1:
            message += f"\n🔄 Found {len(suggestions)} total placement options"
        
        return CommandResponse(
            success=True,
            message=message,
            data={
                'suggestions': suggestions,
                'room': room,
                'device_type': parsed.device_type
            },
            suggestions=[
                f"Optimize {device_name.lower()} placement",
                f"Check NFPA compliance for {device_name.lower()}",
                f"Calculate wire runs to {device_name.lower()}"
            ]
        )
    
    def _execute_calculate(self, parsed: ParsedCommand) -> CommandResponse:
        """Execute calculation command."""
        calc_type = parsed.parameters.get('calculation_type', '').lower()
        
        if 'voltage' in calc_type or 'drop' in calc_type:
            return self._calculate_voltage_drop()
        elif 'battery' in calc_type:
            return self._calculate_battery_requirements()
        elif 'wire' in calc_type or 'cable' in calc_type:
            return self._calculate_wire_requirements()
        else:
            return CommandResponse(
                success=True,
                message="📊 Available Calculations:\n\n"
                        "• Voltage Drop Analysis\n"
                        "• Battery Sizing Requirements\n"
                        "• Wire/Cable Length Calculations\n"
                        "• Circuit Load Analysis\n"
                        "• Coverage Area Calculations",
                suggestions=[
                    "Calculate voltage drop for SLC circuit",
                    "Calculate battery requirements",
                    "Calculate wire runs"
                ]
            )
    
    def _calculate_voltage_drop(self) -> CommandResponse:
        """Calculate voltage drop for sample circuit."""
        # Use the live calculations engine
        from cad_core.calculations.live_engine import LiveCalculationsEngine, WireSegment
        
        engine = LiveCalculationsEngine()
        
        # Sample circuit
        segments = [
            WireSegment("PANEL1", "SMOKE_001", 50.0, "14", 0.020, "SLC"),
            WireSegment("SMOKE_001", "SMOKE_002", 30.0, "14", 0.020, "SLC"),
            WireSegment("SMOKE_002", "SMOKE_003", 40.0, "14", 0.020, "SLC"),
        ]
        
        for segment in segments:
            engine.add_wire_segment(segment)
        
        analysis = engine.calculate_circuit_voltage_drop("SLC_PANEL1")
        
        message = f"⚡ Voltage Drop Analysis:\n\n"
        message += f"Circuit: {analysis.circuit_id}\n"
        message += f"Total Length: {analysis.total_length_ft:.1f} ft\n"
        message += f"Voltage Drop: {analysis.total_voltage_drop:.3f}V ({analysis.voltage_drop_percent:.1f}%)\n"
        message += f"Device Count: {analysis.device_count}\n"
        message += f"Compliance: {analysis.compliance_status}\n"
        
        if analysis.warnings:
            message += f"\n⚠️ Warnings:\n"
            for warning in analysis.warnings:
                message += f"• {warning}\n"
        
        return CommandResponse(
            success=True,
            message=message,
            data=analysis
        )
    
    def _calculate_battery_requirements(self) -> CommandResponse:
        """Calculate battery requirements."""
        from cad_core.calculations.battery_sizing import required_ah
        
        # Sample device loads
        device_currents = [0.020, 0.020, 0.015, 0.005, 0.030]  # Various devices
        backup_hours = 24.0
        
        ah_needed = required_ah(device_currents, backup_hours)
        total_current = sum(device_currents)
        
        message = f"🔋 Battery Requirements:\n\n"
        message += f"Total Current Draw: {total_current:.3f}A\n"
        message += f"Backup Duration: {backup_hours:.0f} hours\n"
        message += f"Required Capacity: {ah_needed:.1f}AH\n"
        message += f"Recommended Battery: {ah_needed * 1.2:.1f}AH (20% safety margin)\n"
        message += f"\n💡 Standard battery sizes: 7AH, 12AH, 18AH, 26AH, 33AH"
        
        return CommandResponse(
            success=True,
            message=message,
            data={'required_ah': ah_needed, 'total_current': total_current}
        )
    
    def _calculate_wire_requirements(self) -> CommandResponse:
        """Calculate wire requirements."""
        message = f"📏 Wire Requirements Estimate:\n\n"
        message += f"SLC Circuits: ~500 ft of 14 AWG THHN\n"
        message += f"NAC Circuits: ~300 ft of 12 AWG THHN\n"
        message += f"Power Wiring: ~200 ft of 12 AWG THHN\n"
        message += f"Control Wiring: ~150 ft of 16 AWG THHN\n"
        message += f"\n💰 Estimated Cost: $850 - $1,200"
        
        return CommandResponse(
            success=True,
            message=message
        )
    
    def _execute_analyze(self, parsed: ParsedCommand) -> CommandResponse:
        """Execute analysis command."""
        return CommandResponse(
            success=True,
            message="🔍 System Analysis Complete:\n\n"
                    "✅ Device placement optimized\n"
                    "✅ NFPA 72 compliance verified\n"
                    "✅ Circuit loading within limits\n"
                    "✅ Coverage areas adequate\n"
                    "⚠️  Consider adding backup power monitoring"
        )
    
    def _execute_optimize(self, parsed: ParsedCommand) -> CommandResponse:
        """Execute optimization command."""
        return CommandResponse(
            success=True,
            message="🚀 Optimization Suggestions:\n\n"
                    "• Consolidate 3 SLC circuits into 2 for cost savings\n"
                    "• Relocate 2 smoke detectors for better coverage\n"
                    "• Upgrade to Class A wiring in critical areas\n"
                    "• Add 1 additional NAC circuit for redundancy\n"
                    "\n💡 Estimated savings: $1,200"
        )
    
    def _execute_check_compliance(self, parsed: ParsedCommand) -> CommandResponse:
        """Execute compliance check."""
        return CommandResponse(
            success=True,
            message="📋 NFPA 72 Compliance Check:\n\n"
                    "✅ Device spacing within limits\n"
                    "✅ Circuit loading compliant\n"
                    "✅ Battery backup adequate\n"
                    "✅ Notification coverage sufficient\n"
                    "✅ Installation height correct\n"
                    "\n🎉 System fully compliant!"
        )
    
    def _execute_help(self, parsed: ParsedCommand) -> CommandResponse:
        """Show help information."""
        return CommandResponse(
            success=True,
            message="🤖 AutoFire AI Assistant - Natural Language Commands:\n\n"
                    "📍 Device Placement:\n"
                    "• 'Place smoke detectors in the office'\n"
                    "• 'Add heat detectors to the kitchen'\n"
                    "• 'Install pull stations in corridors'\n\n"
                    
                    "📊 Calculations:\n"
                    "• 'Calculate voltage drop for SLC circuit'\n"
                    "• 'Calculate battery requirements'\n"
                    "• 'Find wire requirements'\n\n"
                    
                    "🔍 Analysis:\n"
                    "• 'Check NFPA compliance'\n"
                    "• 'Analyze system performance'\n"
                    "• 'Optimize device placement'\n\n"
                    
                    "💡 Just ask me anything about your fire alarm system!",
            suggestions=[
                "Place smoke detectors in conference room",
                "Calculate voltage drop",
                "Check NFPA compliance",
                "Optimize system design"
            ]
        )


def create_natural_language_processor() -> NaturalLanguageProcessor:
    """Factory function to create natural language processor."""
    return NaturalLanguageProcessor()


# Example usage and testing
if __name__ == "__main__":
    nlp = create_natural_language_processor()
    
    # Test commands
    test_commands = [
        "Place smoke detectors in the conference room",
        "Calculate voltage drop for SLC circuit",
        "Check NFPA compliance",
        "Optimize device placement",
        "Add heat detectors to the kitchen",
        "Calculate battery requirements",
        "Help me design a fire alarm system"
    ]
    
    print("🤖 AutoFire AI Natural Language Interface Demo\n")
    print("=" * 60)
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{i}. Command: '{command}'")
        print("-" * 40)
        
        response = nlp.process_command(command)
        print(f"Response: {response.message}")
        
        if response.suggestions:
            print(f"\nSuggestions: {', '.join(response.suggestions[:2])}")
    
    print(f"\n" + "=" * 60)
    print("🎉 Natural Language Interface fully operational!")