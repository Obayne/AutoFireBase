"""Download a gpt4all-j ggml/gguf/bin model from Hugging Face for a specific revision.

It lists files in the repo revision, looks for likely model filenames, downloads the first match
with `hf_hub_download`, verifies size and sha256, and saves to C:\Dev\Models\gpt4all-j.bin.

Usage: run from the repo root using the repo venv:
  .\.venv\Scripts\python.exe .\scripts\tools\hf_download_gpt4all.py
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
import time
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download

REPO_ID = "nomic-ai/gpt4all-j"
REVISION = "v1.2-jazzy"
TARGET_DIR = Path(r"C:\Dev\Models")
TARGET_PATH = TARGET_DIR / "gpt4all-j.bin"
CACHE_DIR = Path(".hf_cache")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    api = HfApi()
    print(f"Listing files for {REPO_ID} revision={REVISION}...")
    try:
        files = api.list_repo_files(repo_id=REPO_ID, revision=REVISION)
    except Exception as exc:  # network / rate-limit / auth
        print("ERROR: Unable to list repo files:", exc)
        return 2

    print(f"Found {len(files)} files in repo revision. Scanning for model candidates...")

    # Heuristics for filenames likely to be the ggml/gguf model
    candidates = []
    for fn in files:
        lower = fn.lower()
        if (
            lower.endswith((".gguf", ".bin", ".ggml"))
            or "gpt4all-j" in lower
            or "ggml-gpt4all" in lower
        ):
            candidates.append(fn)

    if not candidates:
        print("No candidate model filenames found in the repo revision listing.")
        print("Files available (first 50):")
        for fn in files[:50]:
            print("  ", fn)
        return 3

    print("Candidates:")
    for i, c in enumerate(candidates, 1):
        print(f"  {i}. {c}")

    # Try downloading candidates in order until one looks valid
    for fn in candidates:
        print(f"Attempting to download '{fn}' ...")
        try:
            local = hf_hub_download(
                repo_id=REPO_ID, filename=fn, revision=REVISION, cache_dir=str(CACHE_DIR)
            )
        except Exception as exc:
            print(f"  Download failed for {fn}: {exc}")
            continue

        try:
            size = os.path.getsize(local)
        except OSError:
            print(f"  Downloaded file not found at {local}")
            continue

        print(f"  Downloaded to cache: {local} ({size} bytes)")

        if size < 1_000_000:  # too small to be a model
            print("  File too small to be a model, skipping.")
            continue

        sha = sha256_file(Path(local))
        print(f"  SHA256: {sha}")

        # Backup existing target if present
        if TARGET_PATH.exists():
            stamp = time.strftime("%Y%m%d_%H%M%S")
            backup = TARGET_PATH.with_suffix(TARGET_PATH.suffix + f".bak-restore-{stamp}")
            shutil.move(str(TARGET_PATH), str(backup))
            print(f"  Existing target moved to {backup}")

        # Move from cache to target path
        try:
            shutil.copy2(local, TARGET_PATH)
            print(f"  Saved model to {TARGET_PATH}")
        except Exception as exc:
            print(f"  Failed to save model to {TARGET_PATH}: {exc}")
            # attempt to restore backup
            return 5

        print("Model download and save complete. Verifying saved file...")
        saved_sha = sha256_file(TARGET_PATH)
        saved_size = TARGET_PATH.stat().st_size
        print(f"  Saved size={saved_size}, sha256={saved_sha}")
        if saved_sha != sha:
            print("WARNING: SHA mismatch between cached file and saved file.")

        print(
            "All done. You can now run "
            " .\\venv\\Scripts\\python.exe .\\scripts\\tools\\local_llm_test.py "
            "to validate the model load."
        )
        return 0

    print("Tried all candidates but none produced a valid model file.")
    return 4


if __name__ == "__main__":
    sys.exit(main())
