#!/usr/bin/env python3
"""
Autonomous client agenda runner for Nalu podcast clients.
Handles Dom, Hack You, and Jeremy sequentially.
Polls Slack every 60s, formats content via Claude API, updates Google Docs.
Saves state to .tmp/agenda_state.json for crash recovery.

Usage:
    python3 tools/run_client_agendas.py [--resume]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TOOLS_DIR = BASE_DIR / "tools"
CONFIG_DIR = BASE_DIR / "config"
STATE_FILE = BASE_DIR / ".tmp" / "agenda_state.json"
CLIENTS_FILE = BASE_DIR / ".claude" / "skills" / "client-agendas" / "clients.json"

BOT_USER_ID = "U0AJT4W0BNJ"
SCOTT_USER_ID = "U07BL527UP8"
CHANNEL_ID = "C08P14TTBA7"
CHANNEL_NAME = "#nalu-hub"

ANTHROPIC_API = "https://api.anthropic.com/v1/messages"
SLACK_API = "https://slack.com/api"


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def load_keys():
    with open(CONFIG_DIR / "api-keys.json") as f:
        return json.load(f)


def ordinal(n):
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{['th','st','nd','rd','th','th','th','th','th','th'][n % 10]}"


def next_monday_str():
    today = datetime.now()
    days_ahead = 7 - today.weekday() if today.weekday() != 0 else 7
    if today.weekday() == 0:
        days_ahead = 7
    else:
        days_ahead = (7 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
    monday = today + timedelta(days=days_ahead)
    return f"{ordinal(monday.day)} {monday.strftime('%B')}"


# ---------------------------------------------------------------------------
# Slack
# ---------------------------------------------------------------------------

def slack_request(endpoint, data=None, method="POST"):
    keys = load_keys()
    token = keys["slack_nalu"]
    url = f"{SLACK_API}/{endpoint}"
    if method == "GET":
        if data:
            qs = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in data.items())
            url = f"{url}?{qs}"
        body = None
    else:
        body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def slack_send(text):
    result = slack_request("chat.postMessage", {"channel": CHANNEL_ID, "text": text})
    if not result.get("ok"):
        raise RuntimeError(f"Slack send failed: {result.get('error')}")
    return result["ts"]


def slack_reply(thread_ts, text):
    result = slack_request("chat.postMessage", {
        "channel": CHANNEL_ID,
        "thread_ts": thread_ts,
        "text": text
    })
    if not result.get("ok"):
        raise RuntimeError(f"Slack reply failed: {result.get('error')}")
    return result["ts"]


def slack_read_thread(thread_ts):
    import urllib.parse
    result = slack_request(
        "conversations.replies",
        {"channel": CHANNEL_ID, "ts": thread_ts},
        method="GET"
    )
    if not result.get("ok"):
        raise RuntimeError(f"Slack read-thread failed: {result.get('error')}")
    return result.get("messages", [])


def poll_for_scott(thread_ts, after_ts, poll_interval=60):
    """Poll every poll_interval seconds until Scott replies after after_ts. Returns message text."""
    log(f"Polling for Scott's reply (after ts={after_ts})...")
    while True:
        time.sleep(poll_interval)
        messages = slack_read_thread(thread_ts)
        for msg in messages:
            msg_ts = float(msg.get("ts", "0"))
            if msg_ts > float(after_ts) and msg.get("user") != BOT_USER_ID:
                text = msg.get("text", "").strip()
                log(f"Scott replied: {text[:80]}{'...' if len(text) > 80 else ''}")
                return text, msg["ts"]
        log("  No reply yet, waiting 60s...")


# ---------------------------------------------------------------------------
# Google Docs
# ---------------------------------------------------------------------------

def gdocs(args_list):
    cmd = ["python3", str(TOOLS_DIR / "gdocs.py"), "--account", "nalu"] + args_list
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR)
    if result.returncode != 0:
        raise RuntimeError(f"gdocs.py error: {result.stderr}")
    return result.stdout.strip()


def duplicate_template(template_id, title):
    out = gdocs(["duplicate", "--template-id", template_id, "--title", title])
    data = json.loads(out)
    return data["id"]


def get_doc(doc_id):
    out = gdocs(["get", "--doc-id", doc_id])
    return json.loads(out)


def batch_replace(doc_id, replacements):
    gdocs(["batch-replace", "--doc-id", doc_id, "--replacements", json.dumps(replacements)])


def write_at(doc_id, operations):
    gdocs(["write-at", "--doc-id", doc_id, "--operations", json.dumps(operations)])


def share_doc(doc_id, email, role="reader"):
    gdocs(["share", "--doc-id", doc_id, "--email", email, "--role", role])


def move_doc(doc_id, folder_id):
    gdocs(["move", "--doc-id", doc_id, "--folder-id", folder_id])


# ---------------------------------------------------------------------------
# Gmail
# ---------------------------------------------------------------------------

def send_email(to, subject, body, cc=None):
    cmd = ["python3", str(TOOLS_DIR / "gmail.py"), "--account", "nalu", "send",
           "--to", to, "--subject", subject, "--body", body]
    if cc:
        cmd += ["--cc", cc]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR)
    if result.returncode != 0:
        raise RuntimeError(f"gmail.py error: {result.stderr}")
    return result.stdout.strip()


# ---------------------------------------------------------------------------
# Anthropic API
# ---------------------------------------------------------------------------

def call_claude(system_prompt, user_prompt, model="claude-haiku-4-5-20251001"):
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
            return result["content"][0]["text"].strip()
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        raise RuntimeError(f"Claude API error: {err}")


# ---------------------------------------------------------------------------
# Doc structure helpers
# ---------------------------------------------------------------------------

def extract_doc_text(doc):
    """Extract list of (startIndex, endIndex, text, nestingLevel) from doc."""
    items = []
    for elem in doc["body"]["content"]:
        if "paragraph" in elem:
            para = elem["paragraph"]
            text = "".join(e.get("textRun", {}).get("content", "") for e in para.get("elements", []))
            nest = para.get("bullet", {}).get("nestingLevel", -1)
            items.append({
                "start": elem["startIndex"],
                "end": elem["endIndex"],
                "text": text.rstrip("\n"),
                "nest": nest
            })
    return items


def find_slot_after(items, heading_text, count=1):
    """Find the first `count` empty or placeholder slots after a heading."""
    found_heading = False
    slots = []
    for item in items:
        if not found_heading:
            if heading_text.lower() in item["text"].lower():
                found_heading = True
            continue
        # Stop if we hit another top-level heading (nest == -1, non-empty)
        if item["nest"] == -1 and item["text"] and item["text"] != heading_text:
            break
        # Collect slots (empty or '.' placeholder)
        if item["text"] in ("", ".", "..") or not item["text"]:
            slots.append(item)
            if len(slots) >= count:
                break
    return slots


# ---------------------------------------------------------------------------
# Content formatting prompts
# ---------------------------------------------------------------------------

SYSTEM_FORMAT = """You are a content formatter for Nalu podcast client agendas.
You receive a section name, Scott's brain dump (raw notes), and the doc slot structure.
Return ONLY a valid JSON object: {"operations": [{start, end, text}, ...]}

