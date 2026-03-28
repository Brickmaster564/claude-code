#!/usr/bin/env python3
"""
Revolut Business API tool for Nalu.

Auth flow (one-time setup):
  python tools/revolut.py auth          → prints URL to visit in browser
  python tools/revolut.py exchange --code CODE  → saves tokens to config/revolut-token.json

Ongoing use (tokens auto-refresh):
  python tools/revolut.py accounts
  python tools/revolut.py transactions [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--account ACCOUNT_ID] [--limit N]
  python tools/revolut.py counterparties
"""

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

import jwt  # PyJWT
import requests

# ── Config ────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"

PRIVATE_KEY_PATH = CONFIG_DIR / "revolut_private.pem"
TOKEN_PATH = CONFIG_DIR / "revolut-token.json"

CLIENT_ID = "mOgeIWc1kuh21EgE-wNNNJAQ4NTGE5Lqy4B6jUKRTLk"
REDIRECT_URI = "https://nalupartners.com/revolut/callback"
ISS = "nalupartners.com"
AUD = "https://revolut.com"

API_BASE = "https://b2b.revolut.com/api/1.0"
AUTH_BASE = "https://b2b.revolut.com/api/1.0"

# ── JWT & Auth ────────────────────────────────────────────────────────────────

def load_private_key():
    if not PRIVATE_KEY_PATH.exists():
        print(f"ERROR: Private key not found at {PRIVATE_KEY_PATH}", file=sys.stderr)
        sys.exit(1)
    return PRIVATE_KEY_PATH.read_text()


