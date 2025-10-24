"""CI helper: collect ldd diagnostics for PySide6/shiboken6 and write to /tmp/ldd-shiboken6.txt
This is executed inside the Actions runner when PySide6 import fails.
"""

import importlib
import os
import subprocess
import traceback

OUT = "/tmp/ldd-shiboken6.txt"


def safe_write(s):
    with open(OUT, "a", encoding="utf-8") as f:
        f.write(s + "\n")


if __name__ == "__main__":
    try:
        open(OUT, "w", encoding="utf-8").write("ldd diagnostics start\n")
    except Exception:
        pass

    try:
        shib = importlib.import_module("shiboken6")
        path = getattr(shib, "__file__", None)
        if path:
            safe_write("shiboken6: " + path)
            safe_write("== ldd(shiboken6) ==")
            try:
                subprocess.run(
                    ["ldd", path], check=False, stdout=open(OUT, "a"), stderr=subprocess.STDOUT
                )
            except Exception:
                safe_write("ldd failed on shiboken6")
    except Exception:
        safe_write("shiboken6 import failed:")
        safe_write(traceback.format_exc())

    try:
        import PySide6

        pd = os.path.dirname(PySide6.__file__)
        safe_write("\nPySide6 package dir: " + pd)
        safe_write("== scanning for .so files under PySide6 package dir ==")
        for root, dirs, files in os.walk(pd):
            for fn in files:
                if fn.endswith((".so", ".so.6")):
                    p = os.path.join(root, fn)
                    safe_write("\nfile: " + p)
                    try:
                        subprocess.run(
                            ["ldd", p], check=False, stdout=open(OUT, "a"), stderr=subprocess.STDOUT
                        )
                    except Exception:
                        safe_write("ldd failed on " + p)
    except Exception:
        safe_write("PySide6 ldd collection failed:")
        safe_write(traceback.format_exc())

    try:
        print("Wrote diagnostics to", OUT)
    except Exception:
        pass
