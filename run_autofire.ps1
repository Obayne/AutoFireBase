# AutoFire Launcher (PowerShell)
Write-Host "Starting AutoFire..." -ForegroundColor Green
try {
    & python main.py
} catch {
    Write-Host "Error running AutoFire: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
