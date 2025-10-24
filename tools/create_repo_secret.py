"""Create a GitHub repository secret from a local PAT file.

Usage: python tools/create_repo_secret.py --owner Obayne --repo AutoFireBase \
    --name <secret_name> --token-path PATH

This script does NOT print the PAT; it only reports success/failure.
"""

import argparse
import base64
import json
import os
import sys

try:
    import requests
    from nacl import encoding, public
except ImportError:
    print(
        "Missing dependencies. Please run: python -m pip install requests pynacl",
        file=sys.stderr,
    )
    sys.exit(2)


def load_token(path):
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    public_key = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--owner", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--name", required=True)
    p.add_argument(
        "--token-path",
        default=None,
        help=(
            "Path to the PAT file (required). Do NOT commit this file. "
            "If not provided the script will exit."
        ),
    )
    args = p.parse_args()

    token_path = args.token_path
    if not token_path:
        print(
            "Error: --token-path is required. Provide a path to a file containing\n"
            "your GitHub PAT (one line).",
            file=sys.stderr,
        )
        sys.exit(2)

    if not os.path.exists(token_path):
        print(f"Token file not found at {token_path}", file=sys.stderr)
        sys.exit(1)

    pat = load_token(token_path)
    if not pat:
        print("Token file is empty", file=sys.stderr)
        sys.exit(1)

    headers = {"Authorization": f"token {pat}", "Accept": "application/vnd.github+json"}
    base = f"https://api.github.com/repos/{args.owner}/{args.repo}"

    # Get the public key for repo secrets
    r = requests.get(base + "/actions/secrets/public-key", headers=headers)
    if r.status_code != 200:
        print("Failed to fetch repository public key:", r.status_code, r.text)
        sys.exit(1)

    key_data = r.json()
    key_id = key_data.get("key_id")
    key_b64 = key_data.get("key")
    if not key_id or not key_b64:
        print("Invalid public key response")
        sys.exit(1)

    encrypted_value = encrypt_secret(key_b64, pat)

    payload = {
        "encrypted_value": encrypted_value,
        "key_id": key_id,
    }

    put_url = base + f"/actions/secrets/{args.name}"
    r2 = requests.put(put_url, headers=headers, data=json.dumps(payload))
    if r2.status_code in (201, 204):
        print(f"Secret '{args.name}' created/updated successfully (repo: {args.owner}/{args.repo})")
        # delete the local file securely
        try:
            os.remove(token_path)
            print(f"Local token file '{token_path}' deleted.")
        except OSError as e:
            print("Warning: failed to delete local token file:", e)
        sys.exit(0)
    else:
        print("Failed to create secret:", r2.status_code, r2.text)
        sys.exit(1)


if __name__ == "__main__":
    main()
