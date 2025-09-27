import argparse, os, sys, zipfile, shutil, datetime

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(APP_ROOT, "_backups")
VERSION_FILE = os.path.join(APP_ROOT, "VERSION.txt")


def read_version():
    if os.path.exists(VERSION_FILE):
        try:
            with open(VERSION_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return ""
    return ""


def write_version(v):
    try:
        with open(VERSION_FILE, "w", encoding="utf-8") as f:
            f.write(str(v).strip() + "\n")
    except Exception as e:
        print("[warn] could not write VERSION.txt:", e)


def backup_current():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"autofire_backup_{ts}.zip")
    print("[backup] creating", backup_path)
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
    print("[update] applying", update_zip)
    with zipfile.ZipFile(update_zip, "r") as z:
        z.extractall(APP_ROOT)


def verify_post_update():
    p = os.path.join(APP_ROOT, "app", "main.py")
    if not os.path.exists(p):
        raise RuntimeError("post-update verification failed: app/main.py missing")
    print("[verify] ok")


def rollback_to(backup_zip):
    print("[rollback] using", backup_zip)
    with zipfile.ZipFile(backup_zip, "r") as z:
        z.extractall(APP_ROOT)
    print("[rollback] done")


def main():
    parser = argparse.ArgumentParser(description="AutoFire updater")
    parser.add_argument("--update", help="Path to update zip to apply")
    parser.add_argument("--rollback", help="Path to backup zip to restore")
    args = parser.parse_args()

    if args.rollback:
        rollback_to(args.rollback)
        return

    if not args.update:
        print(
            "Usage:\n  python apply_update.py --update C:\\AutoFireUpdates\\AutoFire_patch.zip\n"
            "or rollback:\n  python apply_update.py --rollback .\\_backups\\autofire_backup_YYYYMMDD_HHMMSS.zip"
        )
        return

    update_zip = args.update
    if not os.path.exists(update_zip):
        print("[error] update zip not found:", update_zip)
        sys.exit(1)

    cur_ver = read_version() or "(unknown)"
    print("[version] current:", cur_ver)

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
        print("[done] update complete. new version:", new_ver)
    except Exception as e:
        print("[error] update failed:", e)
        print("[info] rolling back...")
        rollback_to(backup_zip)
        sys.exit(2)


if __name__ == "__main__":
    main()
