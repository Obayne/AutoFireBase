import os
import subprocess
import time
from pathlib import Path

import pytest


@pytest.mark.gui
def test_system_builder_smoke_creates_screenshot():
    """Smoke test: run the debug_show helper and assert a screenshot is produced.

    The debug helper writes to C:/Dev/pwsh-diagnostics/autofire-window-screenshot.png
    """
    repo_root = Path(__file__).resolve().parent.parent
    debug_script = repo_root / "tools" / "debug_show.py"
    assert debug_script.exists(), "debug_show.py missing"

    out_dir = Path(r"C:/Dev/pwsh-diagnostics")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "autofire-window-screenshot.png"
    if out_file.exists():
        out_file.unlink()

    env = os.environ.copy()
    env["AUTOFIRE_DEBUG_SHOW"] = "1"
    env["AUTOFIRE_DISABLE_STYLES"] = "1"

    # Run the debug helper which runs the app and saves a screenshot
    subprocess.run(["python", str(debug_script)], env=env, timeout=30, check=True)

    # Wait briefly for file to appear
    deadline = time.time() + 5
    while time.time() < deadline and not out_file.exists():
        time.sleep(0.1)

    assert out_file.exists(), "screenshot not created"
    assert out_file.stat().st_size > 1024, "screenshot file too small"
