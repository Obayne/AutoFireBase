param(
  [string]$Repo = (Split-Path -Parent $PSScriptRoot),
  [switch]$Execute
)
$ErrorActionPreference = "Continue"
Push-Location $Repo
try {
  Write-Host "Preview (untracked):" -ForegroundColor Cyan
  git clean -nd
  Write-Host "`nPreview (ignored):" -ForegroundColor Cyan
  git clean -ndX
  if ($Execute) {
    $ans = Read-Host "Run cleanup (this will NOT touch tracked files)? [y/N]"
    if ($ans -match "^[yY]") {
      git clean -fd
      git clean -fdX
      Write-Host "Cleanup done."
    } else {
      Write-Host "Skipped."
    }
  } else {
    Write-Host "`nRun with -Execute to perform cleanup."
  }
} finally {
  Pop-Location
}