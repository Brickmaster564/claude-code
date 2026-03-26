---
name: morning-coffee
description: Use when someone asks to run morning coffee, get the daily briefing, run the morning intel, or get today's marketing insights.
disable-model-invocation: true
---

## What This Skill Does

Daily intelligence briefing that keeps Jasper sharp on copywriting, AI, and marketing. Researches live content across four domains, compiles a formatted briefing, saves it as a swipe file, and delivers it via email.

Runs automatically at 7:45 AM daily via cron, or manually with `/morning-coffee`.

## Output

1. **Email** from hello@clientnetwork.io to Jasperkilic10@gmail.com
2. **Swipe file** saved to `output/morning-coffee/YYYY-MM-DD.md`

---

## Steps

### Step 1: Copywriting Wisdom (3 nuggets)

Search the web for 3 actionable copywriting insights. Pull from a broad, rotating pool of sources:

**Classic masters:**
- Gary Halbert (search thegaryhalbertletter.com and related content)
- Dan Kennedy
- David Ogilvy
- Eugene Schwartz
- Claude Hopkins

**Modern practitioners:**
- Sabri Suby
- Jason Fladien
- Rory Sutherland
- Alex Hormozi
- Russell Brunson

Use WebSearch to find specific letters, frameworks, principles, or quotes. Rotate sources daily so it doesn't repeat the same people. Each nugget should be:
- A specific, actionable insight (not vague motivation)
- Attributed to the source
- 2-4 sentences max. Include the core principle and why it matters.

**Search strategy:** Vary your queries. Examples:
- "Gary Halbert letter [topic]" (rotate topics: headlines, offers, urgency, storytelling, leads)
- "Dan Kennedy direct response [concept]"
- "Rory Sutherland behavioral economics marketing"
- "Jason Fladien webinar copywriting secrets"
- Don't just search for quotes. Search for frameworks, techniques, case studies.

### Step 2: AI News (3-5 items)

Use WebSearch to find the latest AI developments from the last 24-48 hours.

**Filter for marketer relevance:** Only include news that affects how Jasper works. That means:
- New AI tools for content creation, ad optimization, or automation
- Platform updates (Meta, Google, TikTok AI features)
- AI regulation that impacts advertising
- New models or capabilities that change what's possible

**Skip:** Academic papers, funding rounds (unless massive), developer-only updates, hardware news.

Each item: 1-2 sentence summary of what happened + 1 sentence on why it matters for marketing/lead gen.

### Step 3: X/Twitter Insights (Media Buying Focus)

Scrape recent tweets from tracked marketers using Apify. The X section is one of the most valuable parts of the briefing, so invest real effort here.

**Current X handles** (stored in `x-handles.json` supporting file):
See the supporting file for the current list. Read it before scraping. Handles are tagged by category. **Media buying accounts are the top priority** and should always appear first and get the most coverage.

**Process:**
1. Read `x-handles.json` from this skill's directory
2. Run `python3 tools/apify.py scrape-tweets --handles [comma-separated handles] --max-per-user 5`
3. From the results, extract the most insightful/actionable tweets from each person
4. Skip promotional tweets, retweets with no commentary, and generic motivation
5. **Prioritise media buying insights:** Meta ad tactics, spend strategies, campaign structure, creative testing learnings, attribution, scaling approaches, CPM/CPA trends, and platform changes. These are the insights Jasper uses daily.
6. For each person, pick the 1-3 best tweets and summarize the insight
7. **Group tweets by person.** Never repeat a person's name/handle as a separate block. List all their tweets under one heading.
8. **Order: media-buying accounts first, then general-marketing accounts.** Within each category, lead with whoever had the most valuable content that day.

**What makes a good X insight for this briefing:**
- Specific tactics or learnings from actual ad spend (e.g., "Switched from ABO to CBO on cold audiences, saw 30% CPL drop")
- Platform changes or algorithm shifts observed in the wild
- Creative testing results or frameworks
- Scaling strategies with real numbers or ratios
- Contrarian takes backed by data

**What to skip:**
- Motivational fluff, "grind" content, lifestyle posts
- Pure self-promotion or course launches
- Retweets without added commentary
- Takes without substance or data behind them

If Apify fails (credits exhausted, rate limit, etc.), fall back to WebSearch: search "[person name] site:x.com" for their recent activity. Note the fallback in the briefing.

