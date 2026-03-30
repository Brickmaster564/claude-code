---
name: guest-pipeline
description: Use when someone asks to run guest discovery, find new podcast guests, run the guest pipeline, source guest candidates, do guest research, or refresh guest lists for any show (FTT, Deal Junky, Scale to Win, Hack You). Also use when someone asks to find guests similar to a specific person, or find the CEO/founder of specific companies. Triggers on "guest-pipeline" in Slack messages.
argument-hint: show name, count, and optional seed person or companies
---

## What This Skill Does

Three modes:

1. **Full pipeline** (cron or manual): Runs 5 research methods, deduplicates against Airtable, enforces diversity quotas, and writes qualified candidates to the client's Airtable guest tracker.
2. **Targeted search - similar to** (ad-hoc): Given a seed person, finds similar guest candidates and adds them to Airtable. Fast, focused, no Apify costs.
3. **Targeted search - company lookup** (ad-hoc): Given one or more company names, researches the founder/CEO of each, qualifies them against guest criteria, and adds qualified candidates to Airtable.

## Detect Mode

Parse the `` to determine which mode to run. Requests can come from `/guest-pipeline`, natural language, or Slack messages from Jasper or Scott.

**Required info for targeted/reactive requests:** The request MUST specify the show and the count. If a seed person is given, run similar-to mode. If companies are given (STW only), run company lookup. If neither, ask for clarification.

**Show name aliases:** Map these to config keys before proceeding:
- `ftt`: "FTT", "First Things THRST", "THRST", "Mike Thurston", "Mike's show"
- `jh`: "JH", "Deal Junky", "Jeremy Harbour", "Jeremy's show", "DJ"
- `stw`: "STW", "Scale to Win", "Dominic", "Dom's show"
- `hym`: "HYM", "Hack You", "Hack You Media", "HY"

**Slack trigger examples (Jasper or Scott may phrase it like):**
- "guest-pipeline: find 15 people for Deal Junky similar to Daniel Priestley"
- "guest-pipeline: 10 guests for FTT like Ed Mylett"
- "guest-pipeline: find 20 new guests for STW"
- "guest-pipeline: who runs Gousto, Brewdog, Gymshark? add to STW"

### Mode Detection:

- If `` contains "similar to" or "like" followed by a person name: **Targeted search - similar to**. Extract the seed name, count, and client. Examples:
  - "find 15 people for Deal Junky similar to Daniel Priestley" -> seed: "Daniel Priestley", count: 15, client: jh
  - "10 guests for FTT like Ed Mylett" -> seed: "Ed Mylett", count: 10, client: ftt
  - `/guest-pipeline stw similar to Tom Blomfield 10` -> seed: "Tom Blomfield", count: 10, client: stw
- If `` contains company names (with or without "find the CEO of", "founder of", "who runs"): **Targeted search - company lookup**. This mode is **STW only**. Extract the company name(s). If the client isn't STW, default to STW. Examples:
  - "who runs Gousto, Brewdog, Gymshark? add to STW" -> companies: ["Gousto", "Brewdog", "Gymshark"], client: stw
  - `/guest-pipeline stw companies: Monzo, Starling, Revolut` -> companies: ["Monzo", "Starling", "Revolut"], client: stw
- If `` is just a client name or "run guest pipeline for [client]": **Full pipeline mode**.

---

## Tool Pre-Flight (ALL MODES)

Before doing anything else, load all required deferred tools. These are not available by default and will fail silently if not loaded first.

```
ToolSearch: "select:mcp__claude_ai_Airtable__list_records_for_table,mcp__claude_ai_Airtable__create_records_for_table,WebSearch,WebFetch"
```

If any tool fails to load, retry with individual `select:` queries. Do NOT proceed until all four tools are confirmed available.

---

## TARGETED SEARCH: SIMILAR TO

### Steps

1. Read config and guest criteria (same as full pipeline).
2. Pull all existing names from Airtable for dedup.
3. Run a focused research burst for the seed person:
   - **WebSearch x3:** "people similar to [Seed Name]", "[Seed Name] similar creators podcast", "if you like [Seed Name] you'll love"
   - **WebSearch x2:** "[Seed Name]'s niche/industry" to understand their lane, then search for other people in that lane
   - **WebFetch** the top 2-3 listicle/recommendation results to extract names
4. Deduplicate against Airtable.
5. Apply guest criteria from the client's criteria file (same quality bar as full pipeline).
6. Write up to [count] qualified candidates to Airtable (same fields as full pipeline).
7. Post a Slack summary to #guest-research-and-comms using `python3 tools/slack.py send --channel "C089HSD8US1" --text "MESSAGE"`. Tag Scott: "<@U07BL527UP8> Targeted search: [count] guests similar to [Seed Name] added to [Show Name] Airtable." List each candidate with their rationale.
8. No run log file needed for targeted searches.

