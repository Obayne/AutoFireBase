# Build AutoFire Windows Installer
# Requires: PyInstaller, NSIS installed

param(
    [switch]$SkipBuild,      # Skip PyInstaller build
    [switch]$SkipInstaller,  # Skip NSIS compilation
    [switch]$Clean           # Clean dist/build folders first
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$InstallerDir = Join-Path $RepoRoot "installer"
$DistDir = Join-Path $RepoRoot "dist"
$BuildDir = Join-Path $RepoRoot "build"
$Version = (Get-Content (Join-Path $RepoRoot "VERSION.txt")).Trim()

Write-Host "`n🔨 AutoFire Installer Build Script" -ForegroundColor Cyan
Write-Host "==================================`n" -ForegroundColor Cyan

# Clean if requested
if ($Clean) {
    Write-Host "🧹 Cleaning build directories..." -ForegroundColor Yellow
    if (Test-Path $DistDir) { Remove-Item $DistDir -Recurse -Force }
    if (Test-Path $BuildDir) { Remove-Item $BuildDir -Recurse -Force }
    Write-Host "✓ Cleaned`n" -ForegroundColor Green
}

# Step 1: Build with PyInstaller
if (-not $SkipBuild) {
    Write-Host "📦 Building executable with PyInstaller..." -ForegroundColor Yellow

    # Check if build script exists
    $BuildScript = Join-Path $RepoRoot "Build_LV_CAD.ps1"
    if (-not (Test-Path $BuildScript)) {
        Write-Host "❌ Build_LV_CAD.ps1 not found!" -ForegroundColor Red
        exit 1
    }

    # Run the existing build script
    Push-Location $RepoRoot
    try {
        & $BuildScript
        if ($LASTEXITCODE -ne 0) {
            throw "PyInstaller build failed with exit code $LASTEXITCODE"
        }
        Write-Host "✓ Executable built successfully`n" -ForegroundColor Green
    }
    finally {
        Pop-Location
    }

    # Verify output
    $ExePath = Join-Path $DistDir "LV_CAD\LV_CAD\LV_CAD.exe"
    if (-not (Test-Path $ExePath)) {
        Write-Host "❌ LV_CAD.exe not found in dist folder!" -ForegroundColor Red
        Write-Host "   Expected at: $ExePath" -ForegroundColor Yellow
        exit 1
    }

    $ExeSize = (Get-Item $ExePath).Length / 1MB
    Write-Host "  📊 Executable size: $([math]::Round($ExeSize, 2)) MB`n" -ForegroundColor Gray
}

# Step 2: Build NSIS installer
if (-not $SkipInstaller) {
    Write-Host "📦 Building NSIS installer..." -ForegroundColor Yellow

    # Check for NSIS
    $NSIS = "C:\Program Files (x86)\NSIS\makensis.exe"
    if (-not (Test-Path $NSIS)) {
        Write-Host "❌ NSIS not found at: $NSIS" -ForegroundColor Red
        Write-Host "   Download from: https://nsis.sourceforge.io/" -ForegroundColor Yellow
        exit 1
    }

    # Compile installer
    $NSIScript = Join-Path $InstallerDir "autofire-installer.nsi"
    if (-not (Test-Path $NSIScript)) {
        Write-Host "❌ Installer script not found: $NSIScript" -ForegroundColor Red
        exit 1
    }

    Push-Location $InstallerDir
    try {
        & $NSIS "/DAPP_VERSION=$Version" $NSIScript
        if ($LASTEXITCODE -ne 0) {
            throw "NSIS compilation failed with exit code $LASTEXITCODE"
        }
        Write-Host "✓ Installer built successfully`n" -ForegroundColor Green
    }
    finally {
        Pop-Location
    }

    # Verify installer
    $InstallerPath = Join-Path $InstallerDir "LV_CAD-$Version-Setup.exe"
    if (Test-Path $InstallerPath) {
        $InstallerSize = (Get-Item $InstallerPath).Length / 1MB
        Write-Host "  📊 Installer size: $([math]::Round($InstallerSize, 2)) MB" -ForegroundColor Gray
        Write-Host "  📁 Location: $InstallerPath`n" -ForegroundColor Gray
    }
}

Write-Host "✅ Build complete!`n" -ForegroundColor Green

# Summary
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Test installer on clean Windows VM" -ForegroundColor Gray
Write-Host "  2. Verify desktop/start menu shortcuts" -ForegroundColor Gray
Write-Host "  3. Test file association (.afire files)" -ForegroundColor Gray
Write-Host "  4. Test uninstaller" -ForegroundColor Gray
