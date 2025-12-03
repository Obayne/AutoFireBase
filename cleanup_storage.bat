@echo off
echo AutoFire Storage Cleanup Script
echo ================================
echo.

echo Current disk usage:
powershell -Command "Get-ChildItem -Path '.' -Recurse | Measure-Object -Property Length -Sum | Select-Object @{Name='TotalSizeGB'; Expression={[math]::Round($_.Sum / 1GB, 2)}}"
echo.

echo 1. Clearing Python cache files...
powershell -Command "Get-ChildItem -Path '.' -Recurse -Directory | Where-Object { $_.Name -eq '__pycache__' } | Remove-Item -Recurse -Force"
echo Cache files cleared.
echo.

echo 2. Removing build artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo Build artifacts removed.
echo.

echo 3. Cleaning log files...
powershell -Command "Get-ChildItem -Path '.' -Recurse -File | Where-Object { $_.Name -match '\.log$' } | Remove-Item -Force"
echo Log files cleaned.
echo.

echo 4. Checking for large temporary files...
powershell -Command "Get-ChildItem -Path '.' -Recurse -File | Where-Object { $_.Length -gt 100MB } | Select-Object FullName, @{Name='SizeMB'; Expression={[math]::Round($_.Length / 1MB, 2)}} | Sort-Object SizeMB -Descending"
echo.

echo Cleanup complete! New disk usage:
powershell -Command "Get-ChildItem -Path '.' -Recurse | Measure-Object -Property Length -Sum | Select-Object @{Name='TotalSizeGB'; Expression={[math]::Round($_.Sum / 1GB, 2)}}"
echo.

echo To recreate virtual environment if needed:
echo   .\setup_dev.ps1
echo.

pause
