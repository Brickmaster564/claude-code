#!/bin/bash
# Cron launcher for Morning Coffee daily briefing
# Runs at 7:45 AM daily via crontab
#
# Usage: ./cron-morning-coffee.sh
# Crontab: 45 7 * * * /path/to/cron-morning-coffee.sh

set -euo pipefail

WORKDIR="/Users/jasper/Library/Application Support/Claude/Jasper OS - CC Hub"
LOGDIR="/tmp/claude-morning-coffee"
LOGFILE="${LOGDIR}/$(date +%Y%m%d-%H%M).log"

mkdir -p "$LOGDIR"

echo "$(date): Starting morning coffee briefing" >> "$LOGFILE"

cd "$WORKDIR"

# Notify Slack that the cron job has started
python3 tools/slack.py send --channel "C08P14TTBA7" \
  --text "Cron started: Morning Coffee. Compiling daily briefing now..." \
  >> "$LOGFILE" 2>&1

/Users/jasper/.local/bin/claude \
  --print \
  --dangerously-skip-permissions \
  --max-budget-usd 3 \
  "Run /morning-coffee. Follow the skill instructions exactly. Save the swipe file and send the email." \
  >> "$LOGFILE" 2>&1

echo "$(date): Finished morning coffee briefing" >> "$LOGFILE"
