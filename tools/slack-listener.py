#!/usr/bin/env python3
"""
Slack Socket Mode listener for on-demand skill triggers.

Supported triggers:
  - "guest-pipeline" in #guest-research-and-comms -> runs /guest-pipeline
  - "client-agendas" in #nalu-hub -> runs /client-agendas

Usage:
    python3 tools/slack-listener.py

Runs as a persistent process (LaunchAgent). Zero cost when idle.
Spawned tasks are fully detached and survive listener restarts.
"""

import json
import os
import re
import subprocess
import sys
import logging
from datetime import datetime
from pathlib import Path

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from logging.handlers import RotatingFileHandler

# Setup logging with rotation (5 MB max, 3 backups)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler("/tmp/slack-listener.log", maxBytes=5*1024*1024, backupCount=3),
    ],
)
log = logging.getLogger(__name__)

# Paths
WORKDIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = WORKDIR / "config" / "api-keys.json"
SPAWN_SCRIPT = WORKDIR / "tools" / "slack-spawn.sh"

# PID files for duplicate guard (survives listener restarts)
PIDFILE_DIR = Path("/tmp/slack-listener-pids")
PIDFILE_DIR.mkdir(exist_ok=True)

# Clean PATH for spawned processes
SPAWN_ENV_PATH = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/Users/jasper/.local/bin"

# Load tokens
with open(CONFIG_FILE) as f:
    keys = json.load(f)

BOT_TOKEN = keys["slack_nalu"]
APP_TOKEN = keys.get("slack_nalu_app_token", "")

if not APP_TOKEN or not APP_TOKEN.startswith("xapp-"):
    log.error("Missing or invalid slack_nalu_app_token in config/api-keys.json")
    sys.exit(1)

# Channels
GUEST_PIPELINE_CHANNEL = "C089HSD8US1"  # #guest-research-and-comms
NALU_HUB_CHANNEL = "C08P14TTBA7"  # #nalu-hub

app = App(token=BOT_TOKEN)


def _is_skill_active(skill_name):
    """Check if a skill is already running via PID file (survives listener restarts)."""
    pidfile = PIDFILE_DIR / f"{skill_name}.pid"
    if not pidfile.exists():
        return False
    try:
        pid = int(pidfile.read_text().strip())
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        pidfile.unlink(missing_ok=True)
        return False


def spawn_claude(skill_name, prompt, event, say):
    """Acknowledge in Slack and spawn a fully self-contained Claude process."""
    user = event.get("user", "unknown")
    thread_ts = event.get("ts", "")
    channel = event.get("channel", "")
    text = event.get("text", "").strip()

    if _is_skill_active(skill_name):
        log.warning(f"{skill_name} already running, ignoring duplicate trigger from {user}")
        say(text=f"{skill_name} is already running. Wait for it to finish.", thread_ts=thread_ts)
        return

    log.info(f"{skill_name} triggered by user {user}: {text}")
    say(text=f"On it. Running {skill_name} now...", thread_ts=thread_ts)

    log_dir = Path(f"/tmp/claude-{skill_name}-slack")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"

    with open(log_file, "w") as lf:
        lf.write(f"Triggered by: {user}\nMessage: {text}\n---\n")

    spawn_env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    spawn_env["PATH"] = SPAWN_ENV_PATH
    spawn_env["HOME"] = "/Users/jasper"

    try:
        process = subprocess.Popen(
            [str(SPAWN_SCRIPT), skill_name, channel, thread_ts, str(log_file), prompt],
            env=spawn_env,
            start_new_session=True,
        )
        (PIDFILE_DIR / f"{skill_name}.pid").write_text(str(process.pid))
        log.info(f"slack-spawn.sh launched with PID {process.pid}")
    except Exception as e:
        log.error(f"Failed to spawn: {e}")
        say(text=f"Failed to start {skill_name}: {e}", thread_ts=thread_ts)


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
    if event.get("bot_id") or event.get("subtype"):
        return

    channel = event.get("channel", "")
    text = event.get("text", "").strip()
    if not text:
        return

    if channel == GUEST_PIPELINE_CHANNEL and is_guest_pipeline_trigger(text):
        prompt = (
            f'Run /guest-pipeline with this Slack request: "{text}". '
            f"Follow the skill instructions exactly. Post progress updates to "
            f"#guest-research-and-comms as described in the Progress Updates section "
            f"of the skill. Write all qualified candidates to Airtable and send the "
            f"final Slack summary to #guest-research-and-comms."
        )
        spawn_claude("guest-pipeline", prompt, event, say)

    elif channel == NALU_HUB_CHANNEL and is_client_agendas_trigger(text):
        prompt = (
            f'Run /client-agendas with this Slack request: "{text}". '
            f"Follow the skill instructions exactly. Poll the Slack thread "
            f"for Scott's replies - wait 60 seconds between polls. "
            f"Process Dom first, then Jeremy unless a specific client is requested."
        )
        spawn_claude("client-agendas", prompt, event, say)


if __name__ == "__main__":
    log.info("Starting Slack Socket Mode listener...")
    log.info("Watching #guest-research-and-comms for 'guest-pipeline' triggers")
    log.info("Watching #nalu-hub for 'client-agendas' triggers")
    handler = SocketModeHandler(app, APP_TOKEN)
    handler.start()
