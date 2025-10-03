@echo off
setlocal
cd /d "%~dp0"
echo [AutoFire] Launching...
python main.py %*
endlocal
