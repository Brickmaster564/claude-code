# Image Generation Prompt Methodology

Master reference for constructing image generation prompts. Use this alongside `prompt-guide.md` (Kie.ai-specific settings) whenever building prompts for ad creatives, whether through Winner Variant, Full Ad Creative, or any mode that ends in image generation.

## Core Philosophy

Describe the image as if you are art-directing it, not tagging it.

Do NOT build prompts as loose keyword piles like:
> cinematic, red dress, beautiful woman, soft light, luxury, editorial

Instead, turn the request into a controlled description of: subject, setting, action, composition, lighting, style, surface detail, mood, color behavior, text requirements, and output format.

Descriptive, narrative prompts outperform disconnected keywords because the model understands relationships and intent better when the prompt reads like a clear visual brief.

---

## Step 1: Define the Job of the Image

Before writing a single line, define what the image is supposed to do.

Ask: "What is the image trying to communicate, and where will it be used?"

This determines:
- Realism vs stylization
- Composition density
- Whether negative space is needed
- Whether typography is primary or secondary
- Whether the subject should feel editorial, commercial, cinematic, playful, premium, raw, etc.

---

## Step 2: Classify the Prompt Type

Each type needs different ingredients:

**A. Photoreal scene** (believable photo)
- Shot type, camera viewpoint, lens feeling, environment, lighting design, physical textures, realistic action/expression

**B. Product / commercial** (e-commerce, ads, packaging)
- Product hero emphasis, lighting setup, materials and finish, background control, brand tone, legibility

**C. Stylized illustration / graphic** (posters, icons, brand art)
- Explicit art style, line quality, shading treatment, shape language, palette discipline, background instruction

**D. Typography-led image** (text must render well)
- Exact copy, hierarchy, font style described in words, placement, surrounding layout, contrast and readability rules

**E. Edit / transformation** (modifying an input image)
- What changes, what stays unchanged, preservation rules for lighting, framing, identity, expression, texture

**F. Multi-image composition** (combining references)
- Which element comes from which image, how they integrate, what must remain unchanged, final scene description

---

## Step 3: Build the Image from the Inside Out

Write prompts in this layered order:

### Layer 1: Primary Subject

Who or what is the hero? Define:
- Exact subject
- Age / type / material / identity
- Distinctive physical traits
- Wardrobe / finish / design cues
- Emotional state or pose

Bad: "a woman in a dress"
Better: "a confident woman in her early 30s wearing a tailored emerald silk evening dress with clean architectural draping and minimal jewelry"

The point is specificity that influences the output, not verbosity for its own sake.

### Layer 2: Action or State

What is happening? Even static images benefit from a clear action or held moment:
- Holding, walking, turning, looking at camera, laughing, mid-pour, arranged neatly, suspended in air, emerging from shadow

This adds intent and reduces ambiguity.

### Layer 3: Environment

Where does the image happen? Define:
- Location type
- Level of detail
- Time of day or ambient context
- Relevant props
- Whether the background is sharp, soft, minimal, or atmospheric

Example: "inside a high-end minimalist skincare boutique with limestone counters, frosted glass shelving, and warm indirect architectural lighting"
Not: "in a store"

### Layer 4: Composition

One of the most important parts. Intentionally define:
- **Framing:** close-up, medium shot, wide shot, macro, overhead, flat lay, portrait crop
- **Camera angle:** eye-level, low-angle, top-down, three-quarter angle, profile
- **Subject position:** centered, left third, lower-right, foreground hero
- **Spatial balance:** symmetrical, asymmetrical, airy, dense
- **Negative space:** where it exists and why
- **Focus priority:** what is sharp and what falls off

Example: "a clean three-quarter product shot, centered slightly left, with generous negative space on the right for copy overlay"

---

## Step 4: Design the Lighting Deliberately

Lighting is not decoration. Lighting is structure. Nearly always specify:

- **Source type:** window light, softbox, rim light, practical lamp, golden-hour sun, neon spill
- **Hardness:** soft, diffused, crisp, dramatic
- **Direction:** side-lit, backlit, top-lit, frontal, edge-lit
- **Contrast level:** low contrast, moody contrast, high-key, deep shadows
- **Purpose:** flattering skin, luxury sheen, product separation, drama, cleanliness

Examples:
- "soft north-facing window light for an editorial natural look"
- "studio three-point softbox setup for a clean premium commercial finish"
- "warm sunset backlight with subtle lens bloom for a romantic cinematic mood"

**Rule: Never say just "good lighting." Always specify the lighting behavior.**

---

## Step 5: Control Style Explicitly

Style is not one word. It is a bundle of decisions. Specify some combination of:

- **Realism level**
- **Medium:** photo, illustration, vector, oil painting, comic ink, 3D render, mixed media
- **Visual references** in broad descriptive language
- **Finish:** glossy, matte, grainy, polished, painterly, flat, textured
- **Density:** minimal, richly detailed, maximalist, restrained
- **Mood:** luxurious, playful, clinical, dreamy, gritty, nostalgic

If a style word can mean ten different things, unpack it. Instead of just "cinematic," describe what cinematic means here: anamorphic feel? moody contrast? shallow depth of field? atmospheric haze? dramatic backlight?

