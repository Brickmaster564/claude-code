#!/usr/bin/env python3
"""PostToolUse hook: Verifies Slack sends actually succeeded.

After any tools/slack.py send or reply command, checks the output
for success indicators. Feeds failure context back to the agent
so it doesn't plow forward assuming the message was delivered.

Exit 0: Success or not a Slack send (proceed, with context if failed)
Exit 1: Non-critical issue logged
"""

import json
import sys


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = event.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    command = event.get("tool_input", {}).get("command", "")

    # Only check slack.py send/reply commands
    if "slack.py" not in command:
        sys.exit(0)
    if "send" not in command and "reply" not in command:
        sys.exit(0)

    response = event.get("tool_response", "")

    # Check for failure indicators (specific Slack API error codes only,
    # NOT generic words like "error" which could appear in message text)
    failure_signals = [
        "channel_not_found",
        "not_in_channel",
        "invalid_auth",
        "token_revoked",
        "missing_scope",
        "no_permission",
        "is_archived",
        "\"ok\": false",
        "\"ok\":false",
    ]

    response_lower = response.lower() if isinstance(response, str) else ""

    # Try to parse as JSON for structured error checking
    try:
        result = json.loads(response) if isinstance(response, str) else {}
        if isinstance(result, dict):
            if result.get("ok") is False or "error" in result:
                error_msg = result.get("error", "unknown error")
                context = {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": f"WARNING: Slack send FAILED with error: {error_msg}. The message was NOT delivered. Fix the issue before continuing."
                    }
                }
                print(json.dumps(context))
                sys.exit(0)
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback: check raw output for failure signals
    for signal in failure_signals:
        if signal in response_lower:
            context = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": f"WARNING: Slack send may have failed. Output contained '{signal}'. Verify the message was delivered before continuing."
                }
            }
            print(json.dumps(context))
            sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
