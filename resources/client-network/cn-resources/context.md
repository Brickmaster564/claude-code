# Client Network Master Context

Compiled: 2026-03-02

## Primary Operating Context

# Client Network core file

## Business model foundation (PPL)

### What pay-per-lead is
- Client Network gets paid a fixed amount per qualified lead delivered.
- Payment is for outcome units, not impressions, clicks, or effort.
- This is a pipeline business, weakest stage becomes the bottleneck.

### The 3 parties and incentives
1) Lead generator (us)
- Controls traffic, funnel/quiz, qualification, verification, routing, reporting, optional nurture.
- Goal is buying attention below resale value while keeping buyer retention high.

2) Lead buyer
- Examples: insurance, legal, home services, solar, lending.
- Controls intake speed, sales process, close rate, LTV, compliance.
- Goal is predictable customer acquisition at acceptable CPA.

3) Prospect
- Experiences ad -> landing/quiz/form -> submit -> contact/nurture.
- Wants trust and a solution, not our unit economics.

Important operating truth from your notes
- Lead performance is heavily affected by buyer operations, often 70 to 80 percent.
- Same lead quality can perform very differently between weak intake and strong call-center buyers.

### PPL vs nearby performance models
- PPL leads
- Pay per call
- Pay per appointment
- Commission per sale
- Lead brokering
- Infrastructure/retainer model

Default stance
- PPL is the cleanest first model: define lead spec, deliver, bill.

### End-to-end process, phase 1
1) Choose vertical with:
- real buyer demand (ideally 3+ buyers)
- enough lead volume
- economics that support margin
- scalability across multiple geos

2) Define lead spec (core control document)
Lead spec must include:
- required fields
- qualification criteria
- geo acceptance rules
- duplication rules
- disqualifiers
- verification requirements
- delivery method
- replacement/refund policy and time window

Pricing and qualification rule
- Higher pricing should map to deeper qualification and higher lead quality.
- Better quality lowers buyer workload and improves buyer CPA.
- Avoid racing to the bottom on price.

### End-to-end process, phase 2 (build engine)
3) Traffic acquisition
- paid ads are main scalable lever (Meta, TikTok, Google Search/YouTube, native)
- third-party lead suppliers are possible but reduce control
- SEO can be high-quality but slower and more exposed to search ecosystem shifts

Creative rule
- In paid social, creative is usually the top lever.
- Iterate fast, strong creatives tend to show performance quickly.

4) Funnel / quiz / form
- Optimise for qualified leads at profitable CAC, not raw lead volume.
- Use decision trees to tier lead quality and route by buyer value.
- Typical tools: Heyflow, LeadsHook, GHL forms.

Quality upgrades
- stronger hook/headline
- fewer but smarter questions
- use GeoIP where useful
- phone validation or OTP in selected verticals only
- strong thank-you page with trust and next-step push (book call, expectations, proof)

5) Backend infrastructure
- storage: CRM/sheet/GHL
- routing logic: who gets which lead tier
- delivery: webhook/API/Zapier/GHL/notifications
- logging: timestamp, source, campaign, answers, consent trail
- billing ledger: lead counts, disputes, replacements

Buyer integration rule
- If buyer has IT, request webhook and test payload mapping.
- If not, secure system access or place buyer in managed GHL sub-account.

### End-to-end process, phase 3 (buyer acquisition)
6) Build buyer list
- prioritise buyers already buying leads or already running paid ads
- target marketing/partnership leadership in larger firms
- target founder/owner in smaller firms

7) Outreach and closing workflow
- multi-channel outreach (LinkedIn + email + optional phone/social)
- 3-4 follow-ups with 1-2 day spacing
- execute at scale (250+ targets) before changing thesis

Messaging rules
- short, natural, industry-native language
- simple binary CTA (yes/no/more info)
- avoid over-pitching, move to discovery fast

Dual-angle outreach rule
- direct angle: are you currently buying X leads
- research angle: market interview framing to extract pain points and demand intel

