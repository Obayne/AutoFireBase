@echo off
REM Quick start for full automation

echo ===============================================
echo  LV CAD - Full Automation Quick Start
echo ===============================================
echo.

echo Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Ollama is not running!
    echo Please start Ollama first: ollama serve
    echo.
    pause
    exit /b 1
)
echo [OK] Ollama is running

echo.
echo Checking DeepSeek Coder...
ollama list | findstr "deepseek-coder" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] DeepSeek Coder not found!
    echo Installing DeepSeek Coder...
    ollama pull deepseek-coder
)
echo [OK] DeepSeek Coder ready

echo.
echo ===============================================
echo  Starting Full Automation Pipeline
echo ===============================================
echo.
echo The system will:
echo  1. Read tasks from tasks/ directory
echo  2. Use AI to implement each task
echo  3. Run automated tests
echo  4. Create PRs for review
echo  5. Wait for your approval
echo  6. Auto-merge approved PRs
echo.
echo You only need to:
echo  - Review and test each PR
echo  - Approve on GitHub when ready
echo.
echo Press Ctrl+C to stop at any time
echo.
pause

powershell -ExecutionPolicy Bypass -File "%~dp0scripts\full_auto.ps1"

pause
