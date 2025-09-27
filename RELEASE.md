# Releases and Versioning

We use Semantic Versioning: MAJOR.MINOR.PATCH.
- MAJOR: incompatible changes
- MINOR: new functionality, backwards compatible
- PATCH: bug fixes and internal changes

Tags and changelog
- Every release is tagged on main as `vX.Y.Z`.
- `CHANGELOG.md` follows Keep a Changelog format with an Unreleased section.

Workflow
- Merge feature PRs into `main`.
- Bump version and update changelog: `./scripts/bump_version.ps1 -Part patch|minor|major -Message "Short summary"`
- Push commit and tag. CI creates a GitHub Release and attaches the Windows build.

Artifacts
- GitHub Actions builds on Windows and uploads `AutoFire.exe` from `dist/**/AutoFire.exe` (supports fallback timestamped dist paths).
- Release includes a SHA256 checksum file alongside the EXE.

Notes
- Do not tag from a dirty tree. Ensure CI is green before tagging.
- If a release fails, fix on a new commit and re-tag with an incremented PATCH version.
