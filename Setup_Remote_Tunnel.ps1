# Setup VS Code Remote Tunnel for AutoFire
# This script helps you set up remote access from your Android phone

Write-Host "=== AutoFire Remote Tunnel Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if VS Code is installed
Write-Host "Checking for VS Code installation..." -ForegroundColor Yellow
$codeCommand = Get-Command code -ErrorAction SilentlyContinue

if (-not $codeCommand) {
    Write-Host "ERROR: VS Code 'code' command not found in PATH" -ForegroundColor Red
    Write-Host "Please ensure VS Code is installed and added to PATH" -ForegroundColor Red
    Write-Host "You may need to restart PowerShell after installing VS Code" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ VS Code found at: $($codeCommand.Source)" -ForegroundColor Green
Write-Host ""

# Show options
Write-Host "Choose an option:" -ForegroundColor Cyan
Write-Host "  1. Start tunnel (interactive session)" -ForegroundColor White
Write-Host "  2. Install tunnel as Windows service (runs at startup)" -ForegroundColor White
Write-Host "  3. Check tunnel status" -ForegroundColor White
Write-Host "  4. View tunnel info" -ForegroundColor White
Write-Host "  5. Stop tunnel/service" -ForegroundColor White
Write-Host "  6. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting VS Code tunnel..." -ForegroundColor Yellow
        Write-Host "You will be prompted to sign in with GitHub or Microsoft" -ForegroundColor Cyan
        Write-Host "After signing in, you'll choose a tunnel name (e.g., 'autofire-dev')" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Press Ctrl+C to stop the tunnel when done" -ForegroundColor Yellow
        Write-Host ""
        Start-Sleep -Seconds 2

        # Start tunnel
        code tunnel
    }

    "2" {
        Write-Host ""
        Write-Host "Installing VS Code tunnel as Windows service..." -ForegroundColor Yellow
        Write-Host "The tunnel will start automatically when Windows boots" -ForegroundColor Cyan
        Write-Host ""

        # Install service
        code tunnel service install

        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✓ Tunnel service installed successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Cyan
            Write-Host "  1. The service will start automatically" -ForegroundColor White
            Write-Host "  2. On your Android, go to https://vscode.dev" -ForegroundColor White
            Write-Host "  3. Click 'Open Remote Tunnel' and sign in" -ForegroundColor White
            Write-Host "  4. Select your tunnel name" -ForegroundColor White
        } else {
            Write-Host ""
            Write-Host "✗ Failed to install tunnel service" -ForegroundColor Red
            Write-Host "Try running PowerShell as Administrator" -ForegroundColor Yellow
        }
    }

    "3" {
        Write-Host ""
        Write-Host "Checking tunnel status..." -ForegroundColor Yellow
        code tunnel status
    }

    "4" {
        Write-Host ""
        Write-Host "Tunnel Information:" -ForegroundColor Cyan
        Write-Host "==================" -ForegroundColor Cyan
        code tunnel status
        Write-Host ""
        Write-Host "To connect from Android:" -ForegroundColor Cyan
        Write-Host "  1. Open browser and go to: https://vscode.dev" -ForegroundColor White
        Write-Host "  2. Click 'Open Remote Tunnel'" -ForegroundColor White
        Write-Host "  3. Sign in with your GitHub/Microsoft account" -ForegroundColor White
        Write-Host "  4. Select your tunnel from the list" -ForegroundColor White
    }

    "5" {
        Write-Host ""
        Write-Host "Choose stop option:" -ForegroundColor Cyan
        Write-Host "  1. Stop running tunnel session" -ForegroundColor White
        Write-Host "  2. Uninstall tunnel service" -ForegroundColor White
        Write-Host ""
        $stopChoice = Read-Host "Enter choice (1-2)"

        if ($stopChoice -eq "1") {
            Write-Host ""
            Write-Host "Stopping tunnel..." -ForegroundColor Yellow
            code tunnel kill
            Write-Host "✓ Tunnel stopped" -ForegroundColor Green
        } elseif ($stopChoice -eq "2") {
            Write-Host ""
            Write-Host "Uninstalling tunnel service..." -ForegroundColor Yellow
            code tunnel service uninstall

            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Tunnel service uninstalled" -ForegroundColor Green
            } else {
                Write-Host "✗ Failed to uninstall service" -ForegroundColor Red
                Write-Host "Try running PowerShell as Administrator" -ForegroundColor Yellow
            }
        }
    }

    "6" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }

    default {
        Write-Host "Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "For more information, see: docs\REMOTE_ACCESS_SETUP.md" -ForegroundColor Cyan
