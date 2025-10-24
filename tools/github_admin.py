"""GitHub admin helper: create a repository secret, create rename issue,
and enable branch protection on main.

Usage: set env var GITHUB_PAT (do not commit token). Then run:
    python tools/github_admin.py --owner Obayne --repo AutoFireBase \
        --secret-name AUTOBOT_TOKEN

This script will not print the PAT. It will print high-level
success/failure messages.
"""

import argparse
import base64
import json
import os
import sys

import requests
from nacl import encoding, public


def encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    public_key = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def get_public_key(owner: str, repo: str, headers: dict):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()


def put_secret(owner: str, repo: str, name: str, encrypted, key_id: str, headers: dict):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/{name}"
    payload = {"encrypted_value": encrypted, "key_id": key_id}
    r = requests.put(url, headers=headers, data=json.dumps(payload), timeout=30)
    r.raise_for_status()
    return r.status_code


def create_issue(owner: str, repo: str, title: str, body: str, headers: dict):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    payload = {"title": title, "body": body}
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    r.raise_for_status()
    return r.json()


def enable_branch_protection(owner: str, repo: str, branch: str, headers: dict):
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}/protection"
    # Minimal recommended protection: require status checks (strict) and PR reviews
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
    p.add_argument("--secret-name", default="AUTOBOT_TOKEN")
    p.add_argument("--branch", default="main")
    args = p.parse_args()

    pat = os.environ.get("GITHUB_PAT")
    if not pat:
        print("GITHUB_PAT environment variable not set; aborting", file=sys.stderr)
        sys.exit(1)

    headers = {"Authorization": f"token {pat}", "Accept": "application/vnd.github+json"}

    # 1) Create repo secret
    try:
        key_data = get_public_key(args.owner, args.repo, headers)
        key_id = key_data["key_id"]
        key_b64 = key_data["key"]
        encrypted = encrypt_secret(key_b64, pat)
        put_secret(args.owner, args.repo, args.secret_name, encrypted, key_id, headers)
        print(f"Repository secret '{args.secret_name}' created/updated.")
    except Exception as e:
        print(f"Failed to create secret: {e}", file=sys.stderr)
        # continue to try other actions

    # 2) Create rename proposal issue from docs/RENAME_PROPOSAL.md if present
    body = ""
    mdpath = os.path.join(os.getcwd(), "docs", "RENAME_PROPOSAL.md")
    if os.path.exists(mdpath):
        try:
            with open(mdpath, encoding="utf-8") as f:
                body = f.read()
            title = "Repo rename proposal: replace AutoFire branding"
            issue = create_issue(args.owner, args.repo, title, body, headers)
            print(f"Created issue #{issue.get('number')}: {issue.get('html_url')}")
        except Exception as e:
            print(f"Failed to create issue: {e}", file=sys.stderr)

    # 3) Enable branch protection on main
    try:
        status = enable_branch_protection(args.owner, args.repo, args.branch, headers)
        print(f"Branch protection enabled on {args.branch} (status {status}).")
    except Exception as e:
        print(f"Failed to enable branch protection: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
