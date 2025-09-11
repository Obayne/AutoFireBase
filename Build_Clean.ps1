
Write-Host "==============================================="
Write-Host " AutoFire — Clean build folders & processes"
Write-Host "==============================================="

# Stop running EXE if present
Write-Host "Stopping any running AutoFire.exe ..."
Get-Process AutoFire -ErrorAction SilentlyContinue | Stop-Process -Force

Start-Sleep -Milliseconds 600

# Close leftover handles from PowerShell launching the EXE (best effort)
$null = Get-Process AutoFire -ErrorAction SilentlyContinue | Stop-Process -Force

# Clean build output
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

SafeRemove ".\dist\AutoFire"
SafeRemove ".\build\AutoFire"

Write-Host "Clean step done."
