#!/bin/bash
# Cron launcher for Guest Pipeline (Jeremy Harbour / Deal Junky)
# Runs weekly on Thursday at 3 PM UK time via crontab
#
# Usage: ./cron-guest-pipeline-jh.sh
# Crontab: 0 15 * * 4 /path/to/cron-guest-pipeline-jh.sh

set -euo pipefail

WORKDIR="/Users/jasper/Library/Application Support/Claude/Jasper OS - CC Hub"
LOGDIR="/tmp/claude-guest-pipeline-jh"
LOGFILE="${LOGDIR}/$(date +%Y%m%d-%H%M).log"

mkdir -p "$LOGDIR"

echo "$(date): Starting Deal Junky (Jeremy Harbour) guest pipeline" >> "$LOGFILE"

cd "$WORKDIR"

/Users/jasper/.local/bin/claude \
  --print \
  --dangerously-skip-permissions \
  "Run /guest-pipeline for jh. Follow the skill instructions exactly. Write all qualified candidates to Airtable and send the Slack summary." \
  >> "$LOGFILE" 2>&1

echo "$(date): Finished Deal Junky guest pipeline" >> "$LOGFILE"
