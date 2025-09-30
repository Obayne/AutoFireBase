# Deploy & PR Checklist

This checklist should be followed before creating a PR or merging large changes.

1. Run unit tests (focused):
   - pytest -q tests/test_placement_settings_persistence.py tests/test_device_device_id_roundtrip.py tests/test_place_into_drawing_adds_devices.py tests/test_device_palette_thumbnail.py tests/test_save_load_integration.py

2. Create a repository backup:
   - PowerShell: `.\scripts\backup_repo.ps1`

3. Lint & Format
   - `ruff check --fix .` then `black .`

4. Commit and push your branch
   - `git checkout -b feat/your-topic`
   - `git add -A && git commit -m "feat: ..."`
   - `git push -u origin feat/your-topic`

5. Open a PR and include:
   - Purpose and summary of changes
   - Link to related issue(s)
   - Any special test or environment notes

6. After merge
   - If you made database or data model changes, run the DB migration or export a backup.
