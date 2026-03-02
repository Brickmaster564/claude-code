# Prospector Workflow

End-to-end pipeline: find decision-makers in Apollo, verify their emails, and load verified leads into an Instantly campaign.

## Input

The user triggers this workflow with a message like:

> Find me 20 leads for tax debt, US, 50-500 employees. List: US - Tax Debt - 25/02. Instantly campaign: Lead Gen - Tax Debt - US

**Required inputs (can be given in any order):**
- **Vertical/industry** — the lead gen vertical (e.g. life-insurance, tax-relief, senior-care, home-security)
- **Location** — country/region (e.g. US, UK, Australia, Canada)
- **Lead count** — how many prospects to find
- **Apollo list name** — the Apollo list/label to add contacts to
- **Company size** — employee count range (minimum 10 employees, always)
- **Instantly campaign name** — the Instantly campaign to load verified leads into

If any input is missing, ask before proceeding.

---

## Working Data File

All prospect data MUST be written to `.tmp/prospector-run.json` and kept updated after every step. This ensures the pipeline can survive context compaction without losing progress.

**File structure:**
```json
{
  "inputs": {
    "vertical": "",
    "location": "",
    "lead_count": 0,
    "apollo_list": "",
    "company_size": "",
    "instantly_campaign": ""
  },
  "current_step": 1,
  "prospects": [
    {
      "name": "",
      "first_name": "",
      "title": "",
      "company": "",
      "email": "",
      "apollo_id": "",
      "status": "found|enriched|no_email|duplicate|created|good|risky|bad|recovered|loaded"
    }
  ],
  "stats": {
    "found": 0,
    "enriched": 0,
    "duplicates_skipped": 0,
    "contacts_created": 0,
    "emails_good": 0,
    "emails_risky": 0,
    "emails_bad": 0,
    "emails_recovered": 0,
    "loaded_to_instantly": 0
  }
}
```

**Rules:**
- Create this file at the start of Step 1 with the user's inputs.
- Update it after each step completes (update `current_step`, prospect statuses, and stats).
- If context has been compacted, read this file first to recover state before continuing.
- Delete the file after Step 8 (final report).

---

## Target Roles (Universal — Same Across All Verticals)

These are the decision-maker roles we always target. Do not deviate from these unless Jasper explicitly overrides.

**Primary — Marketing:**
- Head of Marketing
- Marketing Director
- Marketing Manager
- VP of Marketing
- Chief Marketing Officer (CMO)

**Primary — Partnerships:**
- Head of Partnerships
- Strategic Partnerships Manager
- Partnership Director
- VP of Partnerships

**Primary — Business Development:**
- Head of Business Development
- Business Development Director
- Business Development Manager
- VP of Business Development

**Secondary — Operations:**
- Head of Operations
- Director of Operations
- VP of Operations
- Chief Operating Officer (COO)

When searching Apollo, combine these titles with the vertical's industry filters. Cast a wide net across all role groups to hit the lead count.

---

## Steps

### Step 1 — Apollo Search (MCP)

Use `apollo_mixed_people_api_search` to find prospects matching:
- **Titles:** all roles listed above (search multiple batches if needed to cover all role groups)
- **Industry + Keywords:** use the industry as the broad filter, then layer in specific keywords to narrow results to the right niche (see Vertical Search Config below)
- **Location:** as specified by Jasper (person location, not company HQ)
- **Company size:** as specified by Jasper (never less than 10 employees — hard floor)
- **Seniority:** director, vp, c_suite, owner, founder, manager

Collect results until you have enough unique prospects to meet the requested lead count. If a single search doesn't return enough, run additional searches varying the title keywords or broadening keyword combinations.

**After searching:** Create `.tmp/prospector-run.json` with all found prospects. Extract only the fields we need (name, first_name, title, company, email, apollo_id). Do NOT store full Apollo response objects — keep it lean.

**Vertical Search Config:**

Keywords are critical for result quality. The industry is the broad bucket; the keywords narrow it down to the specific niche. Always use multiple keywords per search to maximise coverage.

| Vertical | Industry | Keywords |
|---|---|---|
| life-insurance | insurance, financial services | life insurance, final expense, term life insurance, term life, whole life, universal life, burial insurance, mortgage protection |
| tax-relief | tax services, accounting, financial services | tax debt, tax relief, tax resolution, tax settlement, IRS debt, back taxes, offer in compromise, tax lien, penalty abatement, enrolled agent |
| senior-care | home health care, elder care, healthcare | senior care, home care, elder care, assisted living, memory care, in-home care, senior living, aging in place, companion care, dementia care |
| home-security | security, home security | home security, alarm systems, security monitoring, home automation, smart home security, surveillance, burglar alarm, access control |

**Keyword inference rule:** If Jasper asks for a vertical or niche not in the table above, determine the best keywords by thinking about:
1. What does this company actually sell or do?
2. What terms would appear on their website or in their employees' job titles?
3. What would a buyer in this space search for?

Use 5-10 specific keywords. Avoid generic terms that would pull in unrelated companies. When in doubt, ask Jasper to confirm the keywords before searching.