### Notes for Similar-To Mode
- No Apify calls. Pure WebSearch/WebFetch.
- No diversity quotas (the whole point is finding people in a specific lane).
- Still deduplicate against Airtable. Still apply quality criteria.
- **Never guess social handles.** For each candidate, run a quick WebSearch like "[Name] [platform] official" to find the verified profile. If you cannot confirm the correct profile, leave the Profile field empty. Wrong links are worse than no links.
- Uses a separate checkpoint: `.tmp/guest-pipeline-targeted.json` (won't interfere with full pipeline runs).

---

## TARGETED SEARCH: COMPANY LOOKUP (STW ONLY)

This mode is exclusively for Scale to Win. The show is about UK scale-up founders/CEOs, so the natural input is often a company name rather than a person name.

### Steps

1. Read STW config and guest criteria (`guest-criteria-stw.md`).
2. Pull all existing names from STW's Airtable for dedup.
3. For each company name provided:
   a. **WebSearch:** "[Company Name] founder CEO" and "[Company Name] leadership team headcount"
   b. Identify the founder and/or current CEO. If the founder has left and there's a new CEO, note both but prioritize the current leader (they're more likely to accept a podcast invite).
   c. **Research the person:** WebSearch "[Person Name]" to understand their background, company size (headcount), funding stage, story arc (scaling journey, exit, challenges).
   d. **Qualify against STW criteria.** Check: 30+ employees? Real scaling story? UK/European connection? Fits one of the 6 guest lanes?
   e. **Find their LinkedIn profile.** WebSearch "[Person Name] LinkedIn". Verify the link is correct before using it.
   f. If qualified, add to the candidates list. If not, skip and note why.
4. Deduplicate against Airtable.
5. Write all qualified candidates to Airtable (same field mapping as full pipeline).
6. Post a Slack summary to #guest-research-and-comms using `python3 tools/slack.py send --channel "C089HSD8US1" --text "MESSAGE"`. Tag Scott: "<@U07BL527UP8> Company lookup: researched [X] companies for Scale to Win. [Y] qualified candidates added to Airtable." List each company and outcome (added / already exists / didn't qualify).

### Notes for Company Lookup Mode
- This mode is thorough per candidate rather than broad. Expect 1 candidate per company (sometimes 2 if co-founders both qualify).
- No diversity quotas. No Apify calls.
- Still deduplicate and apply quality criteria.
- **Never guess profile URLs.** Always verify via WebSearch. LinkedIn is the expected platform for STW.
- The rationale field should include company context: "[Name] is CEO of [Company] ([headcount] employees, [sector]). [1 sentence on why they fit Scale to Win]."
- Uses the same checkpoint as similar-to: `.tmp/guest-pipeline-targeted.json`.

---

## FULL PIPELINE MODE

## Before You Start

1. Read the config: `.claude/skills/guest-pipeline/config.json`
2. Determine the client. If `` is provided, use it. If not, default to `ftt`. Look up the client key in `config.clients`.
3. Read the guest criteria file specified in the client config's `guest_criteria_file` field: `.claude/skills/guest-pipeline/[filename]`. Default: `guest-criteria.md` (FTT).
4. Check for an existing checkpoint file at `.tmp/guest-pipeline-run.json`. If it exists and `run_date` matches today, resume from `current_method`. If it exists but the date is old, delete it and start fresh.

## Step 1: Deduplication Setup

Pull ALL existing records from the client's Airtable table using `mcp__claude_ai_Airtable__list_records_for_table`. Use pagination (pass `nextCursor` if returned) to get every record. Request the Name, Rationale, and Profile fields (Method 2 needs Rationale to pick seed guests, Method 3 needs Profile to extract Instagram handles).

Build a dedup set: normalize each name (lowercase, trim whitespace, strip titles like "Dr.", "Mr.", suffixes like "Jr", "III"). Store as a list in the checkpoint file.

**If Airtable read fails, STOP the entire run. Dedup is non-negotiable.**

Write checkpoint: save `existing_names` to `.tmp/guest-pipeline-run.json`.

## Step 2: Run 5 Research Methods

Run each method sequentially. After each method, write the checkpoint to `.tmp/guest-pipeline-run.json` with the method's candidates and status set to "completed". Keep candidate data lean:

```json
{"name": "Full Name", "profile": "url or empty", "source": "method_name", "category": "diversity_tag", "context": "1 sentence max"}
```

For EVERY candidate found, immediately check against the dedup set (existing Airtable names + candidates from earlier methods in this run). Skip duplicates. Use fuzzy matching: normalize both names and compare. Match on first+last name (handles "Dr. Andrew Huberman" matching "Andrew Huberman").

### Method 1: Competitor Podcast Scraping

For each show in `config.clients.[client].competitor_podcasts`:

