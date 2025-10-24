#!/usr/bin/env python3
"""Scan job-*-logs.zip files in C:/Dev/pwsh-diagnostics and summarize error lines.
Writes results to C:/Dev/pwsh-diagnostics/job_log_summaries.txt
"""

import re
import zipfile
from pathlib import Path

OUT_DIR = Path(r"C:/Dev/pwsh-diagnostics")
OUT_FILE = OUT_DIR / "job_log_summaries.txt"
PATTERN = re.compile(r"error|Exception|Traceback|FAILED|ERROR:", re.IGNORECASE)

OUT_DIR.mkdir(parents=True, exist_ok=True)

with OUT_FILE.open("w", encoding="utf-8") as outf:
    zips = sorted(OUT_DIR.glob("job-*-logs.zip"))
    if not zips:
        outf.write("No job-*.zip files found.\n")
        print("No job-*.zip files found.")
    for z in zips:
        outf.write(f"=== {z.name} ===\n")
        try:
            with zipfile.ZipFile(z, "r") as zf:
                extract_dir = OUT_DIR / z.stem
                # remove existing extracted dir
                if extract_dir.exists():
                    for p in sorted(extract_dir.rglob("*"), reverse=True):
                        try:
                            if p.is_file():
                                p.unlink()
                            elif p.is_dir():
                                p.rmdir()
                        except Exception:
                            pass
                    try:
                        extract_dir.rmdir()
                    except Exception:
                        pass
                zf.extractall(extract_dir)
                found = False
                for f in extract_dir.rglob("*"):
                    if f.is_file():
                        try:
                            text = f.read_text(encoding="utf-8")
                        except Exception:
                            try:
                                text = f.read_text(encoding="latin-1")
                            except Exception:
                                continue
                        for i, line in enumerate(text.splitlines(), start=1):
                            if PATTERN.search(line):
                                outf.write(f"{f.relative_to(OUT_DIR)}:{i}: {line.strip()}\n")
                                found = True
                if not found:
                    outf.write("No matching error lines found\n")
        except zipfile.BadZipFile:
            outf.write("Failed to expand: Bad zip file\n")
        except Exception as e:
            outf.write(f"Failed to process zip: {e}\n")

print(f"Scan complete. Summaries written to {OUT_FILE}")
