import os

root = r"C:\Dev\Autofire"
legacy = []
for dirpath, dirs, files in os.walk(os.path.join(root, "cad_core")):
    for f in files:
        if f.endswith(".py"):
            rel = os.path.relpath(os.path.join(dirpath, f), root)
            legacy.append(rel.replace("\\", "/"))
lv = []
if os.path.isdir(os.path.join(root, "lv_cad", "cad_core")):
    for dirpath, dirs, files in os.walk(os.path.join(root, "lv_cad", "cad_core")):
        for f in files:
            if f.endswith(".py"):
                rel = os.path.relpath(os.path.join(dirpath, f), root)
                lv.append(rel.replace("\\", "/"))
print("legacy cad_core files:")
for x in sorted(legacy):
    print(" -", x)
print("\nlv_cad cad_core files:")
for x in sorted(lv):
    print(" -", x)
missing = [x for x in legacy if x.replace("cad_core/", "lv_cad/cad_core/") not in lv]
print("\nmissing in lv_cad:")
for x in missing:
    print(" -", x)
# backend
legacy_b = []
for dirpath, dirs, files in os.walk(os.path.join(root, "backend")):
    for f in files:
        if f.endswith(".py"):
            rel = os.path.relpath(os.path.join(dirpath, f), root)
            legacy_b.append(rel.replace("\\", "/"))
lv_b = []
if os.path.isdir(os.path.join(root, "lv_cad", "backend")):
    for dirpath, dirs, files in os.walk(os.path.join(root, "lv_cad", "backend")):
        for f in files:
            if f.endswith(".py"):
                rel = os.path.relpath(os.path.join(dirpath, f), root)
                lv_b.append(rel.replace("\\", "/"))
print("\nlegacy backend files:")
for x in sorted(legacy_b):
    print(" -", x)
print("\nlv_cad backend files:")
for x in sorted(lv_b):
    print(" -", x)
missing_b = [x for x in legacy_b if x.replace("backend/", "lv_cad/backend/") not in lv_b]
print("\nmissing in lv_cad backend:")
for x in missing_b:
    print(" -", x)
