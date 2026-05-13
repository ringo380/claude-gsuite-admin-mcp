#!/usr/bin/env python3
"""Exchange OAuth authorization code for credentials.

Workaround for setup_oauth.py's interactive input(), which buffers/truncates very
long redirect URLs in some terminals (zsh on macOS in particular). Pass the full
redirect URL — or just the raw code — as an argv arg instead.

Usage:
    python exchange_code.py 'http://localhost:4100/code?code=4/...&scope=...'
    python exchange_code.py '4/0AeoWuM-...'
"""
import json
import os
import sys
from urllib.parse import urlparse, parse_qs

from claude_gsuite_admin.auth.oauth_manager import OAuthManager


def load_primary_account():
    accounts_file = os.environ.get(
        "GSUITE_ACCOUNTS_FILE",
        os.path.join(os.path.dirname(__file__), ".accounts.json"),
    )
    with open(accounts_file) as fh:
        data = json.load(fh)
    accounts = data.get("accounts", [])
    if not accounts:
        raise RuntimeError(f"No accounts configured in {accounts_file}")
    email = accounts[0]["email"]
    return email, email.split("@", 1)[1]


def extract_code(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("http"):
        qs = parse_qs(urlparse(raw).query)
        if "code" in qs:
            return qs["code"][0]
    if "code=" in raw:
        return raw.split("code=", 1)[1].split("&", 1)[0]
    return raw


def main():
    if len(sys.argv) < 2:
        print("Usage: python exchange_code.py '<full-redirect-url-or-just-code>'")
        sys.exit(1)

    auth_code = extract_code(sys.argv[1])
    user_email, user_domain = load_primary_account()
    print(f"Exchanging code for {user_email} (domain: {user_domain})")
    print(f"Code: {auth_code[:25]}...")

    om = OAuthManager()
    creds = om.get_credentials(user_email, auth_code)
    if not creds:
        print("Failed to exchange code")
        sys.exit(1)

    print(f"Saved credentials for {user_email}")
    print("Testing Directory API...")
    svc = om.get_service(user_email, "admin", "directory_v1")
    res = svc.users().list(domain=user_domain, maxResults=3).execute()
    users = res.get("users", [])
    print(f"OK — found {len(users)} user(s):")
    for u in users:
        print(f"  - {u.get('primaryEmail')}")


if __name__ == "__main__":
    main()
