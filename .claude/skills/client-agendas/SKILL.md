---
name: client-agendas
description: Use when someone asks to prepare a client agenda, build a weekly agenda, run client agendas for a specific client, or send a Friday performance update for a Nalu podcast client.
---

## What This Skill Does

Prepares and delivers weekly client agendas for Nalu podcast clients. The entire process runs through a Slack thread in #nalu-hub between Claude and Scott. Claude duplicates the template, opens a thread, walks Scott through each section one by one, updates the doc in real time, then handles review, email, and logging.

Configured clients: **Dominic Monkhouse**, **Jeremy Harbour**. Process runs Dom first, then Jeremy.

## Key People

- **Scott** (`U07BL527UP8` / `@scottlawuk`): Does the brain dumps for all clients. Reviews the doc draft and approves the email before it sends. The entire workflow runs between Claude and Scott via the Slack thread.

## Input

Jasper triggers this with something like:
> Run client agendas
> Prepare Dom's Friday agenda
> Client agendas for dominic-monkhouse

If no client is specified, run all clients in order (Dom first, then Jeremy). The client name must match a key in `clients.json`. Once triggered, the workflow runs autonomously between Claude and Scott in #nalu-hub. Jasper does not need to intervene.

---

## Steps

### Step 1: Load Client Config

1. Read `clients.json` from this skill's directory
2. Look up the client by name (match against keys, `display_name`, or `short_name`)
3. If "all" or no client specified, queue all clients starting with `dominic-monkhouse`

### Step 2: Duplicate the Template

Duplicate the client's template **before** opening the Slack thread. The doc needs to exist so Scott has the link from the start.

```bash
python3 tools/gdocs.py --account {google_account} duplicate --template-id "{template_doc_id}" --title "{doc_title}"
```

Title uses `doc_title_format` from the client config. The date is the Monday of the coming week (next Monday from today), formatted as ordinal (e.g. "9th March", "16th March").

Store the new document ID.

### Step 3: Open Slack Thread

Post the kickoff message to `#nalu-hub` tagging Scott, with a link to the new doc:

```bash
python3 tools/slack.py send --channel "#nalu-hub" --text "<@U07BL527UP8> Right, agenda time. Starting on {display_name}.\n\nDoc: https://docs.google.com/document/d/{new_doc_id}/edit\n\nI'm going to ask you a series of questions one by one. Just give me your brain dump and I'll tighten them up into notes in the doc for you to review once finished. Open this thread and we'll crack on."
```

**Store the `ts` from the response.** This is the thread ID. All subsequent messages for this client go in this thread using `reply`.

### Step 4: Collect Brain Dumps and Update Doc (One Section at a Time)

Walk through sections **one by one**. For each section in the client's `sections` config:

1. **Post the prompt** in the thread:

```bash
python3 tools/slack.py reply --channel "#nalu-hub" --thread-ts "{thread_ts}" --text "*{section_label}*\n{prompt}"
```

2. **Wait for Scott to reply.** Poll the thread every 60 seconds until a new message from Scott appears. Do not stop polling. Keep looping (`sleep 60` then read-thread) until Scott's reply is detected.

```bash
# Poll loop: repeat every 60 seconds until Scott replies
python3 tools/slack.py read-thread --channel "#nalu-hub" --thread-ts "{thread_ts}"
```

Compare the message count or latest timestamp against what you had before posting the question. A new message from a user other than the bot (`U0AJT4W0BNJ`) means Scott has replied.

3. **Parse Scott's brain dump.** He'll voice-dump via Whisper or type quick messy notes. Stream-of-consciousness, no structure. Extract the key data: numbers, names, dates, statuses, action items.

4. **If something critical is missing or unclear**, reply with a short follow-up: "Got it. Quick one: what's the status on [X]? Filmed or still to do?"

5. **Update that section in the doc immediately.** Don't wait until all sections are done. Read the doc structure first with `get` to understand the exact placeholder positions, nesting levels, and formatting. Then use `batch-replace` to swap placeholder text with real content, preserving the template's bullet hierarchy.

```bash
python3 tools/gdocs.py --account {google_account} get --doc-id "{new_doc_id}"
python3 tools/gdocs.py --account {google_account} batch-replace --doc-id "{new_doc_id}" --replacements '{...}'
```

**Critical:** The templates use specific placeholder text at specific nesting levels. Replace the placeholder text only. Do not restructure the doc's bullet hierarchy. The template already has the correct headings, sub-headings, and nesting. You just fill in the content under each.

6. **Move to the next section.** No need to confirm each section back to Scott unless clarifying.

After all sections are done, reply in the thread: "All sections done. Doc's updated. Have a look, make any changes you need, and confirm once you're happy. I'll draft the email."

---

## Template Structures

