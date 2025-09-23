@echo off
:: ===== K I S S  H U B =====
set "PROJECT=C:\Dev\Autofire"
set "BACKUPS=%PROJECT%\_backups"

if not exist "%PROJECT%" (
  echo Project not found: %PROJECT%
  pause
  exit /b 1
)

for /f %%i in ('powershell -NoProfile -Command "(Get-Date).ToString(\"yyyy-MM-dd_HH-mm-ss\")"') do set "TS=%%i"

:menu
cls
echo ================== AutoFire KISS ==================
echo Project: %PROJECT%
echo.
echo [1] Open Project Folder
echo [2] Save Point  (backup copy + optional Git snapshot)
echo [3] Backup THEN Clean Junk  (safe)
echo [0] Exit
echo.
set "choice="
set /p "choice=Select: "
if "%choice%"=="1" goto open
if "%choice%"=="2" goto save
if "%choice%"=="3" goto backup_clean
if "%choice%"=="0" goto bye
goto menu

:open
start "" explorer "%PROJECT%"
goto menu

:save
echo.
echo === Save Point ===
if not exist "%BACKUPS%" mkdir "%BACKUPS%"
set "DEST=%BACKUPS%\%TS%"
echo Backing up to: %DEST%
robocopy "%PROJECT%" "%DEST%" /E /XJ ^
  /XD _backups .git .venv dist build __pycache__ .pytest_cache .ruff_cache .mypy_cache .vscode .idea >nul
echo Backup done: %DEST%

:: Optional Git snapshot (silent if not set up)
where git >nul 2>&1 || goto save_done
if not exist "%PROJECT%\.git" goto save_done
git -C "%PROJECT%" add -A
git -C "%PROJECT%" commit -m "savepoint %TS%" >nul 2>&1
git -C "%PROJECT%" remote get-url origin >nul 2>&1 && git -C "%PROJECT%" push -u origin master
:save_done
echo Done.
pause
goto menu

:backup_clean
echo.
echo === Backup THEN Clean (safe) ===
if not exist "%BACKUPS%" mkdir "%BACKUPS%"
set "DEST=%BACKUPS%\%TS%"
echo Backing up to: %DEST%
robocopy "%PROJECT%" "%DEST%" /E /XJ ^
  /XD _backups >nul
echo Backup done.

echo.
echo Preview of junk to remove:
where git >nul 2>&1 && if exist "%PROJECT%\.git" (
  git -C "%PROJECT%" clean -n -dxf
) else (
  for %%D in (__pycache__ .pytest_cache .ruff_cache .mypy_cache dist build .venv) do (
    if exist "%PROJECT%\%%D" echo would remove: %%D\
  )
)
echo.
set "ans="
set /p "ans=Proceed with CLEAN now? (Y/N): "
if /I not "%ans%"=="Y" goto menu

where git >nul 2>&1 && if exist "%PROJECT%\.git" (
  git -C "%PROJECT%" clean -f -dxf
) else (
  for %%D in (__pycache__ .pytest_cache .ruff_cache .mypy_cache dist build .venv) do (
    if exist "%PROJECT%\%%D" rmdir /s /q "%PROJECT%\%%D"
  )
)
echo Clean complete.
pause
goto menu

:bye
exit /b 0
