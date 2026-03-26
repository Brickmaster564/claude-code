# Winner Variant Guide

Take a winning creative and produce genuinely different variants across messaging angles, visual direction, and creative formats. Each variant should feel like a completely different ad to Meta's Andromeda algorithm: different colors, different characters/imagery, different layout, different copy angle.

## Core Principle

Preserve the core conversion logic. The original won for a reason. Every variant keeps that underlying truth but delivers it through a different lens. A variant is NOT a twin with a swapped word or color. If the original and the variant could sit side by side and look like they came from different campaigns, you've done it right.

## Before You Start: Load Copywriting Resources

Every variant must be grounded in proven direct response principles and ICP-specific language. Before analyzing the winner or writing a single line of copy, load these resources:

**Vertical-specific** from `resources/client-network/{vertical}/`:
- `copywriting-bible.md` -- Messaging pillars, emotional triggers, objection-handling blocks, ICP language
- `voc.md` -- Voice of customer data, the exact words the ICP uses to describe their problems and desires
- `ad-copy-swipe-file.md` -- Proven ad copy for this vertical
- `headlines-swipe-file.md` -- Proven headlines for this vertical

**General copywriting** from `resources/general/copywriting-resources/`:
- `awareness-stages-ad-copy-playbook.md` -- Stage-matched messaging rules
- `sabri_suby_ad_insights.md` -- Direct response principles (halo strategy, under-the-fingernail, belief shifts)
- `ad-copy-swipe-file-dna.md` -- Universal ad copy patterns
- `headlines-swipe-file-dna.md` -- Universal headline structures
- `headline-performers.md` -- 30 proven headline patterns
- `copywriting-operating-rules.md` -- Delivery standards and readability

**Frameworks:** `.claude/skills/copywriter/frameworks.md` -- PAS, AIDA, BAB, FAB, and other framework templates

**Performance log:** `resources/general/performance-log.md` -- What has worked before

These resources are not optional background reading. They are the raw material for writing variant copy. Use VOC language verbatim where it fits. Use the copywriting bible's emotional triggers and objection blocks to inform each angle. Use Sabri Suby's principles (halo strategy, under-the-fingernail agitation, belief shifts) to sharpen every headline and subhead. Use the headline swipe files and performers to pressure-test your headline structures against proven patterns.

**When vertical-specific resources don't exist** (e.g. a new niche, a vertical without its own folder, or a B2B audience that doesn't have a dedicated copywriting bible), you still load and use every general copywriting resource listed above. Draw on Sabri Suby, the headline DNA files, the awareness playbook, the frameworks, and the universal swipe files. Combine that with what the user gives you (the winning creative, any context about the ICP) and what you can observe from the creative itself (the language it uses, the emotional triggers it taps, the objections it handles). The general resources apply to every niche and every ICP because the underlying direct response principles are universal.

The goal is that every variant reads like high-performing direct response copy, not generic marketing, because it was built on top of real customer language and tested frameworks.

---

## Static Winners

### Step 1: Analyze the Winning Creative

Break down the winner into its components:

- **Hook and headline approach:** What stops the scroll? What's the first thing the eye hits?
- **Awareness stage:** Which of Schwartz's 5 levels is this targeting?
- **Angle and emotional driver:** What feeling does this ad tap into? (fear, relief, curiosity, urgency, social proof, aspiration, etc.)
- **Visual elements:** Colors, layout, imagery, characters, font treatment, overall vibe
- **What makes this ad work:** The core conversion logic that must be preserved across all variants

### Step 2: Ideate 5 Variants

Pick the 5 messaging angles that make the most sense for this specific winner. Don't use a fixed list; choose what fits. Some angle types to draw from:

| Angle | Core Feel | When It Fits |
|---|---|---|
| Tragic/Fear | What happens if you don't act | When the downside is severe and emotionally real |
| Ease/Affordability | This is simpler and cheaper than you think | When the ICP's main blocker is perceived cost or complexity |
| Informative | Here's what you need to know | When the ICP is under-educated on the solution |
| Urgency | The window is closing | When there's a real time-sensitive element |
| Social Proof | Everyone like you is already doing this | When the ICP needs validation from peers |
| Curiosity Gap | There's something you don't know yet | When the product has a surprising or counterintuitive angle |
| Myth-Busting | What you've been told is wrong | When the ICP holds a specific false belief |
| Lifestyle Outcome | This is what life looks like after | When aspiration is a stronger driver than fear |
| Objection Handling | The reason you haven't done this is wrong | When there's a dominant objection keeping people stuck |
| Transparency/Real Talk | Here's what no one else will tell you | When trust is the main barrier |
| Hidden Mistake | You're already making this error | When the ICP is unknowingly hurting themselves |
| Case Study | Real results from a real person | When proof and relatability drive conversion |

