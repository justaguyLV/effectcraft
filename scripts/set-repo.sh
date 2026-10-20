#!/usr/bin/env bash
# scripts/set-repo.sh owner/name: writes the repository address into the README, docs and notices.
set -euo pipefail
REPO="${1:?usage: set-repo.sh owner/name}"
cd "$(dirname "$0")/.."
grep -rl '@REPO@' --include='*.md' . | while read -r f; do sed -i "s|@REPO@|$REPO|g" "$f"; done
echo "repository set to $REPO"
