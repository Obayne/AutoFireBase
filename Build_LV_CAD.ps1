
Write-Host "==============================================="
Write-Host "  LV CAD PowerShell Build (safe, improved)"
Write-Host "==============================================="

# Warn for OneDrive (can lock files)
if ($PWD.Path -match "OneDrive") {
  Write-Warning "You're building inside OneDrive. Sync can lock files and break the build."
  Write-Warning "If you hit 'Access is denied', consider pausing OneDrive or moving the project to C:\Dev\LV_CAD"
}

# Ensure deps
Write-Host "Installing build requirements (pip, PySide6, ezdxf, packaging, pyinstaller) ..."
python -m pip install -U pip PySide6 ezdxf packaging pyinstaller | Out-Null

# Stop any running EXE and clean prior outputs
Write-Host "Stopping any running LV_CAD.exe ..."
Get-Process LV_CAD -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 600

function SafeRemove($path) {
  if (Test-Path $path) {
    try {
      Remove-Item $path -Recurse -Force -ErrorAction Stop
      Write-Host "Removed $path"
    } catch {
      Write-Warning "Could not remove $path: $($_.Exception.Message)"
    }
  }
}

SafeRemove ".\dist\LV_CAD"
SafeRemove ".\build\LV_CAD"

# Primary build
$dist = ".\dist\LV_CAD"
$work = ".\build\LV_CAD"

Write-Host "Building LV_CAD.exe ..."
pyinstaller --noconfirm --distpath $dist --workpath $work LV_CAD.spec
$code = $LASTEXITCODE

if ($code -ne 0) {
  Write-Warning "Primary build failed with exit code $code. Retrying with a fresh dist folder ..."
  $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $dist2 = ".\dist\LV_CAD_$stamp"
  # Try again
  pyinstaller --noconfirm --distpath $dist2 --workpath $work LV_CAD.spec
  $code = $LASTEXITCODE
  if ($code -ne 0) {
    Write-Error "PyInstaller failed again (exit $code). Check the console above for details."
    exit $code
  } else {
    Write-Host "Build complete. EXE:"
    Write-Host (Resolve-Path "$dist2\LV_CAD\LV_CAD.exe")
    exit 0
  }
} else {
  Write-Host "Build complete. EXE:"
  Write-Host (Resolve-Path "$dist\LV_CAD\LV_CAD.exe")
  exit 0
}
