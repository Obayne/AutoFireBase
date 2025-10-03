"""Run the app and write detailed logs to a file under ~/AutoFire/logs for diagnosis.

This ensures logs are persisted even when GUI steals stdout/stderr or message boxes appear.
"""

import datetime
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

LOG_DIR = Path.home() / "AutoFire" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"run_app_debug_{datetime.datetime.now():%Y%m%d_%H%M%S}.log"

# Also write a copy under the repo so workspace tools can read it for diagnostics
REPO_LOG_DIR = Path(__file__).parents[1] / "run_logs"
REPO_LOG_DIR.mkdir(parents=True, exist_ok=True)
REPO_LOG_FILE = REPO_LOG_DIR / LOG_FILE.name

handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
root = logging.getLogger()
root.addHandler(handler)
root.setLevel(logging.DEBUG)

# Mirror logs to repo-local file as well
repo_handler = logging.FileHandler(REPO_LOG_FILE, encoding="utf-8")
repo_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
root.addHandler(repo_handler)


def main():
    try:
        import app.main as app_main

        logging.getLogger(__name__).debug("Calling app.main()")
        res = app_main.main()
        logging.getLogger(__name__).debug("app.main() returned %r (type=%s)", res, type(res))
        print("Wrote debug log to:", LOG_FILE)
        return 0
    except Exception:
        logging.exception("Unhandled exception running app.main()")
        print("Wrote debug log to:", LOG_FILE)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
