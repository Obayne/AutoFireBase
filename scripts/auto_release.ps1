#Requires -Version 7.0
<#
.SYNOPSIS
    Automated release management for LV CAD
.DESCRIPTION
    Bumps version, generates changelog, creates release notes, and publishes release
.PARAMETER Version
    Target version (e.g., "1.0.0")
.PARAMETER Type
    Release type: major, minor, patch
.PARAMETER Draft
    Create draft release
.PARAMETER PreRelease
    Mark as pre-release
#>

param(
    [string]$Version = "",
    [ValidateSet('major','minor','patch')]
    [string]$Type = 'patch',
    [switch]$Draft = $false,
    [switch]$PreRelease = $false
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

function Write-Header($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Info($msg) { Write-Host "ℹ $msg" -ForegroundColor Blue }
function Write-Error($msg) { Write-Host "✗ $msg" -ForegroundColor Red }

Write-Header "LV CAD Automated Release"

# Ensure we're on main branch and clean
Write-Info "Checking git status..."
$branch = git rev-parse --abbrev-ref HEAD
if ($branch -ne "main") {
    Write-Error "Must be on main branch for release. Current branch: $branch"
    exit 1
}

$status = git status --porcelain
if ($status) {
    Write-Error "Working directory is not clean. Please commit or stash changes."
    exit 1
}

Write-Success "Git status OK"

# Determine version
if (-not $Version) {
    Write-Info "Bumping version ($Type)..."
    .\scripts\bump_version.ps1 -Part $Type
    $Version = Get-Content VERSION.txt -Raw
} else {
    Write-Info "Setting version to $Version..."
    $Version | Out-File VERSION.txt -Encoding UTF8
}

Write-Success "Version set to $Version"

# Run full automation suite
Write-Header "Running Pre-Release Automation"
Write-Info "Running complete automation suite..."
.\scripts\auto_complete.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Error "Automation failed. Cannot proceed with release."
    exit 1
}

Write-Success "All checks passed"

# Generate documentation
Write-Info "Generating release documentation..."
.\scripts\auto_docs.ps1

# Build and package
Write-Header "Building Release Package"
Write-Info "Creating deployment package..."
.\scripts\auto_deploy.ps1 -Version $Version -CreateInstaller

# Generate release notes
Write-Header "Generating Release Notes"

$changelog = Get-Content CHANGELOG.md -Raw
$releaseNotes = @"
# LV CAD v$Version

$(Get-Date -Format "yyyy-MM-dd")

## What's New

$($changelog -split '## \[' | Select-Object -Skip 1 | Select-Object -First 1)

## Installation

### For Windows Users:
1. Download `LV_CAD_Setup_v$Version.exe`
2. Run the installer
3. Launch LV CAD from the Start menu

### For Developers:
```bash
pip install -r requirements.txt
python app/main.py
```

## System Requirements
- Windows 10/11 (64-bit)
- Python 3.11+ (for development)
- 4GB RAM minimum
- 2GB disk space

## Verification
- SHA256: $(Get-FileHash "dist\LV_CAD_Setup_v$Version.exe" -Algorithm SHA256 | Select-Object -ExpandProperty Hash)

## Links
- [Documentation](https://your-repo.github.io/docs/)
- [Issues](https://github.com/your-repo/issues)
- [Discussions](https://github.com/your-repo/discussions)

---
*This release was automatically generated and tested.*
"@

$releaseNotes | Out-File "RELEASE_NOTES_v$Version.md" -Encoding UTF8
Write-Success "Release notes generated"

# Commit and tag
Write-Header "Committing Release"
Write-Info "Committing version bump and documentation..."
git add .
git commit -m "chore(release): prepare v$Version`n`n- Update version to $Version`n- Generate documentation`n- Update changelog`n- Build release package"
git tag "v$Version"

Write-Success "Release committed and tagged"

# Push to remote
Write-Header "Publishing Release"
Write-Info "Pushing to remote repository..."
git push origin main
git push origin "v$Version"

Write-Success "Release pushed to remote"

# Create GitHub release
if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Info "Creating GitHub release..."

    $releaseArgs = @(
        "release", "create", "v$Version",
        "--title", "LV CAD v$Version",
        "--notes-file", "RELEASE_NOTES_v$Version.md"
    )

    if ($Draft) { $releaseArgs += "--draft" }
    if ($PreRelease) { $releaseArgs += "--prerelease" }

    # Add assets
    if (Test-Path "dist\LV_CAD_Setup_v$Version.exe") {
        $releaseArgs += "dist\LV_CAD_Setup_v$Version.exe"
    }
    if (Test-Path "dist\LV_CAD-v$Version-windows-x64.zip") {
        $releaseArgs += "dist\LV_CAD-v$Version-windows-x64.zip"
    }

    & gh @releaseArgs
    Write-Success "GitHub release created"
} else {
    Write-Info "GitHub CLI not found - manual release creation required"
    Write-Info "Upload these files to GitHub releases:"
    Get-ChildItem dist\*.exe, dist\*.zip | ForEach-Object { Write-Host "  - $($_.Name)" }
}

Write-Header "Release Complete"

$releaseSummary = @"
🚀 LV CAD v$Version Released!

📦 Package: dist\LV_CAD-v$Version-windows-x64.zip
📋 Release Notes: RELEASE_NOTES_v$Version.md
🏷️  Tag: v$Version
🌐 GitHub Release: $(if (Get-Command gh -ErrorAction SilentlyContinue) { "Created" } else { "Manual creation needed" })

Next Steps:
1. Test the release on a clean Windows machine
2. Announce the release in your community
3. Monitor for any issues
4. Plan the next development cycle
"@

Write-Host $releaseSummary -ForegroundColor Green

Write-Host "`n✨ Automated release complete!`n" -ForegroundColor Magenta
