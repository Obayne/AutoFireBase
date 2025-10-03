# VS Code AutoFire Development Setup Guide

**For Non-Programmers: Complete Automated Development Environment**

---

## 🎯 Step 1: Ensure Correct Project in VS Code

### Open the Correct Workspace
```bash
# Method 1: Open Folder
# In VS Code: File → Open Folder → Select C:\Dev\Autofire

# Method 2: Create Workspace File (Recommended)
# This ensures VS Code always opens the right project
```

### Create AutoFire Workspace File
```json
// Save as: C:\Dev\Autofire\AutoFire.code-workspace
{
    "folders": [
        {
            "name": "AutoFire",
            "path": "C:\\Dev\\Autofire"
        }
    ],
    "settings": {
        "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
        "python.terminal.activateEnvironment": true,
        "python.linting.enabled": true,
        "python.linting.ruffEnabled": true,
        "python.formatting.provider": "black",
        "python.testing.pytestEnabled": true,
        "python.testing.pytestArgs": ["-q"],
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        },
        "files.associations": {
            "*.spec": "python",
            "*.md": "markdown"
        },
        "git.autofetch": true,
        "git.enableSmartCommit": true,
        "workbench.editor.enablePreview": false,
        "explorer.confirmDelete": false
    },
    "launch": {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: AutoFire Main",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/main.py",
                "console": "integratedTerminal",
                "justMyCode": false,
                "python": "${workspaceFolder}/.venv/Scripts/python.exe"
            },
            {
                "name": "Python: Debug Application",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/tools/run_app_debug.py",
                "console": "integratedTerminal",
                "justMyCode": false,
                "python": "${workspaceFolder}/.venv/Scripts/python.exe"
            }
        ]
    },
    "tasks": {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Setup Development Environment",
                "type": "shell",
                "command": "${workspaceFolder}/setup_dev.ps1",
                "group": {
                    "kind": "build",
                    "isDefault": true
                },
                "presentation": {
                    "echo": true,
                    "reveal": "always",
                    "focus": false,
                    "panel": "shared"
                },
                "problemMatcher": []
            },
            {
                "label": "Run AutoFire",
                "type": "shell",
                "command": "python",
                "args": ["main.py"],
                "group": "build",
                "presentation": {
                    "echo": true,
                    "reveal": "always",
                    "focus": false,
                    "panel": "shared"
                }
            },
            {
                "label": "Run Tests",
                "type": "shell",
                "command": "pytest",
                "args": ["-q"],
                "group": "test",
                "presentation": {
                    "echo": true,
                    "reveal": "always",
                    "focus": false,
                    "panel": "shared"
                }
            },
            {
                "label": "Format Code",
                "type": "shell",
                "command": "black",
                "args": ["."],
                "group": "build"
            },
            {
                "label": "Lint Code",
                "type": "shell",
                "command": "ruff",
                "args": ["check", "--fix", "."],
                "group": "build"
            },
            {
                "label": "Build Production",
                "type": "shell",
                "command": "${workspaceFolder}/Build_AutoFire.ps1",
                "group": "build"
            },
            {
                "label": "Quality Check All",
                "type": "shell",
                "command": "black . ; ruff check --fix . ; pytest -q",
                "group": "build",
                "dependsOn": ["Format Code", "Lint Code", "Run Tests"]
            }
        ]
    },
    "extensions": {
        "recommendations": [
            "ms-python.python",
            "ms-python.black-formatter",
            "charliermarsh.ruff",
            "ms-python.pylint",
            "ms-python.mypy-type-checker",
            "ms-vscode.vscode-json",
            "redhat.vscode-yaml",
            "ms-vscode.powershell",
            "github.copilot",
            "github.copilot-chat",
            "gruntfuggly.todo-tree",
            "ms-vscode.test-adapter-converter",
            "hbenl.vscode-test-explorer",
            "ms-vscode.vscode-github-issue-notebooks"
        ]
    }
}
```

### Install Required VS Code Extensions
**Command Palette (Ctrl+Shift+P) → "Extensions: Install from Recommendations"**

