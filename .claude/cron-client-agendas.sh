#!/bin/bash
# Cron launcher for Client Agendas (Nalu)
# Runs every Thursday at 8PM UK time via crontab
#
# Usage: ./cron-client-agendas.sh
# Crontab: 0 20 * * 4 /path/to/cron-client-agendas.sh

set -euo pipefail

WORKDIR="/Users/jasper/Library/Application Support/Claude/Jasper OS - CC Hub"
LOGDIR="/tmp/claude-client-agendas"
LOGFILE="${LOGDIR}/$(date +%Y%m%d-%H%M).log"

mkdir -p "$LOGDIR"

echo "$(date): Starting client agendas" >> "$LOGFILE"

cd "$WORKDIR"

# Notify Slack that the cron job has started
python3 tools/slack.py send --channel "C08P14TTBA7" \
  --text "Cron started: Client Agendas. Preparing weekly agendas for all clients now..." \
  >> "$LOGFILE" 2>&1

/Users/jasper/.local/bin/claude \
  --print \
  --dangerously-skip-permissions \
  --max-budget-usd 10 \
  "Run /client-agendas for all clients. Follow the skill instructions exactly. Poll the Slack thread for Scott's replies - wait 60 seconds between polls. Process Dom first, then Jeremy." \
  >> "$LOGFILE" 2>&1

echo "$(date): Finished client agendas" >> "$LOGFILE"
