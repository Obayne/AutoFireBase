param(
  [string]$Repo = (Split-Path -Parent $PSScriptRoot)
)
$ErrorActionPreference = "Continue"
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$dist = Join-Path $Repo "dist"
New-Item -ItemType Directory -Force -Path $dist | Out-Null

# Placeholder "build": create a small zip to simulate an artifact
$zip = Join-Path $dist ("AutoFire_TEST_{0}.zip" -f $stamp)
Write-Host "Building artifact -> $zip"
$tempdir = Join-Path $env:TEMP ("autofire_build_" + $stamp)
New-Item -ItemType Directory -Force -Path $tempdir | Out-Null
"Build OK at $stamp" | Set-Content (Join-Path $tempdir "build.txt")

try {
  Compress-Archive -Path (Join-Path $tempdir "*") -DestinationPath $zip -Force
  Write-Host "Done."
} catch {
  Write-Warning "Compress-Archive failed: $($_.Exception.Message)"
}
Remove-Item $tempdir -Recurse -Force -ErrorAction SilentlyContinue