8) Fact-finding call, required discovery
Capture before making offer:
- product/service sold and best-converting sub-offers
- target CPA and current CPL economics
- close/contact rate benchmarks
- geo targets/exclusions
- definition of a good lead
- daily/weekly intake capacity
- delivery method requirements
- compliance requirements (TCPA, TrustedForm, Jornaya where applicable)

Then propose:
- written lead spec
- realistic volume band (day/week)
- pricing justified by qualification depth, lead age, and source quality

### End-to-end process, phase 4 (fulfilment and delivery reliability)
9) Launch, test, stabilise
- start with controlled daily volume, even when buyer requests very high weekly numbers
- use trust-building ramp plans, prove consistency, then scale
- in test cycles, move fast, cut weak ads by threshold, ship fresh creative variants quickly

10) Delivery implementation
- deliver in buyer-usable format:
  - real-time webhook into buyer CRM
  - GHL sub-account
  - Zapier bridge into email/SMS + sheet + CRM
  - round-robin or rules-based routing for multi-buyer setups
- speed-to-lead is a core performance lever in many verticals

11) Quality control feedback loop
- ingest buyer outcomes: accepted, rejected, duplicate, wrong geo, invalid contact
- tune funnel qualifiers/disqualifiers and verification settings
- tune campaign layer: creative, placement, geo, targeting
- avoid overreacting to tiny samples, look for sustained patterns over time

### End-to-end process, phase 5 (billing, disputes, retention)
12) Billing structures
- weekly invoicing
- net 15 or net 30
- real-time billing per lead
- upfront deposits or pre-funded balances
- with larger buyers, collaborate on controlled volume ramps and cashflow-safe billing terms

13) Dispute handling system
- define duplicate window and source of truth
- define replace vs credit policy with timing boundaries
- enforce geo acceptance rules in form and backend routing
- monitor fraud patterns, repeated numbers, fake identities

Large buyer duplicate-risk pattern
- big buyers may reject heavily on duplicate overlap and may not share CRM data
- mitigation options:
  - test alternate channels or audience angles with lower overlap
  - auto-route overlap-prone leads to secondary buyers
  - balance with smaller buyers that have less saturated databases
  - stay compliant with consent rules when routing/reselling

14) Retention and compounding logic
- target 2-5 buyers per vertical for routing resilience and negotiation leverage
- maintain stable lead spec and transparent QA standards
- grow trust into higher volume allocations
- introduce quality tiers with price tiers by lead attributes

## Why PPL works
For Client Network
- clean unit economics, price per lead multiplied by qualified volume
- scalable when paid traffic margins hold
- easier to sell where buyers already value lead flow
- repeatable operating system from spec to billing

For buyers
- lower risk than retainers, payment tied to delivered outcomes
- rapid scaling possible when lead quality holds
- more predictable pipeline when delivery is consistent

## Pro-level operating nuances
A) Lead quality is engineered
- Better questions, routing, verification, and creative-message alignment create quality.
- If qualification gets stricter, CPL generally rises, so price and unit economics must support that.

B) Form type is secondary to buyer intake quality
- Quiz vs form matters less than buyer speed-to-lead, scripts, call centre capacity, and follow-up discipline.

C) Pricing is positioning
- Avoid price races to the bottom.
- Justify higher prices with deeper qualification, fresher leads, stronger sources, and stronger expected buyer CPA.
- Use volume bands and controlled ramping.
- Small per-lead price changes compound massively at scale.

D) Exclusive vs shared
- Exclusive is default preference, cleaner buyer trust and cleaner operations.
- Shared can work in certain markets, but adds routing, compliance, and consent complexity.

E) Multi-buyer routing is risk control
- Buyers will eventually pause, cap, or change criteria.
- Protect delivery with alternative buyers and rules-based distribution.

F) Pipeline-first management
Track end-to-end flow:
- Impressions
- Clicks
- Landing page conversion
- Qualified lead rate
- Delivered lead acceptance
- Buyer contact rate
- Buyer close rate
- Buyer LTV/CPA
- Retention and volume growth

