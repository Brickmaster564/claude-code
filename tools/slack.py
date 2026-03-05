#!/usr/bin/env python3
"""
Slack tool for Nalu workspace (direct API, not MCP).

Usage:
    python3 tools/slack.py send --channel "#nalu-hub" --text "Hello from Nalu Bot"
    python3 tools/slack.py send --channel "C01ABC123" --text "Message here"
    python3 tools/slack.py list-channels
    python3 tools/slack.py find-channel --name "nalu-hub"

Uses the Nalu bot token from config/api-keys.json (slack_nalu).
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
SLACK_API = "https://slack.com/api"


def load_token():
    with open(CONFIG_DIR / "api-keys.json") as f:
        keys = json.load(f)
    token = keys.get("slack_nalu")
    if not token:
        print("ERROR: slack_nalu token not found in config/api-keys.json", file=sys.stderr)
        sys.exit(1)
    return token


def slack_request(method, endpoint, data=None):
    """Make an authenticated Slack API request."""
    token = load_token()
    url = f"{SLACK_API}/{endpoint}"

    if method == "GET" and data:
        params = "&".join(f"{k}={v}" for k, v in data.items())
        url = f"{url}?{params}"
        body = None
    else:
        body = json.dumps(data).encode() if data else None

    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json; charset=utf-8")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {"ok": False, "error": f"HTTP {e.code}: {e.reason}", "detail": error_body}

    if not result.get("ok"):
        print(f"Slack API error: {result.get('error', 'unknown')}", file=sys.stderr)

    return result


def send_message(channel, text):
    """Send a message to a Slack channel. Channel can be an ID or #name."""
    # If channel starts with #, resolve it to an ID first
    if channel.startswith("#"):
        channel_name = channel[1:]
        found = find_channel(channel_name)
        if not found:
            return {"ok": False, "error": f"Channel '{channel_name}' not found"}
        channel = found["id"]

    return slack_request("POST", "chat.postMessage", {
        "channel": channel,
        "text": text
    })


def list_channels():
    """List all channels (public and private) the bot can see."""
    all_channels = []
    cursor = None

    while True:
        params = {"types": "public_channel,private_channel", "limit": "200"}
        if cursor:
            params["cursor"] = cursor

        result = slack_request("GET", "conversations.list", params)
        if not result.get("ok"):
            return result

        all_channels.extend(result.get("channels", []))

        cursor = result.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    return {"ok": True, "channels": all_channels}


def find_channel(name):
    """Find a channel by name. Returns channel dict or None."""
    result = list_channels()
    if not result.get("ok"):
        return None

    for ch in result.get("channels", []):
        if ch["name"] == name:
            return ch
    return None


def main():
    parser = argparse.ArgumentParser(description="Slack tool (Nalu workspace)")
    subparsers = parser.add_subparsers(dest="command")

    # send
    send_cmd = subparsers.add_parser("send", help="Send a message to a channel")
    send_cmd.add_argument("--channel", required=True, help="Channel ID or #name")
    send_cmd.add_argument("--text", required=True, help="Message text")

    # list-channels
    subparsers.add_parser("list-channels", help="List all channels")

    # find-channel
    find_cmd = subparsers.add_parser("find-channel", help="Find a channel by name")
    find_cmd.add_argument("--name", required=True, help="Channel name (without #)")

    args = parser.parse_args()

    if args.command == "send":
        result = send_message(args.channel, args.text)
        print(json.dumps(result, indent=2))
    elif args.command == "list-channels":
        result = list_channels()
        if result.get("ok"):
            for ch in result["channels"]:
                print(f"  {ch['id']}  #{ch['name']}")
            print(f"\n{len(result['channels'])} channels found")
        else:
            print(json.dumps(result, indent=2))
    elif args.command == "find-channel":
        ch = find_channel(args.name)
        if ch:
            print(json.dumps(ch, indent=2))
        else:
            print(f"Channel '{args.name}' not found")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    if args.command == "send" and isinstance(result, dict) and not result.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()