### Step 4: BlackHatWorld Marketing Insights

Use WebSearch and WebFetch to find recent threads from BlackHatWorld's marketing sections.

**Search for:**
- "site:blackhatworld.com" + marketing terms (lead gen, Facebook ads, Google ads, SEO, funnels, cold email, automation)
- Focus on threads from the last 7 days with active discussion
- Look for unconventional tactics, case studies, split test results, and contrarian strategies

**Extract 2-3 insights:**
- What the tactic/insight is
- Why it's interesting or contrarian
- Any results or data shared

Skip: spam threads, basic beginner questions, tool promotions.

### Step 5: Format the Briefing

Compile everything into **two formats**:
1. **Markdown** (swipe file archive) using the Markdown Template below
2. **HTML** (email delivery) using the HTML Template below

The tone should be sharp, direct, no fluff. Written like a briefing from a trusted advisor, not a newsletter.

### Step 6: Save Files

Save both versions:
```
output/morning-coffee/YYYY-MM-DD.md    (markdown swipe file)
output/morning-coffee/YYYY-MM-DD.html  (HTML email)
```

Use today's date. If files already exist (e.g., manual re-run), overwrite them.

### Step 7: Send HTML Email

Send the HTML briefing as a formatted email from hello@clientnetwork.io to Jasperkilic10@gmail.com.

**Process:**
1. Save both files first (Step 6)
2. Run: `python3 tools/gmail.py send --to "Jasperkilic10@gmail.com" --subject "Morning Coffee | YYYY-MM-DD" --html-file "output/morning-coffee/YYYY-MM-DD.html"`

The subject line should use today's date (e.g., "Morning Coffee | 2026-03-05").

If email delivery fails, flag the error but still save the swipe files.

---

## Markdown Template (swipe file)

```
Morning Coffee | [date]

---

COPYWRITING WISDOM

1. [Source Name] - [Title/Topic]
[2-4 sentence insight]

2. [Source Name] - [Title/Topic]
[2-4 sentence insight]

3. [Source Name] - [Title/Topic]
[2-4 sentence insight]

---

AI RADAR

- [Headline]: [1-2 sentence summary]. Why it matters: [1 sentence].
- [Headline]: [1-2 sentence summary]. Why it matters: [1 sentence].
- [Headline]: [1-2 sentence summary]. Why it matters: [1 sentence].

---

X FEED

[Person Name] (@handle)
> [Tweet 1 content or paraphrased insight]
Takeaway: [Why this matters]

> [Tweet 2 content or paraphrased insight]
Takeaway: [Why this matters]

[Next Person Name] (@handle)
> [Tweet content or paraphrased insight]
Takeaway: [Why this matters]

...

---

FROM THE UNDERGROUND (BlackHatWorld)

1. [Thread title / topic]
[What the insight is + any data/results shared]

2. [Thread title / topic]
[What the insight is + any data/results shared]

---

End of briefing.
```

## HTML Template (email)

Build a clean, readable HTML email using the structure in `email-template.html` (supporting file). The template uses inline CSS for email client compatibility. Populate it with the same content as the markdown version.

Key design rules for the HTML email:
- Dark background (#1a1a1a) with light text for a premium, focused feel
- Section headers in accent color (#c0945c, warm gold)
- Blockquotes styled with left border for tweet content
- Clean sans-serif typography (system font stack)
- Responsive: single column, max-width 640px
- No images, no external resources. Everything inline.

---

## Supporting Files

- **`x-handles.json`** - List of X/Twitter handles to scrape. Update this file when Jasper adds or removes people to track.

---

## Notes

- **No em dashes.** Use periods, commas, colons, or restructure instead.
- **Rotate copywriting sources.** Don't pull from the same person two days in a row. Mix classic and modern.
- **Quality over quantity.** If a section has nothing good (e.g., no relevant AI news), say "Quiet day" rather than padding with garbage.
- **Apify costs credits.** The X scrape is the only paid component. Keep it to the handles in x-handles.json only.
- **If a section fails,** include what you got and note what failed. Never silently skip a section.
- **BlackHatWorld is supplementary.** If nothing interesting surfaces, the section can be short. Don't force it.
- **Swipe file is the archive.** Over time these build into a searchable knowledge base of insights.
