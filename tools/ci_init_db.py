from __future__ import annotations

import os
import sqlite3
import sys

try:
    from db import loader
except Exception as exc:  # pragma: no cover - CI helper
    print("Could not import db.loader:", exc)
    raise


def main() -> int:
    # Seed a workspace-local DB (used by CI helper) and also seed the loader's
    # default DB path so tests which call loader.connect() without arguments
    # (using DB_DEFAULT) will find the required tables.
    dbpath = os.path.join(os.getcwd(), ".autofire_ci_test.db")
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
