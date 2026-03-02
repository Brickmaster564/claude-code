# A Bunch of Skills

Custom Claude Code skills for Client Network and Nalu.

## Project Structure

```
.claude/skills/       — Skill definitions (SKILL.md per skill)
config/               — API keys and credentials (gitignored)
resources/            — Reference material for skills
  general/            — Shared copywriting frameworks & swipe files
  client-network/     — Per-vertical resources (life-insurance, tax-relief, etc.)
  nalu/               — Nalu podcast agency resources
output/               — Skill output files
```

## Available Skills

### `/skills-builder`
Build, optimize, or audit Claude Code skills following official best practices.

### `/copywriter`
Research-gated copywriter for Client Network (lead gen verticals) and Nalu (podcast agency). Produces channel-specific, framework-driven copy backed by VOC data, offer architecture, and awareness mapping.

- **Triggers:** "write copy for...", "create an ad for...", "draft headlines for..."
- **Resources:** `resources/client-network/{vertical}/`, `resources/nalu/`, `resources/general/`

### `/youtube-transcript`
Download transcripts from YouTube videos.
