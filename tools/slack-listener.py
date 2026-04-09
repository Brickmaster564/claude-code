#!/usr/bin/env python3
"""
Slack Socket Mode listener for on-demand skill triggers.

Supported triggers:
  - "guest-pipeline" in #guest-research-and-comms -> runs /guest-pipeline
  - "client-agendas" in #nalu-hub -> runs /client-agendas
  - Thread reply to a notification with "EMAIL ID:" in #guest-research-and-comms -> runs /reply-router

Usage:
    python3 tools/slack-listener.py

Runs as a persistent process (LaunchAgent). Zero cost when idle.
Spawned tasks are fully detached and survive listener restarts.
"""

import json
import os
import re
import signal
import subprocess
import sys
import logging
import threading
import time
import urllib.request
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

# Max time a spawned skill can run before being considered stuck (30 minutes)
SKILL_TIMEOUT_SECS = 30 * 60

app = App(token=BOT_TOKEN)

# Track last event received for WebSocket health monitoring
_last_event_time = time.time()


@app.middleware
def update_heartbeat(body, next):
    """Update the heartbeat timestamp on EVERY incoming event (not just messages).

    Without this, the watchdog only sees message events. If no one posts for 15
    minutes the watchdog falsely kills the process. Slack Socket Mode sends
    various internal events (slash commands ack, interactive payloads, etc.)
    that pass through middleware, keeping the heartbeat alive.
    """
    global _last_event_time
    _last_event_time = time.time()
    event_type = body.get("event", {}).get("type", "?") if isinstance(body, dict) else "?"
    log.info(f"MIDDLEWARE: event_type={event_type} keys={list(body.keys()) if isinstance(body, dict) else 'n/a'}")
    next()


def _reap_and_watchdog():
    """Daemon thread: reap zombies, clean stale PIDs, and monitor WebSocket health.

    Runs every 60 seconds. Uses the Socket Mode client's is_connected() method
    to check WebSocket health instead of tracking event timestamps, since quiet
    channels can go hours without any application-level events.

    If the client reports disconnected for 3 consecutive checks (3 minutes),
    we force-exit so launchd can restart us. The SDK's auto-reconnect handles
    transient blips, so 3 consecutive failures means something is genuinely stuck.
    """
    disconnect_streak = 0
    DISCONNECT_THRESHOLD = 3  # consecutive checks before we force-exit

    while True:
        try:
            # 1. Reap zombie children
            while True:
                try:
                    pid, status = os.waitpid(-1, os.WNOHANG)
                    if pid == 0:
                        break
                    log.info(f"Reaped child PID {pid} (status {status})")
                except ChildProcessError:
                    break

            # 2. Clean stale PID files older than SKILL_TIMEOUT_SECS
            for pidfile in PIDFILE_DIR.glob("*.pid"):
                try:
                    age = time.time() - pidfile.stat().st_mtime
                    if age > SKILL_TIMEOUT_SECS:
                        pid = int(pidfile.read_text().strip())
                        skill = pidfile.stem
                        log.warning(
                            f"{skill} PID {pid} has been running for {int(age)}s "
                            f"(>{SKILL_TIMEOUT_SECS}s), killing and clearing"
                        )
                        try:
                            os.killpg(os.getpgid(pid), signal.SIGTERM)
                        except (OSError, ProcessLookupError):
                            pass
                        pidfile.unlink(missing_ok=True)
                except Exception as e:
                    log.error(f"Error cleaning PID file {pidfile}: {e}")

            # 3. WebSocket health check using actual connection state
            if _socket_handler and hasattr(_socket_handler, "client"):
                connected = _socket_handler.client.is_connected()
                if not connected:
                    disconnect_streak += 1
                    log.warning(
                        f"WebSocket not connected (streak: {disconnect_streak}/"
                        f"{DISCONNECT_THRESHOLD}). SDK auto-reconnect should handle this."
                    )
                    if disconnect_streak >= DISCONNECT_THRESHOLD:
                        log.error(
                            f"WebSocket disconnected for {disconnect_streak} consecutive "
                            f"checks. Auto-reconnect failed. Exiting so launchd can restart."
                        )
                        os._exit(1)
                else:
                    if disconnect_streak > 0:
                        log.info(f"WebSocket reconnected after {disconnect_streak} check(s)")
                    disconnect_streak = 0

        except Exception as e:
            log.error(f"Reaper/watchdog thread error: {e}")

        time.sleep(60)


