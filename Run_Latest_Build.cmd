@echo off
setlocal
echo ===============================================
echo  AutoFire - Run Latest Build
echo ===============================================

set exe=.\dist\AutoFire\AutoFire.exe
if exist "%exe%" goto :run

for /f "delims=" %%F in ('dir /ad /o:-d /b ".\dist" ^| findstr /r "^AutoFire_[0-9]"') do (
  if exist ".\dist\%%F\AutoFire\AutoFire.exe" (
    set exe=.\dist\%%F\AutoFire\AutoFire.exe
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
