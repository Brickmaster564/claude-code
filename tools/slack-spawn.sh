#!/bin/bash
# Self-contained Claude spawner for Slack listener.
# Runs Claude, then posts completion/failure back to Slack.
# Designed to survive listener restarts (runs in own session).
#
# Usage: slack-spawn.sh <skill_name> <channel> <thread_ts> <log_file> <prompt>

set -uo pipefail

# Ensure tools are on PATH
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/Users/jasper/.local/bin:$PATH"
unset CLAUDECODE 2>/dev/null || true

SKILL_NAME="$1"
CHANNEL="$2"
THREAD_TS="$3"
LOG_FILE="$4"
PROMPT="$5"

WORKDIR="/Users/jasper/Library/Application Support/Claude/Jasper OS - CC Hub"
START_TIME=$(date +%s)

# Always clean up PID file on exit (normal, error, or signal)
cleanup() {
  rm -f "/tmp/slack-listener-pids/${SKILL_NAME}.pid"
}
trap cleanup EXIT

cd "$WORKDIR" || exit 1

# Run Claude with a 25-minute timeout (reaper kills at 30, so this fires first)
timeout 1500 claude \
  --print \
  --dangerously-skip-permissions \
  --max-budget-usd 10 \
  "$PROMPT" \
  >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

# Calculate duration
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINS=$((ELAPSED / 60))
SECS=$((ELAPSED % 60))
DURATION="${MINS}m ${SECS}s"

# Post completion notification back to Slack (reply in the trigger thread)
if [ $EXIT_CODE -eq 0 ]; then
  python3 tools/slack.py reply \
    --channel "$CHANNEL" \
    --thread-ts "$THREAD_TS" \
    --text "${SKILL_NAME} completed successfully (${DURATION})." \
    >> "$LOG_FILE" 2>&1 || true
else
  python3 tools/slack.py reply \
    --channel "$CHANNEL" \
    --thread-ts "$THREAD_TS" \
    --text "${SKILL_NAME} failed (exit code ${EXIT_CODE}, ${DURATION}). Check logs: ${LOG_FILE}" \
    >> "$LOG_FILE" 2>&1 || true
fi

echo "$(date): ${SKILL_NAME} finished with exit code ${EXIT_CODE} (${DURATION})" >> "$LOG_FILE"
# PID file cleanup handled by EXIT trap
