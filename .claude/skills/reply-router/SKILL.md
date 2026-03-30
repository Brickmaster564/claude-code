---
name: reply-router
description: Use when someone asks to reply to an Instantly email, process a guest reply, or when triggered by a Slack thread reply to an email notification. Also triggers on "reply-router" in Slack messages.
disable-model-invocation: true
---

## What This Skill Does

Drafts and sends email replies through Instantly based on team notes from Slack. Triggered automatically when someone replies in a Slack thread to an Instantly email notification (posted by Nalu Helper via n8n).

## Flow

1. Slack listener detects a thread reply to a notification containing "EMAIL ID:"
2. Claude is spawned with the email ID, notification context, and team member's notes
3. Claude fetches the full email from Instantly to get the complete context
4. Claude identifies the campaign/show, assesses intent, and updates Airtable if the guest shows positive interest
5. Claude drafts a professional reply using the team's notes and Nalu brand voice
6. Claude sends the reply via Instantly API
7. Claude posts confirmation back to the Slack thread (including whether Airtable was updated)

## Steps

### Step 1: Parse the Input

The spawned prompt includes these fields (extracted by slack-listener.py):
- `INSTANTLY EMAIL ID` - the UUID of the email to reply to
- `ORIGINAL NOTIFICATION` - the notification message posted by Nalu Helper
- `TEAM MEMBER'S NOTES` - rough notes/direction from Scott or Jasper
- `SLACK CHANNEL` and `SLACK THREAD TS` - for posting confirmation

### Step 2: Fetch the Original Email

Run:
```
python3 tools/instantly.py get-email --id "<INSTANTLY EMAIL ID>"
```

This returns the full email including:
- `from_address_email` - who sent the reply
- `to_address_email_list` - who the email was sent to
- `cc_address_email_list` - anyone CC'd on the email
- `eaccount` - the Instantly sending account (needed for replying)
- `subject` - the email subject
- `body` - the full email body (text and HTML)
- `thread_id` - the email thread

Note the `cc_address_email_list` field. This is needed for reply-all in Step 5.

### Step 3: Identify Show and Update Airtable

This step determines which podcast show the campaign belongs to, checks whether the guest's reply indicates positive interest, and updates their Airtable record accordingly.

**3a. Identify the show from the campaign**

The ORIGINAL NOTIFICATION from Nalu Helper contains the campaign name and campaign ID. Examine these to determine which show the email belongs to:

| Campaign contains | Show | Airtable Base | Airtable Table |
|---|---|---|---|
| "FTT" | First Things THRST | `appiowT0T5O07BfYB` | `tbltDNojUS6gREZ2E` |
| "Scale to Win" or "STW" | Scale to Win | `appZcubMACqoEtA5f` | `tbloHFKqyqhwZG8bV` |
| "HYM" or "Hack You" | Hack You Media | `apptwbxnUum6b0fv4` | `tblDgQFIg9c02D4SH` |
| "JH" or "Jeremy Harbour" or "Deal Junky" | Deal Junky | `appsHgXM4NYOx8n2y` | `tbloHFKqyqhwZG8bV` |

**Skip entirely if the campaign name starts with "CN -" or "🔴 PPC".** These are Client Network campaigns, not Nalu guest outreach. Do not attempt Airtable lookup or status update for these. Proceed directly to Step 4 (Draft the Reply).

If the campaign name is ambiguous, use the `campaign_id` from the `get-email` response to fetch the full campaign details:
```
python3 tools/instantly.py get-campaign --id "<campaign_id>"
```

**3b. Assess intent**

Read the guest's email reply and determine whether it signals positive interest in appearing on the show. Positive intent includes:
- Expressing interest or excitement about the podcast
- Asking about scheduling, logistics, or next steps
- Requesting more information about the format or topics
- Confirming availability or suggesting times
- Any reply that moves the conversation forward toward a booking

Negative or neutral intent (do NOT update Airtable):
- Declining the invitation
- Unsubscribe requests
- Out-of-office or auto-replies
- Asking to be removed
- Non-committal responses that don't advance the conversation

**3c. Update Airtable (positive intent only)**

If the reply shows positive intent, find and update the guest's Airtable record.

**Search strategy:** Try MCP first, fall back to REST API if MCP is unavailable.

**Option A: Airtable MCP (preferred)**

```
Use ToolSearch to load: select:mcp__claude_ai_Airtable__search_records,mcp__claude_ai_Airtable__update_record
```

If the tools load successfully, search for the guest by their email address (`from_address_email` from the get-email response):
```
mcp__claude_ai_Airtable__search_records
  base_id: <base from table above>
  table_id: <table from table above>
  search_term: <guest's email address>
```

If no match, try searching by the guest's name (extracted from the email body or notification context).

To update:
```
mcp__claude_ai_Airtable__update_record
  base_id: <base>
  table_id: <table>
  record_id: <matched record ID>
  fields: { "<status_field_id>": { "name": "<new status value>" } }
```