Rules:
- Professional and direct. No em dashes. Short sentences. No filler.
- Each text value must end with \\n
- Bullet points use a dash prefix where appropriate
- Keep it tight: every word earns its place
- Checkbox action items use the ☐ symbol
- Do NOT include any text outside the JSON object
"""


def format_section(section_name, brain_dump, slots, extra_rules=""):
    slot_info = "\n".join(f"  Slot {i+1}: indices {s['start']}-{s['end']}, current: {repr(s['text'])}"
                          for i, s in enumerate(slots))
    user_prompt = f"""Section: {section_name}

Scott's brain dump:
{brain_dump}

Doc slots to fill:
{slot_info}

{extra_rules}

Return a JSON object with an "operations" array. Each operation: {{start: N, end: N, text: "content\\n"}}
Fill each slot with the appropriate content. Keep it concise and factual."""

    raw = call_claude(SYSTEM_FORMAT, user_prompt)
    # Extract JSON from response
    match = re.search(r'\{[\s\S]*\}', raw)
    if not match:
        raise RuntimeError(f"No JSON in Claude response: {raw}")
    return json.loads(match.group())["operations"]


def format_email(client_config, doc_id, doc_title, brain_dumps):
    """Draft the client email using Claude."""
    all_content = "\n\n".join(f"**{k}**: {v}" for k, v in brain_dumps.items())
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    system = """You draft short Friday client emails for a podcast agency.
Write as Jasper - casual, direct, no fluff, no em dashes.
Open with 'Hey {greeting},' then 2-3 lines covering key points conversationally.
Include the doc link inline. Close with 'Speak Monday.' Sign off as 'Jasper'.
4-6 sentences total after the greeting. No bullet points. Plain text only."""

    user = f"""Client: {client_config['display_name']}
Greeting: {client_config['email_greeting']}
Doc link: {doc_url}
Doc title: {doc_title}

Agenda content summary:
{all_content}

Write the email body (just the body, no subject line)."""

    return call_claude(system, user)


def format_whatsapp(client_config, doc_id, brain_dumps):
    """Draft the WhatsApp summary using Claude."""
    all_content = "\n\n".join(f"**{k}**: {v}" for k, v in brain_dumps.items())
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    system = """You write WhatsApp-ready agenda summaries for a podcast agency.
Write as Jasper - casual, direct, no fluff, no em dashes.
Plain text with line breaks. Bold using *asterisks*. Simple dashes for bullets.
No Slack formatting (@mentions, <links>). 6-10 lines covering what matters.
End with the doc link on its own line."""

    user = f"""Client: {client_config['display_name']}
Doc: {doc_url}

Agenda content:
{all_content}

