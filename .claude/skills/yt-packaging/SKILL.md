---
name: yt-packaging
description: Use when someone asks to package a podcast episode, create YouTube titles from a transcript, find high-ceiling concepts in a transcript, or do episode packaging for a podcast.
argument-hint: [file path to transcript, or paste transcript in chat]
---

## What This Skill Does

Reads a podcast transcript, identifies the episode's fundamental theme as experienced by the show's audience, extracts 3-5 audience-facing umbrella concepts with verbatim evidence, and generates YouTube title options using proven conventions. Built for Nalu client episodes, primarily First Things THRST (FTT).

---

## Step 1: Get the Transcript + Context

Accept the transcript via one of:
- **File path** — Read the file from the provided path (`.txt`, `.md`, or similar)
- **Pasted text** — User pastes the transcript directly in chat

If neither is provided, ask: "Paste the transcript or give me a file path to work from."

**Also capture:**
- **Show name** — Which show is this for? Default to FTT if not specified.
- **Any rough direction** — Topic angle, positioning, or framing the user is leaning toward.

If the transcript is very short (under ~500 words), flag it:
> "This transcript is short. I'll work with what's here, but the concept extraction may be limited."

---

## Step 2: Load Reference Material

Read these files using the Agent tool with subagent_type=Explore to load in parallel:

**YouTube title conventions:**
- `resources/nalu/yt-headlines-swipe-file.md` — Outlier frameworks, pattern library, reusable structures, hard-coded title rules

**General headline resources:**
- `resources/general/copywriting-resources/headline-performers.md` — 30 proven headline convention patterns
- `resources/general/copywriting-resources/headlines-swipe-file-dna.md` — Universal headline structures and assembly rules

---

## Step 3: Understand the Show's Audience

Before extracting anything, ground yourself in the show's audience. Every concept you extract and every title you write must pass through this lens.

### FTT (First Things THRST) — Default

- **Audience:** Ambitious men aged 18-30, UK-first, then US and English-speaking
- **What they care about:** Life lessons, wealth-building, masculinity, identity, relationships, discipline, reinvention, status, purpose, health, entrepreneurship, mental models
- **Show tone:** Direct, honest, unfiltered life advice from guests who have lived it
- **The viewer's question:** "What can I learn from this conversation that makes my life better?"

### FTT Title DNA (derived from 135 episodes)

Study these real FTT titles to internalise the show's packaging conventions:

- "What Ambitious Men Get Wrong About Wealth, Success & Life"
- "Powerful Life Hacks For Men To Become Dangerous, Free & Unforgettable (unfiltered)"
- "After Making $40M Online, This Is My Best Advice To Get Rich"
- "Maxims to Live a Rich(er) & More Productive Life In Your 20s & 30s"
- "How To Reinvent Yourself In 90 Days (no matter your situation)"
- "4 Signs You're Going To Stay Unhappy (No Matter What)"
- "Modern Life Is Killing Us: How To Stay Healthy In A Broken System"
- "Brutal Life Lessons You Must Accept To Live A Better Life"
- "You're NOT Lazy: My System To Build Relentless Discipline & Toughness"
- "Disappear (This Winter) If You Want To Improve Your Life"
- "The Guaranteed Way to Live Your Best Life as a Man"
- "How to Un*fck Your Mind So That Hard Things Become Easy"
- "Raw Bodybuilding, Health & Life Advice From a 6x Mr. Olympia"

**Patterns to internalise:**
- Titles speak TO the viewer about their life, never ABOUT the guest's personal story
- Multi-topic stacks are common and strong: "X, Y & Z" covering the episode's breadth
- Parenthetical amplifiers add edge: (unfiltered), (no matter your situation), (No Matter What)
- Identity-driven framing: "Men", "Ambitious", "Young People", "Your 20s & 30s"
- The guest's stories are delivery vehicles for the audience's transformation, not the headline
- No guest name in the title (unless specifically requested)

### For other shows

If the show is not FTT, ask: "Who watches this show and what do they care about?" Then apply the same audience-first logic.

---

## Step 4: Extract Umbrella Concepts

Read the full transcript carefully. Then ask the fundamental question:

> **"What is this episode about when you zoom all the way out?"**

You are not looking for the most dramatic moment. You are not looking for the best clip. You are identifying the **underlying themes of the conversation that deliver value to the show's audience.**

