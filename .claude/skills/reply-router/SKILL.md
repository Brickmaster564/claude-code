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
4. Claude drafts a professional reply using the team's notes and Nalu brand voice
5. Claude sends the reply via Instantly API
6. Claude posts confirmation back to the Slack thread

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
- `eaccount` - the Instantly sending account (needed for replying)
- `subject` - the email subject
- `body` - the full email body (text and HTML)
- `thread_id` - the email thread

### Step 3: Draft the Reply

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

### Step 4: Send the Reply

Run:
```
python3 tools/instantly.py send-reply \
  --reply-to "<INSTANTLY EMAIL ID>" \
  --eaccount "<eaccount from get-email>" \
  --subject "Re: <original subject>" \
  --body "<drafted reply text>"
```

### Step 5: Post Confirmation to Slack

Post the sent reply back to the Slack thread so the team can see exactly what was sent:

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
