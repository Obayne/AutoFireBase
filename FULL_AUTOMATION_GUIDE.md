# Full Automation Guide - LV CAD

## 🤖 Autonomous Development Pipeline

This repository now has **fully autonomous development** capabilities. The system can implement features with minimal human intervention.

---

## 🚀 Quick Start

### Prerequisites Check
```powershell
# Ensure these are running:
ollama serve                    # Start Ollama server
ollama pull deepseek-coder     # Ensure model is downloaded
```

### Run Full Automation
```powershell
# One-time run through all tasks
.\scripts\full_auto.ps1

# Continuous mode (daemon)
.\scripts\full_auto.ps1 -ContinuousMode

# Skip approval (auto-merge - not recommended)
.\scripts\full_auto.ps1 -ApprovalRequired:$false
```

---

## 📋 How It Works

### 1️⃣ Task Queue System
Tasks are stored in `tasks/` directory:
- `task-*.md` - High priority infrastructure tasks
- `feat-*.md` - Feature implementation tasks

Example task file:
```markdown
### Task: Create Database Connection Manager

**Objective:** Create centralized SQLite connection manager

**Key Steps:**
1. Create `db/connection.py`
2. Implement singleton pattern
3. Add tests

**Acceptance Criteria:**
- No startup errors
- Tests pass
```

### 2️⃣ Automation Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                   FULL AUTO PIPELINE                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 📋 Read Task Queue                                 │
│     └─ Get next unprocessed task from tasks/          │
│                                                         │
│  2. 🌿 Create Feature Branch                           │
│     └─ Branch: feat/auto-<task-name>                   │
│                                                         │
│  3. 🤖 AI Implementation                               │
│     ├─ DeepSeek Coder analyzes task                   │
│     ├─ Generates implementation plan                   │
│     ├─ Creates/modifies files                          │
│     └─ Generates pytest tests                          │
│                                                         │
│  4. 🧪 Automated Testing                               │
│     ├─ Black formatting                                │
│     ├─ Ruff linting                                    │
│     └─ pytest execution                                │
│                                                         │
│  5. 📤 Create Draft PR                                 │
│     └─ Labeled: automated, needs-testing               │
│                                                         │
│  6. ⏸️  HUMAN TESTING REQUIRED ⏸️                      │
│     ├─ Review code changes                             │
│     ├─ Manual testing in app                           │
│     └─ Approve PR on GitHub                            │
│                                                         │
│  7. 🔀 Auto-Merge                                      │
│     ├─ Wait for CI checks                              │
│     ├─ Squash merge to main                            │
│     └─ Archive task to tasks/pr/                       │
│                                                         │
│  8. 🔄 Repeat for Next Task                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3️⃣ Your Role (Human Testing)

**When automation pauses for you:**

1. **Review the PR** on GitHub
   - Check code quality
   - Verify logic correctness
   - Look for edge cases

2. **Test manually**
   ```powershell
   # Checkout the PR branch
   gh pr checkout <PR_NUMBER>
   
   # Run the application
   python app/main.py
   
   # Test the new feature
   # Verify no regressions
   ```

3. **Approve on GitHub**
   - If tests pass → Approve PR
   - If issues found → Request changes
   - Automation will auto-merge after approval

---

## 🛠️ Advanced Usage

### Single Task Implementation
```powershell
# Implement one specific task
python scripts/ai_coder.py tasks/task-db-connection-manager.md
```

### Add New Task
```powershell
# Create task file
New-Item -Path "tasks/task-my-feature.md" -ItemType File

# Edit with your task description
# Follow format: Objective, Key Steps, Acceptance Criteria

# Automation will pick it up automatically
```

### Monitor Progress
```powershell
# Watch automation log
.\scripts\full_auto.ps1 | Tee-Object -FilePath logs/automation.log

# Check current PRs
gh pr list --label automated

# View task queue
Get-ChildItem tasks/*.md
```

---

## 🎯 Task Prioritization

Tasks are processed in this order:
1. **`task-*.md`** - Infrastructure/foundation tasks
2. **`feat-*.md`** - Feature implementation
3. **Others** - General improvements

### Example Queue
```
tasks/
├── task-db-connection-manager.md          # ← Processed first
├── task-integrate-coverage-service.md     # ← Then this
├── feat-cad-core-trim-suite.md            # ← Then features
├── feat-backend-schema-loader.md
└── pr/                                     # ← Completed tasks archived here
    └── task-completed-example.md
```

---

## 🔧 Configuration

### AI Model Settings
Edit `scripts/ai_coder.py`:
```python
self.model = "deepseek-coder:latest"  # Change model
temperature = 0.3                      # Adjust creativity (0.0-1.0)
num_predict = 4096                     # Max tokens
```

