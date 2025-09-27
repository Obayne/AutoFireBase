"""
Coverage models and helpers for sound and visual devices.

Currently includes a simple inverse-square speaker level model:
  L(r) = L_ref - 20 * log10(r / r_ref)

Where:
- L_ref is the sound pressure level (dB) measured at reference distance r_ref (ft).
- L(r) is the level at distance r (ft).

Functions here are pure and unit-tested. Values are in feet unless stated.
"""

from __future__ import annotations

import math


def db_at_distance(l_ref_db: float, r_ref_ft: float, r_ft: float) -> float:
    """Compute dB level at distance ``r_ft`` using inverse-square law.

    Args:
        l_ref_db: Level in dB at the reference distance ``r_ref_ft``.
        r_ref_ft: Reference distance in feet (must be > 0).
        r_ft: Target distance in feet (must be > 0).

    Returns:
        The sound level in dB at distance ``r_ft``.

    Raises:
        ValueError: If ``r_ref_ft`` <= 0 or ``r_ft`` <= 0.
    """
    if r_ref_ft <= 0 or r_ft <= 0:
        raise ValueError("Distances must be positive and non-zero")
    return l_ref_db - 20.0 * math.log10(r_ft / r_ref_ft)


def radius_for_target_db(
    l_ref_db: float,
    target_db: float,
    r_ref_ft: float = 10.0,
    *,
    min_radius_ft: float = 0.1,
    max_radius_ft: float = 1_000.0,
) -> float:
    """Compute radius (ft) achieving ``target_db`` given ``l_ref_db`` at ``r_ref_ft``.

    Uses the inverse of the inverse-square law:
        r = r_ref * 10 ** ((L_ref - L_target) / 20)

    Clamps the result to ``[min_radius_ft, max_radius_ft]``.

    Args:
        l_ref_db: Level in dB at reference distance ``r_ref_ft``.
        target_db: Desired level in dB at the computed radius.
        r_ref_ft: Reference distance in feet (default 10 ft).
        min_radius_ft: Lower clamp for the radius (ft), default 0.1.
        max_radius_ft: Upper clamp for the radius (ft), default 1000.

    Returns:
        Radius in feet to meet or exceed ``target_db``.

    Raises:
        ValueError: If ``r_ref_ft`` <= 0 or clamps are invalid.
    """
    if r_ref_ft <= 0:
        raise ValueError("Reference distance must be positive and non-zero")
    if not (0 < min_radius_ft <= max_radius_ft):
        raise ValueError("Invalid radius clamps")

    # Solve r from: target_db = l_ref_db - 20*log10(r/r_ref_ft)
    # => r = r_ref_ft * 10 ** ((l_ref_db - target_db) / 20)
    exponent = (l_ref_db - target_db) / 20.0
    r = r_ref_ft * (10.0**exponent)

    # Clamp to bounds to avoid degenerate UI states
    if r < min_radius_ft:
        return min_radius_ft
    if r > max_radius_ft:
        return max_radius_ft
    return r


__all__ = ["db_at_distance", "radius_for_target_db"]
