# Deploy & PR Checklist

This checklist should be followed before creating a PR or merging large changes.

1. Run unit tests (focused):
    - pytest -q AutoFireBase/tests/test_headless_startup.py
       (CI quick-tests will include optional focused tests when present, but always runs the headless startup smoke-test)

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