### Automation Behavior
Edit `scripts/full_auto.ps1`:
```powershell
$CheckIntervalSeconds = 300      # How often to check for new tasks
$ApprovalRequired = $true        # Require human approval
```

---

## 📊 Monitoring & Metrics

### View Automation Status
```powershell
# Current branch
git branch

# Recent commits
git log --oneline -10

# PR status
gh pr status

# CI checks
gh run list --limit 5
```

### Automation Metrics
The system tracks:
- ✅ Tasks completed
- ⏱️ Time per task
- 🧪 Test pass rate
- 📊 Lines of code generated

---

## 🚨 Troubleshooting

### "Ollama not running"
```powershell
# Start Ollama
ollama serve

# Verify
curl http://localhost:11434/api/tags
```

### "DeepSeek Coder not found"
```powershell
# Pull the model
ollama pull deepseek-coder

# Verify
ollama list
```

### "Tests failing"
```powershell
# Check the branch
git checkout feat/auto-<task-name>

# Run tests manually
pytest -v

# Fix issues, commit
git add -A
git commit -m "fix: address test failures"
git push
```

### "AI generated bad code"
```powershell
# Checkout the branch
git checkout feat/auto-<task-name>

# Edit files manually
# Fix the issues

# Commit and push
git add -A
git commit -m "fix: manual corrections to AI code"
git push

# PR will update automatically
```

---

## 🎓 Best Practices

### Writing Good Task Files
```markdown
### Task: [Clear, concise title]

**Objective:** One-sentence goal

**Key Steps:**
1. Specific, actionable step
2. Another specific step
3. Final step

**Acceptance Criteria:**
- Measurable outcome 1
- Measurable outcome 2

**Constraints:**
- Under 300 lines
- Add tests
- No breaking changes
```

### Task Sizing
- ✅ **Good:** Single feature, <300 lines, clear scope
- ❌ **Too Large:** Multiple features, >500 lines, vague requirements
- ❌ **Too Small:** Trivial changes, not worth automation

### Review Checklist
When reviewing AI-generated PRs:
- [ ] Code follows project patterns
- [ ] Tests cover edge cases
- [ ] No security issues
- [ ] Documentation updated
- [ ] Manual testing passed
- [ ] No regressions

---

## 🔐 Security & Privacy

### Local AI Benefits
- ✅ Code never leaves your machine
- ✅ No cloud API costs
- ✅ Full control over models
- ✅ Works offline

### GitHub Actions
- Uses GitHub secrets for authentication
- No code sent to external services
- All CI runs in isolated containers

---

## 📈 Performance

### Speed Estimates
- **Simple task** (< 100 lines): 5-10 minutes
- **Medium task** (100-300 lines): 15-30 minutes
- **Complex task** (> 300 lines): Split into smaller tasks

### Resource Usage
- **CPU:** Moderate during AI generation
- **RAM:** ~4-8GB for DeepSeek Coder
- **Disk:** Minimal (models already downloaded)

---

## 🤝 Human-AI Collaboration

### What AI Does Best
- ✅ Boilerplate code generation
- ✅ Test scaffolding
- ✅ Following established patterns
- ✅ Consistent formatting

### What You Do Best
- ✅ Architecture decisions
- ✅ Edge case identification
- ✅ User experience evaluation
- ✅ Security review

### The Sweet Spot
**AI implements → You validate → AI refines → You approve**

---

## 📞 Support

### If Automation Gets Stuck
1. Check logs: `logs/automation.log`
2. Review GitHub Actions: `gh run list`
3. Check Ollama: `ollama ps`
4. Restart: `Ctrl+C` and re-run

### Emergency Stop
```powershell
# Stop automation
Ctrl + C

# Return to main
git checkout main

# Clean up branches
git branch -D feat/auto-*
```

---

## 🎉 Success Metrics

Track your automation success:
```powershell
# PRs created by automation
gh pr list --label automated --state all

# Merge rate
gh pr list --label automated --state merged | wc -l

# Average time to merge
# (GitHub Insights > Pull Requests > Time to merge)
```

---

## 🔮 Future Enhancements

Planned improvements:
- [ ] Multi-model support (GPT-4, Claude, etc.)
- [ ] Self-healing (AI fixes its own test failures)
- [ ] Intelligent task prioritization
- [ ] Automatic documentation generation
- [ ] Performance benchmarking

---

## 📚 Additional Resources

- **AI Model Docs:** https://ollama.ai/library/deepseek-coder
- **Continue Extension:** https://continue.dev
- **GitHub CLI:** https://cli.github.com/manual/

---

**Ready to start?**
```powershell
.\scripts\full_auto.ps1
```

Let the AI build while you focus on design and testing! 🚀
