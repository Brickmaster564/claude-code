#!/bin/bash
# Auto-backup: commits and pushes any changes to GitHub daily

REPO_DIR="/Users/jasper/Library/Application Support/Claude/Jasper OS - CC Hub"
export PATH="/opt/homebrew/bin:$PATH"

cd "$REPO_DIR" || exit 1

# Only commit and push if there are changes
if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -m "Auto-backup: $(date '+%Y-%m-%d %H:%M')"
    git push origin main
fi
