# Phase 2 Roadmap: Production Hardening

**Timeline:** December 2025 - January 2026
**Focus:** Production deployment readiness
**Status:** Planning

---

## 🎯 Phase 2 Goals

1. **Production Monitoring** - Sentry error tracking
2. **Distribution** - Windows installer (NSIS/MSI)
3. **Performance** - Baseline metrics and regression detection
4. **Reliability** - Error handling and recovery

---

## 📋 Task Breakdown

### Task 1: Sentry Error Tracking

**Priority:** High
**Estimated Time:** 2-4 hours
**Dependencies:** None

#### Deliverables

- [ ] Install `sentry-sdk` package
- [ ] Add Sentry initialization to `backend/tracing.py`
- [ ] Configure DSN for production environment
- [ ] Add error boundaries in critical paths
- [ ] Test error reporting flow
- [ ] Document Sentry setup in README

#### Implementation Steps

```python
# backend/tracing.py
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

def init_sentry(dsn: str | None = None, environment: str = "production"):
    """Initialize Sentry error tracking."""
    dsn = dsn or os.environ.get("SENTRY_DSN")
    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=0.1,  # 10% of transactions
        profiles_sample_rate=0.1,
        integrations=[
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)
        ],
        before_send=filter_sensitive_data,
    )
```

#### Success Criteria

- Errors logged to Sentry dashboard
- Source maps work correctly
- PII filtered out
- Performance overhead < 5%

---

### Task 2: Windows Installer

**Priority:** High
**Estimated Time:** 4-8 hours
**Dependencies:** PyInstaller build working

#### Deliverables

- [ ] Choose installer framework (NSIS recommended)
- [ ] Create installer script (.nsi file)
- [ ] Add desktop shortcuts
- [ ] Add file associations (.lvcad files)
- [ ] Test installation/uninstallation
- [ ] Add to release workflow
- [ ] Document installer creation

#### NSIS Script Outline

```nsis
; LV_CAD.nsi
!define APP_NAME "LV CAD"
!define APP_VERSION "0.7.0"
!define APP_PUBLISHER "AutoFire"
!define APP_EXE "LV_CAD.exe"

; Modern UI
!include "MUI2.nsh"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Install section
Section "Install"
    SetOutPath "$INSTDIR"
    File /r "dist\LV_CAD\*.*"

    ; Desktop shortcut
    CreateShortCut "$DESKTOP\LV CAD.lnk" "$INSTDIR\${APP_EXE}"

    ; Start menu
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"

    ; File association
    WriteRegStr HKCR ".lvcad" "" "LVCADFile"
    WriteRegStr HKCR "LVCADFile\shell\open\command" "" '"$INSTDIR\${APP_EXE}" "%1"'

    ; Uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

; Uninstall section
Section "Uninstall"
    Delete "$DESKTOP\LV CAD.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    RMDir /r "$INSTDIR"
    DeleteRegKey HKCR ".lvcad"
    DeleteRegKey HKCR "LVCADFile"
SectionEnd
```

#### Build Integration

```powershell
# Build_Installer.ps1
param(
    [string]$Version = "0.7.0"
)

# Build executable
.\Build_LV_CAD.ps1

# Create installer
& "C:\Program Files (x86)\NSIS\makensis.exe" /DAPP_VERSION=$Version LV_CAD.nsi

# Sign installer (optional)
# signtool sign /f cert.pfx /p password "LV_CAD_Setup_${Version}.exe"

# Verify installer
if (Test-Path "LV_CAD_Setup_${Version}.exe") {
    Write-Host "✅ Installer created successfully"
    Get-Item "LV_CAD_Setup_${Version}.exe" | Select-Object Name, Length
} else {
    Write-Error "❌ Installer creation failed"
}
```

#### Success Criteria

- One-click installation works
- Desktop shortcut functional
- File associations work (.lvcad opens in LV CAD)
- Clean uninstallation removes all files
- Installer size < 50MB

---

### Task 3: Performance Baselines

**Priority:** Medium
**Estimated Time:** 2-3 hours
**Dependencies:** None

#### Deliverables

- [ ] Document current benchmark times
- [ ] Set regression thresholds (±5%)
- [ ] Add performance tests to pytest
- [ ] Create performance dashboard (optional)
- [ ] Add to CI as optional checks

#### Benchmark Suite

```python
# tests/performance/test_benchmarks.py
import pytest
import time
from lv_cad.operations import offset, fillet
from lv_cad.geometry import Point, Line

@pytest.mark.benchmark
def test_offset_performance(benchmark):
    """Benchmark offset operation."""
    polyline = [(0, 0), (100, 0), (100, 100), (0, 100)]
    result = benchmark(offset.offset_polyline, polyline, 10.0)
    assert result is not None

@pytest.mark.benchmark
def test_fillet_performance(benchmark):
    """Benchmark fillet operation."""
    line1 = Line(Point(0, 0), Point(10, 0))
    line2 = Line(Point(10, 0), Point(10, 10))
    result = benchmark(fillet.compute_fillet, line1, line2, 2.0)
    assert result is not None

# Run with: pytest -m benchmark --benchmark-autosave
```

#### Performance Thresholds

