# Lead Replenish Outbound Workflow

Automated weekly pipeline with two modes:

1. **Replenish mode** (default): Scan Instantly campaigns for completed leads, identify their companies, find fresh contacts at those same companies via Apollo.
2. **Fresh prospect mode** (fallback): If no completed leads exist, source entirely new leads from new companies using industry/keyword search in Apollo. Same as the prospector workflow's search logic.

Both modes then verify emails, check LinkedIn activity (posts AND comments), load into Instantly, and route active LinkedIn users to Lemlist.

## Input

This workflow is triggered by a cron job or manual invocation specifying a vertical:

> Run replenisher for life-insurance

**Required input:**
- **Vertical name** — must match a key in `config/replenisher.json`

The config file contains everything else (campaign IDs, Apollo lists, Lemlist campaign ID). If the vertical isn't in the config, stop and ask Jasper to add it.

---

## Config File

`config/replenisher.json` maps each vertical to its campaign details:

```json
{
  "life-insurance": {
    "instantly_campaign_id": "...",
    "lemlist_campaigns": { "US": "...", "UK": "...", "CA": "...", "AU": "..." },
    "max_leads_per_run": 150,
    "max_per_company": 4
  },
  "home-security": {
    "instantly_campaign_id": "...",
    "lemlist_campaign_id": "...",
    "max_leads_per_run": 150,
    "max_per_company": 4
  },
  "senior-care": {
    "instantly_campaign_id": "...",
    "lemlist_campaign_id": "...",
    "max_leads_per_run": 150,
    "max_per_company": 4
  }
}
```

**Lemlist routing:**
- Most verticals use a single `lemlist_campaign_id`.
- **Life Insurance** uses `lemlist_campaigns` (geo-keyed object) because each geography has its own Lemlist campaign. The lead's country from Apollo determines which campaign they're routed to.

Jasper will populate campaign IDs as verticals go live.

---

## Working Data File

All data MUST be written to `.tmp/replenisher-run.json` and kept updated throughout the run. Same rationale as the prospector workflow: survives context compaction.

**File structure:**
```json
{
  "vertical": "",
  "mode": "replenish|fresh_prospect",
  "config": {},
  "current_step": 1,
  "step_status": "in_progress",
  "completed_leads": [],
  "replied_companies": [],
  "target_companies": [],
  "new_prospects": [],
  "stats": {
    "completed_scanned": 0,
    "replied_companies_excluded": 0,
    "target_companies": 0,
    "prospects_found": 0,
    "emails_good": 0,
    "emails_risky": 0,
    "emails_bad": 0,
    "emails_recovered": 0,
    "loaded_to_instantly": 0,
    "loaded_to_lemlist": 0,
    "linkedin_active_posters": 0,
    "linkedin_active_commenters": 0,
    "linkedin_inactive": 0,
    "linkedin_no_profile": 0
  }
}
```

**Rules:**
- Create this file at the start of Step 1.
- Write after every individual operation.
- Follow the same compaction recovery procedure as the prospector workflow: read the file, check `current_step` and `step_status`, resume from where you left off.

---

## Target Roles

Same as the prospector workflow. Search order matters: exhaust Primary before falling back to Secondary.

**Primary -- Marketing (search first):**
- Head of Marketing
- Marketing Director
- Marketing Manager
- VP of Marketing
- Chief Marketing Officer (CMO)

**Primary -- Partnerships:**
- Head of Partnerships
- Strategic Partnerships Manager
- Partnership Director
- VP of Partnerships

**Primary -- Business Development:**
- Head of Business Development
- Business Development Director
- Business Development Manager
- VP of Business Development

**Secondary -- Operations + Sales (fallback only):**
- Head of Operations
- Director of Operations
- VP of Operations
- Chief Operating Officer (COO)
- Head of Sales
- Sales Director
- VP of Sales

**Excluded titles (never add these):**
- Chief of People Operations
- Any HR/People Operations role

---

## Steps

### Steps 1-3 -- Scan Campaign + Decide Mode

**Step 1:** Pull all leads from the Instantly campaign with status "completed" (finished the sequence without replying):

```bash
python3 tools/instantly.py list-leads --campaign-id "CAMPAIGN_ID" --status "completed"
```

**Step 2:** Pull all leads with status "replied":

```bash
python3 tools/instantly.py list-leads --campaign-id "CAMPAIGN_ID" --status "replied"
```

Extract unique company names from replied leads. These companies are excluded from replenishment.

**Step 3 -- Mode decision:**

