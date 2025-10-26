import os
import sys

print("PYTHONPATH=", os.environ.get("PYTHONPATH"))
print("QT_QPA_PLATFORM=", os.environ.get("QT_QPA_PLATFORM"))
try:
    import autofire_professional_integrated as api

    print("Import OK:", api.__name__)
    print("File:", getattr(api, "__file__", None))
except Exception as e:  # noqa: BLE001
    print("IMPORT-ERROR:", repr(e))
    sys.exit(1)
