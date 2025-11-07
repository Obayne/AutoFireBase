# GitHub Automation Quick Reference

This document outlines the automations configured for the repository and how to interpret their outputs.

Workflows included:

- Dependabot (weekly): creates dependency update PRs for pip and GitHub Actions.
- Stale management: marks and closes stale issues/PRs.
- Welcome: posts a short comment on new PRs/issues to help first-time contributors.
- PR size labeler: automatically labels PRs with `pr-size:*` labels.
- Auto-merge (draft): marks PRs eligible for auto-merge but does not perform merges without admin approval.

Labels and conventions

- `strangler`: migration PRs moving code to `lv_cad`.
- `devops`: CI/automation PRs.
- `needs-review` / `ci-pass` / `ci-fail`: used by reviewer workflows.

If you need a workflow changed (e.g., thresholds), open a draft PR referencing this doc and propose the YAML changes.
