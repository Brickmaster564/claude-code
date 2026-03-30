#!/usr/bin/env python3
"""
Instantly.ai campaign tools.

Usage:
    python3 tools/instantly.py get-campaign --campaign-id "ID"
    python3 tools/instantly.py list-campaigns --search "campaign name"
    python3 tools/instantly.py create-campaign --name "Campaign Name" --emails "sender@domain.com"
    python3 tools/instantly.py create-campaign --name "Campaign Name" --emails "sender@domain.com" --sequence-file sequence.json
    python3 tools/instantly.py set-sequence --campaign-id "ID" --sequence-file sequence.json
    python3 tools/instantly.py add-leads --campaign-id "ID" --leads '[{"email":"...","first_name":"...","company_name":"..."}]'
    python3 tools/instantly.py list-leads --campaign-id "ID" --status "completed" --limit 500
    python3 tools/instantly.py get-email --id "EMAIL_UUID"
    python3 tools/instantly.py list-emails --email-type received --campaign-id "ID" --limit 20
    python3 tools/instantly.py send-reply --reply-to "EMAIL_UUID" --eaccount "sender@domain.com" --subject "Re: Subject" --body "Reply text"

Sequence JSON format (array of steps):
    [
        {
            "subject": "Subject line with {{firstName}}",
            "body": "HTML body of email",
            "delay": 0,
            "delay_unit": "days",
            "variants": [
                {"subject": "Alt subject", "body": "Alt body"}
            ]
        }
    ]

    Each step requires "subject" and "body" for the primary variant.
    "delay" is the wait before this step (0 for first email, default 3 days).
    "delay_unit" can be "minutes", "hours", or "days" (default "days").
    Optional "variants" array adds A/B test variants to the step.

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


def api_request(api_key, method, endpoint, data=None, params=None, timeout=30):
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
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "detail": error_body}
    except Exception as e:
        return {"error": str(e)}


def _build_schedule(timezone="America/New_York", start_hour="09:00", end_hour="17:00",
                     weekdays_only=True, start_date=None, end_date=None):
    """Build a campaign_schedule object with sensible defaults."""
    days = {}
    for d in range(7):
        if weekdays_only:
            days[str(d)] = d not in (0, 6)  # 0=Sun, 6=Sat
        else:
            days[str(d)] = True

    schedule = {
        "schedules": [
            {
                "name": "Default Schedule",
                "timing": {"from": start_hour, "to": end_hour},
                "days": days,
                "timezone": timezone,
            }
        ]
    }
    if start_date:
        schedule["start_date"] = start_date
    if end_date:
        schedule["end_date"] = end_date
    return schedule


def _parse_sequence_file(filepath):
    """Parse a sequence JSON file into the Instantly sequences format.

    Accepts an array of step objects. Each step has:
        subject (str): Subject line (required)
        body (str): HTML body (required)
        delay (int): Wait before this step in delay_unit (default: 0 for first, 3 for rest)
        delay_unit (str): "minutes", "hours", or "days" (default: "days")
        variants (list): Optional additional A/B variants, each with subject + body
    """
    with open(filepath) as f:
        steps_raw = json.load(f)

    if not isinstance(steps_raw, list) or len(steps_raw) == 0:
        print("ERROR: Sequence file must contain a non-empty JSON array of steps", file=sys.stderr)
        sys.exit(1)

    steps = []
    for i, step in enumerate(steps_raw):
        if "subject" not in step or "body" not in step:
            print(f"ERROR: Step {i + 1} missing required 'subject' or 'body' field", file=sys.stderr)
            sys.exit(1)

        delay = step.get("delay", 0 if i == 0 else 3)
        delay_unit = step.get("delay_unit", "days")

        variants = [{"subject": step["subject"], "body": step["body"]}]
        for v in step.get("variants", []):
            if "subject" not in v or "body" not in v:
                print(f"ERROR: Variant in step {i + 1} missing 'subject' or 'body'", file=sys.stderr)
                sys.exit(1)
            variants.append({"subject": v["subject"], "body": v["body"]})

        steps.append({
            "type": "email",
            "delay": delay,
            "delay_unit": delay_unit,
            "variants": variants,
        })

    return [{"steps": steps}]


def create_campaign(api_key, name, email_list, sequence_file=None, daily_limit=50,
                    timezone="America/New_York", start_hour="09:00", end_hour="17:00",
                    weekdays_only=True, start_date=None, end_date=None,
                    stop_on_reply=True, link_tracking=True, open_tracking=True,
                    email_gap=5, random_wait_max=10):
    """Create a new campaign via POST /campaigns."""
    payload = {
        "name": name,
        "campaign_schedule": _build_schedule(
            timezone=timezone, start_hour=start_hour, end_hour=end_hour,
            weekdays_only=weekdays_only, start_date=start_date, end_date=end_date,
        ),
        "email_list": email_list if isinstance(email_list, list) else [email_list],
        "daily_limit": daily_limit,
        "stop_on_reply": stop_on_reply,
        "link_tracking": link_tracking,
        "open_tracking": open_tracking,
        "email_gap": email_gap,
        "random_wait_max": random_wait_max,
    }

    if sequence_file:
        payload["sequences"] = _parse_sequence_file(sequence_file)

    result = api_request(api_key, "POST", "/campaigns", data=payload)
    if "error" in result:
        return result

    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "status": result.get("status"),
        "email_list": result.get("email_list"),
        "daily_limit": result.get("daily_limit"),
        "steps_count": len(result.get("sequences", [{}])[0].get("steps", [])) if result.get("sequences") else 0,
        "timestamp_created": result.get("timestamp_created"),
    }


def set_sequence(api_key, campaign_id, sequence_file):
    """Update sequences on an existing campaign via PATCH /campaigns/{id}."""
    sequences = _parse_sequence_file(sequence_file)
    payload = {"sequences": sequences}
    result = api_request(api_key, "PATCH", f"/campaigns/{campaign_id}", data=payload)
    if "error" in result:
        return result

    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "steps_count": len(result.get("sequences", [{}])[0].get("steps", [])) if result.get("sequences") else 0,
        "updated": True,
    }


def get_campaign(api_key, campaign_id):
    """Get a single campaign by ID via GET /campaigns/{id}. Includes sequences."""
    result = api_request(api_key, "GET", f"/campaigns/{campaign_id}")
    return result


def list_campaigns(api_key, search=None):
    params = {"limit": "100"}
    if search:
        params["search"] = search
    result = api_request(api_key, "GET", "/campaigns", params=params)
    return result


def add_leads(api_key, campaign_id, leads):
    """Add leads to a campaign via POST /leads/add (batch endpoint).

    Automatically splits into chunks of 100 to avoid API timeouts on large
    payloads. Each chunk uses a 120s timeout and retries once on failure.
    """
    CHUNK_SIZE = 100
    totals = {
        "leads_uploaded": 0,
        "duplicated_leads": 0,
        "skipped_count": 0,
        "invalid_email_count": 0,
        "in_blocklist": 0,
        "remaining_in_plan": None,
        "errors": [],
    }

    for i in range(0, len(leads), CHUNK_SIZE):
        chunk = leads[i : i + CHUNK_SIZE]
        payload = {
            "campaign_id": campaign_id,
            "skip_if_in_campaign": True,
            "leads": chunk,
        }

        result = None
        for attempt in range(2):
            result = api_request(api_key, "POST", "/leads/add", data=payload, timeout=120)
            if "error" not in result:
                break
            if attempt == 0:
                time.sleep(3)

        if "error" in result:
            totals["errors"].append({"chunk": i // CHUNK_SIZE + 1, "error": result["error"]})
            continue

        totals["leads_uploaded"] += result.get("leads_uploaded", 0)
        totals["duplicated_leads"] += result.get("duplicated_leads", 0)
        totals["skipped_count"] += result.get("skipped_count", 0)
        totals["invalid_email_count"] += result.get("invalid_email_count", 0)
        totals["in_blocklist"] += result.get("in_blocklist", 0)
        totals["remaining_in_plan"] = result.get("remaining_in_plan")

        if i + CHUNK_SIZE < len(leads):
            time.sleep(2)

    output = {
        "campaign_id": campaign_id,
        "total_sent": len(leads),
        "leads_uploaded": totals["leads_uploaded"],
        "duplicated_leads": totals["duplicated_leads"],
        "skipped_count": totals["skipped_count"],
        "invalid_email_count": totals["invalid_email_count"],
        "in_blocklist": totals["in_blocklist"],
        "remaining_in_plan": totals["remaining_in_plan"],
    }
    if totals["errors"]:
        output["chunk_errors"] = totals["errors"]
    return output


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


def update_lead(api_key, lead_id, updates):
    """Update a lead's fields via PATCH /leads/{id}.

    `updates` is a dict of fields to change (e.g. {"company_name": "New Name"}).
    """
    result = api_request(api_key, "PATCH", f"/leads/{lead_id}", data=updates, timeout=30)
    return result


def get_email(api_key, email_id):
    """Get a single email by ID via GET /emails/{id}."""
    result = api_request(api_key, "GET", f"/emails/{email_id}")
    if "error" in result:
        return result
    return {
        "id": result.get("id", ""),
        "subject": result.get("subject", ""),
        "from_address_email": result.get("from_address_email", ""),
        "to_address_email_list": result.get("to_address_email_list", ""),
        "cc_address_email_list": result.get("cc_address_email_list", ""),
        "body": result.get("body", {}),
        "eaccount": result.get("eaccount", ""),
        "campaign_id": result.get("campaign_id", ""),
        "lead": result.get("lead", ""),
        "ue_type": result.get("ue_type", 0),
        "is_unread": result.get("is_unread", 0),
        "thread_id": result.get("thread_id", ""),
        "timestamp_email": result.get("timestamp_email", ""),
        "timestamp_created": result.get("timestamp_created", ""),
    }


def list_emails(api_key, email_type=None, campaign_id=None, is_unread=None,
                eaccount=None, lead=None, limit=20, min_timestamp=None):
    """List emails via GET /emails with optional filters.

    Rate limited to 20 requests per minute.
    email_type: "received", "sent", or "manual"
    """
    params = {"limit": str(min(limit, 100))}
    if email_type:
        params["email_type"] = email_type
    if campaign_id:
        params["campaign_id"] = campaign_id
    if is_unread is not None:
        params["is_unread"] = str(is_unread).lower()
    if eaccount:
        params["eaccount"] = eaccount
    if lead:
        params["lead"] = lead
    if min_timestamp:
        params["min_timestamp_created"] = min_timestamp

    all_emails = []
    starting_after = None

    while True:
        if starting_after:
            params["starting_after"] = starting_after

        result = api_request(api_key, "GET", "/emails", params=params)
        if "error" in result:
            return {"error": result["error"], "emails": all_emails}

        items = result.get("items", [])
        if not items:
            break

        for email in items:
            all_emails.append({
                "id": email.get("id", ""),
                "subject": email.get("subject", ""),
                "from_address_email": email.get("from_address_email", ""),
                "to_address_email_list": email.get("to_address_email_list", ""),
                "body_text": (email.get("body") or {}).get("text", ""),
                "eaccount": email.get("eaccount", ""),
                "lead": email.get("lead", ""),
                "campaign_id": email.get("campaign_id", ""),
                "is_unread": email.get("is_unread", 0),
                "thread_id": email.get("thread_id", ""),
                "timestamp_email": email.get("timestamp_email", ""),
            })

            if len(all_emails) >= limit:
                break

        if len(all_emails) >= limit:
            break

        next_after = result.get("next_starting_after")
        if not next_after:
            break
        starting_after = next_after

    return {"total": len(all_emails), "emails": all_emails}


def send_reply(api_key, reply_to_uuid, eaccount, subject, body_text, body_html=None, cc=None):
    """Reply to an email via POST /emails/reply.

    reply_to_uuid: ID of the email being replied to
    eaccount: the sending email account (must be connected to workspace)
    subject: subject line (typically "Re: ...")
    body_text: plain text body
    body_html: optional HTML body (defaults to wrapping body_text in <p> tags)
    cc: comma-separated CC email addresses for reply-all
    """
    if not body_html:
        body_html = body_text.replace("\n", "<br>\n")

    payload = {
        "eaccount": eaccount,
        "reply_to_uuid": reply_to_uuid,
        "subject": subject,
        "body": {
            "html": body_html,
            "text": body_text,
        },
    }

    if cc:
        cc_list = [addr.strip() for addr in cc.split(",") if addr.strip()]
        if cc_list:
            payload["cc"] = cc_list

    result = api_request(api_key, "POST", "/emails/reply", data=payload)
    if "error" in result:
        return result

    return {
        "sent": True,
        "id": result.get("id", ""),
        "reply_to": reply_to_uuid,
        "eaccount": eaccount,
        "subject": subject,
        "cc": cc or "",
    }


def main():
    parser = argparse.ArgumentParser(description="Instantly.ai campaign tools")
    subparsers = parser.add_subparsers(dest="command")

    # create-campaign
    cc_cmd = subparsers.add_parser("create-campaign", help="Create a new campaign")
    cc_cmd.add_argument("--name", required=True, help="Campaign name")
    cc_cmd.add_argument("--emails", required=True, help="Comma-separated sender email addresses")
    cc_cmd.add_argument("--sequence-file", help="Path to sequence JSON file")
    cc_cmd.add_argument("--daily-limit", type=int, default=50, help="Daily send limit (default 50)")
    cc_cmd.add_argument("--timezone", default="America/New_York", help="Schedule timezone (default America/New_York)")
    cc_cmd.add_argument("--start-hour", default="09:00", help="Send window start (default 09:00)")
    cc_cmd.add_argument("--end-hour", default="17:00", help="Send window end (default 17:00)")
    cc_cmd.add_argument("--include-weekends", action="store_true", help="Include weekends in schedule")
    cc_cmd.add_argument("--start-date", help="Campaign start date (YYYY-MM-DD)")
    cc_cmd.add_argument("--end-date", help="Campaign end date (YYYY-MM-DD)")
    cc_cmd.add_argument("--no-link-tracking", action="store_true", help="Disable link tracking")
    cc_cmd.add_argument("--no-open-tracking", action="store_true", help="Disable open tracking")
    cc_cmd.add_argument("--email-gap", type=int, default=5, help="Minutes between emails (default 5)")

    # get-campaign
    gc_cmd = subparsers.add_parser("get-campaign", help="Get campaign details including sequences")
    gc_cmd.add_argument("--campaign-id", required=True, help="Instantly campaign ID")

    # set-sequence
    ss_cmd = subparsers.add_parser("set-sequence", help="Set/update email sequence on a campaign")
    ss_cmd.add_argument("--campaign-id", required=True, help="Instantly campaign ID")
    ss_cmd.add_argument("--sequence-file", required=True, help="Path to sequence JSON file")

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

    # get-email
    ge_cmd = subparsers.add_parser("get-email", help="Get a single email by ID")
    ge_cmd.add_argument("--id", required=True, help="Email UUID")

    # list-emails
    le_cmd = subparsers.add_parser("list-emails", help="List emails (rate limit: 20/min)")
    le_cmd.add_argument("--email-type", choices=["received", "sent", "manual"], help="Filter by type")
    le_cmd.add_argument("--campaign-id", help="Filter by campaign ID")
    le_cmd.add_argument("--is-unread", action="store_true", help="Only unread emails")
    le_cmd.add_argument("--eaccount", help="Filter by sending account email")
    le_cmd.add_argument("--lead", help="Filter by lead email address")
    le_cmd.add_argument("--limit", type=int, default=20, help="Max emails to return (default 20)")
    le_cmd.add_argument("--since", help="Only emails after this ISO datetime")

    # send-reply
    sr_cmd = subparsers.add_parser("send-reply", help="Reply to an email")
    sr_cmd.add_argument("--reply-to", required=True, help="UUID of the email to reply to")
    sr_cmd.add_argument("--eaccount", required=True, help="Sending email account")
    sr_cmd.add_argument("--subject", required=True, help="Reply subject line")
    sr_cmd.add_argument("--body", required=True, help="Plain text reply body")
    sr_cmd.add_argument("--body-html", help="Optional HTML reply body")
    sr_cmd.add_argument("--cc", help="Comma-separated CC email addresses for reply-all")

    args = parser.parse_args()
    api_key = load_api_key()

    if args.command == "create-campaign":
        email_list = [e.strip() for e in args.emails.split(",")]
        result = create_campaign(
            api_key, name=args.name, email_list=email_list,
            sequence_file=args.sequence_file, daily_limit=args.daily_limit,
            timezone=args.timezone, start_hour=args.start_hour, end_hour=args.end_hour,
            weekdays_only=not args.include_weekends,
            start_date=args.start_date, end_date=args.end_date,
            link_tracking=not args.no_link_tracking,
            open_tracking=not args.no_open_tracking,
            email_gap=args.email_gap,
        )
        print(json.dumps(result, indent=2))

    elif args.command == "get-campaign":
        result = get_campaign(api_key, args.campaign_id)
        print(json.dumps(result, indent=2))

    elif args.command == "set-sequence":
        result = set_sequence(api_key, args.campaign_id, args.sequence_file)
        print(json.dumps(result, indent=2))

    elif args.command == "list-campaigns":
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

    elif args.command == "get-email":
        result = get_email(api_key, args.id)
        print(json.dumps(result, indent=2))

    elif args.command == "list-emails":
        result = list_emails(
            api_key, email_type=args.email_type, campaign_id=args.campaign_id,
            is_unread=True if args.is_unread else None, eaccount=args.eaccount,
            lead=args.lead, limit=args.limit, min_timestamp=args.since,
        )
        print(json.dumps(result, indent=2))

    elif args.command == "send-reply":
        result = send_reply(
            api_key, reply_to_uuid=args.reply_to, eaccount=args.eaccount,
            subject=args.subject, body_text=args.body, body_html=args.body_html,
            cc=args.cc,
        )
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