1. WebFetch the Apple Podcasts URL. Extract episode titles from the page content.
2. Parse guest names from episode titles. Common formats:
   - "Guest Name: Topic" (e.g., "Simon Sinek: The Dangerous Myth of Online Vulnerability")
   - "Credential: Hook... Guest Name" (e.g., "Discipline Expert: The Habit That Will Make Or Break... James Clear")
   - "Guest Name - Topic"
   - "Topic with Guest Name"
3. If a title is ambiguous (no obvious person name), skip it.
4. Also run 1-2 WebSearch queries like "podcasts similar to [show name] for men" to auto-discover 2-3 additional shows. WebFetch those Apple Podcasts pages too.

Target: 40-60 raw names. After dedup, expect 20-30 unique.

**Write checkpoint after this method completes.**

### Method 2: Seed-Based Lookalike Search

1. From the Airtable records pulled in Step 1, randomly select up to `seed_sample_size` (10) existing guests. Prefer those with a Rationale field filled (richer data). If fewer than 10 have rationales, take all that do and fill the rest randomly.
2. For each seed guest, run 1-2 WebSearch queries:
   - "people similar to [Guest Name] podcast"
   - "[Guest Name] similar creators" or "if you like [Guest Name]"
3. Parse person names from the search results (listicles, recommendation articles, "similar to" sections).
4. Assign a diversity category based on context clues from the search results.

Target: 20-30 raw names.

**Write checkpoint after this method completes.**

### Method 3: Instagram Discovery

**For FTT only (Instagram-primary show).** For STW and JH, skip Instagram Discovery entirely. Instead, run a LinkedIn-based discovery method: WebSearch "[seed name] LinkedIn connections" and "people also viewed [seed name] LinkedIn" for up to 8 seed guests who have a LinkedIn URL in the Profile field. Parse names from the results. This produces comparable yield without wasting Apify credits on shows where Instagram is irrelevant.

**FTT steps:**
1. From Airtable records, find up to 8 guests who have an Instagram URL in the Profile field. Extract the Instagram handle from the URL.
2. Run `python3 tools/apify.py scrape-instagram-related --handles "handle1,handle2,..." --min-followers [threshold from config]` via Bash.
3. If the Apify actor fails or returns an error, fall back to WebSearch: "[seed name] similar Instagram accounts 100k followers" for each seed.
4. From the results, extract name, handle, follower count, and bio.
5. Assign diversity categories based on bio content.

Target: 20-30 raw names.

**Write checkpoint after this method completes.**

### Method 4: Listicle/Trending Mining

1. Read the `diversity_categories` from config.
2. For each category, construct 2-3 WebSearch queries using its search terms. Examples:
   - "top [search_term] to watch 2026"
   - "best [search_term] podcast guests"
   - "most influential [search_term] with large following"
3. Read the previous run log from `output/guest-pipeline/` (most recent file). If certain categories were under-represented, give those categories extra queries this run.
4. WebFetch the top 1-2 listicle results per query. Extract person names from the articles.
5. Tag each candidate with their diversity category.

Target: 30-40 raw names.

**Write checkpoint after this method completes.**

### Method 5: Book/Media Discovery

1. Run WebSearch queries across diverse domains:
   - "new business books 2026 authors"
   - "best new psychology books 2026"
   - "viral podcast guest 2026"
   - "trending thought leaders [category]"
   - "fastest growing YouTube channels [category]"
2. Extract person names, noting what makes them relevant (book title, channel name, media appearance).
3. Tag with diversity category.

Target: 15-25 raw names.

**Write checkpoint after this method completes.**

## Step 3: Diversity Selection

After all 5 methods complete, read the full candidate list from the checkpoint file.

1. **Tag every candidate with a primary diversity category** based on their source, context, and bio. Use the category search terms from config as matching keywords.
2. **Apply hard exclusions.** Remove any candidate matching `exclude_types` from config. Check against their context/bio text.
3. **Enforce quotas.** For each diversity category:
   - First pass: select candidates up to `quota_min`, picking the strongest (most context, profile URL found, multiple source methods).
   - Second pass: fill remaining slots (to reach `target_per_run`) from any category, picking the strongest remaining.
   - If a category cannot meet its minimum, redistribute those slots.
   - **For JH only:** Verify the final split respects `lane_split` from config (70% operators, 30% M&A). Count candidates in operator-prefixed categories vs ma-prefixed categories. If the split drifts beyond 60/40 or 80/20, rebalance by swapping overflow candidates.
4. **Final dedup check.** For any candidate whose name is ambiguous (common name, possible nickname match), do a quick Airtable search using a formula filter on the Name field to confirm they don't already exist.

The final list should have exactly `target_per_run` candidates (default: 30). If fewer than 15 survive, log a warning.

## Step 4: Write to Airtable

