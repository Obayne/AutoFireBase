@echo off
title AutoFire - One-Click Build
echo ===============================================
echo   AutoFire - One-Click Build
echo ===============================================

REM Ensure deps
py -3 -m pip install -U pip PySide6 ezdxf packaging pyinstaller

REM Stop any running exe (prevents "Access is denied" during rebuild)
taskkill /f /im AutoFire.exe >nul 2>&1

REM Clean previous output (ignore errors)
rmdir /s /q "dist\\AutoFire" 2>nul
rmdir /s /q "build\\AutoFire" 2>nul

REM Build using the spec file if it exists; else build from app\\boot.py
if exist "AutoFire.spec" (
  py -3 -m PyInstaller --noconfirm AutoFire.spec
) else (
  py -3 -m PyInstaller --noconfirm --name AutoFire --windowed app\\boot.py
)

if errorlevel 1 (
  echo.
  echo ERROR: PyInstaller failed. See the messages above.
  pause
  exit /b 1
)

echo.
echo Build complete. Output:
echo   dist\\AutoFire\\AutoFire.exe
echo.
echo Launching...
start "" "dist\\AutoFire\\AutoFire.exe"