- If completed leads exist: extract unique company names, remove replied companies. Set `mode: "replenish"`. Proceed to **Step 4A**.
- If NO completed leads exist (campaign is new or leads haven't finished sequences yet): set `mode: "fresh_prospect"`. Proceed to **Step 4B**.

**Write checkpoint:** Save completed leads, replied companies, target companies, and mode to `.tmp/replenisher-run.json`.

---

### Step 4A -- Find New Contacts at Target Companies (Replenish Mode)

For each target company from Step 3, search Apollo for new contacts:

1. Use `apollo_mixed_people_api_search` with:
   - **Company domain** (extract from the existing lead's email) or **company name** as keyword
   - **Titles** from Primary groups first (Marketing, Partnerships, BD)
   - If no Primary results, search **Secondary** titles (Operations, Sales)
   - **Seniority:** director, vp, c_suite, owner, founder, manager

2. **Deduplicate against existing Apollo contacts.** Use `apollo_contacts_search` with the person's email or name + company to check if they already exist as a contact. If they do, skip them.

3. **Cap per company:** max `max_per_company` new contacts per company (default 4).

4. **Cap per run:** stop once you hit `max_leads_per_run` total new prospects (default 150). Target ~100 new leads into Instantly after deduplication.

5. If no contacts are found for a company at all (Primary + Secondary exhausted), skip that company.

**Per-company checkpoint:** After processing each company, write results to the working file.

---

### Step 4B -- Fresh Prospect Search (Fresh Prospect Mode)

When no completed leads exist, source entirely new leads using industry/keyword search. This mirrors the prospector workflow's search logic.

Use `apollo_mixed_people_api_search` with:
- **Titles:** Primary groups first (Marketing, Partnerships, BD), then Secondary if needed
- **Seniority:** director, vp, c_suite, owner, founder, manager
- **Industry + Keywords:** per the vertical search config below
- **Company size:** minimum 10 employees
- **Per page:** `per_page: 10`

**Vertical Search Config:**

| Vertical | Industry | Keywords |
|---|---|---|
| life-insurance | insurance, financial services | life insurance, final expense, term life, whole life, universal life, burial insurance, mortgage protection |
| senior-care | home health care, elder care, healthcare | senior care, home care, elder care, assisted living, memory care, in-home care, senior living, aging in place |
| home-security | security, home security | home security, alarm systems, security monitoring, home automation, smart home security, surveillance, burglar alarm |

**Dedup, caps, and enrichment:** Same rules as Step 4A:
- Deduplicate against existing Apollo contacts
- Max `max_per_company` contacts per company (default 4)
- Stop at `max_leads_per_run` total prospects (default 150)
- Enrich via `apollo_people_bulk_match` to get emails and LinkedIn URLs

**Per-page checkpoint:** After processing each page of results, write to the working file.

### Step 5 -- Email Verification (MillionVerifier)

Run all new prospect emails through MillionVerifier:

```bash
python3 tools/millionverifier.py --emails "email1@co.com,email2@co.com,..."
```

- **good** -> proceed to Step 6
- **risky** -> proceed to Step 5b (BounceBan)
- **bad** -> discard

### Step 5b -- BounceBan Risky Email Verification

Send risky emails to BounceBan:

```bash
python3 tools/bounceban.py --emails "risky1@co.com,risky2@co.com,..."
```

- **deliverable** -> mark as `recovered`, proceed to Step 6
- Everything else -> discard

**Write checkpoint:** Update verification results in the working file.

### Step 6 -- LinkedIn Activity Check (Apify)

Two-pass check for all verified leads (good + recovered) that have a LinkedIn URL from Apollo.

**Pass 1: Profile scraper (posts)**

```bash
python3 tools/apify.py scrape-profiles --urls "https://linkedin.com/in/person1,https://linkedin.com/in/person2,..."
```

Runs `dev_fusion/Linkedin-Profile-Scraper`. If `updates/0/postText` exists and is non-empty, the lead is an **active poster**.

**Pass 2: Comments scraper (engagement)**

For leads that came back with NO recent posts in Pass 1, run the comments scraper:

```bash
python3 tools/apify.py scrape-comments --usernames "person1,person2,..."
```

Runs `apimaestro/linkedin-profile-comments`. Extract the username slug from the LinkedIn URL (the part after `/in/`). The scraper returns all comments the user has made on other people's posts.

**Classification (applied after both passes):**
- **Active poster** = has recent posts from Pass 1 -> route to Lemlist + Instantly
- **Active commenter** = no recent posts, BUT has commented on someone else's post within the last 9 months -> route to Lemlist + Instantly
- **Inactive** = no recent posts AND no comments within 9 months -> route to Instantly only
- **No profile** = no LinkedIn URL from Apollo -> treat as inactive, route to Instantly only

The comments scraper costs ~$0.005 per profile ($5/1000), so running it on all non-posters is negligible.

**Write checkpoint:** Update each prospect with their LinkedIn activity status (`active_poster`, `active_commenter`, or `inactive`).

### Step 7 -- Load into Instantly

Add ALL verified leads (good + recovered) to the Instantly campaign:

```bash
python3 tools/instantly.py add-leads --campaign-id "CAMPAIGN_ID" --leads '[{"email":"...","first_name":"...","company_name":"..."}]'
```

Same batch endpoint as the prospector workflow.

**Write checkpoint:** Update loaded status.

### Step 8 -- Load Active LinkedIn Users into Lemlist

For leads flagged as **active poster** or **active commenter** in Step 6, also add them to the Lemlist campaign.

**Geo-based routing (Life Insurance only):**
If the vertical config has `lemlist_campaigns` (object), use the lead's country from Apollo to pick the correct campaign ID. Map common country values: "United States" -> "US", "United Kingdom" -> "UK", "Canada" -> "CA", "Australia" -> "AU". If the lead's country doesn't match any key, skip Lemlist for that lead and note it in the report.

**Single campaign (all other verticals):**
If the config has `lemlist_campaign_id` (string), use that for all leads.

```bash
python3 tools/lemlist.py add-lead --campaign-id "LEMLIST_CAMPAIGN_ID" --email "..." --first-name "..." --last-name "..." --company "..." --title "..." --linkedin "..."
```

Run this for each active poster. The Lemlist API accepts one lead per call.

If no Lemlist campaign is configured (empty string or missing), skip this step and note it in the report.

**Write checkpoint:** Update Lemlist loaded status.

### Step 9 -- Create Contacts in Apollo + Add to New List (MCP)

For all verified leads that were loaded to Instantly, create them as contacts in Apollo and add to a **new list specific to this run**:

1. Generate the list name: `{Vertical} - Replenish - {DD/MM/YY}` (e.g., "Senior Care - Replenish - 05/03/26")
2. Use `apollo_contacts_create` with `run_dedupe: true`
3. Include `label_names` with the new run-specific list name
4. Apollo auto-creates the list if it doesn't exist
5. This keeps replenished contacts separate from initial prospector batches while still ensuring future runs deduplicate against them

**Per-contact checkpoint:** Write after each create.

### Step 10 -- Report + Slack Notification

Compile the final summary and send to Slack:

```
REPLENISHER COMPLETE
====================

Vertical:         {vertical}
Mode:             {replenish | fresh_prospect}
Campaign:         {instantly campaign name}
Lemlist Campaign: {lemlist campaign name or "N/A"}

Completed Leads Scanned: {X}
Replied Companies Excluded: {X}
Target Companies: {X}

New Prospects Found: {X}
Verified: {X} good + {X} recovered
Discarded: {X} bad/undeliverable

LinkedIn Active Posters: {X} (-> Instantly + Lemlist)
LinkedIn Active Commenters: {X} (-> Instantly + Lemlist)
LinkedIn Inactive: {X} (-> Instantly only)
No LinkedIn: {X} (-> Instantly only)

Loaded to Instantly: {X}
Loaded to Lemlist: {X}
Skipped by Instantly: {X}

LEADS ADDED:
| Name | Title | Company | Email | LinkedIn | Status |
|------|-------|---------|-------|----------|--------|
| ...  | ...   | ...     | ...   | Active   | good   |
```

Send this summary to Slack using the Slack MCP integration, then present it in chat.

After reporting, delete `.tmp/replenisher-run.json`.

---

## Error Handling

- **Instantly returns no completed leads:** Switch to fresh prospect mode (Step 4B). Do NOT stop.
- **No target companies after exclusion (all replied):** Switch to fresh prospect mode (Step 4B). Do NOT stop.
- **Apollo returns no new contacts for a company:** Skip that company, note in the report.
- **Apify profile scraper fails or times out:** Default those leads to "inactive" (Instantly only). Don't block the pipeline.
- **Apify comments scraper fails for a username:** Default that lead to "inactive". Don't block the pipeline.
- **Lemlist campaign ID not set:** Skip Lemlist loading entirely, note in the report.
- **MillionVerifier or BounceBan API errors:** Retry once. If still failing, pause and ask Jasper.
- **Rate limits:** Back off and retry with a short delay.
- **Context compacted mid-run:** Read `.tmp/replenisher-run.json` and resume from the last step.

## Notes

- This workflow is designed to run weekly per vertical via cron job.
- Apollo enrichment credits are consumed during Step 4. The workflow proceeds automatically since finding contacts is the core purpose.
- Apify compute units are consumed during Step 6. Profile scraper + comments scraper combined cost ~$0.05 + $0.005 per lead. At 150 leads, expect ~$8-9 total for LinkedIn checks.
- The Lemlist routing (Step 8) is optional. If no Lemlist campaign is configured, leads still go to Instantly.
- This workflow does NOT write outreach copy. Use `/copywriter` for that.
- All API keys are loaded from `config/api-keys.json` by the tool scripts.