---

## Step 6: Define Color as a System

Treat color in five layers:

1. **Dominant palette:** What are the main colors?
2. **Accent palette:** What supports them?
3. **Temperature:** Warm, cool, neutral, mixed?
4. **Saturation:** Muted, rich, pastel, high-saturation, restrained?
5. **Contrast behavior:** Monochromatic, complementary, tonal, high-contrast, luxury neutrals?

Color should reinforce the brand feeling and subject hierarchy.

Also specify color grading in photo prompts:
- Warm editorial grading
- Cool polished commercial grading
- Soft matte filmic tones
- Crisp high-contrast luxury grading

---

## Step 7: Add Material, Texture, and Surface Behavior

This is where prompts get much better. Specify:
- Skin texture, fabric type, surface finish, reflections, transparency, grain
- Paper texture, brushed metal, frosted glass, ceramic glaze, condensation
- Dust, haze, mist, velvet, linen, chrome

Models respond well to tactile specificity. It makes the output feel intentional.

Example: "a matte ceramic jar with a softly speckled finish and a warm tactile stone cap"
Not: "a nice product container"

---

## Step 8: Handle Text and Typography with Precision

Text rendering works best when the prompt is very explicit. Define:

**A. Exact text:** Quote the exact words.

**B. Role of each element:** headline, subheadline, CTA, label, badge, caption

**C. Visual character of the type** (describe font style, don't name exact fonts):
- Modern geometric sans
- Elegant high-contrast serif
- Rounded friendly sans
- Condensed bold poster type
- Handwritten marker lettering

**D. Placement:** Centered at top, bottom-left, wrapped around object, aligned right in negative space, stacked headline above CTA

**E. Readability constraints:** High contrast, clean spacing, legible at thumbnail size, no distortion, straight baseline, well-balanced margins

**F. Hierarchy:** Which text is largest? Secondary? Subtle?

Example: "Include the headline 'Glow That Lasts' in a refined modern serif, centered in the upper third. Place a smaller sans-serif subheadline beneath it with generous spacing. Add a discreet CTA button reading 'Shop Now' in the lower-right negative space."

**Rules for text:**
- Always give the exact copy
- Always assign placement
- Always describe the font mood
- Always mention readability
- Keep the layout simple when text matters
- If reliable text rendering is critical, simplify the composition so text is not fighting the image

---

## Step 9: Add Output-Shape Constraints

Include:
- Aspect ratio or orientation
- Intended crop behavior
- Amount of headroom / negative space
- Whether it should work for feed, story, poster, thumbnail, or web hero

---

## Step 10: Add Preservation Rules When Editing

For edits, separate the prompt into two parts:

1. **Change request:** What to add / remove / modify
2. **Preservation rules:** What must remain untouched

Example: "Using the provided image, change only the blue sofa to a vintage brown leather chesterfield. Keep everything else exactly the same, preserving the original room layout, wall color, lighting, perspective, and composition."

**Rule: When editing, tell the model both what to change and what not to change.**

---

## Paid Social Ad Rules

When building prompts for Meta/Facebook/Instagram feed ads, these rules override general best practices:

1. **Text economy is everything.** A feed ad lives at thumbnail size on a phone. If the text isn't readable at 160px wide, there's too much. Aim for 3-4 text elements max and under 25 words total on the image. Every word must earn its place.

2. **Bold color stops the scroll.** A white or light background disappears in a feed. Feed ads need a strong, saturated background color or a striking visual element that interrupts the endless scroll. Think: what makes someone's thumb stop?

3. **Shapes create hierarchy.** Geometric elements (circles, banners, pills, badges) guide the eye and separate text elements. They do the work that whitespace does on a landing page but in a fraction of the space.

4. **Simplify the composition.** Fewer elements with more impact always beats more elements with less impact. If the ad has a strong headline, a mechanism line, and a CTA, that might be enough. Don't add bullets, subheads, and social proof lines just because the template has fields for them.

5. **The ad must work at three sizes:** thumbnail in feed (tiny), full-size in feed (medium), and expanded/clicked (large). If any text element is unreadable at thumbnail, remove it or make it bigger by removing something else.

6. **Match the winner's visual weight.** If the original ad has bold color, heavy type, and strong shapes, the variant needs equal visual punch. A variant that is "cleaner" or "more minimal" than the original is almost always weaker in a feed, not stronger.

---

## Default Prompt Skeleton

This is the mental template for structuring any prompt:

1. **Output type and overall intent:** What kind of image, what it should feel like
2. **Subject:** Who/what is featured, with specific traits
3. **Action / pose / state:** What the subject is doing
4. **Setting:** Where it happens and what supports the scene
5. **Composition:** Framing, angle, position, balance, negative space
6. **Lighting:** Source, softness, direction, contrast, mood
7. **Style / rendering approach:** Photoreal, illustrated, luxury editorial, clean vector, etc.
8. **Color palette / grading:** Palette, saturation, temperature, accents
9. **Detail emphasis:** Textures, materials, focus priorities
10. **Text / typography:** Exact copy, type style, placement, hierarchy, readability
11. **Output constraints:** Aspect ratio, transparent background, ad-safe space, format