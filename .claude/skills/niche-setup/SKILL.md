---
name: niche-setup
description: Use when someone asks to set up a new niche, build resources for a vertical, research a vertical for lead gen, create foundational docs for a new vertical, or run niche setup.
argument-hint: [vertical-name]
disable-model-invocation: true
---

## What This Skill Does

Researches and builds the complete foundational resource library for a new Client Network lead gen vertical. Produces 10 source-of-truth documents that match the quality, depth, and structure of existing verticals (senior care, home security).

Output: 10 `.md` files saved locally + uploaded to Google Drive as Google Docs.

## Inputs

- **Required:** Vertical/niche name (e.g., "solar", "roofing", "debt-relief")
- **Argument:** `$ARGUMENTS` is the vertical name

## Before You Start

### 1. Set up the vertical directory

```
resources/client-network/{vertical}/
```

Create the directory if it doesn't exist. Use lowercase, hyphens for the folder name (e.g., `debt-relief`, `home-warranty`).

### 2. Set up Google Drive folder

In Client Network's Google Drive, navigate to the **Lead Gen Brands** folder:
1. Create a folder named after the vertical (title case, e.g., "Debt Relief")
2. Inside it, create a subfolder called **Foundational Docs**

All finished documents get uploaded here as Google Docs (converted from markdown).

Use the Google OAuth credentials in `config/google-credentials.json` and `config/google-token.json` (hello@clientnetwork.io account). If no Drive upload tool exists in `tools/`, create `tools/google_drive.py` with functions to create folders and upload markdown as Google Docs.

### 3. Load templates

Before creating ANY document, read the equivalent document from an established vertical to understand the exact structure, section hierarchy, depth, and formatting to replicate. Senior care and home security are the most complete.

**Template mapping:**

| Document | Primary Template | Fallback Template |
|----------|-----------------|-------------------|
| Niche Overview | `senior-care/senior_care_niche_overview.md` | `home-security/home_security_niche_overview.md` |
| PPL Playbook | `senior-care/senior-care-ppl-playbook.md` | `home-security/home-security-ppl-playbook.md` |
| Competitors | `senior-care/senior-care-competitors.md` | `home-security/home-security-competitors.md` |
| Lead Buyers | `senior-care/senior-care-lead-buyers.md` | `home-security/home-security-lead-buyers.md` |
| Competitor Funnel Audit | `home-security/home-security-competitors.md` (site audit sections) | — |
| Avatar | `life-insurance/Avatar.md` | `senior-care/voc.md` (Section 1) |
| VOC | `senior-care/voc.md` | `home-security/voc.md` |
| Copywriting Bible | `senior-care/copywriting-bible.md` | `home-security/copywriting-bible.md` |
| Ad Copy Swipe File | `senior-care/ad-copy-swipe-file.md` | `home-security/ad-copy-swipe-file.md` |
| Headlines Swipe File | `senior-care/headlines-swipe-file.md` | `home-security/headlines-swipe-file.md` |

All template paths are relative to `resources/client-network/`.

---

## Phase 1: Market Research

Research the market thoroughly using WebSearch and WebFetch. Cross-reference multiple sources. Prioritize recent data (last 2 years). Every claim should be verifiable.

After completing all Phase 1 docs, present a summary to Jasper and wait for approval before moving to Phase 2.

### Step 1: Niche Overview

**Read template first:** `senior-care/senior_care_niche_overview.md`

**Research targets (use WebSearch + WebFetch):**
- Industry size, growth rate, market trends
- Types of services/products within the vertical
- Key terminology and definitions
- Customer demographics (who buys, age, income, geography)
- Cost landscape (what consumers pay)
- Regulatory landscape (licensing, compliance, state-by-state differences)
- Key statistics useful for ad copy

**Structure to match:**
1. The [Vertical] Industry (overview paragraph)
2. Market Size and Trends (stats, growth projections)
3. Types of [Vertical] Services (categorized breakdown)
4. Key Terminology (definitions for industry-specific terms)
5. The Lead Buyers (brief overview, expanded in Step 4)
6. Customer Demographics (who the end consumer is)
7. Cost Landscape (pricing tables/ranges)
8. Regulatory Landscape (federal, state, licensing)
9. Key Statistics for Ad Copy (table: Stat | Source Use)
10. References (numbered citations)

**Save as:** `resources/client-network/{vertical}/{vertical}_niche_overview.md`

### Step 2: PPL Playbook

**Read template first:** `senior-care/senior-care-ppl-playbook.md`

**Research targets:**
- Cost-per-lead benchmarks by platform (Facebook, Google, TikTok, native)
- Lead selling prices in this vertical (what buyers pay per lead)
- Unit economics (CPL vs. sell price, margins)
- Lead generation mechanics (form fills, calls, ping-post)
- Lead qualification criteria (what makes a lead valid)
- Buyer expectations (exclusivity, return policies, real-time delivery)
- Seasonality patterns (when demand peaks/dips)

