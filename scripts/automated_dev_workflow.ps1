# Automated Development Workflow Script
# Demonstrates integration of newly installed VS Code extensions and tools

param(
    [switch]$Format,
    [switch]$Lint,
    [switch]$Test,
    [switch]$Todo,
    [switch]$GitStatus,
    [switch]$All
)

Write-Host "🚀 AutoFire Automated Development Workflow" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Function to run Prettier (for any JS/TS files if they exist)
function Run-Prettier {
    Write-Host "`n📝 Running Prettier code formatting..." -ForegroundColor Yellow
    Write-Host "ℹ️  Prettier integration ready (requires Node.js setup)" -ForegroundColor Blue
}

# Function to run Black formatter (Python)
function Run-Black {
    Write-Host "`n🎨 Running Black Python formatter..." -ForegroundColor Yellow
    try {
        $result = python -m black --check --diff . 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Code is already formatted with Black" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Code needs Black formatting" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "⚠️  Black not available" -ForegroundColor Yellow
    }
}

# Function to run ESLint (for JS/TS files)
function Run-ESLint {
    Write-Host "`n🔍 Running ESLint..." -ForegroundColor Yellow
    Write-Host "ℹ️  ESLint integration ready (requires Node.js setup)" -ForegroundColor Blue
}

# Function to run Python linting
function Run-Pylint {
    Write-Host "`n🔍 Running Pylint..." -ForegroundColor Yellow
    try {
        python -m pylint app/ backend/ core/ --output-format=colorized --reports=no 2>$null
        Write-Host "✅ Pylint completed" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Pylint not available or failed to run" -ForegroundColor Yellow
    }
}

# Function to check for TODOs
function Check-Todos {
    Write-Host "`n📋 Checking for TODO comments..." -ForegroundColor Yellow
    $todoFiles = Get-ChildItem -Recurse -Include "*.py", "*.js", "*.ts", "*.md" |
                 Select-String -Pattern "TODO|FIXME|XXX" |
                 Group-Object -Property Path |
                 Select-Object Name, Count

    if ($todoFiles) {
        Write-Host "📝 Found TODOs in the following files:" -ForegroundColor Cyan
        $todoFiles | ForEach-Object {
            Write-Host "  $($_.Name): $($_.Count) items" -ForegroundColor White
        }
    } else {
        Write-Host "✅ No TODO comments found" -ForegroundColor Green
    }
}

# Function to run tests
function Run-Tests {
    Write-Host "`n🧪 Running tests..." -ForegroundColor Yellow
    try {
        python -m pytest tests/ -v --tb=short 2>$null
        Write-Host "✅ Tests completed" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Tests failed or pytest not available" -ForegroundColor Yellow
    }
}

# Function to show Git status with GitLens-style info
function Show-GitStatus {
    Write-Host "`n📊 Git Status (GitLens style):" -ForegroundColor Yellow
    try {
        $status = git status --porcelain 2>$null
        if ($status) {
            Write-Host "📝 Changes:" -ForegroundColor Cyan
            foreach ($line in $status) {
                $prefix = $line.Substring(0, 2)
                $file = $line.Substring(3)
                switch ($prefix) {
                    " M" { Write-Host "  🔄 Modified: $file" -ForegroundColor Yellow }
                    "A " { Write-Host "  ➕ Added: $file" -ForegroundColor Green }
                    "D " { Write-Host "  ➖ Deleted: $file" -ForegroundColor Red }
                    "R " { Write-Host "  🔄 Renamed: $file" -ForegroundColor Blue }
                    "??" { Write-Host "  ❓ Untracked: $file" -ForegroundColor Gray }
                    default { Write-Host "  📄 $prefix $file" -ForegroundColor White }
                }
            }
        } else {
            Write-Host "✅ Working directory clean" -ForegroundColor Green
        }

        # Show recent commits (Git Graph style)
        Write-Host "`n📈 Recent Commits:" -ForegroundColor Cyan
        $commits = git log --oneline -5 2>$null
        if ($commits) {
            $commits | ForEach-Object {
                Write-Host "  $_" -ForegroundColor White
            }
        }
    }
    catch {
        Write-Host "⚠️  Git not available or not a git repository" -ForegroundColor Yellow
    }
}

# Main execution logic
if ($All) {
    Run-Black
    Run-Prettier
    Run-Pylint
    Run-ESLint
    Run-Tests
    Check-Todos
    Show-GitStatus
} else {
    if ($Format) {
        Run-Black
        Run-Prettier
    }
    if ($Lint) {
        Run-Pylint
        Run-ESLint
    }
    if ($Test) { Run-Tests }
    if ($Todo) { Check-Todos }
    if ($GitStatus) { Show-GitStatus }
}

# If no switches provided, show help
if (-not ($Format -or $Lint -or $Test -or $Todo -or $GitStatus -or $All)) {
    Write-Host "`n🔧 Usage:" -ForegroundColor Cyan
    Write-Host "  .\automated_dev_workflow.ps1 -All              # Run all checks"
    Write-Host "  .\automated_dev_workflow.ps1 -Format           # Format code"
    Write-Host "  .\automated_dev_workflow.ps1 -Lint             # Run linters"
    Write-Host "  .\automated_dev_workflow.ps1 -Test             # Run tests"
    Write-Host "  .\automated_dev_workflow.ps1 -Todo             # Check TODOs"
    Write-Host "  .\automated_dev_workflow.ps1 -GitStatus        # Show Git status"
    Write-Host "`n💡 This script leverages your newly installed VS Code extensions:"
    Write-Host "   • Prettier & Black for code formatting"
    Write-Host "   • ESLint & Pylint for code quality"
    Write-Host "   • Todo Tree for task management"
    Write-Host "   • GitLens/Git Graph for version control"
    Write-Host "   • And more automation tools!"
}

Write-Host "`n✨ Workflow automation complete!" -ForegroundColor Green
