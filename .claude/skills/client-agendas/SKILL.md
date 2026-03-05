---
name: client-agendas
description: Use when someone asks to prepare a client agenda, build a weekly agenda, run client agendas for a specific client, or send a Friday performance update for a Nalu podcast client.
---

## What This Skill Does

Prepares and delivers weekly client agendas for Nalu podcast clients. The entire process runs through a Slack thread in #nalu-hub: tag Scott, collect his brain dumps, structure the agenda doc, let him review and tweak, then send the email and log it on his "good to go."

Configured clients: **Dominic Monkhouse**, **Jeremy Harbour**. Process runs Dom first, then Jeremy.

## Key People

- **Scott** (`U07BL527UP8` / `@scottlawuk`): Does the brain dumps for all clients. Tag him to kick off each agenda.
- **Jasper**: Triggers the skill. Signs off on the final email.

## Input

Jasper triggers this with something like:
> Run client agendas
> Prepare Dom's Friday agenda
> Client agendas for dominic-monkhouse

If no client is specified, run all clients in order (Dom first, then Jeremy). The client name must match a key in `clients.json`.

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

### Step 3: Collect Brain Dumps (In-Thread)

For each section in the client's `sections` config, post a prompt in the thread:

```bash
python3 tools/slack.py reply --channel "#nalu-hub" --thread-ts "{thread_ts}" --text "*{section_label}*\n{prompts_formatted}"
```

**Prompting style:**
- Post one section at a time. Keep it simple and specific.
- Frame prompts so Scott can just talk/type stream-of-consciousness. Example: "*Performance (Dominic Long-Form)* - What's the viewership/subscriber snapshot looking like this week? Any bottlenecks?"
- Don't ask multiple complex questions in one message. One section, one clear ask.
- After posting a section prompt, tell Jasper (in Claude Code) that you're waiting for Scott's reply, then pause.

**Reading Scott's replies:**
- When Jasper says Scott has replied (or says "check thread", "continue", etc.), read the thread:

```bash
python3 tools/slack.py read-thread --channel "#nalu-hub" --thread-ts "{thread_ts}"
```

- Parse Scott's brain dump. He'll send messy, verbatim voice-to-text or quick typed notes. Extract the key data: numbers, names, dates, statuses, action items.
- If something is unclear or missing, reply in the thread asking for clarification. Keep follow-ups short and specific.
- Once you have what you need for that section, move to the next one.
- After all sections are covered, reply in the thread: "Got everything. Building the doc now."

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

**Content formatting rules:**
- Structure Scott's brain dumps into clean, professional bullet points.
- Performance sections: Snapshot first, then Bottleneck + Solution if applicable.
- Episode timeline: Bold episode name, then date and status.
- Next steps: Checkbox-style list of action items with owners.
- Professional but direct tone. No em dashes.

### Step 6: Share for Review

Share the doc with Scott (writer access) and post the link in the thread:

```bash
python3 tools/gdocs.py --account {google_account} share --doc-id "{new_doc_id}" --email "scott@nalupodcasts.com" --role "writer"
```

Then reply in the thread:

```bash
python3 tools/slack.py reply --channel "#nalu-hub" --thread-ts "{thread_ts}" --text "Draft ready for review: https://docs.google.com/document/d/{new_doc_id}/edit\n\nHave a look, tweak anything, add screenshots if needed. Let me know when it's good to go."
```

**Now wait.** Scott will review, edit the doc directly, add screenshots, tighten things up. Do not proceed until Scott confirms.

### Step 7: Wait for "Good to Go"

When Jasper says Scott has confirmed (or says "good to go", "send it", "all done", "approved", etc.), read the thread to verify:

```bash
python3 tools/slack.py read-thread --channel "#nalu-hub" --thread-ts "{thread_ts}"
```

Look for Scott's confirmation message. Once confirmed, proceed to send.

### Step 8: Send Email

Share the doc with the client (reader access), then send the email:

```bash
python3 tools/gdocs.py --account {google_account} share --doc-id "{new_doc_id}" --email "{email_to}" --role "reader"
python3 tools/gdocs.py --account {google_account} share --doc-id "{new_doc_id}" --email "{email_cc}" --role "reader"
```

```bash
python3 tools/gmail.py --account {google_account} send \
  --to "{email_to}" \
  --cc "{email_cc}" \
  --subject "{doc_title}" \
  --body "{casual_email_body}"
```

**Email voice and tone:**
- Write as Jasper, not as a corporate agency. Conversational, direct, no fluff.
- Open casually: "Hey Dom, just sending in the agenda for next week." Match the greeting name to `email_greeting` in the client config.
- Get into the substance quickly. Mention 2-3 headline points from the agenda in a natural, conversational way. Not bullet points. Just talk through it like a quick verbal rundown.
- Include the Google Doc link inline, e.g. "Full agenda here: {link}"
- Close warmly but briefly: "Speak Monday." or "Chat Monday." Sign off as "Jasper" (not "Jasper & Team Nalu").
- No em dashes. Keep it short. 4-6 sentences max after the greeting.
- The email should feel like a quick Friday message from someone who knows the client well, not a formal report delivery.

Skip CC if `email_cc` is empty in the config.

### Step 9: Move to Logged Folder

```bash
python3 tools/gdocs.py --account {google_account} move --doc-id "{new_doc_id}" --folder-id "{logged_folder_id}"
```

### Step 10: Confirm in Thread

Reply in the Slack thread:

```bash
python3 tools/slack.py reply --channel "#nalu-hub" --thread-ts "{thread_ts}" --text "Done. Email sent to {email_to}. Doc moved to Logged. Moving on to {next_client_or_'all done'}."
```

Also confirm to Jasper in Claude Code:
- Doc: {link} (shared, moved to Logged)
- Email: sent to {email_to} (CC: {email_cc} or "none")

### Step 11: Next Client

If there are more clients in the queue, go back to Step 2 and start a **new thread** for the next client. Each client gets their own thread.

---

## Notes

- **Google account:** Always use the account specified in the client config (typically "nalu").
- **Template structure:** Google Doc, not a Sheet. Use the Docs API for all operations.
- **No em dashes.** Use periods, commas, colons, or restructure instead.
- **Date format:** Use ordinal dates (10th March, not March 10). Week commencing = next Monday.
- **Slack tool:** Uses `tools/slack.py` (direct API with Nalu bot token), not the MCP Slack integration (which is CN workspace only).
- **Scott's email for doc sharing:** scott@nalupodcasts.com (writer access for review). Update if this changes.
- **Async workflow:** This skill pauses at two points waiting for Scott: (1) after each section prompt for brain dumps, (2) after sharing the draft for review. Jasper tells Claude when to continue by saying things like "check thread", "he's replied", "good to go", etc.
- **Multiple clients:** Each client gets a separate Slack thread. Run Dom first, then Jeremy, unless Jasper specifies otherwise.
