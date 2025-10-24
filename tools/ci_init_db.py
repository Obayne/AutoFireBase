from __future__ import annotations

import os
import sqlite3
import sys

# Make a best-effort to ensure the repository's package root is on sys.path
# so `from db import loader` works regardless of the runner's checkout
# behavior. We check a few likely locations (repo root, nested `Autofire`
# folder) and append them to sys.path if they contain a `db` package.
repo_root = os.getcwd()
# Prefer deterministic locations for the `db` package. The repository
# typically contains `db/` at the repo root or under the `Autofire/`
# subdirectory. This avoids accidental matches in cache directories
# (e.g. `.mypy_cache`) which can confuse imports.
found_db_parent = None
candidates = [
    os.path.join(repo_root, "db"),
    os.path.join(repo_root, "Autofire", "db"),
    os.path.join(repo_root, "AutoFireBase", "db"),
]
for cand in candidates:
    if os.path.isdir(cand):
        # Parent directory is the place we should add to sys.path so
        # `import db` resolves to the intended package.
        found_db_parent = os.path.dirname(cand)
        break

# If not found in known locations, walk the repo tree (shallow) to find a
# `db` directory, skipping cache and hidden directories
if not found_db_parent:
    for root, dirs, files in os.walk(repo_root):
        # Skip hidden and cache directories
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".") and d not in ("__pycache__", "node_modules", "venv", ".venv")
        ]
        # Only consider directories named 'db'
        if "db" in dirs:
            found_db_parent = root
            break

if found_db_parent:
    if found_db_parent not in sys.path:
        sys.path.insert(0, found_db_parent)
    print(f"Found 'db' package under: {found_db_parent}; added to sys.path")
else:
    # Fallback: do a conservative walk but skip hidden/cache dirs that
    # often contain stale packages (e.g. .mypy_cache, __pycache__). This
    # reduces false positives.
    print("Top-level db not found in common locations; performing conservative search...")
    for root, dirs, files in os.walk(repo_root):
        # Filter out hidden and common cache/venv dirs from traversal
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d
            not in (
                "__pycache__",
                "venv",
                "env",
                "site-packages",
            )
        ]
        if "db" in dirs:
            found_db_parent = root
            if found_db_parent not in sys.path:
                sys.path.insert(0, found_db_parent)
            print(f"Found 'db' package under (fallback): {found_db_parent}; added to sys.path")
            break
    if not found_db_parent:
        print(
            "Warning: could not locate a local 'db' package under cwd; "
            "will attempt import anyway."
        )

# Clear any stale 'db' module from sys.modules before importing
if "db" in sys.modules:
    del sys.modules["db"]
if "db.loader" in sys.modules:
    del sys.modules["db.loader"]


try:
    from db import loader
except (ImportError, ModuleNotFoundError) as exc:  # pragma: no cover - CI helper
    # Fallback: attempt to locate db/loader.py in the checkout and import
    # it as a module. This handles cases where the package layout isn't on
    # sys.path but the source files are present in the workspace.
    print("Could not import db.loader via package import:", exc)
    print("Attempting to locate db/loader.py in the checkout...")
    loader_path = None
    for root, dirs, files in os.walk(repo_root):
        # Skip hidden and cache directories in fallback search
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".") and d not in ("__pycache__", "node_modules", "venv", ".venv")
        ]
        if "loader.py" in files and os.path.basename(root) == "db":
            loader_path = os.path.join(root, "loader.py")
            # Ensure the parent directory is in sys.path
            parent_dir = os.path.dirname(root)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
                print(f"Added {parent_dir} to sys.path for module import")
            break

    if loader_path is None:
        print("Failed to locate db/loader.py; sys.path:", sys.path)
        print("cwd contents:", os.listdir(repo_root))
        raise

    print(f"Found loader at: {loader_path}; " "importing as module 'ci_db_loader'")
    import importlib.util

    spec = importlib.util.spec_from_file_location("ci_db_loader", loader_path)
    if spec is None or spec.loader is None:
        print("Could not construct module spec for loader; aborting")
        raise ImportError("Could not import db.loader (spec creation failed)") from exc

    ci_db_loader = importlib.util.module_from_spec(spec)
    # Ensure the package parent is on sys.path so internal imports inside
    # loader.py (e.g. `from db import coverage_tables`) resolve to the
    # repository package rather than a cached/stale package.
    parent_of_db = os.path.dirname(os.path.dirname(loader_path))
    if parent_of_db not in sys.path:
        sys.path.insert(0, parent_of_db)
    # If a conflicting 'db' entry is already loaded, remove it so the
    # fresh import will bind correctly to the repo's package.
    if "db" in sys.modules:
        try:
            del sys.modules["db"]
        except Exception:
            pass

    spec.loader.exec_module(ci_db_loader)  # type: ignore

    # Provide a `loader` alias for the rest of the script to use.
    loader = ci_db_loader


def main() -> int:
    # Seed a workspace-local DB (used by CI helper) and also seed the loader's
    # default DB path so tests which call loader.connect() without arguments
    # (using DB_DEFAULT) will find the required tables.
    dbpath = os.path.join(os.getcwd(), ".autofire_ci_test.db")
    # Ensure the loader (if imported) will use the seeded DB by default so
    # tests that call `db.loader.connect()` without arguments see the
    # seeded tables. This is a defensive measure for CI environments.
    try:
        # Capture the loader's original DB default (if available) so we can
        # seed the actual path the tests will use (typically under the
        # runner's home directory). Then set loader.DB_DEFAULT to the CI
        # test DB path as a convenience.
        orig_default = getattr(loader, "DB_DEFAULT", None)
        setattr(loader, "DB_DEFAULT", dbpath)
        print(f"Set loader.DB_DEFAULT to: {dbpath}")
    except Exception:
        orig_default = getattr(loader, "DB_DEFAULT", None)
        # If loader isn't present or doesn't allow attribute assignment,
        # continue; we'll still attempt to seed the common default path
        # (orig_default) and the local CI path.
    # Ensure we attempt to seed both the CI-local DB path and the
    # loader's original default (if present) so the test process will
    # find the required tables regardless of which path it uses.
    paths_to_seed = []
    if dbpath:
        paths_to_seed.append(dbpath)
    if orig_default and orig_default not in paths_to_seed:
        paths_to_seed.append(orig_default)
    for path in paths_to_seed:
        if not path:
            continue
        con = None
        try:
            print(f"Initializing DB at: {path}")
            con = loader.connect(path)
            loader.ensure_schema(con)
            try:
                loader.seed_demo(con)
            except sqlite3.Error as exc:  # pragma: no cover - best-effort
                print(f"Seeding demo data (sqlite error) for {path} " f"(continuing): {exc}")
        except sqlite3.Error as exc:
            print(f"Failed to initialize DB at {path} (sqlite error): {exc}")
        except OSError as exc:
            # Catch filesystem / OS related errors but allow other exceptions to
            # surface (they should fail the job so we can fix them).
            print(f"Failed to initialize DB at {path} (OS error): {exc}")
        finally:
            if con is not None:
                try:
                    con.close()
                except sqlite3.Error:
                    pass
    print("DB initialization attempts complete. Seeded:", dbpath, "and loader default (if present)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
