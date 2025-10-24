#!/usr/bin/env python3
"""Create an issue from docs/RENAME_PROPOSAL.md and enable branch protection.
Usage: python tools/github_issue_protect.py --owner Obayne --repo AutoFireBase \
    --token-path C:\\Dev\\git_provided.txt
"""

import argparse
import json
import os

import requests


def create_issue(owner, repo, title, body, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    r = requests.post(
        url, headers=headers, data=json.dumps({"title": title, "body": body}), timeout=30
    )
    r.raise_for_status()
    return r.json()


def enable_branch_protection(owner, repo, branch, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}/protection"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    payload = {
        "required_status_checks": {"strict": True, "contexts": ["CI"]},
        "enforce_admins": True,
        "required_pull_request_reviews": {"required_approving_review_count": 1},
        "restrictions": None,
    }
    r = requests.put(url, headers=headers, data=json.dumps(payload), timeout=30)
    r.raise_for_status()
    return r.status_code


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--owner", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--token-path", required=True)
    p.add_argument("--branch", default="main")
    args = p.parse_args()

    if not os.path.exists(args.token_path):
        print("Token file not found", flush=True)
        return
    token = open(args.token_path).read().strip()

    # create issue
    md = os.path.join("docs", "RENAME_PROPOSAL.md")
    if os.path.exists(md):
        body = open(md, encoding="utf-8").read()
        title = "Repo rename proposal: replace AutoFire branding"
        try:
            iss = create_issue(args.owner, args.repo, title, body, token)
            print(f"Created issue #{iss.get('number')}: {iss.get('html_url')}")
        except Exception as e:
            print("Failed to create issue:", e)
    else:
        print("Rename proposal doc not found; skipping issue creation")

    try:
        status = enable_branch_protection(args.owner, args.repo, args.branch, token)
        print(f"Branch protection enabled on {args.branch} (status {status})")
    except Exception as e:
        print("Failed to enable branch protection:", e)


if __name__ == "__main__":
    main()
