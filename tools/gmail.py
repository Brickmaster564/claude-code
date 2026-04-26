#!/usr/bin/env python3
"""
Gmail send tool using Google OAuth credentials.

Usage:
    python3 tools/gmail.py send --to "recipient@example.com" --subject "Subject" --body "Email body"
    python3 tools/gmail.py send --to "recipient@example.com" --subject "Subject" --html-file path/to/email.html
    python3 tools/gmail.py send --to "recipient@example.com" --subject "Subject" --body "Report" --attachment report.pdf
    python3 tools/gmail.py --account nalu send --to "recipient@example.com" --subject "Subject" --body "Hello"
    python3 tools/gmail.py reply --thread-search "from:bob subject:meeting" --body "Sounds good!"
    python3 tools/gmail.py reply --thread-id 18f3a2b1c9d0e4f5 --body "Thanks!"

Accounts: cn (hello@clientnetwork.io, default), nalu.
Supports plain text (--body / --body-file) or HTML (--html-file) emails.
Supports file attachments via --attachment.
Supports threaded replies via the 'reply' subcommand.
"""

import argparse
import base64
import json
import sys
import urllib.request
import urllib.error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
GMAIL_API = "https://gmail.googleapis.com/gmail/v1/users/me"

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
    """Refresh the OAuth access token using the refresh token."""
    data = {
        "client_id": token_data["client_id"],
        "client_secret": token_data["client_secret"],
        "refresh_token": token_data["refresh_token"],
        "grant_type": "refresh_token"
    }
    body = "&".join(f"{k}={v}" for k, v in data.items()).encode()
    req = urllib.request.Request(
        token_data["token_uri"],
        data=body,
        method="POST"
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())

    token_data["token"] = result["access_token"]
    save_token(token_data)
    return token_data["token"]


def _get_access_token():
    """Get a valid access token, refreshing if needed."""
    token_data = load_token()
    return token_data["token"], token_data


def gmail_request(access_token, method, endpoint, data=None):
    """Make an authenticated Gmail API request."""
    url = f"{GMAIL_API}{endpoint}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "detail": error_body}


def gmail_get(access_token, endpoint):
    """Make an authenticated GET request to Gmail API."""
    url = f"{GMAIL_API}{endpoint}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {access_token}")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "detail": error_body}


def _api_get_with_refresh(endpoint):
    """Make a Gmail API GET call, refreshing the token once on 401."""
    token_data = load_token()
    access_token = token_data["token"]
    result = gmail_get(access_token, endpoint)
    if isinstance(result, dict) and "error" in result and "401" in str(result.get("error", "")):
        print("Access token expired, refreshing...", file=sys.stderr)
        access_token = refresh_access_token(token_data)
        result = gmail_get(access_token, endpoint)
    return result


def _build_message(to, subject, body_text, content_type="plain", cc=None, attachment_path=None,
                    in_reply_to=None, references=None):
    """Build a MIME message and return the base64url-encoded raw string."""
    if attachment_path:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body_text, content_type, "utf-8"))
        file_path = Path(attachment_path)
        with open(file_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=file_path.name)
        part["Content-Disposition"] = f'attachment; filename="{file_path.name}"'
        msg.attach(part)
    else:
        msg = MIMEText(body_text, content_type, "utf-8")
    msg["to"] = to
    msg["subject"] = subject
    if cc:
        msg["cc"] = cc
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
    if references:
        msg["References"] = references
    return base64.urlsafe_b64encode(msg.as_bytes()).decode()


def _api_call_with_refresh(endpoint, payload, method="POST"):
    """Make a Gmail API call, refreshing the token once on 401."""
    token_data = load_token()
    access_token = token_data["token"]
    result = gmail_request(access_token, method, endpoint, payload)
    if isinstance(result, dict) and "error" in result and "401" in str(result.get("error", "")):
        print("Access token expired, refreshing...", file=sys.stderr)
        access_token = refresh_access_token(token_data)
        result = gmail_request(access_token, method, endpoint, payload)
    return result


def send_email(to, subject, body_text, content_type="plain", cc=None, attachment=None,
               thread_id=None, in_reply_to=None, references=None):
    """Send an email via Gmail API. content_type can be 'plain' or 'html'."""
    raw = _build_message(to, subject, body_text, content_type, cc, attachment_path=attachment,
                         in_reply_to=in_reply_to, references=references)
    payload = {"raw": raw}
    if thread_id:
        payload["threadId"] = thread_id
    return _api_call_with_refresh("/messages/send", payload)


def create_draft(to, subject, body_text, content_type="plain", cc=None, attachment=None,
                 thread_id=None, in_reply_to=None, references=None):
    """Create a draft email via Gmail API."""
    raw = _build_message(to, subject, body_text, content_type, cc, attachment_path=attachment,
                         in_reply_to=in_reply_to, references=references)
    payload = {"message": {"raw": raw}}
    if thread_id:
        payload["message"]["threadId"] = thread_id
    return _api_call_with_refresh("/drafts", payload)


