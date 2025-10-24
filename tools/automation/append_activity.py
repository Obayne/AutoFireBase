"""Append a timestamped entry to tools/automation/agent_activity.log
Usage: python tools/automation/append_activity.py "Some activity description"""

import sys
from datetime import datetime
from pathlib import Path

LOG = Path(__file__).resolve().parents[0] / "agent_activity.log"


def append(msg: str):
    ts = datetime.utcnow().isoformat() + "Z"
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{ts} | {msg}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: append_activity.py "message"')
        sys.exit(1)
    append(" ".join(sys.argv[1:]))
    print("Appended activity.")
