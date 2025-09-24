# Backend

Headless logic: loaders, schemas, configuration, and service layer.

Targets
- Own `db/loader.py` and future persistence.
- Provide clean APIs used by `frontend`.

DTOs and Serialization
- DTOs (e.g., `PointDTO`, `SegmentDTO`) define simple data contracts shared across layers.
- Serialization helpers (when present) convert DTOs to plain dicts suitable for JSON and back.
- Keep DTOs and serializers pure and free of side effects for easy testing.