Constraint rule
- Improve the narrowest bottleneck first, then re-evaluate the full system.

## Core SOP checklist (Client Network)
- define vertical and buyer ICP
- define lead spec and pricing assumptions
- build funnel with decision-tree qualification and verification
- build backend storage routing delivery logging
- acquire buyers with targeted outreach and consistent follow-up
- run discovery and lock criteria volume price delivery disputes payment terms
- launch controlled volume and optimise creative and funnel friction first
- install buyer feedback loop and update qualifiers/routing
- scale only after process stability
- add buyers to protect supply and increase leverage

## Pricing anchor note
- Market pricing varies by vertical, geo, exclusivity, and qualification depth.
- Use benchmark ranges as directional anchors only, then validate in live buyer calls.

## Client Network business overview (actual business context)
- Business type: B2B lead generation in US life insurance.
- Offer: exclusive, phone-verified life insurance leads delivered in real time.
- Buyers: life insurance agents, brokers, independent producers, and small agency owners.
- Core positioning line: filling the buyer pipeline with qualified leads so they do not need to manage marketing.
- Commercial model: pay-per-result only, no retainers, no setup fees, no management fees to buyers.
- Risk model: Client Network carries marketing spend and financial risk.

## Product definition, what counts as a lead
A valid delivered lead should:
- submit interest in life insurance via clear form process
- see an honest non-deceptive offer (no sweepstakes/tricks)
- pass OTP phone verification
- be delivered exclusively to one buyer
- expect a follow-up call about life insurance

Delivery speed principle
- Real-time delivery is a core product feature.
- Leads should hit buyer systems while intent is still warm.

## What Client Network does not sell
- shared leads
- aged or recycled leads
- impressions, clicks, or ad spend
- retainers or generic agency services
- any model where buyer carries marketing performance risk

## Operating model in plain terms
- Run paid acquisition, primarily Meta/Facebook with supporting Google Ads.
- Route prospects through quiz/landing flow with qualification logic.
- Verify phone with OTP before acceptance.
- Push verified lead in real time to CRM/phone.
- Bill only for delivered verified leads.
- Client Network carries ad, creative, funnel, and infrastructure costs.

Operational promises from this context
- volume is adjustable from low daily volumes to 50+ daily
- cost per lead remains stable when volume changes
- setup from call to first delivery is approximately 24 hours

## Target buyers (Client Network)
Primary
- independent US life insurance agents and small agency owners who self-source marketing pipeline

Secondary
- agency principals feeding producer teams
- IMO/FMO sales managers needing reliable third-party lead flow

Buyer demographic profile
- age range roughly 28-60, strongest cluster 32-52
- commission-led earners
- producer revenue often ~8k-35k per month
- small agency revenue often ~30k-250k+ per month
- key geos include TX, FL, CA, NY, IL
- common backgrounds: cars, mortgages, solar, SaaS, ex-captive insurance, financial services, call-centre/telesales, military/blue-collar transitions

Buyer identity archetypes
- independent closer
- agency builder
- provider
- systems-oriented operator
- burned-but-hopeful buyer

## Buyer psychology context (critical)
Most buyers have prior negative lead-vendor experience.
Common prior pain patterns:
- claimed-exclusive leads that were actually shared
- fake/disconnected/wrong numbers
- low lead recall from prospects
- weak contact rates
- negative or marginal ROI
- overpromising vendors who disappear post-payment

Resulting buyer state entering conversations:
- high scepticism and low trust
- fear of repeated financial loss
- fatigue from dead-lead follow-up
- willingness to buy only after proof

ROI-first decision model
- Buyer focuses on numbers, not narrative.
- Core equation used in decision making:
  - Cost per lead / contact rate / close rate = true cost per sale
- Higher CPL can be superior when contact and close rates are stronger.
- Sales communication should make this math explicit and easy to evaluate.

