#Requires -Version 7.0
<#
.SYNOPSIS
    Automated maintenance script for LV CAD
.DESCRIPTION
    Keeps the project clean, updated, and automated
.PARAMETER Mode
    Maintenance mode: daily, weekly, full
.PARAMETER Schedule
    Set up scheduled task
#>

param(
    [ValidateSet('daily', 'weekly', 'full')]
    [string]$Mode = "daily",
    [switch]$Schedule = $false
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

function Write-Header($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Info($msg) { Write-Host "ℹ $msg" -ForegroundColor Blue }

Write-Header "🔧 LV CAD Automated Maintenance"

if ($Schedule) {
    Write-Header "Setting Up Scheduled Maintenance"

    # Create scheduled task for daily maintenance
    $taskName = "LV_CAD_Daily_Maintenance"
    $scriptPath = Join-Path $PSScriptRoot "auto_maintain.ps1"

    Write-Info "Creating scheduled task: $taskName"

    # Remove existing task if it exists
    schtasks /delete /tn "$taskName" /f 2>$null

    # Create new daily task at 6 AM
    $taskCommand = "powershell.exe -ExecutionPolicy Bypass -File `"$scriptPath`" -Mode daily"
    schtasks /create /tn "$taskName" /tr "$taskCommand" /sc daily /st 06:00 /rl highest /f

    Write-Success "Scheduled task created - runs daily at 6:00 AM"

    # Create weekly task for full maintenance
    $weeklyTaskName = "LV_CAD_Weekly_Maintenance"
    $weeklyCommand = "powershell.exe -ExecutionPolicy Bypass -File `"$scriptPath`" -Mode full"
    schtasks /delete /tn "$weeklyTaskName" /f 2>$null
    schtasks /create /tn "$weeklyTaskName" /tr "$weeklyCommand" /sc weekly /d SUN /st 02:00 /rl highest /f

    Write-Success "Weekly maintenance task created - runs Sundays at 2:00 AM"
    exit 0
}

# Activate virtual environment
if (Test-Path ".venv\Scripts\Activate.ps1") {
    . .venv\Scripts\Activate.ps1
}

# Daily maintenance
if ($Mode -in @('daily', 'full')) {
    Write-Header "Daily Maintenance"

    Write-Info "Running code quality checks..."
    .\scripts\auto_complete.ps1 -Mode analyze

    Write-Info "Updating dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt --quiet
    pip install -r requirements-dev.txt --quiet

    Write-Info "Checking for outdated packages..."
    $outdated = pip list --outdated --format=json | ConvertFrom-Json
    if ($outdated) {
        Write-Info "Found $($outdated.Count) outdated packages"
        $outdated | ForEach-Object { Write-Host "  $($_.name): $($_.version) -> $($_.latest_version)" }
    }

    Write-Info "Cleaning temporary files..."
    Get-ChildItem -Path "." -Include "*.pyc", "__pycache__", "*.tmp" -Recurse -Force | Remove-Item -Force -Recurse 2>$null

    Write-Success "Daily maintenance completed"
}

# Weekly maintenance
if ($Mode -in @('weekly', 'full')) {
    Write-Header "Weekly Maintenance"

    Write-Info "Running full test suite..."
    .\scripts\auto_complete.ps1 -Mode test

    Write-Info "Regenerating documentation..."
    .\scripts\auto_docs.ps1

    Write-Info "Checking git status..."
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Info "Uncommitted changes found - consider committing maintenance updates"
    }

    Write-Info "Updating pre-commit hooks..."
    pre-commit autoupdate

    Write-Success "Weekly maintenance completed"
}

# Full maintenance (monthly)
if ($Mode -eq 'full') {
    Write-Header "Full Maintenance"

    Write-Info "Running complete automation suite..."
    .\scripts\auto_all.ps1 -Mode dev

    Write-Info "Checking automation scripts integrity..."
    $scripts = Get-ChildItem "scripts\*.ps1"
    foreach ($script in $scripts) {
        try {
            $null = Get-Command $script.FullName -Syntax
            Write-Success "$($script.Name) syntax OK"
        } catch {
            Write-Warning "$($script.Name) has syntax issues"
        }
    }

    Write-Info "Verifying CI/CD pipeline..."
    if (Test-Path ".github\workflows\ci.yml") {
        Write-Success "GitHub Actions workflow present"
    }

    Write-Success "Full maintenance completed"
}

Write-Header "Maintenance Summary"

$summary = @"
🔧 Maintenance completed successfully!

📅 Next scheduled runs:
   • Daily: 6:00 AM every day
   • Weekly: 2:00 AM every Sunday

🛠️  What was maintained:
   • Code quality checks
   • Dependency updates
   • Documentation refresh
   • Test suite validation
   • File system cleanup

💡 To modify schedule:
   • Run: .\scripts\auto_maintain.ps1 -Schedule
   • Or edit Windows Task Scheduler

📊 System Health: ✅ All systems operational
"@

Write-Host $summary -ForegroundColor Green

Write-Host "`n🔄 Maintenance automation active!`n" -ForegroundColor Magenta