def search_threads(query, max_results=5):
    """Search for threads matching a Gmail query. Returns list of thread objects."""
    q_encoded = urllib.request.quote(query)
    result = _api_get_with_refresh(f"/threads?q={q_encoded}&maxResults={max_results}")
    if isinstance(result, dict) and "error" in result:
        return result
    return result.get("threads", [])


def get_thread(thread_id):
    """Get a thread by ID, including message metadata."""
    return _api_get_with_refresh(f"/threads/{thread_id}?format=metadata")


def get_message(message_id):
    """Get a message by ID with metadata."""
    return _api_get_with_refresh(f"/messages/{message_id}?format=metadata")


def _extract_header(headers, name):
    """Extract a header value from a list of Gmail header objects."""
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return None


def find_thread_for_reply(query):
    """Find a thread and extract the info needed to reply to it.
    Returns (thread_id, message_id_header, subject, to_address) or raises."""
    threads = search_threads(query, max_results=1)
    if isinstance(threads, dict) and "error" in threads:
        print(f"ERROR: Search failed: {threads}", file=sys.stderr)
        sys.exit(1)
    if not threads:
        print(f"ERROR: No threads found matching: {query}", file=sys.stderr)
        sys.exit(1)

    thread_id = threads[0]["id"]
    thread = get_thread(thread_id)
    if isinstance(thread, dict) and "error" in thread:
        print(f"ERROR: Could not fetch thread: {thread}", file=sys.stderr)
        sys.exit(1)

    messages = thread.get("messages", [])
    if not messages:
        print("ERROR: Thread has no messages", file=sys.stderr)
        sys.exit(1)

    # Get the last message in the thread to reply to
    last_msg = messages[-1]
    headers = last_msg.get("payload", {}).get("headers", [])

    message_id_header = _extract_header(headers, "Message-ID") or _extract_header(headers, "Message-Id")
    subject = _extract_header(headers, "Subject") or ""
    from_addr = _extract_header(headers, "From") or ""
    to_addr = _extract_header(headers, "To") or ""

    # Build references chain
    existing_refs = _extract_header(headers, "References") or ""
    if message_id_header:
        references = f"{existing_refs} {message_id_header}".strip() if existing_refs else message_id_header
    else:
        references = existing_refs

    # Ensure subject has Re: prefix
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"

    # Print thread context for visibility
    print(f"Thread: {thread_id}", file=sys.stderr)
    print(f"Replying to last message from: {from_addr}", file=sys.stderr)
    print(f"Subject: {subject}", file=sys.stderr)
    print(f"Messages in thread: {len(messages)}", file=sys.stderr)

    return {
        "thread_id": thread_id,
        "message_id": message_id_header,
        "references": references,
        "subject": subject,
        "from": from_addr,
        "to": to_addr,
    }


def reply_to_thread(query=None, thread_id=None, to=None, body_text="", content_type="plain",
                    cc=None, attachment=None, as_draft=False):
    """Reply to an existing thread, found by search query or thread ID.

    If as_draft=True, creates a threaded draft instead of sending.
    """
    if query:
        info = find_thread_for_reply(query)
    elif thread_id:
        thread = get_thread(thread_id)
        if isinstance(thread, dict) and "error" in thread:
            print(f"ERROR: Could not fetch thread: {thread}", file=sys.stderr)
            sys.exit(1)
        messages = thread.get("messages", [])
        if not messages:
            print("ERROR: Thread has no messages", file=sys.stderr)
            sys.exit(1)
        last_msg = messages[-1]
        headers = last_msg.get("payload", {}).get("headers", [])
        message_id_header = _extract_header(headers, "Message-ID") or _extract_header(headers, "Message-Id")
        subject = _extract_header(headers, "Subject") or ""
        from_addr = _extract_header(headers, "From") or ""
        existing_refs = _extract_header(headers, "References") or ""
        if message_id_header:
            references = f"{existing_refs} {message_id_header}".strip() if existing_refs else message_id_header
        else:
            references = existing_refs
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"
        info = {
            "thread_id": thread_id,
            "message_id": message_id_header,
            "references": references,
            "subject": subject,
            "from": from_addr,
            "to": _extract_header(headers, "To") or "",
        }
        print(f"Thread: {thread_id}", file=sys.stderr)
        print(f"Replying to last message from: {from_addr}", file=sys.stderr)
        print(f"Subject: {subject}", file=sys.stderr)
        print(f"Messages in thread: {len(messages)}", file=sys.stderr)
    else:
        print("ERROR: Must provide --thread-search or --thread-id", file=sys.stderr)
        sys.exit(1)

    # Default reply-to is the sender of the last message, unless --to overrides
    reply_to = to or info["from"]

    send_fn = create_draft if as_draft else send_email
    return send_fn(
        to=reply_to,
        subject=info["subject"],
        body_text=body_text,
        content_type=content_type,
        cc=cc,
        attachment=attachment,
        thread_id=info["thread_id"],
        in_reply_to=info["message_id"],
        references=info["references"],
    )