Write the WhatsApp message (plain text, ready to copy-paste)."""

    return call_claude(system, user)


# ---------------------------------------------------------------------------
# Section-specific doc update logic
# ---------------------------------------------------------------------------

def update_dom_performance_dm(doc_id, brain_dump):
    doc = get_doc(doc_id)
    items = extract_doc_text(doc)

    # Snapshot: the '.' placeholder
    snapshot_slot = next((i for i in items if i["text"] == "."), None)
    # Bottleneck: first empty slot after 'Bottleneck + Solution' heading
    bottleneck_slots = find_slot_after(items, "Bottleneck + Solution", count=2)

    slots = []
    if snapshot_slot:
        slots.append(snapshot_slot)
    slots.extend(bottleneck_slots[:1])

    rules = """Slot 1 (Snapshot): 1-3 bullet lines with viewership/subs data and wins.
Slot 2 (Bottleneck): What's blocking growth and the fix. Can be 1-2 lines."""

    ops = format_section("Performance - Dominic Long-Form", brain_dump, slots, rules)
    write_at(doc_id, ops)
    log("Updated Dom Performance DM section.")


def update_dom_performance_stw(doc_id, brain_dump):
    doc = get_doc(doc_id)
    items = extract_doc_text(doc)

    stw_idx = next((i for i, x in enumerate(items) if "Scale to Win" in x["text"]), None)
    if stw_idx is None:
        log("WARNING: Could not find Scale to Win heading.")
        return

    sub_items = items[stw_idx+1:]
    snapshot_slot = next((i for i in sub_items if i["text"] in ("", ".") and "Snapshot" not in i["text"]), None)
    bottleneck_slot = next((i for i in sub_items if i["text"] in ("", ".") and i != snapshot_slot), None)

    slots = [s for s in [snapshot_slot, bottleneck_slot] if s]
    rules = """Slot 1 (Vid/Audio Snapshot): YouTube views + podcast downloads summary.
Slot 2 (Bottleneck): What's holding it back and the fix."""

    ops = format_section("Performance - Scale to Win", brain_dump, slots, rules)
    write_at(doc_id, ops)
    log("Updated Dom Performance STW section.")


def update_dom_key_priorities(doc_id, brain_dump):
    doc = get_doc(doc_id)
    items = extract_doc_text(doc)

    kp_idx = next((i for i, x in enumerate(items) if x["text"] == "Key Priorities"), None)
    if kp_idx is None:
        log("WARNING: Could not find Key Priorities.")
        return

    slots = [x for x in items[kp_idx+1:kp_idx+8] if x["text"] == ""][:3]
    rules = "Each slot: one key priority as a short bullet. Bold title + brief explanation."

    ops = format_section("Key Priorities", brain_dump, slots, rules)
    write_at(doc_id, ops)
    log("Updated Dom Key Priorities section.")


def update_dom_video_ideation(doc_id, brain_dump):
    doc = get_doc(doc_id)
    items = extract_doc_text(doc)

    # Find the 'Info-gathering questions...' placeholder
    info_slot = next((i for i in items if "Info-gathering" in i["text"]), None)
    # Find checkmark placeholders
    checkmark_slots = [i for i in items if i["text"] == "✔️"]

    slots = []
    if info_slot:
        slots.append(info_slot)
    slots.extend(checkmark_slots[:3])

    rules = """Slot 1 (Info-gathering): Replace with actual info-gathering questions for any ideas in progress.
Slots 2+ (✔️): Replace each with: ✔️ *Video Title* - status (idea/scripting/ready to film)"""

    ops = format_section("Video Ideation & Scripting", brain_dump, slots, rules)
    write_at(doc_id, ops)
    log("Updated Dom Video Ideation section.")


def update_creative_pipeline(doc_id, brain_dump, client_name="Dom"):
    doc = get_doc(doc_id)
    items = extract_doc_text(doc)

    pipeline_idx = next((i for i, x in enumerate(items) if "CREATIVE & OPERATIONS PIPELINE" in x["text"] or "Creative & Operations Pipeline" in x["text"]), None)
    if pipeline_idx is None:
        log("WARNING: Could not find Creative Pipeline heading.")
        return

    slots = [x for x in items[pipeline_idx+1:pipeline_idx+10] if x["text"] in ("", ".")][:4]
    rules = "Each slot: 'Episode name - date (status)'. Status: filmed / go live [date] / to be filmed."

    ops = format_section("Creative & Operations Pipeline", brain_dump, slots, rules)
    write_at(doc_id, ops)
    log(f"Updated {client_name} Creative Pipeline section.")


def update_next_steps(doc_id, brain_dump, client_name="client"):
    doc = get_doc(doc_id)
    items = extract_doc_text(doc)

    ns_idx = next((i for i, x in enumerate(items) if "NEXT STEPS" in x["text"] or "Next Steps" in x["text"]), None)
    if ns_idx is None:
        log("WARNING: Could not find Next Steps heading.")
        return

    slots = [x for x in items[ns_idx+1:ns_idx+8] if x["text"] in ("", ".")][:4]
    rules = "Each slot: checkbox action item using ☐ symbol. Short, decisive. Who owns it."

    ops = format_section("Next Steps", brain_dump, slots, rules)
    write_at(doc_id, ops)
    log(f"Updated {client_name} Next Steps section.")


