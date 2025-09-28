"""Clean HF revision downloader.

Downloads files for REPO_ID@REVISION into C:/Dev/Models/<repo>-<revision>.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Iterable, Optional

import shutil
from huggingface_hub import HfApi, hf_hub_download


REPO_ID = "nomic-ai/gpt4all-j"
REVISION = "v1.2-jazzy"
TARGET_ROOT = Path("C:/Dev/Models")
CACHE_DIR_NAME = ".hf_cache"


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def download_with_retries(repo_id: str, filename: str, revision: str, cache_dir: Path, attempts: int = 4) -> Optional[Path]:
    for attempt in range(1, attempts + 1):
        try:
            local = hf_hub_download(repo_id=repo_id, filename=filename, revision=revision, cache_dir=str(cache_dir))
            return Path(local)
        except Exception as exc:
            print(f"attempt {attempt} error: {exc}")
            if attempt < attempts:
                time.sleep(2 * attempt)
            else:
                return None


def download_files(files: Iterable[str], target_dir: Path) -> int:
    ensure_dir(target_dir)
    cache_dir = target_dir / CACHE_DIR_NAME
    ensure_dir(cache_dir)

    for fn in files:
        print(f"Downloading {fn} ...")
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
            shutil.copy2(local, dest)
            print(f"  saved -> {dest} ({dest.stat().st_size} bytes)")
        except Exception as exc:
            print(f"  FAILED saving {fn}: {exc}")
            return 3

    return 0


def main() -> int:
    api = HfApi()
    print(f"Listing files for {REPO_ID} @ {REVISION}...")
    try:
        files = api.list_repo_files(repo_id=REPO_ID, revision=REVISION)
    except Exception as exc:
        print("ERROR listing files:", exc)
        return 1

    if not files:
        print("No files found")
        return 2

    target_dir = TARGET_ROOT / (REPO_ID.replace("/", "-")) / REVISION
    print("Target dir:", target_dir)
    rc = download_files(files, target_dir)
    if rc != 0:
        print("Download failed code", rc)
        return rc

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
