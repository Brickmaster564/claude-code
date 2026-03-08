---
name: bhw-intel
description: Use when someone asks to run BHW intel, scan BlackHatWorld, check Meta underground, get Facebook ads intel, or run the BHW briefing.
disable-model-invocation: true
---

## What This Skill Does

Scans BlackHatWorld's Facebook and paid advertising subforums for Meta bulletproofing tactics and ad performance insights. Compiles a focused briefing, saves it as a markdown archive, and delivers it via email.

Runs Mon / Thu / Sun via cron, or manually with `/bhw-intel`.

## Context: Jasper's Meta Setup

Jasper runs a specific infrastructure that filters what's relevant:

- **2 aged US ad accounts** inside an **aged Business Manager** (purchased)
- Those ad accounts are **shared/invited into a clean personal BM** for day-to-day operations
- Each aged account runs in its own **AdsPower browser profile** with dedicated proxy and fingerprint
- The aged accounts provide spend power and history; the personal BM is the control center

Everything in this briefing should be evaluated through this lens. Threads about creating fresh accounts from scratch are not relevant. Threads about BM sharing, aged account maintenance, AdsPower configuration, proxy hygiene, and scaling on aged accounts are high priority.

## Output

1. **Email** from hello@clientnetwork.io to Jasperkilic10@gmail.com
2. **Archive** saved to `output/bhw-intel/YYYY-MM-DD.md`

---

## Steps

### Step 1: Scan Facebook Subforum

Use WebSearch and WebFetch to find recent threads from:
`https://www.blackhatworld.com/forums/facebook.86/`

**Search strategies:**
- `site:blackhatworld.com/forums/facebook.86/` + keywords
- WebFetch the subforum page directly and scan thread titles
- Keywords to rotate: ad account banned, business manager, BM structure, aged accounts, AdsPower, antidetect browser, proxy Facebook ads, account warming, spend limit, restricted ad account, appeal, checkpoint, cloaking, agency account

**Filter for two categories:**

**Bulletproofing (priority):**
- Account bans and ban patterns (what triggers them, how to avoid)
- BM structure and BM-to-BM sharing strategies
- Aged account sourcing, warming, and maintenance
- AdsPower / antidetect browser configuration and fingerprinting
- Proxy setup and hygiene for ad accounts
- Spend scaling on aged accounts without triggering reviews
- Cascading ban prevention (how bans spread across shared BMs)
- Account checkpoints, verification, and appeals
- Cloaking strategies and compliance workarounds

**Ad Performance:**
- CTR optimization and creative testing
- Scaling strategies ($1K to $10K+ infrastructure)
- Targeting and audience building tactics
- Campaign structure and budget allocation
- What's working right now for specific verticals

Extract **3-5 insights** from this subforum. Each insight should include:
- Thread title and link
- Core tactic or finding
- Any data, results, or consensus from replies
- Whether it's bulletproofing or performance related

### Step 2: Scan Paid Advertising Subforums

Search across these subforums for Meta-relevant threads:
- `https://www.blackhatworld.com/forums/pay-per-click.13/`
- `https://www.blackhatworld.com/forums/media-buying.175/`
- `https://www.blackhatworld.com/forums/general-ppc-discussion.125/`

**Search strategies:**
- `site:blackhatworld.com` + "facebook ads" OR "meta ads" OR "ad account" in these subforums
- WebFetch the subforum pages and scan for Meta-relevant thread titles
- Focus on threads from the last 7 days with active discussion

Extract **3-5 Meta-relevant insights** from these subforums. Same format as Step 1. Skip threads about Google Ads, Bing, TikTok, or other platforms unless they contain cross-platform lessons applicable to Meta.

### Step 3: Format the Briefing

Compile everything into two formats:

1. **Markdown** (archive) using the Markdown Template below
2. **HTML** (email delivery) using the HTML template in `email-template.html`

**Structure the briefing in this order:**

1. **QUICK HITS** (executive summary at the very top). One-liner actionable takeaways from the entire briefing. Each line should be something Jasper can act on or internalize immediately. Written in second person ("your accounts", "your BM"). 3-6 bullets max. These should be specific to Jasper's setup (aged US accounts, AdsPower profiles, BM sharing) or universally useful Meta ads intel. No generic advice.

2. **BULLETPROOFING** (detailed section). Full write-ups with thread links, context, data.

3. **AD PERFORMANCE** (detailed section). Full write-ups with thread links, context, data.

Within each detailed section, lead with the most actionable or urgent items.

**Relevance filter:** Every insight should either (a) directly relate to Jasper's infrastructure (aged accounts in AdsPower, BM sharing, proxy hygiene, scaling spend) or (b) be genuinely useful Meta ads intelligence that any serious advertiser would benefit from. Skip beginner-level content and generic complaints.

The tone should be sharp, direct, no fluff. Written like an intelligence report from someone embedded in the trenches.

### Step 4: Save Files

Save both versions:
```
output/bhw-intel/YYYY-MM-DD.md    (markdown archive)
output/bhw-intel/YYYY-MM-DD.html  (HTML email)
```

Use today's date. Overwrite if files already exist.

### Step 5: Send HTML Email

Send the HTML briefing via email.

**Process:**
1. Save both files first (Step 4)
2. Run: `python3 tools/gmail.py send --to "Jasperkilic10@gmail.com" --subject "BHW Intel | YYYY-MM-DD" --html-file "output/bhw-intel/YYYY-MM-DD.html"`

The subject line should use today's date (e.g., "BHW Intel | 2026-03-08").

If email delivery fails, flag the error but still save the archive files.

---

## Markdown Template

```
BHW Intel | [date]

---

QUICK HITS

- [One-liner actionable takeaway, specific to Jasper's setup or universally useful]
- [One-liner actionable takeaway]
- [One-liner actionable takeaway]
- ...

---

BULLETPROOFING

1. [Thread title](thread URL)
[Core tactic or finding. Any data/results from replies. 2-4 sentences.]

2. [Thread title](thread URL)
[Core tactic or finding. Any data/results from replies. 2-4 sentences.]

3. [Thread title](thread URL)
[Core tactic or finding. Any data/results from replies. 2-4 sentences.]

---

AD PERFORMANCE

1. [Thread title](thread URL)
[Core tactic or finding. Any data/results from replies. 2-4 sentences.]

2. [Thread title](thread URL)
[Core tactic or finding. Any data/results from replies. 2-4 sentences.]

3. [Thread title](thread URL)
[Core tactic or finding. Any data/results from replies. 2-4 sentences.]

---

End of briefing.
```

---

## Supporting Files

- **`email-template.html`** - HTML email template (dark theme, gold accents, matching Morning Coffee style)

---

## Notes

- **No em dashes.** Use periods, commas, colons, or restructure instead.
- **Quality over quantity.** If a section has nothing good, say "Quiet week on BHW" rather than padding with garbage. 3 strong insights beat 6 weak ones.
- **Relevance filter is strict.** Every insight must pass through Jasper's setup lens: aged accounts, AdsPower profiles, BM sharing, proxy hygiene. Generic "my account got banned help" posts are noise.
- **Include thread links.** Jasper needs to be able to dive deeper on anything interesting.
- **Recency matters.** Prioritize threads from the last 7 days. Older threads are fine only if they contain evergreen tactical depth.
- **If a section fails,** include what you got and note what failed. Never silently skip a section.
- **No cost concerns.** This skill uses only WebSearch and WebFetch, no paid APIs.