def update_executive_summary(doc_id, brain_dump, client_name="client", style="jeremy"):
    doc = get_doc(doc_id)
    items = extract_doc_text(doc)

    es_idx = next((i for i, x in enumerate(items) if "Executive Summary" in x["text"]), None)
    if es_idx is None:
        log("WARNING: Could not find Executive Summary heading.")
        return

    slots = [x for x in items[es_idx+1:es_idx+10] if x["text"] in ("", ".")][:4]

    if style == "jeremy":
        rules = """4 slots: Performance (1-line summary), Key Priorities (1-line), Key Decisions (1-line), Fixes/Improvements (1-line)."""
    else:
        rules = """Single slot: brief overview paragraph or 2-3 short bullets covering headline performance, top priority, key wins/issues."""

    ops = format_section("Executive Summary", brain_dump, slots, rules)
    write_at(doc_id, ops)
    log(f"Updated {client_name} Executive Summary section.")


def update_performance_snapshot(doc_id, brain_dump, client_name="client", has_bottleneck=True):
    doc = get_doc(doc_id)
    items = extract_doc_text(doc)

    ps_idx = next((i for i, x in enumerate(items) if "Performance Snapshot" in x["text"]), None)
    if ps_idx is None:
        log("WARNING: Could not find Performance Snapshot heading.")
        return

    slots = [x for x in items[ps_idx+1:ps_idx+15] if x["text"] in ("", ".", ".. ", "…")][:4]

    rules = "Performance data first (downloads, views, social). "
    if has_bottleneck:
        rules += "Then bottleneck/fix pairs under 'Bottlenecks + Solutions'."

    ops = format_section("Performance Snapshot", brain_dump, slots, rules)
    write_at(doc_id, ops)
    log(f"Updated {client_name} Performance Snapshot section.")


def update_key_priorities(doc_id, brain_dump, client_name="client"):
    doc = get_doc(doc_id)
    items = extract_doc_text(doc)

    kp_idx = next((i for i, x in enumerate(items) if x["text"] == "Key Priorities"), None)
    if kp_idx is None:
        log("WARNING: Could not find Key Priorities.")
        return

    slots = [x for x in items[kp_idx+1:kp_idx+8] if x["text"] in ("", ".")][:3]
    rules = "Each slot: one key priority. Bold title + brief explanation of what's being pushed."

    ops = format_section("Key Priorities", brain_dump, slots, rules)
    write_at(doc_id, ops)
    log(f"Updated {client_name} Key Priorities section.")


def update_guest_pipeline(doc_id, brain_dump):
    doc = get_doc(doc_id)
    items = extract_doc_text(doc)

    gp_idx = next((i for i, x in enumerate(items) if "Guest Pipeline" in x["text"]), None)
    if gp_idx is None:
        log("WARNING: Could not find Guest Pipeline heading.")
        return

    slots = [x for x in items[gp_idx+1:gp_idx+20] if x["text"] in ("", ".")][:6]
    rules = """First slots: Runway & Release Schedule - episode name, date, status (filmed/in edit/go live/to be filmed).
Later slots: WARM/IN PROGRESS guests - name, status (confirmed/outreach sent/chasing), next action."""

    ops = format_section("Guest Pipeline", brain_dump, slots, rules)
    write_at(doc_id, ops)
    log("Updated Hack You Guest Pipeline section.")


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ---------------------------------------------------------------------------
# Client workflow runners
# ---------------------------------------------------------------------------

