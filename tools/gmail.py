#!/usr/bin/env python3
"""
Gmail send tool using Google OAuth credentials.

Usage:
    python3 tools/gmail.py send --to "recipient@example.com" --subject "Subject" --body "Email body"
    python3 tools/gmail.py send --to "recipient@example.com" --subject "Subject" --html-file path/to/email.html
    python3 tools/gmail.py send --to "recipient@example.com" --subject "Subject" --body "Report" --attachment report.pdf
    python3 tools/gmail.py --account nalu send --to "recipient@example.com" --subject "Subject" --body "Hello"

Accounts: cn (hello@clientnetwork.io, default), nalu.
Supports plain text (--body / --body-file) or HTML (--html-file) emails.
Supports file attachments via --attachment.
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


def _build_message(to, subject, body_text, content_type="plain", cc=None, attachment_path=None):
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


def send_email(to, subject, body_text, content_type="plain", cc=None, attachment=None):
    """Send an email via Gmail API. content_type can be 'plain' or 'html'."""
    raw = _build_message(to, subject, body_text, content_type, cc, attachment_path=attachment)
    return _api_call_with_refresh("/messages/send", {"raw": raw})


def create_draft(to, subject, body_text, content_type="plain", cc=None, attachment=None):
    """Create a draft email via Gmail API."""
    raw = _build_message(to, subject, body_text, content_type, cc, attachment_path=attachment)
    return _api_call_with_refresh("/drafts", {"message": {"raw": raw}})


def main():
    parser = argparse.ArgumentParser(description="Gmail send tool")
    subparsers = parser.add_subparsers(dest="command")

    parser.add_argument("--account", default="cn", choices=list(ACCOUNTS.keys()),
                        help="Google account to use (default: cn)")

    # Shared email arguments
    for cmd_name, cmd_help in [("send", "Send an email"), ("create-draft", "Create an email draft")]:
        cmd = subparsers.add_parser(cmd_name, help=cmd_help)
        cmd.add_argument("--to", required=True, help="Recipient email address(es), comma-separated")
        cmd.add_argument("--subject", required=True, help="Email subject line")
        cmd.add_argument("--body", help="Email body text (plain text)")
        cmd.add_argument("--body-file", help="Path to file containing plain text body")
        cmd.add_argument("--html-file", help="Path to file containing HTML body")
        cmd.add_argument("--cc", help="CC email address(es), comma-separated")
        cmd.add_argument("--attachment", help="Path to file to attach")

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
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
