# GitHub Automation Visual Flow

## 📋 PR Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│  Developer Creates PR                                        │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  Automatic Actions Triggered:                                │
│  ✓ Add size label (XS/S/M/L/XL)                             │
│  ✓ Add type label (feature/fix/chore)                       │
│  ✓ Add area label (frontend/backend/cad-core)               │
│  ✓ Assign to maintainer                                      │
│  ✓ Run CI (linting, formatting, tests)                       │
│  ✓ Welcome first-time contributors                           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  Review Process                                              │
│  👤 Reviewers check code                                     │
│  💬 Comments and discussions                                 │
│  ✅ Approval or 🔄 Changes requested                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
         ┌────────┴────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│ Has auto-merge? │  │  Manual merge   │
│     label?      │  │                 │
└────────┬────────┘  └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Auto-Merge Checks:                                          │
│  ✓ Has approval?                                             │
│  ✓ All CI checks passed?                                     │
│  ✓ No merge conflicts?                                       │
│  ✓ No "changes requested"?                                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  🎉 Automatically Merged!                                    │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Weekly Automation Cycle

```
Monday 9:00 AM UTC
│
├─► Dependabot checks for dependency updates
│   ├─ Python packages (pip)
│   └─ GitHub Actions
│
└─► Creates PRs for outdated dependencies
    ├─ Auto-labels: "dependencies", "type: chore"
    ├─ Auto-assigns to maintainer
    └─ Includes changelog and release notes
```

```
Daily 1:00 AM UTC
│
├─► Stale Bot runs
│   │
│   ├─ Issues (60 days inactive)
│   │  ├─ Mark as "stale"
│   │  └─ Close after 7 more days
│   │
│   └─ PRs (30 days inactive)
│      ├─ Mark as "stale"
│      └─ Close after 14 more days
│
└─► Exempt labels: pinned, security, sprint:01, in-progress
```

## 🏷️ Label System

```
Branch Name          →    Auto-Label
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
feat/new-feature     →    type: feature
fix/bug-fix          →    type: fix
chore/update-docs    →    type: chore
*-frontend-*         →    area: frontend
*-backend-*          →    area: backend
*-cad-core-*         →    area: cad-core

PR Size (lines)      →    Label
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
< 10                 →    size: XS  (🟢 green)
10-49               →    size: S   (🟢 lime)
50-199              →    size: M   (🟠 orange)
200-499             →    size: L   (🔴 tomato)
500+                →    size: XL  (🔴 red)
```

## 🚀 Release Flow

```
Developer                GitHub Actions              GitHub
───────────────────────────────────────────────────────────

Update VERSION.txt
Commit changes
Create tag v1.2.3
Push tag
                  ─────► Checkout code
                         Setup Python
                         Build with PyInstaller
                         Create .exe artifact
                                        ─────► Create Release
                                               Attach .exe
                                               Publish
```

## 🎯 VS Code Integration Points

```
VS Code GUI                      GitHub
─────────────────────────────────────────

Source Control Panel
├─ Stage files         ─────►    Commit
├─ Write message
└─ Commit & Push       ─────►    Push to GitHub
                                 │
                                 ├─ Triggers CI workflow
                                 ├─ Auto-labeling
                                 └─ Notifications

GitHub Panel
├─ View Issues         ◄─────    Fetch from GitHub
├─ Create branch       ─────►    Push new branch
├─ View PRs
└─ Review comments     ◄─────    Sync with GitHub

Tasks Menu (Ctrl+Shift+P)
├─ Run AutoFire
├─ Run Tests
├─ Format & Lint       ─────►    Local validation
├─ Build Executable              (before pushing)
└─ Setup Dev Environment

Debug (F5)
├─ Start with breakpoints
├─ Step through code
└─ Inspect variables
```

## 🛡️ Quality Gates

```
                    PR Submission
                         │
                         ▼
              ┌──────────────────────┐
              │  CI Pipeline         │
              │  ──────────────      │
              │  1. Ruff Check       │──► ❌ Fail → Cannot merge
              │  2. Black Format     │──► ❌ Fail → Cannot merge
              │  3. Pytest           │──► ❌ Fail → Cannot merge
              └──────────┬───────────┘
                         │
                         ▼ All Pass
              ┌──────────────────────┐
              │  Review Required     │
              │  ──────────────      │
              │  Min 1 Approval      │──► ⏳ Waiting
              └──────────┬───────────┘
                         │
                         ▼ Approved
              ┌──────────────────────┐
              │  Ready to Merge      │
              │  ──────────────      │
              │  Manual or Auto      │──► ✅ Merge
              └──────────────────────┘
```

## 📊 Metrics & Visibility

The automation provides these visibility points:

| Location | What You See | Updated When |
|----------|-------------|--------------|
| PR Labels | Size, Type, Area | On PR open/update |
| PR Status | CI checks | On every push |
| Actions Tab | Workflow runs | Real-time |
| PR Comments | Auto-merge status, Welcome messages | On events |
| Issues/PRs List | Stale labels | Daily |
| Releases | Auto-generated releases | On tag push |
| Dependencies | Dependabot PRs | Weekly Monday |

## 🎨 Color Coding

GitHub labels use consistent colors for easy visual scanning:

- 🟢 **Green**: Small changes (size: XS, size: S)
- 🟠 **Orange**: Medium changes (size: M)
- 🔴 **Red**: Large changes (size: L, XL)
- 🔵 **Blue**: Type labels (feature, fix, chore)
- 🟣 **Purple**: Area labels (frontend, backend, cad-core)
- ⚫ **Gray**: Status (stale, dependencies)

## 💡 Pro Tips

1. **Branch names matter** - They trigger automatic labeling
2. **Small PRs** - Get reviewed faster and auto-label as XS/S
3. **Use auto-merge** - Save time on straightforward PRs
4. **Comment on issues** - Prevents stale automation
5. **Check Actions tab** - See all automation in real-time
6. **Use VS Code tasks** - Format before pushing to pass CI faster