Each variant is a **creative brief** with copy AND visual direction:

```
### VARIANT [N]: [ANGLE NAME]
**Awareness stage:** [level]
**Angle:** [emotional driver and why it fits as a variant of the original]

**IN-AD COPY:**
- Headline: [2-4 words per line, max 2 lines]
- Subhead: [1-2 sentences]
- Value prop: [key benefit or proof point, formatted for visual element]
- CTA: [button text]

**VISUAL DIRECTION:**
- Color palette: [specific shift from original, e.g. "warm gold/navy instead of pink/white"]
- Layout: [what changes in structure/placement]
- Imagery/Characters: [new subject, setting, objects, or character description]
- Font treatment: [any changes to type style or hierarchy]

**FORMAT SUGGESTION:** [only if this variant would genuinely work better as a different
format, e.g. carousel, UGC video, interview style. Not every variant needs one.]
```

### Step 3: Feedback Loop

User picks favorites and gives feedback: tweak a headline, change a color, adjust imagery, combine elements from two variants. Iterate until approved.

### Step 4: Generate the Creative

On approval:
1. Read `prompt-guide.md` for Nano Banana Pro prompting rules
2. Build the image gen prompt incorporating the approved copy and visual direction
3. Show the prompt to the user for confirmation
4. On confirmation, generate: `python3 tools/higgsfield.py generate-and-wait --prompt "[PROMPT]" --aspect-ratio "[RATIO]" --resolution "2K" --n 2`
5. Deliver image URLs in chat

## Video Winners

The same copywriting resources loaded in "Before You Start" apply here. Every script variant should be informed by VOC language, the copywriting bible's emotional triggers, Sabri Suby's direct response principles, and proven headline structures. Also load `winning-scripts.md` for the quality benchmark and `video-rehash-guide.md` for script structure guidance.

### Step 1: Analyze the Winning Video

User sends a video URL and/or script. If a URL is provided, download the transcript using the youtube-transcript skill.

Break down the winner:
- **Hook and opening approach:** What grabs attention in the first 3 seconds?
- **Persuasion structure:** Map to the 6 stages (hook, problem agitation, mechanism, social proof, offer, CTA)
- **Format type:** UGC, interview, podcast, direct-to-camera, voiceover, etc.
- **What makes this video work:** The core conversion logic to preserve

### Step 2: Ideate 5 Variants

Same angle selection process as static, but each variant also includes a format recommendation:

```
### VARIANT [N]: [ANGLE NAME]
**Awareness stage:** [level]
**Angle:** [emotional driver and why it fits]
**Format:** [same as original, or a suggested format shift with reasoning]

[Full rewritten script in script format, line breaks after each sentence]
```

Format shifts to consider:
- Podcast interview becomes AI UGC direct-to-camera
- Direct-to-camera monologue becomes interview/testimonial style
- Voiceover becomes story-driven first person
- UGC becomes text-on-screen static sequence

Only suggest a format shift when the angle genuinely calls for it. A fear-based angle might work better as direct-to-camera confession. A social proof angle might work better as an interview. Let the angle inform the format.

### Step 3: Feedback Loop

Same as static: user picks, tweaks, iterates.

### Step 4: Deliver Final Script

Polished script in the chosen format, ready for production. Apply the quality standards from `winning-scripts.md`:
- No filler or waffle
- Lead with emotional reality
- Concrete numbers
- Simple CTA
- Reads like a real person talking, not a marketer

## Key Principles

1. **Every variant must be a genuinely different ad.** Different colors, different people, different layout, different copy. Twins are useless for testing.
2. **Preserve the core conversion logic.** The original won because it tapped into something real. Keep that truth, change the delivery.
3. **Angles are creative choices, not a checklist.** Pick what fits this specific winner. A gold IRA ad calls for different angles than a life insurance ad.
4. **Format suggestions are optional but valuable.** Only when there's a genuine fit between the angle and a different format.
5. **Visual direction is mandatory for static variants.** Every static variant needs a complete creative brief, not just copy. The whole point is that each variant looks and feels like a different ad.