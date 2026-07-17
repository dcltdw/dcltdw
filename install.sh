#!/usr/bin/env bash
# Install dcltdw's shared Claude rules so they load in every project on this
# machine — regardless of where this repo is cloned.
#
# Idempotent: safe to re-run (e.g. after `git pull`). Run once per machine:
#     ./install.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RULES_DIR="$REPO_DIR/claude"

CLAUDE_HOME="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
LINK="$CLAUDE_HOME/dcltdw"                     # stable path, independent of clone location
GLOBAL_MD="$CLAUDE_HOME/CLAUDE.md"
IMPORT='@~/.claude/dcltdw/AGENTS.md'           # canonical import
LEGACY='@~/Github/dcltdw/claude/universal.md'  # old hardcoded-path import to migrate

mkdir -p "$CLAUDE_HOME"

# 1) Point a stable path at the rules dir, so imports never hardcode the clone location.
ln -sfn "$RULES_DIR" "$LINK"
echo "linked $LINK -> $RULES_DIR"

# 2) Ensure the machine-global user memory imports the rules.
touch "$GLOBAL_MD"
if grep -qF "$IMPORT" "$GLOBAL_MD"; then
  echo "global import already present ($GLOBAL_MD)"
elif grep -qF "$LEGACY" "$GLOBAL_MD"; then
  cp "$GLOBAL_MD" "$GLOBAL_MD.bak"
  awk -v old="$LEGACY" -v new="$IMPORT" '{print ($0==old ? new : $0)}' "$GLOBAL_MD" > "$GLOBAL_MD.tmp"
  mv "$GLOBAL_MD.tmp" "$GLOBAL_MD"
  echo "migrated legacy import -> $IMPORT (backup: $GLOBAL_MD.bak)"
else
  printf '\n# Shared collaboration rules (dcltdw)\n%s\n' "$IMPORT" >> "$GLOBAL_MD"
  echo "added import to $GLOBAL_MD"
fi

echo
echo "Done. Start a new Claude session (or /clear) to pick up the rules."
echo "Garmin repos: add '@~/.claude/dcltdw/garmin-release.md' to that repo's CLAUDE.md (see claude/ADOPTING.md)."
