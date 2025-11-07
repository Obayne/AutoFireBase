# Automation Flow

Simple diagram (markdown):

- PR opened -> PR size labeler -> run CI -> request @codex review -> apply labels

Dependabot -> open dependency PR -> run CI -> label `devops` -> human review

Stale scheduled -> mark inactive -> close after grace period