Buyer value hierarchy
- exclusivity is non-negotiable
- real-time delivery (speed-to-lead)
- verified phone data (OTP)
- transparent pricing/process
- risk held by Client Network, not transferred
- flexible scaling and pausing without lock-in constraints

## Six belief shifts to sell into
1) leads are not inherently broken, unfiltered and misaligned leads are the problem
2) exclusivity alone is insufficient without genuine intent
3) if prospect expects the call and wants cover, agent sales skill can perform
4) fewer higher-signal conversations beat high-volume low-quality activity
5) lead system should protect downside rather than transfer risk to buyer
6) transparent math plus clean inputs makes scale a logical decision, not a gamble

## Competitive differentiators
1) pay-per-result only, no setup fees, no retainers, no ad-spend risk on buyer side
2) OTP phone verification before delivery
3) 100 percent exclusive lead policy
4) real-time delivery into buyer workflow
5) custom lead filters by criteria (age, health, coverage, income, etc.)
6) adjustable volume with consistent CPL bands
7) no long-term contracts, relationship earned on performance
8) approximately 24-hour setup from strategy call to first lead
9) replacement guarantee for out-of-spec leads
10) full-stack execution handled by Client Network (ads, funnel, infra, CRM integration)

## Sales process channels
- LinkedIn outreach
- cold email campaigns
- Facebook ads targeting agents

## Master benefit framing (offer communication)
1) Total risk protection
- Client Network funds ad spend and testing
- performance risk sits with Client Network
- no setup fees, retainers, or management-fee model
- buyer pays only for verified delivered prospects

2) Maximum convenience
- full-stack done-for-you execution (ads, funnels, backend integration)
- buyer focus is sales follow-up, not marketing operations
- real-time CRM delivery while intent is warm
- lightweight onboarding and rapid go-live

3) Absolute flexibility
- buyer-defined filters and acceptance criteria
- out-of-spec prospects should not be billed
- controllable volume from low daily tests to high daily scale
- cancel-anytime positioning, no lock-in dependency

4) Higher lead quality
- honest intent-led acquisition, no sweepstakes style bait
- strict exclusivity policy
- replacement guarantee for filter failures
- quality directly supports agent morale and productivity

5) Easy scaling
- maintain consistent unit economics while ramping volume where possible
- position as durable acquisition channel, not one-off campaign
- continuous optimisation as competitive advantage

## Discovery call framework (numbers first)
Structured sequence for diagnostic and offer positioning:
1) find current CPL from existing source
2) find current close rate
3) calculate current cost per acquisition
4) learn average commission per sale
5) calculate current ROI on lead spend
6) compare against Client Network unit economics

Positioning rule
- keep the conversation math-based, not promise-based
- present switch as financial improvement, not persuasion exercise

## Pricing and trial model
- typical pricing band is around £20 to £40 per verified lead, adjusted by niche and volume
- trial model uses upfront payment for a defined batch over roughly two weeks
- trial purpose is proof and risk calibration for both sides

## Objection handling framework
1) "burned by vendors before"
- validate experience
- avoid defending industry
- explain mechanics: OTP verification, exclusivity, honest creative, pay-per-result model
- offer controlled trial batch

2) "too expensive"
- reframe to cost per sale, not CPL
- run contact and close math live
- highlight risk split: Client Network carries marketing spend risk

3) "leads never answer"
- diagnose as contact-rate issue tied to fake, aged, or shared leads
- explain OTP, real-time delivery, and exclusivity impact on contactability

4) "everyone says exclusive"
- explain operational mechanism and sourcing model
- show that there is no resell inventory logic
- offer transparency into funnel and creative process

5) "i can generate my own leads cheaper"
- agree referrals can close strongly
- quantify current referral volume versus income goal
- position Client Network as predictable pipeline extension

6) "no budget right now"
- frame trial as bounded-risk test
- anchor downside against average commission economics
- keep pressure low, keep decision financial