def main():
    parser = argparse.ArgumentParser(description="Gmail send tool")
    subparsers = parser.add_subparsers(dest="command")

    parser.add_argument("--account", default="cn", choices=list(ACCOUNTS.keys()),
                        help="Google account to use (default: cn)")

    # Shared email arguments for send and create-draft
    for cmd_name, cmd_help in [("send", "Send an email"), ("create-draft", "Create an email draft")]:
        cmd = subparsers.add_parser(cmd_name, help=cmd_help)
        cmd.add_argument("--to", required=True, help="Recipient email address(es), comma-separated")
        cmd.add_argument("--subject", required=True, help="Email subject line")
        cmd.add_argument("--body", help="Email body text (plain text)")
        cmd.add_argument("--body-file", help="Path to file containing plain text body")
        cmd.add_argument("--html-file", help="Path to file containing HTML body")
        cmd.add_argument("--cc", help="CC email address(es), comma-separated")
        cmd.add_argument("--attachment", help="Path to file to attach")

    # Reply subcommand
    reply_cmd = subparsers.add_parser("reply", help="Reply to an existing email thread")
    reply_cmd.add_argument("--thread-search", help="Gmail search query to find the thread (uses most recent match)")
    reply_cmd.add_argument("--thread-id", help="Gmail thread ID to reply to directly")
    reply_cmd.add_argument("--to", help="Override recipient (default: replies to sender of last message)")
    reply_cmd.add_argument("--body", help="Reply body text (plain text)")
    reply_cmd.add_argument("--body-file", help="Path to file containing plain text body")
    reply_cmd.add_argument("--html-file", help="Path to file containing HTML body")
    reply_cmd.add_argument("--cc", help="CC email address(es), comma-separated")
    reply_cmd.add_argument("--attachment", help="Path to file to attach")
    reply_cmd.add_argument("--as-draft", action="store_true",
                           help="Create a threaded draft instead of sending")

    # Search subcommand
    search_cmd = subparsers.add_parser("search", help="Search for email threads")
    search_cmd.add_argument("--query", required=True, help="Gmail search query")
    search_cmd.add_argument("--max-results", type=int, default=5, help="Max threads to return (default: 5)")

    args = parser.parse_args()

    set_account(args.account)

    if args.command in ("send", "create-draft"):
        if args.html_file:
            body_text = Path(args.html_file).read_text()
            content_type = "html"
        elif args.body_file:
            body_text = Path(args.body_file).read_text()
            content_type = "plain"
        elif args.body:
            body_text = args.body
            content_type = "plain"
        else:
            print("ERROR: Must provide --body, --body-file, or --html-file", file=sys.stderr)
            sys.exit(1)

        attachment = getattr(args, "attachment", None)
        if attachment and not Path(attachment).exists():
            print(f"ERROR: Attachment file not found: {attachment}", file=sys.stderr)
            sys.exit(1)

        if args.command == "send":
            result = send_email(args.to, args.subject, body_text, content_type, cc=args.cc, attachment=attachment)
        else:
            result = create_draft(args.to, args.subject, body_text, content_type, cc=args.cc, attachment=attachment)

        print(json.dumps(result, indent=2))

        if isinstance(result, dict) and "error" in result:
            sys.exit(1)

    elif args.command == "reply":
        if args.html_file:
            body_text = Path(args.html_file).read_text()
            content_type = "html"
        elif args.body_file:
            body_text = Path(args.body_file).read_text()
            content_type = "plain"
        elif args.body:
            body_text = args.body
            content_type = "plain"
        else:
            print("ERROR: Must provide --body, --body-file, or --html-file", file=sys.stderr)
            sys.exit(1)

        attachment = getattr(args, "attachment", None)
        if attachment and not Path(attachment).exists():
            print(f"ERROR: Attachment file not found: {attachment}", file=sys.stderr)
            sys.exit(1)

        result = reply_to_thread(
            query=args.thread_search,
            thread_id=args.thread_id,
            to=args.to,
            body_text=body_text,
            content_type=content_type,
            cc=args.cc,
            attachment=attachment,
            as_draft=args.as_draft,
        )
        print(json.dumps(result, indent=2))

        if isinstance(result, dict) and "error" in result:
            sys.exit(1)

    elif args.command == "search":
        threads = search_threads(args.query, args.max_results)
        if isinstance(threads, dict) and "error" in threads:
            print(json.dumps(threads, indent=2))
            sys.exit(1)
        for t in threads:
            thread_detail = get_thread(t["id"])
            messages = thread_detail.get("messages", [])
            if messages:
                headers = messages[0].get("payload", {}).get("headers", [])
                subject = _extract_header(headers, "Subject") or "(no subject)"
                from_addr = _extract_header(headers, "From") or ""
                date = _extract_header(headers, "Date") or ""
                print(f"Thread: {t['id']}  |  Messages: {len(messages)}  |  {date}")
                print(f"  Subject: {subject}")
                print(f"  From: {from_addr}")
                print()
        print(f"Found {len(threads)} thread(s)")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
