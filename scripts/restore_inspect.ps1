<#
Extracts a backup zip to a temporary inspection folder. This is intentionally non-destructive
and will not overwrite files in the working tree. It prints the extraction path for manual inspection
or branch creation.

Usage: .\scripts\restore_inspect.ps1 -ZipPath backups\autofire-backup-YYYYMMDD-HHMMSS.zip
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$ZipPath
)

if (-not (Test-Path $ZipPath)) { Write-Error "Zip not found: $ZipPath"; exit 1 }

$now = Get-Date -Format "yyyyMMdd-HHmmss"
$tmp = Join-Path $env:TEMP ("autofire_restore_inspect_$now")
New-Item -ItemType Directory -Path $tmp | Out-Null

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($ZipPath, $tmp)

Write-Host "Backup extracted to (inspection only): $tmp"
Write-Host "To restore selectively: copy files from this folder into a new branch or use the GitHub UI to compare and create a PR."