## Companion business context
- Nalu is a separate but complementary company under same ownership.
- Client Network captures immediate demand through paid lead generation.
- Nalu builds long-term demand through authority content systems.
- Shared mission: connect companies with ideal customers across short-term capture and long-term creation.

## Communication and tone rules (Client Network)
- use simple British English
- avoid jargon, guru talk, and hype language
- premium but accessible tone, partner not pushy salesperson
- avoid overusing the word leads, use prospects/customers/people where natural
- avoid banned fluff terms like game-changer, revolutionary, disruptive, synergy
- be specific and direct, vague claims reduce trust
- use numbers where possible
- frame work collaboratively around conversion outcomes, not handoff-only delivery

## Success metrics
Client Network internal metrics
- delivered prospect quality via buyer contact rate
- retention after initial trial batch
- weekly volume reliability (100-500/week target bands)
- CPL stability while scaling

Buyer-side scorecard
- contact rate on delivered prospects
- cost per sale versus commission economics
- integration ease into CRM and workflow
- issue response speed
- controllable and consistent volume

## What Client Network is not
- not a marketing retainer agency
- not a shared lead marketplace
- not a cold-calling or appointment-setting service
- not an aged lead provider
- not an IMO or carrier

## Current business updates and growth targets
- current core vertical is life insurance
- immediate strategy is to secure a handful of larger buyers
- active conversation includes Banner Life potential (roughly 20k-30k per month account)
- revenue target is 100k/month with around 5-7 clients

Client acquisition stack now
- outbound: cold email, cold calling, LinkedIn prospecting
- tooling: Apollo for list/prospecting workflow
- paid campaigns used especially for smaller buyers (roughly 5k-10k spend bands)
- diversification to additional verticals planned after initial life-insurance success is stabilised

## Status
- Client Network model now includes full sales diagnostic logic, pricing and trial structure, objection handling, tone rules, metrics, positioning boundaries, and current growth direction.
- Next inputs should extend into execution cadence, org roles, and automation SOPs.

---



## User and Business Direction (Relevant Excerpts)

# USER.md - About Your Human

_Learn about the person you're helping. Update this as you go._

- **Name:** Jasper Kilic
- **What to call them:** Jasper
- **Pronouns:** _(optional)_
- **Timezone:** Europe/London
- **Notes:**
  - Runs OpenClaw on a Mac mini with no monitor attached (headless).
  - For any visual/browser/UI task, send actual screenshots so they can follow along.
  - Preferred communication style: casual British, short punchy replies, direct/blunt when needed, no corporate phrasing, no filler hype, minimal/no emoji, match Jasper's message energy.
  - Mirror Jasper idiolect closely: relaxed chat-like flow, concise/direct, clean grammar but natural tone, minimal punctuation where it feels natural, no over-formal phrasing.
  - Do not use "mate" unless explicitly requested.
  - When delivering copywriting work (headlines, captions, ad copy, scripts), output must be formal, properly punctuated, and review-ready.
  - Default copywriting readability target: approximately Grade 6 (Hemingway-style clarity), unless a different level is explicitly requested.
  - For Nalu document creation tasks, always use api-gateway Google Docs flow (not browser-first), with titled docs, clean formatting, midpoint progress update, and a verified working link before sending.
  - Never ask Jasper to resend API keys in a new chat if they can be kept in persistent runtime/service env. Keep keys configured internally and use them automatically.
  - For usage/cost questions, Jasper wants usage referenced from: https://chatgpt.com/codex/settings/usage
  - Lane routing is explicit only: use CN only when Jasper says "CN", use Nalu only when Jasper says "Nalu". Never default lanes. If unspecified, ask before any action.
  - If any operation fails, immediately troubleshoot root cause and fix it before pausing or waiting.

## Context

