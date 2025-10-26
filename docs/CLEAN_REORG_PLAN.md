# Clean Reorg Plan (staged and reversible)

Goal: produce a clean, minimal root containing only the files the app actually uses today, without risking breakage.

We’ll do this in 3 phases:

1) Discover used files (no runtime side‑effects)
- Use a static import graph of our entry scripts via Python’s modulefinder to generate a manifest of imported modules (file paths) under the repo root.
- Output: logs/used_files_manifest.json

2) Create a new clean root with a bootstrap
- Create unified_app/ with a README and (optionally) a bootstrap entry that imports our existing entrypoint.
- Add a copier script that reads the manifest and clones only the needed files into unified_app/src/, preserving relative paths.

3) Validate and switch
- Run lint/tests against unified_app/src (or run the app) to validate.
- Update launchers to point to unified_app once validated. Keep the original tree as a safety net until we’re fully confident.

Notes
- This process doesn’t delete or move originals; it's "copy and validate."
- If modulefinder misses dynamically imported files, we can append them to the manifest and re-run the copier.
- After the switch, we can archive legacy folders.
