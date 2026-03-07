---
name: ad-creatives
description: Use when someone asks to create ads, rehash ad copy, review ad creatives, generate ad images, create UGC AI characters, rewrite video ad scripts, build ad creative variants, or workshop ad messaging for any Client Network vertical.
disable-model-invocation: true
---

## What This Skill Does

A universal ad creative workshop for Client Network. Handles everything from rehashing competitor copy to generating full AI ad images via Kie.ai (Nano Banana Pro). Works across all verticals: life insurance, senior care, home security, tax relief, client acquisition.

Four modes, auto-detected from context:

1. **Copy-Only** -- Rehash in-ad messaging from competitor or cross-vertical ads
2. **Full Ad Creative** -- Workshop copy + design, then generate images on approval
3. **UGC AI Characters** -- Generate realistic phone-photo-style people for ads
4. **Video Script Rehash** -- Rewrite competitor video transcripts for our verticals

This skill is conversational and malleable. Sessions can shift between modes fluidly. Follow the user's creative direction.

For supporting references:
- [prompt-guide.md](prompt-guide.md) -- Nano Banana Pro prompting for designed ads
- [ugc-prompt-template.md](ugc-prompt-template.md) -- UGC character prompt template
- [video-rehash-guide.md](video-rehash-guide.md) -- Video script rehash process
- [winning-scripts.md](winning-scripts.md) -- Quality benchmark scripts

---

## Step 1: Identify Vertical and Load Resources

Determine which vertical from the user's message. If unclear, ask.

**Verticals:** life-insurance, senior-care, home-security, tax-relief, client-acquisition

Load these resources using the Agent tool (subagent_type=Explore) in parallel:

**Vertical-specific** from `resources/client-network/{vertical}/`:
- `copywriting-bible.md` -- Brand voice, messaging pillars, key phrases
- `voc.md` -- Voice of customer data, real language the ICP uses
- `ad-copy-swipe-file.md` -- Proven ad copy for this vertical
- `headlines-swipe-file.md` -- Proven headlines for this vertical

**General copywriting** from `resources/general/copywriting-resources/`:
- `awareness-stages-ad-copy-playbook.md` -- Stage-matched messaging
- `sabri_suby_ad_insights.md` -- Direct response principles
- `ad-copy-swipe-file-dna.md` -- Universal ad copy patterns
- `headlines-swipe-file-dna.md` -- Universal headline structures
- `headline-performers.md` -- 30 proven headline patterns
- `copywriting-operating-rules.md` -- Delivery standards and readability

**Frameworks:** `.claude/skills/copywriter/frameworks.md` -- Framework selection reference

**Performance log:** `resources/general/performance-log.md` -- What's worked before

---

## Step 2: Determine Mode

Auto-detect from the user's input:

| User Provides | Mode |
|---|---|
| Ad image + asks for copy variants | Copy-Only |
| Ad image + asks to recreate/redesign | Full Ad Creative |
| Describes a person/scene for UGC | UGC AI Character |
| Pastes a video transcript | Video Script Rehash |

If ambiguous, ask. The user may also explicitly state what they want.

---

## Step 3: Copy-Only Mode

The user sends an ad (image or description) and wants messaging variants. No image generation.

1. **Analyze the input ad:**
   - What's the hook?
   - What awareness stage is it targeting?
   - What angle/framework is being used?
   - What's the CTA?
   - If it's from a different niche, what's the underlying psychology that makes it work?

2. **Map to target vertical:**
   - Use VOC data for the ICP's actual language
   - Use the copywriting bible for messaging pillars
   - Use awareness playbook for stage-appropriate messaging

3. **Produce 3-5 copy variants.** For each variant:
   - **Awareness stage** (label it)
   - **Angle** (what approach: fear, relief, social proof, authority, urgency)
   - **Headline/hook**
   - **Body copy** (in-ad text)
   - **CTA**
   - **Why this works** (one sentence hypothesis)

4. If the user specifies an awareness stage, write for that stage. Otherwise, produce variants across 2-3 different stages.

5. Apply humanizer pass: no corporate tone, no jargon, read like a real person wrote it.

---

## Step 4: Full Ad Creative Mode

Interactive workshop. Analyze, suggest, iterate, generate on approval.

1. **Analyze the input ad:**
   - Visual elements: layout, colors, imagery, text placement
   - Copy elements: hook, body, CTA, awareness stage
   - What makes it work (or not work)
   - If cross-vertical: what's the universal concept we can extract?

