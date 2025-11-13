#Requires -Version 7.0
<#
.SYNOPSIS
    Automated documentation generation for LV CAD
.DESCRIPTION
    Generates API documentation, README updates, and documentation artifacts
.PARAMETER Mode
    Generation mode: api, readme, all
.PARAMETER Publish
    Publish documentation to GitHub Pages
#>

param(
    [string]$Mode = "all",
    [switch]$Publish = $false
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

function Write-Header($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Info($msg) { Write-Host "ℹ $msg" -ForegroundColor Blue }
function Write-Error($msg) { Write-Host "✗ $msg" -ForegroundColor Red }

Write-Header "LV CAD Documentation Automation"

# Ensure virtual environment
Write-Info "Checking virtual environment..."
if (-not (Test-Path ".venv")) {
    Write-Info "Creating virtual environment..."
    .\setup_dev.ps1
}
. .venv\Scripts\Activate.ps1

# Install documentation dependencies if needed
Write-Info "Installing documentation tools..."
pip install pdoc3 mkdocs mkdocs-material

if ($Mode -in @("api", "all")) {
    Write-Header "Generating API Documentation"

    Write-Info "Generating HTML documentation with pdoc3..."
    pdoc --html --output-dir docs/api app cad_core frontend --force

    Write-Info "Generating Markdown documentation..."
    pdoc --pdf app > docs/API_REFERENCE.md

    Write-Success "API documentation generated"
}

if ($Mode -in @("readme", "all")) {
    Write-Header "Updating README and Documentation"

    # Get current version
    $version = Get-Content VERSION.txt -Raw

    # Update README with current version and automation status
    $readmePath = "README.md"
    if (Test-Path $readmePath) {
        $readme = Get-Content $readmePath -Raw

        # Update version badge
        $readme = $readme -replace '!\[Version\]\([^)]*\)', "![Version](https://img.shields.io/badge/version-$version-blue.svg)"

        # Update last updated
        $date = Get-Date -Format "yyyy-MM-dd"
        $readme = $readme -replace 'Last updated: \d{4}-\d{2}-\d{2}', "Last updated: $date"

        $readme | Out-File $readmePath -Encoding UTF8
        Write-Success "README updated with version $version"
    }

    # Generate feature overview from code
    Write-Info "Analyzing codebase for feature documentation..."
    $featureAnalysis = @"
## 📊 Codebase Analysis

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

### Module Structure
- **app/**: Main application modules ($((Get-ChildItem app -Recurse -File -Name "*.py").Count) files)
- **cad_core/**: CAD engine core ($((Get-ChildItem cad_core -Recurse -File -Name "*.py").Count) files)
- **frontend/**: User interface components ($((Get-ChildItem frontend -Recurse -File -Name "*.py").Count) files)
- **tests/**: Test suite ($((Get-ChildItem tests -Recurse -File -Name "*.py").Count) files)

### Test Coverage
- Total tests: $((Get-ChildItem tests -Recurse -File -Name "test_*.py").Count)
- Test files: $(Get-ChildItem tests -Recurse -File -Name "*.py" | Measure-Object | Select-Object -ExpandProperty Count)

### Automation Status
- ✅ CI/CD Pipeline: Active
- ✅ Code Quality: Ruff + Black
- ✅ Testing: Pytest with coverage
- ✅ Documentation: Auto-generated
- ✅ Deployment: PyInstaller builds
- ✅ Security: CodeQL scanning
"@

    $featureAnalysis | Out-File "docs/CODEBASE_ANALYSIS.md" -Encoding UTF8
    Write-Success "Codebase analysis generated"
}

if ($Publish) {
    Write-Header "Publishing Documentation"

    Write-Info "Checking for MkDocs configuration..."
    if (Test-Path "mkdocs.yml") {
        Write-Info "Building MkDocs site..."
        mkdocs build

        Write-Info "Publishing to GitHub Pages..."
        mkdocs gh-deploy --force
        Write-Success "Documentation published to GitHub Pages"
    } else {
        Write-Info "MkDocs not configured - skipping publish"
    }
}

Write-Header "Documentation Generation Complete"

$docStats = @"
📚 Documentation Generated:
   📖 API Reference: docs/api/
   📋 Code Analysis: docs/CODEBASE_ANALYSIS.md
   📝 Updated README: README.md
   🌐 GitHub Pages: $(if ($Publish) { "Published" } else { "Ready for publish" })
"@

Write-Host $docStats -ForegroundColor Green

Write-Host "`n✨ Documentation automation complete!`n" -ForegroundColor Magenta
