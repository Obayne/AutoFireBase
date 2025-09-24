# Data Model

This document describes the backend data transfer objects (DTOs), their serialized form, and basic compatibility guarantees.

## DTOs

- PointDTO: `{ "x": float, "y": float }`
- SegmentDTO: `{ "a": PointDTO, "b": PointDTO }`
- CircleDTO: `{ "center": PointDTO, "r": float }`
- FilletArcDTO: `{ "center": PointDTO, "r": float, "t1": PointDTO, "t2": PointDTO }`

## Schema Version

- Current: `0.1.0` (see `backend/schema_version.py`).
- Compatibility policy: same major version is considered compatible for loading.

## Serialization

Pure JSON objects with primitive number fields. Serializers live in `backend/serializers.py` and provide `to_dict_*` and `from_dict_*` helpers for each DTO.

