#!/usr/bin/env python3
"""
Google Calendar tool using Google OAuth credentials.

Usage:
    python3 tools/gcal.py --account nalu create-event \
        --title "Guest Pipeline FTT" \
        --start "2026-03-16T10:00:00" \
        --end "2026-03-16T10:30:00" \
        --timezone "Europe/London" \
        --recurrence "RRULE:FREQ=WEEKLY;BYDAY=MO,TH" \
        --description "Automated guest research pipeline for FTT"

    python3 tools/gcal.py --account nalu list-events --max 10

Accounts: cn (default), nalu.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
CALENDAR_API = "https://www.googleapis.com/calendar/v3"

ACCOUNTS = {
    "cn": {"token": "google-token.json"},
    "nalu": {"token": "google-token-nalu.json"},
}

_active_token_path = CONFIG_DIR / "google-token.json"


def set_account(name):
    global _active_token_path
    account = ACCOUNTS.get(name)
    if not account:
        print(f"ERROR: Unknown account '{name}'. Available: {', '.join(ACCOUNTS.keys())}", file=sys.stderr)
        sys.exit(1)
    _active_token_path = CONFIG_DIR / account["token"]


def load_token():
    with open(_active_token_path) as f:
        return json.load(f)


def save_token(token_data):
    with open(_active_token_path, "w") as f:
        json.dump(token_data, f, indent=2)


def refresh_access_token(token_data):
    data = {
        "client_id": token_data["client_id"],
        "client_secret": token_data["client_secret"],
        "refresh_token": token_data["refresh_token"],
        "grant_type": "refresh_token",
    }
    body = "&".join(f"{k}={v}" for k, v in data.items()).encode()
    req = urllib.request.Request(token_data["token_uri"], data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
    token_data["token"] = result["access_token"]
    save_token(token_data)
    return token_data["token"]


def api_request(access_token, method, endpoint, data=None, token_data=None):
    url = f"{CALENDAR_API}{endpoint}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 401 and token_data:
            new_token = refresh_access_token(token_data)
            return api_request(new_token, method, endpoint, data, token_data=None)
        error_body = e.read().decode() if e.fp else ""
        print(f"ERROR: HTTP {e.code}: {e.reason}\n{error_body}", file=sys.stderr)
        sys.exit(1)


def create_event(args):
    token_data = load_token()
    access_token = token_data["token"]

    event = {
        "summary": args.title,
        "start": {"dateTime": args.start, "timeZone": args.timezone},
        "end": {"dateTime": args.end, "timeZone": args.timezone},
    }
    if args.description:
        event["description"] = args.description
    if args.recurrence:
        event["recurrence"] = [args.recurrence]
    if args.color_id:
        event["colorId"] = args.color_id

    result = api_request(access_token, "POST", "/calendars/primary/events", event, token_data)
    print(json.dumps(result, indent=2))
    return result


def list_events(args):
    token_data = load_token()
    access_token = token_data["token"]
    endpoint = f"/calendars/primary/events?maxResults={args.max}&orderBy=startTime&singleEvents=true&timeMin=2026-03-15T00:00:00Z"
    result = api_request(access_token, "GET", endpoint, token_data=token_data)
    for item in result.get("items", []):
        start = item.get("start", {}).get("dateTime", item.get("start", {}).get("date", "?"))
        print(f"  {start}  {item.get('summary', '(no title)')}")
    return result


def delete_event(args):
    token_data = load_token()
    access_token = token_data["token"]
    endpoint = f"/calendars/primary/events/{args.event_id}"
    url = f"{CALENDAR_API}{endpoint}"
    req = urllib.request.Request(url, method="DELETE")
    req.add_header("Authorization", f"Bearer {access_token}")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp.read()
        print(f"Deleted event {args.event_id}")
    except urllib.error.HTTPError as e:
        if e.code == 401 and token_data:
            new_token = refresh_access_token(token_data)
            req2 = urllib.request.Request(url, method="DELETE")
            req2.add_header("Authorization", f"Bearer {new_token}")
            with urllib.request.urlopen(req2, timeout=30) as resp:
                resp.read()
            print(f"Deleted event {args.event_id}")
            return
        error_body = e.read().decode() if e.fp else ""
        print(f"ERROR: HTTP {e.code}: {e.reason}\n{error_body}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Google Calendar tool")
    parser.add_argument("--account", default="cn", choices=ACCOUNTS.keys())
    sub = parser.add_subparsers(dest="command")

    p_create = sub.add_parser("create-event")
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--start", required=True)
    p_create.add_argument("--end", required=True)
    p_create.add_argument("--timezone", default="Europe/London")
    p_create.add_argument("--description", default="")
    p_create.add_argument("--recurrence", default="")
    p_create.add_argument("--color-id", default="")

    p_list = sub.add_parser("list-events")
    p_list.add_argument("--max", type=int, default=10)

    p_delete = sub.add_parser("delete-event")
    p_delete.add_argument("--event-id", required=True)

    args = parser.parse_args()
    set_account(args.account)

    if args.command == "create-event":
        create_event(args)
    elif args.command == "list-events":
        list_events(args)
    elif args.command == "delete-event":
        delete_event(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
