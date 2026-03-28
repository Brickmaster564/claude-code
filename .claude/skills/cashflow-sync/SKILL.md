---
name: cashflow-sync
description: Use when someone asks to sync the cashflow sheet, run the cashflow sync, update operational expenses, or refresh the cashflow from Revolut.
disable-model-invocation: true
---

## What This Skill Does

Syncs the operational expenses section of the Nalu cashflow master sheet against live Revolut card payments. Runs automatically biweekly on Sundays, or manually on demand.

**Two behaviours:**

1. **Existing rows** — for every subscription already in the sheet, pull the Revolut total for that merchant in the current month. If the sheet value differs (e.g. additional Meta charges mid-month), overwrite with the correct total.

2. **New rows** — for Revolut card payments not matched to any existing sheet row (and not in the skip list), insert a new row above the General section, add the merchant name, and populate the month amount.

## Sources of Truth

- **Revolut**: `tools/revolut.py transactions` (card payments only, current month)
- **Sheet**: `https://docs.google.com/spreadsheets/d/1JGkLHMHdur-faQysThO1cvTa4SbtT7dYojPbBLtsq9o` — tab `2026`, operational expenses section (Subscriptions + General rows)

## How to Run

```bash
# Current month
python3 tools/cashflow_sync.py

# Specific month
python3 tools/cashflow_sync.py --month 2026-03

# Preview without writing
python3 tools/cashflow_sync.py --dry-run
```

## Schedule

Runs biweekly — every other Sunday at 10:00 AM via CC Desktop scheduler.
Cron script: `.claude/cron-cashflow-sync.sh`

## Output

- Sheet updated in place (existing rows overwritten, new rows inserted above General section)
- Slack summary to #nalu-hub with what changed (updated rows with before/after, new rows added)

## Logic Details

### Matching

Merchant names from Revolut are normalized and matched to sheet row labels via:
1. Alias table (e.g. `apollo.io` → `apollo`, `meta pay` → `meta`, `openai` → `gpt`)
2. Fuzzy contains-match on normalized strings
3. Google Workspace: all variants (Nalup, Upio, Vidac) consolidated into one total

### Skip List

The following are ignored (not subscriptions):
- Bank transfers (`To X` payments)
- Food, travel, hotels, taxis
- Government / tax payments
- Payment processors (Payoneer, Wise)
- Freelancer ad-hoc payments
- Ad spend (Uproas, Meta — Meta ad spend is tracked separately as "Meta")

### New Row Behaviour

New rows are inserted above the "General" sub-section header (dynamically found each run, so row numbers shifting doesn't break anything). Blue-light background formatting is applied automatically.

### Idempotent

Running the script twice on the same data is safe — it overwrites with the same values, inserts no duplicates.

## Dependencies

- `tools/revolut.py` (Revolut Business API)
- `tools/slack.py` (Slack notification)
- `config/google-token-nalu.json` + `config/google-credentials-nalu.json`
- `config/revolut-token.json` + `config/revolut_private.pem`