# ClientInsure Life Insurance - Campaign Config

Reference config for adding new ads to the Life Insurance lead campaign on the ClientInsure account.

## Account & Campaign

- **Ad Account:** `act_1434968008126478`
- **Campaign:** `120242141928480598` (Life Insurance - Lead Campaign - 11/03)
- **Page ID:** `960223713847378`
- **Instagram User ID:** `17841480666572815`
- **Pixel ID:** `935910862717553`
- **Landing Page:** `https://intake.clientinsure.io/start`
- **CTA:** `LEARN_MORE`

## Ad Set Config (replicate for every new ad set)

```json
{
  "campaign_id": "120242141928480598",
  "billing_event": "IMPRESSIONS",
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
  "optimization_goal": "OFFSITE_CONVERSIONS",
  "promoted_object": {
    "pixel_id": "935910862717553",
    "custom_event_type": "LEAD"
  },
  "targeting": {
    "geo_locations": {
      "countries": ["US"]
    }
  },
  "is_dynamic_creative": true,
  "daily_budget": 600,
  "status": "PAUSED"
}
```

**Important:** Do NOT set `age_min`/`age_max` - Special Ad Category (insurance) forces 18-65+ and the API rejects custom age targeting.

## Primary Text Variations (4 options - use ALL of them)

### Body 1
```
Want to produce more qualified leads and higher-value policies for your firm?

✔️ We connect you with consumers looking for life insurance

✔️ We help with qualifying and converting the leads

✔️ Your team advises the client and gets paid!

Complete the form below to see how it works and get a quote.
```

### Body 2
```
Are you tired of wasting your marketing budget on life insurance leads that never close?

Imagine only paying for qualified prospects who actually need coverage and are ready to buy.

That's exactly what our service delivers.

While other lead vendors sell the same prospects to five different agents, we provide exclusive, pre-qualified life insurance leads tailored to your specific criteria.

Our system targets high-intent prospects in your geographic area using advanced qualification technology that screens for:

- Income level and affordability
- Coverage need urgency

and much more.

The result? Higher conversion rates and better ROI for your agency.

Limited spots available in each market to maintain exclusivity.

Schedule your consultation today to secure your territory and start receiving quality leads that actually convert.

Don't let another qualified prospect go to your competition.
```

### Body 3
```
We are generating too many life insurance leads right now.

My current partners can't handle the volume (they're hiring more agents as you watch this ad)

If you want high quality life insurance leads that are

- Mobile verified
- Ready to pay

Then fill out the form below.

BUT - this only works if:

- You can dial leads fast
- You have a proper intake team
- You are ready to scale

Click below to fill out form and set up a trial.
```

### Body 4
```
This ad isn't for every life insurance agency...

If you're happy buying shared leads from a database and competing with four other agents on every call, keep scrolling.

But if you want:

- Leads generated exclusively for your agency
- Prospects who verified their phone number and requested a quote today
= A steady pipeline you can actually plan around

Then fill out the form below.

We run the campaigns. We qualify the leads. We send them to you and only you.
```

## Headline Variations (5 options - use ALL of them)

1. `Attn Life Insurance Brokers: Get high-quality leads every month without ads`
2. `For Life Insurance Agencies - Get Qualified Leads Without Ads or Cold Calling`
3. `Life Insurance Leads That Convert - Close More Policies This Month`
4. `Get Pre-Qualified Life Insurance Leads Every Month Without Ads or Cold Calling`
5. `Write More Policies This Month With Pre-Qualified Life Insurance Customers`

## Degrees of Freedom (Advantage+ Creative - ALL OFF)

Pulled from working creative `957209943458835`. Only these keys are accepted by the API (as of 2026-03-15).

```json
{
  "degrees_of_freedom_spec": {
    "creative_features_spec": {
      "advantage_plus_creative": {"enroll_status": "OPT_OUT"},
      "image_brightness_and_contrast": {"enroll_status": "OPT_OUT"},
      "image_templates": {"enroll_status": "OPT_OUT"},
      "image_touchups": {"enroll_status": "OPT_OUT"},
      "inline_comment": {"enroll_status": "OPT_OUT"},
      "pac_relaxation": {"enroll_status": "OPT_OUT"},
      "product_extensions": {"enroll_status": "OPT_OUT"},
      "reveal_details_over_time": {"enroll_status": "OPT_OUT"},
      "show_destination_blurbs": {"enroll_status": "OPT_OUT"},
      "show_summary": {"enroll_status": "OPT_OUT"},
      "site_extensions": {"enroll_status": "OPT_OUT"},
      "text_optimizations": {"enroll_status": "OPT_OUT"}
    }
  }
}
```

**Do NOT include `standard_enhancements` - deprecated. Do NOT use old keys like `highlight_animation`, `music`, `three_d_animation` etc. - the API rejects them.**

## Ad Naming Convention

`LI - Leads - [Hook/Description] - IMG##` (for images)
`LI - Leads - [Hook/Description] - VID##` (for videos)

## Ad Set Naming Convention

`LI - [Hook/Description]`

## Process for Adding New Ads

1. Download creative from Google Drive link
2. Upload to Meta (image via `upload-image`, video via video upload endpoint)
3. For videos: fetch auto-generated thumbnail URL from video's `thumbnails` field
4. Create ad creative with full `asset_feed_spec` (ALL 4 bodies + ALL 5 headlines above)
5. Create ad set with config above (1 ad per ad set, Creative Scaling System)
6. Create ad in PAUSED state
7. Confirm with Jasper before activating

## API Limitations

- Ad set rename/budget updates are BLOCKED by API when Advantage+ audience is enabled under Special Ad Category. Jasper must do these in Ads Manager manually.
- Status changes (pause/unpause) work fine via API at ad level.
- Ad-level renames work fine via API.
