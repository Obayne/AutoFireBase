# Release Process

## 🎯 Overview

This document defines the **release process** for AutoFire, ensuring consistent, high-quality releases that align with the master specification.

## 📋 Release Types

### Semantic Versioning
```
MAJOR.MINOR.PATCH
├── MAJOR: Breaking changes
├── MINOR: New features (backward compatible)
└── PATCH: Bug fixes (backward compatible)
```

### Release Cadence
- **Patch Releases**: As needed for critical fixes
- **Minor Releases**: Every 2-4 weeks with feature sets
- **Major Releases**: Major architectural changes (rare)

## 🔄 Release Workflow

### 1. Pre-Release Preparation

#### Update Version
```bash
# Update VERSION.txt
echo "1.2.3" > VERSION.txt

# Update version in code if needed
grep -r "version.*=.*["']1\.2\.2['"]" . --include="*.py" | head -5
```

#### Update Changelog
```markdown
## [1.2.3] - 2025-10-03

### Added
- System builder feature (closes #123)
- Device palette filtering (#124)

### Fixed
- Voltage drop calculation bug (#125)

### Changed
- Improved UI responsiveness (#126)
```

#### Run Full Test Suite
```bash
# Run all tests
pytest -v --tb=short

# Check test coverage
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Manual testing checklist
- [ ] Application starts without errors
- [ ] Core workflows functional
- [ ] No console errors/warnings
- [ ] Performance acceptable
```

### 2. Build Process

#### Development Build
```powershell
# Create debug build
.\Build_AutoFire_Debug.ps1

# Test the build
.\Run_AutoFire_Debug.cmd
```

#### Release Build
```powershell
# Create production build
.\Build_AutoFire.ps1

# Verify build artifacts
ls build/
ls dist/
```

### 3. Quality Assurance

#### Automated Checks
```bash
# Final CI simulation
ruff check .
black --check .
pytest -q
python -c "import autofire; print('Import OK')"
```

#### Manual QA Checklist
- [ ] All planned features implemented
- [ ] No known critical bugs
- [ ] Performance meets requirements
- [ ] UI/UX consistent with design
- [ ] Documentation updated
- [ ] Master specification compliance verified

### 4. Release Creation

#### Git Tagging
```bash
# Create annotated tag
git tag -a v1.2.3 -m "Release v1.2.3: Add system builder feature

## Changes
- New system builder UI for device staging
- Enhanced device palette with filtering
- Improved voltage drop calculations

## Testing
- All tests pass
- Manual QA completed
- Build verified on Windows"

# Push tag to trigger release
git push origin v1.2.3
```

#### GitHub Release
1. Go to [Releases](https://github.com/Obayne/AutoFireBase/releases)
2. Click "Create a new release"
3. **Tag**: `v1.2.3`
4. **Title**: `Release v1.2.3: Add system builder feature`
5. **Description**: Copy from CHANGELOG.md
6. **Assets**: Upload build artifacts
   - `AutoFire_v1.2.3.exe`
   - `AutoFire_Debug_v1.2.3.exe`
   - Source code zip/tar

### 5. Post-Release Activities

#### Update Documentation
```bash
# Update any version-specific docs
# Announce release in relevant channels
```

#### Monitor & Support
- Monitor for critical issues in first 24-48 hours
- Be prepared for hotfix release if needed
- Update issue statuses and close completed items

## 🚨 Hotfix Process

### When to Use
- Critical security vulnerability
- Data corruption bug
- Application crash in production
- Major functionality broken

### Process
1. **Create hotfix branch**: `git checkout -b hotfix/critical-fix main`
2. **Implement fix**: Minimal changes only
3. **Test thoroughly**: Full test suite + manual verification
4. **Bump patch version**: `1.2.3` → `1.2.4`
5. **Merge directly**: Bypass PR for critical fixes
6. **Tag and release**: Follow normal release process

## 📊 Release Metrics

### Quality Metrics
- **Test Coverage**: >80% maintained
- **Zero Critical Bugs**: In release notes
- **Performance Baseline**: No regression >10%
- **Build Success Rate**: 100% for releases

### Process Metrics
- **Release Cadence**: Minor releases every 2-4 weeks
- **Time to Release**: <4 hours from preparation start
- **Hotfix Frequency**: <1 per month ideally
- **Rollback Success**: 100% rollback capability

## 🔧 Tools & Automation

### Build Scripts
- `Build_AutoFire.ps1` - Production build
- `Build_AutoFire_Debug.ps1` - Development build
- `setup_dev.ps1` - Development environment

### CI/CD Integration
- GitHub Actions for automated testing
- Pre-commit hooks for code quality
- Automated dependency updates (future)

### Release Automation (Future)
```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: [ "v*" ]
jobs:
  release:
    # Automated build, test, and release
```

## 📞 Emergency Contacts

- **Critical Issues**: [Contact method for urgent issues]
- **Build Failures**: Check CI logs, fix immediately
- **Security Issues**: Halt all work, address immediately

---

## 📝 Checklist Summary

### Pre-Release
- [ ] Version updated in VERSION.txt
- [ ] CHANGELOG.md updated
- [ ] All tests pass
- [ ] Manual QA completed
- [ ] Build successful

### Release
- [ ] Git tag created and pushed
- [ ] GitHub release created
- [ ] Build artifacts uploaded
- [ ] Release announced

### Post-Release
- [ ] Monitor for issues (24-48 hours)
- [ ] Update documentation
- [ ] Close completed issues