The guest's personal stories, anecdotes, and experiences are *evidence* that supports these themes. They are never the theme itself.

### The audience filter (CRITICAL)

For every potential concept, ask: **"Would a 22-year-old ambitious guy pressing play care about this as a life lesson for HIM?"**

- "The music industry is political" = guest-centric, niche, low ceiling
- "Why the thing you're most passionate about will test you harder than anything" = audience-facing, universal, high ceiling

- "His marriage fell apart because of a tattoo" = guest drama, voyeuristic
- "What ambitious men get wrong about relationships and commitment" = audience lesson, applicable

Always reframe through the audience's lens.

### What to produce for each concept (3-5 total):

**A. Umbrella Label**
A short, audience-facing name for this concept. Frame it as the lesson or theme, not the guest's story.

**B. High-Level Framing (1-2 sentences)**
What is this concept about at the highest level? Write it as if you're explaining to the viewer why they should care. This is the pitch for the concept.

**C. Micro Sub-Themes (2-4 per umbrella)**
Specific angles, arguments, or points within the umbrella. Each one should be a distinct, tightly focused sub-lesson.

For each micro sub-theme, include:
- **1-line summary** — The viewer-facing version of this point
- **Verbatim quotes** — Exact words from the transcript that support this point. Include timestamps if available. Pull the strongest, most quotable lines.

### Rules for quote extraction:
- **ONLY use verbatim text from the transcript.** Never fabricate, paraphrase, or embellish quotes.
- Pick quotes that are emotionally charged, surprising, or highly specific.
- If the transcript lacks strong quotes for a sub-theme, note that explicitly rather than forcing weak ones.

---

## Step 5: Rank Concepts by Ceiling

Rank the umbrella concepts from highest to lowest ceiling.

**Ranking criteria (in order of weight):**
1. **Audience relevance** — Does this concept directly address something the show's audience is navigating in their own life? A theme about ambitious men figuring out status, money, or identity will always outrank a niche industry insight.
2. **Emotional pull** — Does it trigger curiosity, fear, desire, or aspiration in the VIEWER (not just about the guest)?
3. **Mass appeal** — Would people outside the core audience still click?
4. **Breadth of coverage** — Does this concept honestly represent a significant portion of the conversation, or is it pulled from one 3-minute segment?
5. **Quotability** — Does the transcript have strong verbatim lines to back it up?

For each concept, include a 1-sentence justification for its ranking.

**Recommend a top pick** with a brief explanation of why it's the strongest lead concept for packaging.

---

## Step 6: Generate Title Options

Produce **8-12 YouTube title variations** across the ranked concepts.

### The golden rule of title generation

**Every title must speak TO the viewer about THEIR life.** The viewer is the subject. The guest's stories, credentials, and experiences are supporting context, not the headline.

- YES: "What Ambitious Men Get Wrong About Status, Money & Relationships"
- NO: "Her Tattoo Told Me Everything She'd Been Hiding for 10 Years"

- YES: "Brutal Truths on Music, Money & Building Something Real (unfiltered)"
- NO: "How Rob the Bank Broke Into the DJ World"

### Title generation process:

1. **Reference the swipe file.** Read the pattern library, reusable frameworks, and raw examples from `resources/nalu/yt-headlines-swipe-file.md`. Match the episode's content to the frameworks that fit best.

2. **Reference headline conventions.** Use patterns from `headline-performers.md` and `headlines-swipe-file-dna.md` to inform structure, but adapt them for YouTube (not ads).

3. **Study the show's actual titles** (listed in Step 3). Your titles should feel like they belong in that catalogue. If a title would look out of place next to "What Ambitious Men Get Wrong About Wealth, Success & Life" or "Brutal Life Lessons You Must Accept To Live A Better Life," it's wrong.

4. **Apply the swipe file's operator note.** Optimise titles in this order:
   - Emotional pull
   - Clarity of outcome
   - Curiosity gap
   - Character length fit (78 characters max)
   - Broad relevance

5. **Write at 6th-grade level.** Simple words, high-stakes meaning. No jargon.

6. **Must have mass appeal**, even if the episode is niched down. Connect niche topics to universal human motives: money, health, attraction, identity, freedom, meaning.

