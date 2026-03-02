---
name: yt-packaging
description: Use when someone asks to package a podcast episode, create YouTube titles from a transcript, find high-ceiling concepts in a transcript, or do episode packaging for a podcast.
disable-model-invocation: true
argument-hint: [file path to transcript, or paste transcript in chat]
---

## What This Skill Does

Analyzes a podcast transcript to extract the highest-ceiling concepts, packages them with verbatim evidence, ranks them by click potential, and generates YouTube title options based on proven conventions. Built for Nalu client episodes.

---

## Step 1: Get the Transcript + Direction

Accept the transcript via one of:
- **File path** — Read the file from the provided path (`.txt`, `.md`, or similar)
- **Pasted text** — User pastes the transcript directly in chat

If neither is provided, ask: "Paste the transcript or give me a file path to work from."

**Also capture any rough direction the user gives.** This might include:
- Guest name
- General topic/angle they're leaning toward
- Target audience for this episode
- Any specific framing or positioning they want to explore

Direction is optional but common. Use it to weight the concept extraction and title generation. If no direction is given, extract purely from the transcript.

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

## Step 3: Extract Umbrella Concepts

Read the full transcript carefully. Identify **3-5 umbrella concepts** — the broadest, most compelling overarching themes.

For each umbrella concept, produce:

### A. High-Level Framing (1-2 sentences)
What is this concept about at the highest level? Write it as a viewer-facing pitch — why should someone care about this theme? Think: what would make the widest audience click?

### B. Micro Sub-Themes (2-4 per umbrella)
Specific angles, arguments, or sub-topics within the umbrella. Each one should be a distinct, tightly focused point that could stand on its own as a hook.

For each micro sub-theme, include:
- **1-line summary** — The viewer-facing version of this point
- **Verbatim quotes** — Exact words from the transcript that support this point. Include timestamps if available in the transcript. Pull the strongest, most quotable lines — the ones that would stop someone mid-scroll.

### Rules for quote extraction:
- **ONLY use verbatim text from the transcript.** Never fabricate, paraphrase, or embellish quotes.
- Pick quotes that are emotionally charged, surprising, or highly specific.
- If the transcript lacks strong quotes for a sub-theme, note that explicitly rather than forcing weak ones.

---

## Step 4: Rank Concepts by Ceiling

Rank the umbrella concepts from highest to lowest ceiling. "Ceiling" means: which concept has the greatest potential to attract the widest audience while still being true to the episode content?

**Ranking criteria (in order of weight):**
1. **Emotional pull** — Does it trigger curiosity, fear, desire, or aspiration?
2. **Mass appeal** — Would people outside the niche still click?
3. **Specificity** — Is there a concrete, tangible hook (not vague/generic)?
4. **Quotability** — Does the transcript have strong verbatim lines to back it up?

For each concept, include a 1-sentence justification for its ranking.

**Recommend a top pick** with a brief explanation of why it's the strongest lead concept for the episode.

---

## Step 5: Generate Title Options

Produce **5-10 YouTube title variations** across the top-ranked concepts.

### Title generation process:

1. **Reference the swipe file.** Read the pattern library, reusable frameworks, and raw examples from `resources/nalu/yt-headlines-swipe-file.md`. Match the episode's content to the frameworks that fit best.

2. **Reference headline conventions.** Use patterns from `headline-performers.md` and `headlines-swipe-file-dna.md` to inform structure — but adapt them for YouTube (not ads).

3. **Apply the swipe file's operator note.** Optimise titles in this order:
   - Emotional pull
   - Clarity of outcome
   - Curiosity gap
   - Character length fit (78 characters max)
   - Broad relevance

4. **Write at 6th-grade level.** Simple words, high-stakes meaning. No jargon.

5. **Must have mass appeal**, even if the episode is niched down. Connect niche topics to universal human motives: money, health, attraction, identity, freedom, meaning.

### Title variety:
- Spread titles across different umbrella concepts (don't cluster all titles on one concept)
- Use different structural frameworks from the swipe file (don't repeat the same pattern)
- Mix styles: some curiosity-driven, some identity-driven, some contrarian, some specificity-driven
- Include parenthetical amplifiers where they add value: (No Matter What), (For Normal People), (Start Here), (Unfiltered)
- Optional: include guest name with pipe format where it adds credibility — `| Guest Name`
- **IMPORTANT — Include 2-3 unconventional titles per batch.** These break traditional YouTube title conventions on purpose. Patterns from the swipe file section "Unconventional / raw tone" include:
  - Lowercase, broken grammar, casual texting energy
  - First-person confessional with specific numbers
  - Conversational parentheticals: "(this feels illegal)", "(pls watch this)"
  - Stacked short sentences with rhythm
  - Year-stamping for timeliness (e.g., "2026...")
  - These stand out BECAUSE they don't look like typical YouTube titles. Mix them in alongside traditional formats for variety.

### For each title, note:
- Which umbrella concept it maps to
- Which framework/pattern it uses (from the swipe file)

---

## Step 6: Weak Transcript Fallback

If the transcript lacks strong high-ceiling concepts (no clear emotional hooks, no quotable moments, no standout themes), do NOT force it. Instead:

1. **Flag it clearly:**
   > "This transcript doesn't have a clear high-ceiling concept. The content covers multiple topics without a dominant theme that would drive outsized clicks."

2. **Default to the compound multi-topic format.** Identify 2-3 core topic areas and build a descriptive title:

   > `Raw Bodybuilding, Health & Life Advice From a 6x Mr. Olympia | Dorian Yates (E050)`
   > `Dating, Money & Life Lessons From a Self-Made Millionaire | Guest Name`

   This format is honest, clear, and still performs — it just doesn't aim for an outlier click rate.

3. Still provide the concept breakdown (Steps 3-4) so the user has the analysis, even if the title approach is different.

---

## Output Format

Print everything to chat. Structure the output as:

```
## Episode Packaging: [brief episode description]

### Concept 1: [Umbrella Label] ⭐ RECOMMENDED
**Ceiling rank: #1** — [1-sentence justification]
**High-level framing:** [1-2 sentences]

**Micro sub-themes:**

**1.1 — [Sub-theme title]**
[1-line summary]
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

## Title Options

| # | Title | Concept | Framework |
|---|-------|---------|-----------|
| 1 | [title text] | Concept 1 | [pattern name] |
| 2 | [title text] | Concept 2 | [pattern name] |
| ... | ... | ... | ... |

**Top recommendation:** Title [#] — [brief reason why this is the strongest]
```

---

## Notes

- This skill is for analysis and packaging, not full copywriting. It does not produce descriptions, thumbnails, captions, or other assets. Use `/copywriter` for those.
- Never fabricate quotes. If a sub-theme has weak transcript support, say so.
- Titles must respect the 78-character max from the swipe file. Flag any that run over.
- When a title is confirmed as used by Jasper, append it to the "Winning Titles Log" in `resources/nalu/yt-headlines-swipe-file.md`.
- If the user asks for more title options or different angles after the initial output, generate additional variations without re-running the full analysis.
