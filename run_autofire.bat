@echo off
setlocal
cd /d "%~dp0"
echo [AutoFire] Ensuring Python packages...
python -m pip install --upgrade pip >NUL 2>&1
python -m pip install -r requirements.txt
echo [AutoFire] Launching...
python -m app.main %*
endlocal
