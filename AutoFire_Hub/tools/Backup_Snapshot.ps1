param(
  [string]$Repo = (Split-Path -Parent $PSScriptRoot),
  [string]$Exclude = ".git,.venv,dist,build,archive,attic",
  [string]$OutName = "snapshot"
)
$ErrorActionPreference = "Continue"
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$archiveDir = Join-Path $Repo "archive"
New-Item -ItemType Directory -Force -Path $archiveDir | Out-Null
$zip = Join-Path $archiveDir ("{0}_{1}.zip" -f $OutName, $stamp)
$ex = $Exclude.Split(",") | ForEach-Object { $_.Trim() }
$paths = Get-ChildItem -Force -LiteralPath $Repo | Where-Object { $ex -notcontains $_.Name }
Write-Host "Snapshot -> $zip"
try {
  Compress-Archive -Path ($paths | ForEach-Object { $_.FullName }) -DestinationPath $zip -Force
  Write-Host "Snapshot complete."
} catch {
  Write-Warning "Snapshot failed: $($_.Exception.Message)"
}