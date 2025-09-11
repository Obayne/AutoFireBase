@echo off
setlocal
echo ===============================================
echo  AutoFire - Open Crash Logs
echo ===============================================

set userlog=%USERPROFILE%\AutoFire\logs\last_crash.txt
set exelog=

if exist ".\dist\AutoFire\logs\last_crash.txt" set exelog=.\dist\AutoFire\logs\last_crash.txt

if "%exelog%"=="" (
  for /f "delims=" %%F in ('dir /ad /o:-d /b ".\dist" ^| findstr /r "^AutoFire_[0-9]"') do (
    if exist ".\dist\%%F\AutoFire\logs\last_crash.txt" (
      set exelog=.\dist\%%F\AutoFire\logs\last_crash.txt
      goto :found
    )
  )
)

:found
if exist "%userlog%" (
  echo Opening: %userlog%
  start notepad "%userlog%"
) else (
  echo No user log at %userlog%
)

if not "%exelog%"=="" (
  if exist "%exelog%" (
    echo Opening: %exelog%
    start notepad "%exelog%"
  ) else (
    echo No EXE-side log found at %exelog%
  )
) else (
  echo No EXE-side log path detected.
)

echo.
echo If no logs opened, either the app did not crash or the logging patch is missing.
pause
