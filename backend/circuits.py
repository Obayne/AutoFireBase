"""Circuit calculations and summaries for AlarmForge.

Pure functions that can be tested without the GUI. The UI layer (Circuits Editor)
can call these helpers to compute voltage drop and battery sizing and to summarize
per-circuit status.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


# Ohms per 1000 ft for common copper wire gauges (approximate)
AWG_OHMS_PER_1000FT: dict[str, float] = {
    # Source: typical copper DC resistance at 20°C (ohms/1000 ft)
    "26": 41.00,
    "24": 25.67,
    "22": 16.14,
    "20": 10.15,
    "18": 6.385,
    "16": 4.016,
    "14": 2.525,
    "12": 1.588,
    "10": 0.999,
    "8": 0.628,
}


def ohms_per_1000ft(awg: str | int | None) -> float:
    if awg is None:
        return 10.0
    s = str(awg).strip()
    return AWG_OHMS_PER_1000FT.get(s, 10.0)


def loop_resistance_ohms(length_ft: float, awg: str | int | None) -> float:
    """Return round-trip resistance for a two-conductor loop of given length.

    R = (ohms/1000ft) * (2 * length_ft / 1000)
    """
    try:
        length = max(0.0, float(length_ft))
    except Exception:
        length = 0.0
    return ohms_per_1000ft(awg) * (2.0 * length / 1000.0)


def voltage_drop_percent(
    length_ft: float, current_a: float, awg: str | int | None, source_voltage: float = 24.0
) -> float:
    try:
        i = max(0.0, float(current_a))
    except Exception:
        i = 0.0
    r = loop_resistance_ohms(length_ft, awg)
    if source_voltage <= 0:
        return 0.0
    v_drop = i * r
    return max(0.0, (v_drop / float(source_voltage)) * 100.0)


def battery_capacity_ah(
    standby_hours: float,
    alarm_minutes: float,
    standby_current_a: float,
    alarm_current_a: float,
    derate: float = 1.25,
) -> float:
    try:
        s_h = max(0.0, float(standby_hours))
        a_m = max(0.0, float(alarm_minutes))
        i_s = max(0.0, float(standby_current_a))
        i_a = max(0.0, float(alarm_current_a))
        d = max(1.0, float(derate))
    except Exception:
        return 0.0
    ah = (s_h * i_s) + ((a_m / 60.0) * i_a)
    return round(d * ah, 4)


@dataclass
class CircuitEval:
    panel: str
    circuit_id: str
    circuit_type: str
    device_count: int
    length_ft: float
    gauge: str
    current_a: float
    drop_percent: float
    battery_ah: float
    status: str  # PASS/WARN/FAIL


DEFAULT_CURRENT_PER_DEVICE_A: dict[str, tuple[float, float]] = {
    # type -> (standby_current_A, alarm_current_A) per device
    "SLC": (0.005, 0.005),
    "NAC": (0.0, 0.06),
    "POWER": (0.0, 0.0),
}

# Typical strobe current at 24V by candela (approx, amps)
TYPICAL_STROBE_CURRENT_BY_CANDELA: dict[int, float] = {
    15: 0.08,
    30: 0.10,
    75: 0.18,
    95: 0.20,
    110: 0.23,
    135: 0.28,
    185: 0.35,
}


def _get_attr(it: Any, *names: str) -> Any:
    for n in names:
        if hasattr(it, n):
            try:
                return getattr(it, n)
            except Exception:
                continue
        # allow dict-like
        try:
            return it[n]  # type: ignore[index]
        except Exception:
            pass
    return None


def estimate_device_currents(device: Any) -> tuple[float, float]:
    """Estimate (standby_a, alarm_a) for a device from attributes and name.

    Priority:
    1) Explicit attributes if present: standby_current_a / alarm_current_a
    2) Device-spec database (backend/device_currents.json) by part_number/model/name
    3) Strobe candela mapping if available
    4) Keyword-based averages by device name/type
    5) Fallback small SLC draw
    """
    # 1) explicit
    s_exp = _get_attr(device, "standby_current_a", "standby_a", "standby_ma")
    a_exp = _get_attr(device, "alarm_current_a", "alarm_a", "alarm_ma")
    try:
        if s_exp is not None or a_exp is not None:
            s = float(s_exp) if s_exp is not None else 0.0
            a = float(a_exp) if a_exp is not None else 0.0
            # If values were in mA fields, convert to A
            if _get_attr(device, "standby_ma") is not None:
                s = s / 1000.0
            if _get_attr(device, "alarm_ma") is not None:
                a = a / 1000.0
            return max(0.0, s), max(0.0, a)
    except Exception:
        pass

    # 2) device-spec DB lookup
    try:
        table = _load_device_currents_table()
        candidates: list[str] = []
        for key_name in ("part_number", "model", "name"):
            v = _get_attr(device, key_name)
            if v:
                candidates.append(str(v).strip().lower())
        for key in candidates:
            if key in table:
                spec = table[key]
                s = float(spec.get("standby_current_a", spec.get("standby_ma", 0.0)))
                a = float(spec.get("alarm_current_a", spec.get("alarm_ma", 0.0)))
                # If values were in mA, convert to A
                if "standby_ma" in spec and "standby_current_a" not in spec:
                    s = s / 1000.0
                if "alarm_ma" in spec and "alarm_current_a" not in spec:
                    a = a / 1000.0
                return max(0.0, s), max(0.0, a)
    except Exception:
        # Robust against malformed JSON or unexpected data
        pass

    # 2) strobe by candela
    cand = _get_attr(device, "candela", "cd")
    if cand is None:
        # coverage params may hold candela
        cov = _get_attr(device, "coverage")
        if isinstance(cov, dict):
            cand = cov.get("params", {}).get("candela")
    try:
        if cand is not None:
            c = int(cand)
            if c in TYPICAL_STROBE_CURRENT_BY_CANDELA:
                return 0.0, TYPICAL_STROBE_CURRENT_BY_CANDELA[c]
    except Exception:
        pass

    # 3) by keywords
    name = str(_get_attr(device, "name", "device_type") or "").lower()
    pn = str(_get_attr(device, "part_number") or "").lower()
    text = f"{name} {pn}"
    if any(k in text for k in ("horn strobe", "horn/strobe", "p2r", "p2w", "hs")):
        return 0.0, 0.15  # average horn-strobe draw
    if "strobe" in text:
        return 0.0, 0.12
    if "horn" in text:
        return 0.0, 0.09
    if "speaker" in text:
        return 0.02, 0.06  # depends on tap
    if any(k in text for k in ("smoke", "sd", "detector")):
        return 0.005, 0.005
    if any(k in text for k in ("heat", "hd")):
        return 0.003, 0.003
    if any(k in text for k in ("pull", "bg-", "manual")):
        return 0.0, 0.0

    # 4) fallback small SLC draw
    return 0.004, 0.004


@lru_cache(maxsize=1)
def _load_device_currents_table() -> dict[str, dict[str, float]]:
    path = Path(__file__).with_name("device_currents.json")
    try:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                # normalize keys to lowercase
                return {str(k).lower(): v for k, v in (data or {}).items()}
    except Exception:
        pass
    return {}


def evaluate_circuit(
    device_count: int,
    circuit_type: str,
    length_ft: float,
    awg: str | int | None,
    source_voltage: float = 24.0,
    standby_hours: float = 24.0,
    alarm_minutes: float = 5.0,
    derate: float = 1.25,
) -> tuple[float, float, float, str]:
    """Return (current_a, drop_percent, battery_ah, status).

    Status thresholds (VD): PASS <=10%, WARN <=15%, FAIL otherwise.
    """
    standby_per, alarm_per = DEFAULT_CURRENT_PER_DEVICE_A.get(circuit_type, (0.0, 0.02))
    standby_current_a = device_count * standby_per
    alarm_current_a = device_count * alarm_per
    # Use alarm current for worst-case VD
    current_a = alarm_current_a
    drop = voltage_drop_percent(length_ft, current_a, awg, source_voltage)
    batt_ah = battery_capacity_ah(
        standby_hours,
        alarm_minutes,
        standby_current_a,
        alarm_current_a,
        derate,
    )
    if drop <= 10.0:
        status = "PASS"
    elif drop <= 15.0:
        status = "WARN"
    else:
        status = "FAIL"
    return current_a, drop, batt_ah, status


def aggregate_wire_by_circuit(wire_items: Iterable[Any]) -> dict[str, dict[str, Any]]:
    """Aggregate length and dominant gauge by circuit_id from wire-like items."""
    totals: dict[str, dict[str, Any]] = defaultdict(lambda: {"length_ft": 0.0, "gauge": ""})
    gauge_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for it in wire_items or []:
        cid = str(getattr(it, "circuit_id", "") or "").strip()
        if not cid:
            continue
        length = 0.0
        if hasattr(it, "length_ft"):
            try:
                length = float(getattr(it, "length_ft"))
            except Exception:
                length = 0.0
        elif hasattr(it, "length"):
            try:
                length = float(getattr(it, "length"))
            except Exception:
                length = 0.0
        totals[cid]["length_ft"] = float(totals[cid]["length_ft"]) + length
        g = str(getattr(it, "wire_gauge", getattr(it, "awg", getattr(it, "gauge", ""))))
        if g:
            gauge_counts[cid][g] += 1
    for cid, counts in gauge_counts.items():
        if counts:
            totals[cid]["gauge"] = counts.most_common(1)[0][0]
    return totals


def _iter_panels(items: Iterable[Any]) -> list[Any]:
    panels: list[Any] = []
    for it in items or []:
        if getattr(it, "panel_type", None) == "main" and hasattr(it, "circuits"):
            panels.append(it)
    return panels


def summarize_panel_circuits(
    device_items: Iterable[Any], wire_items: Iterable[Any]
) -> list[CircuitEval]:
    """Produce a per-circuit evaluation summary for all panels in device_items."""
    wire_map = aggregate_wire_by_circuit(wire_items)
    results: list[CircuitEval] = []
    for p in _iter_panels(device_items):
        panel_name = getattr(p, "name", "Panel")
        circuits = getattr(p, "circuits", {}) or {}
        for cid, cdata in circuits.items():
            ctype = str(cdata.get("type", "")).strip() or "SLC"
            devs = cdata.get("devices", []) or []
            agg = wire_map.get(str(cid), {"length_ft": 0.0, "gauge": "18"})
            length_ft = float(agg.get("length_ft", 0.0))
            gauge = str(agg.get("gauge", "18"))
            # Sum device currents using estimates
            total_standby = 0.0
            total_alarm = 0.0
            for d in devs:
                s, a = estimate_device_currents(d)
                total_standby += s
                total_alarm += a
            # If no devices or totals are zero, fall back to type-based estimate per device
            if (total_standby == 0.0 and total_alarm == 0.0) and devs:
                standby_per, alarm_per = DEFAULT_CURRENT_PER_DEVICE_A.get(ctype, (0.0, 0.02))
                total_standby = standby_per * len(devs)
                total_alarm = alarm_per * len(devs)

            # Use total_alarm for VD, both totals for battery sizing
            current_a = total_alarm
            drop = voltage_drop_percent(length_ft, current_a, gauge)
            batt_ah = battery_capacity_ah(24.0, 5.0, total_standby, total_alarm, 1.25)
            if drop <= 10.0:
                status = "PASS"
            elif drop <= 15.0:
                status = "WARN"
            else:
                status = "FAIL"
            results.append(
                CircuitEval(
                    panel=panel_name,
                    circuit_id=str(cid),
                    circuit_type=ctype,
                    device_count=len(devs),
                    length_ft=round(length_ft, 2),
                    gauge=gauge,
                    current_a=round(current_a, 4),
                    drop_percent=round(drop, 2),
                    battery_ah=round(batt_ah, 2),
                    status=status,
                )
            )
    return results
