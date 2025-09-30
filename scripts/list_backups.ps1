<# List available backups in the backups/ folder #>
param(
    [string]$Dir = "backups"
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$path = Join-Path $root $Dir
if (-not (Test-Path $path)) { Write-Host "No backups found (folder does not exist): $path"; exit 0 }

Get-ChildItem -Path $path -File | Sort-Object LastWriteTime -Descending | ForEach-Object {
    Write-Host "$($_.Name) - $($_.LastWriteTime) - $($_.Length) bytes"
}