**Structure to match:**
1. Introduction to PPL Economics in [Vertical]
2. CPL & Cost-Per-Deal by Platform (tables with benchmarks)
3. Lead Selling Prices & Unit Economics (pricing tiers, margin analysis)
4. Lead Generation & Delivery Mechanics (funnel structures, ping-post)
5. Lead Qualification & Buyer Expectations (valid lead criteria, SLAs)
6. Seasonality in [Vertical] Lead Gen (monthly/quarterly patterns)
7. References

Include a table of contents with anchor links.

**Save as:** `resources/client-network/{vertical}/{vertical}-ppl-playbook.md`

### Step 3: Competitors

**Read template first:** `senior-care/senior-care-competitors.md`

**Research targets (use WebSearch + WebFetch to find and analyze):**
- Lead generation companies operating in this vertical
- Referral platforms and matching sites
- Lead aggregators and networks
- Pay-per-call networks
- Comparison/quote sites
- Technology platforms
- Marketing agencies specializing in this vertical

**For each competitor, capture:**
- Company name, URL, HQ location
- Business model (aggregator, direct gen, marketplace, etc.)
- Lead types sold (exclusive, shared, live transfer, aged)
- Pricing model if discoverable
- Geographic coverage
- Notable features or differentiators

**Structure to match:**
- Market Overview (brief landscape summary)
- Categorized sections (e.g., "Category 1: Referral Platforms")
- Numbered entries with Field | Detail tables per company
- Competitive Landscape Summary at the end
- Sources section

**Save as:** `resources/client-network/{vertical}/{vertical}-competitors.md`

### Step 4: Lead Buyers

**Read template first:** `senior-care/senior-care-lead-buyers.md`

**Research targets:**
- National/enterprise companies in this vertical
- Large regional operators
- Mid-size regional companies
- Franchise networks
- Lead marketplaces and intermediaries already buying in this space
- Industry events where lead buyers gather

**For each buyer, capture:**
- Company name, HQ, geographic coverage
- Number of locations/agents/offices
- Services offered
- Revenue estimate if available
- Lead buying likelihood assessment
- Notes on why they'd buy leads

**Structure to match:**
- Tiered hierarchy (Tier 1: National, Tier 2: Large Regional, etc.)
- Standardized Field: Detail format per company
- Summary table: Total Addressable Market by Tier
- Recommended Priority Targets (top 10 for first outreach)
- Key Industry Events for Lead Buyer Prospecting
- Sources

**Save as:** `resources/client-network/{vertical}/{vertical}-lead-buyers.md`

### Phase 1 Review

Present to Jasper:
- Brief summary of each document (2-3 sentences)
- Any gaps or areas where research was thin
- Key findings that will influence Phase 2 (audience insights, competitor angles)

**Do NOT proceed to Phase 2 until Jasper approves.**

---

## Phase 2: Audience & Competitor Deep Dive

This phase goes deeper into the people: who the competitors are targeting, how they talk to them, and who the actual consumer is. Use WebSearch and WebFetch extensively. Visit actual competitor websites and funnels.

After completing all Phase 2 docs, present a summary and wait for approval before moving to Phase 3.

### Step 5: Competitor Funnel Audit

**Read template first:** The site audit sections in `home-security/home-security-competitors.md` (this doc includes deep funnel audits per competitor site)

**Process:**
1. From the Competitors doc (Step 3), identify the top 10-15 competitors with active lead gen funnels
2. Visit each competitor's website/funnel using WebFetch
3. For each site, audit and document:
   - Landing page headline and subheadline (exact copy)
   - Lead capture mechanism (form, quiz, call, chat)
   - Key benefit claims and proof points
   - Language patterns (fear-based, aspirational, urgency, etc.)
   - CTA copy (exact wording)
   - Trust signals (testimonials, badges, guarantees)
   - Offer structure (free quote, comparison, guide, etc.)
   - Notable copy angles or hooks worth swiping

