#!/usr/bin/env python3
"""
Client agenda orchestrator.
Handles the full polling workflow for client agenda sessions.
Usage:
    python3 tools/agenda_orchestrator.py poll-reply --channel C08P14TTBA7 --thread-ts 1234.5678 --after-ts 1234.5678 --timeout 540
    python3 tools/agenda_orchestrator.py call-claude --prompt "..." --system "..."
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
SLACK_API = "https://slack.com/api"
ANTHROPIC_API = "https://api.anthropic.com/v1/messages"
BOT_USER_ID = "U0AJT4W0BNJ"


def load_keys():
    with open(CONFIG_DIR / "api-keys.json") as f:
        return json.load(f)


def slack_request(endpoint, data=None, method="POST"):
    keys = load_keys()
    token = keys["slack_nalu"]
    url = f"{SLACK_API}/{endpoint}"
    if method == "GET" and data:
        params = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in data.items())
        url = f"{url}?{params}"
        body = None
    else:
        body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def read_thread(channel, thread_ts):
    """Read all replies in a thread. Returns list of messages."""
    result = slack_request(
        "conversations.replies",
        {"channel": channel, "ts": thread_ts},
        method="GET"
    )
    if not result.get("ok"):
        print(f"ERROR reading thread: {result.get('error')}", file=sys.stderr)
        return []
    return result.get("messages", [])


def poll_for_reply(channel, thread_ts, after_ts, timeout_seconds=540):
    """
    Poll the thread every 60 seconds until a non-bot message appears after after_ts.
    Returns the message text, or None on timeout.
    """
    deadline = time.time() + timeout_seconds
    print(f"Polling for Scott's reply (timeout: {timeout_seconds}s)...", flush=True)
    while time.time() < deadline:
        time.sleep(60)
        messages = read_thread(channel, thread_ts)
        for msg in messages:
            msg_ts = float(msg.get("ts", "0"))
            if msg_ts > float(after_ts) and msg.get("user") != BOT_USER_ID:
                print(f"Scott replied: {msg.get('text', '')[:100]}", flush=True)
                return msg.get("text", "")
        remaining = int(deadline - time.time())
        print(f"  No reply yet. {remaining}s remaining...", flush=True)
    return None


def call_claude(system_prompt, user_prompt, model="claude-haiku-4-5-20251001"):
    """Call Anthropic API directly via urllib."""
    keys = load_keys()
    api_key = keys["anthropic"]
    payload = {
        "model": model,
        "max_tokens": 2000,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}]
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(ANTHROPIC_API, data=body, method="POST")
    req.add_header("x-api-key", api_key)
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
            return result["content"][0]["text"]
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"Claude API error: {err}", file=sys.stderr)
        return None


def main():
    import urllib.parse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # poll-reply subcommand
    p_poll = subparsers.add_parser("poll-reply")
    p_poll.add_argument("--channel", required=True)
    p_poll.add_argument("--thread-ts", required=True)
    p_poll.add_argument("--after-ts", required=True, help="Only return messages after this ts")
    p_poll.add_argument("--timeout", type=int, default=540)

    # call-claude subcommand
    p_claude = subparsers.add_parser("call-claude")
    p_claude.add_argument("--system", required=True)
    p_claude.add_argument("--prompt", required=True)
    p_claude.add_argument("--model", default="claude-haiku-4-5-20251001")

    args = parser.parse_args()

    if args.command == "poll-reply":
        reply = poll_for_reply(args.channel, args.thread_ts, args.after_ts, args.timeout)
        if reply is None:
            print("TIMEOUT: No reply received within timeout period.")
            sys.exit(1)
        else:
            print(f"REPLY: {reply}")

    elif args.command == "call-claude":
        result = call_claude(args.system, args.prompt, args.model)
        if result is None:
            print("ERROR: Claude API call failed.")
            sys.exit(1)
        else:
            print(result)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
