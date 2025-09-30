# AutoFire CI/CD Infrastructure

## Overview

This repository uses GitHub Actions for CI/CD with fast lint/tests, reproducible builds, and basic security hygiene.

## Workflows

### 1) Continuous Integration (`.github/workflows/ci.yml`)
- Triggers: push, pull_request, workflow_dispatch
- Matrix: ubuntu-latest and windows-latest
- Steps: setup Python 3.11, install deps, Ruff, Black (check), pytest

### 2) Security Scan (`.github/workflows/security.yml`)
- Triggers: push, pull_request, schedule (weekly), manual
- Tools:
  - Bandit (SAST) – SARIF uploaded to GitHub Security tab
  - Safety (dependency vulnerability check)

### 3) Release (`.github/workflows/release.yml`)
- Trigger: tag push (v*), manual
- Builds: PyInstaller artifacts uploaded to the release

### 4) Maintenance (`.github/workflows/maintenance.yml`)
- Triggers: schedule (weekly), manual
- Tasks: report outdated Python packages; optional cache/repo hygiene

## Usage

Run from Actions tab or locally with GitHub CLI:

```
gh workflow run ci.yml
gh workflow run security.yml
gh workflow run maintenance.yml
gh workflow run release.yml
```

## Configuration

- Python version: 3.11
- Secrets:
  - `GITHUB_TOKEN` (provided) – SARIF upload, workflow permissions
  - `CODECOV_TOKEN` (optional) – only if coverage upload is added
- Customize:
  - Edit `.github/workflows/*`
  - Lint rules in `pyproject.toml`
  - Tests via `pytest.ini`
