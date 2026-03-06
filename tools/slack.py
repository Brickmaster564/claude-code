#!/usr/bin/env python3
"""
Slack tool for Nalu and Client Network workspaces (direct API, not MCP).

Usage:
    python3 tools/slack.py send --channel "#nalu-hub" --text "Hello"
    python3 tools/slack.py send --workspace cn --channel "#client-network-hub" --text "Hello"
    python3 tools/slack.py reply --channel "C08P14TTBA7" --thread-ts "1234.5678" --text "Reply here"
    python3 tools/slack.py read-thread --channel "C08P14TTBA7" --thread-ts "1234.5678"
    python3 tools/slack.py list-channels
    python3 tools/slack.py find-channel --name "nalu-hub"
    python3 tools/slack.py find-user --name "scott"

Defaults to Nalu workspace (slack_nalu). Use --workspace cn for Client Network (slack_cn).
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
SLACK_API = "https://slack.com/api"


WORKSPACE_KEYS = {
    "nalu": "slack_nalu",
    "cn": "slack_cn",
}

_active_workspace = "nalu"


def load_token():
    with open(CONFIG_DIR / "api-keys.json") as f:
        keys = json.load(f)
    key_name = WORKSPACE_KEYS[_active_workspace]
    token = keys.get(key_name)
    if not token:
        print(f"ERROR: {key_name} token not found in config/api-keys.json", file=sys.stderr)
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


def resolve_channel(channel):
    """Resolve a #name to a channel ID, or return the ID as-is."""
    if channel.startswith("#"):
        found = find_channel(channel[1:])
        if not found:
            return None
        return found["id"]
    return channel


def send_message(channel, text, thread_ts=None):
    """Send a message to a Slack channel, optionally in a thread."""
    channel_id = resolve_channel(channel)
    if not channel_id:
        return {"ok": False, "error": f"Channel '{channel}' not found"}

    payload = {"channel": channel_id, "text": text}
    if thread_ts:
        payload["thread_ts"] = thread_ts

    return slack_request("POST", "chat.postMessage", payload)


def read_thread(channel, thread_ts):
    """Read all replies in a thread."""
    channel_id = resolve_channel(channel)
    if not channel_id:
        return {"ok": False, "error": f"Channel '{channel}' not found"}

    result = slack_request("GET", "conversations.replies", {
        "channel": channel_id,
        "ts": thread_ts,
        "limit": "200"
    })
    return result


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


def find_user(name):
    """Find a user by name (partial match on real_name or display_name)."""
    result = slack_request("GET", "users.list")
    if not result.get("ok"):
        return result

    name_lower = name.lower()
    matches = []
    for m in result.get("members", []):
        if m.get("deleted") or m.get("is_bot") or m.get("id") == "USLACKBOT":
            continue
        real = m.get("real_name", "").lower()
        display = m.get("profile", {}).get("display_name", "").lower()
        username = m.get("name", "").lower()
        if name_lower in real or name_lower in display or name_lower in username:
            matches.append(m)

    return {"ok": True, "users": matches}


def main():
    parser = argparse.ArgumentParser(description="Slack tool (Nalu / CN workspace)")
    parser.add_argument("--workspace", choices=["nalu", "cn"], default="nalu",
                        help="Workspace to use: nalu (default) or cn (Client Network)")
    subparsers = parser.add_subparsers(dest="command")

    # send
    send_cmd = subparsers.add_parser("send", help="Send a message to a channel")
    send_cmd.add_argument("--channel", required=True, help="Channel ID or #name")
    send_cmd.add_argument("--text", required=True, help="Message text")

    # reply (send in a thread)
    reply_cmd = subparsers.add_parser("reply", help="Reply in a thread")
    reply_cmd.add_argument("--channel", required=True, help="Channel ID or #name")
    reply_cmd.add_argument("--thread-ts", required=True, help="Thread timestamp of parent message")
    reply_cmd.add_argument("--text", required=True, help="Reply text")

    # read-thread
    rt_cmd = subparsers.add_parser("read-thread", help="Read all replies in a thread")
    rt_cmd.add_argument("--channel", required=True, help="Channel ID or #name")
    rt_cmd.add_argument("--thread-ts", required=True, help="Thread timestamp of parent message")

    # list-channels
    subparsers.add_parser("list-channels", help="List all channels")

    # find-channel
    find_ch_cmd = subparsers.add_parser("find-channel", help="Find a channel by name")
    find_ch_cmd.add_argument("--name", required=True, help="Channel name (without #)")

    # find-user
    find_u_cmd = subparsers.add_parser("find-user", help="Find a user by name")
    find_u_cmd.add_argument("--name", required=True, help="Name to search for")

    args = parser.parse_args()
    global _active_workspace
    _active_workspace = args.workspace
    result = None

    if args.command == "send":
        result = send_message(args.channel, args.text)
        print(json.dumps(result, indent=2))
    elif args.command == "reply":
        result = send_message(args.channel, args.text, thread_ts=args.thread_ts)
        print(json.dumps(result, indent=2))
    elif args.command == "read-thread":
        result = read_thread(args.channel, args.thread_ts)
        if result.get("ok"):
            for msg in result.get("messages", []):
                user = msg.get("user", "bot")
                text = msg.get("text", "")
                ts = msg.get("ts", "")
                print(f"[{ts}] <{user}> {text}")
            print(f"\n{len(result.get('messages', []))} messages in thread")
        else:
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
    elif args.command == "find-user":
        result = find_user(args.name)
        if result.get("ok"):
            for u in result["users"]:
                print(f"  {u['id']}  {u.get('real_name', '?'):30s}  @{u.get('name', '?')}")
            if not result["users"]:
                print("No matching users found")
        else:
            print(json.dumps(result, indent=2))
    else:
        parser.print_help()
        sys.exit(1)

    if result and isinstance(result, dict) and not result.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()
