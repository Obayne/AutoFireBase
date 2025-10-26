# Runs the v1 beta from the clean sandbox (unified_app/src) with GUI
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath "$PSScriptRoot"

# Activate venv if present
if (Test-Path .\.venv\Scripts\Activate.ps1) {
    . .\.venv\Scripts\Activate.ps1
}

# Ensure GUI platform (unset headless overrides)
Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue | Out-Null
Remove-Item Env:AUTOFIRE_NO_SPLASH -ErrorAction SilentlyContinue | Out-Null

$src = Join-Path (Get-Location) 'unified_app\src'
if (-not (Test-Path $src)) {
    Write-Host "Sandbox not found: $src`nRun tools/generate_module_manifest.py then tools/clone_minimal_tree.py first." -ForegroundColor Yellow
    exit 2
}

$env:PYTHONPATH = $src
Write-Host "Launching v1 beta from: $src" -ForegroundColor Cyan
python "$src\autofire_professional_integrated.py"
