---
name: outreach-retarget
description: Use when someone asks to retarget completed outreach guests, run outreach retarget, update completed campaign contacts in Airtable, or check which podcast outreach leads never responded.
argument-hint: client name (ftt, jh, stw, or all)
disable-model-invocation: true
---

## What This Skill Does

Scans Instantly outreach campaigns for podcast clients, identifies contacts who completed the sequence without responding, matches them to their Airtable guest tracker records, and updates those records to move them into a retargeting pool. Posts a summary to Slack.

Runs as a weekly Sunday cron or manually via `/outreach-retarget [client]`.

## Config

Read config from `.claude/skills/outreach-retarget/config.json`. Each client entry contains:
- `instantly_campaign_id` -- the Instantly campaign to scan
- `airtable_base_id` / `airtable_table_id` -- the guest tracker table
- `airtable_fields` -- field IDs for name, status, location, profile
- `retarget_values` -- the exact values to set for location and status

## Steps

### 1. Parse Input

Parse `` to determine which client(s) to process.
- `ftt`, `jh`, `stw` -- run for that client only
- `all` or no argument -- run for all configured clients sequentially
- If the client key doesn't exist in config, report the error and stop.

### 2. Pull Completed Leads from Instantly

For each client, run:

```bash
python3 tools/instantly.py list-leads --campaign-id "<campaign_id>" --status completed --limit 5000
```

This returns contacts with status code 3 and email_reply_count == 0 (completed sequence, never replied).

If the result contains an error or zero leads, log it and skip to the next client. Do NOT proceed with an empty list.

### 3. Pull All Records from Airtable

Use the Airtable MCP to list all records from the client's guest tracker table:

- `baseId`: from config
- `tableId`: from config
- Fetch fields: name, status, location, profile (use field IDs from config)
- Paginate to get ALL records (don't stop at first page)

### 4. Match Instantly Leads to Airtable Records

For each completed Instantly lead, try to find a matching Airtable record:

1. **Email match (exact):** Check if the lead's email appears in any Airtable record's profile field (which contains URLs/contact info). This is the strongest signal.
2. **Name match (fuzzy):** Compare the lead's `first_name + last_name` against Airtable record names. Use case-insensitive comparison. Allow for:
   - Exact match: "John Smith" == "John Smith"
   - First name + last initial: "John S" matches "John Smith"
   - Reversed order: "Smith John" matches "John Smith"
   - Partial: if the Instantly lead name is a substring of the Airtable name (or vice versa), flag as probable match

If no match is found, add the lead to an "unmatched" list for the summary.

### 5. Filter Already-Retargeted Records

Before updating, check the current values of matched Airtable records:
- If a record's location already equals the retarget location value AND status already matches the retarget status value (or both are empty/null), skip it (already processed in a previous run).
- Only update records that haven't been retargeted yet.

### 6. Update Matched Records in Airtable

For each matched (and not already retargeted) record, update the Airtable record:

- Set `location` field to the `retarget_values.location` from config
- Set `status` field to the `retarget_values.status` from config. If the value is an empty string `""`, clear the status field by setting it to `null` (this removes the current status value in Airtable).

Use the Airtable MCP `update_records_for_table`. Batch updates in groups of 10 (Airtable's batch limit).

### 7. Post Slack Summary

Send a summary message to the configured Slack channel (#guest-research-and-comms):

```bash
python3 tools/slack.py send --channel "<channel_id>" --text "<summary>"
```

Summary format:

```
Outreach Retarget -- [Client Name] ([date])

Instantly campaign scanned: [campaign_id]
Total completed (no reply): [count]
Matched to Airtable: [count]
Already retargeted (skipped): [count]
Updated this run: [count]
Unmatched leads: [count]

[If unmatched > 0:]
Unmatched leads (not found in Airtable):
- [first_name] [last_name] ([email])
- ...
```

### 8. Save Output Log

Write results to `output/outreach-retarget/YYYY-MM-DD-[client].json`:

```json
{
  "client": "ftt",
  "date": "2026-03-08",
  "instantly_campaign_id": "...",
  "total_completed": 42,
  "matched": 35,
  "already_retargeted": 5,
  "updated": 30,
  "unmatched": 7,
  "updated_records": [
    {"airtable_id": "rec...", "name": "...", "matched_via": "email|name"}
  ],
  "unmatched_leads": [
    {"email": "...", "first_name": "...", "last_name": "..."}
  ]
}
```

Create the output directory if it doesn't exist.

## Notes

- This skill has side effects (Airtable writes, Slack messages). That's why `disable-model-invocation` is true.
- **Instantly API quirk:** The v2 API uses the field `campaign` (not `campaign_id`) in POST /leads/list. The tool (`tools/instantly.py`) already handles this correctly.
- The Instantly `list-leads` tool does client-side filtering. Status "completed" = status code 3 + reply count 0.
- **Location is a multi-select field** in the FTT Airtable. Pass the value as an array: `["General / Retargeting"]`, not a plain string.
- **"you" entries:** Some Instantly leads have first_name set to "you" (generic). Skip these during matching. Log them in the output for manual review.
- Airtable batch updates are limited to 10 records per call. Chunk accordingly.
- If running for "all" clients, process them sequentially and post a separate Slack summary per client.
- Do NOT delete or modify any Instantly data. This is read-only on the Instantly side.
- If the Airtable MCP is unavailable, report the error clearly and stop. Do not fall back to API calls.
