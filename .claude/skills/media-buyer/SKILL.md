---
name: media-buyer
description: Use when someone asks to check ad performance, run a media buyer report, review Meta campaigns, upload creatives to ads manager, create Meta campaigns, optimize ad spend, generate a daily ad briefing, bulk upload ads, or manage Meta ad accounts.
disable-model-invocation: true
argument-hint: [account ID, vertical, or command]
---

## What This Skill Does

Meta Ads media buyer co-pilot. Three pillars:

1. **Reporting** -- Pull live data from Meta Marketing API, analyze performance, generate a visual PDF report, and email it. Your pre-session briefing before opening Ads Manager.
2. **Operations** -- Create campaigns, ad sets, and ads. Bulk upload creatives with copy. Manage status (pause, activate, archive).
3. **Optimization** -- Analyze campaigns against performance rules and suggest cut/scale/hold decisions, budget shifts, and creative rotations.

## Context Loading

Always load these before any action:
- `resources/paid-advertising/meta-campaign-playbook.md` (scaling rules, neutral buffer, creative rotation, submission timing)
- `resources/paid-advertising/meta-advertising-handbook.md` (infrastructure architecture, account warming, agency accounts)
- `.claude/skills/media-buyer/report-template.md` (decision rules, CPL targets, verdict logic)
- Load the relevant vertical resources from `resources/client-network/{vertical}/` if the vertical is known

## Setup

If `meta_access_token` is not in `config/api-keys.json`, direct the user to `.claude/skills/media-buyer/meta-api-setup.md` for the one-time setup process.

---

## Pillar 1: Daily Report

Fire-and-forget mode. User asks for a report, skill generates and emails it.

### Steps

1. Get the ad account ID from the user (or from `$ARGUMENTS`). Format: `act_XXXXXXXXX`
2. Ask which vertical this is for (to set CPL targets). If unknown, use a general $20 CPL target.
3. Pull data by running these commands via `tools/meta_ads.py`:
   ```
   python3 tools/meta_ads.py --account-id {ID} account-overview --days 7
   python3 tools/meta_ads.py --account-id {ID} campaign-insights --days 7
   python3 tools/meta_ads.py --account-id {ID} ad-insights --days 7
   python3 tools/meta_ads.py --account-id {ID} daily-breakdown --days 7
   ```
4. For the top 5 campaigns by spend, pull creative details:
   ```
   python3 tools/meta_ads.py --account-id {ID} creative-performance --campaign-id {CAMP_ID} --days 7
   ```
5. Analyze the data. Apply verdict rules from `report-template.md`:
   - **SCALE:** CPL below target AND spend > $20 AND frequency < 3
   - **HOLD:** CPL within 20% of target OR insufficient data (< $10 spend)
   - **CUT:** CPL > 2x target OR frequency > 5 OR CTR < 0.5%
6. Write the recommendations text block with specific actions:
   - Which campaigns/ads to scale (with suggested new budget)
   - Which to cut (with reasoning)
   - Which creatives show fatigue (frequency > 3 = WARNING, > 5 = CRITICAL)
   - Budget reallocation suggestions
7. Assemble the report data JSON and write to `.tmp/report-data.json`
8. Generate the PDF:
   ```
   python3 tools/meta_report.py generate --data-file .tmp/report-data.json --output output/media-buyer/YYYY-MM-DD.pdf --email jasperkilic10@gmail.com
   ```
9. Confirm to the user: report generated and emailed.

### CPL Targets

| Vertical | Target | Scale Below | Cut Above |
|---|---|---|---|
| Life Insurance | $20 | $16 | $40 |
| Senior Care | $16 | $13 | $32 |
| Home Security | $12 | $10 | $24 |
| Tax Relief | $14 | $11 | $28 |
| Gold IRA | $28 | $22 | $56 |

---

## Pillar 2: Operations

Conversational mode. Always confirm before executing write operations.

### Upload Creatives to Existing Campaign

1. User provides: image files (paths), ad copy (primary text, headline, description, CTA), target ad set ID, Facebook Page ID
2. Show the user a summary of what will be created. Wait for confirmation.
3. Upload images:
   ```
   python3 tools/meta_ads.py --account-id {ID} upload-image --path {IMAGE_PATH}
   ```
   Or bulk:
   ```
   python3 tools/meta_ads.py --account-id {ID} bulk-upload --paths '["{path1}","{path2}"]'
   ```
