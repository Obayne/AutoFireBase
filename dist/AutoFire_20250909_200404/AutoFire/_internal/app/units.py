
import math

IN_PER_FT = 12.0

def ft_to_inches(ft: float) -> float:
    return ft * IN_PER_FT

def inches_to_ft(inches: float) -> float:
    return inches / IN_PER_FT

def px_to_ft(px: float, px_per_ft: float) -> float:
    return px / px_per_ft

def ft_to_px(ft: float, px_per_ft: float) -> float:
    return ft * px_per_ft

def fmt_ft_inches(ft_val: float) -> str:
    neg = ft_val < 0
    ft_val = abs(ft_val)
    whole_ft = int(ft_val)
    inches = round((ft_val - whole_ft) * 12.0, 2)
    return f"-{whole_ft}' {inches:.2f}\"" if neg else f"{whole_ft}' {inches:.2f}\""

def from_db_spherical(db_at_1m: float, target_db: float, px_per_ft: float) -> float:
    """Return radius in *pixels* using 20*log10(r/reference). Uses 1m≈3.28084ft ref."""
    if db_at_1m <= 0: return 0.0
    if target_db >= db_at_1m: return 0.0
    ratio = 10 ** ((db_at_1m - target_db) / 20.0)  # r @ 1m reference
    r_ft = ratio * 3.28084
    return r_ft * px_per_ft

def from_db_per_10ft(db_at_10ft: float, target_db: float, loss_per_10ft: float, px_per_ft: float) -> float:
    """Simple linear-per-10ft model (designer-style rule)."""
    if db_at_10ft <= 0: return 0.0
    if target_db >= db_at_10ft: return 0.0
    steps = (db_at_10ft - target_db) / max(loss_per_10ft, 0.1)
    r_ft = 10.0 * steps
    return r_ft * px_per_ft

def strobe_radius_from_cd_lux(candela: float, lux: float, px_per_ft: float) -> float:
    if candela <= 0 or lux <= 0: return 0.0
    r_m = math.sqrt(candela / lux)
    r_ft = r_m * 3.28084
    return r_ft * px_per_ft
