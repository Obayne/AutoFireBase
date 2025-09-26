# Tasklist: Changelog + Workflows Hardening

Goal: Clean up CHANGELOG and standardize/strengthen CI/CD + automation while keeping main green.

## Changelog
- [ ] Add "Unreleased" section at top (Keep a Changelog style) with compare link.
- [ ] Normalize version style to match tags (prefer `vX.Y.Z` everywhere; release tags use `v*`).
- [ ] Fix encoding artifacts across entries; ensure UTF-8.
- [ ] Add compare links between versions (optional).
- [ ] Verify each tag has a matching changelog entry; backfill if missing.

## CI
- [x] Add pip caching keyed to requirements files and Python version.
- [x] Add OS matrix (ubuntu+windows) with Python 3.11.
- [x] Add concurrency to cancel in-progress duplicate runs per ref.
- [x] Add non-blocking mypy step (continue-on-error).
- [ ] Consider adding Python 3.10/3.12 if supported.
- [ ] Add coverage reporting (`pytest --cov`) and upload coverage artifact.
- [ ] Ensure branch protection requires CI before merge (repo setting).

## Release workflow
- [x] Update artifact upload to handle timestamped fallback path (match `dist/**/AutoFire.exe`).
- [x] Generate and upload SHA256 checksum for the artifact.
- [x] Attach `VERSION.txt` and release notes (CHANGELOG slice) to the GitHub Release.
- [ ] Validate Release job end-to-end with a test tag.

## Labeling and ownership
- [x] Standardize labels in `labeler.yml` to `area:backend`, `area:frontend`, `area:cad_core` (no spaces/hyphens).
- [ ] Optionally enhance area detection by changed paths rather than branch names.
- [ ] Confirm `assign-owners.yml` mappings match standardized labels.
- [ ] Ensure required labels exist (pre-create or via seed workflow) using the standardized names.

## Agent Orchestrator
- [ ] Replace `git branch --show-current` detection with `github.ref_name` or env input from orchestrator.
- [ ] Ensure the orchestrator pushes new branches using `GITHUB_TOKEN` auth.
- [ ] Auto-link PRs to triggering issues when event is `issues:labeled`.

## Issue templates
- [x] Fix UTF-8 encoding glitches (e.g., "+/- corrupted LOC line)."
- [x] Re-save templates as UTF-8 and verify rendering.

## Documentation
- [ ] Update `RELEASE.md` to mention fallback build path and checksums.
- [ ] Add a short CI section to `docs/CONTRIBUTING.md` (lint, format, tests, type-check).

## Verification
- [ ] Run CI on a branch to confirm Windows job passes (headless tests with PySide6 present).
