---
name: client-agendas
description: Use when someone asks to prepare a client agenda, build a weekly agenda, run client agendas for a specific client, or send a Friday performance update for a Nalu podcast client.
---

## What This Skill Does

Prepares and delivers a weekly client agenda for Nalu podcast clients. Interviews Jasper to gather performance data and priorities, duplicates a Google Doc template, fills it in, and sends it to the client via email.

Currently configured for: **Dominic Monkhouse** (DM long-form + Scale to Win)

## Input

Jasper triggers this with something like:
> Run client agenda for Dom
> Prepare Dom's Friday agenda
> Client agendas for dominic-monkhouse

The client name must match a key in `clients.json` (supporting file in this skill's directory). If no client is specified, ask which client.

---

## Steps

### Step 1: Load Client Config

1. Read `clients.json` from this skill's directory
2. Look up the client by name (match against keys, `display_name`, or `short_name`)
3. If no match, list available clients and ask Jasper to pick

### Step 2: Interview Jasper

Walk through each section defined in the client's `sections` config. For each section:

1. State the section name (e.g., "Performance (Dominic Long-Form)")
2. Ask the prompts listed for that section
3. Wait for Jasper's response before moving to the next section
4. Take notes on everything Jasper provides. Capture specific numbers, names, dates, and action items exactly as given.

**Interview style:**
- Be direct and efficient. Don't repeat back what Jasper said unless clarifying.
- If Jasper gives a short answer, accept it. Don't push for more detail unless something is unclear.
- If Jasper says "skip" or "nothing" for a section, leave it minimal (e.g., "No updates this week").
- Once all sections are covered, confirm: "Got everything. Ready to build the doc?"

### Step 3: Duplicate the Template

Use the Google Docs tool to duplicate the client's template:

```bash
python3 tools/gdocs.py --account {google_account} duplicate --template-id "{template_doc_id}" --title "{display_name} & SW: Agenda (W/C {next_monday_date})"
```

The title format is: `{display_name} & SW: Agenda (W/C {date})` where the date is the Monday of the coming week (next Monday from today). Use format like "10th March", "17th March", etc.

Store the new document ID from the response.

### Step 4: Update the Document

The template uses a structured Google Doc format. Use the Docs API batchUpdate to insert content into the duplicated document.

Since the template has placeholder section headings, use `replace` or `batch-replace` commands to fill in content:

```bash
python3 tools/gdocs.py --account {google_account} batch-replace --doc-id "{new_doc_id}" --replacements '{...}'
```

**Content formatting rules:**
- Write in the same style as the filled-in example: bullet points, bold key items, concise.
- Performance sections: Snapshot first, then Bottleneck + Solution if applicable.
- Episode timeline: Bold episode name, then date and status (filmed/to be filmed/link available).
- Next steps: Checkbox-style list of action items.
- Keep Dom's voice and the agency's professional but direct tone.

If the template doesn't use simple placeholders (it uses section headings instead), read the doc structure first with `get`, then use the Docs API batchUpdate with `insertText` requests at the right positions. Adapt to whatever the template structure requires.

### Step 5: Share the Document

Share the completed doc with the client's email addresses:

```bash
python3 tools/gdocs.py --account {google_account} share --doc-id "{new_doc_id}" --email "{email_to}" --role "reader"
python3 tools/gdocs.py --account {google_account} share --doc-id "{new_doc_id}" --email "{email_cc}" --role "reader"
```

### Step 6: Send Email

Send a summary email from the Nalu Gmail account with a link to the completed agenda doc.

```bash
python3 tools/gmail.py --account {google_account} send \
  --to "{email_to}" \
  --cc "{email_cc}" \
  --subject "{display_name} & SW: Agenda (W/C {next_monday_date})" \
  --body "{email_greeting},

Here's your agenda and performance snapshot for the week commencing {next_monday_date}.

Doc: https://docs.google.com/document/d/{new_doc_id}/edit

{executive_summary}

Speak Monday.

Best,
Jasper & Team Nalu"
```

The email body should include:
- Link to the Google Doc
- A brief executive summary (2-4 bullet points hitting: performance headline, top priority, any decisions needed)
- Professional but warm sign-off

### Step 7: Move to Logged Folder

Move the completed agenda doc into the client's "Logged" folder in Drive:

```bash
python3 tools/gdocs.py --account {google_account} move --doc-id "{new_doc_id}" --folder-id "{logged_folder_id}"
```

The `logged_folder_id` comes from the client config. This keeps the client's Drive folder clean, with only the template remaining at the top level.

### Step 8: Post to Slack (if available)

If the Slack channel is accessible, post a message to the client's Slack channel with the doc link and a brief summary.

If the Slack workspace isn't connected (as is currently the case for Nalu), skip this step and note it was skipped.

### Step 9: Confirm

Tell Jasper:
- Doc created, shared, and moved to Logged: {link}
- Email sent to {email_to} (CC: {email_cc} or "none")
- Slack: {sent/skipped}

---

## Notes

- **Google account:** Always use the account specified in the client config (typically "nalu" for Nalu clients).
- **Template structure:** The template is a Google Doc, not a Sheet. Use the Docs API for all operations.
- **No em dashes.** Use periods, commas, colons, or restructure instead.
- **Date format:** Use ordinal dates (10th March, not March 10). Week commencing = next Monday.
- **Multiple clients:** The skill is designed to support multiple clients via `clients.json`. Each client has their own template, sections, and delivery config. Add new clients by adding entries to the config.
- **Slack:** Currently blocked because the MCP is connected to the CN workspace, not Nalu. Once a second Slack workspace is connected, update the channel ID in the config.