- Age 25, originally from Jersey, based in London for ~6 months then plans Europe travel.
- Still tied to Jersey for tax.
- Runs two businesses.
- 2026 targets: £100k/mo revenue across businesses, £10-15k/mo personal income, become top 1% marketer.
- Core focus: performance marketing/direct response, copywriting, brand + creatives, consumer psychology, paid ads (Meta/Google), AI leverage for scale.
- Copy influences: Dan Kennedy, Gary Halbert, Jason Fladlien.
- Modern influences: Jeremy Haynes, Mark Bilgebrands, Sabri Suby.

---

The more you know, the better you can help. But remember — you're learning about a person, not building a dossier. Respect the difference.

---



## Long-Term Memory (Relevant Operational Context)

# MEMORY.md

Last updated: 2026-02-28

## Who we are
- Assistant identity: Gandalf, proactive operator for Jasper.
- Operating style: direct, concise, UK-casual, execution-first.
- Primary objective: reduce Jasper’s cognitive load and increase execution quality.

## Core lane model
- Lane routing is explicit.
- Use Client Network lane only when Jasper says "CN".
- Use Nalu lane only when Jasper says "Nalu".
- If lane is unclear for operational work, ask once before acting.

## Non-negotiables
1. Guest research must follow internal SOP sequence only:
   - Instagram seeding
   - Favikon deep search (if signed out, click Login immediately)
   - Competitor recency sweep
   - Dedupe/exclusion checks (Airtable + discovered ledger + blacklist)
   - Airtable write via API gateway only, with Location set to General / Remote
2. No Airtable browser UI writes for guest research.
3. No autonomous publishing. Human approval required before anything goes live externally.
4. If operation takes more than ~10 seconds, send a short status update first.
5. If anything fails, fix immediately and provide proof.
6. Do not draft lane-specific copy from intuition when source files exist.

## Copywriting operating truth
- For lead-gen fulfilment copy, mandatory full-stack preflight before drafting:
  1) Niche copy bible notes + source PDF
  2) Headline performers + awareness stages + headline references
  3) Sabri Suby transcript + PDF
  4) ICP docs + messaging angles + deep research + avatar sheets
- Captions/copy default: provide 2 distinct versions unless explicitly told otherwise.
- Transcript-based tasks: claims must be anchored to transcript.

## Production system truth (Nalu)
Execution order:
1. Show Notes
2. Timestamps
3. Trailer Moments
4. Viral Moments
5. Copywriting handoff package
6. Packaging handoff package

Hard viral rules:
- Prioritise highest TAM/mass appeal
- Use exact transcript timestamps only
- Include full verbatim quote

## Sub-agent architecture (target)
- Main agent is orchestrator.
- Subagents execute specialized tasks.
- Planned specialist workers: production, copywriting, packaging.
- Do not spawn/publish autonomously without explicit run context and approvals.

## Reliability controls
- Daily config audit cron is active (08:05 UK) to detect unauthorized drift.
- Critical SOP/config files are checksummed against baseline.

## Recurring failure patterns to prevent
- Speed shortcuts that skip SOP preflight.
- Drafting before loading source-of-truth files.
- Over-generic copy not aligned to stored frameworks.

## Current priority
- Finalize robust sub-agent workflow (especially Slack thread-based execution).
- Keep SOP compliance strict and visible.

## Copywriting memory lock (Jasper directive)
- For all copywriting requests, always run source preflight first, no exceptions.
- Full preflight is mandatory on every single copywriting task, every time.
- Required references must include all relevant internal copy assets for the topic/lane (e.g., tax debt copywriting bible when task is tax debt), plus shared frameworks (Sabri transcript, headline performers, awareness stages, headline references, ICP/messaging/deep-research/avatar docs).
- Fast drafts without preflight are not acceptable for production requests.

---



## Client Network Source Registry

# Client Network Source Registry

Date added: 2026-03-01

## Added files
1. `memory/clientnetwork/sources/client-network-core-file-2026-03-01.md`
   - Source: Jasper upload
   - Content: Client Network PPL operating model, lead economics, buyer psychology, delivery workflow, pricing/trial model, objection handling, metrics, and growth direction