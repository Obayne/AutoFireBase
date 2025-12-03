#!/bin/bash

# Post-create script for GitHub Codespaces
# This script runs after the devcontainer is created to set up the development environment

set -e

echo "🚀 Setting up Professional Python Development Environment in Codespaces"
echo "======================================================================="

# Update package lists
echo "📦 Updating package lists..."
sudo apt-get update

# Install additional system dependencies if needed
echo "🔧 Installing system dependencies..."
sudo apt-get install -y curl wget git

# Create virtual environment
echo "🏗️ Creating Python virtual environment..."
python -m venv .venv
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

# Install runtime dependencies
if [ -f "requirements.txt" ]; then
    echo "📦 Installing runtime dependencies..."
    pip install -r requirements.txt
fi

# Install development dependencies
if [ -f "requirements-dev.txt" ]; then
    echo "🛠️ Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Setup pre-commit hooks
if [ -f ".pre-commit-config.yaml" ]; then
    echo "🔗 Setting up pre-commit hooks..."
    pre-commit install
    pre-commit install --hook-type commit-msg
fi

# Initial code quality check
echo "🔍 Running initial code quality checks..."

# Format code
if command -v black &> /dev/null; then
    echo "🎨 Formatting code with Black..."
    black .
fi

# Lint code
if command -v ruff &> /dev/null; then
    echo "🔍 Linting code with Ruff..."
    ruff check --fix .
fi

# Type check
if command -v mypy &> /dev/null; then
    echo "🔍 Type checking with MyPy..."
    mypy . || true  # Don't fail on initial mypy errors
fi

# Run tests
if [ -d "tests" ] && command -v pytest &> /dev/null; then
    echo "🧪 Running tests..."
    python -m pytest tests/ -v --tb=short || true  # Don't fail on test errors
fi

# Setup AI tools (if Ollama is available)
echo "🤖 Checking for AI tools..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama found - AI tools ready"
    echo "💡 To use AI assistance:"
    echo "   1. Pull models: ollama pull deepseek-coder:latest"
    echo "   2. Start Ollama: ollama serve"
    echo "   3. Use Continue extension in VS Code"
else
    echo "⚠️ Ollama not available - install locally for AI assistance"
fi

echo ""
echo "🎉 Codespace development environment setup complete!"
echo "======================================================"

echo ""
echo "📝 Next steps:"
echo "1. The virtual environment is already activated"
echo "2. Start coding with AI assistance!"
echo "3. Use VS Code tasks for common operations"
echo "4. Run tests with the test button in the sidebar"

echo ""
echo "🔧 Available features:"
echo "• Python 3.11 with virtual environment"
echo "• All development tools pre-installed"
echo "• VS Code extensions configured"
echo "• Git and GitHub integration ready"
echo "• Port forwarding for web applications"

echo ""
echo "📚 Documentation:"
echo "• README.md - Project overview"
echo "• docs/ - Additional documentation"
echo "• AI_USAGE_GUIDE.md - AI tools usage guide"

echo ""
echo "✨ Happy coding in Codespaces!"
