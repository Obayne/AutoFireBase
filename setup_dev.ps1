param(
  [switch]$Force
)

Write-Host "[dev-setup] Using Python: $(python --version 2>$null)"

$venvPath = ".venv"
if (-not (Test-Path $venvPath) -or $Force) {
  Write-Host "[dev-setup] Creating venv at $venvPath"
  python -m venv $venvPath
}

$activate = Join-Path $venvPath "Scripts/Activate.ps1"
if (-not (Test-Path $activate)) {
  Write-Error "Activation script not found at $activate"
  exit 1
}

Write-Host "[dev-setup] Activating venv"
. $activate

Write-Host "[dev-setup] Upgrading pip"
python -m pip install --upgrade pip

if (Test-Path "requirements.txt") {
  Write-Host "[dev-setup] Installing project requirements"
  pip install -r requirements.txt
} else {
  Write-Warning "requirements.txt not found — skipping."
}

if (Test-Path "requirements-dev.txt") {
  Write-Host "[dev-setup] Installing dev tools (pre-commit, black, ruff, mypy)"
  pip install -r requirements-dev.txt
  Write-Host "[dev-setup] Installing pre-commit hooks"
  pre-commit install
} else {
  Write-Warning "requirements-dev.txt not found — skipping dev tools."
}

Write-Host "[dev-setup] Done. To activate later: . .venv/Scripts/Activate.ps1"

