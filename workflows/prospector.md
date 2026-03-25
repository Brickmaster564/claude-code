# Prospector Workflow

End-to-end pipeline: find decision-makers in Apollo, verify their emails, and load verified leads into an Instantly campaign.

## Input

The user triggers this workflow with a message like:

> Find me 20 leads for tax debt, US, 50-500 employees. List: US - Tax Debt - 25/02. Instantly campaign: Lead Gen - Tax Debt - US

**Required inputs (can be given in any order):**
- **Vertical/industry** — the lead gen vertical (e.g. life-insurance, tax-relief, senior-care, home-security)
- **Location** — country/region (e.g. US, UK, Australia, Canada)
- **Lead count** — how many prospects to find
- **Apollo list name** — auto-generated each run as `{Location} {Vertical} - DD/MM/YY` using today's date (e.g. "UK Life Insurance - 07/03/26"). Do NOT reuse existing lists.
- **Company size** — employee count range (minimum 10 employees, always)
- **Instantly campaign name** — the Instantly campaign to load verified leads into

If any input is missing, ask before proceeding.

---

## Working Data File

All prospect data MUST be written to `.tmp/prospector-run.json` and kept updated throughout the run. This is the single source of truth that survives context compaction.

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
  "discovered": {
    "apollo_list_label_id": "",
    "instantly_campaign_id": "",
    "instantly_campaign_name": "",
    "lemlist_campaign_id": "",
    "lemlist_campaigns": {}
  },
  "current_step": 1,
  "step_status": "in_progress|completed",
  "prospects": [
    {
      "name": "",
      "first_name": "",
      "title": "",
      "company": "",
      "email": "",
      "apollo_id": "",
      "linkedin_url": "",
      "linkedin_status": "active_poster|active_commenter|inactive|no_profile",
      "status": "found|enriched|no_email|duplicate|created|good|risky|bad|recovered|loaded|loaded_lemlist"
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
- Create this file at the start of Step 1 with the user's inputs.
- **Write after every individual operation** — not just after each step. After each Apollo create, each enrichment result, each verification result, update the prospect's status and write the file. This ensures no data is lost if context compacts mid-step.
- Set `step_status` to `"in_progress"` when starting a step, `"completed"` when done.
- Store discovered IDs (Apollo list label ID, Instantly campaign ID) as soon as they're found — these prevent redundant lookups after compaction.
- Delete the file only after Step 9 (final report).

**Compaction recovery procedure:**

When context has been compacted mid-run, the FIRST action must be:

1. Read `.tmp/prospector-run.json`
2. Check `current_step` and `step_status`:
   - If `step_status` is `"completed"` → advance to `current_step + 1`
   - If `step_status` is `"in_progress"` → resume `current_step` (use prospect statuses to skip already-processed leads)
3. Use `discovered` IDs directly — do NOT re-search for campaign or list IDs
4. Use prospect `status` fields to determine which leads still need processing:
   - Step 2: skip prospects already at `enriched` or later
   - Step 3: skip prospects already at `created` or later — `run_dedupe` protects against re-creation
   - Steps 4-5: only verify prospects with status `created` (not yet verified)
   - Step 6: only check LinkedIn for prospects with status `good` or `recovered` that don't have a `linkedin_status` yet
   - Step 7: only load prospects with status `good` or `recovered` that haven't been loaded yet
   - Step 8: only load prospects flagged `active_poster` or `active_commenter` that haven't been loaded to Lemlist yet
5. Resume the pipeline from the determined step

---

## Target Roles (Universal — Same Across All Verticals)

These are the core decision-maker functions we target. **Title matching is fuzzy.** Any title that clearly relates to one of these core functions qualifies, even if the exact wording differs. For example, "Affiliate Marketing Manager", "Growth Marketing Lead", "Partnership Recruiter", "Digital Marketing Specialist", or "Senior Affiliate Manager" all qualify under their respective groups.

**Search order matters.** Always exhaust the three Primary groups first before falling back to Secondary. The goal is to fill lead counts with marketing, partnerships, and BD contacts. Only pull from Secondary (Operations) if Primary groups don't yield enough results for a given company.

**Primary — Marketing (search first):**
- Head of Marketing
- Marketing Director / Marketing Manager
- VP of Marketing
- Chief Marketing Officer (CMO)
- *Also matches:* Affiliate Marketing Manager, Digital Marketing Specialist, Growth Marketing Manager, Content Marketing Manager, Email Marketing Manager, Performance Marketing Manager, and any other title where the core function is marketing

**Primary — Partnerships:**
- Head of Partnerships
- Strategic Partnerships Manager / Partnership Director
- VP of Partnerships
- *Also matches:* Affiliate Manager, Affiliate Partnership Manager, Partnership Recruiter, Channel Partnership Manager, and any other title where the core function is partnerships or affiliate relationships

**Primary — Business Development:**
- Head of Business Development
- Business Development Director / Business Development Manager
- VP of Business Development
- *Also matches:* Growth Manager, Revenue Development Manager, and any other title where the core function is business development

**Secondary — Operations (fallback only):**
- Head of Operations
- Director of Operations
- VP of Operations
- Chief Operating Officer (COO)

**Excluded titles (never add these):**
- Chief of People Operations
- Any HR/People Operations role (e.g. VP of People, Head of People, People Operations Manager)
- Pure sales roles with no marketing/partnership component (e.g. "Account Executive", "Sales Rep") unless they are the only contacts available at a target company

When searching Apollo, combine these titles with the vertical's industry filters. Prioritise the three Primary groups to hit the lead count. Only dip into Secondary if needed. When searching, use broad title keywords (e.g. "marketing", "affiliate", "partnership") rather than exact title strings to catch variations.

---

## Steps

### Step 1 — Apollo Search (MCP)

Use `apollo_mixed_people_api_search` to find prospects matching:
- **Titles:** Search Primary groups first (Marketing, Partnerships, BD) using broad keywords like "marketing", "affiliate", "partnership", "growth", "business development". Only search Secondary (Operations) if Primary doesn't fill the lead count for a company. Never include excluded titles (People Operations, HR roles). Title matching is fuzzy: any title relating to marketing, partnerships, or BD qualifies.
- **Industry + Keywords:** use the industry as the broad filter, then layer in specific keywords to narrow results to the right niche (see Vertical Search Config below)
- **Location:** as specified by Jasper (person location, not company HQ)
- **Company size:** as specified by Jasper (never less than 10 employees — hard floor)
- **Seniority:** director, vp, c_suite, owner, founder, manager
- **Per page:** use `per_page: 10` to keep each response lean

**Max 5 contacts per company.** While collecting results, track how many prospects have been picked from each company. Once a company has 5 people in the pipeline, skip any further results from that company. This prevents over-saturating a single organisation while still capturing enough decision-makers in verticals with distributed teams (e.g. separate affiliate, marketing, and partnership functions).

Collect results until you have enough unique prospects to meet the requested lead count (overshoot by ~20% to account for losses in enrichment and dedup). If a single search doesn't return enough, run additional searches varying the title keywords or broadening keyword combinations.

**Per-page checkpoint:** After processing each page of results, extract the lean fields (name, first_name, title, company, email, apollo_id) and write them to `.tmp/prospector-run.json` BEFORE requesting the next page. Do NOT store full Apollo response objects.

**After all searching is complete:** Update `current_step` and `step_status` in the working file.

**Vertical Search Config:**

Keywords are critical for result quality. The industry is the broad bucket; the keywords narrow it down to the specific niche. Always use multiple keywords per search to maximise coverage.

| Vertical | Industry | Keywords | Exclude Keywords |
|---|---|---|---|
| life-insurance | insurance, financial services | life insurance, final expense, term life insurance, term life, whole life, universal life, burial insurance, mortgage protection | software, SaaS, platform, technology, marketing agency, digital agency, CRM, insurtech, consulting |
| tax-relief | tax services, accounting, financial services | tax debt, tax relief, tax resolution, tax settlement, IRS debt, back taxes, offer in compromise, tax lien, penalty abatement, enrolled agent | software, SaaS, platform, technology, marketing agency, digital agency, CRM, fintech, consulting |
| senior-care | home health care, elder care, healthcare | senior care, home care, elder care, assisted living, memory care, in-home care, senior living, aging in place, companion care, dementia care | software, SaaS, platform, technology, marketing agency, digital agency, CRM, healthtech, consulting |
| home-security | security, home security | home security, alarm systems, security monitoring, home automation, smart home security, surveillance, burglar alarm, access control | software, SaaS, platform, technology, marketing agency, digital agency, CRM, cybersecurity, consulting |

**Exclude Keywords** prevent software companies, marketing agencies, and tech platforms that serve the vertical from polluting results. Apollo's MCP API does NOT support negative keyword filtering natively. Instead, apply exclusions **post-search**: after each page of results, check each prospect's company name and title against the exclude keywords. Drop any prospect whose company name or description contains an exclude keyword (e.g. a company called "InsurTech Solutions" or "Life Insurance Marketing Platform"). This is critical for verticals like life insurance where many results are software/marketing companies that service the industry rather than actual insurance companies that buy leads.

**Keyword inference rule:** If Jasper asks for a vertical or niche not in the table above, determine the best keywords by thinking about:
1. What does this company actually sell or do?
2. What terms would appear on their website or in their employees' job titles?
3. What would a buyer in this space search for?

Use 5-10 specific keywords. Avoid generic terms that would pull in unrelated companies. When in doubt, ask Jasper to confirm the keywords before searching.

### Step 1B — LinkedIn Supplemental Discovery (Apify)

After Step 1, check which companies returned fewer than 5 contacts from Apollo. For each under-covered company, run the LinkedIn company employees scraper to find people Apollo missed.

**Tool:** `python3 tools/apify.py scrape-company-employees --company-url "<linkedin_company_url>" --job-title "<keyword>" --max-employees 5`

**Process:**
1. Identify companies with < 5 contacts from Step 1
2. For each company, run 3 keyword searches:
   - Run 1: `--job-title "marketing"` (catches CMO, Marketing Director, Digital Marketing, Affiliate Marketing)
   - Run 2: `--job-title "affiliate"` (catches Affiliate Manager, Partnership Recruiter)
   - Run 3: `--job-title "business development"` (catches BD Director, Growth Manager)
3. All runs use `--max-employees 5` (~$0.01-0.05 per run)
4. Merge and dedupe results across all 3 runs (match by name or profile URL)
5. Filter locally: only keep people whose headline contains target role keywords (marketing, affiliate, partnership, CMO, growth, business development, digital marketing, director). Drop pure sales reps, account execs, IT, HR, etc.
6. Dedupe against contacts already found in Step 1 (match by name or LinkedIn URL)
7. For new contacts found, extract their LinkedIn profile URLs and run them through `apollo_people_match` in Step 2 to get emails

**Cost control:** 3 runs per company (~$0.03-0.15 per company). For 15 under-covered companies, total cost is typically under $2.

**LinkedIn company URL:** If you don't have the company's LinkedIn URL, search Apollo's company data or construct it as `https://www.linkedin.com/company/<company-slug>/`. Common patterns: "goldco-precious-metals", "preserve-gold", "rosland-capital".

### Step 2 — Apollo Enrich (MCP)

For prospects that don't have email addresses from the search results (including new contacts from Step 1B):
- Use `apollo_people_bulk_match` for batches (preferred — fewer API calls, less context used)
- Fall back to `apollo_people_match` individually only if bulk fails

**Per-prospect writes:** After each enrichment batch, update the working file immediately:
- Set status to `enriched` for prospects that now have emails
- Set status to `no_email` for prospects that still don't
- Filter out `no_email` prospects from the active pipeline

Report how many were enriched vs dropped.

### Step 3 — Apollo Create Contacts + Dedup + Add to List (Bulk Tool)

Run the bulk create tool to create all enriched contacts in Apollo in one call:

```bash
python3 tools/apollo_bulk_create.py --list "{apollo_list_name}" --workers 3
```

The tool reads `.tmp/prospector-run.json`, finds all prospects with status `enriched`, creates them in Apollo via the REST API with concurrent workers, applies dedup, adds to the specified list, and updates the working file with results. It checkpoints every 50 contacts.

Apollo auto-creates the list when a new name is passed. The tool updates prospect statuses to `created` or `duplicate` and writes stats.

**Do NOT use individual `apollo_contacts_create` MCP calls for bulk runs.** The MCP endpoint is single-contact only and will take hours for 300+ contacts. Always use the bulk tool.

If the Apollo REST API key is not configured, add it to `config/api-keys.json` as `apollo_api_key` (get it from Apollo Settings > Integrations > API).

**Known Instantly campaign IDs:**
| Campaign Name | Campaign ID |
|---|---|
| CN- Life - US/UK/AUS/CA | 14f5a1a1-cfca-422d-b8cd-d4c5d8577364 |
| CN - Senior Care - US - 04/03/26 | 6f4800d2-13e1-4b95-a4a8-a489d48866e5 |

Update this table as new campaigns are discovered.

Report: "{X} contacts created, {X} duplicates skipped, added to {list name}"

### Step 4 — MillionVerifier Email Verification (API)

Run the MillionVerifier tool script to verify all emails from contacts with status `created`:

```bash
python3 tools/millionverifier.py --emails "email1@co.com,email2@co.com,..."
```

The script verifies emails concurrently and returns a JSON result categorising each email as `good`, `risky`, or `bad`.

- **good** → these go straight to Instantly (Step 6)
- **risky** → these go to BounceBan (Step 5)
- **bad** → discard, report as undeliverable

Update `.tmp/prospector-run.json` with verification results for each prospect.

### Step 5 — BounceBan Risky Email Verification (API)

Send only the `risky` emails from Step 4 to BounceBan:

```bash
python3 tools/bounceban.py --emails "risky1@co.com,risky2@co.com,..."
```

The script verifies emails concurrently and returns results categorised as `deliverable`, `risky`, `undeliverable`, or `unknown`.

- **deliverable** → mark as `recovered`, add to Instantly (Step 6)
- Everything else → discard, report as undeliverable

Update `.tmp/prospector-run.json` with BounceBan results.

### Step 6 — LinkedIn Activity Check (Apify)

Two-pass check for all verified leads (good + recovered) that have a LinkedIn URL from Apollo enrichment.

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

Runs `apimaestro/linkedin-profile-comments`. Extract the username slug from the LinkedIn URL (the part after `/in/`). The tool automatically batches up to 30 usernames per actor run and defaults to 1 comment per profile (enough to determine activity). Do NOT override `--results-per-profile` unless you have a specific reason.

**Classification (applied after both passes):**
- **Active poster** = has recent posts from Pass 1. Route to Lemlist + Instantly.
- **Active commenter** = no recent posts, BUT has commented on someone else's post within the last 9 months. Route to Lemlist + Instantly.
- **Inactive** = no recent posts AND no comments within 9 months. Route to Instantly only.
- **No profile** = no LinkedIn URL from Apollo. Treat as inactive, route to Instantly only.

**Write checkpoint:** Update each prospect with their `linkedin_status`.

### Step 6B — Clean Company Names

Before loading leads into Instantly or Lemlist, strip legal/corporate fluff from company names so they read like a human wrote them. This runs on all prospects with status `good` or `recovered` in the working file.

**What to strip:**
- Legal entity suffixes: Inc, LLC, PLLC, Ltd, Corp, Corporation, Company, Co, Limited, Incorporated, P.C., P.A., S.C., P.L., "and Co."
- These can appear with or without a preceding comma

**What to fix:**
- ALL CAPS names (3+ words) get converted to Title Case, preserving mixed-case words (e.g. McPherson) and known acronyms (MD, ENT, NYC, DC, JC, LA, FACS, DDS)
- Small words (of, and, for, the, in, at) get lowercased unless they start the name

**What NOT to touch:**
- Spa, MedSpa, Associates, Group (these are meaningful in medical/service businesses, not legal fluff)
- Names that are already clean
- Brand-specific formatting (miraDry, BeautyFix, etc.)

Update the `company` field on each prospect in the working file after cleaning. This ensures both Instantly and Lemlist receive the cleaned version.

### Step 7 — Add Leads to Instantly Campaign (API)

First, find the campaign by name:

```bash
python3 tools/instantly.py list-campaigns --search "campaign name from input"
```

This returns matching campaigns with their IDs. Fuzzy match the user's input to the closest campaign name. If ambiguous, confirm with Jasper. Store the campaign ID and name in the `discovered` object.

Then add ALL verified leads (those with status `good` or `recovered`) regardless of LinkedIn status:

```bash
python3 tools/instantly.py add-leads --campaign-id "CAMPAIGN_ID" --leads '[{"email":"...","first_name":"...","company_name":"..."},...]'
```

The script uses the batch `POST /leads/add` endpoint which accepts `campaign_id` and a `leads` array in one call. The response includes `leads_uploaded`, `duplicated_leads`, `skipped_count`, and `invalid_email_count` for verification.

**Important:** Do NOT use `POST /leads` (the single-lead create endpoint) for campaign adds. It creates orphan leads. Always use `POST /leads/add` (the batch endpoint) which properly associates leads with campaigns. The `instantly.py` script handles this correctly.

Update `.tmp/prospector-run.json`. Set status to `loaded` for each lead successfully added.

### Step 8 — Load Active LinkedIn Users into Lemlist (API)

For leads flagged as **active poster** or **active commenter** in Step 6, also add them to the Lemlist campaign for LinkedIn outreach.

**Lemlist campaign config:** Read `config/replenisher.json` and look up the vertical. The config determines routing:

- **Geo-keyed campaigns** (e.g., life-insurance has `lemlist_campaigns` object): Use the lead's country from Apollo to pick the correct campaign ID. Map: "United States" -> "US", "United Kingdom" -> "UK", "Canada" -> "CA", "Australia" -> "AU". If the lead's country doesn't match any key, skip Lemlist for that lead and note it in the report.
- **Single campaign** (e.g., `lemlist_campaign_id` string): Use that for all leads.
- **No config for this vertical:** Skip Lemlist entirely and note it in the report.

```bash
python3 tools/lemlist.py add-lead --campaign-id "LEMLIST_CAMPAIGN_ID" --email "..." --first-name "..." --last-name "..." --company "..." --title "..." --linkedin "..."
```

Run this for each active lead. The Lemlist API accepts one lead per call.

Store discovered Lemlist campaign IDs in the `discovered` object for compaction recovery.

**Write checkpoint:** Update Lemlist loaded status.

### Step 9 — Report

Read `.tmp/prospector-run.json` to compile the final summary, then present in chat:

```
PROSPECTOR COMPLETE
═══════════════════

Vertical:    {vertical}
Apollo List: {list name}
Campaign:    {instantly campaign name}
Lemlist:     {lemlist campaign name or "N/A"}

Found:       {X} prospects
Enriched:    {X} with emails
Duplicates:  {X} skipped
Verified:    {X} good + {X} recovered from risky
Discarded:   {X} bad/undeliverable

LinkedIn Active Posters:    {X} (-> Instantly + Lemlist)
LinkedIn Active Commenters: {X} (-> Instantly + Lemlist)
LinkedIn Inactive:          {X} (-> Instantly only)
No LinkedIn Profile:        {X} (-> Instantly only)

Loaded to Instantly: {X}
Loaded to Lemlist:   {X}

LEADS ADDED:
| Name | Title | Company | Email | LinkedIn | Status |
|------|-------|---------|-------|----------|--------|
| ...  | ...   | ...     | ...   | Active   | good   |
| ...  | ...   | ...     | ...   | Inactive | recovered |
```

After presenting the report, delete `.tmp/prospector-run.json`.

---

## Error Handling

- **Apollo search returns too few results:** Broaden title keywords, try related industries, or report the shortfall and ask Jasper if he wants to proceed with fewer.
- **Enrichment yields no email:** Drop the prospect, count in the "discarded" tally.
- **Apollo rejects contact as duplicate (`run_dedupe`):** Mark as `duplicate`, source a replacement if needed to maintain lead count.
- **MillionVerifier or BounceBan API errors:** Report the error, retry once. If still failing, pause and ask Jasper.
- **Instantly campaign not found:** Show available campaigns and ask Jasper to pick.
- **Apify profile scraper fails or times out:** Default those leads to "inactive" (Instantly only). Don't block the pipeline.
- **Apify comments scraper fails for a username:** Default that lead to "inactive". Don't block the pipeline.
- **Lemlist campaign not configured for this vertical:** Skip Lemlist loading entirely, note in the report. Don't fail the run.
- **Rate limits hit:** Back off and retry with a short delay.
- **Context compacted mid-run:** Follow the compaction recovery procedure in the Working Data File section above. ALWAYS read `.tmp/prospector-run.json` before doing anything else — it contains all state needed to resume.

## Notes

- Apollo enrichment uses credits. The workflow will always proceed with enrichment since it's required for email verification. If Jasper wants to skip enrichment for any reason, he'll say so.
- All API keys are loaded from `config/api-keys.json` by the tool scripts.
- Apify compute units are consumed during Step 6. Comments scraper is batched (30 per run, 1 result per profile) so costs are minimal. Profile scraper runs as a single batch.
- Lemlist routing (Step 8) is optional. If the vertical isn't in `replenisher.json` or has no Lemlist campaign configured, leads still go to Instantly.
- This workflow does NOT write outreach copy. That's a separate task — use `/copywriter` for sequence messaging.
