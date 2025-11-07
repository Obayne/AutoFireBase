<!-- PR template for onboarding automated reviewers like @codex -->
## Summary

Describe the change in one or two sentences.

## Checklist

- [ ] Backup created (if modifying entrypoint)
- [ ] Parity test added (if migration)
- [ ] Linters run and code formatted
- [ ] Unit tests added/updated
- [ ] CI passing

## Testing notes

Provide any notes necessary to run the tests or reproduce the change locally.

## Reviewer guidance

- Focus on behavioral parity for migrated modules under `/cad_core/`, `/lv_cad/`, and `/backend/`.
- If this is a migration, ensure the parity test exercises representative inputs and tolerances for numerical outputs.

_Auto-requested reviewer: @codex (review-only)_

## Summary

Briefly describe the change and why it’s needed.

## Linked Issue

Closes #<number>

## Changes

-

## Testing

- [ ] Unit tests added/updated
- [ ] `pytest -q` passes locally
- [ ] CI green

## Checklist

- [ ] Follows style (Black/Ruff)
- [ ] Docs updated (README/docs/* if needed)
