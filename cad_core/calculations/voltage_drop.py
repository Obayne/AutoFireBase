"""Simple voltage drop calculator for a circuit segment.

Function provided is intentionally minimal and well-tested.
"""

from collections.abc import Iterable


def voltage_drop_segment(current_a: float, resistance_ohm: float) -> float:
    """Compute voltage drop V = I * R for a segment.

    Args:
        current_a: current in amperes
        resistance_ohm: resistance in ohms

    Returns:
        Voltage drop in volts (float)
    """
    return float(current_a) * float(resistance_ohm)


def total_voltage_drop(segments: Iterable[tuple[float, float]]) -> float:
    """Compute total voltage drop for a series of segments.

    Each segment is a tuple (current_a, resistance_ohm). Returns sum of drops.
    """
    total = 0.0
    for current, resistance in segments:
        total += voltage_drop_segment(current, resistance)
    return total
