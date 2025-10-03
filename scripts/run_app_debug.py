"""Run the application with DEBUG logging for diagnosis.

Usage:
  python scripts/run_app_debug.py

This script configures root logging to DEBUG via app.logging_config.setup_logging
then imports and runs app.main(). It prints exceptions and the final exit code.
"""

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

try:
    from app.logging_config import setup_logging

    setup_logging(level=logging.DEBUG)
except Exception as e:
    print("Failed to configure logging:", e)


def main():
    try:
        import app.main as app_main

        logging.getLogger(__name__).debug("Calling app.main()")
        res = app_main.main()
        logging.getLogger(__name__).debug("app.main() returned %r (type=%s)", res, type(res))
        # app.main() may return an AppController instance or an int; normalize to exit code
        if isinstance(res, int):
            return res
        try:
            return int(res)
        except Exception:
            # Non-numeric / non-int return (e.g., AppController) — treat as success
            return 0
    except Exception:
        logging.exception("Unhandled exception running app.main()")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
