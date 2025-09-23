Param(
  [string]$Remote = "origin",
  [switch]$SkipTests
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Require-CleanTree {
  $status = git status --porcelain
  if ($status) {
    throw "Working tree not clean. Please commit/stash before running."
  }
}

function Branch-Exists([string]$branch) {
  $out = git ls-remote --heads $Remote $branch
  return -not [string]::IsNullOrEmpty($out)
}

function Wait-For-Remote-Branch([string]$branch, [int]$TimeoutSec = 60) {
  $start = Get-Date
  while (-not (Branch-Exists $branch)) {
    if ((Get-Date) - $start -gt [TimeSpan]::FromSeconds($TimeoutSec)) {
      throw "Timed out waiting for '$branch' on '$Remote'."
    }
    Start-Sleep -Seconds 2
  }
}

function Run-Tests([string[]]$Targets) {
  if ($SkipTests) { return }
  python -m pip install -e . | Out-Null
  if ($Targets -and $Targets.Count -gt 0) {
    $args = @("-q") + $Targets
  } else {
    $args = @("-q")
  }
  Write-Host "pytest $($args -join ' ')"
  pytest @args
}

function Commit-And-Push([string]$branch, [string]$message, [string[]]$paths, [string[]]$tests) {
  Write-Host "==> Branch: $branch" -ForegroundColor Cyan
  git checkout -B $branch
  if ($paths -and $paths.Count -gt 0) {
    git add -- $paths
  } else {
    git add -A
  }
  if (-not (git diff --cached --quiet)) {
    git commit -m $message
  } else {
    Write-Host "No staged changes for $branch; skipping commit."
  }
  Run-Tests $tests
  git push -u $Remote $branch -f
  Wait-For-Remote-Branch $branch
  Write-Host "Pushed $branch" -ForegroundColor Green
}

# Ensure repo and update main
git rev-parse --is-inside-work-tree | Out-Null
git fetch $Remote
git checkout main
git pull $Remote main

# PR 1: Repo scaffold
Commit-And-Push `
  -branch "chore/repo-scaffold" `
  -message "chore: repo scaffold with Black/Ruff, pytest, base dirs" `
  -paths @("pyproject.toml","pytest.ini",".gitignore",".editorconfig","tests/test_sanity.py","frontend/__init__.py","backend/__init__.py","cad_core/__init__.py") `
  -tests @("tests/test_sanity.py")

# PR 2: Agent + Contrib docs
Commit-And-Push `
  -branch "docs/agent-guide-and-contrib" `
  -message "docs: add agent guide, contributing, and architecture overview" `
  -paths @("AGENTS.md","docs/CONTRIBUTING.md","docs/ARCHITECTURE.md") `
  -tests @()

# PR 3: Tooling scripts + pre-commit
Commit-And-Push `
  -branch "chore/tooling-scripts-precommit" `
  -message "chore: add lint/format/test scripts and pre-commit hooks" `
  -paths @("scripts/lint","scripts/format","scripts/test",".pre-commit-config.yaml","docs/CONTRIBUTING.md") `
  -tests @()

# PR 4: Backend settings
Commit-And-Push `
  -branch "feat/backend-settings" `
  -message "feat(backend): add typed settings loader with env/file overrides" `
  -paths @("backend/settings.py","tests/backend/test_settings.py") `
  -tests @("tests/backend/test_settings.py")

# PR 5: Storage abstraction
Commit-And-Push `
  -branch "feat/backend-storage" `
  -message "feat(backend): add storage interface and in-memory impl" `
  -paths @("backend/storage.py","tests/backend/test_storage.py") `
  -tests @("tests/backend/test_storage.py")

# PR 6: CAD units
Commit-And-Push `
  -branch "feat/cad-units" `
  -message "feat(cad_core): add units conversions and helpers" `
  -paths @("cad_core/units.py","tests/cad_core/test_units.py") `
  -tests @("tests/cad_core/test_units.py")

# PR 7: Geometry primitives
Commit-And-Push `
  -branch "feat/cad-geom" `
  -message "feat(cad_core): add Point/Vector primitives and ops" `
  -paths @("cad_core/geom.py","tests/cad_core/test_geom.py") `
  -tests @("tests/cad_core/test_geom.py")

# PR 8: Core ops
Commit-And-Push `
  -branch "feat/cad-ops" `
  -message "feat(cad_core): add transforms and bounding box ops" `
  -paths @("cad_core/ops.py","tests/cad_core/test_ops.py") `
  -tests @("tests/cad_core/test_ops.py")

# PR 9: Frontend skeleton
Commit-And-Push `
  -branch "feat/frontend-skeleton" `
  -message "feat(frontend): add Qt app entry and main window skeleton" `
  -paths @("frontend/app.py","frontend/main_window.py","tests/frontend/test_smoke.py") `
  -tests @("tests/frontend/test_smoke.py")

# PR 10: PR template + CI
Commit-And-Push `
  -branch "chore/gh-pr-template-and-ci" `
  -message "chore: add PR template and CI workflow" `
  -paths @(".github/PULL_REQUEST_TEMPLATE.md",".github/workflows/ci.yml") `
  -tests @()

# PR 11: Point helpers
Commit-And-Push `
  -branch "feat/cad-point" `
  -message "feat(cad_core): add Point with distance, equals, and move" `
  -paths @("cad_core/point.py") `
  -tests @("tests/cad_core/test_point.py")

Write-Host "All branches prepared and pushed (where changes were present)." -ForegroundColor Cyan
Write-Host "Open PRs on GitHub; checker can proceed." -ForegroundColor Cyan

# Include CAD PR 12: lines (now implemented)
Commit-And-Push `
  -branch "feat/cad-lines" `
  -message "feat(cad_core): add Line API (intersection/trim/extend) and helpers" `
  -paths @("cad_core/lines.py","cad_core/__init__.py") `
  -tests @("tests/cad_core/test_lines.py")

# Commit-And-Push `
#   -branch "feat/cad-segments" `
#   -message "feat(cad_core): add segment ops and intersections" `
#   -paths @("cad_core/segments.py","tests/cad_core/test_segments.py") `
#   -tests @("tests/cad_core/test_segments.py")

# Commit-And-Push `
#   -branch "feat/cad-trim-extend" `
#   -message "feat(cad_core): add trim/extend operations" `
#   -paths @("cad_core/trim_extend.py","tests/cad_core/test_trim_extend.py") `
#   -tests @("tests/cad_core/test_trim_extend.py")

# Commit-And-Push `
#   -branch "feat/cad-circle" `
#   -message "feat(cad_core): add circle primitives and intersections" `
#   -paths @("cad_core/circle.py","tests/cad_core/test_circle.py") `
#   -tests @("tests/cad_core/test_circle.py")

# Commit-And-Push `
#   -branch "feat/cad-fillet" `
#   -message "feat(cad_core): add fillet primitives and ops" `
#   -paths @("cad_core/fillet.py","cad_core/fillet_ops.py","tests/cad_core/test_fillet.py","tests/cad_core/test_fillet_ops.py") `
#   -tests @("tests/cad_core/test_fillet.py","tests/cad_core/test_fillet_ops.py")
