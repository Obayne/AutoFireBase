Task: Docs + Backend – Data model and schema version

Scope
- Author `docs/DATA_MODEL.md` describing DTOs, entities, and relationships.
- Add `backend/schema_version.py` with `CURRENT_VERSION = "0.1.0"` and helpers.

Details
- Document serialization format and compatibility policy.
- Provide `get_version()` and `is_compatible(ver: str) -> bool` for loaders.
- Include unit tests in `tests/backend/test_schema_version.py`.

Acceptance
- Docs build/read cleanly; tests pass.
- `ruff` and `black --check` pass.

Branch
- `docs/data-model-and-schema-version`