Or manually install:
- Python (ms-python.python)
- Black Formatter (ms-python.black-formatter)
- Ruff (charliermarsh.ruff)
- GitHub Copilot (github.copilot)
- GitHub Copilot Chat (github.copilot-chat)
- Todo Tree (gruntfuggly.todo-tree)

---

## 🤖 AI Project Manager Setup

### How to Use Me (GitHub Copilot) as Project Manager

#### 1. **Daily Workflow with AI Guidance**
```
Morning:
├── Open VS Code workspace
├── Check with AI: "What's the priority today?"
├── AI reviews current status and suggests next steps
└── AI creates/updates todo list

Development:
├── Tell AI what you want to accomplish
├── AI breaks it down into specific tasks
├── AI provides exact commands to run
└── AI validates work quality

Evening:
├── AI reviews completed work
├── AI suggests improvements
└── AI prepares for next day
```

#### 2. **AI Command Examples**
```bash
# Instead of programming, tell me what you want:
"Tell me what to do today for AutoFire development"

"Create a new feature for device placement"

"Fix the build issues I'm seeing"

"Review the code quality of my changes"

"Prepare for release"
```

#### 3. **AI Quality Assurance**
- **Before committing**: "Check my code for issues"
- **After changes**: "Validate this implementation"
- **Build issues**: "Help me fix this error"
- **Testing**: "Make sure tests are working"

---

## 🚀 Automated Development Workflow

### One-Click Setup (Run Once)
```powershell
# In VS Code Terminal (Ctrl+` to open)
cd C:\Dev\Autofire

# Run automated setup
.\setup_dev.ps1

# Verify everything works
python --version  # Should be 3.11+
python -c "import PySide6; print('PySide6 OK')"
pytest -q         # Should run tests
```

### Daily Development Automation

#### Method 1: VS Code Tasks (Recommended for Beginners)
1. **Open Command Palette**: `Ctrl+Shift+P`
2. **Type**: "Tasks: Run Task"
3. **Select**:
   - "Setup Development Environment" (first time only)
   - "Run AutoFire" (to test application)
   - "Run Tests" (to validate code)
   - "Quality Check All" (format, lint, test)

#### Method 2: PowerShell Automation
```powershell
# Add these to your PowerShell profile ($PROFILE)
# Edit with: notepad $PROFILE

function autofire-setup {
    cd C:\Dev\Autofire
    .\setup_dev.ps1
}

function autofire-run {
    cd C:\Dev\Autofire
    . .venv/Scripts/Activate.ps1
    python main.py
}

function autofire-test {
    cd C:\Dev\Autofire
    . .venv/Scripts/Activate.ps1
    pytest -q
}

function autofire-build {
    cd C:\Dev\Autofire
    . .venv/Scripts/Activate.ps1
    .\Build_AutoFire.ps1
}

function autofire-quality {
    cd C:\Dev\Autofire
    . .venv/Scripts/Activate.ps1
    black .
    ruff check --fix .
    pytest -q
}

