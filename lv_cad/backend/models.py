"""Parity copy of backend.models into lv_cad.backend."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PointDTO:
    x: float
    y: float


@dataclass(frozen=True)
class SegmentDTO:
    a: PointDTO
    b: PointDTO


@dataclass(frozen=True)
class CircleDTO:
    center: PointDTO
    r: float


@dataclass(frozen=True)
class FilletArcDTO:
    center: PointDTO
    r: float
    t1: PointDTO
    t2: PointDTO