4. Create creatives:
   ```
   python3 tools/meta_ads.py --account-id {ID} create-creative --image-hash {HASH} --body "{PRIMARY_TEXT}" --title "{HEADLINE}" --link "{URL}" --page-id {PAGE_ID} --cta {CTA_TYPE}
   ```
5. Create ads (PAUSED):
   ```
   python3 tools/meta_ads.py --account-id {ID} create-ad --adset-id {ADSET_ID} --creative-id {CREATIVE_ID} --name "{AD_NAME}"
   ```
6. Report back: "Created X ads in PAUSED state. Activate when ready."
7. If user confirms activation:
   ```
   python3 tools/meta_ads.py --account-id {ID} update-status --object-type ad --object-id {AD_ID} --status ACTIVE
   ```

### Create New Campaign

1. User provides: vertical, campaign name, objective (default OUTCOME_LEADS), daily budget, targeting details, images, copy
2. Present the full campaign plan for confirmation:
   - Campaign: name, objective, budget
   - Ad set: targeting, optimization goal
   - Ads: creative details
3. After confirmation, execute in order:
   ```
   create-campaign > create-adset > upload-image(s) > create-creative(s) > create-ad(s)
   ```
4. All created in PAUSED state. Report the IDs back.
5. **Neutral buffer reminder:** If the campaign contains aggressive creatives (direct response, urgency), remind the user of the 4:1 neutral buffer rule from the campaign playbook. Offer to create neutral placeholder ads alongside.

### Status Management

Update campaign, ad set, or ad status:
```
python3 tools/meta_ads.py --account-id {ID} update-status --object-type {TYPE} --object-id {OBJ_ID} --status {ACTIVE|PAUSED|ARCHIVED}
```

---

## Pillar 3: Optimization

Conversational mode. Pull fresh data or reference the latest report.

### Steps

1. Pull current performance data (same as report steps 3-4)
2. Apply campaign playbook rules:
   - **Scaling:** Max 20-30% budget increase per change. Start at $49/day, move to $99 after 48h stable, then split across accounts.
   - **Creative rotation:** Rotate one element every 3-5 days. Maintain minimum 20 creatives in library.
   - **Budget reallocation:** Move spend from CUT campaigns to SCALE campaigns.
   - **Frequency watch:** Any ad above 3.0 frequency needs a replacement creative planned. Above 5.0 = replace immediately.
3. Present specific, actionable recommendations with numbers:
   - "Increase Campaign X budget from $49 to $59 (+20%). CPL $14.50 vs $20 target, frequency 1.8."
   - "Pause Ad Y. CPL $45 (2.25x target), frequency 5.2 (CRITICAL). Replace with new creative."
   - "Reallocate $30/day from Campaign Z to Campaign X."
4. If user agrees, execute the changes via `update-status` and note what was changed.

---

## Guardrails

- **NEVER activate** campaigns, ad sets, or ads without explicit user confirmation
- **NEVER increase budget** by more than 30% in a single change (per campaign playbook)
- **NEVER appeal** rejected ads. Duplicate with changes instead (per campaign playbook)
- **Always create** campaigns and ads in PAUSED state
- **Warn on restricted verticals:** Life insurance and gold IRA are restricted categories on Meta. Flag compliance requirements when creating campaigns for these verticals.
- **Confirm before write operations:** Any action that creates, modifies, or deletes objects in Ads Manager requires user confirmation first
- **Cost awareness:** Creating campaigns/ads is free, but activating them costs money. Always make this clear.

## Notes

- All monetary values in `meta_ads.py` are in cents (e.g., 4900 = $49.00)
- The tool outputs JSON to stdout. Parse it to extract the data you need.
- For the report, you assemble the `report-data.json` file from multiple tool calls. The report tool just renders what you give it.
- If the API returns a token expiry error (code 190), tell the user to regenerate their token following `meta-api-setup.md`.
- This skill works with ANY Meta ad account. The user passes the account ID each time, or you can ask for it.
