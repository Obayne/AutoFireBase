# unified_app (clean root sandbox)

This folder hosts a clean copy of only the files actually used by the current app.

Usage (after generating and cloning the minimal tree):

1) Generate a used-files manifest from repo root:
   - Python: tools/generate_module_manifest.py
2) Clone the minimal tree into unified_app/src:
   - Python: tools/clone_minimal_tree.py
3) Run from this isolated tree (example):
   - Set PYTHONPATH to unified_app/src and run the entry script (e.g., main.py)

Notes
- This is a sandbox for validation. The original tree remains unchanged.
- If a needed file is missing, add it to the manifest or adjust the entry list.
