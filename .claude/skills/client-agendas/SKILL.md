---
name: client-agendas
description: Use when someone asks to prepare a client agenda, build a weekly agenda, run client agendas for a specific client, or send a Friday performance update for a Nalu podcast client.
---

## What This Skill Does

Prepares and delivers weekly client agendas for Nalu podcast clients. The entire process runs through a Slack thread in #nalu-hub: tag Scott, collect his brain dumps, structure the agenda doc, let him review and tweak, then send the email and log it on his "good to go."

Configured clients: **Dominic Monkhouse**, **Jeremy Harbour**. Process runs Dom first, then Jeremy.

## Key People

- **Scott** (`U07BL527UP8` / `@scottlawuk`): Does the brain dumps for all clients. Reviews the doc draft and approves the email before it sends. The entire workflow runs between Claude and Scott via the Slack thread.

## Input

Jasper triggers this with something like:
> Run client agendas
> Prepare Dom's Friday agenda
> Client agendas for dominic-monkhouse

If no client is specified, run all clients in order (Dom first, then Jeremy). The client name must match a key in `clients.json`. Once triggered, the workflow runs autonomously between Claude and Scott in #nalu-hub. Jasper does not need to relay or intervene.

---

## Steps

### Step 1: Load Client Config

1. Read `clients.json` from this skill's directory
2. Look up the client by name (match against keys, `display_name`, or `short_name`)
3. If "all" or no client specified, queue all clients starting with `dominic-monkhouse`

### Step 2: Open Slack Thread

Post the kickoff message to `#nalu-hub` tagging Scott:

```bash
python3 tools/slack.py send --channel "#nalu-hub" --text "<@U07BL527UP8> - {display_name} agenda for W/C {next_monday_date}. Going to walk through each section. Just brain dump whatever you've got and I'll structure it."
```

**Store the `ts` from the response.** This is the thread ID. All subsequent messages for this client go in this thread using `reply`.

### Step 3: Collect Brain Dumps (In-Thread, One Section at a Time)

Walk through sections **one by one**. Post a single section prompt, wait for Scott's brain dump, then move to the next.

For each section in the client's `sections` config:

1. Post the prompt:

```bash
python3 tools/slack.py reply --channel "#nalu-hub" --thread-ts "{thread_ts}" --text "*{section_label}*\n{prompt}"
```

2. Wait for Scott to reply. After a reasonable pause, check the thread for new messages:

```bash
python3 tools/slack.py read-thread --channel "#nalu-hub" --thread-ts "{thread_ts}"
```

4. Parse Scott's brain dump. He'll voice-dump via Whisper or type quick messy notes. Stream-of-consciousness, no structure. Extract the key data: numbers, names, dates, statuses, action items.

5. If something critical is missing or unclear, reply with a short follow-up: "Got it. Quick one: what's the status on [X]? Filmed or still to do?"

6. Once you have what you need for that section, move to the next one. No need to confirm each section back to Scott unless clarifying.

After all sections are done, reply in the thread: "Got everything. Building the doc now."

### Step 4: Duplicate the Template

```bash
python3 tools/gdocs.py --account {google_account} duplicate --template-id "{template_doc_id}" --title "{doc_title_from_format}"
```

Use the `doc_title_format` from the client config. Date is next Monday from today, formatted as ordinal (e.g. "10th March").

Store the new document ID.

### Step 5: Update the Document

Read the template structure first:

```bash
python3 tools/gdocs.py --account {google_account} get --doc-id "{new_doc_id}"
```

Then fill in content using batch-replace (if placeholders exist) or insertText at the right positions:

```bash
python3 tools/gdocs.py --account {google_account} batch-replace --doc-id "{new_doc_id}" --replacements '{...}'
```

**Content formatting rules (match the finished agenda style exactly):**

The doc must look like a polished, professional weekly agenda. Structure Scott's messy brain dumps into this exact format:

- **Performance sections** (DM Long-Form, Scale to Win):
  - **Snapshot** (or **Vid/Audio Snapshot** for STW): concise bullet points on viewership, subs, audio DL/streams. Short, factual sentences.
  - **Bottleneck + Solution**: what's blocking growth + the proposed fix. Sub-bullets (italic) for caveats or notes.
  - Screenshots get dropped in by Scott during review. Leave space for them.

- **Key Priorities**: each priority is a bold heading with sub-bullets explaining what's happening. E.g.:
  - **Guest pipeline extended for Scale To Win**
    - Pat to report on outreach + continue to book in guests for next week
    - Email outreach begins on Monday (with warmed inboxes)

- **DM: Video Ideation & Scripting**:
  - "New Video Ideas Highlighted:" heading
  - Notion link if available
  - Each idea: checkmark + **bold title** + sub-bullet with status/notes (e.g. "Script to be drafted this weekend." or "Info-gathering questions here")

