# VS Code & GitHub Workflow Guide

This guide helps you work efficiently with AutoFireBase using VS Code's GUI and GitHub automation.

## 🚀 Getting Started with VS Code

### First Time Setup

1. **Open the Workspace**
   - Double-click `AutoFireBase.code-workspace` to open the project
   - Or in VS Code: `File > Open Workspace from File...`

2. **Install Recommended Extensions**
   - VS Code will prompt you to install recommended extensions
   - Click "Install All" when prompted
   - Essential extensions:
     - Python (Microsoft)
     - GitHub Pull Requests and Issues
     - GitLens
     - GitHub Actions

3. **Setup Python Environment**
   - Open Command Palette: `Ctrl+Shift+P` (or `F1`)
   - Type: `Tasks: Run Task`
   - Select: `Setup Dev Environment`
   - Wait for it to complete

4. **Select Python Interpreter**
   - Click the Python version in the status bar (bottom right)
   - Select: `.venv/Scripts/python.exe`

## 🎯 Daily Workflow (GUI-Based)

### Running the Application

**Method 1: Debug Menu (Recommended)**
1. Press `F5` or click the Run icon in the sidebar (▶️)
2. Select "Python: AutoFire App" from the dropdown
3. The app will launch in debug mode

**Method 2: Tasks Menu**
1. `Ctrl+Shift+P` → `Tasks: Run Task`
2. Select "Run AutoFire"

### Running Tests

**Visual Test Explorer:**
1. Click the Testing icon in the sidebar (🧪)
2. Tests will auto-discover
3. Click ▶️ next to any test to run it
4. Green ✓ = passed, Red ✗ = failed

**Run All Tests:**
- `Ctrl+Shift+P` → `Tasks: Run Task` → "Run Tests"

### Formatting & Linting

**Automatic (Recommended):**
- Code auto-formats when you save (`Ctrl+S`)
- Format on save is already enabled

**Manual:**
- `Ctrl+Shift+P` → `Tasks: Run Task` → "Format & Lint"
- Or right-click in editor → "Format Document" (`Shift+Alt+F`)

## 📝 Working with Git & GitHub (GUI)

### Source Control Panel

1. Click the Source Control icon in the sidebar (branch icon)
2. View all changed files
3. Stage changes by clicking the `+` icon
4. Enter commit message in the text box
5. Click the ✓ checkmark to commit
6. Click `...` → `Push` to push to GitHub

### GitHub Pull Requests

**View Issues & PRs:**
1. Click the GitHub icon in the sidebar
2. Browse:
   - My Issues
   - Sprint 01 Issues
   - Open Pull Requests
   - Recent Issues

**Create a Branch for an Issue:**
1. In GitHub panel, right-click an issue
2. Select "Create Branch..."
3. VS Code creates and checks out the branch

**Create a Pull Request:**
1. After pushing your branch, VS Code shows a notification
2. Click "Create Pull Request"
3. Fill in title and description
4. GitHub Actions will automatically:
   - Run CI checks
   - Add size label (XS/S/M/L/XL)
   - Add type label (feature/fix/chore)
   - Assign reviewers

### Viewing GitHub Actions

1. Install "GitHub Actions" extension
2. Click Actions icon in sidebar
3. View workflow runs in real-time
4. See which checks passed/failed
5. View logs directly in VS Code

## 🤖 GitHub Automations (What Happens Automatically)

### When You Open a PR:

✅ **Auto-Labeling:**
- Size label based on lines changed (XS/S/M/L/XL)
- Type label from branch name (feat/ → type: feature)
- Area label from branch name (frontend/ → area: frontend)

✅ **Auto-Assignment:**
- PR automatically assigned to maintainer
- Issues assigned based on area labels

✅ **CI Checks:**
- Linting (Ruff)
- Formatting (Black)
- Tests (Pytest)

✅ **Welcome Message:**
- First-time contributors get a welcome comment with helpful links

### Auto-Merge (Optional):

