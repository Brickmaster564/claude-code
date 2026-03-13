# Jasper OS — CC Hub

Universal workspace for Client Network, Nalu, and personal automation. Combines skills (expertise layers) with workflows (process orchestration) under one roof.

## Project Structure

```
.claude/skills/       — Skill definitions (SKILL.md per skill)
config/               — API keys and credentials (gitignored)
resources/            — Reference material for skills and workflows
  general/            — Shared copywriting frameworks & swipe files
  client-network/     — Per-vertical resources (life-insurance, tax-relief, etc.)
  nalu/               — Nalu podcast agency resources
output/               — Skill and workflow output files
workflows/            — Workflow SOPs (markdown process definitions)
tools/                — Python scripts for deterministic workflow execution
.tmp/                 — Temporary processing files (gitignored, regenerable)
```

## Available Skills

### `/skills-builder`
Build, optimize, or audit Claude Code skills following official best practices.

### `/copywriter`
Research-gated copywriter for Client Network (lead gen verticals) and Nalu (podcast agency). Produces channel-specific, framework-driven copy backed by VOC data, offer architecture, and awareness mapping.

- **Triggers:** "write copy for...", "create an ad for...", "draft headlines for..."
- **Resources:** `resources/client-network/{vertical}/`, `resources/nalu/`, `resources/general/`

### `/yt-packaging`
Analyzes a podcast transcript to extract 3-5 high-ceiling concepts (with micro sub-themes and verbatim quotes), ranks them by click potential, and generates 5-10 YouTube title options based on proven conventions. Built for Nalu client episodes.

- **Triggers:** "package this episode", "find high-ceiling concepts", "create YouTube titles from transcript"
- **Resources:** `resources/nalu/yt-headlines-swipe-file.md`, `resources/general/copywriting-resources/headline-performers.md`, `resources/general/copywriting-resources/headlines-swipe-file-dna.md`

### `/niche-setup`
Researches and builds the complete foundational resource library for a new Client Network lead gen vertical. Produces 10 source-of-truth documents matching the quality and structure of existing verticals, then uploads to Google Drive.

- **Triggers:** "set up a new niche", "build resources for [vertical]", "research [vertical] for lead gen", "niche setup [vertical]"
- **Phases:** Market Research > Audience & Competitor Deep Dive > Synthesis (review between each)
- **Outputs:** `resources/client-network/{vertical}/` (local) + Google Drive `Lead Gen Brands/{Vertical}/Foundational Docs/` (Google Docs)
- **Dependencies:** WebSearch, WebFetch, Sabri Suby resources, existing vertical templates, Google Drive API

### `/morning-coffee`
Daily intelligence briefing covering copywriting wisdom, AI news, X/Twitter insights from tracked marketers, and BlackHatWorld gems. Runs as a 7:45 AM cron job or manually.

- **Triggers:** "run morning coffee", "daily briefing", "morning intel"
- **Outputs:** Email (hello@clientnetwork.io → Jasperkilic10@gmail.com) + `output/morning-coffee/YYYY-MM-DD.md`
- **Dependencies:** WebSearch, WebFetch, Apify (X scraper), `tools/gmail.py`
- **Cron:** `cron-morning-coffee.sh` at 7:45 AM daily

### `/bhw-intel`
Scans BlackHatWorld's Facebook and paid advertising subforums for Meta bulletproofing tactics and ad performance insights. Tuned to Jasper's setup (aged US accounts, AdsPower profiles, BM sharing).

- **Triggers:** "run bhw intel", "black hat world scan", "meta underground"
- **Outputs:** Email (hello@clientnetwork.io → Jasperkilic10@gmail.com) + `output/bhw-intel/YYYY-MM-DD.md`
- **Dependencies:** WebSearch, WebFetch, `tools/gmail.py`
- **Cron:** `cron-bhw-intel.sh` Mon / Thu / Sun 9 AM

### `/youtube-transcript`
Download transcripts from YouTube videos.

### `/guest-pipeline`
Automated guest discovery pipeline for Nalu podcast clients. Runs 5 research methods (competitor podcast scraping, seed-based lookalikes, Instagram discovery, listicle mining, book/media trending), deduplicates against Airtable, enforces diversity quotas, and writes 30 qualified candidates per run.

- **Triggers:** "find new podcast guests", "run guest pipeline", "guest research for [client]", "refresh guest list"
- **Clients:** FTT (Mike Thurston), Scale to Win (Dominic Munkhouse), Jeremy Harbour
- **Outputs:** Records in client's Airtable guest tracker + Slack summary to #nalu-hub + `output/guest-pipeline/YYYY-MM-DD.json`
- **Dependencies:** WebSearch, WebFetch, Apify (Instagram), Airtable MCP, `tools/apify.py`, `tools/slack.py`
- **Cron:** `cron-guest-pipeline.sh` Monday + Thursday 10 AM

