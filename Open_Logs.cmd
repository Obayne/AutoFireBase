@echo off
setlocal
echo ===============================================
echo  Open Crash Logs
echo ===============================================

set userlog1=%USERPROFILE%\AlarmForge\logs\last_crash.txt
set userlog2=%USERPROFILE%\AutoFire\logs\last_crash.txt
set exelog=

if exist ".\dist\AlarmForge\logs\last_crash.txt" set exelog=.\dist\AlarmForge\logs\last_crash.txt
if "%exelog%"=="" if exist ".\dist\AutoFire\logs\last_crash.txt" set exelog=.\dist\AutoFire\logs\last_crash.txt

if "%exelog%"=="" (
  for /f "delims=" %%F in ('dir /ad /o:-d /b ".\dist" ^| findstr /r "^AlarmForge_[0-9]"') do (
    if exist ".\dist\%%F\AlarmForge\logs\last_crash.txt" (
      set exelog=.\dist\%%F\AlarmForge\logs\last_crash.txt
      goto :found
    )
  )
  for /f "delims=" %%F in ('dir /ad /o:-d /b ".\dist" ^| findstr /r "^AutoFire_[0-9]"') do (
    if exist ".\dist\%%F\AutoFire\logs\last_crash.txt" (
      set exelog=.\dist\%%F\AutoFire\logs\last_crash.txt
      goto :found
    )
  )
)

:found
if exist "%userlog1%" (
  echo Opening: %userlog1%
  start notepad "%userlog1%"
) else if exist "%userlog2%" (
  echo Opening: %userlog2%
  start notepad "%userlog2%"
) else (
  echo No user log found in user profile.
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
