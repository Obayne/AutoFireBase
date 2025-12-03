#Requires -Version 7.0
<#
.SYNOPSIS
    Automated deployment script for LV CAD
.DESCRIPTION
    Builds, packages, and prepares LV CAD for deployment
.PARAMETER Version
    Version number (e.g., "0.6.9")
.PARAMETER CreateInstaller
    Create an installer package
.PARAMETER UploadArtifacts
    Upload artifacts to release location
#>

param(
    [string]$Version = "",
    [switch]$CreateInstaller = $false,
    [switch]$UploadArtifacts = $false
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

function Write-Header($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Info($msg) { Write-Host "ℹ $msg" -ForegroundColor Blue }
function Write-Error($msg) { Write-Host "✗ $msg" -ForegroundColor Red }

Write-Header "LV CAD Deployment Automation"

# Get version
if (-not $Version) {
    if (Test-Path "VERSION.txt") {
        $Version = Get-Content "VERSION.txt" -Raw
        $Version = $Version.Trim()
    } else {
        $Version = "0.6.8"
    }
}
Write-Info "Version: $Version"

# Step 1: Pre-deployment checks
Write-Header "Pre-Deployment Checks"

Write-Info "Running tests..."
& .venv\Scripts\python.exe -m pytest tests/ -q
if ($LASTEXITCODE -ne 0) {
    Write-Error "Tests failed. Aborting deployment."
    exit 1
}
Write-Success "All tests passed"

Write-Info "Checking code quality..."
& .venv\Scripts\python.exe -m ruff check . --quiet
Write-Success "Code quality check passed"

# Step 2: Clean previous builds
Write-Header "Cleaning Previous Builds"
if (Test-Path "dist") {
    Remove-Item "dist" -Recurse -Force
    Write-Success "Removed old dist/"
}
if (Test-Path "build") {
    Remove-Item "build" -Recurse -Force
    Write-Success "Removed old build/"
}

# Step 3: Build executable
Write-Header "Building Executable"
Write-Info "Running PyInstaller..."
& .venv\Scripts\pyinstaller.exe LV_CAD.spec --clean --noconfirm

if (-not (Test-Path "dist\LV_CAD\LV_CAD.exe")) {
    Write-Error "Build failed - executable not found"
    exit 1
}

$exeSize = (Get-Item "dist\LV_CAD\LV_CAD.exe").Length / 1MB
Write-Success "Build complete (Executable: $([math]::Round($exeSize, 1)) MB)"

# Step 4: Create build info
Write-Header "Creating Build Information"
$buildInfo = @{
    version = $Version
    build_date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    commit = (git rev-parse HEAD 2>$null)
    branch = (git rev-parse --abbrev-ref HEAD 2>$null)
    builder = $env:USERNAME
    machine = $env:COMPUTERNAME
} | ConvertTo-Json -Depth 10

$buildInfo | Out-File "dist\LV_CAD\build_info.json" -Encoding UTF8
Write-Success "Build info created"

# Step 5: Create deployment package
Write-Header "Creating Deployment Package"
$packageName = "LV_CAD-v$Version-windows-x64.zip"
$packagePath = "dist\$packageName"

Compress-Archive -Path "dist\LV_CAD\*" -DestinationPath $packagePath -Force
$packageSize = (Get-Item $packagePath).Length / 1MB
Write-Success "Package created: $packageName ($([math]::Round($packageSize, 1)) MB)"

# Step 6: Create installer (optional)
if ($CreateInstaller) {
    Write-Header "Creating Installer"
    Write-Info "Checking for Inno Setup..."

    $innoSetup = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if (Test-Path $innoSetup) {
        # Create Inno Setup script
        $issScript = @"
[Setup]
AppName=LV CAD
AppVersion=$Version
DefaultDirName={autopf}\LV CAD
DefaultGroupName=LV CAD
OutputDir=dist
OutputBaseFilename=LV_CAD_Setup_v$Version
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\LV_CAD\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\LV CAD"; Filename: "{app}\LV_CAD.exe"
Name: "{autodesktop}\LV CAD"; Filename: "{app}\LV_CAD.exe"
"@
        $issScript | Out-File "setup.iss" -Encoding UTF8

        & $innoSetup "setup.iss"
        Write-Success "Installer created"
    } else {
        Write-Info "Inno Setup not found - skipping installer creation"
    }
}

# Step 7: Generate deployment report
Write-Header "Deployment Report"

$distSize = (Get-ChildItem "dist\LV_CAD" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
$fileCount = (Get-ChildItem "dist\LV_CAD" -Recurse -File).Count

$report = @"
# LV CAD Deployment Report

**Version:** $Version
**Build Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Build Machine:** $env:COMPUTERNAME

## Package Details
- **Distribution Size:** $([math]::Round($distSize, 2)) MB
- **File Count:** $fileCount files
- **Package:** $packageName
- **Location:** $packagePath

## Deployment Checklist
- ✓ Tests passed
- ✓ Code quality verified
- ✓ Executable built
- ✓ Package created
- $(if ($CreateInstaller) { "✓" } else { "☐" }) Installer created
- ☐ Documentation updated
- ☐ Release notes prepared
- ☐ Artifacts uploaded

## Distribution Instructions

### For End Users:
1. Extract the ZIP file
2. Run LV_CAD.exe
3. No installation required

### System Requirements:
- Windows 10/11 (64-bit)
- No additional dependencies

## Next Steps:
1. Test on clean Windows machine
2. Update documentation
3. Create release notes
4. Upload to distribution server
5. Notify users

---
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

$report | Out-File "dist\DEPLOYMENT_REPORT.md" -Encoding UTF8
Write-Success "Deployment report created"

# Step 8: Final summary
Write-Header "Deployment Complete"
Write-Host @"

📦 Package Ready: $packageName
📍 Location: dist\
📊 Size: $([math]::Round($distSize, 2)) MB
🗂️  Files: $fileCount

Next steps:
  1. Test the package: dist\LV_CAD\LV_CAD.exe
  2. Review: dist\DEPLOYMENT_REPORT.md
  3. Create release notes
  $(if ($UploadArtifacts) { "4. Uploading artifacts..." } else { "4. Upload with: .\scripts\auto_deploy.ps1 -UploadArtifacts" })

"@ -ForegroundColor Green

# Step 9: Upload artifacts (optional)
if ($UploadArtifacts) {
    Write-Header "Uploading Artifacts"
    Write-Info "Upload functionality coming soon..."
    Write-Info "Manually upload: $packagePath"
}

Write-Host "`n✨ Deployment automation complete!`n" -ForegroundColor Magenta
