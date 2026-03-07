#!/bin/bash
# Cron launcher for Outreach Retarget (all clients)
# Runs weekly on Sundays at 9 AM UK via crontab
#
# Usage: ./cron-outreach-retarget.sh
# Crontab: 0 9 * * 0 /path/to/cron-outreach-retarget.sh

set -euo pipefail

# Ensure tools are on PATH (cron runs with minimal env)
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export PATH="/Users/jasper/.local/bin:$PATH"

# Prevent nested Claude session errors
unset CLAUDECODE 2>/dev/null || true

WORKDIR="/Users/jasper/Library/Application Support/Claude/Jasper OS - CC Hub"
LOGDIR="/tmp/claude-outreach-retarget"
LOGFILE="${LOGDIR}/$(date +%Y%m%d-%H%M).log"

mkdir -p "$LOGDIR"

echo "$(date): Starting outreach retarget (all clients)" >> "$LOGFILE"

cd "$WORKDIR"

# Notify Slack that the cron job has started
python3 tools/slack.py send --channel "C089HSD8US1" \
  --text "Cron started: Outreach Retarget (all clients). Scanning completed leads now..." \
  >> "$LOGFILE" 2>&1 || true

claude \
  --print \
  --dangerously-skip-permissions \
  "Run /outreach-retarget for all. Follow the skill instructions exactly. Update matched records in Airtable and send the Slack summary for each client." \
  >> "$LOGFILE" 2>&1

echo "$(date): Finished outreach retarget (all clients)" >> "$LOGFILE"