**IMPORTANT:** Always `get` the duplicated doc before writing to it. The templates define the exact structure. Your job is to replace placeholder text while preserving the formatting, nesting, and bullet styles.

### Dom's Template (`1nceseooW3wVi7eEWw_wbFo740-686i3QumrLdSlqDq0`)

```
Performance (DOMINIC LONG-FORM)          ← Section heading (no bullet)
  ○ Snapshot                              ← L1 bold sub-heading
    ■ .                                   ← L2 placeholder (replace with snapshot bullets)
  ○ Bottleneck + Solution                 ← L1 bold sub-heading
    ■ (empty)                             ← L2 placeholder (replace with bottleneck + fix)
      ● (empty)                           ← L3 italic caveat sub-bullets

---

Performance (Scale to Win)               ← Section heading
  ○ Vid/Audio Snapshot                    ← L1 bold sub-heading
    ■ (placeholders)                      ← L2 content
  ○ Bottleneck + Solution                 ← L1 bold sub-heading
    ■ (placeholders)                      ← L2 content

Key Priorities                            ← L0 bold heading
  (empty lines for priority bullets)

---
1. DM: VIDEO IDEATION & SCRIPTING         ← Section heading
  New Video Ideas Highlighted:
  Notion Link #1:
  NEW VIDEO IDEAS
    ○ Info-gathering questions...          ← L1
  ✔️ (checkmark items)                    ← L0

---
2. CREATIVE & OPERATIONS PIPELINE         ← Section heading
  Episode timeline:
    ○ Episode name - date (status)        ← L0 bold placeholders to replace

---
4. NEXT STEPS
  Critical Decisions Round-up:
  This Week's Strategic Priorities:
```

**Dom section prompts map to:** performance_dm → fills "Performance (DOMINIC LONG-FORM)" section; performance_stw → fills "Performance (Scale to Win)"; key_priorities → fills "Key Priorities"; video_ideation → fills "DM: VIDEO IDEATION & SCRIPTING"; creative_pipeline → fills "CREATIVE & OPERATIONS PIPELINE"; next_steps → fills "NEXT STEPS".

### Jeremy's Template (`1N8qZaLVrX2p6xPDVbBGxSNIzgCZWz2j1ny7GLQ9vvDU`)

```
Executive Summary                         ← Heading
  ○ Performance:                          ← L0 bold (fill with 1-line summary)
  ○ Key Priorities                        ← L0 bold
  ○ Key Decisions                         ← L0 bold
  ○ Fixes / Improvements                  ← L0 bold

---

1. Performance Snapshot                   ← Section heading
  ○ Episode downloads:                    ← L0 bold placeholder
  ○ Social performance                    ← L0 bold placeholder
  ○ Content Analysis                      ← L0 bold placeholder
  Highlight wins, lessons, outcomes       ← Italic (no bullet)
  ○ ..  /  …  /  …                       ← L0 placeholders for extra content

---
2. CREATIVE & OPERATIONS PIPELINE         ← Section heading
  Episode timeline:
  ○ Episode name - date (status)          ← L0 bold placeholders

---
3. NEXT STEPS
  Critical Decisions Round-up:
  This Week's Strategic Priorities:
```

**Jeremy section prompts map to:** executive_summary → fills "Executive Summary" bullets; performance_snapshot → fills "1. Performance Snapshot" (Episode downloads, Social performance, Content Analysis, wins/outcomes); creative_pipeline → fills "CREATIVE & OPERATIONS PIPELINE"; next_steps → fills "NEXT STEPS".

**Key differences from Dom:** Jeremy has an Executive Summary at the top. His Performance Snapshot is flat (L0 bullets, no Snapshot/Bottleneck sub-structure). He has no Video Ideation section. He has no Key Priorities section outside the Executive Summary.

---

## Content Formatting Rules

- **Tone**: professional but direct. Short sentences. No em dashes. No filler. Every bullet should convey information, not padding.
- **Performance sections**: Replace placeholders with concise, factual content. For Dom, the Snapshot gets viewership/subs data and the Bottleneck + Solution gets what's blocking growth and the fix. Italic caveats go in L3 sub-bullets under Bottleneck.
- **Key Priorities** (Dom only): Each priority is a bold line with sub-bullets explaining what's happening.
- **Video Ideation** (Dom only): Each idea gets a checkmark + bold title + status notes.
- **Creative & Operations Pipeline**: Replace episode placeholder lines with actual episode names, dates, and statuses (filmed, go live [date], to be filmed, TO BE FILMED for urgent).
- **Next Steps**: Checkbox-style (☐) action items. Short, decisive.
- **Executive Summary** (Jeremy only): Fill each bullet (Performance, Key Priorities, Key Decisions, Fixes/Improvements) with a 1-line summary of that area.
- Screenshots get dropped in by Scott during review. Leave space for them.

