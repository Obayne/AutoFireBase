"""Debug runner: configure DEBUG logging to ./logs/run_app_debug.log and run app.main().

Usage: python tools/run_app_debug.py
"""

import logging
import sys
from pathlib import Path

LOG_DIR = Path("./logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "run_app_debug.log"


def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    # File handler
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    fh.setFormatter(fmt)
    root.addHandler(fh)
    # Also print errors to console
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    root.addHandler(ch)


def main():
    setup_logging()
    logging.getLogger(__name__).info("Starting app debug runner...")
    try:
        # Import and run app.main
        from app import main as app_main

        result = app_main.main()
        logging.getLogger(__name__).info("app.main() returned: %r", result)
    except Exception:
        logging.exception("Unhandled exception during app startup")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