### Title variety:
- Spread titles across different umbrella concepts (don't cluster all titles on one concept)
- Use different structural frameworks from the swipe file (don't repeat the same pattern)
- Mix styles: some curiosity-driven, some identity-driven, some contrarian, some specificity-driven
- Include parenthetical amplifiers where they add value: (No Matter What), (For Normal People), (Start Here), (Unfiltered)
- **No guest name in titles** unless specifically requested
- Multi-topic stack titles are strong for wide-ranging episodes: "X, Y & Z" format
- **Include 2-3 unconventional titles per batch.** Patterns from the swipe file "Unconventional / raw tone" section:
  - Lowercase, broken grammar, casual texting energy
  - First-person confessional with specific numbers
  - Conversational parentheticals: "(this feels illegal)", "(pls watch this)"
  - Year-stamping for timeliness
  - These stand out because they break conventions. Mix them in alongside traditional formats.

### For each title, note:
- Which umbrella concept it maps to
- Which framework/pattern it uses (from the swipe file)

---

## Step 7: Weak Transcript Fallback

If the transcript lacks strong high-ceiling concepts (no clear emotional hooks, no quotable moments, no standout themes), do NOT force it. Instead:

1. **Flag it clearly:**
   > "This transcript doesn't have a clear high-ceiling concept. The content covers multiple topics without a dominant theme that would drive outsized clicks."

2. **Default to the compound multi-topic format.** Identify 2-3 core topic areas and build a descriptive title:

   > `Raw Bodybuilding, Health & Life Advice From a 6x Mr. Olympia`
   > `Dating, Money & Life Lessons From a Self-Made Millionaire`

   This format is honest, clear, and still performs, it just doesn't aim for an outlier click rate.

3. Still provide the concept breakdown (Steps 4-5) so the user has the analysis, even if the title approach is different.

---

## Output Format

Print everything to chat. Structure the output as:

```
## Episode Packaging: [brief audience-facing episode description]

### Concept 1: [Audience-Facing Umbrella Label] // RECOMMENDED
**Ceiling rank: #1** — [1-sentence justification]
**High-level framing:** [1-2 sentences, written as viewer pitch]

**Micro sub-themes:**

**1.1 — [Sub-theme title]**
[1-line summary, audience-facing]
> "[Verbatim quote]" [timestamp if available]
> "[Verbatim quote]" [timestamp if available]

**1.2 — [Sub-theme title]**
[1-line summary]
> "[Verbatim quote]" [timestamp if available]

---

### Concept 2: [Umbrella Label]
**Ceiling rank: #2** — [1-sentence justification]
...

---

### Concept 3: [Umbrella Label]
**Ceiling rank: #3** — [1-sentence justification]
...

---

## Title Brainstorm

| # | Title | Concept | Framework |
|---|-------|---------|-----------|
| 1 | [title text] | Concept 1 | [pattern name] |
| 2 | [title text] | Concept 2 | [pattern name] |
| ... | ... | ... | ... |

**Top recommendation:** Title [#] — [brief reason why this is the strongest for the show's audience]
```

---

## Step 8: Write to Google Doc in Nalu Drive

After generating the packaging output, write it to a Google Doc in the correct location in Nalu Drive.

### Client folder map

All episode folders live under **Clients** (`1Lvb2249AEVv0JhucitfYHVJiyMWtH1w4`) in the Nalu Drive.

**FTT (First Things THRST) — Mike Thurston:**

| Level | Folder ID |
|-------|-----------|
| Client: Mike Thurston | `1bust-3v2WnzAzk8Oa4lha6mWKpQgHi7J` |
| Show: First Things THRST | `1VC82Q3T0N9NxTMmm-d76sw2AvIyfsEdy` |
| Episodes | `1hKuCrnVYLC0LEfqeU3KTwKuHDTaLImpA` |
| — WIP | `1kIlgmGLgD0MkHNE_L8Y5o1Dh5SlzGa4V` |
| — PRODUCTION (MAKE) | `1RnyCjFYrP8DPvZD00e8TSjc_o-PByTiJ` |
| — Finished | `1GrAIorssnoj0XMpUZasSATNPRo2oZF9g` |
| — Potential | `1IJaneAltJBRPLrz5dQUhRCq5ZJ_XUZ7p` |
| — US Preps | `18P6mcCq1EW7dWh9A8LSja9PgCb7ag-P0` |

Guest folders are named like `E00 - [Guest Name]` and contain subfolders including `Packaging/`.

**Other clients (search these stage folders for guest name):**

| Client | Stage Folders to Search |
|--------|----------------------|
| Hack You Media | WIP: `17zVblN06-Zt9uWo1rH7zkbqFEL-ICVOg`, PRODUCTION: `1j4lSkWyRP5uPtKq7wwgw2aRtthNPplkp` |
| Dominic (Scale To Win) | WIP Episodes: `1Qvz8d89lOH4CzJz08Xcjq71hy-i5mnSK` |
| Ayax (Build to Matter) | WIP: `1aDfNo7xbjUCdZTT5lhpLoBPzAL6rMlhd`, Finished: `1mZLRtDw4wS9nh8m-zdP-RSK13PtQYF9D` |
| Jeremy Harbour (Deal Junky) | WIP Episodes: `1hjNnvXH2EEF9wWdrr4ot2x9kcRA-Hgpe` |

### Navigation process

1. **Identify the show.** Match the episode to the correct client from the map above. Default to FTT if not specified.

2. **Search for the guest folder.** Use `tools/gdocs.py --account nalu search-folder` to find the guest's folder. Search across the stage folders for that client (WIP first, then PRODUCTION, then Finished):
   ```
   python3 tools/gdocs.py --account nalu search-folder --parent-id "STAGE_FOLDER_ID" --name "Guest Name"
   ```
   Try the guest's last name first. If no results, try the full name or a distinctive part of it.

3. **Find the best subfolder for the doc.** List the guest folder's contents:
   ```
   python3 tools/gdocs.py --account nalu list-folder --folder-id "GUEST_FOLDER_ID"
   ```
   - If a **Packaging** subfolder exists, place the doc there.
   - If there is no Packaging subfolder, place the doc directly in the guest folder.

4. **Create the doc.** Create a new Google Doc titled `[Guest Name] - Episode Packaging` in the target folder:
   ```
   python3 tools/gdocs.py --account nalu create-doc --title "Guest Name - Episode Packaging" --folder-id "TARGET_FOLDER_ID"
   ```

5. **Write and format the content.** The doc must be properly formatted using the Google Docs API, not plain text. Use a Python script that:

   **a) Inserts the full text** via `write-at` at index 1.

   **b) Applies formatting via the Docs API `batchUpdate`** endpoint with these rules:
   - **HEADING_1:** Doc title (e.g., "Rob Oliver - Episode Packaging")
   - **HEADING_2:** Concept headers ("Concept 1: ..."), "Title Brainstorm", "Top Recommendation"
   - **HEADING_3:** Micro sub-theme headers ("1.1 ...", "2.3 ...", etc.)
   - **Bold:** "Ceiling rank:" labels, "Show:" and "Status:" labels, title options in the brainstorm list
   - **Italic:** All verbatim quotes from the transcript

   Use `updateParagraphStyle` for headings and `updateTextStyle` for bold/italic. Track character positions during text assembly so you can apply ranges accurately.

   **c) No ASCII art.** No `========` separators, no pipe-delimited tables, no monospace formatting. The doc should look clean and professional, as if formatted by hand in Google Docs.

   For the title brainstorm section, use a numbered list format:
   ```
   1. Title Text Here
      Concept X / Framework name / XX chars
   ```

6. **Return the link.** Print the Google Doc URL: `https://docs.google.com/document/d/DOC_ID/edit`

### If the guest folder is not found

If the guest folder doesn't exist in any stage folder for the client, tell the user:
> "I couldn't find a folder for [Guest Name] in the [Show] Episodes directory. Do you want me to create the doc elsewhere, or can you point me to the right folder?"

Do NOT create folders. Only create the doc in existing folders.

---

## Notes

- This skill is for analysis and packaging, not full copywriting. It does not produce descriptions, thumbnails, captions, or other assets. Use `/copywriter` for those.
- Never fabricate quotes. If a sub-theme has weak transcript support, say so.
- Titles must respect the 78-character max from the swipe file. Flag any that run over.
- When a title is confirmed as used by Jasper, append it to the "Winning Titles Log" in `resources/nalu/yt-headlines-swipe-file.md`.
- If the user asks for more title options or different angles after the initial output, generate additional variations without re-running the full analysis.
- The guest's personal drama is never the umbrella. It is evidence supporting an audience-facing theme.