#!/usr/bin/env python3
"""
Re-authenticate a Google account to get a fresh refresh token.

Usage:
    python3 tools/google-reauth.py --account cn
    python3 tools/google-reauth.py --account nalu
"""

import json
import http.server
import urllib.request
import urllib.parse
import webbrowser
import sys
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"

ACCOUNTS = {
    "cn": {
        "credentials": "google-credentials.json",
        "token": "google-token.json",
    },
    "nalu": {
        "credentials": "google-credentials-nalu.json",
        "token": "google-token-nalu.json",
    },
}

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/spreadsheets",
]

REDIRECT_PORT = 8085
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"


def main():
    account = "cn"
    if "--account" in sys.argv:
        idx = sys.argv.index("--account")
        account = sys.argv[idx + 1]

    if account not in ACCOUNTS:
        print(f"Unknown account: {account}. Use: {', '.join(ACCOUNTS.keys())}")
        sys.exit(1)

    cred_path = CONFIG_DIR / ACCOUNTS[account]["credentials"]
    token_path = CONFIG_DIR / ACCOUNTS[account]["token"]

    with open(cred_path) as f:
        creds = json.load(f)

    app = creds.get("installed") or creds.get("web") or creds
    client_id = app["client_id"]
    client_secret = app["client_secret"]

    # Build authorization URL
    params = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    })
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{params}"

    print(f"\nRe-authenticating: {account}")
    print(f"Opening browser...\n")
    webbrowser.open(auth_url)

    # Wait for the redirect with the auth code
    auth_code = None

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal auth_code
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            auth_code = params.get("code", [None])[0]

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h2>Authentication successful!</h2><p>You can close this tab.</p></body></html>")

        def log_message(self, format, *args):
            pass  # Suppress server logs

    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), Handler)
    print(f"Waiting for Google redirect on port {REDIRECT_PORT}...")
    server.handle_request()

    if not auth_code:
        print("ERROR: No auth code received.")
        sys.exit(1)

    # Exchange code for tokens
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }).encode()

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        method="POST",
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())

    token_data = {
        "token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": client_id,
        "client_secret": client_secret,
        "scopes": SCOPES,
    }

    with open(token_path, "w") as f:
        json.dump(token_data, f, indent=2)

    print(f"\nToken saved to {token_path}")
    print("Re-authentication complete.")


if __name__ == "__main__":
    main()
