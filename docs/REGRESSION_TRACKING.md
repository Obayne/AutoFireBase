# Regression Tracking - v0.7.0+

**Last Updated**: December 3, 2025
**Status**: 🔴 Critical regressions identified during manual testing

---

## 🔥 Critical Issues (Blocks Core Functionality)

### 1. AI System Design Broken

**Status**: 🔴 Critical
**Discovered**: Dec 3, 2025 during manual testing
**Error**: `TypeError: SystemBuilder.design_system() got an unexpected keyword argument 'occupancy_type'`

**Impact**:

- Cannot run automated system design from UI
- Blocks primary AI-assisted workflow
- Users cannot generate FACP/device layouts

**Investigation Needed**:

- [ ] Locate SystemBuilder class
- [ ] Review design_system() signature changes
- [ ] Check if occupancy_type was renamed or removed
- [ ] Verify what parameters are actually supported
- [ ] Update UI calls to match current API

**Test**: `tests/regression/test_ai_system.py::TestSystemBuilderRegression::test_design_system_with_occupancy_type`

---

### 2. Database Items Missing

**Status**: 🟡 High Priority
**Discovered**: Dec 3, 2025 user feedback
**Symptom**: User reports database items are missing

**Impact**:

- Data loss or corruption
- Projects may not load correctly
- Device catalog may be incomplete

**Investigation Needed**:

- [ ] Identify which database items are missing
- [ ] Check for migration failures
- [ ] Verify SQLite database integrity
- [ ] Check catalog JSON loading
- [ ] Review recent schema changes

**Test**: `tests/regression/test_ai_system.py::TestDatabaseIntegration::test_project_persistence`

---

### 3. CAD Functionality Incomplete

**Status**: 🟡 High Priority
**Discovered**: Dec 3, 2025 user feedback
**Symptom**: "CAD portion needs a lot of work"

**Impact**:

- Drawing tools may not work correctly
- Edit operations unreliable
- User experience degraded

**Investigation Needed**:

- [ ] Test each drawing tool (line, arc, circle, polyline, etc.)
- [ ] Test each edit tool (trim, extend, fillet, offset, etc.)
- [ ] Test osnap and selection
- [ ] Identify specific broken operations

**Test**: `tests/regression/test_ai_system.py::TestCADFunctionalityRegression::test_drawing_tools_complete`

---

### 4. AI Assistant "Stiff and Rigid"

**Status**: 🟢 Enhancement
**Discovered**: Dec 3, 2025 user feedback
**Symptom**: AI responses lack flexibility

**Impact**:

- Poor user experience
- AI feels robotic rather than conversational
- May be missing context or using wrong prompts

**Investigation Needed**:

- [ ] Review AI model selection (which model is used?)
- [ ] Check temperature/sampling parameters
- [ ] Review system prompts
- [ ] Add conversation history/context
- [ ] Consider prompt engineering improvements

**Test**: `tests/regression/test_ai_system.py::TestSystemBuilderRegression::test_ai_assistant_stiffness`

---

## 📊 Test Coverage Reality Check

**Current Metrics**:

- Backend coverage: 90% ✅
- CAD core coverage: High ✅
- **Integration coverage: ~0%** 🔴
- **UI workflow coverage: ~0%** 🔴
- **End-to-end coverage: ~0%** 🔴

**The Problem**:
We have excellent **unit test coverage** but almost **zero functional test coverage**.

Tests are focused on:

- ✅ Pure functions (geometry, calculations)
- ✅ Data models and DTOs
- ✅ Isolated services

Tests are missing:

- 🔴 UI interactions and workflows
- 🔴 Database integration and persistence
- 🔴 AI system integration
- 🔴 Tool interactions and state management
- 🔴 Import/export round-trips

---

## 🎯 Testing Strategy Going Forward

### Phase 1: Document All Regressions (This Week)

1. ✅ Create regression test skeleton (xfail tests)
2. ⏳ Manual testing to identify all broken features
3. ⏳ Document each issue in regression tests
4. ⏳ Prioritize by severity

### Phase 2: Fix Critical Regressions (Next Week)

1. Fix SystemBuilder.design_system() API break
2. Identify and restore missing database items
3. Test and fix each CAD tool individually
4. Improve AI assistant prompts/settings

### Phase 3: Add Integration Tests (Ongoing)

1. Add UI workflow tests (pytest-qt)
2. Add database integration tests
3. Add import/export tests with real fixtures
4. Add tool interaction tests

---

## 📝 Known Issues List

### Immediate (Discovered Today)

- [ ] **SystemBuilder.design_system()** - occupancy_type argument missing
- [ ] **Database persistence** - unspecified items missing
- [ ] **CAD tools** - unspecified functionality broken
- [ ] **AI responses** - stiff/rigid behavior
- [ ] **frontend.tool_registry** - import error in tests
- [ ] **Geometry warnings** - QWindowsWindow::setGeometry warnings

### From Previous Testing

- [ ] Pre-commit mypy hook - types-pkg-resources dependency issue
- [ ] Black formatting - some files fail to parse
- [ ] Icon files missing (installer)
- [ ] LICENSE file missing (installer)

---

## 🔄 Testing Workflow

### Before Each Release

1. Run full unit test suite: `pytest tests/ -v`
2. Run regression tests: `pytest tests/regression/ -v`
3. Manual smoke test checklist:
   - [ ] Create new project
   - [ ] Draw basic shapes (line, arc, circle)
   - [ ] Run AI system design
   - [ ] Save and reload project
   - [ ] Export/import DXF
   - [ ] Verify device catalog loads

### When Adding Features

1. Write regression test first (if fixing bug)
2. Write unit tests for new code
3. Add integration test if touching UI/database
4. Update this document with any new known issues

---

## 📅 Regression Fix Schedule

**Week of Dec 3-9**:

- [ ] Investigate SystemBuilder API change
- [ ] Document all broken CAD tools
- [ ] Identify missing database items
- [ ] Create manual test protocol

**Week of Dec 10-16**:

- [ ] Fix SystemBuilder.design_system()
- [ ] Restore missing database items
- [ ] Fix top 5 broken CAD tools
- [ ] Improve AI prompt engineering

**Week of Dec 17-23**:

- [ ] Add integration test suite
- [ ] Achieve 50% functional test coverage
- [ ] Document all known issues
- [ ] Create release checklist

---

## 🎓 Lessons Learned

1. **High unit test coverage ≠ working software**
   - 90% backend coverage missed major UI breaks
   - Need integration and E2E tests

2. **Manual testing is essential**
   - Automated tests don't catch UX issues
   - Need regular smoke testing protocol

3. **API changes need deprecation warnings**
   - SystemBuilder change broke silently
   - Need better interface versioning

4. **Test what matters to users**
   - Focus on user workflows
   - Cover most common use cases first

---

**Next Review**: December 10, 2025
**Owner**: Development Team
**Priority**: Critical - blocks v0.7.0 production use
