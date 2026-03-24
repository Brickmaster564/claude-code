#!/usr/bin/env python3
"""PreToolUse hook: Validates required API keys exist before tool scripts run.

Checks the Bash command for tools/*.py invocations and verifies the
required API keys are present in config/api-keys.json. Blocks execution
if a required key is missing or empty.

Exit 0: Key exists or command isn't a tool script (proceed)
Exit 2: Required key missing (block + feed error back to agent)
"""

import json
import os
import sys

# Map tool scripts to their required API key paths in config/api-keys.json
TOOL_KEY_MAP = {
    "instantly.py": ["instantly"],
    "millionverifier.py": ["millionverifier"],
    "bounceban.py": ["bounceban"],
    "lemlist.py": ["lemlist"],
    "apify.py": ["apify"],
    "slack.py": ["slack_nalu", "slack_cn"],  # needs at least one
    "gmail.py": [],  # uses OAuth tokens, not API keys
    "meta_ads.py": ["meta_access_token"],
    "meta_report.py": ["meta_access_token"],
    "higgsfield.py": ["kie"],
}

# Tools where ANY one key is sufficient (vs ALL required)
ANY_KEY_SUFFICIENT = {"slack.py"}


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = event.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    command = event.get("tool_input", {}).get("command", "")

    # Find which tool script is being called
    matched_tool = None
    for tool_script in TOOL_KEY_MAP:
        if tool_script in command:
            matched_tool = tool_script
            break

    if not matched_tool:
        sys.exit(0)

    required_keys = TOOL_KEY_MAP[matched_tool]
    if not required_keys:
        sys.exit(0)

    # Load API keys config
    project_dir = event.get("cwd", "")
    config_path = os.path.join(project_dir, "config", "api-keys.json")

    if not os.path.isfile(config_path):
        print(f"BLOCKED: config/api-keys.json not found. Cannot run {matched_tool}.", file=sys.stderr)
        sys.exit(2)

    try:
        with open(config_path, "r") as f:
            keys = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"BLOCKED: config/api-keys.json is invalid: {e}", file=sys.stderr)
        sys.exit(2)

    # Check keys
    if matched_tool in ANY_KEY_SUFFICIENT:
        found_any = any(keys.get(k) for k in required_keys)
        if not found_any:
            print(f"BLOCKED: {matched_tool} needs at least one of: {', '.join(required_keys)}. None found in config/api-keys.json.", file=sys.stderr)
            sys.exit(2)
    else:
        missing = [k for k in required_keys if not keys.get(k)]
        if missing:
            print(f"BLOCKED: {matched_tool} requires these keys in config/api-keys.json: {', '.join(missing)}", file=sys.stderr)
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