# Then use simple commands:
autofire-setup  # One-time setup
autofire-run    # Run application
autofire-test   # Run tests
autofire-build  # Build release
autofire-quality # Full quality check
```

---

## 🔄 GitHub Automation (Free)

### Automated CI/CD (Already Configured)
- **GitHub Actions**: Runs automatically on every push
- **Tests**: Automatic testing, linting, formatting
- **Quality Gates**: Prevents bad code from merging

### Automated Code Quality
```yaml
# .github/workflows/ci.yml (already active)
- Linting with Ruff
- Formatting with Black
- Testing with pytest
- Build validation
```

### Automated Releases (Optional Setup)
```yaml
# Can add automatic releases on tags
# See docs/RELEASE_PROCESS.md for details
```

---

## 📊 Project Management with AI

### Daily Standup with AI
**Ask me each morning:**
```
"Good morning! What's the current status of AutoFire?
What should I work on today?
Any urgent issues to address?"
```

### Task Management
**Tell me what you want to accomplish:**
```
"I want to add device placement functionality"
"Fix the voltage drop calculations"
"Improve the user interface"
"Add export capabilities"
```

**I will:**
- Break it down into specific, actionable tasks
- Provide exact commands to run
- Guide you through each step
- Validate the implementation
- Ensure quality standards are met

### Quality Assurance
**Before any work:**
```
"Review the current codebase quality"
"Check for any issues I should address"
"Validate the build is working"
```

**After any changes:**
```
"Check my recent changes for issues"
"Make sure tests are still passing"
"Validate the implementation meets requirements"
```

---

## 🎯 Step-by-Step Setup Instructions

### Step 1: VS Code Workspace Setup
1. **Open VS Code**
2. **File → Open Folder → Select `C:\Dev\Autofire`**
3. **Create workspace file**: Copy the JSON above to `AutoFire.code-workspace`
4. **File → Open Workspace from File → Select `AutoFire.code-workspace`**

### Step 2: Install Extensions
1. **Ctrl+Shift+P → "Extensions: Install from Recommendations"**
2. **Or manually install recommended extensions**

### Step 3: Environment Setup
1. **Ctrl+Shift+P → "Tasks: Run Task" → "Setup Development Environment"**
2. **Wait for completion (may take a few minutes)**

### Step 4: Test Everything Works
1. **Tasks: Run Task → "Run Tests"** (should pass)
2. **Tasks: Run Task → "Run AutoFire"** (should open application)
3. **Tasks: Run Task → "Quality Check All"** (should pass)

### Step 5: Daily Workflow
1. **Open VS Code workspace** (it will remember your settings)
2. **Ask me**: "What should I work on today?"
3. **Follow my guidance** for each task
4. **Use VS Code tasks** for automation
5. **Ask me to review** your work

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### VS Code Can't Find Python
```
# Check Python interpreter
Ctrl+Shift+P → "Python: Select Interpreter"
Select: .venv/Scripts/python.exe
```

#### Tests Failing
```
# Run individual test
pytest tests/specific_test.py -v

# Ask me: "Help me fix this test failure"
```

#### Build Issues
```
# Clean and rebuild
.\Build_Clean.ps1
.\Build_AutoFire.ps1

# Ask me: "Help me fix this build error"
```

#### Git Issues
```
# Check status
git status

# Ask me: "Help me resolve this git conflict"
```

---

## 📈 Quality Assurance Automation

### Automated Checks (Run Before Commit)
- **Formatting**: `black .` (automatic)
- **Linting**: `ruff check --fix .` (automatic)
- **Testing**: `pytest -q` (required)
- **Type Checking**: `mypy frontend/ backend/ cad_core/` (optional)

### AI Quality Reviews
**Always ask me:**
- "Review my code changes"
- "Check for security issues"
- "Validate the implementation"
- "Ensure it follows best practices"

---

## 🎯 Success Metrics

### Daily Goals
- ✅ Environment setup working
- ✅ Tests passing
- ✅ Code formatted and linted
- ✅ Application runs without errors
- ✅ AI guidance followed

### Weekly Goals
- ✅ New features implemented
- ✅ Code quality maintained
- ✅ Documentation updated
- ✅ Builds successful

### Monthly Goals
- ✅ Releases created
- ✅ Issues resolved
- ✅ Quality standards met
- ✅ Project progressing

---

## 📞 Getting Help

### When to Ask Me (AI)
- **Planning**: "What should I work on?"
- **Implementation**: "How do I implement this feature?"
- **Debugging**: "Why is this not working?"
- **Quality**: "Is this code good?"
- **Next Steps**: "What's the next priority?"

### When to Use Documentation
- **Setup**: `docs/DEVELOPMENT_SETUP.md`
- **Commands**: `docs/DEVELOPMENT_COMMANDS.md`
- **Workflow**: `docs/DEVELOPMENT_WORKFLOW.md`
- **CI/CD**: `docs/CI_CD_AGENTS.md`

---

**Remember**: You're not programming - you're **directing development**. Tell me what you want to accomplish, and I'll guide you through each step with exact commands and validation. This setup ensures **consistent, high-quality work** with **maximum automation**. 🚀
