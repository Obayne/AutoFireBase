"""Minimal conduit fill calculator.

This is a small, dependency-free utility that approximates conduit fill based on
AWG diameters and a handful of common EMT sizes. Intended as a foundation for
UI labels and later NEC table expansion.

Assumptions:
- Uses bare conductor AWG diameters for area (ignores insulation thickness)
- Approximates internal area for EMT sizes from NEC tables (rounded)
- Default max fill limit of 40% for a bundle (typical multi-conductor rule)

All values are in inches / square inches.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi
from typing import Dict, Tuple


@dataclass(frozen=True)
class ConduitSpec:
    kind: str  # e.g., "EMT"
    trade_size: str  # e.g., "3/4"
    internal_area_in2: float
    max_fill_pct: float = 40.0


# Approximate internal areas for EMT (in^2)
_EMT_AREAS_IN2: Dict[str, float] = {
    "1/2": 0.304,
    "3/4": 0.533,
    "1": 0.864,
    "1-1/4": 1.496,
    "1-1/2": 2.036,
}

# Bare AWG diameters in inches (approximate)
# Source: standard AWG table (rounded to 4 decimals)
_AWG_DIAMETER_IN: Dict[int, float] = {
    10: 0.1019,
    12: 0.0808,
    14: 0.0641,
    16: 0.0508,
    18: 0.0403,
    20: 0.0320,
}


def awg_area_in2(awg: int) -> float:
    d = _AWG_DIAMETER_IN.get(awg)
    if d is None:
        raise ValueError(f"Unsupported AWG: {awg}")
    return pi * (d / 2) ** 2


def get_conduit_spec(
    kind: str, trade_size: str, *, max_fill_pct: float | None = None
) -> ConduitSpec:
    kind_u = kind.upper()
    if kind_u == "EMT":
        area = _EMT_AREAS_IN2.get(trade_size)
        if area is None:
            raise ValueError(f"Unsupported EMT size: {trade_size}")
        return ConduitSpec("EMT", trade_size, area, max_fill_pct or 40.0)
    raise ValueError(f"Unsupported conduit kind: {kind}")


def compute_fill_pct(kind: str, trade_size: str, wires: Dict[int, int]) -> Tuple[float, bool]:
    """Compute fill percent and pass/fail boolean by limit.

    Parameters
    - kind: conduit kind (e.g., 'EMT')
    - trade_size: e.g., '3/4'
    - wires: mapping of AWG -> count

    Returns (fill_percent, is_within_limit)
    """
    spec = get_conduit_spec(kind, trade_size)

    total_area = 0.0
    for awg, count in wires.items():
        total_area += awg_area_in2(awg) * max(0, int(count))

    fill_pct = (total_area / spec.internal_area_in2) * 100.0 if spec.internal_area_in2 > 0 else 0.0
    return fill_pct, fill_pct <= spec.max_fill_pct


__all__ = [
    "ConduitSpec",
    "get_conduit_spec",
    "awg_area_in2",
    "compute_fill_pct",
]
