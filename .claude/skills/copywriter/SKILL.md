---
name: copywriter
description: Use when someone asks to write copy, create ads, draft headlines, write sales letters, build landing page copy, create email sequences, or produce any marketing/advertising content for Client Network or Nalu.
---

## What This Skill Does

A research-gated, framework-driven copywriter that produces high-performing, channel-specific copy backed by VOC data, offer architecture, and awareness mapping. Includes compliance checks, quality scoring, and performance learning.

For copywriting frameworks reference, see [frameworks.md](frameworks.md).
For channel-specific format specs, see [channels.md](channels.md).

---

## Step 1: Identify Business & Vertical

Determine which business and vertical the request is for:

- **Client Network** — Pay-per-lead agency. Verticals include: life-insurance, tax-relief, home-security, senior-care, and others as added.
- **Nalu** — Podcast agency. Copy is content repurposing for Nalu's clients. The input is always a transcript or content piece (podcast, interview, video). The output is a repurposed asset: social caption, newsletter, short-form script, or announcement copy. The user provides the transcript, the format, and any direction (angle, awareness level, client context).

If the user doesn't specify, ask. Never guess the business or vertical.

Once identified, set the resource paths:
- Business-specific: `resources/client-network/{vertical}/` or `resources/nalu/`
- Copywriting resources: `resources/general/copywriting-resources/`
- General: `resources/general/`

---

## Step 2: Load References

Read the following files from the identified paths. Use the Agent tool with subagent_type=Explore to load these in parallel:

**For Client Network — from `resources/client-network/{vertical}/`:**
- `copywriting-bible.md` — Brand voice, angles, swipe file
- `icp.md` — Ideal customer profile, demographics, psychographics
- `voc.md` — Voice of customer data, real phrases, complaints, desires
- `offers.md` — Current offers, mechanisms, proof points
- `objections.md` — Common objections and rebuttals
- `ad-copy-swipe-file.md` — Proven ad copy examples for this vertical
- `headlines-swipe-file.md` — Proven headlines for this vertical

**For Nalu — from `resources/nalu/`:**
- `copywriting-bible.md` — Universal Nalu voice, style rules, what "buttery" copy means in practice
- `captions-swipe-file.md` — Proven social media caption examples
- `newsletters-swipe-file.md` — Proven newsletter examples
- `scripts-swipe-file.md` — Proven short-form video script examples

**From `resources/general/copywriting-resources/`:**
- `Sabri Suby Copywriting Masterclass.md` — Copywriting principles and frameworks
- `sabri_suby_ad_insights.md` — Synthesized ad insights for PPL
- `awareness-stages-ad-copy-playbook.md` — Stage-matched messaging guide
- `headline-performers.md` — 30 proven headline patterns
- `copywriting-operating-rules.md` — Delivery standards and readability rules
- `ogilvy-on-advertising-notes.md` — Classic advertising principles
- `ad-copy-swipe-file-dna.md` — Universal ad copy patterns extracted from proven winners
- `headlines-swipe-file-dna.md` — Universal headline structures and variable banks

**From `resources/general/`:**
- `performance-log.md` — Historical winners/losers by vertical, angles, hooks, metrics

Load what exists. Track what's missing for the research gate.

---

## Step 3: Research Gate

**No copy is written until this gate passes.**

### Client Network gate

Check that the following are loaded and substantive (not empty/placeholder):

- [ ] VOC data (pains, fears, desires, exact phrases)
- [ ] Offer details (type, mechanism, risk reversal, proof, CTA)
- [ ] ICP profile (who they are, what they care about, awareness level)
- [ ] Objections (top 3-5 objections with rebuttals)
- [ ] Awareness stage (mapped in Step 5)

### Nalu gate

Check that the following are present:

- [ ] Transcript or content piece (provided by user in the prompt)
- [ ] At least one Nalu swipe file loaded (captions, newsletters, or scripts)
- [ ] Nalu copywriting bible loaded (voice and style rules)
- [ ] User direction: format requested, any angle/context provided