**Option B: REST API fallback**

If MCP tools fail to load, use the Airtable REST API directly. The API key is in `config/api-keys.json` under `"airtable"`.

Search across all email-type fields using an OR formula. Airtable tables may store the guest's email in any of several fields (`Direct Email`, `Team Emails`, `General (third)`, `Email`, etc.), so cast a wide net:

```python
python3 -c "
import json, urllib.request, urllib.parse

with open('config/api-keys.json') as f:
    key = json.load(f)['airtable']

base_id = '<base>'
table_id = '<table>'
email = '<guest email>'.lower()

# Search across all common email fields plus name
formula = urllib.parse.quote(
    \"OR(\"
    \"FIND('\" + email + \"', LOWER({Direct Email})),\"
    \"FIND('\" + email + \"', LOWER({Team Emails})),\"
    \"FIND('\" + email + \"', LOWER({General (third)})),\"
    \"FIND('\" + email + \"', LOWER({Email}))\"
    \")\"
)
url = f'https://api.airtable.com/v0/{base_id}/{table_id}?filterByFormula={formula}'
req = urllib.request.Request(url)
req.add_header('Authorization', f'Bearer {key}')
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())
print(json.dumps(data, indent=2))
"
```

If no match on email fields, fall back to a name search using the guest's name from the email thread:
```python
formula = urllib.parse.quote("FIND('<guest first name lower>', LOWER({Name}))")
```

To update via REST API:
```python
python3 -c "
import json, urllib.request

with open('config/api-keys.json') as f:
    key = json.load(f)['airtable']

url = 'https://api.airtable.com/v0/<base>/<table>/<record_id>'
payload = json.dumps({'fields': {'<status_field_id>': {'name': '<new status value>'}}}).encode()
req = urllib.request.Request(url, data=payload, method='PATCH')
req.add_header('Authorization', f'Bearer {key}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req, timeout=15) as resp:
    print(json.loads(resp.read().decode()))
"
```

**Status values by show:**

| Show | New Status Value | Status Field ID |
|---|---|---|
| FTT | "Interested" | `fldd2ZMHVcs8tsQcl` |
| STW | "In Progress" | `fld86R8OzKDoBuZlC` |
| HYM | "In Progress" | `fldnF236htySErV2o` |
| JH | "Warm (in convo)" | `fld86R8OzKDoBuZlC` |

If no matching record is found after both email and name searches, skip the update silently and note it in the Slack confirmation. Do not create new records.

### Step 4: Draft the Reply

Using the team member's notes as direction, draft a professional email reply.

**Voice guidelines (from Nalu copywriting bible):**
- Conversational, not corporate. Write how people talk. First person, contractions.
- Direct, not motivational. State plainly, no fluff.
- Specific, not vague. Reference real details from the conversation.
- Keep it concise. Guest outreach replies should be short and action-oriented.
- Warm but professional. These are potential podcast guests, treat them as peers.
- No em dashes. Use colons, commas, or periods instead.
- No staccato fragments. Combine short sentences into proper ones.

**Reply conventions:**
- Open with their name (e.g., "Hi Latt,")
- Address their question or point directly
- If confirming logistics: be specific about dates, times, and next steps
- If following up: reference something specific from their reply
- Close with a clear next action or question
- Sign off as the person who sent the original outreach (check the `eaccount` or original email context)
- Keep replies under 150 words unless the situation demands more

### Step 5: Send the Reply

Run:
```
python3 tools/instantly.py send-reply \
  --reply-to "<INSTANTLY EMAIL ID>" \
  --eaccount "<eaccount from get-email>" \
  --subject "Re: <original subject>" \
  --body "<drafted reply text>"
```

### Step 6: Post Confirmation to Slack

Post the sent reply back to the Slack thread so the team can see exactly what was sent. If an Airtable update was made in Step 3, append a line confirming it (e.g., `Airtable: Updated <guest name> to "<status>" in <show name>`). If no update was made, don't mention Airtable at all.

```
python3 tools/slack.py reply \
  --channel "<SLACK CHANNEL>" \
  --thread-ts "<SLACK THREAD TS>" \
  --text "Reply sent to <recipient email>:\n\n<the drafted reply text>"
```

## Error Handling

- If `get-email` fails: post error to Slack thread, do not attempt to send
- If `send-reply` fails: post the drafted reply to Slack thread with the error so the team can take manual action
- If the email ID is missing or invalid: post to Slack thread explaining the issue

## Notes

- The `eaccount` (sending email account) comes from the `get-email` response, not from the notification
- Always preserve the original subject line with "Re: " prefix
- Never fabricate details. If the team notes are unclear, draft the best reply possible and flag any assumptions in the Slack confirmation
- Never include an email signature. No name block, no title, no company info. Just the body text and a first-name sign-off at most.
- This skill is spawned by `slack-listener.py`, not invoked interactively
