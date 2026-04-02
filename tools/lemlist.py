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


def add_lead(api_key, campaign_id, email=None, first_name=None, last_name=None,
             company=None, title=None, linkedin=None):
    """Add a single lead to a Lemlist campaign."""
    payload = {}
    if email:
        payload["email"] = email
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


def list_leads(api_key, campaign_id):
    """List all leads in a Lemlist campaign with their status.

    Paginates automatically. Returns lead details including step status.
    """
    if not campaign_id.startswith("cam_"):
        campaign_id = f"cam_{campaign_id}"

    all_leads = []
    offset = 0
    limit = 100

    while True:
        result = api_request(api_key, "GET", f"/campaigns/{campaign_id}/leads?offset={offset}&limit={limit}")

        if isinstance(result, dict) and "error" in result:
            return {"error": result["error"], "leads": all_leads}

        if not result or (isinstance(result, list) and len(result) == 0):
            break

        items = result if isinstance(result, list) else result.get("leads", result.get("data", []))
        if not items:
            break

        all_leads.extend(items)

        if len(items) < limit:
            break

        offset += limit

    return {"total": len(all_leads), "leads": all_leads}


def update_lead(api_key, email, updates):
    """Update a lead's fields via PATCH /leads/{email}.

    `updates` is a dict of fields to change (e.g. {"companyName": "New Name"}).
    """
    result = api_request(api_key, "PATCH", f"/leads/{email}", data=updates)
    return result


def delete_lead(api_key, campaign_id, email):
    """Delete a single lead from a Lemlist campaign."""
    if not campaign_id.startswith("cam_"):
        campaign_id = f"cam_{campaign_id}"
    result = api_request(api_key, "DELETE", f"/campaigns/{campaign_id}/leads/{email}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Lemlist campaign tools")
    subparsers = parser.add_subparsers(dest="command")

    # add-lead
    add_cmd = subparsers.add_parser("add-lead", help="Add a lead to a campaign")
    add_cmd.add_argument("--campaign-id", required=True, help="Lemlist campaign ID")
    add_cmd.add_argument("--email", required=False, default=None, help="Lead email (optional for LinkedIn-only leads)")
    add_cmd.add_argument("--first-name", help="First name")
    add_cmd.add_argument("--last-name", help="Last name")
    add_cmd.add_argument("--company", help="Company name")
    add_cmd.add_argument("--title", help="Job title")
    add_cmd.add_argument("--linkedin", help="LinkedIn profile URL")

    # list-campaigns
    subparsers.add_parser("list-campaigns", help="List all campaigns")

    # list-leads
    ll_cmd = subparsers.add_parser("list-leads", help="List leads in a campaign")
    ll_cmd.add_argument("--campaign-id", required=True, help="Lemlist campaign ID")

    # update-lead
    ul_cmd = subparsers.add_parser("update-lead", help="Update a lead's fields")
    ul_cmd.add_argument("--email", required=True, help="Email of lead to update")
    ul_cmd.add_argument("--company", help="New company name")
    ul_cmd.add_argument("--first-name", help="New first name")
    ul_cmd.add_argument("--last-name", help="New last name")
    ul_cmd.add_argument("--title", help="New job title")

    # delete-lead
    dl_cmd = subparsers.add_parser("delete-lead", help="Delete a lead from a campaign")
    dl_cmd.add_argument("--campaign-id", required=True, help="Lemlist campaign ID")
    dl_cmd.add_argument("--email", required=True, help="Email of lead to delete")

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

    elif args.command == "list-leads":
        result = list_leads(api_key, args.campaign_id)
        print(json.dumps(result, indent=2))

    elif args.command == "update-lead":
        updates = {}
        if args.company:
            updates["companyName"] = args.company
        if args.first_name:
            updates["firstName"] = args.first_name
        if args.last_name:
            updates["lastName"] = args.last_name
        if args.title:
            updates["jobTitle"] = args.title
        if not updates:
            print("ERROR: No fields to update. Provide at least one of --company, --first-name, --last-name, --title", file=sys.stderr)
            sys.exit(1)
        result = update_lead(api_key, args.email, updates)
        print(json.dumps(result, indent=2))

    elif args.command == "delete-lead":
        result = delete_lead(api_key, args.campaign_id, args.email)
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
