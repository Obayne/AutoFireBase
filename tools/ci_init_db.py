from __future__ import annotations

import os
import sqlite3
import sys

# Make a best-effort to ensure the repository's package root is on sys.path
# so `from db import loader` works regardless of the runner's checkout
# behavior. We check a few likely locations (repo root, nested `Autofire`
# folder) and append them to sys.path if they contain a `db` package.
repo_root = os.getcwd()

# Walk the repo tree (shallow) to find a `db` directory regardless of
# nested checkout layout (e.g., D:/a/Repo/Repo/...). Add its parent to
# sys.path so `from db import loader` succeeds.
found_db_parent = None
for root, dirs, files in os.walk(repo_root):
    # Only consider directories named 'db'
    if "db" in dirs:
        found_db_parent = root
        break

if found_db_parent:
    if found_db_parent not in sys.path:
        sys.path.insert(0, found_db_parent)
    print(f"Found 'db' package under: {found_db_parent}; added to sys.path")
else:
    print("Warning: could not locate a local 'db' package under cwd; will attempt import anyway.")

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
        if "loader.py" in files and os.path.basename(root) == "db":
            loader_path = os.path.join(root, "loader.py")
            break

    if loader_path is None:
        print("Failed to locate db/loader.py; sys.path:", sys.path)
        print("cwd contents:", os.listdir(repo_root))
        raise

    print(f"Found loader at: {loader_path}; importing as module 'ci_db_loader'")
    import importlib.util

    spec = importlib.util.spec_from_file_location("ci_db_loader", loader_path)
    if spec is None or spec.loader is None:
        print("Could not construct module spec for loader; aborting")
        raise ImportError("Could not import db.loader (spec creation failed)") from exc

    ci_db_loader = importlib.util.module_from_spec(spec)
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
        setattr(loader, "DB_DEFAULT", dbpath)
        print(f"Set loader.DB_DEFAULT to: {dbpath}")
    except Exception:
        # If loader isn't present or doesn't allow attribute assignment,
        # continue; the script will still seed dbpath explicitly below.
        pass
    for path in (dbpath, getattr(loader, "DB_DEFAULT", None)):
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
                print(f"Seeding demo data (sqlite error) for {path} (continuing):", exc)
        except sqlite3.Error as exc:
            print(f"Failed to initialize DB at {path} (sqlite error):", exc)
        except OSError as exc:
            # Catch filesystem / OS related errors but allow other exceptions to
            # surface (they should fail the job so we can fix them).
            print(f"Failed to initialize DB at {path} (OS error):", exc)
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
