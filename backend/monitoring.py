"""
Lightweight monitoring hooks (logging + optional Sentry).

Initialize once per process. Controlled by env:
  - SENTRY_DSN: if set, enables Sentry SDK
  - SENTRY_ENVIRONMENT: environment tag (default: AUTOFIRE_ENV or 'production')
"""

from __future__ import annotations

import logging
import os
from typing import Any

_initialized = False


def init_monitoring() -> None:
    global _initialized
    if _initialized:
        return

    # Basic logging setup (no-op if already configured)
    logging.basicConfig(level=logging.INFO)

    dsn = os.getenv("SENTRY_DSN")
    if dsn:
        try:
            import sentry_sdk  # type: ignore

            sentry_sdk.init(
                dsn=dsn,
                environment=os.getenv("SENTRY_ENVIRONMENT")
                or os.getenv("AUTOFIRE_ENV")
                or "production",
                traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
            )
            logging.getLogger(__name__).info("Sentry monitoring initialized")
        except Exception as e:  # pragma: no cover
            logging.getLogger(__name__).warning(f"Sentry init failed: {e}")

    _initialized = True


def capture_exception(exc: BaseException, context: dict[str, Any] | None = None) -> None:
    """Capture exception if Sentry is active; otherwise log it."""
    if os.getenv("SENTRY_DSN"):
        try:
            import sentry_sdk  # type: ignore

            with sentry_sdk.push_scope() as scope:  # type: ignore[attr-defined]
                for k, v in (context or {}).items():
                    scope.set_extra(k, v)
                sentry_sdk.capture_exception(exc)
            return
        except Exception:  # pragma: no cover
            pass
    logging.getLogger(__name__).exception("Unhandled exception", exc_info=exc)