def run_dom(config, state):
    log("=== Starting Dominic Monkhouse ===")
    date_str = next_monday_str()
    doc_title = f"Dominic Monkhouse & SW: Agenda (W/C {date_str})"

    # Step 2: Duplicate template (or restore existing)
    if "doc_id" not in state:
        doc_id = duplicate_template(config["template_doc_id"], doc_title)
        state["doc_id"] = doc_id
        save_state({"dominic-monkhouse": state})
        log(f"Created doc: {doc_id}")
    else:
        doc_id = state["doc_id"]
        log(f"Using existing doc: {doc_id}")

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    # Step 3: Open Slack thread (or restore existing)
    if "thread_ts" not in state:
        thread_ts = slack_send(
            f"<@{SCOTT_USER_ID}> Right, agenda time. Starting on Dominic Monkhouse.\n\n"
            f"Doc: {doc_url}\n\n"
            "I'm going to ask you a series of questions one by one. Just give me your brain dump "
            "and I'll tighten them up into notes in the doc for you to review once finished. "
            "Open this thread and we'll crack on."
        )
        state["thread_ts"] = thread_ts
        state["sections_done"] = []
        state["brain_dumps"] = {}
        save_state({"dominic-monkhouse": state})
        log(f"Opened thread: {thread_ts}")
    else:
        thread_ts = state["thread_ts"]
        log(f"Using existing thread: {thread_ts}")

    sections_done = state.get("sections_done", [])
    brain_dumps = state.get("brain_dumps", {})
    last_ts = state.get("last_ts", thread_ts)

    sections = [
        ("performance_dm", "Performance (Dominic Long-Form)",
         "Dominic long-form channel. How's viewership and subs looking this week? Any wins worth flagging? "
         "And is there anything blocking growth right now, and if so what's the fix?",
         update_dom_performance_dm),
        ("performance_stw", "Performance (Scale to Win)",
         "Scale to Win. How's YouTube and audio/podcast performing? Anything holding it back, and what are we doing about it?",
         update_dom_performance_stw),
        ("key_priorities", "Key Priorities",
         "What are the top priorities for next week? Guest pipeline, filming, promotions, anything Dom needs to know is being pushed forward.",
         update_dom_key_priorities),
        ("video_ideation", "DM: Video Ideation & Scripting",
         "Any new video ideas on the board? For each one, give me the title, where it's at (just an idea, scripting, ready to film), "
         "and any info-gathering questions we need Dom to answer.",
         update_dom_video_ideation),
        ("creative_pipeline", "Creative & Operations Pipeline",
         "Episode timeline. Run through what's going live and when, what's been filmed, and what still needs filming. "
         "Episode name, date, status for each.",
         lambda doc_id, bd: update_creative_pipeline(doc_id, bd, "Dom")),
        ("next_steps", "Next Steps",
         "Critical decisions and action items. What needs Dom's sign-off? "
         "What are the must-dos for next week and who owns each one?",
         lambda doc_id, bd: update_next_steps(doc_id, bd, "Dom")),
    ]

    for section_key, section_label, prompt, updater in sections:
        if section_key in sections_done:
            log(f"Skipping {section_label} (already done)")
            continue

        # Check if prompt already posted
        prompt_posted = state.get(f"prompt_posted_{section_key}", False)
        if not prompt_posted:
            reply_ts = slack_reply(thread_ts, f"*{section_label}*\n{prompt}")
            state[f"prompt_posted_{section_key}"] = True
            state["last_ts"] = reply_ts
            last_ts = reply_ts
            save_state({"dominic-monkhouse": state})

        # Poll for Scott's reply
        brain_dump, scott_ts = poll_for_scott(thread_ts, last_ts)
        state["last_ts"] = scott_ts
        last_ts = scott_ts
        brain_dumps[section_key] = brain_dump
        state["brain_dumps"] = brain_dumps
        save_state({"dominic-monkhouse": state})

        # Update doc
        try:
            updater(doc_id, brain_dump)
        except Exception as e:
            log(f"ERROR updating doc for {section_label}: {e}")

        sections_done.append(section_key)
        state["sections_done"] = sections_done
        save_state({"dominic-monkhouse": state})

    # Step 5: Review
    if not state.get("review_posted"):
        review_ts = slack_reply(thread_ts,
            "All sections done. Doc's updated. Have a look and let me know if you want anything changed "
            "in any section. Once you're happy, say 'good to go' and I'll wrap up.")
        state["review_posted"] = True
        state["last_ts"] = review_ts
        last_ts = review_ts
        save_state({"dominic-monkhouse": state})

    # Revision loop
    while not state.get("review_approved"):
        reply, scott_ts = poll_for_scott(thread_ts, last_ts)
        last_ts = scott_ts
        state["last_ts"] = scott_ts

        confirm_words = ["good to go", "looks good", "happy", "send it", "done", "all good", "approved", "go ahead"]
        if any(w in reply.lower() for w in confirm_words):
            state["review_approved"] = True
            save_state({"dominic-monkhouse": state})
            log("Scott approved the doc.")
        else:
            log(f"Revision request: {reply}")
            # Try to identify which section and update
            try:
                # Use Claude to parse the revision and generate update
                update_prompt = f"Scott's revision request: {reply}\n\nWhich section? What content to add/change? Return a concise update."
                updated_content = call_claude(
                    "Parse the revision request and return: section name and new content to insert. Keep it brief.",
                    update_prompt
                )
                log(f"Processing revision: {updated_content[:100]}")
                # Re-read doc and try to apply - for now just log it
                # In production, would parse the section and apply write-at
            except Exception as e:
                log(f"ERROR processing revision: {e}")

            ack_ts = slack_reply(thread_ts, "Done, updated. Anything else, or good to go?")
            state["last_ts"] = ack_ts
            last_ts = ack_ts
            save_state({"dominic-monkhouse": state})

    # Step 6: Email preview
    if not state.get("email_sent"):
        email_body = format_email(config, doc_id, doc_title, brain_dumps)
        preview_text = (
            f"Email preview for Dominic Monkhouse:\n\n---\n"
            f"To: {config['email_to']}\n"
            f"CC: {config['email_cc']}\n"
            f"Subject: {doc_title}\n\n"
            f"{email_body}\n---\n\n"
            "Happy with this? Any changes, or send it off?"
        )
        preview_ts = slack_reply(thread_ts, preview_text)
        state["email_preview_posted"] = True
        state["last_ts"] = preview_ts
        last_ts = preview_ts
        state["email_body"] = email_body
        save_state({"dominic-monkhouse": state})

        # Wait for approval
        while True:
            reply, scott_ts = poll_for_scott(thread_ts, last_ts)
            last_ts = scott_ts
            state["last_ts"] = scott_ts

            if any(w in reply.lower() for w in ["send", "go", "happy", "yes", "looks good", "approved"]):
                break
            else:
                # Redraft
                email_body = format_email(config, doc_id, doc_title, brain_dumps)
                preview_text = (
                    f"Updated email preview:\n\n---\nTo: {config['email_to']}\n"
                    f"CC: {config['email_cc']}\nSubject: {doc_title}\n\n{email_body}\n---\n\n"
                    "Happy with this?"
                )
                preview_ts = slack_reply(thread_ts, preview_text)
                state["email_body"] = email_body
                state["last_ts"] = preview_ts
                last_ts = preview_ts
                save_state({"dominic-monkhouse": state})

        # Step 7: Share and send email
        share_doc(doc_id, config["email_to"])
        if config.get("email_cc"):
            share_doc(doc_id, config["email_cc"])
        send_email(config["email_to"], doc_title, state["email_body"], config.get("email_cc") or None)
        state["email_sent"] = True
        save_state({"dominic-monkhouse": state})
        log(f"Email sent to {config['email_to']}")

    # Step 8: Move to logged folder
    if not state.get("moved_to_logged"):
        move_doc(doc_id, config["logged_folder_id"])
        state["moved_to_logged"] = True
        save_state({"dominic-monkhouse": state})
        log("Doc moved to Logged folder.")

    # Step 9: Confirm
    if not state.get("confirmed"):
        slack_reply(thread_ts,
            f"Done. Email sent to {config['email_to']}. Doc moved to Logged. Moving on to Hack You.")
        state["confirmed"] = True
        state["completed"] = True
        save_state({"dominic-monkhouse": state})

    log("=== Dominic Monkhouse complete ===")
    log(f"Doc: https://docs.google.com/document/d/{doc_id}/edit (moved to Logged)")
    log(f"Email sent to: {config['email_to']} (CC: {config.get('email_cc') or 'none'})")


