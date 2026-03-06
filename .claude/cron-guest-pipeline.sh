#!/bin/bash
# Cron launcher for Guest Pipeline (FTT)
# Runs twice weekly (Monday and Thursday) at 10 AM via crontab
#
# Usage: ./cron-guest-pipeline.sh
# Crontab: 0 10 * * 1,4 /path/to/cron-guest-pipeline.sh

set -euo pipefail

WORKDIR="/Users/jasper/Library/Application Support/Claude/Jasper OS - CC Hub"
LOGDIR="/tmp/claude-guest-pipeline"
LOGFILE="${LOGDIR}/$(date +%Y%m%d-%H%M).log"

mkdir -p "$LOGDIR"

echo "$(date): Starting FTT guest pipeline" >> "$LOGFILE"

cd "$WORKDIR"

# Notify Slack that the cron job has started
python3 tools/slack.py send --channel "C089HSD8US1" \
  --text "Cron started: Guest Pipeline (FTT). Running full 30-candidate pipeline now..." \
  >> "$LOGFILE" 2>&1

/Users/jasper/.local/bin/claude \
  --print \
  --dangerously-skip-permissions \
  "Run /guest-pipeline for FTT. Follow the skill instructions exactly. Write all qualified candidates to Airtable and send the Slack summary." \
  >> "$LOGFILE" 2>&1

echo "$(date): Finished FTT guest pipeline" >> "$LOGFILE"