```yaml
# .performance-thresholds.yml
offset_polyline:
  baseline: 0.002  # seconds
  threshold: 0.0021  # +5%

fillet_compute:
  baseline: 0.001
  threshold: 0.00105

full_test_suite:
  baseline: 5.0
  threshold: 5.25
```

#### CI Integration

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on:
  pull_request:
    types: [labeled]

jobs:
  benchmark:
    if: contains(github.event.pull_request.labels.*.name, 'performance')
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements-dev.txt pytest-benchmark
      - run: pytest -m benchmark --benchmark-json=output.json
      - uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: 'pytest'
          output-file-path: output.json
```

#### Success Criteria

- Baseline times documented
- Regression detection works
- CI runs performance tests on demand
- Performance report generated

---

### Task 4: Enhanced Error Handling

**Priority:** Medium
**Estimated Time:** 3-5 hours
**Dependencies:** Sentry integration

#### Deliverables

- [ ] Add try/except blocks in critical paths
- [ ] User-friendly error messages
- [ ] Error recovery mechanisms
- [ ] Logging enhancements
- [ ] Error reporting UI

#### Error Boundaries

```python
# backend/error_handling.py
from typing import Callable, TypeVar, ParamSpec
import logging
from functools import wraps

P = ParamSpec('P')
T = TypeVar('T')

def with_error_handling(
    operation: str,
    user_message: str | None = None,
    fallback_value: T | None = None
) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
    """Decorator for consistent error handling."""
    def decorator(func: Callable[P, T]) -> Callable[P, T | None]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f"{operation} failed: {e}", exc_info=True)
                if sentry_sdk:
                    sentry_sdk.capture_exception(e)

                if user_message:
                    show_error_dialog(user_message, str(e))

                return fallback_value
        return wrapper
    return decorator

# Usage
@with_error_handling(
    operation="DXF Import",
    user_message="Failed to import DXF file",
    fallback_value=None
)
def import_dxf(filepath: str) -> DXFDocument | None:
    return ezdxf.readfile(filepath)
```

#### User Error Dialog

```python
# frontend/dialogs/error_dialog.py
from PySide6.QtWidgets import QMessageBox, QTextEdit

def show_error_dialog(title: str, message: str, details: str | None = None):
    """Show user-friendly error dialog with optional technical details."""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)

    if details:
        msg.setDetailedText(details)

    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec()
```

#### Success Criteria

- No unhandled exceptions reach user
- Clear error messages in UI
- Technical details available in logs
- Errors tracked in Sentry

---

## 📊 Success Metrics

### Overall Phase 2 Goals

- **Sentry:** > 95% error capture rate
- **Installer:** < 5 minute installation time
- **Performance:** No regressions > 5%
- **Error Handling:** Zero unhandled exceptions in production

### Quality Gates

- All Phase 2 tasks completed
- Integration tests passing
- User acceptance testing complete
- Documentation updated

---

## 🗓️ Timeline

### Week 1 (Dec 2-8)

- ✅ Complete Phase 1 (PR #64 merged)
- ✅ Tag v0.7.0
- [ ] Set up Sentry project
- [ ] Install Sentry SDK
- [ ] Test error reporting

### Week 2 (Dec 9-15)

- [ ] Create NSIS installer script
- [ ] Test installer on clean Windows VM
- [ ] Add installer to build workflow
- [ ] Document installer process

### Week 3 (Dec 16-22)

- [ ] Implement performance benchmarks
- [ ] Set baseline metrics
- [ ] Add CI performance checks
- [ ] Create performance dashboard

### Week 4 (Dec 23-29)

- [ ] Enhanced error handling
- [ ] Error recovery mechanisms
- [ ] User error dialogs
- [ ] Integration testing

### Week 5 (Dec 30 - Jan 5)

- [ ] Final testing
- [ ] Documentation updates
- [ ] Phase 2 release (v0.8.0)
- [ ] Phase 3 planning

---

## 🎓 Learning Resources

### Sentry

- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)
- [PySide6 Integration](https://docs.sentry.io/platforms/python/integrations/qt/)

### NSIS

- [NSIS Documentation](https://nsis.sourceforge.io/Docs/)
- [Modern UI](https://nsis.sourceforge.io/Docs/Modern%20UI%202/Readme.html)

### Performance Testing

- [pytest-benchmark](https://pytest-benchmark.readthedocs.io/)
- [GitHub Actions Benchmark](https://github.com/benchmark-action/github-action-benchmark)

---

## 🚧 Risks & Mitigation

### Risk 1: Sentry Overhead

- **Impact:** Performance degradation
- **Mitigation:** Sample rate 10%, async reporting
- **Fallback:** Disable in performance-critical paths

### Risk 2: Installer Size

- **Impact:** Long download times
- **Mitigation:** UPX compression, remove debug symbols
- **Fallback:** Web installer (downloads files on demand)

### Risk 3: Performance Regression

- **Impact:** Slower application
- **Mitigation:** Automated benchmarks, CI checks
- **Fallback:** Revert commits causing regressions

---

## 📝 Notes

- **Platform Focus:** Windows only for Phase 2
- **Python Version:** 3.11+ required
- **Qt Version:** PySide6 6.10.0
- **Build Tool:** PyInstaller 6.11.1

---

**Phase 2 Owner:** DevOps Team
**Review Cadence:** Weekly
**Go-Live Target:** January 15, 2026
