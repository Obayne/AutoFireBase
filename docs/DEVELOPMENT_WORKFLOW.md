# Continuous Development Workflow

## 🎯 Overview

This document establishes the **continuous development practices** for AutoFire, ensuring clarity on **what**, **when**, **who**, and **how** for all development activities. All work must align with the [Master Specification](MASTER_SPECIFICATION.rtf).

## 📋 What: Requirements & Specifications

### Primary References
- **[Master Specification](MASTER_SPECIFICATION.rtf)** - Authoritative scope of work and product vision
- **[AGENTS.md](../AGENTS.md)** - Development principles and team guidelines
- **GitHub Issues** - Detailed requirements with acceptance criteria

### Work Definition Process
1. **Feature Request** → Create GitHub issue using feature request template
2. **Requirements Analysis** → Reference master specification for alignment
3. **Acceptance Criteria** → Define clear, testable completion conditions
4. **Technical Design** → Document implementation approach in issue comments

### Code Standards
- **Style**: Black (100 char lines) + Ruff linting
- **Architecture**: Modular design (frontend/backend/cad_core)
- **Testing**: pytest with coverage, no PR without tests for logic changes
- **Documentation**: Update docs for API/behavior changes

## ⏰ When: Development Timeline

### Sprint Cycle (2 weeks)
```
Week 1: Planning → Development → Testing
Week 2: Integration → Review → Release
```

### Daily Workflow
- **Morning**: Check issues, update status, plan day's work
- **Development**: Small, focused commits (<300 lines)
- **Evening**: Test locally, update issues, prepare for next day

### Branch Lifecycle
- **Creation**: `feat/`, `fix/`, `chore/`, `docs/` prefixes
- **Duration**: Max 3-5 days per feature branch
- **Merging**: Via PR with review, keep `main` always green

### Release Cadence
- **Patch Releases**: As needed for critical fixes
- **Minor Releases**: Every 2-4 weeks with feature sets
- **Major Releases**: Major architectural changes (rare)

## 👥 Who: Roles & Responsibilities

### Code Ownership (CODEOWNERS)
```
# Core Architecture
/frontend/controller.py @lead-dev
/cad_core/algorithms/ @cad-expert
/backend/services/ @backend-dev

# Feature Areas
docs/MASTER_SPECIFICATION.rtf @product-owner
*.md @tech-writer
```

### Review Process
- **Required Reviews**: At least 1 human approval for all PRs
- **Reviewers**: Domain experts for changed areas
- **Review Criteria**:
  - Code quality (style, architecture)
  - Test coverage
  - Documentation updates
  - Master spec alignment

### Accountability
- **Issue Creator**: Defines requirements and acceptance criteria
- **Developer**: Implements solution, writes tests, updates docs
- **Reviewer**: Ensures quality and alignment
- **Product Owner**: Validates against master specification

## 🔧 How: Development Process

### 1. Issue Creation
```markdown
## Summary
[Clear, actionable description]

## Linked Master Spec Section
[Reference to MASTER_SPECIFICATION.rtf section]

## Acceptance Criteria
- [ ] Feature implemented according to spec
- [ ] Tests pass (pytest -q)
- [ ] Documentation updated
- [ ] No breaking changes
```

### 2. Branch & Development
```bash
# Create feature branch
git checkout -b feat/add-system-builder

# Development cycle
while not done:
    # Make small changes
    edit files
    run tests locally
    commit with clear message

# Keep commits focused
git commit -m "feat: implement device staging in system builder

- Add DeviceStagingWidget to frontend/widgets/
- Connect to backend catalog service
- Add unit tests for staging logic"
```

### 3. Testing Strategy
```bash
# Local testing before PR
pytest -q                           # Run all tests
pytest tests/frontend/ -v          # Specific test suite
black --check . && ruff check .    # Code quality
python app/main.py                 # Manual testing
```

### 4. Pull Request Process
```markdown
## PR Template Compliance
- [x] Summary describes change and rationale
- [x] Linked issue with acceptance criteria
- [x] Changes listed clearly
- [x] Testing checklist complete
- [x] Style checklist complete

## Review Requirements
- [x] CI passes (lint, format, tests)
- [x] At least 1 human review approval
- [x] No merge conflicts
- [x] Branch up-to-date with main
```

### 5. Release Process
```bash
# Version bump (semantic versioning)
# X.Y.Z where X=major, Y=minor, Z=patch
echo "1.2.3" > VERSION.txt

# Update changelog
# See CHANGELOG.md for format

# Tag release
git tag -a v1.2.3 -m "Release v1.2.3: Add system builder feature"
git push origin v1.2.3
```

## 🛠️ Tools & Automation

### CI/CD Pipeline
- **GitHub Actions**: Automated testing on every push/PR
- **Pre-commit Hooks**: Code quality enforcement
- **Dependency Management**: requirements.txt + pip
- **Build System**: PyInstaller for releases

### Quality Gates
```yaml
# Must pass before merge
- ruff check .          # Linting
- black --check .       # Formatting
- pytest -q            # Unit tests
- python app/main.py   # Smoke test
```

### Monitoring & Metrics
- **Test Coverage**: Aim for 80%+ coverage
- **Build Status**: CI must be green
- **Code Quality**: Ruff/Black compliance
- **Documentation**: Updated with code changes

## 🚨 Exception Handling

### Breaking Changes
- Require major version bump
- Update migration guide
- Communicate to all stakeholders
- Test backward compatibility

### Hotfixes
- Create `fix/critical-issue` branch from main
- Bypass normal review for critical issues
- Apply fix, test thoroughly
- Merge directly to main with explanation

### Technical Debt
- Document in issue with "technical-debt" label
- Schedule in next sprint
- Don't accumulate - address regularly

## 📊 Success Metrics

### Process Metrics
- **Sprint Velocity**: Story points completed per sprint
- **Code Review Time**: <24 hours average
- **CI Build Time**: <10 minutes
- **Bug Fix Time**: <48 hours for critical issues

### Quality Metrics
- **Test Coverage**: >80%
- **Code Quality**: 0 linting errors
- **Documentation**: Updated with all features
- **Master Spec Alignment**: 100% feature compliance

## 🔄 Continuous Improvement

### Retrospective Process
- **Weekly**: Team reviews past week's work
- **Monthly**: Process improvements and tooling updates
- **Quarterly**: Architecture and tooling audits

### Feedback Loops
- **Code Reviews**: Technical feedback
- **User Testing**: Feature validation
- **Performance Monitoring**: System health
- **Customer Feedback**: Product direction

---

## 📞 Quick Reference

**Need Help?**
- Check [Master Specification](MASTER_SPECIFICATION.rtf) first
- Review [AGENTS.md](../AGENTS.md) for principles
- Create issue for new work
- Ask in PR for implementation questions

**Emergency?**
- Critical bugs: Direct to lead dev
- Build broken: Check CI logs, fix immediately
- Security issue: Halt all work, address immediately

This workflow ensures **predictable, high-quality development** aligned with the AutoFire vision.
