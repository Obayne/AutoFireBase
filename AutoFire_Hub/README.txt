AutoFire Project Hub (PowerShell Menu)
======================================

What this is:
- A single PowerShell menu you can double‑click to handle common tasks:
  Start Day, Build, Test, Branch, Commit, Wrap Up & Clean, and a simple CI Lab.
- It writes logs to: <your repo>\logs\<YYYY-MM-DD>\

How to use (once):
1) Copy the whole folder "AutoFire_Hub" into your repo root (e.g. C:\Dev\AutoFireBase\AutoFire_Hub\)
2) Right‑click Start_Hub.ps1 -> Run with PowerShell
   (If Windows blocks it, open PowerShell as Admin and run:  Set-ExecutionPolicy -Scope CurrentUser Bypass)
3) On first run, the menu will use defaults from agent.config.json (edit if your paths differ).

Menu options (plain English):
[1] Start My Day     -> git status, optional git pull, opens Repo + today's logs folder
[2] Build Project    -> runs scripts\Build_AutoFire.ps1 (placeholder included)
[3] Run Tests        -> runs scripts\Run_Tests.ps1 (placeholder included)
[4] Create Branch    -> asks for a name and makes feat/<name> from main
[5] Commit Helper    -> guides you through Conventional Commit message
[6] Wrap Up & Clean  -> version bump -> tag -> build -> copy to updater -> backup -> safe clean (with confirm)
[7] CI Lab           -> pick a CI, copy prompt, create placeholder file, open it
[8] Quick Links      -> open Repo, Updater, Docs, Logs
[9] Toggle Watch     -> (future) file watcher stub; prints a message
[0] Exit

Notes:
- The Build script creates dist\AutoFire_TEST_<timestamp>.zip so you have an artifact to test the flow.
- The Wrap‑Up step NEVER deletes tracked files. It shows a preview, asks you to confirm first.
- You can edit agent.config.json to change paths or the main branch name.