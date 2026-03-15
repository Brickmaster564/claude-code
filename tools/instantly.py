#!/usr/bin/env python3
"""
Instantly.ai campaign tools.

Usage:
    python3 tools/instantly.py list-campaigns --search "campaign name"
    python3 tools/instantly.py add-leads --campaign-id "ID" --leads '[{"email":"...","first_name":"...","company_name":"..."}]'
    python3 tools/instantly.py list-leads --campaign-id "ID" --status "completed" --limit 500

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
    if body is not None:
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


def list_leads(api_key, campaign_id, status=None, limit=100):
    """List leads from a campaign, optionally filtered by status.

    Uses POST /leads/list with campaign_id filter.
    Paginates automatically to collect all matching leads.

    Both campaign and status filtering are done client-side because the
    Instantly v2 API ignores server-side filter params. Supported status values:
      - "completed": status == 3 and email_reply_count == 0
      - "replied": email_reply_count > 0
      - "bounced": status == -1
    """
    all_leads = []
    starting_after = None

    while True:
        payload = {
            "campaign": campaign_id,
            "limit": 100,
        }
        if starting_after:
            payload["starting_after"] = starting_after

        result = api_request(api_key, "POST", "/leads/list", data=payload)

        if "error" in result:
            return {"error": result["error"], "leads_collected": len(all_leads), "leads": all_leads}

        items = result if isinstance(result, list) else result.get("items", result.get("data", []))
        if not items:
            break

        for lead in items:
            lead_status_code = lead.get("status", 0)
            reply_count = lead.get("email_reply_count", 0)

            # Client-side status filtering
            if status == "completed" and not (lead_status_code == 3 and reply_count == 0):
                continue
            elif status == "replied" and reply_count == 0:
                continue
            elif status == "bounced" and lead_status_code != -1:
                continue

            all_leads.append({
                "email": lead.get("email", ""),
                "first_name": lead.get("first_name", ""),
                "last_name": lead.get("last_name", ""),
                "company_name": lead.get("company_name", ""),
                "lead_status": "replied" if reply_count > 0 else ("completed" if lead_status_code == 3 else ("bounced" if lead_status_code == -1 else str(lead_status_code))),
                "email_reply_count": reply_count,
                "id": lead.get("id", ""),
            })

            if len(all_leads) >= limit:
                break

        if len(all_leads) >= limit:
            break

        # Pagination
        next_after = result.get("next_starting_after")
        if not next_after:
            last = items[-1] if items else None
            next_after = last.get("id") if last else None
        if not next_after or next_after == starting_after:
            break
        starting_after = next_after

    return {
        "campaign_id": campaign_id,
        "status_filter": status or "all",
        "total": len(all_leads),
        "leads": all_leads,
    }


def delete_leads(api_key, campaign_id, emails):
    """Delete leads from a campaign by email.

    Finds lead IDs by listing campaign leads and matching emails,
    then deletes each via DELETE /leads/{id}.
    """
    email_set = {e.lower() for e in emails}
    matched = []
    starting_after = None

    # Find lead IDs by scanning campaign
    while email_set:
        payload = {"campaign": campaign_id, "limit": 100}
        if starting_after:
            payload["starting_after"] = starting_after
        result = api_request(api_key, "POST", "/leads/list", data=payload)
        if "error" in result:
            return {"error": result["error"], "deleted": matched}
        items = result if isinstance(result, list) else result.get("items", result.get("data", []))
        if not items:
            break
        for lead in items:
            if lead.get("email", "").lower() in email_set:
                matched.append({"id": lead["id"], "email": lead["email"]})
                email_set.discard(lead["email"].lower())
        next_after = result.get("next_starting_after")
        if not next_after:
            last = items[-1] if items else None
            next_after = last.get("id") if last else None
        if not next_after or next_after == starting_after:
            break
        starting_after = next_after

    # Delete each matched lead
    deleted = []
    failed = []
    for m in matched:
        res = api_request(api_key, "DELETE", f"/leads/{m['id']}")
        if "error" in res:
            failed.append({"email": m["email"], "error": res["error"]})
        else:
            deleted.append(m["email"])

    return {
        "deleted": deleted,
        "failed": failed,
        "not_found": list(email_set),
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

    # list-leads
    ll_cmd = subparsers.add_parser("list-leads", help="List leads from a campaign")
    ll_cmd.add_argument("--campaign-id", required=True, help="Instantly campaign ID")
    ll_cmd.add_argument("--status", help="Filter by lead status (e.g. completed, replied)")
    ll_cmd.add_argument("--limit", type=int, default=1000, help="Max leads to return (default 1000)")

    # delete-leads
    del_cmd = subparsers.add_parser("delete-leads", help="Delete leads from a campaign")
    del_cmd.add_argument("--campaign-id", required=True, help="Instantly campaign ID")
    del_cmd.add_argument("--emails", required=True, help="Comma-separated list of emails to delete")

    args = parser.parse_args()
    api_key = load_api_key()

    if args.command == "list-campaigns":
        result = list_campaigns(api_key, search=args.search)
        print(json.dumps(result, indent=2))

    elif args.command == "add-leads":
        leads = json.loads(args.leads)
        result = add_leads(api_key, args.campaign_id, leads)
        print(json.dumps(result, indent=2))

    elif args.command == "list-leads":
        result = list_leads(api_key, args.campaign_id, status=args.status, limit=args.limit)
        print(json.dumps(result, indent=2))

    elif args.command == "delete-leads":
        emails = [e.strip() for e in args.emails.split(",")]
        result = delete_leads(api_key, args.campaign_id, emails)
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