**Structure:**
- Site index table (Site #, Name, URL, Model, Type)
- Individual audit sections per site with structured field tables
- Summary of common language patterns across all competitors
- Top angles and hooks observed (swipeable insights)

**Save as:** `resources/client-network/{vertical}/{vertical}-funnel-audit.md` (always a separate file to keep competitors.md focused on market mapping and this file focused on copy/language analysis)

### Step 6: Avatar

**Read template first:** `life-insurance/Avatar.md` AND `senior-care/voc.md` (Section 1: Customer Avatar)

**Research targets:**
- Demographics: age range, gender split, income, geography, family status
- Psychographics: values, fears, motivations, daily life
- The decision-making journey (what triggers them to search)
- Emotional state at each stage of awareness
- Direct consumer language (from forums, Reddit, reviews, Quora, social media)
- Key life events that trigger need for this service/product

**Structure to match:**
1. Demographic & General Information (age, income, location, family)
2. Key Challenges & Pain Points
3. Goals & Aspirations
4. Emotional Drivers & Psychological Insights
5. Direct Client Quotes (sourced from forums, reviews, social)
6. Key Emotional Fears & Deep Frustrations
7. Typical Emotional Journey (Awareness > Frustration > Desperation > Relief)

Use verbatim consumer language wherever possible. Source quotes from Reddit, forums, review sites, social media, Quora. Attribute the source type (e.g., "Reddit user," "Google review").

**Save as:** `resources/client-network/{vertical}/Avatar.md`

### Step 7: VOC (Voice of Customer)

**Read template first:** `senior-care/voc.md`

**Research targets:**
- Pains: what keeps the consumer up at night (categorized by theme)
- Fears: deepest emotional drivers
- Hopes: what they want to feel after solving the problem
- Dreams: best-case outcome
- Objections: why they haven't taken action yet (with counter-arguments)
- Key statistics useful for copy angles
- Emotional journey map (stage by stage)
- Channel-specific language patterns (how they talk on Facebook vs. Google vs. forums)

**Structure to match:**
1. Customer Avatar (brief recap linking to Avatar.md)
2. Pains (categorized with verbatim quotes under each)
3. Fears (emotional driver statements)
4. Hopes (desired feelings)
5. Dreams (best-case outcomes)
6. Objections (with heading, description, and counter-argument for each)
7. Key Statistics for Copy Angles (Stat | Source Use table)
8. Emotional Journey Map (4 stages with quotes and descriptions)
9. Channel-Specific Language Patterns (Facebook, Google, YouTube)
10. Halo Strategy Language (SAY > THINK > FEEL > DESIRE pyramid per Sabri Suby)

**Save as:** `resources/client-network/{vertical}/voc.md`

### Phase 2 Review

Present to Jasper:
- Avatar summary (who the consumer is in 3-4 sentences)
- Top 3 pain points and objections discovered
- Most interesting competitor angles/language found in funnel audits
- Any surprises or insights that should influence the copywriting bible

**Do NOT proceed to Phase 3 until Jasper approves.**

---

## Phase 3: Synthesis

This phase synthesizes ALL research from Phases 1 and 2 into actionable copywriting assets. Every document in this phase MUST be built from the research, not from generic knowledge.

### Required: Load Sabri Suby Resources

Before writing ANY Phase 3 document, read ALL of these files:

- `resources/general/copywriting-resources/Sabri Suby Copywriting Masterclass.md`
- `resources/general/copywriting-resources/sabri_suby_ad_insights.md`
- `resources/general/copywriting-resources/ad-copy-swipe-file-dna.md`
- `resources/general/copywriting-resources/headlines-swipe-file-dna.md`
- `resources/general/copywriting-resources/awareness-stages-ad-copy-playbook.md`
- `resources/general/copywriting-resources/copywriting-operating-rules.md`
- `resources/general/copywriting-resources/headline-performers.md`
- `resources/general/copywriting-resources/ogilvy-on-advertising-notes.md`

These frameworks govern how all copy is written. The copywriting bible, ad swipe file, and headlines swipe file must be built through these lenses.

Also re-read the vertical's own Phase 1 and Phase 2 docs to have all research fresh in context.

### Step 8: Copywriting Bible

**Read template first:** `senior-care/copywriting-bible.md`

**This is the capstone document.** It synthesizes:
- VOC language (pains, fears, hopes, dreams) into the Halo Strategy table
- Competitor funnel language into hooks and angles
- Avatar insights into targeting and tone
- Sabri Suby frameworks into structured copy templates

**Structure to match:**
1. Common Language & Emotional Triggers (Halo Strategy table: Pains, Fears, Hopes/Dreams, Objections, Confusion - with verbatim language from VOC)
2. Facebook Ad Hooks (categorized by angle: Fear, Simplicity, Affordability, Skepticism, News/Urgency, Specificity, Social Proof - 4-6 hooks each)
3. Full Facebook Ad Copy Examples (4 complete ads with Eyebrow > Headline > Body > CTA structure)
4. Google Search Ad Copy (table: Keyword Theme | Headlines 1-3 | Descriptions 1-2)
5. Landing Page Headline Options (8-10 options with strategy notes)
6. Fascination Bullets / Bullet Copy (12-15 benefit-driven bullets)
7. Quiz Funnel Questions & Framing (6 questions with standard + benefit-framed versions, plus results page structure)
8. Email Sequence Hooks (6 email subject lines with preview body text)
9. P.S. Formulas (5 variations)
10. Objection-Handling Copy Blocks (table: Objection | Copy Block for each major objection from VOC)
11. Under-the-Fingernail Copy Blocks (3 long narrative blocks using deep emotional pain points from VOC)

**Rules:**
- All copy must use language sourced from the VOC and Avatar docs, not generic phrasing
- Apply the Larger Market Formula: target the 95% not actively buying (information gathering, problem aware, unaware)
- Follow the 17-step sales message structure from Sabri Suby where applicable
- Grade 6 readability per copywriting operating rules
- No em dashes

**Save as:** `resources/client-network/{vertical}/copywriting-bible.md`

### Step 9: Ad Copy Swipe File

**Read template first:** `senior-care/ad-copy-swipe-file.md`
**Also reference:** `resources/general/copywriting-resources/ad-copy-swipe-file-dna.md` (for structural patterns and voice DNA)

**Structure to match:**
- Metadata line: **Market:** [geo] | **Target:** [demographics] | **Offer:** [offer type] | **Format:** Facebook/Meta Ads
- 7 complete ad examples, each titled "Ad XX - [Angle] / [Awareness Stage] Angle"
- Each ad follows: Hook > Body > Bullets > CTA
- Angles to cover: Fear, Guilt/Identity, Affordability, Pain, Objection Handle, Aspiration/Relief, Urgency
- Final section: Recurring Hooks & Phrases (Swipe These) with sub-sections for Hooks, Proof/Stat Lines, Benefit Bullets, CTAs

**Rules:**
- Ads must use the 5 structural patterns from ad-copy-swipe-file-dna.md
- Voice must match the Voice DNA rules (conversational, soft fear, short sentences, specifics early)
- Price anchoring must use the coffee comparison or equivalent trivial anchor
- All language sourced from VOC/Avatar research

**Save as:** `resources/client-network/{vertical}/ad-copy-swipe-file.md`

### Step 10: Headlines Swipe File

**Read template first:** `senior-care/headlines-swipe-file.md`
**Also reference:** `resources/general/copywriting-resources/headlines-swipe-file-dna.md` (for the 6 headline structures and variable banks)

**Structure to match:**
- Metadata line matching ad copy swipe file
- Headlines by Angle & Awareness Stage (H3 per angle: Unaware, Fear, Questions, Guilt/Burnout, Affordability, Simplicity, Aspiration, Geo)
- 2-9 headlines per angle, covering different awareness stages
- Structural Patterns (Swipe These) - table: Pattern | Example
- Key Variables to Swap & Test (care types, price anchors, audience qualifiers, geo slots, CTA hooks, urgency levers)

**Rules:**
- Use the 6 headline structures from headlines-swipe-file-dna.md as the building framework
- Headlines are assemblies, not inventions: [Audience] + [Benefit/Offer] + [CTA Hook]
- Include variable banks specific to this vertical
- All language sourced from research

**Save as:** `resources/client-network/{vertical}/headlines-swipe-file.md`

### Phase 3 Review

Present to Jasper:
- Overview of the copywriting bible (key angles, strongest hooks)
- Sample of 2-3 best ad copy examples
- Top 5 headlines
- Any areas where research was thin and copy might need refinement

---

## After All Phases Complete

### Upload to Google Drive

Upload all completed documents to `Lead Gen Brands / {Vertical} / Foundational Docs /` on Client Network's Google Drive as Google Docs.

### Final Summary

Present a complete summary:
- All documents created (with local file paths)
- Google Drive folder link
- Key strategic insights about the vertical
- Recommended next steps (e.g., "Start prospecting in Apollo", "Test these 3 ad angles first")

---

## Notes

- **Research depth matters.** These are source-of-truth documents. Shallow research produces bad copy, bad prospecting, bad everything. Take the time to find real data, real quotes, real competitors.
- **Always read the template doc before writing.** Never skip this step. The structure must match existing verticals so all resources feel consistent.
- **Sabri Suby frameworks are non-negotiable for Phase 3.** Load every resource file listed. The copywriting bible, ad swipe, and headlines swipe must be built through these frameworks.
- **Use verbatim consumer language.** The VOC and Avatar docs should contain real quotes from real people. Forums, Reddit, review sites, Quora, social media. Not paraphrased, not sanitized.
- **No em dashes.** Use periods, commas, colons, or restructure instead.
- **Grade 6 readability** for all copy in Phase 3 documents.
- **If research is thin for a section,** flag it to Jasper rather than filling with generic content. Better to have a gap than to have wrong data treated as source of truth.
- **Cross-reference between docs.** The PPL Playbook should reference Lead Buyers. The Copywriting Bible should reference the VOC. The Ad Swipe File should reference the Copywriting Bible. These docs form an interconnected system.
