# UGC AI Character Prompt Template

Use this template when generating realistic AI characters for UGC-style ad creatives. These images must look like real smartphone photos taken by real people, not stock photography or professional shoots.

## Standard Structure

Every UGC character prompt follows this exact structure. Adapt each section to the scenario but never skip sections.

### 1. Opening Line (Format + Context)

State the format, dimensions, and overall feel.

Example:
> A [ASPECT_RATIO] ultra-realistic smartphone photo captured on an iPhone 15 Pro rear camera (~24mm equivalent lens), with authentic phone-native characteristics: mild HDR processing, natural contrast, subtle shadow noise, realistic skin texture, and slightly imperfect exposure. The image must clearly feel like it was casually captured on a phone during [SCENARIO CONTEXT].

### 2. Visibility Constraint

Always specify what should NOT be visible:
> The phone itself must NOT be visible anywhere in the frame.

### 3. Subject Description

Detailed description of the person. Include:
- **Ethnicity and age range** (e.g., "Caucasian father, approximately 32-38 years old")
- **Build:** Average, athletic, slim, etc. Must look like a normal person, NOT a model
- **Skin:** Natural texture, visible pores, slight imperfections
- **Facial details:** Stubble, under-eye texture, natural complexion
- **Hair:** Slightly imperfect, not salon-styled
- **Clothing:** Normal everyday items (plain t-shirt, hoodie, casual jacket)

Key rule: The subject must look like a real person you'd see on the street. No model-perfect features.

### 4. Expression and Behaviour (Critical)

This section defines what the person is DOING and FEELING. Be extremely specific:
- **Mouth position:** Open, closed, slightly parted
- **Expression type:** Listening, speaking, laughing, concerned, thoughtful
- **Eye direction:** Camera, interviewer, off-screen, down
- **Posture:** Calm, attentive, leaning, standing straight
- **Emotion level:** Subtle, not exaggerated

Example:
> He is listening to the interviewer, not speaking:
> - Mouth fully closed
> - Neutral listening expression
> - Eyes focused on interviewer
> - Slightly attentive, thoughtful look
> - Calm posture
> - No smile
> - No exaggerated emotion

### 5. Other People in Frame (If Applicable)

For interview scenarios, describe the interviewer or other visible people:
- **Position relative to camera** (close to camera, partially visible)
- **What's visible:** Side of head, shoulder, arm, microphone
- **What's NOT visible:** Full face, full body
- **Props:** Microphone (realistic, no branding, held naturally)

### 6. Camera Placement

Describe where the virtual camera sits:
- Position relative to subjects
- Angle (slightly behind, eye level, low angle)
- Framing style (handheld feel, slightly imperfect)
- Lens characteristics (wide-angle distortion, depth of field)

### 7. Environment

Describe the setting with specific detail:
- **Location type:** Suburban street, park, living room, gym, office
- **Visible elements:** Buildings, sidewalk, furniture, nature
- **NOT visible:** Other people (unless specified), crowds, busy environments
- **Background feel:** Calm, empty, lived-in, natural

### 8. Lighting

Always natural lighting appropriate to the scene:
- **Time of day:** Morning, mid-afternoon, golden hour, overcast
- **Source:** Natural daylight, window light, overhead fluorescent
- **Quality:** Soft, harsh, directional
- **Shadows:** Natural falloff, phone-typical exposure

### 9. Smartphone Authenticity Requirements

This section is critical. The image MUST look like:
- Rear camera capture (unless selfie is specified)
- Not selfie camera (unless specified)
- Not staged photography
- Not commercial production
- Not influencer content
- Real, spontaneous, believable

Include these technical markers:
- Mild HDR
- Natural skin tones
- Slight grain and shadow noise
- Subtle sharpening
- Slight edge distortion typical of phone cameras
- Imperfect framing (not centered or studio-clean)

### 10. Negative Prompt Controls

List what the AI must NOT generate:
- No stock photo aesthetic
- No studio lighting
- No perfect symmetry
- No oversized or unrealistic proportions
- No visible AI artifacts
- No floating elements
- [Add scenario-specific negatives]

---

## Adapting for Different Scenarios

### Street Interview
- Camera behind interviewer, subject as main focus
- Interviewer partially blocking edge of frame
- Microphone visible, held toward subject
- Empty/calm background

### Selfie (UGC testimonial style)
- Change to selfie camera angle (front-facing)
- Arm's length distance
- Slight upward angle
- Background: living room, kitchen, backyard
- Imperfect framing typical of selfies

### Action Shot (e.g., mowing lawn, cooking, working out)
- Subject mid-activity, not posing
- Natural motion blur if appropriate
- Candid feel, as if someone else took the photo
- Environment matches the activity

### Family Scene
- Main subject in focus, others slightly soft
- Children or partner in background, not looking at camera
- Lived-in home environment
- Warm, natural lighting

---

## Aspect Ratios

| Use Case | Ratio | Kie.ai Value |
|---|---|---|
| Instagram/Facebook feed | 1:1 | 1:1 |
| Instagram Story/Reel | 9:16 | Use closest available |
| Facebook ad (portrait) | 4:5 | Use closest available |
| Landscape | 16:9 | Use closest available |

## Resolution

Default to **2K** for most ad creatives. Use **4K** only when the creative will be used at large display sizes.