To enable auto-merge for your PR:
1. Add the `auto-merge` label to your PR
2. After approval + passing CI, GitHub will auto-merge
3. You'll get a notification when merged

### Dependency Updates:

- **Dependabot** runs weekly (Mondays at 9 AM)
- Creates PRs for outdated dependencies
- You'll see them in the PR list

### Stale Management:

- Issues inactive for 60 days → marked "stale"
- PRs inactive for 30 days → marked "stale"
- Closes after additional waiting period
- Comment on an issue/PR to keep it active

## 🔧 VS Code Commands Quick Reference

### Command Palette (`Ctrl+Shift+P`)

Frequently used commands:
- `Git: Clone` - Clone a repository
- `Git: Create Branch` - Create new branch
- `Git: Checkout to` - Switch branches
- `Python: Select Interpreter` - Choose Python version
- `Tasks: Run Task` - Run predefined tasks
- `Format Document` - Format current file
- `Organize Imports` - Sort imports

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Run/Debug | `F5` |
| Command Palette | `Ctrl+Shift+P` |
| Quick Open File | `Ctrl+P` |
| Terminal | `` Ctrl+` `` |
| Source Control | `Ctrl+Shift+G` |
| Search Files | `Ctrl+Shift+F` |
| Format Document | `Shift+Alt+F` |
| Save | `Ctrl+S` |
| Save All | `Ctrl+K S` |

## 📊 Viewing Build Status

### In VS Code:
1. Bottom status bar shows:
   - Current branch
   - Sync status (↑↓ arrows)
   - Git status
2. GitHub Actions extension shows workflow status

### On GitHub:
1. Go to your PR
2. See all checks at the bottom
3. Click "Details" to view logs
4. Green ✓ = all passing

## 🎨 Visual Indicators

### File Colors (GitLens):
- **Green**: New files
- **Orange**: Modified files
- **Red**: Deleted files
- **Gray**: Ignored files

### Gutter Indicators:
- **Blue bar**: Modified lines
- **Green bar**: Added lines
- **Red triangle**: Deleted lines

### Status Bar:
- Branch name (click to switch)
- Sync status (click to pull/push)
- Errors/Warnings count
- Python version

## 🔍 Troubleshooting

### "Python not found"
- Select interpreter: Click Python version in status bar
- Choose: `.venv/Scripts/python.exe`

### Tests not discovering
- Reload window: `Ctrl+Shift+P` → `Developer: Reload Window`
- Check Testing panel → Refresh icon

### Git sync issues
- Pull first: Source Control → `...` → `Pull`
- Then push: Source Control → `...` → `Push`

### Format not working
- Install Black: Terminal → `pip install black`
- Reload window

## 📚 Additional Resources

- [VS Code Python Tutorial](https://code.visualstudio.com/docs/python/python-tutorial)
- [GitHub Pull Requests Extension](https://code.visualstudio.com/docs/editor/github)
- [VS Code Git Tutorial](https://code.visualstudio.com/docs/editor/versioncontrol)
- [Project README](../README.md)
- [Contributing Guide](../AGENTS.md)

## 💡 Pro Tips

1. **Use the Command Palette** - Press `Ctrl+Shift+P` and start typing. It's the fastest way to do anything.

2. **Multiple Cursors** - Hold `Alt` and click to add cursors, or `Ctrl+Alt+Up/Down` to add cursors above/below.

3. **Zen Mode** - `Ctrl+K Z` for distraction-free coding.

4. **Split Editor** - `Ctrl+\` to split the editor view.

5. **Quick File Navigation** - `Ctrl+P` and start typing filename.

6. **Go to Definition** - `F12` on any symbol to jump to its definition.

7. **Peek Definition** - `Alt+F12` to see definition inline.

8. **Rename Symbol** - `F2` on any variable/function to rename everywhere.

9. **GitHub Copilot** - If you have Copilot, it suggests code as you type!

10. **Todo Tree** - Write `# TODO:` comments and they'll show in the Todo Tree panel.
