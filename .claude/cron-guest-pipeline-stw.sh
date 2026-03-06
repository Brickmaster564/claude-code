#!/bin/bash
# Cron launcher for Guest Pipeline (Scale to Win / Dominic Munkhouse)
# Runs weekly on Tuesday at 10 AM UK time via crontab
#
# Usage: ./cron-guest-pipeline-stw.sh
# Crontab: 0 10 * * 2 /path/to/cron-guest-pipeline-stw.sh

set -euo pipefail

WORKDIR="/Users/jasper/Library/Application Support/Claude/Jasper OS - CC Hub"
LOGDIR="/tmp/claude-guest-pipeline-stw"
LOGFILE="${LOGDIR}/$(date +%Y%m%d-%H%M).log"

mkdir -p "$LOGDIR"

echo "$(date): Starting Scale to Win (Dominic Munkhouse) guest pipeline" >> "$LOGFILE"

cd "$WORKDIR"

/Users/jasper/.local/bin/claude \
  --print \
  --dangerously-skip-permissions \
  "Run /guest-pipeline for stw. Follow the skill instructions exactly. Write all qualified candidates to Airtable and send the Slack summary." \
  >> "$LOGFILE" 2>&1

echo "$(date): Finished Scale to Win guest pipeline" >> "$LOGFILE"
