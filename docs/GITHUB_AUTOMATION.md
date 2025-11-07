# GitHub Automation Quick Reference

## 🤖 What's Automated?

### For Every PR You Open:

| Action | What Happens | Why |
|--------|-------------|-----|
| **Size Label** | Automatically adds `size: XS/S/M/L/XL` | Helps reviewers understand PR scope |
| **Type Label** | Adds label based on branch (feat/ → feature) | Categorizes changes |
| **Area Label** | Adds label from branch name (frontend/ → area: frontend) | Routes to right reviewer |
| **CI Checks** | Runs linting, formatting, tests | Ensures code quality |
| **Assignee** | Auto-assigns to maintainer | Ensures PR doesn't get lost |

### For First-Time Contributors:

| Event | What Happens |
|-------|-------------|
| First Issue | Welcome message with helpful links |
| First PR | Welcome message with contribution guidelines |

### Weekly Maintenance:

| Task | When | What |
|------|------|------|
| **Dependency Updates** | Mondays 9 AM | Dependabot creates PRs for outdated packages |
| **Stale Check** | Daily 1 AM | Marks/closes inactive issues and PRs |

### On Tag Push:

| Event | What Happens |
|-------|-------------|
| Push tag `v*` | Builds Windows executable and creates GitHub Release |

## 🏷️ Labels You Can Use

### Auto-Merge

Add `auto-merge` label to your PR to enable automatic merging:
- ✅ Requires: 1+ approval
- ✅ Requires: All CI checks passing
- ✅ Requires: No "changes requested" reviews
- Merges automatically when conditions met

### Keep-Alive

Prevent stale automation:
- `pinned` - Never marks as stale
- `in-progress` - Exempts PRs from stale check
- `security` - High priority, never stales

### Sprint Labels

- `sprint:01` - Part of Sprint 01
- `agent:auto` - Triggers agent orchestrator

## 📊 CI Checks Explained

When you push to a PR, these checks run:

1. **Ruff Check** (Linting)
   - Checks code style
   - Finds common bugs
   - Ensures imports are organized
   - **Fix**: Run `ruff check --fix .`

2. **Black Check** (Formatting)
   - Ensures consistent formatting
   - Line length = 100
   - **Fix**: Run `black .`

3. **Pytest** (Testing)
   - Runs all tests
   - **Fix**: Fix failing tests or skip with `@pytest.mark.skip`

All checks must pass before merging.

## 🔄 Dependabot PRs

### What to Do:

1. **Review the changes**
   - Check if it's a major version bump
   - Look at the changelog link in PR

2. **Test locally** (optional for minor updates)
   ```bash
   git fetch origin
   git checkout dependabot/pip/package-name
   pytest
   ```

3. **Approve & Merge**
   - If tests pass, approve the PR
   - Add `auto-merge` label for automatic merging

### Tips:
- Minor/patch updates are usually safe
- Major updates may have breaking changes
- Dependabot groups related updates

## 🗑️ Stale Issue/PR Management

### Timeline:

**Issues:**
- Day 60: Marked as `stale` with comment
- Day 67: Closed if no activity

**PRs:**
- Day 30: Marked as `stale` with comment  
- Day 44: Closed if no activity

### Keep Something Active:
- Just leave any comment
- Or add `pinned` label
- Stale label removed automatically when updated

## 🚀 Release Workflow

### Creating a Release:

1. **Update VERSION.txt**
   ```bash
   echo "1.2.3" > VERSION.txt
   git add VERSION.txt
   git commit -m "chore: bump version to 1.2.3"
   ```

2. **Create and push tag**
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```

3. **Automatic Build**
   - GitHub Actions builds Windows .exe
   - Creates GitHub Release
   - Attaches executable to release

### In VS Code:
1. Edit VERSION.txt
2. Commit and sync
3. `Ctrl+Shift+P` → `Git: Create Tag`
4. Enter tag: `v1.2.3`
5. `Ctrl+Shift+P` → `Git: Push Tags`

## 🎯 Branch Naming for Auto-Labeling

Follow these patterns for automatic labels:

| Branch Pattern | Auto-Label |
|----------------|------------|
| `feat/*` | `type: feature` |
| `fix/*` | `type: fix` |
| `chore/*` | `type: chore` |
| `*frontend*` | `area: frontend` |
| `*backend*` | `area: backend` |
| `*cad-core*` | `area: cad-core` |

**Examples:**
- `feat/add-circle-tool` → `type: feature`
- `fix/frontend-crash` → `type: fix` + `area: frontend`
- `chore/update-docs` → `type: chore`

## 💡 Tips for Success

1. **Use descriptive branch names** - They trigger automatic labels
2. **Keep PRs small** - Easier to review, XS/S PRs merge faster
3. **Wait for CI** - Don't merge until all checks pass
4. **Use auto-merge** - Save time on approved PRs
5. **Comment on issues** - Prevents them from going stale
6. **Review Dependabot PRs** - Keep dependencies current

## 🆘 Troubleshooting

### CI Failing?

**Linting Errors:**
```bash
python -m ruff check --fix .
python -m black .
git add .
git commit -m "fix: apply linting fixes"
git push
```

**Test Failures:**
```bash
python -m pytest -v  # See which tests fail
# Fix the code or tests
git add .
git commit -m "fix: resolve test failures"
git push
```

### PR Not Auto-Merging?

Check:
- ✅ Has `auto-merge` label?
- ✅ Has 1+ approval?
- ✅ All CI checks passed?
- ✅ No "changes requested" reviews?
- ✅ No merge conflicts?

### Dependabot PR Failed?

Usually means:
- Breaking change in dependency
- Tests need updating
- Remove the PR and handle manually

## 📞 Getting Help

- **In Issues**: Tag `@Obayne` or maintainers
- **In PRs**: Request review from maintainers
- **For Automation**: Check workflow logs in Actions tab
- **Documentation**: See [VS Code Guide](VS_CODE_GUIDE.md)
