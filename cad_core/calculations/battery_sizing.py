"""Battery sizing helpers.

This module provides a minimal helper to compute required amp-hours (AH)
given device currents and desired backup duration, including a simple derating.
"""

from collections.abc import Iterable


def required_ah(
    device_currents_a: Iterable[float], backup_hours: float, derate: float = 0.8
) -> float:
    """Compute required battery AH.

    Args:
        device_currents_a: iterable of device current draws (amps)
        backup_hours: required backup duration in hours
        derate: battery usable fraction (default 0.8)

    Returns:
        Required AH (float)
    """
    total_current = sum(float(i) for i in device_currents_a)
    if backup_hours <= 0:
        raise ValueError("backup_hours must be > 0")
    if derate <= 0 or derate > 1:
        raise ValueError("derate must be between 0 and 1")
    ah = (total_current * float(backup_hours)) / float(derate)
    return ah