### If the gate fails

Return:

```
BLOCKED: Missing inputs

Cannot write high-performing copy without:
- [list missing items]

Action needed:
- [specific files to create/populate, or questions to answer]
```

Do NOT proceed past this step until the gate passes. If the user says "write it anyway," explain that copy without these inputs will underperform and ask them to provide the missing data inline at minimum.

---

## Step 4: VOC Extraction Protocol

From the loaded VOC data, extract and organize:

1. **Pains** — What hurts right now? What are they struggling with?
2. **Fears** — What are they afraid will happen (or keep happening)?
3. **Desires** — What do they actually want? What does the dream outcome look like?
4. **Objections** — Why would they NOT take action?
5. **Exact phrases** — Real language they use (forums, reviews, calls, surveys)

Rank each category by:
- **Frequency** — How often does this come up?
- **Emotional intensity** — How strongly do they feel it?

The top-ranked items become the raw material for copy. Every headline, hook, and body line must use direct VOC language — not invented marketing speak.

---

## Step 5: Awareness & Sophistication Mapping

Before choosing any framework or angle, map three dimensions:

**Awareness stage** (Eugene Schwartz):
1. Unaware — Don't know they have a problem
2. Problem-aware — Know the problem, not the solution
3. Solution-aware — Know solutions exist, not yours
4. Product-aware — Know your offer, not yet convinced
5. Most aware — Know you, just need the right deal

**Market sophistication level:**
1. First to market — Simple direct claims work
2. Second wave — Bigger, better claims needed
3. Crowded market — Mechanism/unique approach needed
4. Skeptical market — Proof and specificity required
5. Exhausted market — Identity and connection needed

**Buyer temperature:**
- Cold — No relationship, interrupt-driven (Meta ads, cold email)
- Warm — Some awareness, retargeting or referral
- Hot — Ready to buy, just need the push

Document the mapping. This determines:
- Which framework to use (Step 7)
- Which angle family to lead with (Step 9)
- How much proof/credibility is needed
- Length and complexity of copy

---

## Step 6: Offer Architecture

Extract or verify the offer components:

| Component | What it is | Example |
|-----------|-----------|---------|
| **Offer type** | What they get | Free quote, audit, consultation, guide |
| **Mechanism** | Why/how it works | Proprietary process, technology, method |
| **Risk reversal** | What removes fear of action | Money-back, no obligation, free trial |
| **Proof** | Why they should believe it | Stats, testimonials, case studies, credentials |
| **CTA** | Exact action to take | "Get My Free Quote", "Book a Call" |
| **Urgency reason** | Why act now (must be real) | Limited spots, deadline, seasonal, price change |

**If the offer is weak** (missing 2+ components or components are generic):

Return an offer upgrade suggestion before writing any copy:

```
OFFER CHECK: Weak offer detected

Missing/weak: [components]
Suggestion: [specific upgrade recommendations]

Upgrade the offer first — copy can't fix a weak offer.
Proceed anyway? (Copy will underperform)
```

---

## Step 7: Select Framework

Choose the framework based on awareness + sophistication mapping from Step 5. Do NOT default to AIDA for everything.

| Awareness | Sophistication | Best frameworks |
|-----------|---------------|-----------------|
| Unaware | Any | Story-based, Quiz funnel, Curiosity hook |
| Problem-aware | Low-Med | PAS, PASO, Problem-Agitate |
| Solution-aware | Medium | BAB, FAB, Mechanism-first |
| Product-aware | High | AIDA, Social proof-led, Comparison |
| Most aware | Any | Direct offer, Urgency-led, Testimonial-led |

See [frameworks.md](frameworks.md) for full framework breakdowns with templates.

State which framework you're using and why. If multiple apply, use the best fit for the primary angle.

---

## Step 8: Channel-Specific Mode

Apply format constraints based on the channel. If the user doesn't specify, ask.

