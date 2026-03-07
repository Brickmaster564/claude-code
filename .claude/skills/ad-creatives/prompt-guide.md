# Nano Banana Pro Prompt Guide for Ad Creatives

Use this guide when generating designed ad images (not UGC characters). These are polished ad creatives with text overlays, CTAs, and brand-specific design elements.

## Prompt Structure

Every ad creative prompt follows this structure, top to bottom:

### 1. Opening Line

State the format, dimensions, brand context, and overall emotional tone.

> Create a [ASPECT_RATIO] paid social ad for a [VERTICAL] brand, combining a realistic [IMAGE TYPE] with strong, trust-building text overlays. The ad should feel [EMOTIONAL TONE], with the value proposition clearly emphasized.

### 2. MAIN IMAGE Section

Describe the core visual. Include:
- **Subject details:** Age, gender, clothing, expression, body language
- **Background elements:** What's behind the subject (with depth/focus notes)
- **Environment:** Setting that reinforces the message
- **Composition:** Where the subject sits in the frame

For subjects, specify camera realism (see section 3) to avoid stock-photo look.

### 3. CAMERA REALISM Section

Critical for authenticity. Include when the ad features a photo (not pure graphic design):

> The image must clearly feel like it was taken on an iPhone 15 Pro rear camera, selfie mode, with:
> - Mild HDR
> - Natural skin tones
> - Slight grain and shadow noise
> - Subtle sharpening
> - Slight edge distortion typical of phone selfies
> - Imperfect framing (not centered or studio-clean)
>
> This should not look like a stock photo or professional shoot.

### 4. TEXT OVERLAY Sections (Top to Bottom)

Describe each text element in order of visual hierarchy. For EACH text block:

- **Exact text in double quotes** (the AI renders whatever is quoted)
- **Position:** Top, center, bottom, overlaid on image
- **Styling:** Color, font weight, size relative to other elements
- **Effects:** Stroke, shadow, outline for readability
- **Constraints:** "Must not block faces", "positioned above the value box"

Example:
> TOP QUOTE (WHITE TEXT WITH SOFT STROKE)
> Overlay the quote directly on the image (no box), positioned so it does not block faces.
> Text reads exactly:
> "Now I know they're taken care of."
> "That's all that matters to me."
> Styling: White text, soft dark stroke/outline, medium-weight sans-serif, calm line spacing.

### 5. VALUE STATEMENT Section

The primary message box. This is usually the visual anchor of the ad.

- **Container:** Box shape, color, shadow, border radius
- **Text:** Exact copy in quotes
- **Emphasis rules:** Which words get special treatment
  - Colored pill/highlight for key numbers
  - Underlines for important words
  - Bold for emphasis
- **Visual weight:** This box should dominate the composition

Example:
> PRIMARY VALUE STATEMENT (STRONG BOX)
> Rounded rectangular box, white with soft shadow.
> Text reads:
> "Up to $2,000,000 life insurance cover"
> "that fits your budget. Simple, affordable,"
> "and made for families like yours."
> "$2,000,000 life insurance cover" appears inside a GREEN pill-shaped highlight.
> The word "budget" is underlined.

### 6. CTA Section

The call-to-action button at the bottom.

- **Button text:** Exact copy in quotes (include arrow if needed)
- **Button styling:** Background color, text color, weight, border radius
- **Size:** Clear tap target for mobile

Example:
> CTA BUTTON (BOTTOM)
> Text: "START MY FREE QUOTE ->"
> Solid green background, white bold text, rounded corners, clear mobile tap target.

### 7. LAYOUT and CONSTRAINTS

Final rules for the overall composition:

- **Background treatment** (natural photo, gradient, solid)
- **What NOT to include** (stock photo look, testimonial boxes, speech bubbles)
- **Element hierarchy** (value box dominates over quote, CTA stands alone)
- **Face/text rules** (text must not block faces)
- **Overall mood statement**

Example:
> LAYOUT:
> - Background: natural home interior
> - No stock-photo look
> - No testimonial boxes or speech bubbles
> - Value box must dominate over quote
> - Text must not block faces
>
> Overall mood: Safe, calm, and emotionally reassuring.
> This ad should make parents feel relief, responsibility fulfilled, and confidence taking action.

---

## Vertical Style Notes

### Life Insurance
- **Colors:** Green (trust, growth), white, navy
- **Imagery:** Families, parents with children, homes, everyday moments
- **Tone:** Warm, reassuring, responsible
- **Key numbers:** Coverage amounts ($500K-$2M), daily cost ($1-2/day)

### Senior Care
- **Colors:** Soft blue, warm gold, cream
- **Imagery:** Elderly parents, multi-generational families, comfortable homes
- **Tone:** Compassionate, dignified, caring
- **Key numbers:** Care costs, savings comparisons

### Home Security
- **Colors:** Dark blue/navy, white, accent red or orange
- **Imagery:** Families at home, front doors, neighborhoods
- **Tone:** Protective, empowering, modern
- **Key numbers:** Response times, coverage area, monthly costs

### Tax Relief
- **Colors:** Green, white, professional blue
- **Imagery:** Relieved individuals, paperwork being handled, fresh starts
- **Tone:** Authoritative but approachable, solution-focused
- **Key numbers:** Savings amounts, settlement percentages

### Client Acquisition (CN brand)
- **Colors:** CN brand palette
- **Imagery:** Business growth, partnership, results
- **Tone:** Professional, results-driven, confident

---

## Aspect Ratios

| Use Case | Ratio | Kie.ai Value |
|---|---|---|
| Facebook/Instagram feed | 1:1 | 1:1 |
| Facebook ad (portrait) | 4:5 | Use closest |
| Instagram Story | 9:16 | Use closest |
| Landscape | 16:9 | Use closest |

## Resolution

Default to **2K**. Use **4K** for hero images or large display ads.

## Text Rendering Tips

Nano Banana Pro has strong text rendering. To get the best results:
- Always double-quote the EXACT text you want rendered
- Specify font characteristics (bold, sans-serif, script, etc.)
- Specify text color and any background/pill/highlight treatment
- Specify position explicitly (top-left, centered, bottom)
- Keep text concise. Shorter text renders more accurately.
- For multi-line text, specify line breaks in the prompt
