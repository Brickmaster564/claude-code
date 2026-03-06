#!/usr/bin/env python3
"""
Slack Socket Mode listener for guest-pipeline triggers.

Listens for messages containing "guest-pipeline" in #guest-research-and-comms
and spawns Claude CLI to handle the request.

Usage:
    python3 tools/slack-listener.py

Runs as a persistent process (LaunchAgent). Zero cost when idle.
"""

import json
import os
import subprocess
import sys
import logging
from pathlib import Path

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/tmp/slack-listener.log"),
    ],
)
log = logging.getLogger(__name__)

# Paths
WORKDIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = WORKDIR / "config" / "api-keys.json"

# Load tokens
with open(CONFIG_FILE) as f:
    keys = json.load(f)

BOT_TOKEN = keys["slack_nalu"]
APP_TOKEN = keys.get("slack_nalu_app_token", "")

if not APP_TOKEN or not APP_TOKEN.startswith("xapp-"):
    log.error("Missing or invalid slack_nalu_app_token in config/api-keys.json")
    log.error("Add your App-Level Token (xapp-...) to config/api-keys.json as 'slack_nalu_app_token'")
    sys.exit(1)

# Channel we listen on
TRIGGER_CHANNEL = "C089HSD8US1"  # #guest-research-and-comms
BOT_USER_ID = "U0AJT4W0BNJ"  # Nalu helper bot

# Initialize app
app = App(token=BOT_TOKEN)


@app.event("message")
def handle_message(event, say):
    """Handle messages in channels the bot is in."""
    # Ignore bot messages (prevent loops)
    if event.get("bot_id") or event.get("subtype"):
        return

    # Only listen in #guest-research-and-comms
    channel = event.get("channel", "")
    if channel != TRIGGER_CHANNEL:
        return

    text = event.get("text", "").strip()
    if not text:
        return

    # Fuzzy match for guest-pipeline trigger
    import re
    normalized = text.lower().replace(" ", "").replace("_", "").replace("-", "")
    if not re.search(r"guest\s*[-_]?\s*pipe\s*l+\s*i+\s*n+\s*e", text.lower()) and "guestpipeline" not in normalized:
        return

    user = event.get("user", "unknown")
    thread_ts = event.get("ts", "")
    log.info(f"Guest pipeline triggered by user {user}: {text}")

    # Acknowledge in thread
    say(
        text=f"On it. Running guest pipeline now...",
        thread_ts=thread_ts,
    )

    # Build the Claude CLI prompt
    prompt = (
        f'Run /guest-pipeline with this Slack request: "{text}". '
        f"Follow the skill instructions exactly. Write all qualified candidates "
        f"to Airtable and send the Slack summary to #guest-research-and-comms."
    )

    # Spawn Claude CLI in background
    log_dir = Path("/tmp/claude-guest-pipeline-slack")
    log_dir.mkdir(exist_ok=True)

    from datetime import datetime
    log_file = log_dir / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"

    cmd = [
        "/Users/jasper/.local/bin/claude",
        "--print",
        "--dangerously-skip-permissions",
        prompt,
    ]

    log.info(f"Spawning Claude CLI, logging to {log_file}")

    try:
        with open(log_file, "w") as lf:
            lf.write(f"Triggered by: {user}\n")
            lf.write(f"Message: {text}\n")
            lf.write(f"---\n")
            lf.flush()

            process = subprocess.Popen(
                cmd,
                cwd=str(WORKDIR),
                stdout=lf,
                stderr=subprocess.STDOUT,
            )

        log.info(f"Claude CLI spawned with PID {process.pid}")

    except Exception as e:
        log.error(f"Failed to spawn Claude CLI: {e}")
        say(
            text=f"Failed to start guest pipeline: {e}",
            thread_ts=thread_ts,
        )


if __name__ == "__main__":
    log.info("Starting Slack Socket Mode listener...")
    log.info(f"Watching #{TRIGGER_CHANNEL} for 'guest-pipeline' triggers")
    handler = SocketModeHandler(app, APP_TOKEN)
    handler.start()