For each qualified candidate, create a record using `mcp__claude_ai_Airtable__create_records_for_table`. Use the field IDs from the client's `airtable_fields` config. Map fields dynamically:

| Config Key | Value |
|------------|-------|
| `name` | Full name |
| `location` (if exists) | Wrap `default_location` from config as an array: `["General / Remote"]`. This is a multipleSelects field. Only write if `location` exists in `airtable_fields` AND `default_location` exists in config. |
| `profile` | URL to their strongest social platform. **Must be verified via WebSearch, never guessed.** If unverified, leave empty. Platform choice depends on show (LinkedIn for STW/JH, Instagram/X/YouTube for FTT). |
| `rationale` | 1-2 sentence: who they are, why they fit, audience size if known |
| `additional_notes` (if exists) | Source method, diversity category, extra context |
| `type` (if exists) | Use `airtable_defaults.type` from config |
| `status` (if exists and `airtable_defaults.status` set) | Use default status from config |
| Any other field in `airtable_defaults` | Write the default value. E.g., STW has `stw: "STW"` which marks records as Scale to Win. |

Only write fields that exist in the client's `airtable_fields` config. Different clients have different table schemas. For each key in `airtable_defaults`, check if the corresponding field exists in `airtable_fields` before writing.

Batch in groups of 10 records per API call. Write each batch immediately. Update the checkpoint's `airtable_written` array after each successful batch.

If a batch write fails, retry once. If it fails again, save the remaining candidates to `.tmp/guest-pipeline-pending.json` and continue with the Slack summary.

## Step 5: Slack Summary

Send a summary to #guest-research-and-comms using `python3 tools/slack.py send --channel "C089HSD8US1" --text "MESSAGE"` via Bash. Always tag Scott (`<@U07BL527UP8>`) at the top of the message.

Format:
```
<@U07BL527UP8> GUEST PIPELINE: [Show Name]
Run: [date] | Added: [count] to Airtable

CANDIDATES ADDED:
  [Name] - [1-line rationale] (via [source method])
  [Name] - [1-line rationale] (via [source method])
  ... (list ALL added candidates)

METHOD BREAKDOWN:
  Competitor Podcasts: [X] candidates (from [Y] shows)
  Seed Lookalikes: [X] candidates
  Instagram/LinkedIn Discovery: [X] candidates
  Listicle/Trending: [X] candidates
  Book/Media: [X] candidates

DIVERSITY:
  [Category]: [count] | [Category]: [count] | ...
```

## Step 6: Save Run Log

Save a JSON run log to `output/guest-pipeline/YYYY-MM-DD.json` containing:
- `date`, `client`, `target`, `total_added`
- `method_stats` (per-method candidate counts)
- `diversity_breakdown` (per-category counts)
- `candidates` (full list of added candidates with all fields)
- `errors` (any issues encountered)
- `duplicates_removed` count

Delete the `.tmp/guest-pipeline-run.json` checkpoint file after the run log is saved.

## Error Handling

| Failure | Action |
|---------|--------|
| Airtable read fails (Step 1) | STOP entire run. Post error to Slack. |
| Apify actor fails (Method 3) | Fall back to WebSearch. Continue. |
| Single method produces 0 candidates | Log warning. Other methods compensate. |
| <15 candidates after dedup + selection | Post warning to Slack: "Low yield run. [X] candidates added. Consider manual top-up." |
| Airtable write fails after retry | Save pending to `.tmp/guest-pipeline-pending.json`. Post warning to Slack. |

## Progress Updates

Post progress updates to #guest-research-and-comms during execution so the team knows the pipeline is working. Use `python3 tools/slack.py send --channel "C089HSD8US1" --text "MESSAGE"` via Bash.

**For targeted searches (similar-to / company lookup):**
1. After dedup setup: "Researching [count] candidates similar to [Seed Name] for [Show Name]. Pulling existing guests for dedup..."
2. After research complete, before writing: "Found [X] qualified candidates. Writing to Airtable now..."
3. Final report (already defined in steps above)

**For full pipeline (cron):**
1. After Step 1 (dedup): "Guest pipeline started for [Show Name]. [X] existing guests loaded for dedup. Running 5 research methods..."
2. After Step 2 (all methods done): "Research complete. [X] raw candidates found across 5 methods. Applying diversity selection..."
3. After Step 3 (selection): "Selected [X] candidates. Writing to Airtable..."
4. Final report (Step 5)

## Notes

- Keep analysis LEAN during methods. Store only name + profile + source + category + 1 sentence context. Do not write essays about each candidate. This prevents context window overflow.
- ALWAYS write the checkpoint to `.tmp/guest-pipeline-run.json` after each method. This is your safety net for context compaction.
- Do NOT use em dashes in any output.
- This skill is designed to run unattended via cron. Do not ask the user questions during execution. Make decisions and document them in the run log.