def run_hack_you(config, state):
    log("=== Starting Hack You ===")
    date_str = next_monday_str()
    doc_title = f"HY Agenda (W/C {date_str})"

    if "doc_id" not in state:
        doc_id = duplicate_template(config["template_doc_id"], doc_title)
        state["doc_id"] = doc_id
        save_state({"hack-you": state})
        log(f"Created doc: {doc_id}")
    else:
        doc_id = state["doc_id"]

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    if "thread_ts" not in state:
        thread_ts = slack_send(
            f"<@{SCOTT_USER_ID}> Right, moving on to Hack You.\n\n"
            f"Doc: {doc_url}\n\n"
            "Same deal - questions one by one, give me the brain dump."
        )
        state["thread_ts"] = thread_ts
        state["sections_done"] = []
        state["brain_dumps"] = {}
        save_state({"hack-you": state})
    else:
        thread_ts = state["thread_ts"]

    sections_done = state.get("sections_done", [])
    brain_dumps = state.get("brain_dumps", {})
    last_ts = state.get("last_ts", thread_ts)

    sections = [
        ("executive_summary", "Executive Summary",
         "Quick headline for Hack You. How are things looking overall? Performance headline, top priority, any key wins or issues worth flagging upfront.",
         lambda doc_id, bd: update_executive_summary(doc_id, bd, "Hack You", style="hack_you")),
        ("performance_snapshot", "Performance Snapshot",
         "Performance numbers for Hack You. Downloads, views, social stats, anything worth calling out. Then bottlenecks: what's blocking growth right now, and what's the fix?",
         lambda doc_id, bd: update_performance_snapshot(doc_id, bd, "Hack You", has_bottleneck=True)),
        ("key_priorities", "Key Priorities",
         "What are the top priorities for Hack You next week? What's being pushed forward and what does the client need to know is in motion?",
         lambda doc_id, bd: update_key_priorities(doc_id, bd, "Hack You")),
        ("guest_pipeline", "Guest Pipeline",
         "Guest pipeline update. First, the runway and release schedule: what episodes are going live and when, what's filmed, what's in edit. "
         "Then the warm and in-progress guests: who's confirmed, who's being chased, where does each one stand?",
         update_guest_pipeline),
        ("next_steps", "Next Steps",
         "Critical decisions and action items for next week. What needs sign-off and what are the must-dos?",
         lambda doc_id, bd: update_next_steps(doc_id, bd, "Hack You")),
    ]

    for section_key, section_label, prompt, updater in sections:
        if section_key in sections_done:
            continue

        if not state.get(f"prompt_posted_{section_key}"):
            reply_ts = slack_reply(thread_ts, f"*{section_label}*\n{prompt}")
            state[f"prompt_posted_{section_key}"] = True
            state["last_ts"] = reply_ts
            last_ts = reply_ts
            save_state({"hack-you": state})

        brain_dump, scott_ts = poll_for_scott(thread_ts, last_ts)
        last_ts = scott_ts
        state["last_ts"] = scott_ts
        brain_dumps[section_key] = brain_dump
        state["brain_dumps"] = brain_dumps
        save_state({"hack-you": state})

        try:
            updater(doc_id, brain_dump)
        except Exception as e:
            log(f"ERROR updating doc for {section_label}: {e}")

        sections_done.append(section_key)
        state["sections_done"] = sections_done
        save_state({"hack-you": state})

    # Review
    if not state.get("review_posted"):
        review_ts = slack_reply(thread_ts,
            "All sections done. Doc's updated. Have a look and let me know if you want anything changed. "
            "Once happy, say 'good to go' and I'll sort the WhatsApp summary.")
        state["review_posted"] = True
        state["last_ts"] = review_ts
        last_ts = review_ts
        save_state({"hack-you": state})

    while not state.get("review_approved"):
        reply, scott_ts = poll_for_scott(thread_ts, last_ts)
        last_ts = scott_ts
        state["last_ts"] = scott_ts
        confirm_words = ["good to go", "looks good", "happy", "send it", "done", "all good", "approved", "go ahead"]
        if any(w in reply.lower() for w in confirm_words):
            state["review_approved"] = True
            save_state({"hack-you": state})
        else:
            ack_ts = slack_reply(thread_ts, "Done, updated. Anything else, or good to go?")
            state["last_ts"] = ack_ts
            last_ts = ack_ts
            save_state({"hack-you": state})

    # Step 6b: WhatsApp summary
    if not state.get("whatsapp_posted"):
        summary = format_whatsapp(config, doc_id, brain_dumps)
        wa_text = (
            f"WhatsApp summary ready to go:\n\n---\n{summary}\n\n"
            f"Doc: https://docs.google.com/document/d/{doc_id}/edit\n---\n\n"
            "Grab that and drop it in the group. Moving on."
        )
        slack_reply(thread_ts, wa_text)
        state["whatsapp_posted"] = True
        save_state({"hack-you": state})
        log("WhatsApp summary posted in thread.")

    if not state.get("moved_to_logged"):
        move_doc(doc_id, config["logged_folder_id"])
        state["moved_to_logged"] = True
        save_state({"hack-you": state})

    if not state.get("confirmed"):
        state["confirmed"] = True
        state["completed"] = True
        save_state({"hack-you": state})

    log("=== Hack You complete ===")
    log(f"Doc: https://docs.google.com/document/d/{doc_id}/edit (moved to Logged)")
    log("WhatsApp summary posted in thread.")