### `/ad-creatives`
Universal ad creative workshop for Client Network. Four modes: copy rehash, full ad creative generation, UGC AI characters, and video script rehash. Conversational and interactive. Loads vertical-specific resources and copywriting frameworks automatically.

- **Triggers:** "create ads for...", "rehash this ad", "generate ad images", "create a UGC character", "rewrite this video script for..."
- **Modes:** Copy-Only, Full Ad Creative, UGC AI Character, Video Script Rehash
- **Dependencies:** `tools/higgsfield.py` (Kie.ai API), copywriter resources, vertical resources
- **Image Gen:** Nano Banana Pro via Kie.ai (2 variants per run, 2K default)

---

## Paid Advertising Skills — Client Network Context

18 specialist `/ads-*` skills are installed. When running any of them for Client Network, apply the context below. These skills are optimised for e-commerce by default — the CN adaptations below override that default behaviour.

### Business Model Override
Client Network is a **PPL (pay-per-lead) lead generation** business, not e-commerce. All ads drive prospects into a quiz/landing funnel that qualifies and phone-verifies them before delivering to insurance agents or brokers.

- **Primary KPIs:** CPL (cost per lead), qualified lead rate, contact rate. NOT ROAS.
- **Funnel:** Ad → Quiz/landing page → OTP phone verification → real-time delivery to buyer
- **Primary platform:** Meta (Facebook + Instagram). Secondary: Google Search, YouTube, native.
- **Brand profile:** `resources/client-network/brand-profile.json` — load this before any `/ads-create` or `/ads-generate` run.

### Verticals & Resources
Always load the relevant vertical's `copywriting-bible.md`, `voc.md`, and `ad-copy-swipe-file.md` before auditing or generating creative.

| Vertical | Resource Path | Compliance |
|---|---|---|
| Life Insurance | `resources/client-network/life-insurance/` | Restricted on Meta — no income claims, honest intent, disclaimers required |
| Senior Care | `resources/client-network/senior-care/` | Sensitive category — avoid exploitative framing |
| Home Security | `resources/client-network/home-security/` | Standard category |
| Tax Relief | `resources/client-network/tax-relief/` | Financial services — no relief guarantees |
| Gold IRA | `resources/client-network/gold-ira/` | Investment category — no return guarantees |

### Meta Infrastructure
Full reference docs for CN's Meta setup:
- Handbook: `resources/paid-advertising/meta-advertising-handbook.md`
- Campaign playbook: `resources/paid-advertising/meta-campaign-playbook.md`
- Recovery SOP: `resources/paid-advertising/meta-recovery-sop.md`
- Domain/pixel strategy: `resources/paid-advertising/meta-multi-vertical-domain-strategy.md`

### Skill Quick Reference
| Skill | Use When |
|---|---|
| `/ads-dna` | First run for a new CN campaign — extracts brand from clientnetwork.io, outputs `brand-profile.json` |
| `/ads-audit` | Full multi-platform account health check across active CN campaigns |
| `/ads-meta` | Deep Facebook/Instagram audit — 46 checks incl. Pixel/CAPI, creative fatigue, structure |
| `/ads-google` | Deep Google Ads audit — 74 checks across Search, PMax, YouTube |
| `/ads-create` | Campaign brief generation — reads `brand-profile.json` + vertical resources |
| `/ads-generate` | AI image generation — reads campaign brief + brand profile |
| `/ads-creative` | Creative quality audit — fatigue signals, format diversity, spec compliance |
| `/ads-budget` | Budget allocation + bidding strategy review |
| `/ads-landing` | Landing page / quiz funnel assessment |
| `/ads-competitor` | Competitor ad intelligence — find what others in the vertical are running |
| `/ads-plan` | Strategic media plan for a new vertical or campaign push |
| `/ads-copy` | Platform-compliant headlines, primary text, CTAs |

### `/outreach-retarget`
Weekly scan of Instantly outreach campaigns for podcast clients. Finds contacts who completed the sequence without responding, matches them to Airtable guest tracker records, and updates location/status to move them into a retargeting pool.

- **Triggers:** "run outreach retarget", "retarget completed guests", "check who never responded"
- **Clients:** FTT (more clients to be added)
- **Config:** `.claude/skills/outreach-retarget/config.json`
- **Outputs:** Airtable updates + Slack summary to #guest-research-and-comms + `output/outreach-retarget/YYYY-MM-DD-[client].json`
- **Dependencies:** `tools/instantly.py`, Airtable MCP, `tools/slack.py`
- **Cron:** `cron-outreach-retarget.sh` Sunday 9 AM UK (FTT)

## Available Workflows

### Prospector (`workflows/prospector.md`)
End-to-end lead generation pipeline for Client Network. Finds decision-makers in Apollo (MCP), verifies emails through MillionVerifier and BounceBan, and loads verified leads into an Instantly campaign.

