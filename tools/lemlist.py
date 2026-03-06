#!/usr/bin/env python3
"""
Lemlist campaign tools.

Usage:
    python3 tools/lemlist.py add-lead --campaign-id "ID" --email "e@co.com" --first-name "J" --last-name "D" --company "Acme" --title "CMO" --linkedin "https://linkedin.com/in/jd"
    python3 tools/lemlist.py list-campaigns

Reads API key from config/api-keys.json.
Authentication: HTTP Basic with empty username, API key as password.
"""

import argparse
import base64
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "api-keys.json"
API_BASE = "https://api.lemlist.com/api"


def load_api_key():
    with open(CONFIG_PATH) as f:
        keys = json.load(f)
    key = keys.get("lemlist")
    if not key:
        print("ERROR: No lemlist key found in config/api-keys.json", file=sys.stderr)
        sys.exit(1)
    return key


def auth_header(api_key):
    """Lemlist uses Basic auth with empty username and API key as password."""
    encoded = base64.b64encode(f":{api_key}".encode()).decode()
    return f"Basic {encoded}"


def api_request(api_key, method, endpoint, data=None):
    url = f"{API_BASE}{endpoint}"

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", auth_header(api_key))
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "JasperOS/1.0")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_body = resp.read().decode()
            return json.loads(resp_body) if resp_body else {"status": "ok"}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "detail": error_body}
    except Exception as e:
        return {"error": str(e)}


def add_lead(api_key, campaign_id, email, first_name=None, last_name=None,
             company=None, title=None, linkedin=None):
    """Add a single lead to a Lemlist campaign."""
    payload = {"email": email}
    if first_name:
        payload["firstName"] = first_name
    if last_name:
        payload["lastName"] = last_name
    if company:
        payload["companyName"] = company
    if title:
        payload["jobTitle"] = title
    if linkedin:
        payload["linkedinUrl"] = linkedin

    # Lemlist requires cam_ prefix on campaign IDs
    if not campaign_id.startswith("cam_"):
        campaign_id = f"cam_{campaign_id}"
    result = api_request(api_key, "POST", f"/campaigns/{campaign_id}/leads/", data=payload)
    return result


def list_campaigns(api_key):
    """List all Lemlist campaigns."""
    result = api_request(api_key, "GET", "/campaigns")
    return result


def main():
    parser = argparse.ArgumentParser(description="Lemlist campaign tools")
    subparsers = parser.add_subparsers(dest="command")

    # add-lead
    add_cmd = subparsers.add_parser("add-lead", help="Add a lead to a campaign")
    add_cmd.add_argument("--campaign-id", required=True, help="Lemlist campaign ID")
    add_cmd.add_argument("--email", required=True, help="Lead email")
    add_cmd.add_argument("--first-name", help="First name")
    add_cmd.add_argument("--last-name", help="Last name")
    add_cmd.add_argument("--company", help="Company name")
    add_cmd.add_argument("--title", help="Job title")
    add_cmd.add_argument("--linkedin", help="LinkedIn profile URL")

    # list-campaigns
    subparsers.add_parser("list-campaigns", help="List all campaigns")

    args = parser.parse_args()
    api_key = load_api_key()

    if args.command == "add-lead":
        result = add_lead(
            api_key, args.campaign_id, args.email,
            first_name=args.first_name, last_name=args.last_name,
            company=args.company, title=args.title, linkedin=args.linkedin
        )
        print(json.dumps(result, indent=2))

    elif args.command == "list-campaigns":
        result = list_campaigns(api_key)
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
