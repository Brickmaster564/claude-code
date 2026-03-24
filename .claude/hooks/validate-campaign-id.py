#!/usr/bin/env python3
"""PreToolUse hook: Validates campaign ID format before Instantly/Lemlist calls.

Catches short IDs, typos, and malformed UUIDs before they hit the API
and waste 20 minutes of upstream work.

Exit 0: Valid or not relevant (proceed)
Exit 2: Invalid campaign ID detected (block + feed error back to agent)
"""

import json
import re
import sys

UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)

LEMLIST_CAMPAIGN_PATTERN = re.compile(r'^cam_[A-Za-z0-9]{17,}$')


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = event.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    command = event.get("tool_input", {}).get("command", "")

    # Check Instantly commands
    if "instantly.py" in command:
        # Look for --campaign-id or --campaign_id argument
        match = re.search(r'--campaign[_-]id\s+["\']?([^\s"\']+)', command)
        if match:
            campaign_id = match.group(1)
            if not UUID_PATTERN.match(campaign_id):
                print(
                    f"BLOCKED: Instantly campaign ID '{campaign_id}' is not a valid UUID. "
                    f"Use the full UUID format (e.g. 14f5a1a1-cfca-422d-b8cd-d4c5d8577364), not a short ID.",
                    file=sys.stderr
                )
                sys.exit(2)

    # Check Lemlist commands
    if "lemlist.py" in command:
        match = re.search(r'--campaign[_-]id\s+["\']?([^\s"\']+)', command)
        if match:
            campaign_id = match.group(1)
            # Lemlist accepts cam_XXX or raw XXX (auto-prefixed by lemlist.py)
            if campaign_id.startswith("cam_"):
                # If prefixed, validate the full format
                if not LEMLIST_CAMPAIGN_PATTERN.match(campaign_id):
                    print(
                        f"BLOCKED: Lemlist campaign ID '{campaign_id}' looks malformed. "
                        f"Expected format: cam_ followed by 17+ alphanumeric characters.",
                        file=sys.stderr
                    )
                    sys.exit(2)
            else:
                # Raw ID (no cam_ prefix): must be alphanumeric, 17+ chars
                if not re.match(r'^[A-Za-z0-9]{17,}$', campaign_id):
                    print(
                        f"BLOCKED: Lemlist campaign ID '{campaign_id}' looks malformed. "
                        f"Expected: 17+ alphanumeric characters (with or without cam_ prefix).",
                        file=sys.stderr
                    )
                    sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
