# Build Sphinx Documentation (Windows)

param(
    [Parameter()]
    [ValidateSet("html", "clean", "serve", "help")]
    [string]$Target = "html"
)

$ErrorActionPreference = "Stop"

Write-Host "AutoFire Documentation Builder" -ForegroundColor Cyan
Write-Host ""

switch ($Target) {
    "html" {
        Write-Host "Building HTML documentation..." -ForegroundColor Yellow
        sphinx-build -b html . _build\html

        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✓ Documentation built successfully" -ForegroundColor Green
            Write-Host "  Output: _build\html\index.html" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "To view: Start-Process _build\html\index.html" -ForegroundColor Yellow
        } else {
            Write-Host "✗ Build failed" -ForegroundColor Red
            exit 1
        }
    }

    "clean" {
        Write-Host "Cleaning built documentation..." -ForegroundColor Yellow
        if (Test-Path "_build") {
            Remove-Item "_build" -Recurse -Force
            Write-Host "✓ Clean complete" -ForegroundColor Green
        } else {
            Write-Host "Nothing to clean" -ForegroundColor Gray
        }
    }

    "serve" {
        # Build first
        & $PSCommandPath -Target html

        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "Starting documentation server..." -ForegroundColor Yellow
            Write-Host "  URL: http://localhost:8000" -ForegroundColor Cyan
            Write-Host "  Press Ctrl+C to stop" -ForegroundColor Yellow
            Write-Host ""

            python -m http.server 8000 --directory _build\html
        }
    }

    "help" {
        Write-Host "Available targets:" -ForegroundColor Yellow
        Write-Host "  .\build.ps1 html    - Build HTML documentation" -ForegroundColor Gray
        Write-Host "  .\build.ps1 clean   - Remove built documentation" -ForegroundColor Gray
        Write-Host "  .\build.ps1 serve   - Build and serve documentation locally" -ForegroundColor Gray
        Write-Host "  .\build.ps1 help    - Show this help message" -ForegroundColor Gray
    }
}
