@echo off
REM LV CAD Total Automation Setup
REM This script sets up everything automatically

echo 🚀 Setting up LV CAD Total Automation...
echo.

echo 📦 Installing Python dependencies...
call .venv\Scripts\activate.bat
pip install -r requirements.txt
pip install -r requirements-dev.txt
echo ✅ Dependencies installed
echo.

echo 🔧 Setting up automated maintenance...
powershell.exe -ExecutionPolicy Bypass -File "scripts\auto_maintain.ps1" -Schedule
echo ✅ Scheduled maintenance configured
echo.

echo 📚 Generating initial documentation...
powershell.exe -ExecutionPolicy Bypass -File "scripts\auto_docs.ps1"
echo ✅ Documentation generated
echo.

echo 🧪 Running initial test suite...
powershell.exe -ExecutionPolicy Bypass -File "scripts\auto_complete.ps1" -Mode test
echo ✅ Tests completed
echo.

echo 🎉 Setup complete! Your automation is now fully operational.
echo.
echo Quick commands:
echo   • .\scripts\auto_all.ps1          - Complete automation
echo   • .\scripts\auto_complete.ps1     - Development checks
echo   • .\scripts\auto_deploy.ps1       - Build and deploy
echo   • .\scripts\auto_pr.ps1           - Create PR
echo   • .\scripts\auto_release.ps1      - Create release
echo.
echo The system will maintain itself automatically!
echo.
pause
