#!/bin/bash
# Cron launcher for Lead Replenish Outbound workflow
# Called by crontab with a vertical name as argument
#
# Usage: ./cron-replenish.sh life-insurance
#        ./cron-replenish.sh senior-care
#        ./cron-replenish.sh home-security

set -euo pipefail

VERTICAL="${1:?Usage: cron-replenish.sh <vertical>}"
WORKDIR="/Users/jasper/Library/Application Support/Claude/Jasper OS - CC Hub"
LOGDIR="/tmp/claude-replenish"
LOGFILE="${LOGDIR}/${VERTICAL}-$(date +%Y%m%d-%H%M).log"

mkdir -p "$LOGDIR"

echo "$(date): Starting lead replenish outbound for ${VERTICAL}" >> "$LOGFILE"

cd "$WORKDIR"

/Users/jasper/.local/bin/claude \
  --print \
  --dangerously-skip-permissions \
  --max-budget-usd 5 \
  "Run lead replenish outbound for ${VERTICAL}. FIRST, send a Slack message to #client-network-hub (via Slack MCP) saying 'Cron started: Lead Replenish Outbound (${VERTICAL}). Scanning campaigns and finding fresh leads now...' Then follow the workflow in workflows/lead-replenish-outbound.md exactly. Read the config from config/replenisher.json. When done, send the full Slack summary to #client-network-hub (via Slack MCP) including: leads scanned, target companies, new prospects found, verified count, loaded to Instantly, loaded to Lemlist, skipped, and the full leads table. This is the completion notification so include everything." \
  >> "$LOGFILE" 2>&1

echo "$(date): Finished lead replenish outbound for ${VERTICAL}" >> "$LOGFILE"
