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

# 3) Register the skills-plugin marketplace and install/update the plugin.
if command -v claude >/dev/null 2>&1; then
  # Detect registration by NAME *and* PATH via `--json`, not a text grep on
  # the plain listing. Matching name alone means a moved clone (or a second
  # clone on this machine) looks "already registered" and takes the `update`
  # branch below against its old/other path — which fails and, if unguarded,
  # would abort the whole install under `set -euo pipefail`. `marketplace
  # add` is safe to call even when a marketplace named "dcltdw" already
  # exists elsewhere: it either no-ops ("already on disk") or re-points that
  # registration at this clone — exactly the recovery this repo's docs
  # promise when you move the clone.
  mp_json="$(claude plugin marketplace list --json 2>/dev/null || true)"
  mp_ok=1
  if printf '%s' "$mp_json" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    data = []
repo = sys.argv[1]
sys.exit(0 if any(m.get("name") == "dcltdw" and m.get("path") == repo for m in data) else 1)
' "$REPO_DIR" 2>/dev/null; then
    claude plugin marketplace update dcltdw || mp_ok=0
  else
    claude plugin marketplace add "$REPO_DIR" || mp_ok=0
  fi

  if [ "$mp_ok" = 1 ]; then
    # `plugin install` is a no-op once installed and never picks up a version
    # bump on its own; `plugin update` is what actually refreshes the cached
    # copy, but it errors if the plugin isn't installed yet — so run both:
    # install covers first-time setup, update covers picking up new content.
    plugin_ok=1
    claude plugin install dcltdw@dcltdw || plugin_ok=0
    claude plugin update dcltdw@dcltdw || plugin_ok=0
    if [ "$plugin_ok" = 1 ]; then
      echo "skills plugin dcltdw installed/updated"
    else
      echo "WARNING: failed to install/update the dcltdw skills plugin — see output above." >&2
    fi
  else
    echo "WARNING: failed to register/update the dcltdw plugin marketplace — skills plugin NOT installed/updated." >&2
  fi
else
  echo "WARNING: 'claude' CLI not found — skills plugin NOT installed." >&2
  echo "         Install Claude Code, or ensure the 'claude' CLI is on your PATH" >&2
  echo "         (a VSCode-only install does not add it), then re-run ./install.sh" >&2
fi

echo
echo "Done. Start a new Claude session (or /clear) to pick up the rules."
echo "Garmin repos: add '@~/.claude/dcltdw/garmin-release.md' to that repo's CLAUDE.md (see claude/ADOPTING.md)."