# Handler reference for the watchdog (set in __main__)
_socket_handler = None

# Start the reaper as a daemon thread (watchdog waits for _socket_handler to be set)
_watchdog_thread = threading.Thread(target=_reap_and_watchdog, daemon=True)
_watchdog_thread.start()


def _is_skill_active(skill_name):
    """Check if a skill is already running via PID file (survives listener restarts).

    Detects zombie processes (state Z/defunct) as inactive, since they represent
    finished processes whose parent hasn't reaped them yet.
    """
    pidfile = PIDFILE_DIR / f"{skill_name}.pid"
    if not pidfile.exists():
        return False
    try:
        pid = int(pidfile.read_text().strip())
        os.kill(pid, 0)
        # Process exists, but check if it's a zombie
        try:
            result = subprocess.run(
                ["ps", "-p", str(pid), "-o", "state="],
                capture_output=True, text=True, timeout=5,
            )
            state = result.stdout.strip()
            if state.startswith("Z"):
                log.warning(f"{skill_name} PID {pid} is a zombie, clearing")
                pidfile.unlink(missing_ok=True)
                return False
        except Exception:
            pass
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


def get_parent_message(channel, thread_ts):
    """Fetch the parent message of a thread to check if it's a notification."""
    token = keys["slack_nalu"]
    url = (
        f"https://slack.com/api/conversations.replies"
        f"?channel={channel}&ts={thread_ts}&limit=1&inclusive=true"
    )
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        if data.get("ok") and data.get("messages"):
            return data["messages"][0]
    except Exception as e:
        log.error(f"Failed to fetch parent message: {e}")
    return None


def extract_email_id(text):
    """Extract an Instantly email UUID from a notification message."""
    match = re.search(r"EMAIL ID:\s*([0-9a-f-]{36})", text, re.IGNORECASE)
    return match.group(1) if match else None


@app.event("message")
def handle_message(event, say):
    try:
        _handle_message_inner(event, say)
    except Exception as e:
        log.error(f"Unhandled error in message handler: {e}", exc_info=True)


def _handle_message_inner(event, say):
    log.info(f"EVENT RECEIVED: channel={event.get('channel')} user={event.get('user')} "
             f"bot_id={event.get('bot_id')} subtype={event.get('subtype')} "
             f"thread_ts={event.get('thread_ts')} text={event.get('text', '')[:80]}")
    if event.get("bot_id") or event.get("subtype"):
        return

    channel = event.get("channel", "")
    text = event.get("text", "").strip()
    thread_ts = event.get("thread_ts")
    if not text:
        return

    # Reply-router: thread reply to a notification in #guest-research-and-comms
    if channel == GUEST_PIPELINE_CHANNEL and thread_ts:
        parent = get_parent_message(channel, thread_ts)
        if parent:
            email_id = extract_email_id(parent.get("text", ""))
            if email_id:
                parent_text = parent.get("text", "")
                prompt = (
                    f'Run /reply-router. A team member replied to an Instantly email notification.\n\n'
                    f'SLACK CHANNEL: {channel}\n'
                    f'SLACK THREAD TS: {thread_ts}\n'
                    f'INSTANTLY EMAIL ID: {email_id}\n\n'
                    f'ORIGINAL NOTIFICATION:\n{parent_text}\n\n'
                    f'TEAM MEMBER\'S NOTES:\n{text}\n\n'
                    f'Follow the /reply-router skill instructions exactly. '
                    f'Draft the reply, send it via Instantly, and post confirmation back to this Slack thread.'
                )
                spawn_claude("reply-router", prompt, event, say)
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
    log.info("Watching #guest-research-and-comms for reply-router thread replies")
    log.info("Watching #nalu-hub for 'client-agendas' triggers")
    handler = SocketModeHandler(app, APP_TOKEN)

    # Give the watchdog thread access to the handler's connection state
    _socket_handler = handler

    # Register a raw message listener so the heartbeat updates on ALL WebSocket
    # frames (hello, disconnect, envelopes), not just Bolt-level message events
    def _raw_heartbeat(client, message, raw_message):
        global _last_event_time
        _last_event_time = time.time()
        msg_type = message.get("type", "unknown") if isinstance(message, dict) else "non-dict"
        log.info(f"RAW WS frame: type={msg_type}")

    handler.client.message_listeners.append(_raw_heartbeat)

    handler.start()
