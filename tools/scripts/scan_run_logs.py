#!/usr/bin/env python3
"""Scan run-*-logs.zip files for CI failures and extract top error lines.
Reads fetch_gha_runs_summary.txt to find failed CI runs, then inspects the corresponding run-*.zip.
Writes concise summaries to C:/Dev/pwsh-diagnostics/run_log_summaries.txt
"""

import re
import zipfile
from pathlib import Path

BASE = Path(r"C:/Dev/pwsh-diagnostics")
SUMMARY_IN = BASE / "fetch_gha_runs_summary.txt"
OUT = BASE / "run_log_summaries.txt"
PAT = re.compile(
    r"error|Exception|Traceback|FAILED|ERROR:|subprocess-exited-with-error", re.IGNORECASE
)

runs_to_check = []
if SUMMARY_IN.exists():
    for line in SUMMARY_IN.read_text(encoding="utf-8").splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 4:
            run_id = parts[0]
            name = parts[1]
            status = parts[2]
            conclusion = parts[3]
            # Only look at CI workflow runs that concluded with failure
            if name.upper().strip() == "CI" and conclusion.lower().strip() == "failure":
                runs_to_check.append(run_id)
else:
    # fallback: scan all run-*.zip files
    runs_to_check = [p.stem.split("-", 1)[1] for p in BASE.glob("run-*-logs.zip")]

with OUT.open("w", encoding="utf-8") as outf:
    if not runs_to_check:
        outf.write("No failed CI runs found in fetch_gha_runs_summary.txt.\n")
    for run_id in runs_to_check:
        zip_name = BASE / f"run-{run_id}-logs.zip"
        outf.write(f"=== run {run_id} ===\n")
        if not zip_name.exists():
            outf.write(f"Run archive not found: {zip_name}\n")
            continue
        try:
            with zipfile.ZipFile(zip_name, "r") as zf:
                # list candidate files inside zip that look like logs
                candidates = [
                    n
                    for n in zf.namelist()
                    if n.endswith(".txt")
                    or n.endswith(".log")
                    or "build" in n.lower()
                    or "steps" in n.lower()
                ]
                if not candidates:
                    # fallback: inspect all files
                    candidates = zf.namelist()
                found_any = False
                # inspect each candidate, but stop after collecting some matches
                matches_collected = 0
                for candidate in candidates:
                    if matches_collected >= 30:
                        break
                    try:
                        with zf.open(candidate) as fh:
                            try:
                                content = fh.read().decode("utf-8")
                            except Exception:
                                try:
                                    content = fh.read().decode("latin-1")
                                except Exception:
                                    continue
                    except Exception:
                        continue
                    for i, line in enumerate(content.splitlines(), start=1):
                        if PAT.search(line):
                            outf.write(f"{candidate}:{i}: {line.strip()}\n")
                            found_any = True
                            matches_collected += 1
                            if matches_collected >= 30:
                                break
                if not found_any:
                    outf.write("No matching error lines found in run archive.\n")
        except zipfile.BadZipFile:
            outf.write("Bad zip file (corrupt or HTML response saved).\n")
        except Exception as e:
            outf.write(f"Failed to process run archive: {e}\n")

print(f"Run-scan complete. Wrote summary to {OUT}")
