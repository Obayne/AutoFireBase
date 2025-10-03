# AutoFire PowerShell Profile Setup
# Run this once to set up automation aliases

$profileContent = @'
# AutoFire Development Aliases
# Added automatically by setup script

function autofire-dev {
    param([switch]$Help)
    if ($Help) {
        Write-Host "AutoFire Development Commands:"
        Write-Host "autofire-dev -help    : Show this help"
        Write-Host "autofire-setup        : Initial project setup"
        Write-Host "autofire-run          : Run AutoFire application"
        Write-Host "autofire-test         : Run all tests"
        Write-Host "autofire-build        : Build production executable"
        Write-Host "autofire-quality      : Run full quality checks"
        Write-Host "autofire-status       : Show project status"
        return
    }
    Write-Host "Use 'autofire-dev -Help' for available commands"
}

function autofire-setup {
    cd C:\Dev\Autofire
    if (!(Test-Path ".venv")) {
        Write-Host "Setting up development environment..."
        .\setup_dev.ps1
    } else {
        Write-Host "Environment already set up. Use 'autofire-dev -Help' for commands."
    }
}

function autofire-run {
    cd C:\Dev\Autofire
    if (!(Test-Path ".venv")) {
        Write-Host "Environment not set up. Run 'autofire-setup' first."
        return
    }
    . .venv/Scripts/Activate.ps1
    python main.py
}

function autofire-test {
    cd C:\Dev\Autofire
    if (!(Test-Path ".venv")) {
        Write-Host "Environment not set up. Run 'autofire-setup' first."
        return
    }
    . .venv/Scripts/Activate.ps1
    pytest -q
}

function autofire-build {
    cd C:\Dev\Autofire
    if (!(Test-Path ".venv")) {
        Write-Host "Environment not set up. Run 'autofire-setup' first."
        return
    }
    . .venv/Scripts/Activate.ps1
    .\Build_AutoFire.ps1
}

function autofire-quality {
    cd C:\Dev\Autofire
    if (!(Test-Path ".venv")) {
        Write-Host "Environment not set up. Run 'autofire-setup' first."
        return
    }
    . .venv/Scripts/Activate.ps1
    Write-Host "Running code formatting..."
    black .
    Write-Host "Running linting..."
    ruff check --fix .
    Write-Host "Running tests..."
    pytest -q
    Write-Host "Quality check complete!"
}

function autofire-status {
    cd C:\Dev\Autofire
    Write-Host "=== AutoFire Project Status ==="
    Write-Host "Project: C:\Dev\Autofire"

    if (Test-Path ".venv") {
        Write-Host "✓ Development environment: Set up"
    } else {
        Write-Host "✗ Development environment: Not set up (run autofire-setup)"
    }

    if (Test-Path "main.py") {
        Write-Host "✓ Main application: Present"
    } else {
        Write-Host "✗ Main application: Missing"
    }

    $testCount = (Get-ChildItem tests/ -Recurse -Filter "test_*.py" | Measure-Object).Count
    Write-Host "✓ Tests: $testCount test files found"

    if (Test-Path ".git") {
        $branch = git branch --show-current
        Write-Host "✓ Git repository: Active (branch: $branch)"
    } else {
        Write-Host "✗ Git repository: Not initialized"
    }

    Write-Host ""
    Write-Host "Available commands:"
    Write-Host "  autofire-setup   : Set up development environment"
    Write-Host "  autofire-run     : Run AutoFire application"
    Write-Host "  autofire-test    : Run tests"
    Write-Host "  autofire-build   : Build executable"
    Write-Host "  autofire-quality : Run quality checks"
    Write-Host "  autofire-status  : Show this status"
}
'@

# Check if profile exists, create if not
if (!(Test-Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force | Out-Null
    Write-Host "Created PowerShell profile: $PROFILE"
}

# Add AutoFire aliases to profile
Add-Content -Path $PROFILE -Value $profileContent
Write-Host "Added AutoFire development aliases to PowerShell profile"
Write-Host ""
Write-Host "Available commands (restart PowerShell or run '. $PROFILE'):"
Write-Host "  autofire-setup   : Initial project setup"
Write-Host "  autofire-run     : Run AutoFire application"
Write-Host "  autofire-test    : Run tests"
Write-Host "  autofire-build   : Build executable"
Write-Host "  autofire-quality : Full quality checks"
Write-Host "  autofire-status  : Show project status"
Write-Host ""
Write-Host "Run 'autofire-dev -Help' for detailed help"
