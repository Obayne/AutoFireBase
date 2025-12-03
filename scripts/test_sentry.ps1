#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Test Sentry integration for AutoFire.

.DESCRIPTION
    This script tests the Sentry error tracking integration by:
    1. Verifying sentry-sdk is installed
    2. Running integration tests
    3. Optionally sending a test error to Sentry dashboard

.PARAMETER SendTestError
    If specified, sends a real test error to Sentry (requires SENTRY_DSN)

.PARAMETER DsnFromFile
    Read Sentry DSN from a file instead of environment variable

.EXAMPLE
    .\scripts\test_sentry.ps1
    Run tests without sending real errors

.EXAMPLE
    .\scripts\test_sentry.ps1 -SendTestError
    Run tests and send a test error to Sentry dashboard
#>

param(
    [switch]$SendTestError,
    [string]$DsnFromFile
)

$ErrorActionPreference = "Stop"

Write-Host "🔍 Testing Sentry Integration..." -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
if (Test-Path ".venv/Scripts/Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Gray
    . .venv/Scripts/Activate.ps1
}

# Check sentry-sdk installation
Write-Host "📦 Checking sentry-sdk installation..." -ForegroundColor Yellow
$sentryVersion = pip show sentry-sdk 2>$null | Select-String -Pattern "Version:"
if ($sentryVersion) {
    Write-Host "✅ sentry-sdk installed: $sentryVersion" -ForegroundColor Green
} else {
    Write-Host "❌ sentry-sdk not found. Installing..." -ForegroundColor Red
    pip install sentry-sdk
}
Write-Host ""

# Load DSN from file if specified
if ($DsnFromFile -and (Test-Path $DsnFromFile)) {
    Write-Host "📄 Loading SENTRY_DSN from file: $DsnFromFile" -ForegroundColor Yellow
    $dsn = Get-Content $DsnFromFile -Raw
    $env:SENTRY_DSN = $dsn.Trim()
    Write-Host "✅ DSN loaded from file" -ForegroundColor Green
    Write-Host ""
}

# Check if DSN is configured
$hasDsn = $env:SENTRY_DSN -ne $null -and $env:SENTRY_DSN -ne ""
if ($hasDsn) {
    $maskedDsn = $env:SENTRY_DSN -replace '(?<=https://).+(?=@)', '***'
    Write-Host "✅ SENTRY_DSN configured: $maskedDsn" -ForegroundColor Green
} else {
    Write-Host "⚠️  SENTRY_DSN not configured (tests will be limited)" -ForegroundColor Yellow
    Write-Host "   To test with real Sentry:" -ForegroundColor Gray
    Write-Host "   1. Get DSN from https://sentry.io/settings/projects/" -ForegroundColor Gray
    Write-Host "   2. Set: `$env:SENTRY_DSN = 'your-dsn-here'" -ForegroundColor Gray
    Write-Host "   3. Or save to file: .\scripts\test_sentry.ps1 -DsnFromFile .sentry-dsn" -ForegroundColor Gray
}
Write-Host ""

# Run integration tests
Write-Host "🧪 Running Sentry integration tests..." -ForegroundColor Cyan
pytest tests/integration/test_sentry_integration.py -v

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests failed" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "✅ All integration tests passed!" -ForegroundColor Green
Write-Host ""

# Send test error if requested
if ($SendTestError) {
    if (-not $hasDsn) {
        Write-Host "❌ Cannot send test error: SENTRY_DSN not configured" -ForegroundColor Red
        exit 1
    }

    Write-Host "🚀 Sending test error to Sentry dashboard..." -ForegroundColor Cyan
    pytest tests/integration/test_sentry_integration.py::TestSentryErrorSimulation::test_trigger_test_error_for_sentry -v -m manual

    Write-Host ""
    Write-Host "✅ Test error sent! Check your Sentry dashboard:" -ForegroundColor Green
    Write-Host "   https://sentry.io/organizations/your-org/issues/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Look for: 'This is a TEST error from pytest to verify Sentry integration'" -ForegroundColor Gray
}

Write-Host ""
Write-Host "✅ Sentry integration test complete!" -ForegroundColor Green