- **Trigger:** "find me X leads for [vertical]", "run prospector", "prospect [vertical]"
- **Input:** lead count, vertical, Apollo list name, Instantly campaign name
- **Tools:** `tools/millionverifier.py`, `tools/bounceban.py`, `tools/instantly.py`
- **MCP:** Apollo (search, enrich, create contacts)

### Lead Replenish Outbound (`workflows/lead-replenish-outbound.md`)
Weekly automated pipeline that scans Instantly campaigns for completed leads, finds fresh contacts at the same companies via Apollo, verifies emails, loads them into Instantly, and routes active LinkedIn posters to Lemlist.

- **Trigger:** "run lead replenish outbound for [vertical]", "replenish [vertical]", "lead replenish [vertical]"
- **Input:** vertical name (must match a key in `config/replenisher.json`)
- **Config:** `config/replenisher.json` (maps verticals to campaign IDs, Apollo lists, Lemlist campaigns)
- **Tools:** `tools/instantly.py`, `tools/millionverifier.py`, `tools/bounceban.py`, `tools/apify.py`, `tools/lemlist.py`
- **MCP:** Apollo (search, create contacts), Slack (summary notification)

---

## WAT Framework (Workflows, Agent, Tools)

This workspace uses the WAT architecture to build and run automations. The core principle: probabilistic AI handles reasoning and orchestration, deterministic code handles execution. That separation is what makes things reliable.

### How the layers work

**Workflows** — Markdown SOPs in `workflows/`. Each one defines the objective, required inputs, which tools to run, expected outputs, and edge case handling. Written in plain language. Think of these as recipes.

**Agent** — That's me. I read the workflow, run tools in the correct sequence, handle failures, ask clarifying questions, and improve the system over time. I connect intent to execution without trying to do everything myself.

**Tools** — Python scripts in `tools/` that do the actual work: API calls, data transformations, file operations, external service integrations. Credentials live in `config/api-keys.json`. These scripts are consistent, testable, and fast.

### How skills and workflows coexist

| | Skills | Workflows |
|---|---|---|
| Purpose | Expertise — *how* to think about a task | Orchestration — *what steps* to run and in what order |
| Format | `SKILL.md` in `.claude/skills/` | `.md` files in `workflows/` |
| Execution | Interactive — user prompts, I follow the skill | Process — I read the SOP and chain tools together |
| Example | `/copywriter` loads frameworks, VOC, swipe files | A workflow that researches → writes → formats → sends a newsletter |

A workflow can invoke a skill as one of its steps. They're complementary, not competing.

### Operating rules

1. **Check for existing tools first.** Before building anything new, check `tools/`. Only create new scripts when nothing exists for the task.

2. **Learn and adapt when things fail.** Read the full error, fix the script, retest, and document what changed in the workflow. If a tool uses paid API calls or credits, check with Jasper before re-running.

3. **Keep workflows current.** When I find better methods, discover constraints, or hit recurring issues, update the workflow. But never create or overwrite workflows without asking unless explicitly told to.

4. **Update the Tracker after every creation or significant update.** When a new skill, workflow, or automation is created (or an existing one is significantly updated), add/update a row in the [Tracker sheet](https://docs.google.com/spreadsheets/d/1bypUOLHBBG9E5X0Gxpx4tLT45pGbgIj5hEPfCSB36js) (gid=924376767). Columns: Name, Type (Skill/Workflow), Status, Description, Steps. This is mandatory, not optional. Use the Google Sheets API with `config/google-token.json` credentials to append/update rows.

5. **Self-improvement loop.** Every failure makes the system stronger:
   - Identify what broke
   - Fix the tool
   - Verify the fix
   - Update the workflow
   - Move on with a more robust system

### Tracker Sheet

When a new skill or workflow is created (or an existing one is significantly updated), update the **Tracker** sheet in the [Jasper OS Google Sheet](https://docs.google.com/spreadsheets/d/1bypUOLHBBG9E5X0Gxpx4tLT45pGbgIj5hEPfCSB36js). Columns: Name, Type (Skill/Workflow), Status, Description, Steps (checkmark-style workflow steps matching the Cron Jobs tab format). Use the Google OAuth credentials in `config/google-token.json`.

### File handling

- **Deliverables** go to cloud services (Google Sheets, Docs, etc.) or `output/` where Jasper can access them directly.
- **Intermediates** go to `.tmp/` — these are disposable and regenerable.
- **Credentials** go in `config/api-keys.json` (for tool scripts) or `config/` (for OAuth tokens). Never store secrets anywhere else.

## Proactive Automation Thinking

When working on Client Network or Nalu tasks, actively look for processes that could become workflows. Flag opportunities where:
- A task is repeated more than twice with the same structure
- Multiple manual steps could be chained (research → format → deliver)
- Data moves between systems by hand (CRM, Sheets, email)
- Jasper is doing coordination work that could be orchestrated

Don't build workflows unsolicited — flag the opportunity, explain the value, and wait for the go-ahead.
