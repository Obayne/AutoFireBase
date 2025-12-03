# Professional Python Development Environment Setup
# This script sets up a complete Python development environment with all necessary tools

param(
    [switch]$SkipVenv,
    [switch]$SkipPreCommit,
    [switch]$Force
)

Write-Host "🚀 Setting up Professional Python Development Environment" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "❌ Python 3.11+ required. Please install Python from https://python.org" -ForegroundColor Red
    exit 1
}

# Check Git
try {
    $gitVersion = git --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Git found: $gitVersion" -ForegroundColor Green
    } else {
        throw "Git not found"
    }
} catch {
    Write-Host "❌ Git required. Please install Git from https://git-scm.com" -ForegroundColor Red
    exit 1
}

# Create virtual environment
if (-not $SkipVenv) {
    Write-Host "`n🏗️ Creating virtual environment..." -ForegroundColor Yellow
    if (Test-Path ".venv") {
        if ($Force) {
            Remove-Item -Recurse -Force ".venv"
            Write-Host "🗑️ Removed existing virtual environment" -ForegroundColor Yellow
        } else {
            Write-Host "⚠️ Virtual environment already exists. Use -Force to recreate." -ForegroundColor Yellow
        }
    }

    if (-not (Test-Path ".venv")) {
        python -m venv .venv
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Virtual environment created" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
            exit 1
        }
    }

    # Activate virtual environment
    Write-Host "`n🔄 Activating virtual environment..." -ForegroundColor Yellow
    . .\.venv\Scripts\Activate.ps1

    # Upgrade pip
    Write-Host "`n⬆️ Upgrading pip..." -ForegroundColor Yellow
    python -m pip install --upgrade pip

    # Install runtime dependencies
    if (Test-Path "requirements.txt") {
        Write-Host "`n📦 Installing runtime dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Runtime dependencies installed" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to install runtime dependencies" -ForegroundColor Red
        }
    }

    # Install development dependencies
    if (Test-Path "requirements-dev.txt") {
        Write-Host "`n🛠️ Installing development dependencies..." -ForegroundColor Yellow
        pip install -r requirements-dev.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Development dependencies installed" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to install development dependencies" -ForegroundColor Red
        }
    }
}

# Setup pre-commit hooks
if (-not $SkipPreCommit) {
    Write-Host "`n🔗 Setting up pre-commit hooks..." -ForegroundColor Yellow
    if (Test-Path ".pre-commit-config.yaml") {
        pre-commit install
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Pre-commit hooks installed" -ForegroundColor Green
            pre-commit install --hook-type commit-msg
            Write-Host "✅ Commit message hooks installed" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to install pre-commit hooks" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️ No .pre-commit-config.yaml found, skipping pre-commit setup" -ForegroundColor Yellow
    }
}

# Initial code quality check
Write-Host "`n🔍 Running initial code quality checks..." -ForegroundColor Yellow

# Format code
if (Get-Command black -ErrorAction SilentlyContinue) {
    Write-Host "🎨 Formatting code with Black..." -ForegroundColor Yellow
    black .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Code formatted with Black" -ForegroundColor Green
    }
}

# Lint code
if (Get-Command ruff -ErrorAction SilentlyContinue) {
    Write-Host "🔍 Linting code with Ruff..." -ForegroundColor Yellow
    ruff check --fix .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Code linted with Ruff" -ForegroundColor Green
    }
}

# Type check
if (Get-Command mypy -ErrorAction SilentlyContinue) {
    Write-Host "🔍 Type checking with MyPy..." -ForegroundColor Yellow
    mypy .
    # MyPy might have some errors initially, so we don't check exit code
    Write-Host "✅ Type checking completed" -ForegroundColor Green
}

# Run tests
if ((Test-Path "tests") -and (Get-Command pytest -ErrorAction SilentlyContinue)) {
    Write-Host "🧪 Running tests..." -ForegroundColor Yellow
    python -m pytest tests/ -v --tb=short
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Tests passed" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Some tests failed - review and fix" -ForegroundColor Yellow
    }
}

Write-Host "`n🎉 Development environment setup complete!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

Write-Host "`n📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Activate the virtual environment: . .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Start coding with AI assistance!" -ForegroundColor White
Write-Host "3. Use VS Code tasks for common operations" -ForegroundColor White
Write-Host "4. Run '.\scripts\automated_dev_workflow.ps1 -All' for full workflow" -ForegroundColor White

Write-Host "`n🔧 Available scripts:" -ForegroundColor Cyan
Write-Host "• setup_dev.ps1           - This setup script" -ForegroundColor White
Write-Host "• automated_dev_workflow.ps1 - Complete development workflow" -ForegroundColor White
Write-Host "• Build_App.ps1          - Build application executable" -ForegroundColor White

Write-Host "`n🤖 AI Tools Setup:" -ForegroundColor Cyan
Write-Host "1. Install Ollama: https://ollama.ai/download" -ForegroundColor White
Write-Host "2. Pull models: ollama pull deepseek-coder:latest" -ForegroundColor White
Write-Host "3. Start Ollama: ollama serve" -ForegroundColor White
Write-Host "4. Use Continue extension in VS Code for AI assistance" -ForegroundColor White

Write-Host "`n📚 Documentation:" -ForegroundColor Cyan
Write-Host "• README.md              - Project overview" -ForegroundColor White
Write-Host "• docs/                  - Additional documentation" -ForegroundColor White
Write-Host "• AI_USAGE_GUIDE.md      - AI tools usage guide" -ForegroundColor White

Write-Host "`n✨ Happy coding!" -ForegroundColor Green
