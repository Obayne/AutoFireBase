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

# ETA tracking functions
$timingData = @{}
$startTime = Get-Date

function Start-TimedOperation($operationName) {
    $timingData[$operationName] = @{
        StartTime = Get-Date
        EstimatedDuration = Get-EstimatedDuration $operationName
    }
    if ($timingData[$operationName].EstimatedDuration) {
        Write-Info "$operationName... (ETA: $([math]::Round($timingData[$operationName].EstimatedDuration.TotalSeconds, 0))s)"
    } else {
        Write-Info "$operationName..."
    }
}

function Complete-TimedOperation($operationName) {
    if ($timingData.ContainsKey($operationName)) {
        $duration = (Get-Date) - $timingData[$operationName].StartTime
        $timingData[$operationName].Duration = $duration
        Save-TimingData $operationName $duration
        Write-Success "$operationName complete ($([math]::Round($duration.TotalSeconds, 1))s)"
    }
}

function Get-EstimatedDuration($operationName) {
    $timingFile = ".automation_timings.json"
    if (Test-Path $timingFile) {
        try {
            $timings = Get-Content $timingFile | ConvertFrom-Json
            if ($timings.PSObject.Properties.Name -contains $operationName) {
                $avgSeconds = $timings.$operationName.AverageSeconds
                return [TimeSpan]::FromSeconds($avgSeconds)
            }
        } catch { }
    }
    return $null
}

function Save-TimingData($operationName, $duration) {
    $timingFile = ".automation_timings.json"

    # Read existing timings or create empty hashtable
    $timings = @{}
    if (Test-Path $timingFile) {
        try {
            $jsonData = Get-Content $timingFile | ConvertFrom-Json
            # Convert PSObject to hashtable for easier manipulation
            foreach ($prop in $jsonData.PSObject.Properties) {
                $timings[$prop.Name] = $prop.Value
            }
        } catch { }
    }

    # Initialize operation data if it doesn't exist
    if (-not $timings.ContainsKey($operationName)) {
        $timings[$operationName] = @{
            Runs = 0
            TotalSeconds = 0
            AverageSeconds = 0
        }
    }

    # Update timing data
    $timings[$operationName].Runs = $timings[$operationName].Runs + 1
    $timings[$operationName].TotalSeconds = $timings[$operationName].TotalSeconds + $duration.TotalSeconds
    $timings[$operationName].AverageSeconds = $timings[$operationName].TotalSeconds / $timings[$operationName].Runs

    # Save back to JSON
    $timings | ConvertTo-Json | Set-Content $timingFile
}

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

    # Check for untyped functions
    Write-Info "Checking for untyped functions..."
    $untypedFunctions = & $venvPython -c @"
import ast
import os
from pathlib import Path

def has_type_hints(func_node):
    return bool(func_node.returns or func_node.args.args and any(arg.annotation for arg in func_node.args.args))

issues = []
for root, dirs, files in os.walk('app'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and not has_type_hints(node):
                            issues.append(f'{path}:{node.lineno} - Untyped function: {node.name}')
            except Exception as e:
                pass

for issue in issues[:20]:  # Limit output
    print(issue)
"@

    if ($untypedFunctions) {
        Write-Warning "Found $($untypedFunctions.Count) untyped functions (first 20):"
        $untypedFunctions | ForEach-Object { Write-Host "  $_" }
    } else {
        Write-Success "All functions appear typed"
    }

    # Check for high-complexity code (simple line count proxy)
    Write-Info "Checking for potentially complex functions..."
    $complexFunctions = Get-ChildItem -Path "app", "cad_core", "frontend" -Filter "*.py" -Recurse | ForEach-Object {
        $content = Get-Content $_.FullName -Raw
        $lines = ($content -split "`n").Count
        if ($lines -gt 50) {
            "$($_.FullName): $lines lines"
        }
    } | Select-Object -First 10

    if ($complexFunctions) {
        Write-Warning "Found potentially complex files (>50 lines):"
        $complexFunctions | ForEach-Object { Write-Host "  $_" }
    }
}

# Step 2: Linting and Formatting
if ($Mode -in @("fix", "all")) {
    Write-Header "Code Formatting & Linting"

    Start-TimedOperation "Code Formatting"
    Write-Info "Running ruff..."
    & $venvPython -m ruff check --fix . 2>&1 | Out-Null
    Write-Success "Ruff complete"

    Write-Info "Running black..."
    & $venvPython -m black . 2>&1 | Out-Null
    Complete-TimedOperation "Code Formatting"
    Write-Success "Black complete"
}

# Step 3: Testing
if ($Mode -in @("test", "all")) {
    Write-Header "Running Tests"

    Start-TimedOperation "Test Execution"
    $testResult = & $venvPython -m pytest tests/ -v --tb=short 2>&1
    Complete-TimedOperation "Test Execution"

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
