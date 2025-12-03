# AutoFireBase Project Calendar & Tracking

**Project**: AutoFire LV CAD
**Phase**: v0.7.0 Stabilization & Regression Fixes
**Last Updated**: December 3, 2025

---

## 📅 December 2025

### Week 1 (Dec 2-8): v0.7.0 Release & Regression Discovery

#### ✅ Completed

- **Dec 2**: Merged PR #64 (LV CAD scaffold + 90% backend coverage)
- **Dec 2**: Created v0.7.0 release tag
- **Dec 3**: Added Windows installer infrastructure (NSIS)
- **Dec 3**: Added Sentry error tracking integration
- **Dec 3**: Added performance baseline tests + CI
- **Dec 3**: Built Windows installer (108.39 MB)
- **Dec 3**: Created Sentry integration test suite (6/6 passing)
- **Dec 3**: Published GitHub release v0.7.0

#### 🔴 Critical Issues Discovered

- **Dec 3**: SystemBuilder.design_system() API break (occupancy_type)
- **Dec 3**: Database items missing (specifics TBD)
- **Dec 3**: CAD functionality incomplete
- **Dec 3**: AI assistant stiffness reported

#### ⏳ In Progress

- **Dec 3**: Creating regression test suite
- **Dec 3**: Documenting all broken features
- **Dec 3**: Setting up project tracking system

#### 📋 Planned This Week

- [ ] Complete regression test documentation
- [ ] Investigate SystemBuilder API changes
- [ ] Manual test all CAD tools - document broken ones
- [ ] Identify missing database items
- [ ] Create prioritized fix list

---

### Week 2 (Dec 9-15): Critical Regression Fixes

#### 🎯 Goals

1. Fix SystemBuilder.design_system() API
2. Restore missing database items
3. Fix top 5 broken CAD tools
4. Improve AI assistant flexibility

#### 📋 Planned Tasks

- [ ] **Mon**: Investigate SystemBuilder class location and current API
- [ ] **Tue**: Fix occupancy_type parameter issue
- [ ] **Wed**: Database integrity check - identify missing items
- [ ] **Thu**: CAD tool audit - test each drawing/edit tool
- [ ] **Fri**: Fix highest priority CAD tool issues

#### 🎯 Success Criteria

- [ ] AI system design works from UI
- [ ] No data loss on project save/load
- [ ] At least 5 CAD tools fully functional
- [ ] Zero critical regressions

---

### Week 3 (Dec 16-22): Integration Testing & Coverage

#### 🎯 Goals

1. Add integration test suite
2. Achieve 50% functional test coverage
3. Create manual test protocol
4. Fix remaining CAD tools

#### 📋 Planned Tasks

- [ ] **Mon**: Set up pytest-qt for UI testing
- [ ] **Tue**: Write database integration tests
- [ ] **Wed**: Write DXF import/export tests
- [ ] **Thu**: Write tool workflow tests
- [ ] **Fri**: Manual smoke test - document process

#### 🎯 Success Criteria

- [ ] 20+ integration tests passing
- [ ] Manual test checklist created
- [ ] All critical workflows covered by tests
- [ ] CI runs integration tests

---

### Week 4 (Dec 23-29): Holiday Week - Documentation & Polish

#### 🎯 Goals

1. Complete documentation updates
2. Polish UI/UX issues
3. Prepare v0.7.1 release
4. Year-end review

#### 📋 Planned Tasks

- [ ] Update all documentation
- [ ] Create user-facing changelog
- [ ] Add custom icon to installer
- [ ] Add LICENSE file
- [ ] Performance optimization pass

---

## 📊 Metrics & Tracking

### Test Coverage

| Category | Current | Target | Status |
|----------|---------|--------|--------|
| Unit Tests | 90% backend | 95% | 🟢 |
| Integration Tests | ~0% | 50% | 🔴 |
| Functional Tests | ~0% | 80% | 🔴 |
| Manual Smoke Tests | Ad-hoc | Documented | 🟡 |

### Known Issues

| Priority | Count | This Week Target |
|----------|-------|------------------|
| 🔴 Critical | 4 | Fix 3 |
| 🟡 High | TBD | Fix 5 |
| 🟢 Medium | TBD | Document all |
| ⚪ Low | TBD | Backlog |

### Performance Baselines (v0.7.0)

| Operation | Baseline | Current | Status |
|-----------|----------|---------|--------|
| Line creation | 1.0 μs | 1.0 μs | ✅ |
| Fillet | 12.5 μs | 12.5 μs | ✅ |
| Batch lines (100) | 85.8 μs | 85.8 μs | ✅ |

---

## 🎯 Milestones

### v0.7.0 (Dec 2, 2025) - ✅ Released

- ✅ LV CAD scaffold complete
- ✅ 90% backend test coverage
- ✅ Performance baseline established
- ✅ Windows installer built
- ✅ Sentry error tracking integrated
- 🔴 **Critical regressions discovered post-release**

### v0.7.1 (Target: Dec 20, 2025) - 🎯 Planned

- Fix all critical regressions
- Restore broken functionality
- Add integration test suite
- 50% functional test coverage
- Manual test protocol documented

### v0.8.0 (Target: Jan 15, 2026) - 📋 Planned

- Native offset implementation
- Trim/extend operations complete
- Advanced curve handling
- 95% overall test coverage

---

## 📞 Team Communication

### Daily Standup (When Active)

- **Time**: Flexible
- **Format**: Async updates in chat
- **Focus**: Blockers, progress, plans

### Weekly Review

- **Day**: Friday
- **Format**: Progress summary
- **Artifacts**: Updated calendar, metrics

### Monthly Planning

- **Day**: First Monday of month
- **Format**: Roadmap review
- **Artifacts**: Updated milestones

---

## 🔗 Quick Links

### Documentation

- [Regression Tracking](REGRESSION_TRACKING.md)
- [Production Features Test Results](PRODUCTION_FEATURES_TEST_RESULTS.md)
- [Installer Build Results](INSTALLER_BUILD_RESULTS.md)
- [Performance Testing](PERFORMANCE.md)
- [Testing Guide](TESTING.md)

### GitHub

- [v0.7.0 Release](https://github.com/Obayne/AutoFireBase/releases/tag/v0.7.0)
- [PR #64 - LV CAD Scaffold](https://github.com/Obayne/AutoFireBase/pull/64)
- [Issues](https://github.com/Obayne/AutoFireBase/issues)
- [Project Board](https://github.com/Obayne/AutoFireBase/projects)

### CI/CD

- [Main CI Workflow](https://github.com/Obayne/AutoFireBase/actions/workflows/ci.yml)
- [Performance CI](https://github.com/Obayne/AutoFireBase/actions/workflows/performance.yml)

---

## 📝 Notes & Decisions

### Dec 3, 2025

- **Decision**: Prioritize regression fixes over new features
- **Reason**: v0.7.0 has critical functional regressions that block usage
- **Impact**: Delay v0.8.0 features until v0.7.1 is stable

### Dec 2, 2025

- **Decision**: Publish v0.7.0 release despite ongoing Phase 2 work
- **Reason**: Backend foundation is solid, production features code-complete
- **Impact**: Release demonstrates progress, installer ready for testing

---

**Next Calendar Review**: December 10, 2025
**Owner**: Development Team
**Questions/Updates**: Post in project chat or update this doc