- **Creative & Operations Pipeline**:
  - "Episode timeline:" heading
  - Bullet list: **Bold episode name** - date (status). Statuses: "filmed", "link available [day]", "to be filmed", "TO BE FILMED" (caps for urgent)

- **Next Steps**:
  - "Critical Decisions Round-up:" heading
  - Checkbox-style list (☐) of action items. Short, decisive.

- **Tone**: professional but direct. Short sentences. No em dashes. No filler. Every bullet should convey information, not padding.

- **Per-client adaptation**: Both templates follow the same structure and formatting principles. Jeremy's has an Executive Summary up top (Performance headline, Key Priorities, Key Decisions, Fixes/Improvements) and a single Performance Snapshot instead of two separate channels. Otherwise identical: same bullet hierarchy, same Video Ideation section, same Creative Pipeline, same Next Steps with checkboxes. Always read the template with `get` first and match its exact section headings.

### Step 6: Share for Review

Scott is signed into hello@nalupodcasts.com (the same account that owns the doc), so no sharing step is needed. Just post the link in the thread:

```bash
python3 tools/slack.py reply --channel "#nalu-hub" --thread-ts "{thread_ts}" --text "Draft ready for review: https://docs.google.com/document/d/{new_doc_id}/edit\n\nHave a look, tweak anything, add screenshots if needed. Let me know when it's good to go."
```

**Now wait.** Scott will review, edit the doc directly, add screenshots, tighten things up. Do not proceed until Scott confirms.

### Step 7: Wait for Doc Approval

Wait for Scott to confirm the doc is ready. Check the thread for his response:

```bash
python3 tools/slack.py read-thread --channel "#nalu-hub" --thread-ts "{thread_ts}"
```

Once Scott confirms the doc is ready, move to the email preview. Do not send the email until it has also been approved separately in Step 8.

### Step 8: Preview Email with Scott

Draft the email body and post a preview in the Slack thread for Scott to review before sending:

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

**Now wait.** Scott will either suggest changes or confirm. If he suggests changes, redraft and preview again. Once he says "send it" / "good to go" / confirms, proceed.

### Step 9: Send Email

Share the doc with the client (reader access), then send the approved email:

```bash
python3 tools/gdocs.py --account {google_account} share --doc-id "{new_doc_id}" --email "{email_to}" --role "reader"
```

If `email_cc` is not empty in the config, also share with them:

```bash
python3 tools/gdocs.py --account {google_account} share --doc-id "{new_doc_id}" --email "{email_cc}" --role "reader"
```

Then send:

```bash
python3 tools/gmail.py --account {google_account} send \
  --to "{email_to}" \
  --cc "{email_cc}" \
  --subject "{doc_title}" \
  --body "{approved_email_body}"
```

If `email_cc` is empty, omit the `--cc` flag entirely.

### Step 10: Move to Logged Folder

```bash
python3 tools/gdocs.py --account {google_account} move --doc-id "{new_doc_id}" --folder-id "{logged_folder_id}"
```

### Step 11: Confirm in Thread

Reply in the Slack thread:

```bash
python3 tools/slack.py reply --channel "#nalu-hub" --thread-ts "{thread_ts}" --text "Done. Email sent to {email_to}. Doc moved to Logged. Moving on to {next_client_or_'all done'}."
```

Also log to Claude Code output:
- Doc: {link} (shared, moved to Logged)
- Email: sent to {email_to} (CC: {email_cc} or "none")

### Step 12: Next Client

If there are more clients in the queue, go back to Step 2 and start a **new thread** for the next client. Each client gets their own thread.

---

## Notes

- **Google account:** Always use the account specified in the client config (typically "nalu").
- **Template structure:** Google Doc, not a Sheet. Use the Docs API for all operations.
- **No em dashes.** Use periods, commas, colons, or restructure instead.
- **Date format:** Use ordinal dates (10th March, not March 10). Week commencing = next Monday.
- **Slack tool:** Uses `tools/slack.py` (direct API with Nalu bot token), not the MCP Slack integration (which is CN workspace only).
- **Doc access:** Scott is signed into hello@nalupodcasts.com (the Nalu account), so he has direct edit access to all docs created under that account. No sharing step needed for him.
- **Async workflow:** This skill pauses multiple times waiting for Scott: (1) after each section prompt for brain dumps, (2) after sharing the doc draft for review, (3) after posting the email preview for approval. Claude polls the thread for Scott's replies and proceeds autonomously. Jasper only triggers the skill; everything else runs between Claude and Scott.
- **Multiple clients:** Each client gets a separate Slack thread. Run Dom first, then Jeremy, unless Jasper specifies otherwise.
