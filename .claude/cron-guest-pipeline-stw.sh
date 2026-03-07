#!/bin/bash
# Cron launcher for Guest Pipeline (Scale to Win / Dominic Munkhouse)
# Runs weekly on Tuesday at 10 AM UK time via crontab
#
# Usage: ./cron-guest-pipeline-stw.sh
# Crontab: 0 10 * * 2 /path/to/cron-guest-pipeline-stw.sh

set -euo pipefail

# Ensure tools are on PATH (cron runs with minimal env)
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export PATH="/Users/jasper/.local/bin:$PATH"

# Prevent nested Claude session errors
unset CLAUDECODE 2>/dev/null || true

WORKDIR="/Users/jasper/Library/Application Support/Claude/Jasper OS - CC Hub"
LOGDIR="/tmp/claude-guest-pipeline-stw"
LOGFILE="${LOGDIR}/$(date +%Y%m%d-%H%M).log"

mkdir -p "$LOGDIR"

echo "$(date): Starting Scale to Win (Dominic Munkhouse) guest pipeline" >> "$LOGFILE"

cd "$WORKDIR"

# Notify Slack that the cron job has started
python3 tools/slack.py send --channel "C089HSD8US1" \
  --text "Cron started: Guest Pipeline (Scale to Win / Dominic). Running full pipeline now..." \
  >> "$LOGFILE" 2>&1 || true

claude \
  --print \
  --dangerously-skip-permissions \
  "Run /guest-pipeline for stw. Follow the skill instructions exactly. Write all qualified candidates to Airtable and send the Slack summary." \
  >> "$LOGFILE" 2>&1

echo "$(date): Finished Scale to Win guest pipeline" >> "$LOGFILE"
