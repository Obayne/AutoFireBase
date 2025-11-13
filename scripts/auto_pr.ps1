Param(
  [string]$Branch = "chore/auto-pr/$(Get-Date -Format yyyyMMdd_HHmmss)",
  [switch]$Draft
)

$ErrorActionPreference = 'Stop'

function Activate-Venv {
  if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    . .\.venv\Scripts\Activate.ps1
  } elseif (Test-Path ".\setup_dev.ps1") {
    Write-Host "Creating virtual environment via setup_dev.ps1" -ForegroundColor Cyan
    .\setup_dev.ps1
    . .\.venv\Scripts\Activate.ps1
  } else {
    Write-Warning "No venv found and setup_dev.ps1 missing; proceeding without venv"
  }
}

function Ensure-GitClean {
  $status = git status --porcelain
  if ($status) { Write-Host "Working tree has changes; they will be included in this PR." -ForegroundColor Yellow }
}

function Run-Quality {
  Write-Host "Running ruff+black" -ForegroundColor Cyan
  ruff check --fix .
  black .
  Write-Host "Running pytest" -ForegroundColor Cyan
  pytest -q
}

Activate-Venv
Ensure-GitClean

Write-Host "Creating branch $Branch" -ForegroundColor Cyan
 git checkout -b $Branch

Run-Quality

Write-Host "Committing changes" -ForegroundColor Cyan
 git add -A
 git commit -m "chore(auto): format, lint, and tests via automation"
 git push --set-upstream origin $Branch

# Create PR if gh is available
if (Get-Command gh -ErrorAction SilentlyContinue) {
  $draftFlag = if ($Draft) { "--draft" } else { "" }
  gh pr create $draftFlag --title "chore(auto): format/lint/test" --body "Automated lint+test run and PR creation."
} else {
  Write-Host "GitHub CLI not found; PR not created. Use the link from 'git push' or install gh." -ForegroundColor Yellow
}
