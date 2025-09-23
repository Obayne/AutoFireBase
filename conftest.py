import sys
from pathlib import Path


def ensure_project_on_path():
    # Start from this file's directory and walk up to find project markers
    here = Path(__file__).resolve().parent
    candidates = [here, here.parent]
    for base in candidates:
        if all((base / name).exists() for name in ("cad_core", "backend", "frontend")):
            if str(base) not in sys.path:
                sys.path.insert(0, str(base))
            return


ensure_project_on_path()

