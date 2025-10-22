"""Placement rules helpers.

Minimal, safe helpers used by UI and tests. This module is intentionally
compact so it can be imported by many parts of the app and by the test
suite without side-effects.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class PlacementRule:
    coverage_sqft_per_device: float
    max_spacing_ft: float
    notes: list[str] = field(default_factory=list)


# A small set of conservative defaults used for quick calculations/tests.
DEFAULT_RULES: dict[str, PlacementRule] = {
    "smoke": PlacementRule(
        coverage_sqft_per_device=900.0, max_spacing_ft=30.0, notes=["NFPA typical"]
    ),
    "heat": PlacementRule(
        coverage_sqft_per_device=900.0, max_spacing_ft=50.0, notes=["NFPA typical"]
    ),
}


def get_effective_rule(
    category: str, overrides: dict[str, PlacementRule] | None = None
) -> PlacementRule:
    """Return the effective placement rule for a category, applying overrides.

    The returned object is a shallow copy so callers cannot mutate module defaults.
    """
    base = DEFAULT_RULES.get(category)
    if base is None:
        base = PlacementRule(coverage_sqft_per_device=900.0, max_spacing_ft=30.0, notes=["default"])
    if overrides and category in overrides:
        ov = overrides[category]
        return PlacementRule(ov.coverage_sqft_per_device, ov.max_spacing_ft, list(ov.notes))
    return PlacementRule(base.coverage_sqft_per_device, base.max_spacing_ft, list(base.notes))


def validate_spacing(points_ft: list[tuple[float, float]], max_spacing_ft: float) -> bool:
    """Return True if every point has at least one neighbor within max_spacing_ft."""
    if not points_ft:
        return True
    for i, p in enumerate(points_ft):
        found = False
        for j, q in enumerate(points_ft):
            if i == j:
                continue
            if math.hypot(p[0] - q[0], p[1] - q[1]) <= max_spacing_ft:
                found = True
                break
        if not found:
            return False
    return True


def estimate_required_devices(area_sqft: float, coverage_sqft_per_device: float) -> int:
    """Return ceil(area / coverage) or 0 if coverage is non-positive."""
    if coverage_sqft_per_device <= 0:
        return 0
    return int(math.ceil(area_sqft / coverage_sqft_per_device))
