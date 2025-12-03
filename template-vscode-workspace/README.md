# VS Code Professional Python Workspace Template

This template provides a complete VS Code workspace configuration optimized for professional Python development with AI assistance, comprehensive tooling, and automation.

## 🚀 Quick Setup

1. **Clone this template** into your new project directory
2. **Copy the `.vscode/` folder** to your project root
3. **Install recommended extensions** when prompted by VS Code
4. **Run setup scripts** to configure your development environment

## 📦 What's Included

### Core Configuration
- **`.vscode/settings.json`** - Comprehensive VS Code settings for Python development
- **`.vscode/extensions.json`** - Recommended extensions for professional development
- **`.vscode/tasks.json`** - Build tasks and automation
- **`.vscode/launch.json`** - Debug configurations for Python apps

### Python Tooling
- **Black** - Code formatting (100 character line length)
- **Ruff** - Fast Python linter and import sorter
- **MyPy** - Static type checking
- **Pytest** - Testing framework with coverage
- **Pre-commit** - Git hooks for code quality

### AI Integration
- **Continue** - Local AI models (DeepSeek Coder via Ollama)
- **GitHub Copilot** - AI code completion
- **Tabnine** - Intelligent code suggestions

### Automation Scripts
- **Development setup** - Automated environment configuration
- **Build scripts** - PyInstaller packaging
- **Testing automation** - CI/CD pipeline integration
- **Code quality** - Automated linting and formatting

## 🛠️ Required Tools

### System Requirements
- **Python 3.11+** (recommended)
- **Git** for version control
- **PowerShell 7+** (Windows) or Bash (Linux/Mac)

### Optional but Recommended
- **Ollama** - Local AI model server
- **DeepSeek Coder** - Advanced coding AI model
- **GitHub CLI** - Repository management

## ⚙️ Configuration Highlights

### VS Code Settings
```json
{
  "python.formatting.provider": "black",
  "python.linting.ruffEnabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true,
  "files.autoSave": "afterDelay",
  "git.autofetch": true
}
```

### Recommended Extensions
- Python (Microsoft) - Core Python support
- Pylance - Enhanced Python language server
- Continue - Local AI assistance
- GitHub Copilot - AI code completion
- GitLens - Advanced Git features
- Jupyter - Notebook support

### AI Model Configuration
- **Primary:** DeepSeek Coder (Ollama) - Local, fast, coding-focused
- **Backup:** Claude/OpenRouter - Cloud-based for complex reasoning
- **Tab completion:** DeepSeek Coder for instant suggestions

## 🚀 Getting Started

### 1. Environment Setup
```powershell
# Clone template and setup
git clone <your-repo-url>
cd your-project

# Run development setup (creates venv, installs deps, configures pre-commit)
.\scripts\setup_dev.ps1
```

### 2. Activate Environment
```powershell
# Activate virtual environment
. .venv\Scripts\Activate.ps1
```

### 3. AI Setup (Optional but Recommended)
```powershell
# Install Ollama (if not already installed)
# Download from: https://ollama.ai/download

# Pull DeepSeek Coder model
ollama pull deepseek-coder:latest

# Start Ollama service (runs in background)
ollama serve
```

### 4. Verify Setup
```powershell
# Run automated checks
.\scripts\automated_dev_workflow.ps1 -All

# Run tests
python -m pytest tests/ -v

# Build application
.\scripts\Build_App.ps1
```

## 📁 Project Structure

```
your-project/
├── .vscode/                 # VS Code configuration
│   ├── extensions.json     # Recommended extensions
│   ├── settings.json       # Workspace settings
│   ├── tasks.json         # Build tasks
│   └── launch.json        # Debug configurations
├── .continue/              # AI model configuration
├── scripts/                # Automation scripts
├── tests/                  # Test suite
├── docs/                   # Documentation
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Development dependencies
├── pyproject.toml         # Python project configuration
└── .pre-commit-config.yaml # Git hooks configuration
```

## 🎯 Development Workflow

### Daily Development
1. **Activate environment:** `. .venv\Scripts\Activate.ps1`
2. **Pull latest changes:** `git pull`
3. **Make code changes** with AI assistance
4. **Run quality checks:** `ruff check --fix . && black .`
5. **Run tests:** `python -m pytest tests/`
6. **Commit changes:** `git add -A && git commit -m "feat: your changes"`

### AI-Assisted Development
- **Continue extension** for complex coding tasks
- **Tabnine** for instant code completion
- **GitHub Copilot** for AI-powered suggestions
- **DeepSeek Coder** for local, privacy-focused AI

### Automation Features
- **One-command PR creation:** `./scripts/auto_pr.ps1`
- **Automated maintenance:** `./scripts/auto_maintain.ps1`
- **Release automation:** `./scripts/auto_release.ps1`
- **Complete CI/CD:** `./scripts/auto_complete.ps1`

## 🔧 Customization

### Modifying Settings
Edit `.vscode/settings.json` to customize:
- Python interpreter path
- Linting rules
- Formatting preferences
- Git behavior
- Editor appearance

### Adding Extensions
Update `.vscode/extensions.json` to include:
- Project-specific tools
- Language support
- Productivity enhancements

### AI Configuration
Modify `.continue/config.json` for:
- Different AI models
- API endpoints
- Model preferences

## 📚 Resources

### Documentation
- [VS Code Documentation](https://code.visualstudio.com/docs)
- [Python in VS Code](https://code.visualstudio.com/docs/languages/python)
- [Continue Extension Guide](https://continue.dev/docs)

### Tools
- [Black Code Formatter](https://black.readthedocs.io/)
- [Ruff Linter](https://beta.ruff.rs/docs/)
- [MyPy Type Checker](https://mypy.readthedocs.io/)
- [Pytest Framework](https://docs.pytest.org/)

### AI Models
- [Ollama Models](https://ollama.ai/library)
- [DeepSeek Coder](https://github.com/deepseek-ai/DeepSeek-Coder)
- [GitHub Copilot](https://github.com/features/copilot)

## 🤝 Contributing

When using this template:
1. Keep configurations up-to-date
2. Test automation scripts regularly
3. Update documentation as needed
4. Share improvements with the community

## 📄 License

This template is provided as-is for professional Python development. Customize and adapt to your project needs.
