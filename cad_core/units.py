from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

MM_PER_INCH = 25.4

# Global default tolerance for geometric comparisons
EPS: float = 1e-9


def mm_to_inch(mm: float) -> float:
    return mm / MM_PER_INCH


def inch_to_mm(inch: float) -> float:
    return inch * MM_PER_INCH


def almost_equal(a: float, b: float, tol: float = EPS) -> bool:
    return abs(a - b) <= tol


def clamp(x: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return hi if x > hi else lo if x < lo else x


def sgn(x: float, tol: float = EPS) -> int:
    if x > tol:
        return 1
    if x < -tol:
        return -1
    return 0


def round_tol(value: float, tol: float = 1e-6) -> float:
    if tol <= 0:
        return value
    # Try decimal quantization for decimal-friendly tolerances to avoid FP drift
    try:
        dval = Decimal(str(value))
        dtol = Decimal(str(tol))
        q = (dval / dtol).to_integral_value(rounding=ROUND_HALF_UP)
        return float(q * dtol)
    except Exception:
        return round(value / tol) * tol
