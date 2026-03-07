#!/bin/bash
# Auto-backup: commits and pushes any changes to GitHub daily

REPO_DIR="/Users/jasper/Library/Application Support/Claude/Jasper OS - CC Hub"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export GIT_SSH_COMMAND="ssh -i /Users/jasper/.ssh/id_ed25519 -o IdentitiesOnly=yes"

cd "$REPO_DIR" || exit 1

# Only commit and push if there are changes
if [ -n "$(git status --porcelain)" ]; then
    git -c user.name="Jasper" -c user.email="hello@clientnetwork.io" add -A
    git -c user.name="Jasper" -c user.email="hello@clientnetwork.io" commit -m "Auto-backup: $(date '+%Y-%m-%d %H:%M')"
    git push origin main
fi
