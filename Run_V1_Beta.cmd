@echo off
setlocal
cd /d %~dp0

if exist .\.venv\Scripts\activate.bat (
  call .\.venv\Scripts\activate.bat
)

set PYTHONPATH=
set QT_QPA_PLATFORM=
set AUTOFIRE_NO_SPLASH=1

set SRC=%CD%\unified_app\src
if not exist "%SRC%" (
  echo Sandbox not found: %SRC%
  echo Run tools\generate_module_manifest.py then tools\clone_minimal_tree.py first.
  exit /b 2
)

set PYTHONPATH=%SRC%
python "%SRC%\autofire_professional_integrated.py"
