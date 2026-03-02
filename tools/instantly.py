#!/usr/bin/env python3
"""
Instantly.ai campaign tools.

Usage:
    python3 tools/instantly.py list-campaigns --search "campaign name"
    python3 tools/instantly.py add-leads --campaign-id "ID" --leads '[{"email":"...","first_name":"...","company_name":"..."}]'

Reads API key from config/api-keys.json.
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "api-keys.json"
API_BASE = "https://api.instantly.ai/api/v2"


def load_api_key():
    with open(CONFIG_PATH) as f:
        keys = json.load(f)
    key = keys.get("instantly")
    if not key:
        print("ERROR: No instantly key found in config/api-keys.json", file=sys.stderr)
        sys.exit(1)
    return key


def api_request(api_key, method, endpoint, data=None, params=None):
    url = f"{API_BASE}{endpoint}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "JasperOS/1.0")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "detail": error_body}
    except Exception as e:
        return {"error": str(e)}


def list_campaigns(api_key, search=None):
    params = {"limit": "100"}
    if search:
        params["search"] = search
    result = api_request(api_key, "GET", "/campaigns", params=params)
    return result


def add_leads(api_key, campaign_id, leads):
    """Add leads to a campaign via POST /leads/add (batch endpoint)."""
    payload = {
        "campaign_id": campaign_id,
        "skip_if_in_campaign": True,
        "leads": leads,
    }
    result = api_request(api_key, "POST", "/leads/add", data=payload)

    if "error" in result:
        return {"campaign_id": campaign_id, "error": result["error"]}

    return {
        "campaign_id": campaign_id,
        "total_sent": result.get("total_sent", 0),
        "leads_uploaded": result.get("leads_uploaded", 0),
        "duplicated_leads": result.get("duplicated_leads", 0),
        "skipped_count": result.get("skipped_count", 0),
        "invalid_email_count": result.get("invalid_email_count", 0),
        "in_blocklist": result.get("in_blocklist", 0),
        "remaining_in_plan": result.get("remaining_in_plan"),
    }


def main():
    parser = argparse.ArgumentParser(description="Instantly.ai campaign tools")
    subparsers = parser.add_subparsers(dest="command")

    # list-campaigns
    list_cmd = subparsers.add_parser("list-campaigns", help="List campaigns")
    list_cmd.add_argument("--search", help="Search by campaign name")

    # add-leads
    add_cmd = subparsers.add_parser("add-leads", help="Add leads to a campaign")
    add_cmd.add_argument("--campaign-id", required=True, help="Instantly campaign ID")
    add_cmd.add_argument("--leads", required=True, help="JSON array of lead objects")

    args = parser.parse_args()
    api_key = load_api_key()

    if args.command == "list-campaigns":
        result = list_campaigns(api_key, search=args.search)
        print(json.dumps(result, indent=2))

    elif args.command == "add-leads":
        leads = json.loads(args.leads)
        result = add_leads(api_key, args.campaign_id, leads)
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
