#!/usr/bin/env python3
"""
Slack Socket Mode listener for on-demand skill triggers.

Supported triggers:
  - "guest-pipeline" in #guest-research-and-comms → runs /guest-pipeline
  - "client-agendas" in #nalu-hub → runs /client-agendas

Usage:
    python3 tools/slack-listener.py

Runs as a persistent process (LaunchAgent). Zero cost when idle.
"""

import json
import os
import re
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

# Channels we listen on
GUEST_PIPELINE_CHANNEL = "C089HSD8US1"  # #guest-research-and-comms
NALU_HUB_CHANNEL = "C08P14TTBA7"  # #nalu-hub
BOT_USER_ID = "U0AJT4W0BNJ"  # Nalu helper bot

# Initialize app
app = App(token=BOT_TOKEN)


def spawn_claude(skill_name, prompt, event, say):
    """Acknowledge in Slack and spawn Claude CLI for a skill."""
    user = event.get("user", "unknown")
    thread_ts = event.get("ts", "")
    text = event.get("text", "").strip()

    log.info(f"{skill_name} triggered by user {user}: {text}")

    say(
        text=f"On it. Running {skill_name} now...",
        thread_ts=thread_ts,
    )

    log_dir = Path(f"/tmp/claude-{skill_name}-slack")
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

        lf = open(log_file, "a")
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
            text=f"Failed to start {skill_name}: {e}",
            thread_ts=thread_ts,
        )



def is_guest_pipeline_trigger(text):
    normalized = text.lower().replace(" ", "").replace("_", "").replace("-", "")
    return bool(
        re.search(r"guest\s*[-_]?\s*pipe\s*l+\s*i+\s*n+\s*e", text.lower())
        or "guestpipeline" in normalized
    )


def is_client_agendas_trigger(text):
    normalized = text.lower().replace(" ", "").replace("_", "").replace("-", "")
    return bool(
        re.search(r"client\s*[-_]?\s*agenda", text.lower())
        or "clientagenda" in normalized
        or re.search(r"run\s+(all\s+)?agendas?", text.lower())
    )


@app.event("message")
def handle_message(event, say):
    """Handle messages in channels the bot is in."""
    if event.get("bot_id") or event.get("subtype"):
        return

    channel = event.get("channel", "")
    text = event.get("text", "").strip()
    if not text:
        return

    # Guest pipeline trigger in #guest-research-and-comms
    if channel == GUEST_PIPELINE_CHANNEL and is_guest_pipeline_trigger(text):
        prompt = (
            f'Run /guest-pipeline with this Slack request: "{text}". '
            f"Follow the skill instructions exactly. Post progress updates to "
            f"#guest-research-and-comms as described in the Progress Updates section "
            f"of the skill. Write all qualified candidates to Airtable and send the "
            f"final Slack summary to #guest-research-and-comms."
        )
        spawn_claude("guest-pipeline", prompt, event, say)

    # Client agendas trigger in #nalu-hub
    elif channel == NALU_HUB_CHANNEL and is_client_agendas_trigger(text):
        prompt = (
            f'Run /client-agendas with this Slack request: "{text}". '
            f"Follow the skill instructions exactly."
        )
        spawn_claude("client-agendas", prompt, event, say)


if __name__ == "__main__":
    log.info("Starting Slack Socket Mode listener...")
    log.info(f"Watching #guest-research-and-comms for 'guest-pipeline' triggers")
    log.info(f"Watching #nalu-hub for 'client-agendas' triggers")
    handler = SocketModeHandler(app, APP_TOKEN)
    handler.start()