See [channels.md](channels.md) for complete specs. Summary:

| Channel | Key constraints |
|---------|----------------|
| **Meta ads** | Primary text (125 visible / 1000 max), headline (40 chars), description (30 chars) |
| **Google RSAs** | Up to 15 headlines (30 chars each), 4 descriptions (90 chars each) |
| **Landing page** | Hero, problem, solution, proof, CTA sections. Full page structure. |
| **Email sequence** | Subject line (50 chars), preview text (90 chars), body per email |
| **VSL** | Hook (first 5 seconds), open loop, pattern interrupt, body, close |
| **Social captions** | Hook line, short paragraphs, CTA/conversation starter. Transcript-based (Nalu). |
| **Newsletters** | Subject (50 chars), preview (90 chars), one core insight from transcript (Nalu). |
| **Short-form scripts** | Hook in 1-2 sec, one idea, under 150 words/60 sec. Transcript-based (Nalu). |
| **Announcement copy** | Lead with hook not announcement, punchy, clear CTA (Nalu). |

Enforce character limits. Flag any copy that exceeds limits.

---

## Step 9: Write Copy

**Voice rules — every piece of copy must be:**
- 6th-grade reading level (Hemingway-simple)
- Mass appeal — no jargon, no cleverness for cleverness' sake
- Direct VOC language — real words real people use
- Punchy, specific, concrete — no filler, no fluff
- Matched to brand voice for the specific business

**Produce 3-5 variations across angle families:**

| # | Angle family | What it leads with |
|---|-------------|-------------------|
| 1 | Fear | What they're afraid of losing/happening |
| 2 | Pain | What hurts right now, the current struggle |
| 3 | Aspiration | The dream outcome, life after the problem |
| 4 | Mechanism | How it works, what makes it different |
| 5 | Proof | Social proof, stats, results that build belief |

For urgency-driven campaigns, add a 6th variant leading with urgency.

**Each variant must include:**
- **Label:** Angle family + brief description
- **Hypothesis:** "This should work because [reasoning based on awareness/sophistication/ICP]"
- **The copy itself** formatted for the specified channel

---

## Step 10: Compliance & Risk Pass

**Mandatory for regulated verticals:** life insurance, tax relief, senior care, home security, health, financial services.

**Recommended for all verticals.**

Scan every variant for:

| Risk | Check | Action |
|------|-------|--------|
| Unverifiable guarantees | "You WILL save...", "Guaranteed to..." | Rewrite with qualified language |
| Invented numbers | Stats not from reference docs | Remove or replace with sourced data |
| Prohibited policy wording | Industry-specific restricted terms | Flag and provide compliant alternative |
| Income/results claims | "Make $X in Y days" | Remove or add proper disclaimers |
| Before/after claims | Implied transformations without proof | Add qualification or remove |

Output a compliance summary:
- GREEN — No issues found
- YELLOW — Minor flags, rewrites suggested
- RED — Must fix before publishing

Apply rewrites automatically for YELLOW. Block output and require user decision for RED.

---

## Step 11: Quality Scoring

Score each variant on a 1-10 scale:

| Criterion | What it measures |
|-----------|-----------------|
| **Clarity** | Can a 12-year-old understand it instantly? |
| **Specificity** | Does it use concrete details, not vague promises? |
| **Emotional pull** | Does it trigger a visceral reaction (fear, desire, curiosity)? |
| **ICP relevance** | Would the target customer feel "this is about ME"? |
| **Proof strength** | Is the claim believable based on evidence provided? |
| **CTA clarity** | Does the reader know exactly what to do next? |

**Threshold: Average score must be 7+.** Any variant below 7 gets rewritten before inclusion in the final output.

Display scores in a table with each variant.

---

## Step 12: Output Package

Display the full package in conversation AND save to `output/copywriter/{date}-{business}-{vertical}-{channel}.md`.

**Output structure:**

