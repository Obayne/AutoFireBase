#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Test Windows installer build process.

.DESCRIPTION
    This script tests the AutoFire Windows installer by:
    1. Checking if NSIS is installed
    2. Optionally downloading and installing NSIS
    3. Building the PyInstaller executable
    4. Compiling the NSIS installer
    5. Validating the installer output

.PARAMETER InstallNsis
    If specified, downloads and installs NSIS automatically

.PARAMETER SkipBuild
    Skip PyInstaller build (use existing dist/AutoFire/)

.PARAMETER NsisPath
    Custom path to NSIS installation (if not in PATH)

.EXAMPLE
    .\scripts\test_installer.ps1
    Check NSIS installation status

.EXAMPLE
    .\scripts\test_installer.ps1 -InstallNsis
    Download and install NSIS, then build installer

.EXAMPLE
    .\scripts\test_installer.ps1 -SkipBuild
    Build installer using existing PyInstaller output
#>

param(
    [switch]$InstallNsis,
    [switch]$SkipBuild,
    [string]$NsisPath
)

$ErrorActionPreference = "Stop"

Write-Host "🔧 Testing Windows Installer Build..." -ForegroundColor Cyan
Write-Host ""

# Check for NSIS installation
function Test-NsisInstalled {
    param([string]$CustomPath)

    if ($CustomPath) {
        $makensis = Join-Path $CustomPath "makensis.exe"
        return Test-Path $makensis
    }

    # Check PATH
    $inPath = Get-Command makensis -ErrorAction SilentlyContinue
    if ($inPath) {
        return $true
    }

    # Check common installation paths
    $commonPaths = @(
        "$env:ProgramFiles\NSIS\makensis.exe",
        "${env:ProgramFiles(x86)}\NSIS\makensis.exe",
        "C:\Program Files\NSIS\makensis.exe",
        "C:\Program Files (x86)\NSIS\makensis.exe"
    )

    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            Write-Host "Found NSIS at: $path" -ForegroundColor Green
            return $true
        }
    }

    return $false
}

# Install NSIS automatically
function Install-Nsis {
    Write-Host "📥 Downloading NSIS installer..." -ForegroundColor Yellow

    $nsisVersion = "3.10"
    $nsisUrl = "https://sourceforge.net/projects/nsis/files/NSIS%203/$nsisVersion/nsis-$nsisVersion-setup.exe/download"
    $installerPath = "$env:TEMP\nsis-setup.exe"

    try {
        Invoke-WebRequest -Uri $nsisUrl -OutFile $installerPath -UseBasicParsing
        Write-Host "✅ Downloaded NSIS installer" -ForegroundColor Green

        Write-Host "🔧 Installing NSIS (this may take a minute)..." -ForegroundColor Yellow
        Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait

        Write-Host "✅ NSIS installed successfully!" -ForegroundColor Green

        # Add to PATH for current session
        $nsisPath = "$env:ProgramFiles\NSIS"
        if (Test-Path $nsisPath) {
            $env:PATH += ";$nsisPath"
        }

    } catch {
        Write-Host "❌ Failed to download/install NSIS: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install NSIS manually:" -ForegroundColor Yellow
        Write-Host "1. Download from: https://nsis.sourceforge.io/Download" -ForegroundColor Gray
        Write-Host "2. Run the installer" -ForegroundColor Gray
        Write-Host "3. Restart PowerShell" -ForegroundColor Gray
        exit 1
    }
}

# Check NSIS
Write-Host "🔍 Checking for NSIS installation..." -ForegroundColor Yellow

if (-not (Test-NsisInstalled -CustomPath $NsisPath)) {
    Write-Host "❌ NSIS not found" -ForegroundColor Red
    Write-Host ""

    if ($InstallNsis) {
        Install-Nsis
    } else {
        Write-Host "NSIS is required to build the Windows installer." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Options:" -ForegroundColor Cyan
        Write-Host "1. Run with -InstallNsis flag to download and install automatically" -ForegroundColor Gray
        Write-Host "   .\scripts\test_installer.ps1 -InstallNsis" -ForegroundColor Gray
        Write-Host ""
        Write-Host "2. Install manually from: https://nsis.sourceforge.io/Download" -ForegroundColor Gray
        Write-Host ""
        exit 1
    }
} else {
    Write-Host "✅ NSIS is installed" -ForegroundColor Green

    # Get NSIS version
    $nsisExe = if ($NsisPath) {
        Join-Path $NsisPath "makensis.exe"
    } else {
        (Get-Command makensis).Source
    }

    $version = & $nsisExe /VERSION
    Write-Host "   Version: $version" -ForegroundColor Gray
}
Write-Host ""

# Check installer script
Write-Host "📄 Checking installer script..." -ForegroundColor Yellow
$installerScript = "installer\autofire-installer.nsi"
if (-not (Test-Path $installerScript)) {
    Write-Host "❌ Installer script not found: $installerScript" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Installer script found" -ForegroundColor Green
Write-Host ""

# Build installer
if ($SkipBuild) {
    Write-Host "⏭️  Skipping PyInstaller build (using existing dist/)" -ForegroundColor Yellow
} else {
    Write-Host "🔨 Building with installer/Build-Installer.ps1..." -ForegroundColor Cyan

    if (-not (Test-Path "installer\Build-Installer.ps1")) {
        Write-Host "❌ Build script not found: installer\Build-Installer.ps1" -ForegroundColor Red
        exit 1
    }

    # Run the build script
    & .\installer\Build-Installer.ps1

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build failed" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Write-Host ""
Write-Host "✅ Installer build test complete!" -ForegroundColor Green
Write-Host ""

# Show results
if (Test-Path "installer\AutoFire-Setup.exe") {
    $installerSize = (Get-Item "installer\AutoFire-Setup.exe").Length / 1MB
    Write-Host "📦 Installer created:" -ForegroundColor Cyan
    Write-Host "   Path: installer\AutoFire-Setup.exe" -ForegroundColor Gray
    Write-Host "   Size: $([math]::Round($installerSize, 2)) MB" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Test installation on a clean VM or test machine" -ForegroundColor Gray
    Write-Host "2. Verify desktop shortcut and Start Menu entry" -ForegroundColor Gray
    Write-Host "3. Test .afire file association" -ForegroundColor Gray
    Write-Host "4. Test uninstaller" -ForegroundColor Gray
} else {
    Write-Host "⚠️  Installer not found at expected location" -ForegroundColor Yellow
}
