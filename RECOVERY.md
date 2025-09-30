## Recovery & Backup Procedures

This document describes the safe recovery and backup procedures for the AutoFire repository.

Purpose
- Provide a clear, low-friction process to create repository backups before large/uncertain changes.
- Provide a recovery checklist to reduce the chance of catastrophic regressions.

When to use
- Before changing many files across the repo (large refactors, bulk edits)
- Before modifying database, packaging, or CI configs
- Before merging substantial PRs to `main`

Quick steps
1. Run the backup script: `.\scripts\\backup_repo.ps1` (creates a timestamped zip under `backups/`).
2. Run the focused smoke test: `pytest -q AutoFireBase/tests/test_headless_startup.py`
	- Note: the CI quick-tests workflow will run a set of optional focused tests when they exist, but always runs the headless startup smoke test which is available in this repository. If you need the other focused tests, add them under `tests/` or `AutoFireBase/tests/`.
3. Commit and push your branch, open a PR.

If something goes wrong
1. Stop further changes.
2. Notify the team and include the last successful commit hash and the backup zip filename (from `backups/`).
3. NOTE: Backups are reference-only snapshots. Do not directly overwrite the working tree with a backup.

Safe inspection & selective restore
 - Use the inspection script to extract the backup into a temporary folder for review:
	 - PowerShell: `.\scripts\\restore_inspect.ps1 -ZipPath backups\\autofire-backup-YYYYMMDD-HHMMSS.zip`
 - Inspect the extracted files.
 - To restore changes, create a new branch and copy the specific files you want to restore into that branch, commit, and open a PR. This prevents accidental destructive restores.

Location of backups
- Backups are saved to `backups/` at the repository root. Backups are zip archives: `autofire-backup-YYYYMMDD-HHMMSS.zip`.

Additional notes
- Backups do not include untracked or ignored files by default; the script zips the entire working tree excluding `.git` and virtualenv directories.
- For database backups, use the `backup.db` or explicit DB export steps (see `scripts/` for DB-related scripts).

Reference-only policy
- Backups are intended strictly for reference and for producing a restore branch. Do not copy a backup zip directly into your working tree or overwrite files without a branch+PR.
