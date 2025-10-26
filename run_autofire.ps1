# AutoFire Launcher (PowerShell)
Write-Host "Starting AutoFire..." -ForegroundColor Green
try {
    # Prefer module form to avoid relying on a specific script path across branches
    & python -m frontend.app
} catch {
    Write-Host "Error running AutoFire: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
