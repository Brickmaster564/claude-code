---
name: Lemlist update requires campaign-specific endpoint
description: PATCH /leads/{email} silently ignores companyName updates. Must use PATCH /campaigns/{id}/leads/{email} instead.
type: feedback
---

The generic `PATCH /leads/{email}` endpoint returns `{"status": "ok"}` but silently ignores field updates like companyName. It looks like it succeeded but changes nothing.

The correct endpoint for updating lead fields (especially companyName) is `PATCH /campaigns/{campaignId}/leads/{email}`. This returns the full updated lead object as confirmation.

**Why:** First batch fix attempt "succeeded" (1124 reported ok) but zero company names actually changed. Wasted an entire run and hit rate limits before discovering the issue.

**How to apply:** Always use `update_lead(api_key, email, updates, campaign_id=campaign_id)` when updating leads. The `batch-update` command in lemlist.py now requires `campaign_id` in each plan entry. The `update-lead` CLI also accepts `--campaign-id`.