2. **Present structured analysis** to the user covering the above.

3. **Suggest copy variants** (same process as Step 3).

4. **Suggest design changes:**
   - Colors appropriate to our vertical (see prompt-guide.md for vertical palettes)
   - Imagery changes (subject, setting, mood)
   - Layout adjustments (text placement, CTA positioning)
   - Elements to add or remove

5. **Workshop loop:** Present suggestions, get user feedback, refine. Iterate until the user says "approved" or "go ahead" or similar.

6. **On approval:**
   - Read [prompt-guide.md](prompt-guide.md)
   - Build a comprehensive Nano Banana Pro prompt following the template structure
   - Show the prompt to the user for confirmation
   - On confirmation, run: `python3 tools/higgsfield.py generate-and-wait --prompt "[PROMPT]" --aspect-ratio "[RATIO]" --resolution "2K" --n 2`
   - Deliver the image URLs in chat

---

## Step 5: UGC AI Character Mode

Generate realistic AI people that look like phone photos, not stock images.

1. User describes the person and scenario (e.g., "dad standing outside mowing his lawn", "mum on the sofa with kids in background").

2. Read [ugc-prompt-template.md](ugc-prompt-template.md).

3. Build a detailed structured prompt covering all sections:
   - Opening line (format, camera, authenticity markers)
   - Subject description (age, build, skin, clothing, expression)
   - Expression and behaviour (critical: exactly what they're doing/feeling)
   - Other people in frame (if any)
   - Camera placement
   - Environment
   - Lighting
   - Smartphone authenticity requirements
   - Negative prompt controls

4. Show the prompt to the user for approval.

5. On approval, run: `python3 tools/higgsfield.py generate-and-wait --prompt "[PROMPT]" --aspect-ratio "[RATIO]" --resolution "2K" --n 2`

6. Deliver the image URLs in chat.

---

## Step 6: Video Script Rehash Mode

Rewrite competitor video ad transcripts for our verticals.

1. User pastes a transcript (from any niche).

2. Read [video-rehash-guide.md](video-rehash-guide.md) and [winning-scripts.md](winning-scripts.md).

3. **Analyze the original** -- break it into persuasion stages (hook, problem agitation, mechanism, social proof, offer, CTA).

4. **Translate to target vertical** using VOC data, copywriting bible, awareness playbook, and belief shifts appropriate to the vertical.

5. **Write the rehashed script** in script format (line breaks after each sentence). Must meet the quality bar in winning-scripts.md:
   - Short, punchy. No waffle.
   - Lead with emotional reality.
   - Concrete numbers.
   - Simple CTA.
   - Mass appeal.

6. If the user specifies an awareness stage, write for it. Otherwise, default to problem-aware.

7. Present the rewrite. Iterate if the user wants changes.

---

## Dimension Presets

| Use Case | Aspect Ratio | Notes |
|---|---|---|
| Facebook/Instagram feed | 1:1 | Most common for ad creatives |
| Instagram/Facebook portrait | 4:5 | Use closest Kie.ai ratio |
| Instagram Story/Reel | 9:16 | Vertical video frame |
| Landscape | 16:9 | YouTube, display ads |

Default resolution: **2K**. Use 4K only for hero images or large display.

---

## Notes

### Cost Control
- **Never generate images without explicit user approval.** Always show the prompt first and wait for "approved", "go ahead", "generate it", or similar confirmation.
- Each Kie.ai generation costs credits. If generating multiple (n=2), that's 2 separate tasks.

### Image Generation
- Tool: `tools/higgsfield.py` (uses Kie.ai API with Nano Banana Pro model)
- Default: n=2 (two variants per generation)
- Polling: tool handles polling automatically, returns image URLs
- Images delivered as URLs in chat

### Copy Quality
- All copy must sound like a real person, not a marketer
- No em dashes (use periods, commas, colons instead)
- Reference VOC data for authentic language
- Apply the humanizer pass: if it sounds like an ad, rewrite it
- Concrete numbers always beat vague claims

### Awareness Stages
Use Eugene Schwartz's 5 levels. Reference `awareness-stages-ad-copy-playbook.md` for stage-specific messaging guidance.

### Cross-Vertical Adaptation
When rehashing ads from unrelated niches, focus on extracting the universal psychology (fear, desire, status, relief) and mapping it to the equivalent emotion in our vertical. The structure transfers; the specifics change.
