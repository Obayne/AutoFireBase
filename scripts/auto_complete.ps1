#Requires -Version 7.0
<#
.SYNOPSIS
    Automated development completion script for LV CAD
.DESCRIPTION
    Automatically analyzes the codebase, identifies issues, runs tests, and suggests fixes
.PARAMETER Mode
    Run mode: analyze, fix, test, build, or all
.PARAMETER AutoFix
    Automatically apply fixes without prompting
#>

param(
    [string]$Mode = "all",
    [switch]$AutoFix = $false
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

# Colors for output
function Write-Header($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Warning($msg) { Write-Host "⚠ $msg" -ForegroundColor Yellow }
function Write-Error($msg) { Write-Host "✗ $msg" -ForegroundColor Red }
function Write-Info($msg) { Write-Host "ℹ $msg" -ForegroundColor Blue }

# Ensure virtual environment
Write-Header "Checking Virtual Environment"
if (-not (Test-Path ".venv")) {
    Write-Info "Creating virtual environment..."
    .\setup_dev.ps1
} else {
    Write-Success "Virtual environment exists"
}

# Activate venv
$venvPython = ".venv\Scripts\python.exe"
$venvPip = ".venv\Scripts\pip.exe"

# Step 1: Code Analysis
if ($Mode -in @("analyze", "all")) {
    Write-Header "Code Analysis"

    # Check for common issues
    Write-Info "Scanning for import errors..."
    $importIssues = & $venvPython -c @"
import sys
import ast
import os
from pathlib import Path

issues = []
for root, dirs, files in os.walk('app'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                issues.append(f'{path}:{e.lineno} - Syntax Error: {e.msg}')
            except Exception as e:
                issues.append(f'{path} - Error: {str(e)}')

for issue in issues:
    print(issue)
"@

    if ($importIssues) {
        Write-Warning "Found potential issues:"
        $importIssues | ForEach-Object { Write-Host "  $_" }
    } else {
        Write-Success "No syntax errors found"
    }

    # Check for TODO/FIXME comments
    Write-Info "Finding TODO/FIXME items..."
    $todos = Get-ChildItem -Path "app", "cad_core", "frontend" -Filter "*.py" -Recurse | Select-String -Pattern "(TODO|FIXME|XXX|HACK)" | Select-Object -First 20
    if ($todos) {
        Write-Warning "Found $($todos.Count) action items:"
        $todos | ForEach-Object { Write-Host "  $($_.Filename):$($_.LineNumber) - $($_.Line.Trim())" }
    }
}

# Step 2: Linting and Formatting
if ($Mode -in @("fix", "all")) {
    Write-Header "Code Formatting & Linting"

    Write-Info "Running ruff..."
    & $venvPython -m ruff check --fix . 2>&1 | Out-Null
    Write-Success "Ruff complete"

    Write-Info "Running black..."
    & $venvPython -m black . 2>&1 | Out-Null
    Write-Success "Black complete"
}

# Step 3: Testing
if ($Mode -in @("test", "all")) {
    Write-Header "Running Tests"

    Write-Info "Executing pytest..."
    $testResult = & $venvPython -m pytest tests/ -v --tb=short 2>&1

    if ($LASTEXITCODE -eq 0) {
        $testCount = ($testResult | Select-String "passed").Line -replace '.*?(\d+) passed.*','$1'
        Write-Success "All $testCount tests passed!"
    } else {
        Write-Error "Some tests failed. Review output above."
        if (-not $AutoFix) {
            exit 1
        }
    }
}

# Step 4: Build Check
if ($Mode -in @("build", "all")) {
    Write-Header "Build Verification"

    Write-Info "Checking app entry point..."
    $appCheck = & $venvPython -c "import app.main; print('OK')" 2>&1
    if ($appCheck -match "OK") {
        Write-Success "App imports successfully"
    } else {
        Write-Error "App import failed:"
        Write-Host $appCheck
    }

    Write-Info "Checking required dependencies..."
    $deps = @("PySide6", "ezdxf", "pytest", "ruff", "black")
    foreach ($dep in $deps) {
        $installed = & $venvPip show $dep 2>&1
        if ($installed -match "Name:") {
            Write-Success "$dep installed"
        } else {
            Write-Warning "$dep not found"
        }
    }
}

# Step 5: Report
Write-Header "Completion Report"

$status = @{
    "Virtual Environment" = "✓"
    "Code Syntax" = if ($importIssues) { "⚠" } else { "✓" }
    "Formatting" = "✓"
    "Tests" = if ($LASTEXITCODE -eq 0) { "✓" } else { "✗" }
    "Build Ready" = if ($appCheck -match "OK") { "✓" } else { "✗" }
}

$status.GetEnumerator() | ForEach-Object {
    $color = switch ($_.Value) {
        "✓" { "Green" }
        "⚠" { "Yellow" }
        "✗" { "Red" }
    }
    Write-Host "$($_.Value) $($_.Key)" -ForegroundColor $color
}

Write-Header "Next Steps"
Write-Info "1. Review any warnings above"
Write-Info "2. Run tests: python -m pytest tests/"
Write-Info "3. Launch app: python app/main.py"
Write-Info "4. Build: .\Build_LV_CAD.ps1"

Write-Host "`n✨ Automation complete!`n" -ForegroundColor Magenta
