#!/usr/bin/env python3
"""PostToolUse hook: Lints copywriter output for writing violations.

After any file write to output/copywriter/, scans for:
- Em dashes (absolute zero tolerance)
- Staccato sentence fragments (sequences of short punchy sentences)
- Banned patterns ("it's not X, it's Y")

Blocks the write if violations found, forcing a fix before delivery.

Exit 0: Clean or not a copywriter output (proceed)
Exit 2: Violations found (block)
"""

import json
import re
import sys
import os


def check_em_dashes(text):
    """Find em dashes anywhere in text."""
    violations = []
    for i, line in enumerate(text.split("\n"), 1):
        if "\u2014" in line:  # em dash character
            violations.append(f"  Line {i}: em dash found: ...{line.strip()[:80]}...")
    return violations


def check_staccato(text):
    """Find sequences of short sentences (under 5 words) in a row."""
    violations = []
    lines = text.split("\n")
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        # Split into sentences
        sentences = re.split(r'[.!?]+', line)
        sentences = [s.strip() for s in sentences if s.strip()]
        short_streak = 0
        for s in sentences:
            word_count = len(s.split())
            if 0 < word_count < 5:
                short_streak += 1
            else:
                short_streak = 0
            if short_streak >= 2:
                violations.append(f"  Line {i+1}: staccato fragment sequence: ...{line[:80]}...")
                break
    return violations


def check_banned_patterns(text):
    """Find banned copywriting patterns."""
    violations = []
    patterns = [
        (r"[Ii]t'?s not .{1,30}, it'?s .{1,30}", "it's not X, it's Y"),
    ]
    for i, line in enumerate(text.split("\n"), 1):
        for pattern, name in patterns:
            if re.search(pattern, line):
                violations.append(f"  Line {i}: banned pattern '{name}': ...{line.strip()[:80]}...")
    return violations


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = event.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    file_path = event.get("tool_input", {}).get("file_path", "")

    # Only lint copywriter outputs and ad creative outputs
    lint_paths = ["output/copywriter/", "output/ad-creatives/"]
    if not any(p in file_path for p in lint_paths):
        sys.exit(0)

    # For Write, check the content directly from the tool input
    if tool_name == "Write":
        content = event.get("tool_input", {}).get("content", "")
    else:
        # For Edit, read the file after edit
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, IOError):
            sys.exit(0)

    if not content:
        sys.exit(0)

    # Run all checks
    all_violations = []
    all_violations.extend(check_em_dashes(content))
    all_violations.extend(check_staccato(content))
    all_violations.extend(check_banned_patterns(content))

    if not all_violations:
        sys.exit(0)

    print(f"BLOCKED: {len(all_violations)} writing violation(s) in {os.path.basename(file_path)}:", file=sys.stderr)
    for v in all_violations:
        print(v, file=sys.stderr)
    print("\nFix these violations before saving. Em dashes and staccato fragments are zero tolerance.", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
