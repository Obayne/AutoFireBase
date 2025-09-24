Title: feat(frontend): add env-gated dev hook to register ops tools

Summary
- Adds an environment-driven hook in `frontend/__init__.py` that registers passive ops tools when `FRONTEND_OPS_TOOLS` is set.
- Keeps UI unchanged while enabling quick, opt-in discovery of ops tools in dev builds.

Changes
- Update: `frontend/__init__.py` (gated call to `frontend.integration.register_ops_tools`).
- New: `tests/frontend/test_dev_hooks.py`.

Test Plan
- `ruff check frontend/__init__.py tests/frontend/test_dev_hooks.py`
- `black --check frontend/__init__.py tests/frontend/test_dev_hooks.py`
- `pytest -q tests/frontend/test_dev_hooks.py` (passes)

Notes
- Hook is safe and ignored unless the env var is set.