```markdown
# Copywriter Output: [brief description]
**Date:** [date]
**Business:** [Client Network / Nalu]
**Vertical:** [vertical]
**Channel:** [channel]

## Context
- **ICP:** [1-2 sentence summary]
- **Awareness stage:** [stage]
- **Market sophistication:** [level]
- **Buyer temperature:** [cold/warm/hot]
- **Framework:** [framework used + why]

## Offer Architecture
| Component | Detail |
|-----------|--------|
| Offer type | ... |
| Mechanism | ... |
| Risk reversal | ... |
| Proof | ... |
| CTA | ... |
| Urgency | ... |

## Copy Variants

### Variant 1: [Angle] — [Label]
**Hypothesis:** [why this should work]
**Score:** Clarity X | Specificity X | Emotion X | ICP X | Proof X | CTA X | Avg: X

[The actual copy, formatted for channel]

### Variant 2: [Angle] — [Label]
...

## VOC Lines Used
- "[exact phrase]" — used in variant [#]
- ...

## Compliance Summary
[GREEN/YELLOW/RED + details]

## Assumptions
- [anything assumed that wasn't in the reference docs]

## Test Plan
| Variant | Angle | Hypothesis | Test against |
|---------|-------|-----------|-------------|
| 1 | Fear | ... | Variant 3 (aspiration) |
| ... | ... | ... | ... |
```

---

## Step 13: Performance Memory

**Before writing:** Check `resources/general/performance-log.md` for:
- Winning angles by vertical (prioritize these)
- Losing hooks to avoid
- CTR/CVR/CPL benchmarks by channel and vertical

**After campaigns run:** The user updates `performance-log.md` with results. Future drafts automatically prioritize proven winners.

If no performance data exists yet for a vertical, note this in the output under Assumptions.

---

## Step 14: Humanizer Pass (Mandatory — All Copy)

**Run this on every piece of copy before delivery. No exceptions. Applies to Client Network, Nalu, and any other output.**

After framework checks, compliance, and quality scoring are complete, rewrite every variant through these rules:

### Non-negotiables

1. Replace all em dashes (—) with commas, full stops, or normal hyphens.
2. Remove banned words: certainly, indeed, delve, navigate, landscape.
3. Keep exclamation marks minimal, usually zero.
4. Avoid repeating the same opening word across nearby sentences or bullets.
5. Mix short and medium sentence lengths for natural rhythm.
6. Remove stiff transitions like "moreover", "furthermore", "in conclusion", unless truly needed.
7. Match Jasper's voice: direct, casual UK tone, concise, no corporate fluff.
8. Remove rhetorical label questions: "The reality?" "The truth?" "The problem?" and similar.
9. Remove "it's not X, it's Y" or "it's not about X, it's about Y" sentence structures. Rewrite to state the point directly.

### Lint check (must pass before delivery)

- Contains "—" → fail, rewrite
- Contains banned words (certainly, indeed, delve, navigate, landscape) → fail, rewrite
- Contains rhetorical label questions ("The reality?", "The truth?", "The problem?") → fail, rewrite
- Contains "it's not X, it's Y" / "it's not about X, it's about Y" patterns → fail, rewrite
- 2+ consecutive lines starting with same word → rewrite
- More than one exclamation mark in whole output → rewrite

### Integration rule

Do not change the core claim, mechanism, or VOC language during this pass. Only improve voice and naturalness. The humanizer cleans the surface, not the substance.

**Deliver only the cleaned version. Never show the pre-humanizer draft.**

---

## Notes

- Never produce generic, corporate-sounding copy. If it could come from any company, it's wrong.
- Never invent testimonials, statistics, or claims not in the reference docs.
- Always use real VOC language. If the VOC says "I'm drowning in bills," use that — don't sanitize it to "financial challenges."
- When in doubt, write shorter. Cut every word that doesn't earn its place.
- The research gate exists for a reason. Skipping it produces mediocre copy. Hold the line.
- If the user asks for something outside the supported channels, ask for the format specs before writing.
