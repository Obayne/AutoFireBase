#Requires -Version 7.0
<#
.SYNOPSIS
    Complete automation suite for LV CAD - runs all automation in sequence
.DESCRIPTION
    Executes the full automation pipeline: development, testing, documentation, building, and deployment
.PARAMETER Mode
    Automation mode: dev, test, build, deploy, release, all
.PARAMETER SkipTests
    Skip running tests
.PARAMETER SkipDocs
    Skip documentation generation
#>

param(
    [ValidateSet('dev', 'test', 'build', 'deploy', 'release', 'all')]
    [string]$Mode = "all",
    [switch]$SkipTests = $false,
    [switch]$SkipDocs = $false
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

function Write-Header($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Info($msg) { Write-Host "ℹ $msg" -ForegroundColor Blue }
function Write-Error($msg) { Write-Host "✗ $msg" -ForegroundColor Red }

Write-Header "🚀 LV CAD Total Automation Suite"

$startTime = Get-Date
Write-Info "Started at: $startTime"

# Phase 1: Development Automation
if ($Mode -in @('dev', 'all')) {
    Write-Header "Phase 1: Development Automation"

    Write-Info "Running auto_complete.ps1..."
    .\scripts\auto_complete.ps1

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Development automation failed"
        exit 1
    }

    Write-Success "Development automation completed"
}

# Phase 2: Testing
if ($Mode -in @('test', 'all') -and -not $SkipTests) {
    Write-Header "Phase 2: Testing"

    Write-Info "Running comprehensive tests..."
    .\scripts\auto_complete.ps1 -Mode test

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Testing failed"
        exit 1
    }

    Write-Success "All tests passed"
}

# Phase 3: Documentation
if ($Mode -in @('build', 'deploy', 'release', 'all') -and -not $SkipDocs) {
    Write-Header "Phase 3: Documentation Generation"

    Write-Info "Generating documentation..."
    .\scripts\auto_docs.ps1

    Write-Success "Documentation generated"
}

# Phase 4: Building
if ($Mode -in @('build', 'deploy', 'release', 'all')) {
    Write-Header "Phase 4: Building"

    Write-Info "Building application..."
    .\scripts\auto_deploy.ps1 -Version (Get-Content VERSION.txt -Raw)

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Build failed"
        exit 1
    }

    Write-Success "Build completed"
}

# Phase 5: Deployment/Release
if ($Mode -in @('deploy', 'all')) {
    Write-Header "Phase 5: Deployment"

    Write-Info "Creating deployment package..."
    .\scripts\auto_deploy.ps1 -Version (Get-Content VERSION.txt -Raw) -CreateInstaller

    Write-Success "Deployment package created"
}

if ($Mode -eq 'release') {
    Write-Header "Phase 5: Release"

    Write-Info "Creating full release..."
    .\scripts\auto_release.ps1 -Type patch

    Write-Success "Release completed"
}

# Final Report
Write-Header "🎉 Automation Complete!"

$endTime = Get-Date
$duration = $endTime - $startTime

$report = @"
📊 Automation Summary:
   ⏱️  Duration: $([math]::Round($duration.TotalSeconds, 1)) seconds
   📅 Started: $startTime
   🏁 Finished: $endTime
   🎯 Mode: $Mode

📦 Generated Artifacts:
"@

if (Test-Path "dist") {
    $artifacts = Get-ChildItem dist -Recurse -File | Where-Object { $_.Name -match '\.(exe|zip|md)$' } | ForEach-Object { "   📄 $($_.Name) ($([math]::Round($_.Length / 1MB, 2)) MB)" }
    $report += "`n" + ($artifacts -join "`n")
}

$report += @"

🚀 Quick Commands:
   • Run app: python app/main.py
   • Test app: .\scripts\auto_complete.ps1 -Mode test
   • Build app: .\scripts\auto_deploy.ps1
   • Create PR: .\scripts\auto_pr.ps1
   • Full release: .\scripts\auto_release.ps1

📚 Documentation:
   • API Docs: docs/api/index.html
   • Code Analysis: docs/CODEBASE_ANALYSIS.md
   • Automation Guide: AUTOMATION_COMPLETE.md

✨ Your LV CAD project is fully automated and ready for development!
"@

Write-Host $report -ForegroundColor Green

Write-Host "`n🎊 Total automation successful!`n" -ForegroundColor Magenta
