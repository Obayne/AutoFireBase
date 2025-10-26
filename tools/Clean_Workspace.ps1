param(
    [switch]$Force = $false,
    [int]$KeepArtifacts = 2,
    [int]$LogDays = 14
)

# Safe workspace cleanup with WhatIf by default
# Targets: build/, dist/, __pycache__/, .pytest_cache/, .ruff_cache/, *.spec-build, logs older than N days
# Never touches source files.

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $root\..
try {
    Write-Host "Workspace: $(Get-Location)"

    $targets = @(
        'build',
        'dist',
        '.pytest_cache',
        '.ruff_cache'
    )

    $patterns = @(
        '**/__pycache__'
    )

    $totalBytes = 0

    foreach ($t in $targets) {
        if (Test-Path $t) {
            $size = (Get-ChildItem -Path $t -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            $totalBytes += [int64]($size)
            if ($Force) {
                Remove-Item -Path $t -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "Removed: $t"
            } else {
                Write-Host "Would remove: $t"
            }
        }
    }

    foreach ($p in $patterns) {
        $dirs = Get-ChildItem -Path $p -Directory -Recurse -Force -ErrorAction SilentlyContinue
        foreach ($d in $dirs) {
            $size = (Get-ChildItem -Path $d.FullName -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            $totalBytes += [int64]($size)
            if ($Force) {
                Remove-Item -Path $d.FullName -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "Removed: $($d.FullName)"
            } else {
                Write-Host "Would remove: $($d.FullName)"
            }
        }
    }

    # Prune logs older than $LogDays in logs/
    if (Test-Path 'logs') {
        $threshold = (Get-Date).AddDays(-$LogDays)
        $oldLogs = Get-ChildItem logs -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -lt $threshold }
        foreach ($f in $oldLogs) {
            $totalBytes += [int64]($f.Length)
            if ($Force) {
                Remove-Item $f.FullName -Force -ErrorAction SilentlyContinue
            } else {
                Write-Host "Would remove old log: $($f.FullName)"
            }
        }
    }

    # Keep last N artifacts in artifacts/ if present
    if (Test-Path 'artifacts') {
        $groups = Get-ChildItem artifacts -Directory -Force -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
        $toRemove = $groups | Select-Object -Skip $KeepArtifacts
        foreach ($g in $toRemove) {
            $size = (Get-ChildItem -Path $g.FullName -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            $totalBytes += [int64]($size)
            if ($Force) {
                Remove-Item -Path $g.FullName -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "Removed artifact set: $($g.Name)"
            } else {
                Write-Host "Would remove artifact set: $($g.Name)"
            }
        }
    }

    $mb = [math]::Round($totalBytes / 1MB, 2)
    if ($Force) {
        Write-Host "Reclaimed ~${mb} MB"
    } else {
        Write-Host "Dry-run: would reclaim ~${mb} MB (run with -Force to delete)"
    }
}
finally {
    Pop-Location
}
