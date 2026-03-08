#!/bin/bash
# Cron launcher for BHW Intel briefing
# Schedule: Mon/Thu/Sun 9 AM
source "$(dirname "$0")/cron-common.sh"

init_cron "bhw-intel"

run_claude 1800 \
  "Run /bhw-intel. Follow the skill instructions exactly. Save the archive and send the email." \
  --max-budget-usd 2
