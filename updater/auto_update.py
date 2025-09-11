
import os, sys, json, zipfile, shutil, time
from pathlib import Path

def _exe_dir():
    # Return directory next to the running EXE, or project root in dev
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "executable")).resolve().parent
    return Path(__file__).resolve().parents[1]

def _log(msg: str):
    try:
        base = Path.home() / "AutoFire" / "logs"
        base.mkdir(parents=True, exist_ok=True)
        with (base / "updater.log").open("a", encoding="utf-8") as f:
            f.write(time.strftime("[%Y-%m-%d %H:%M:%S] ") + msg + "\n")
    except Exception:
        pass

def _candidate_update_dirs():
    # environment override first
    env = os.environ.get("AUTO_FIRE_UPDATES_DIR")
    base = _exe_dir()
    dirs = []
    if env: dirs.append(Path(env))
    # common locations
    dirs += [
        Path("C:/AutoFireUpdates"),
        Path.home() / "AutoFireUpdates",
        base / "updates",
    ]
    # unique-ify while preserving order
    seen = set(); out = []
    for d in dirs:
        p = d.resolve()
        if p not in seen:
            seen.add(p); out.append(p)
    return out

def _iter_patch_zips(d: Path):
    if not d.exists(): return []
    zips = sorted([p for p in d.glob("*.zip") if p.is_file()], key=lambda p: p.stat().st_mtime)
    return zips

def _apply_patch_zip(zip_path: Path, target_root: Path) -> bool:
    """Very small patcher: expects manifest.json + files (relative paths)."""
    with zipfile.ZipFile(zip_path, "r") as z:
        try:
            manifest = json.loads(z.read("manifest.json").decode("utf-8"))
        except Exception:
            manifest = None
        # write all files except manifest itself
        wrote = 0
        for info in z.infolist():
            name = info.filename
            if name.endswith("/") or name == "manifest.json":
                continue
            # normalize to Windows separators
            dest = (target_root / Path(name)).resolve()
            dest.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info, "r") as src, open(dest, "wb") as dst:
                shutil.copyfileobj(src, dst)
            wrote += 1
        _log(f"Applied {wrote} files from {zip_path.name} into {target_root}")
        return wrote > 0

def check_and_apply_updates():
    """
    Checks common update folders for *.zip and applies them into the EXE folder.
    Non-fatal: all exceptions are swallowed and logged; returns True if anything applied.
    """
    try:
        base = _exe_dir()
        applied_any = False
        for d in _candidate_update_dirs():
            try:
                for zp in _iter_patch_zips(d):
                    try:
                        ok = _apply_patch_zip(zp, base)
                        # Move to 'applied' folder to avoid reapplying
                        dst_dir = d / "applied"; dst_dir.mkdir(parents=True, exist_ok=True)
                        dst = dst_dir / (zp.stem + "_applied" + zp.suffix)
                        try:
                            zp.replace(dst)
                        except Exception:
                            # if cannot move (e.g., cross-volume), copy then remove
                            shutil.copy2(zp, dst); os.remove(zp)
                        applied_any = applied_any or ok
                    except Exception as e:
                        _log(f"Failed to apply {zp}: {e}")
            except Exception as e:
                _log(f"Error scanning {d}: {e}")
        return applied_any
    except Exception as e:
        _log(f"Updater failed: {e}")
        return False
