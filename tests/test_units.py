from app.units import ft_to_px, px_to_ft, fmt_ft_inches


def test_ft_px_roundtrip():
    scale = 96.0  # 96 px per ft
    feet = 12.5
    px = ft_to_px(feet, scale)
    assert px == feet * scale
    back = px_to_ft(px, scale)
    assert abs(back - feet) < 1e-9


def test_px_to_ft_zero_scale():
    assert px_to_ft(100.0, 0.0) == 0.0


def test_fmt_ft_inches_sign_and_precision():
    assert fmt_ft_inches(5.0) == "5'-0.0\""
    assert fmt_ft_inches(-1.25) == "-1'-3.0\""

