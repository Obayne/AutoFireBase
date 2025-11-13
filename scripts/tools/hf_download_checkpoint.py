"""Download all files for a Hugging Face repo revision into a local folder.

This script downloads every file returned by `HfApi.list_repo_files` for the given
repo and revision, saving them into TARGET_ROOT/<repo-name>/<revision> so you can
point Transformers to the local folder if desired.

Run with the repo venv python:
  .\\.venv\\Scripts\\python.exe .\\scripts\\tools\\hf_download_checkpoint.py
"""

from __future__ import annotations

import shutil
import sys
import time
from collections.abc import Iterable
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download

REPO_ID = "nomic-ai/gpt4all-j"
REVISION = "v1.2-jazzy"
TARGET_ROOT = Path(r"C:\Dev\Models")
CACHE_DIR_NAME = ".hf_cache"


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def download_file_with_retries(fn: str, cache_dir: Path, attempts: int = 4) -> Path | None:
    for attempt in range(1, attempts + 1):
        try:
            print(f"    [attempt {attempt}] hf_hub_download {fn} ...")
            local = hf_hub_download(
                repo_id=REPO_ID, filename=fn, revision=REVISION, cache_dir=str(cache_dir)
            )
            return Path(local)
        except Exception as exc:  # huggingface_hub can raise various exceptions
            print(f"      download error: {exc}")
            if attempt < attempts:
                sleep = 5 * attempt
                print(f"      retrying in {sleep}s...")
                time.sleep(sleep)
            else:
                print("      giving up on this file")
                return None


def download_files(files: Iterable[str], target_dir: Path) -> int:
    ensure_dir(target_dir)
    cache_dir = target_dir / CACHE_DIR_NAME
    ensure_dir(cache_dir)

    for fn in files:
        print(f"Downloading {fn} ...")
        local = download_file_with_retries(fn, cache_dir)
        if local is None:
            print(f"  SKIPPED: {fn}")
            continue

        target_path = target_dir / Path(fn).name
        try:
            # backup existing
            if target_path.exists():
                stamp = time.strftime("%Y%m%d_%H%M%S")
                backup = target_path.with_suffix(target_path.suffix + f".bak-restore-{stamp}")
                target_path.replace(backup)
                print(f"  existing dest backed up to {backup}")

            shutil.copy2(local, target_path)
            print(f"  Saved {target_path} ({target_path.stat().st_size} bytes)")
        except Exception as exc:  # File operations can fail in various ways
            print(f"  ERROR saving {fn}: {exc}")
            return 3

    return 0


def main() -> int:
    api = HfApi()
    print(f"Listing files for {REPO_ID} revision={REVISION}...")
    try:
        files = api.list_repo_files(repo_id=REPO_ID, revision=REVISION)
    except Exception as exc:  # Network/API errors from huggingface_hub
        print("ERROR: Unable to list repo files:", exc)
        return 1

    if not files:
        print("No files found in repo revision")
        return 1

    target_dir = TARGET_ROOT / (REPO_ID.replace("/", "-")) / REVISION
    print(f"Target dir: {target_dir}")
    rc = download_files(files, target_dir)
    if rc != 0:
        print("Download failed with code", rc)
        return rc

    print("All files downloaded. You can point Transformers to this folder to load the model.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
