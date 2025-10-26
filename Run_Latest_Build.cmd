@echo off
setlocal
echo ===============================================
echo  Run Latest Build
echo ===============================================

rem Prefer AlarmForge, fallback to AutoFire
set exe=.\dist\AlarmForge\AlarmForge.exe
if exist "%exe%" goto :run

set exe=.\dist\AutoFire\AutoFire.exe
if exist "%exe%" goto :run

for /f "delims=" %%F in ('dir /ad /o:-d /b ".\dist" ^| findstr /r "^AutoFire_[0-9]"') do (
  if exist ".\dist\%%F\AutoFire\AutoFire.exe" (
    set exe=.\dist\%%F\AutoFire\AutoFire.exe
    goto :run
  )
)

for /f "delims=" %%F in ('dir /ad /o:-d /b ".\dist" ^| findstr /r "^AlarmForge_[0-9]"') do (
  if exist ".\dist\%%F\AlarmForge\AlarmForge.exe" (
    set exe=.\dist\%%F\AlarmForge\AlarmForge.exe
    goto :run
  )
)

echo No built EXE found in .\dist\
echo Please build first, then try again.
pause
exit /b 1

:run
echo Running: %exe%
start "" "%exe%"
exit /b 0
