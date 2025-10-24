# Repository Rename Proposal: Replace 'AutoFire' branding

Context
-------
The current repository and product branding use the name "AutoFire" / "AutoFireBase". You mentioned legal entanglement with this name; renaming the repository and codebase to a neutral name reduces risk and clarifies ownership.

Goals
-----
- Pick a short, neutral name not tied to existing trademarks.
- Minimize breaking changes for users and CI.
- Preserve history and provide a migration plan for local devs and CI.

Candidate names (examples)
--------------------------
- "af-builder" (short, neutral)
- "panelforge" (product-oriented)
- "system-assembler"
- "autobase" (avoid if related to AutoFire)

Migration plan (high-level)
---------------------------
1. Choose the new repo name and confirm stakeholders.
2. Create an issue and a branch `rename/<new-name>` to stage name changes.
3. Update repository metadata (name, description, topics) in GitHub.
4. Update package names & top-level directories if desired (opt-in, risky):
   - Option A (minimal): Keep package names and only rename repo. Update docs, README, logos.
   - Option B (rename code packages): Update `pyproject.toml`, import paths, and CI; requires more testing.
5. Add redirects and update documentation: README, install instructions, workflow references.
6. Notify users and maintainers via an issue and a short migration guide.

Risks & notes
-------------
- Renaming the GitHub repo preserves git history and opens a redirect, but package import paths and pypi packages are unaffected unless you rename package names.
- CI workflows, badges, and URLs might need updates after rename.

Next steps I can take
---------------------
- Open a GitHub issue with this proposal (I can do this if you allow me to use repository automation credentials to create issues), or
- Create a PR that implements the minimal metadata updates (README, description, docs) once you approve the chosen name.

If you want, tell me which candidate name you prefer or say "pick one" and I'll propose a final candidate and create the GitHub issue.
