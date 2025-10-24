#!/usr/bin/env python3
"""Create branches and PRs by uploading files from the local workspace.
Requires env GITHUB_PAT to be set to a token with repo permissions.

This script will:
- Create a branch from main
- Upload listed files to that branch (create or update)
- Open a PR from the branch into main

Usage: Set GITHUB_PAT and run:
  python tools/github_create_prs.py --owner Obayne --repo AutoFireBase

Be careful: this will push files that exist in the workspace to the repo.
"""

import argparse
import base64
import json
import os
from pathlib import Path

import requests

API_BASE = "https://api.github.com"


def read_file_bytes(p: Path):
    with p.open("rb") as f:
        return f.read()


def get_default_branch_sha(owner, repo, headers):
    url = f"{API_BASE}/repos/{owner}/{repo}"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()["default_branch"], (
        r.json()["sha"] if "sha" in r.json() else r.json()["default_branch"]
    )


def get_branch_sha(owner, repo, branch, headers):
    url = f"{API_BASE}/repos/{owner}/{repo}/git/refs/heads/{branch}"
    r = requests.get(url, headers=headers, timeout=30)
    if r.status_code == 200:
        return r.json()["object"]["sha"]
    r.raise_for_status()


def create_branch(owner, repo, branch, sha, headers):
    url = f"{API_BASE}/repos/{owner}/{repo}/git/refs"
    payload = {"ref": f"refs/heads/{branch}", "sha": sha}
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    r.raise_for_status()
    return r.json()


def upload_file(owner, repo, path_in_repo, content_bytes, branch, message, headers):
    url = f"{API_BASE}/repos/{owner}/{repo}/contents/{path_in_repo}"
    b64 = base64.b64encode(content_bytes).decode("utf-8")
    payload = {"message": message, "content": b64, "branch": branch}
    r = requests.put(url, headers=headers, data=json.dumps(payload), timeout=30)
    # If file exists, GitHub requires 'sha' of existing file; try to detect and use update
    if r.status_code == 201:
        return r.json()
    if r.status_code == 422 and "already exists" in r.text:
        # try to get sha and update
        getr = requests.get(url + f"?ref={branch}", headers=headers, timeout=30)
        if getr.status_code == 200:
            sha = getr.json().get("sha")
            payload["sha"] = sha
            r2 = requests.put(url, headers=headers, data=json.dumps(payload), timeout=30)
            r2.raise_for_status()
            return r2.json()
    r.raise_for_status()


def create_pr(owner, repo, head, base, title, body, headers):
    url = f"{API_BASE}/repos/{owner}/{repo}/pulls"
    payload = {"title": title, "head": head, "base": base, "body": body}
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    r.raise_for_status()
    return r.json()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--owner", required=True)
    p.add_argument("--repo", required=True)
    args = p.parse_args()

    token = os.environ.get("GITHUB_PAT")
    # also accept token path for environments where setting env is inconvenient
    if not token:
        # try reading token from a provided file path via env
        token_path = os.environ.get("GITHUB_PAT_FILE")
        if token_path and os.path.exists(token_path):
            token = open(token_path, encoding="utf-8").read().strip()
    if not token:
        print("GITHUB_PAT not set and no token file provided; aborting")
        return
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}

    owner = args.owner
    repo = args.repo

    # Files to push grouped per PR
    workspace = Path.cwd()

    pr_sets = [
        {
            "branch": "chore/dependabot-config",
            "title": "chore: enable Dependabot (weekly pip updates)",
            "body": (
                "Enable Dependabot to open weekly dependency update PRs " "for Python packages."
            ),
            "files": [".github/dependabot.yml"],
        },
        {
            "branch": "docs/rename-proposal",
            "title": "docs: add repository rename proposal",
            "body": "Add the repository rename proposal and migration plan.",
            "files": ["docs/RENAME_PROPOSAL.md"],
        },
        {
            "branch": "chore/automation-log",
            "title": "chore: add automation activity log and helper",
            "body": (
                "Add tools/automation/agent_activity.log and "
                "tools/automation/append_activity.py for traceability "
                "of automated actions."
            ),
            "files": [
                "tools/automation/agent_activity.log",
                "tools/automation/append_activity.py",
            ],
        },
    ]

    # Get main branch sha
    # Use refs API
    r = requests.get(
        f"{API_BASE}/repos/{owner}/{repo}/git/refs/heads/main", headers=headers, timeout=30
    )
    if r.status_code != 200:
        print("Failed to read main branch ref; aborting")
        print(r.status_code, r.text)
        return
    main_sha = r.json()["object"]["sha"]

    for pr in pr_sets:
        branch = pr["branch"]
        print(f"Processing PR branch: {branch}")
        # Create branch
        try:
            create_branch(owner, repo, branch, main_sha, headers)
            print(f"Created branch {branch}")
        except Exception as e:
            # branch may already exist
            print(f"Branch create warning: {e}")
        # Upload files
        for f in pr["files"]:
            local = workspace / f
            if not local.exists():
                print(f"Local file not found, skipping: {local}")
                continue
            content = read_file_bytes(local)
            try:
                upload_file(owner, repo, f, content, branch, f"Add {f}", headers)
                print(f"Uploaded {f} to {branch}")
            except Exception as e:
                print(f"Failed to upload {f}: {e}")
        # Create PR
        try:
            res = create_pr(owner, repo, branch, "main", pr["title"], pr["body"], headers)
            print(f'Created PR: {res.get("html_url")}')
        except Exception as e:
            print(f"Failed to create PR from {branch}: {e}")


if __name__ == "__main__":
    main()
