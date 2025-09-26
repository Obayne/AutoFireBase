@echo off
setlocal

set DOCS=%~dp0docs
if not exist "%DOCS%" (
  echo docs/ folder not found next to this script.
  exit /b 1
)

echo Opening AutoFire help files...
start "" "%DOCS%\UserGuide.md"
start "" "%DOCS%\Shortcuts.md"
explorer "%DOCS%"

exit /b 0

