#!/bin/bash
# Injects tool inventory into model context at SessionStart and PostCompact.
# Prevents the model from forgetting available tools after context compression.
EVENT_NAME="${1:-SessionStart}"
TOOLS=$(ls "$CLAUDE_PROJECT_DIR/tools/"*.py 2>/dev/null | while read f; do basename "$f" .py; done | paste -sd, -)
printf '{"hookSpecificOutput":{"hookEventName":"%s","additionalContext":"[TOOL INVENTORY] Local: %s. MCP: Airtable, Apollo, Gmail, Calendar, Slack, Notion. Deferred: WebSearch, WebFetch. All local tools support --help. Google tools support --account cn|nalu. Check all 3 layers before suggesting workarounds."}}\n' "$EVENT_NAME" "$TOOLS"
