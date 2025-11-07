# VS Code GUI Workflow Guide

Quickstart

1. Open `AutoFireBase.code-workspace` in VS Code.
2. Install recommended extensions (prompt will appear).
3. Create and activate a virtual environment (Windows PowerShell):

```powershell
. .venv/Scripts/Activate.ps1
python -m pip install -r requirements-dev.txt
```

4. Use the Command Palette (Ctrl+Shift+P) to run tasks: `Tasks: Run Task` → `Run tests` or `Format`.

Debugging

- Press F5 to run the `Python: App` configuration.
- Use the `Python: pytest` launch config to run tests under the debugger.

Formatting & Linting

- Formatting runs on save. You can also run the `Format` task.
