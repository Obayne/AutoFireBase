from __future__ import annotations

ABS_EPS: float = 1e-9
REL_EPS: float = 1e-7


def assert_close(a: float, b: float, *, abs_tol: float = ABS_EPS, rel_tol: float = REL_EPS) -> None:
    """Assert two floats are close under absolute/relative tolerances.

    Raises AssertionError if values differ more than allowed.
    """
    da = abs_val(a - b)
    if da <= abs_tol:
        return
    if da <= rel_tol * max(abs_val(a), abs_val(b)):
        return
    raise AssertionError(f"Not close: {a} vs {b} (abs={da}, abs_tol={abs_tol}, rel_tol={rel_tol})")


def abs_val(x: float) -> float:
    return x if x >= 0.0 else -x
