import math
from typing import List, Dict, Any

# Constants (NFPA 72 related)
VOLTAGE_DROP_LIMIT_PERCENT = 20.0 # 20% voltage drop limit
BATTERY_STANDBY_HOURS = 24       # 24 hours standby
BATTERY_ALARM_MINUTES = 5        # 5 minutes alarm

# Wire resistance lookup (Ohms per 1000 feet, for copper wire at 20°C)
# This should ideally come from the wire_specs table
WIRE_RESISTANCE_PER_1000FT = {
    "18/2": 6.38,  # 18 AWG, 2 conductor
    "16/2": 4.01,  # 16 AWG, 2 conductor
    "14/2": 2.52,  # 14 AWG, 2 conductor
    "12/2": 1.59   # 12 AWG, 2 conductor
}

def calculate_voltage_drop(current_ma: float, wire_length_ft: float, wire_gauge: str) -> float:
    """Calculates voltage drop in volts for a given current, wire length, and gauge.
    Assumes a two-way path (out and back).
    """
    if wire_gauge not in WIRE_RESISTANCE_PER_1000FT:
        raise ValueError(f"Unknown wire gauge: {wire_gauge}")

    resistance_per_foot = WIRE_RESISTANCE_PER_1000FT[wire_gauge] / 1000.0
    total_resistance = resistance_per_foot * wire_length_ft * 2 # Two-way path
    voltage_drop = (current_ma / 1000.0) * total_resistance # Convert mA to Amps
    return voltage_drop

def calculate_battery_size(total_standby_current_ma: float, total_alarm_current_ma: float) -> float:
    """Calculates the required battery size in Amp-hours (Ah).
    Assumes 24 hours standby and 5 minutes alarm, as per NFPA 72.
    """
    # Convert minutes to hours for alarm current
    alarm_duration_hours = BATTERY_ALARM_MINUTES / 60.0

    # Calculate total Amp-hours
    standby_ah = (total_standby_current_ma / 1000.0) * BATTERY_STANDBY_HOURS
    alarm_ah = (total_alarm_current_ma / 1000.0) * alarm_duration_hours

    total_ah = standby_ah + alarm_ah
    return total_ah

def get_wire_resistance(gauge: str) -> float:
    """Retrieves wire resistance per 1000ft for a given gauge.
    In a real application, this would query the database.
    """
    return WIRE_RESISTANCE_PER_1000FT.get(gauge, 0.0)
