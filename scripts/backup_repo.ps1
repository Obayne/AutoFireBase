<#
Creates a timestamped zip of the repository (excluding .git and common large/ignored folders).
Run from the repo root in PowerShell: .\scripts\backup_repo.ps1
#>
param(
    [string]$OutDir = "backups",
    [switch]$IncludeUntracked
)

Set-StrictMode -Version Latest

$now = Get-Date -Format "yyyyMMdd-HHmmss"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent

if (-not (Test-Path $repoRoot)) { Write-Error "Cannot determine repo root"; exit 1 }

$outDirFull = Join-Path $repoRoot $OutDir
New-Item -ItemType Directory -Path $outDirFull -Force | Out-Null

$zipName = "autofire-backup-$now.zip"
$zipPath = Join-Path $outDirFull $zipName

Write-Host "Creating backup: $zipPath"

# Build list of files to include (exclude .git and typical virtualenv/build directories)
$exclude = @('.git', 'venv', '.venv', 'build', 'dist', '__pycache__')

$files = Get-ChildItem -Path $repoRoot -Recurse -Force | Where-Object {
    $p = $_.FullName
    foreach ($e in $exclude) { if ($p -like "*\\$e*") { return $false } }
    return $true
}

# Create a temporary folder and copy files there to preserve permissions
$tmp = Join-Path $env:TEMP ("autofire_backup_$now")
if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
New-Item -ItemType Directory -Path $tmp | Out-Null

foreach ($f in $files) {
    $rel = $f.FullName.Substring($repoRoot.Length).TrimStart('\')
    $dest = Join-Path $tmp $rel
    if ($f.PSIsContainer) { New-Item -ItemType Directory -Path $dest -Force | Out-Null }
    else {
        $d = Split-Path $dest -Parent
        if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
        Copy-Item -Path $f.FullName -Destination $dest -Force
    }
}

# Zip
[System.IO.Compression.ZipFile]::CreateFromDirectory($tmp, $zipPath)

# Cleanup
Remove-Item -Recurse -Force $tmp

Write-Host "Backup created: $zipPath"

# Add a metadata manifest inside the zip for easy inspection
try {
    $meta = @{ created = $now; git_head = (git rev-parse --short HEAD 2>$null) ; python = (Get-Command python -ErrorAction SilentlyContinue).Source }
    $metaJson = ($meta | ConvertTo-Json -Depth 4)
    $tmpMeta = Join-Path $env:TEMP ("autofire_backup_meta_$now.json")
    $metaJson | Out-File -FilePath $tmpMeta -Encoding utf8
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::Open($zipPath, [System.IO.Compression.ZipArchiveMode]::Update)
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $tmpMeta, "backup_manifest.json") | Out-Null
    $zip.Dispose()
    Remove-Item $tmpMeta -Force
} catch {
    Write-Host "Warning: could not add metadata to zip: $_"
}

# Mark zip as read-only to emphasize reference-only status
try { Set-ItemProperty -LiteralPath $zipPath -Name IsReadOnly -Value $true } catch {}
