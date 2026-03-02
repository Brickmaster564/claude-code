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

### `/youtube-transcript`
Download transcripts from YouTube videos.

## Available Workflows

### Prospector (`workflows/prospector.md`)
End-to-end lead generation pipeline for Client Network. Finds decision-makers in Apollo (MCP), verifies emails through MillionVerifier and BounceBan, and loads verified leads into an Instantly campaign.

- **Trigger:** "find me X leads for [vertical]", "run prospector", "prospect [vertical]"
- **Input:** lead count, vertical, Apollo list name, Instantly campaign name
- **Tools:** `tools/millionverifier.py`, `tools/bounceban.py`, `tools/instantly.py`
- **MCP:** Apollo (search, enrich, create contacts)

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

4. **Self-improvement loop.** Every failure makes the system stronger:
   - Identify what broke
   - Fix the tool
   - Verify the fix
   - Update the workflow
   - Move on with a more robust system

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
