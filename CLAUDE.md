# Jasper OS — CC Hub

Universal workspace for Client Network, Nalu, and personal automation. Combines skills (expertise layers) with workflows (process orchestration) under one roof.

## Writing Rules (Zero Tolerance)

- **NEVER use em dashes (—).** Use colons, commas, periods, or restructure the sentence. Applies to all output without exception.
- **NEVER write staccato sentence fragments.** No short punchy sentences under 5 words, especially in sequence (e.g. "That ends." / "Simple. Clean. Done." / "Post consistently. See what works."). Combine them into proper sentences. Applies to all output without exception.

## Tool Discovery Protocol (Zero Tolerance)

Before declaring ANY capability unavailable or asking Jasper to provide data manually, check all three layers:

1. **Local scripts:** `ls tools/` + run `--help` on candidates. Full map in `resources/tool-capability-map.md`.
2. **Deferred MCP tools:** Check system reminder for deferred tools. Use ToolSearch with `select:` and keyword variants.
3. **Memory:** Check MEMORY.md Service Integrations for credentials and tool references.

**NEVER** suggest copy-paste, manual download, or "provide it here" when a tool can retrieve the data.

## Quick Start

```bash
python3 tools/<tool>.py --help
```

**Environment:** Python 3. Credentials in `config/api-keys.json` (gitignored). OAuth tokens in `config/google-token*.json`.

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

## Skills

| Skill | Purpose | Triggers |
|-------|---------|----------|
| `/skills-builder` | Build, optimize, or audit Claude Code skills | "build a skill", "optimize skill" |
| `/copywriter` | Research-gated copy for CN verticals and Nalu | "write copy for...", "draft headlines for..." |
| `/yt-packaging` | Extract high-ceiling concepts + YouTube titles from transcripts | "package this episode", "YouTube titles from transcript" |
| `/niche-setup` | Build foundational resource library for new CN vertical | "set up a new niche", "niche setup [vertical]" |
| `/morning-coffee` | Daily intel briefing (copywriting, AI, X, BHW) | "run morning coffee", "daily briefing" |
| `/bhw-intel` | BlackHatWorld Meta bulletproofing scan | "run bhw intel", "meta underground" |
| `/youtube-transcript` | Download YouTube video transcripts | YouTube URL provided |
| `/guest-pipeline` | Automated guest discovery for Nalu podcast clients | "find podcast guests", "run guest pipeline" |
| `/ad-creatives` | Ad creative workshop (5 modes) for CN | "create ads for...", "rehash this ad" |
| `/media-buyer` | Meta Ads co-pilot (reports, operations, optimization) | "check ad performance", "media buyer report" |
| `/outreach-retarget` | Weekly Instantly completed-sequence retargeting scan | "run outreach retarget" |

Each skill has full docs in `.claude/skills/<name>/SKILL.md`, loaded automatically on invocation.

## Workflows

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| Prospector (`workflows/prospector.md`) | Apollo > email verify > Instantly pipeline for CN leads | "run prospector", "prospect [vertical]" |
| Lead Replenish (`workflows/lead-replenish-outbound.md`) | Replenish completed Instantly leads via Apollo + route LinkedIn posters to Lemlist | "lead replenish [vertical]" |

## Paid Advertising — Client Network

### Business Model
PPL (pay-per-lead) lead generation. Ads drive prospects into quiz/landing funnel with OTP phone verification, then real-time delivery to insurance agents/brokers.

- **Primary KPIs:** CPL, qualified lead rate, contact rate (NOT ROAS)
- **Primary platform:** Meta (Facebook + Instagram)

### Verticals

| Vertical | Resource Path | Compliance |
|---|---|---|
| Life Insurance | `resources/client-network/life-insurance/` | Restricted on Meta. No income claims, disclaimers required |
| Senior Care | `resources/client-network/senior-care/` | Sensitive category. Avoid exploitative framing |
| Home Security | `resources/client-network/home-security/` | Standard category |
| Tax Relief | `resources/client-network/tax-relief/` | Financial services. No relief guarantees |
| Gold IRA | `resources/client-network/gold-ira/` | Investment category. No return guarantees |

### Meta Infrastructure Docs
- Handbook: `resources/paid-advertising/meta-advertising-handbook.md`
- Campaign playbook: `resources/paid-advertising/meta-campaign-playbook.md`
- Recovery SOP: `resources/paid-advertising/meta-recovery-sop.md`
- Domain/pixel strategy: `resources/paid-advertising/meta-multi-vertical-domain-strategy.md`

## Operating Rules

1. **Check `tools/` first.** Only create new scripts when nothing exists for the task.
2. **Learn from failures.** Fix, retest, document. If a tool uses paid API calls, check with Jasper before re-running.
3. **Keep workflows current.** Update when methods improve or constraints emerge. Never create/overwrite without asking.
4. **Update the Tracker** after every skill/workflow creation or significant update. [Google Sheet](https://docs.google.com/spreadsheets/d/1bypUOLHBBG9E5X0Gxpx4tLT45pGbgIj5hEPfCSB36js) (Tracker tab, gid=1439128365). Columns: Name, Type, Status, Description, Steps.
5. **File handling:** Deliverables to cloud/`output/`. Intermediates to `.tmp/`. Credentials in `config/` only.

## Proactive Automation Thinking

Flag processes that could become workflows when:
- A task repeats with the same structure
- Multiple manual steps could be chained
- Data moves between systems by hand
- Jasper is doing coordination work that could be orchestrated

Don't build unsolicited. Flag, explain value, wait for go-ahead.

## Coding Principles (Karpathy Skills)

Behavioral guidelines to reduce common LLM coding mistakes. Bias toward caution over speed; for trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them, don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it, don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" -> "Write tests for invalid inputs, then make them pass"
- "Fix the bug" -> "Write a test that reproduces it, then make it pass"
- "Refactor X" -> "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
