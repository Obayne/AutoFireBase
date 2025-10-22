# How to Run AutoFire

This guide is for non-programmers. Follow these steps exactly.

## Prerequisites
- Windows
- Python 3.11 (installed and available in PATH)

## Setup (first time only)
1. Open PowerShell.
2. Navigate to the project folder:
```powershell
cd C:\Dev\Autofire
```
3. Create and activate the virtual environment:
```powershell
./setup_dev.ps1
. .venv\Scripts\Activate.ps1
```
4. Install dependencies if needed:
```powershell
pip install -r requirements.txt
```

## Run the App
- Preferred method (ensures imports work):
```powershell
python -m frontend.app
```

- Alternate method (may require PATH fixes):
```powershell
python frontend/app.py
```

## Troubleshooting
- If you see "No module named 'frontend'": run with `python -m frontend.app`.
- If you see PySide6 errors: ensure `pip install -r requirements.txt` completed successfully.
- If you see database warnings: the app will initialize `autofire.db` automatically.

## Where to Click
- The app opens directly into the System Builder.
- Follow the steps at the top: Welcome → Assess → Panel → Devices → Wiring → Review.
- Annunciators now appear under the Devices step as their own section.

## Need Help?
- Read `MASTER_SPEC_VISION.md` for the project vision and features.
- Read `docs/FEATURE_ROADMAP.md` for planned milestones.