### Step 5: Wait for Doc Approval

Scott will review the doc directly (he's signed into hello@nalupodcasts.com, the account that owns it). He'll tweak wording, add screenshots, tighten things up.

Wait for Scott to confirm in the thread. Poll every 60 seconds (`sleep 60` then read-thread) until Scott replies:

```bash
python3 tools/slack.py read-thread --channel "#nalu-hub" --thread-ts "{thread_ts}"
```

Look for confirmation ("good to go", "looks good", "done", etc.). Once confirmed, move to the email. This may take several minutes as Scott reviews and edits the doc. Keep polling.

### Step 6: Preview Email with Scott

Draft the email body and post a preview in the thread for Scott to review:

```bash
python3 tools/slack.py reply --channel "#nalu-hub" --thread-ts "{thread_ts}" --text "Email preview for {display_name}:\n\n---\nTo: {email_to}\nCC: {email_cc}\nSubject: {doc_title}\n\n{email_body}\n---\n\nHappy with this? Any changes, or send it off?"
```

**Email voice and tone:**
- Write as Jasper, not as a corporate agency. Conversational, direct, no fluff.
- Open casually: "Hey Dom, just sending in the agenda for next week." Match the greeting name to `email_greeting` in the client config.
- Get into the substance quickly. Mention 2-3 headline points from the agenda in a natural, conversational way. Not bullet points. Just talk through it like a quick verbal rundown.
- Include the Google Doc link inline, e.g. "Full agenda here: {link}"
- Close warmly but briefly: "Speak Monday." or "Chat Monday." Sign off as "Jasper" (not "Jasper & Team Nalu").
- No em dashes. Keep it short. 4-6 sentences max after the greeting.
- The email should feel like a quick Friday message from someone who knows the client well, not a formal report delivery.

**Now wait.** Poll every 60 seconds until Scott replies. He will either suggest changes or confirm. If he suggests changes, redraft and preview again. Once he confirms, proceed.

### Step 7: Send Email

Share the doc with the client (reader access):

```bash
python3 tools/gdocs.py --account {google_account} share --doc-id "{new_doc_id}" --email "{email_to}" --role "reader"
```

If `email_cc` is not empty, also share with them:

```bash
python3 tools/gdocs.py --account {google_account} share --doc-id "{new_doc_id}" --email "{email_cc}" --role "reader"
```

Then send the approved email:

```bash
python3 tools/gmail.py --account {google_account} send \
  --to "{email_to}" \
  --cc "{email_cc}" \
  --subject "{doc_title}" \
  --body "{approved_email_body}"
```

If `email_cc` is empty, omit the `--cc` flag entirely.

### Step 8: Move to Logged Folder

```bash
python3 tools/gdocs.py --account {google_account} move --doc-id "{new_doc_id}" --folder-id "{logged_folder_id}"
```

### Step 9: Confirm in Thread

Reply in the Slack thread:

```bash
python3 tools/slack.py reply --channel "#nalu-hub" --thread-ts "{thread_ts}" --text "Done. Email sent to {email_to}. Doc moved to Logged. Moving on to {next_client_or_'All done for this week.'}."
```

Also log to Claude Code output:
- Doc: {link} (shared, moved to Logged)
- Email: sent to {email_to} (CC: {email_cc} or "none")

### Step 10: Next Client

If there are more clients in the queue, go back to Step 2 and start a **new thread** for the next client. Each client gets their own thread.

---

## Notes

- **Google account:** Always use the account specified in the client config (typically "nalu").
- **Template structure:** Google Doc, not a Sheet. Use the Docs API for all operations.
- **No em dashes.** Use periods, commas, colons, or restructure instead.
- **Date format:** Use ordinal dates (9th March, not March 9). Week commencing = next Monday from today.
- **Slack tool:** Uses `tools/slack.py` (direct API with Nalu bot token), not the MCP Slack integration (which is CN workspace only).
- **Doc access:** Scott is signed into hello@nalupodcasts.com (the Nalu account), so he has direct edit access to all docs created under that account. No sharing step needed for him.
- **Update doc as you go:** Each section gets written into the doc immediately after parsing Scott's brain dump. Don't batch all updates to the end.
- **Polling:** This skill pauses multiple times waiting for Scott: (1) after each section prompt for brain dumps, (2) after all sections are done for doc review, (3) after posting the email preview for approval. **At every pause point, poll every 60 seconds** (`sleep 60` then `read-thread`). Never stop polling. Keep looping until Scott replies. The cron job runs with `--dangerously-skip-permissions` so the sleep/poll loop runs unattended.
- **Multiple clients:** Each client gets a separate Slack thread. Run Dom first, then Jeremy, unless specified otherwise.
- **Schedule:** Runs every Thursday at 8PM UK time via cron. Can also be triggered manually.