def make_client_assertion():
    """Generate a signed JWT client assertion for Revolut OAuth."""
    private_key = load_private_key()
    now = int(time.time())
    payload = {
        "iss": ISS,
        "sub": CLIENT_ID,
        "aud": AUD,
        "iat": now,
        "nbf": now,
        "exp": now + 90,  # short-lived; only needed for token exchange
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


def load_tokens():
    if not TOKEN_PATH.exists():
        return None
    with open(TOKEN_PATH) as f:
        return json.load(f)


def save_tokens(data):
    with open(TOKEN_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Tokens saved to {TOKEN_PATH}", file=sys.stderr)


def get_access_token():
    """Return a valid access token, refreshing if needed."""
    tokens = load_tokens()
    if not tokens:
        print("ERROR: No tokens found. Run: python tools/revolut.py auth", file=sys.stderr)
        sys.exit(1)

    # Check if access token is still valid (with 60s buffer)
    expires_at = tokens.get("expires_at", 0)
    if time.time() < expires_at - 60:
        return tokens["access_token"]

    # Refresh
    print("Access token expired, refreshing...", file=sys.stderr)
    assertion = make_client_assertion()
    resp = requests.post(
        f"{AUTH_BASE}/auth/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": assertion,
            "client_id": CLIENT_ID,
        },
    )
    if not resp.ok:
        print(f"ERROR: Token refresh failed: {resp.status_code} {resp.text}", file=sys.stderr)
        print("Re-run auth flow: python tools/revolut.py auth", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    data["expires_at"] = int(time.time()) + data.get("expires_in", 2400)
    save_tokens(data)
    return data["access_token"]


def check_refresh_token_expiry():
    """Warn if refresh token is expiring within 14 days."""
    tokens = load_tokens()
    if not tokens:
        return
    rt_expires = tokens.get("refresh_token_expires_at")
    if not rt_expires:
        return
    days_left = (rt_expires - time.time()) / (24 * 3600)
    if days_left < 0:
        print("WARNING: Revolut refresh token has expired. Re-auth required: python3 tools/revolut.py auth", file=sys.stderr)
    elif days_left < 14:
        print(f"WARNING: Revolut refresh token expires in {int(days_left)} days. Re-auth soon: python3 tools/revolut.py auth", file=sys.stderr)


def api_get(path, params=None):
    check_refresh_token_expiry()
    token = get_access_token()
    resp = requests.get(
        f"{API_BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
    )
    if not resp.ok:
        print(f"ERROR: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)
    return resp.json()


def cmd_status(args):
    """Show auth status and token expiry."""
    import datetime
    tokens = load_tokens()
    if not tokens:
        print("Not authenticated. Run: python3 tools/revolut.py auth")
        return

    now = time.time()
    access_expires = tokens.get("expires_at", 0)
    refresh_expires = tokens.get("refresh_token_expires_at")

    print("\nRevolut Auth Status")
    print("-" * 40)
    if now < access_expires:
        mins = int((access_expires - now) / 60)
        print(f"Access token:   valid ({mins} min remaining)")
    else:
        print("Access token:   EXPIRED (will auto-refresh on next call)")

    if tokens.get("refresh_token"):
        if refresh_expires:
            days = (refresh_expires - now) / (24 * 3600)
            expiry_str = datetime.datetime.fromtimestamp(refresh_expires).strftime("%Y-%m-%d")
            status = f"valid until {expiry_str} ({int(days)} days)"
            if days < 14:
                status += " — RE-AUTH SOON"
            print(f"Refresh token:  {status}")
        else:
            print("Refresh token:  present (expiry unknown — run auth to reset)")
    else:
        print("Refresh token:  MISSING — re-auth required: python3 tools/revolut.py auth")
    print()


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_auth(args):
    """Open the Revolut authorization URL in a browser."""
    auth_url = (
        f"https://business.revolut.com/app-confirm"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=READ"
    )
    print("\nOpening Revolut authorization in your browser...")
    subprocess.run(["open", auth_url])
    print("\nApprove access in the browser.")
    print(f"You'll be redirected to: {REDIRECT_URI}?code=XXXX")
    print("The page may 404 — that's fine. Copy the full URL from the address bar.\n")
    print("Then run:")
    print("  python3 tools/revolut.py exchange --code YOUR_CODE\n")
    print("(Or paste the full redirect URL as the --code value — it'll extract the code automatically)\n")


def cmd_exchange(args):
    """Exchange an authorization code for access + refresh tokens."""
    if not args.code:
        print("ERROR: --code is required", file=sys.stderr)
        sys.exit(1)

    # Accept full redirect URL — extract code automatically
    code = args.code
    if "code=" in code:
        code = code.split("code=")[-1].split("&")[0].strip()

    assertion = make_client_assertion()
    resp = requests.post(
        f"{AUTH_BASE}/auth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": assertion,
            "client_id": CLIENT_ID,
        },
    )

    if not resp.ok:
        print(f"ERROR: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    now = int(time.time())
    data["expires_at"] = now + data.get("expires_in", 2400)
    if data.get("refresh_token"):
        data["refresh_token_expires_at"] = now + (90 * 24 * 3600)  # 90 days
    save_tokens(data)

    if not data.get("refresh_token"):
        print("WARNING: Revolut did not return a refresh_token.", file=sys.stderr)
        print("You will need to re-auth when the access token expires (~40 min).", file=sys.stderr)
        print("This may indicate an issue with your Revolut Business API app configuration.", file=sys.stderr)
    else:
        import datetime
        expiry = datetime.datetime.fromtimestamp(data["refresh_token_expires_at"]).strftime("%Y-%m-%d")
        print(f"Auth successful. Revolut connected.")
        print(f"Refresh token valid until ~{expiry} (90 days). Auto-refresh handles access tokens.")


def cmd_accounts(args):
    """List all Revolut Business accounts."""
    accounts = api_get("/accounts")
    if args.json:
        print(json.dumps(accounts, indent=2))
        return

    print(f"\n{'Account':<40} {'Currency':<10} {'Balance':>12} {'State':<10}")
    print("-" * 76)
    for acc in accounts:
        print(
            f"{acc.get('name', acc['id']):<40} "
            f"{acc['currency']:<10} "
            f"{acc['balance']:>12.2f} "
            f"{acc.get('state', ''):<10}"
        )
    print()


def cmd_transactions(args):
    """Fetch transactions with optional date and account filters."""
    params = {}
    if args.from_date:
        params["from"] = f"{args.from_date}T00:00:00Z"
    if args.to_date:
        params["to"] = f"{args.to_date}T23:59:59Z"
    if args.account:
        params["account"] = args.account
    if args.limit:
        params["count"] = args.limit

    txns = api_get("/transactions", params=params)

    if args.json:
        print(json.dumps(txns, indent=2))
        return

    # Summarise
    total_in = sum(t["legs"][0]["amount"] for t in txns if t["legs"][0]["amount"] > 0)
    total_out = sum(t["legs"][0]["amount"] for t in txns if t["legs"][0]["amount"] < 0)

    print(f"\nTransactions: {len(txns)}")
    print(f"Total in:  {total_in:>10.2f}")
    print(f"Total out: {total_out:>10.2f}")
    print(f"Net:       {total_in + total_out:>10.2f}\n")

    print(f"{'Date':<12} {'Description':<40} {'Amount':>10} {'Currency':<6} {'Type':<12}")
    print("-" * 84)
    for t in txns:
        leg = t["legs"][0]
        date = t.get("created_at", "")[:10]
        desc = t.get("merchant", {}).get("name") or t.get("reference", "") or t.get("type", "")
        desc = str(desc)[:38]
        amount = leg.get("amount", 0)
        currency = leg.get("currency", "")
        ttype = t.get("type", "")
        print(f"{date:<12} {desc:<40} {amount:>10.2f} {currency:<6} {ttype:<12}")
    print()


def cmd_counterparties(args):
    """List all counterparties (clients/vendors)."""
    data = api_get("/counterparties")
    if args.json:
        print(json.dumps(data, indent=2))
        return

    print(f"\n{'Name':<40} {'Type':<10} {'Country':<8} {'ID'}")
    print("-" * 80)
    for cp in data:
        print(
            f"{cp.get('name', ''):<40} "
            f"{cp.get('type', ''):<10} "
            f"{cp.get('country', ''):<8} "
            f"{cp['id']}"
        )
    print()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Revolut Business API tool")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("auth", help="Open OAuth authorization URL in browser")
    sub.add_parser("status", help="Show auth status and token expiry")

    p_exchange = sub.add_parser("exchange", help="Exchange auth code for tokens")
    p_exchange.add_argument("--code", required=True, help="Authorization code or full redirect URL")

    p_accounts = sub.add_parser("accounts", help="List accounts and balances")
    p_accounts.add_argument("--json", action="store_true")

    p_txns = sub.add_parser("transactions", help="List transactions")
    p_txns.add_argument("--from", dest="from_date", help="Start date YYYY-MM-DD")
    p_txns.add_argument("--to", dest="to_date", help="End date YYYY-MM-DD")
    p_txns.add_argument("--account", help="Filter by account ID")
    p_txns.add_argument("--limit", type=int, default=100)
    p_txns.add_argument("--json", action="store_true")

    p_cp = sub.add_parser("counterparties", help="List counterparties")
    p_cp.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "auth":
        cmd_auth(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "exchange":
        cmd_exchange(args)
    elif args.command == "accounts":
        cmd_accounts(args)
    elif args.command == "transactions":
        cmd_transactions(args)
    elif args.command == "counterparties":
        cmd_counterparties(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
