---
name: FTT Airtable empty status
description: FTT guest records must have empty status field, not "For Review"
type: feedback
---

When writing guest candidates to the FTT Airtable, leave the status field empty (do not set it). Other shows use "For Review" as default status, but FTT does not. The FTT view filters by empty status, so setting "For Review" hides records from the team's working view.

**Why:** The FTT Airtable view groups by status, and new candidates sit in the "(Empty)" group. Setting "For Review" moved them into a collapsed group the team doesn't check.

**How to apply:** When writing to FTT's Airtable (base appiowT0T5O07BfYB, table tbltDNojUS6gREZ2E), omit the status field (fldd2ZMHVcs8tsQcl) entirely. Update the config default if needed.