### Step 2 — Apollo Enrich (MCP)

For prospects that don't have email addresses from the search results:
- Use `apollo_people_bulk_match` for batches (preferred — fewer API calls, less context used)
- Fall back to `apollo_people_match` individually only if bulk fails

After enrichment, update `.tmp/prospector-run.json`:
- Set status to `enriched` for prospects that now have emails
- Set status to `no_email` for prospects that still don't
- Filter out `no_email` prospects from the active pipeline

Report how many were enriched vs dropped.

### Step 3 — Dedup Check (MCP)

Before creating any contacts, check each prospect against existing Apollo contacts:
1. For each prospect, search `apollo_contacts_search` using their email address
2. If a match is found, mark as `duplicate` in the working file — they're already in the system
3. If skipped, find a replacement to maintain the requested lead count

Update `.tmp/prospector-run.json` with dedup results.

Report: "{X} duplicates found and skipped, {X} replacements sourced"

### Step 4 — Apollo Create Contacts + Add to List (MCP)

For each prospect that passed the dedup check:
1. Use `apollo_contacts_create` to create the contact in Apollo
2. Include the label/list ID for the specified Apollo list

If the list label ID isn't known, search existing contacts in that list to discover it, or ask Jasper.

**Known list label IDs:**
| List Name | Label ID |
|---|---|
| US - Tax Debt - 25/02 | 699f28b1debd6d0021a38df2 |

Update this table as new lists are discovered.

Update `.tmp/prospector-run.json` — set status to `created` for each successful contact.

Report: "{X} contacts created and added to {list name}"

### Step 5 — MillionVerifier Email Verification (API)

Run the MillionVerifier tool script to verify all emails:

```bash
python3 tools/millionverifier.py --emails "email1@co.com,email2@co.com,..."
```

The script returns a JSON result categorising each email as `good`, `risky`, or `bad`.

- **good** → these go straight to Instantly (Step 7)
- **risky** → these go to BounceBan (Step 6)
- **bad** → discard, report as undeliverable

Update `.tmp/prospector-run.json` with verification results for each prospect.

### Step 6 — BounceBan Risky Email Verification (API)

Send only the `risky` emails from Step 5 to BounceBan:

```bash
python3 tools/bounceban.py --emails "risky1@co.com,risky2@co.com,..."
```

The script returns results categorised as `deliverable`, `risky`, `undeliverable`, or `unknown`.

- **deliverable** → mark as `recovered`, add to Instantly (Step 7)
- Everything else → discard, report as undeliverable

Update `.tmp/prospector-run.json` with BounceBan results.

### Step 7 — Add Leads to Instantly Campaign (API)

First, find the campaign by name:

```bash
python3 tools/instantly.py list-campaigns --search "campaign name from input"
```

This returns matching campaigns with their IDs. Fuzzy match the user's input to the closest campaign name. If ambiguous, confirm with Jasper.

Then add all verified leads (those with status `good` or `recovered`):

```bash
python3 tools/instantly.py add-leads --campaign-id "CAMPAIGN_ID" --leads '[{"email":"...","first_name":"...","company_name":"..."},...]'
```

Fields mapped: `first_name`, `email`, `company_name`.

Update `.tmp/prospector-run.json` — set status to `loaded` for each lead successfully added.

### Step 8 — Report

Read `.tmp/prospector-run.json` to compile the final summary, then present in chat:

```
PROSPECTOR COMPLETE
═══════════════════

Vertical:    {vertical}
Apollo List: {list name}
Campaign:    {instantly campaign name}

Found:       {X} prospects
Enriched:    {X} with emails
Verified:    {X} good + {X} recovered from risky
Discarded:   {X} bad/undeliverable
Loaded:      {X} leads into Instantly

LEADS ADDED:
| Name | Title | Company | Email | Status |
|------|-------|---------|-------|--------|
| ...  | ...   | ...     | ...   | good   |
| ...  | ...   | ...     | ...   | recovered |
```

After presenting the report, delete `.tmp/prospector-run.json`.

---

## Error Handling

- **Apollo search returns too few results:** Broaden title keywords, try related industries, or report the shortfall and ask Jasper if he wants to proceed with fewer.
- **Enrichment yields no email:** Drop the prospect, count in the "discarded" tally.
- **MillionVerifier or BounceBan API errors:** Report the error, retry once. If still failing, pause and ask Jasper.
- **Instantly campaign not found:** Show available campaigns and ask Jasper to pick.
- **Rate limits hit:** Back off and retry with a short delay.
- **Context compacted mid-run:** Read `.tmp/prospector-run.json` to recover state. Check `current_step` and resume from where it left off.

## Notes

- Apollo enrichment uses credits. The workflow will always proceed with enrichment since it's required for email verification. If Jasper wants to skip enrichment for any reason, he'll say so.
- All API keys are loaded from `config/api-keys.json` by the tool scripts.
- This workflow does NOT write outreach copy. That's a separate task — use `/copywriter` for sequence messaging.
