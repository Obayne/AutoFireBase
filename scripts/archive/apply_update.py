import argparse
import datetime
import logging
import os
import sys
import zipfile

from app.logging_config import setup_logging

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(APP_ROOT, "_backups")
VERSION_FILE = os.path.join(APP_ROOT, "VERSION.txt")


def read_version():
    if os.path.exists(VERSION_FILE):
        try:
            with open(VERSION_FILE, encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return ""
    return ""


def write_version(v):
    try:
        with open(VERSION_FILE, "w", encoding="utf-8") as f:
            f.write(str(v).strip() + "\n")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning("could not write VERSION.txt: %s", e)


def backup_current():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"autofire_backup_{ts}.zip")
    logger = logging.getLogger(__name__)
    logger.info("[backup] creating %s", backup_path)
    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(APP_ROOT):
            if os.path.abspath(root).startswith(os.path.abspath(BACKUP_DIR)):
                continue
            if os.path.basename(root).lower() == ".venv":
                continue
            for fn in files:
                p = os.path.join(root, fn)
                rel = os.path.relpath(p, APP_ROOT)
                z.write(p, rel)
    return backup_path


def apply_zip(update_zip):
    logger = logging.getLogger(__name__)
    logger.info("[update] applying %s", update_zip)
    with zipfile.ZipFile(update_zip, "r") as z:
        z.extractall(APP_ROOT)


def verify_post_update():
    p = os.path.join(APP_ROOT, "app", "main.py")
    if not os.path.exists(p):
        raise RuntimeError("post-update verification failed: app/main.py missing")
    logger = logging.getLogger(__name__)
    logger.info("[verify] ok")


def rollback_to(backup_zip):
    logger = logging.getLogger(__name__)
    logger.info("[rollback] using %s", backup_zip)
    with zipfile.ZipFile(backup_zip, "r") as z:
        z.extractall(APP_ROOT)
    logger.info("[rollback] done")


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="AutoFire updater")
    parser.add_argument("--update", help="Path to update zip to apply")
    parser.add_argument("--rollback", help="Path to backup zip to restore")
    args = parser.parse_args()

    if args.rollback:
        rollback_to(args.rollback)
        return

    if not args.update:
        logger.info(
            "Usage:\n"
            "  python apply_update.py --update C:\\AutoFireUpdates\\AutoFire_patch.zip\n"
            "or rollback:\n"
            "  python apply_update.py --rollback .\\_backups\\autofire_backup_YYYYMMDD_HHMMSS.zip"
        )
        return

    update_zip = args.update
    if not os.path.exists(update_zip):
        logger.error("update zip not found: %s", update_zip)
        sys.exit(1)

    cur_ver = read_version() or "(unknown)"
    logger.info("[version] current: %s", cur_ver)

    backup_zip = backup_current()

    try:
        apply_zip(update_zip)
        verify_post_update()
        with zipfile.ZipFile(update_zip, "r") as z:
            new_ver = (
                z.read("VERSION.txt").decode("utf-8").strip()
                if "VERSION.txt" in z.namelist()
                else "0.0.0"
            )
        write_version(new_ver)
        logger.info("[done] update complete. new version: %s", new_ver)
    except Exception:
        logger.exception("[error] update failed")
        logger.info("[info] rolling back...")
        rollback_to(backup_zip)
        sys.exit(2)


if __name__ == "__main__":
    main()
