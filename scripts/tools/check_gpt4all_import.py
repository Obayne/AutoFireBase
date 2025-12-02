"""Import-check helper for gpt4all packages in the repo venv.

Run with the repo venv python to verify installation and show module/version.
"""

from __future__ import annotations

import importlib
import sys

names = ["gpt4all_j", "gpt4all", "gpt4allj"]
found = False

for name in names:
    try:
        m = importlib.import_module(name)
        print("IMPORTED:", name)
        print("module.__name__:", getattr(m, "__name__", "(no name)"))
        print("module file:", getattr(m, "__file__", "(built-in or namespace)"))
        ver = getattr(m, "__version__", None)
        if ver is None:
            # try pkg_resources
            try:
                import pkg_resources

                ver = pkg_resources.get_distribution(name).version
            except Exception:
                ver = "(unknown)"
        print("version:", ver)
        found = True
        break
    except Exception as e:
        print("FAILED_IMPORT:", name, "->", type(e).__name__, e)

if not found:
    print("No known gpt4all module imported. Check installation and package name.")
    sys.exit(1)

print("OK")
