import argparse
import hashlib
import json
import logging
import os
import zipfile

from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--patch", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with zipfile.ZipFile(args.patch, "r") as z:
        manifest = json.loads(z.read("manifest.json").decode("utf-8"))
        logger.info("Applying patch %s to %s", manifest.get("version"), args.project)
        for f in manifest.get("files", []):
            rel = f["path"].replace("\\", "/")
            data = z.read(rel)
            digest = sha256_bytes(data)
            if digest != f.get("sha256"):
                raise SystemExit(f"Checksum mismatch for {rel}")
            out_path = os.path.join(args.project, rel)
            logger.info(("[DRY] " if args.dry_run else "") + "write %s", out_path)
            if not args.dry_run:
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "wb") as w:
                    w.write(data)
    logger.info("Done.")


if __name__ == "__main__":
    main()