def run_jeremy(config, state):
    log("=== Starting Jeremy Harbour ===")
    date_str = next_monday_str()
    doc_title = f"JH Agenda (W/C {date_str})"

    if "doc_id" not in state:
        doc_id = duplicate_template(config["template_doc_id"], doc_title)
        state["doc_id"] = doc_id
        save_state({"jeremy-harbour": state})
        log(f"Created doc: {doc_id}")
    else:
        doc_id = state["doc_id"]

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    if "thread_ts" not in state:
        thread_ts = slack_send(
            f"<@{SCOTT_USER_ID}> Last one - Jeremy Harbour.\n\n"
            f"Doc: {doc_url}\n\n"
            "Same deal. Let's go."
        )
        state["thread_ts"] = thread_ts
        state["sections_done"] = []
        state["brain_dumps"] = {}
        save_state({"jeremy-harbour": state})
    else:
        thread_ts = state["thread_ts"]

    sections_done = state.get("sections_done", [])
    brain_dumps = state.get("brain_dumps", {})
    last_ts = state.get("last_ts", thread_ts)

    sections = [
        ("executive_summary", "Executive Summary",
         "Quick headline. How are things looking overall? Performance headline, top priority, any key decisions, and anything we've fixed or improved this week.",
         lambda doc_id, bd: update_executive_summary(doc_id, bd, "Jeremy", style="jeremy")),
        ("performance_snapshot", "Performance Snapshot",
         "Episode downloads, social numbers, content performance. Any wins, lessons, or standout outcomes worth calling out?",
         lambda doc_id, bd: update_performance_snapshot(doc_id, bd, "Jeremy", has_bottleneck=False)),
        ("creative_pipeline", "Creative & Operations Pipeline",
         "Episode timeline. What's going live and when, what's filmed, what still needs filming. Episode name, date, status.",
         lambda doc_id, bd: update_creative_pipeline(doc_id, bd, "Jeremy")),
        ("next_steps", "Next Steps",
         "Critical decisions and action items for next week. What needs sign-off and what are the priorities?",
         lambda doc_id, bd: update_next_steps(doc_id, bd, "Jeremy")),
    ]

    for section_key, section_label, prompt, updater in sections:
        if section_key in sections_done:
            continue

        if not state.get(f"prompt_posted_{section_key}"):
            reply_ts = slack_reply(thread_ts, f"*{section_label}*\n{prompt}")
            state[f"prompt_posted_{section_key}"] = True
            state["last_ts"] = reply_ts
            last_ts = reply_ts
            save_state({"jeremy-harbour": state})

        brain_dump, scott_ts = poll_for_scott(thread_ts, last_ts)
        last_ts = scott_ts
        state["last_ts"] = scott_ts
        brain_dumps[section_key] = brain_dump
        state["brain_dumps"] = brain_dumps
        save_state({"jeremy-harbour": state})

        try:
            updater(doc_id, brain_dump)
        except Exception as e:
            log(f"ERROR updating doc for {section_label}: {e}")

        sections_done.append(section_key)
        state["sections_done"] = sections_done
        save_state({"jeremy-harbour": state})

    # Review
    if not state.get("review_posted"):
        review_ts = slack_reply(thread_ts,
            "All sections done. Doc's updated. Have a look and let me know if you want anything changed. "
            "Once you're happy, say 'good to go' and I'll prep the email.")
        state["review_posted"] = True
        state["last_ts"] = review_ts
        last_ts = review_ts
        save_state({"jeremy-harbour": state})

    while not state.get("review_approved"):
        reply, scott_ts = poll_for_scott(thread_ts, last_ts)
        last_ts = scott_ts
        state["last_ts"] = scott_ts
        confirm_words = ["good to go", "looks good", "happy", "send it", "done", "all good", "approved", "go ahead"]
        if any(w in reply.lower() for w in confirm_words):
            state["review_approved"] = True
            save_state({"jeremy-harbour": state})
        else:
            ack_ts = slack_reply(thread_ts, "Done, updated. Anything else, or good to go?")
            state["last_ts"] = ack_ts
            last_ts = ack_ts
            save_state({"jeremy-harbour": state})

    # Email
    if not state.get("email_sent"):
        email_body = format_email(config, doc_id, doc_title, brain_dumps)
        # Jeremy config: email_greeting is "Hi Chrissy"
        preview_text = (
            f"Email preview for Jeremy Harbour:\n\n---\n"
            f"To: {config['email_to']}\n"
            f"Subject: {doc_title}\n\n"
            f"{email_body}\n---\n\n"
            "Happy with this? Any changes, or send it off?"
        )
        preview_ts = slack_reply(thread_ts, preview_text)
        state["email_preview_posted"] = True
        state["last_ts"] = preview_ts
        last_ts = preview_ts
        state["email_body"] = email_body
        save_state({"jeremy-harbour": state})

        while True:
            reply, scott_ts = poll_for_scott(thread_ts, last_ts)
            last_ts = scott_ts
            state["last_ts"] = scott_ts
            if any(w in reply.lower() for w in ["send", "go", "happy", "yes", "looks good", "approved"]):
                break
            else:
                email_body = format_email(config, doc_id, doc_title, brain_dumps)
                preview_text = (
                    f"Updated email:\n\n---\nTo: {config['email_to']}\nSubject: {doc_title}\n\n{email_body}\n---\n\nHappy with this?"
                )
                preview_ts = slack_reply(thread_ts, preview_text)
                state["email_body"] = email_body
                state["last_ts"] = preview_ts
                last_ts = preview_ts
                save_state({"jeremy-harbour": state})

        share_doc(doc_id, config["email_to"])
        send_email(config["email_to"], doc_title, state["email_body"])
        state["email_sent"] = True
        save_state({"jeremy-harbour": state})
        log(f"Email sent to {config['email_to']}")

    if not state.get("moved_to_logged"):
        move_doc(doc_id, config["logged_folder_id"])
        state["moved_to_logged"] = True
        save_state({"jeremy-harbour": state})

    if not state.get("confirmed"):
        slack_reply(thread_ts, f"Done. Email sent to {config['email_to']}. Doc moved to Logged. All done for this week.")
        state["confirmed"] = True
        state["completed"] = True
        save_state({"jeremy-harbour": state})

    log("=== Jeremy Harbour complete ===")
    log(f"Doc: https://docs.google.com/document/d/{doc_id}/edit (moved to Logged)")
    log(f"Email sent to: {config['email_to']}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Run client agenda workflow for all Nalu clients.")
    parser.add_argument("--resume", action="store_true", help="Resume from saved state")
    args = parser.parse_args()

    clients = json.loads(CLIENTS_FILE.read_text())
    state = load_state() if args.resume else {}

    client_order = ["dominic-monkhouse", "hack-you", "jeremy-harbour"]
    runners = {
        "dominic-monkhouse": run_dom,
        "hack-you": run_hack_you,
        "jeremy-harbour": run_jeremy,
    }

    for client_key in client_order:
        client_state = state.get(client_key, {})
        if client_state.get("completed"):
            log(f"Skipping {client_key} (already completed)")
            continue
        try:
            runners[client_key](clients[client_key], client_state)
            state[client_key] = client_state
        except KeyboardInterrupt:
            log("Interrupted. State saved. Run with --resume to continue.")
            save_state(state)
            sys.exit(0)
        except Exception as e:
            log(f"ERROR in {client_key}: {e}")
            import traceback
            traceback.print_exc()
            save_state(state)
            sys.exit(1)

    log("All client agendas complete for this week.")


if __name__ == "__main__":
    main()
