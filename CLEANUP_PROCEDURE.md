# File Structure Cleanup Procedure

## Issue Identified
Complete repository duplication: the main working directory contains a subdirectory `AutoFireBase/` with another full copy of the project.

## Cleanup Steps

### 1. Backup Current Work (CRITICAL)
```powershell
# Create a backup of your current changes
git stash push -m "Backup before cleanup - $(Get-Date)"
# Or create a branch for safety
git branch backup-before-cleanup
```

### 2. Verify Active Directory
Your main working directory should be: `C:\Dev\Autofire`
The duplicate is at: `C:\Dev\Autofire\AutoFireBase\`

### 3. Check for Important Changes in Duplicate
```powershell
# Check if AutoFireBase has any newer changes
cd C:\Dev\Autofire\AutoFireBase
git status
git log --oneline -10
```

### 4. Remove the Duplicate Directory
```powershell
# From main directory
cd C:\Dev\Autofire
# Remove the duplicate (be very careful with this command)
Remove-Item -Recurse -Force .\AutoFireBase\
```

### 5. Verify Git Status
```powershell
git status
# Should show only your actual changes, not the duplicate
```

### 6. Clean Up Any Remaining Issues
```powershell
# Remove any build artifacts
Remove-Item -Recurse -Force .pytest_cache\, __pycache__\, *.pyc -ErrorAction SilentlyContinue

# Clean git
git clean -fd
```

### 7. Restore Your Work
```powershell
# If you used stash:
git stash pop

# Or if you used branch:
git checkout backup-before-cleanup
git checkout main
git merge backup-before-cleanup
```

## Post-Cleanup Verification
- [ ] Only one copy of each directory exists
- [ ] Git status shows clean working tree
- [ ] App still runs: `python app/main.py`
- [ ] Tests still work: `pytest -q`

## Warning Signs to Watch For
- DO NOT delete anything if you're unsure
- Check `git status` before and after each step
- The AutoFireBase subdirectory should NOT exist after cleanup
