def ft_to_px(ft: float, px_per_ft: float) -> float:
    return float(ft) * float(px_per_ft)


def px_to_ft(px: float, px_per_ft: float) -> float:
    return float(px) / float(px_per_ft) if px_per_ft > 0 else 0.0


def fmt_ft_inches(ft: float) -> str:
    sign = "-" if ft < 0 else ""
    ft = abs(ft)
    whole = int(ft)
    inches = (ft - whole) * 12.0
    return f"{sign}{whole}'-{inches:.1f}\""
