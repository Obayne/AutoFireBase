#!/usr/bin/env python3
"""
Test script for AutoFire battery calculations.
Demonstrates both simple and advanced battery calculation methods.
"""

import os
import sys

# Add the app directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from battery_calculator import BatteryCalculator, BatteryChemistry


def test_simple_battery_calculation():
    """Test simple battery calculation method."""
    print("=== Simple Battery Calculation Test ===")

    # Create calculator
    calc = BatteryCalculator()

    # Simple calculation parameters
    total_current = 2.5  # amps total system current
    backup_hours = 24  # hours
    safety_factor = 1.25

    # Calculate battery capacity
    result = calc.calculate_simple_battery_capacity(
        total_current_a=total_current, backup_hours=backup_hours, safety_factor=safety_factor
    )

    print(f"Total current: {result['total_current_a']} A")
    print(f"Backup hours: {result['backup_hours']} h")
    print(f"Safety factor: {result['safety_factor']}")
    print(f"Required capacity: {result['battery_capacity_ah']:.1f} Ah")
    print()


def test_advanced_battery_calculation():
    """Test advanced battery calculation with NFPA 72 compliance."""
    print("=== Advanced Battery Calculation Test (NFPA 72) ===")

    # Create calculator
    calc = BatteryCalculator()

    # Advanced calculation parameters
    standby_current = 0.15  # amps standby
    alarm_current = 2.1  # amps alarm
    standby_hours = 24  # hours
    alarm_hours = 0.5  # hours (30 minutes)
    battery_voltage = 24.0
    temperature_f = 86.0  # 30°C
    safety_factor = 1.25

    # Calculate advanced battery requirements
    result = calc.calculate_battery_capacity(
        standby_current_a=standby_current,
        alarm_current_a=alarm_current,
        standby_hours=standby_hours,
        alarm_hours=alarm_hours,
        battery_voltage=battery_voltage,
        battery_chemistry=BatteryChemistry.LEAD_ACID,
        temperature_f=temperature_f,
        safety_factor=safety_factor,
    )

    print(f"Battery voltage: {battery_voltage} V")
    print("Battery chemistry: Lead Acid")
    print(f"Temperature: {temperature_f}°F")
    print(f"Design margin: {safety_factor}x")
    print()
    print("Current requirements:")
    print(".3f")
    print(".3f")
    print()
    print("Time requirements:")
    print(f"Standby: {standby_hours} hours")
    print(f"Alarm: {alarm_hours} hours")
    print()
    print("Amp-hour calculations:")
    print(".1f")
    print(".1f")
    print(".1f")
    print()
    print("Adjustments:")
    print(".2f")
    print(".1f")
    print(".2f")
    print()
    print("Final requirements:")
    print(".1f")
    print()

    # Get battery recommendations
    recommendations = calc.get_battery_recommendations(
        result["battery_capacity_ah"], battery_voltage
    )
    print("Battery recommendations:")
    for rec in recommendations[:2]:  # Show top 2
        print(
            f"  {rec['configuration']} × {rec['battery_size_ah']}Ah = {rec['total_capacity_ah']:.0f}Ah total ({rec['utilization_percent']:.1f}% utilization)"
        )
    print()


def test_temperature_derating():
    """Test temperature derating effects on battery capacity."""
    print("=== Temperature Derating Test ===")

    calc = BatteryCalculator()

    temperatures_f = [32, 50, 68, 77, 86, 104]  # Fahrenheit (0°C, 10°C, 20°C, 25°C, 30°C, 40°C)

    print("Temperature derating factors for Lead-Acid batteries:")
    print("Temp (°F) | Temp (°C) | Derating Factor")
    print("-" * 35)

    for temp_f in temperatures_f:
        derating = calc._get_temperature_factor(temp_f)
        temp_c = (temp_f - 32) * 5 / 9
        print("6.0f")

    print()


def test_peukert_effect():
    """Test Peukert effect compensation."""
    print("=== Peukert Effect Test ===")

    calc = BatteryCalculator()

    # Test different discharge rates (C-rates)
    # C-rate = Current / Capacity, so 1C = 1 hour discharge, 0.1C = 10 hour discharge
    c_rates = [0.05, 0.1, 0.2, 0.5, 1.0]  # C-rates

    print("Peukert effect compensation for Lead-Acid batteries:")
    print("C-Rate | Peukert Factor | Effective Capacity Multiplier")
    print("-" * 55)

    peukert_k = calc.peukert_constants[BatteryChemistry.LEAD_ACID]  # 1.25 for lead-acid

    for c_rate in c_rates:
        # Peukert formula: Actual capacity = Rated capacity * (C-rate)^(1-k)
        # For higher discharge rates (higher C-rate), capacity decreases
        capacity_multiplier = c_rate ** (1 - peukert_k)
        print("4.2f")

    print()
    print("Note: Peukert effect shows that batteries discharge faster at high currents.")
    print("A battery rated for 100Ah at C/10 (10 hour rate) will deliver less")
    print("capacity when discharged at higher rates (shorter times).")
    print()


if __name__ == "__main__":
    print("AutoFire Battery Calculator Test Suite")
    print("=" * 50)
    print()

    try:
        test_simple_battery_calculation()
        test_advanced_battery_calculation()
        test_temperature_derating()
        test_peukert_effect()

        print("All tests completed successfully!")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()
