# Optimized AutoFire Build with Caching
# Uses incremental builds and smart caching for faster rebuilds

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  AutoFire Optimized Build (with caching)" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$DIST_DIR = ".\dist\AutoFire"
$BUILD_DIR = ".\build\AutoFire"
$CACHE_DIR = ".\build\.cache"
$SPEC_FILE = "AutoFire.spec"

# Create cache directory
if (-not (Test-Path $CACHE_DIR)) {
    New-Item -ItemType Directory -Path $CACHE_DIR -Force | Out-Null
}

# Function to get file hash for change detection
function Get-FileHash-MD5 {
    param($Path)
    if (Test-Path $Path) {
        return (Get-FileHash -Path $Path -Algorithm MD5).Hash
    }
    return $null
}

# Function to check if rebuild is needed
function Test-NeedsRebuild {
    $hashFile = Join-Path $CACHE_DIR "build.hash"

    # Get current source hash
    $sourceFiles = Get-ChildItem -Path "app", "backend", "cad_core", "frontend" -Recurse -Filter "*.py" -ErrorAction SilentlyContinue
    $currentHash = ($sourceFiles | Get-FileHash -Algorithm MD5 | Select-Object -ExpandProperty Hash) -join ""

    if (Test-Path $hashFile) {
        $lastHash = Get-Content $hashFile -Raw
        if ($currentHash -eq $lastHash) {
            Write-Host "✓ No source changes detected - using cached build" -ForegroundColor Green
            return $false
        }
    }

    # Save new hash
    $currentHash | Set-Content $hashFile
    return $true
}

# Warn for OneDrive
if ($PWD.Path -match "OneDrive") {
    Write-Warning "Building inside OneDrive - sync can interfere with build"
    Write-Warning "Consider pausing OneDrive or moving to C:\Dev\AutoFireBase"
    Write-Host ""
}

# Check if rebuild is needed
$needsRebuild = Test-NeedsRebuild

if (-not $needsRebuild -and (Test-Path "$DIST_DIR\AutoFire.exe")) {
    Write-Host "Build is up to date!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Output: $DIST_DIR\AutoFire.exe" -ForegroundColor Cyan

    $exeSize = (Get-Item "$DIST_DIR\AutoFire.exe").Length / 1MB
    Write-Host "Size: $([math]::Round($exeSize, 2)) MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To force rebuild: Remove-Item .\build\.cache\build.hash" -ForegroundColor Yellow
    exit 0
}

# Install/verify dependencies
Write-Host "Checking dependencies..." -ForegroundColor Yellow

$depsHash = Join-Path $CACHE_DIR "deps.hash"
$currentDepsHash = (Get-FileHash -Path "requirements.txt" -Algorithm MD5).Hash

$needsDepsInstall = $true
if (Test-Path $depsHash) {
    $lastDepsHash = Get-Content $depsHash -Raw
    if ($currentDepsHash -eq $lastDepsHash) {
        Write-Host "✓ Dependencies unchanged" -ForegroundColor Green
        $needsDepsInstall = $false
    }
}

if ($needsDepsInstall) {
    Write-Host "Installing/updating dependencies..." -ForegroundColor Yellow
    python -m pip install -q --upgrade pip
    python -m pip install -q -r requirements.txt
    python -m pip install -q pyinstaller
    $currentDepsHash | Set-Content $depsHash
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    # Still verify PyInstaller is available
    $pyinstaller = Get-Command pyinstaller -ErrorAction SilentlyContinue
    if (-not $pyinstaller) {
        Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
        python -m pip install -q pyinstaller
    }
}

Write-Host ""

# Stop running processes
Write-Host "Stopping any running AutoFire.exe..." -ForegroundColor Yellow
Get-Process AutoFire -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 300

# Clean only if needed
if ($needsRebuild) {
    Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow

    if (Test-Path $DIST_DIR) {
        try {
            Remove-Item $DIST_DIR -Recurse -Force -ErrorAction Stop
            Write-Host "✓ Removed dist directory" -ForegroundColor Green
        } catch {
            Write-Warning "Could not remove dist: $($_.Exception.Message)"
        }
    }

    # Keep build cache for faster rebuilds
    Write-Host "✓ Retaining build cache for faster rebuild" -ForegroundColor Green
}

Write-Host ""

# Build
Write-Host "Building AutoFire.exe..." -ForegroundColor Cyan
Write-Host "Spec file: $SPEC_FILE" -ForegroundColor Gray
Write-Host "Output: $DIST_DIR" -ForegroundColor Gray
Write-Host ""

$buildStart = Get-Date

pyinstaller --noconfirm --distpath $DIST_DIR --workpath $BUILD_DIR $SPEC_FILE

$buildTime = (Get-Date) - $buildStart
$exitCode = $LASTEXITCODE

Write-Host ""

if ($exitCode -ne 0) {
    Write-Host "✗ Build FAILED (exit code: $exitCode)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check error messages above" -ForegroundColor Gray
    Write-Host "  2. Try: Remove-Item .\build -Recurse -Force" -ForegroundColor Gray
    Write-Host "  3. Verify Python environment: python --version" -ForegroundColor Gray
    Write-Host "  4. Check spec file: $SPEC_FILE" -ForegroundColor Gray
    exit $exitCode
}

# Verify output
if (-not (Test-Path "$DIST_DIR\AutoFire.exe")) {
    Write-Host "✗ Build completed but AutoFire.exe not found!" -ForegroundColor Red
    exit 1
}

# Success
Write-Host "✓ Build SUCCESSFUL" -ForegroundColor Green
Write-Host ""
Write-Host "Build time: $([math]::Round($buildTime.TotalSeconds, 1)) seconds" -ForegroundColor Cyan

$exeSize = (Get-Item "$DIST_DIR\AutoFire.exe").Length / 1MB
Write-Host "Executable size: $([math]::Round($exeSize, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output location:" -ForegroundColor White
Write-Host "  $DIST_DIR\AutoFire.exe" -ForegroundColor Cyan
Write-Host ""

# Optional: Show dependencies count
$depsCount = (Get-ChildItem "$DIST_DIR" -File).Count
Write-Host "Total files in dist: $depsCount" -ForegroundColor Gray
Write-Host ""

Write-Host "To run: .\dist\AutoFire\AutoFire.exe" -ForegroundColor Yellow
Write-Host "Or use: .\Run_Latest_Build.cmd" -ForegroundColor Yellow
