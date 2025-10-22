from __future__ import annotations

"""Download all files for a Hugging Face repo revision into a local folder.

This script lists files in a Hugging Face repo revision and downloads each one into
TARGET_ROOT/<repo-id-repr>/<revision>. It includes simple retry logic and backs up
existing files by appending a .bak-restore-<timestamp> suffix.

Usage:
  .venv\Scripts\python.exe .\scripts\tools\hf_download_checkpoint.py
"""

import shutil  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections.abc import Iterable  # noqa: E402
from pathlib import Path  # noqa: E402

from huggingface_hub import HfApi, hf_hub_download  # noqa: E402

REPO_ID = "nomic-ai/gpt4all-j"
REVISION = "v1.2-jazzy"
TARGET_ROOT = Path(r"C:\Dev\Models")
CACHE_DIR_NAME = ".hf_cache"


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def download_with_retries(
    repo_id: str, filename: str, revision: str, cache_dir: Path, attempts: int = 4
) -> Path | None:
    """Try to download a single file with retries. Returns the local Path or None."""
    for attempt in range(1, attempts + 1):
        try:
            print(f"    [attempt {attempt}] downloading {filename} ...")
            local = hf_hub_download(
                repo_id=repo_id, filename=filename, revision=revision, cache_dir=str(cache_dir)
            )
            return Path(local)
        except Exception as exc:  # pragma: no cover - network/IO retries
            print(f"      error: {exc}")
            if attempt < attempts:
                wait = 5 * attempt
                print(f"      retrying in {wait}s...")
                time.sleep(wait)
            else:
                print("      giving up on this file")
                return None


def download_files(files: Iterable[str], target_dir: Path) -> int:
    ensure_dir(target_dir)
    cache_dir = target_dir / CACHE_DIR_NAME
    ensure_dir(cache_dir)

    for fn in files:
        print(f"Downloading: {fn}")
        local = download_with_retries(REPO_ID, fn, REVISION, cache_dir)
        if local is None:
            print(f"  SKIPPED: {fn}")
            continue

        dest = target_dir / Path(fn).name
        try:
            if dest.exists():
                stamp = time.strftime("%Y%m%d_%H%M%S")
                backup = dest.with_suffix(dest.suffix + f".bak-restore-{stamp}")
                dest.replace(backup)
                print(f"  backed up existing to {backup}")

            shutil.copy2(local, dest)
            print(f"  saved -> {dest} ({dest.stat().st_size} bytes)")
        except Exception as exc:  # pragma: no cover - IO errors
            print(f"  FAILED saving {fn}: {exc}")
            return 3

    return 0


def main() -> int:
    api = HfApi()
    print(f"Listing files for {REPO_ID} revision={REVISION}...")
    try:
        files = api.list_repo_files(repo_id=REPO_ID, revision=REVISION)
    except Exception as exc:  # pragma: no cover - network failures
        print("ERROR: Unable to list repo files:", exc)
        return 1

    if not files:
        print("No files found in revision")
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
