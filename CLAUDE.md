# CLAUDE.md — dcltdw/dcltdw repo instructions

This repo ships `claude/` two ways at once: as the `dcltdw` plugin
(marketplace `.claude-plugin/marketplace.json`, plugin
`claude/.claude-plugin/plugin.json`) and as the target of the
`~/.claude/dcltdw` symlink that `install.sh` creates. Those two delivery
paths behave differently:

- `claude/AGENTS.md` and `claude/garmin-release.md` reach an installed
  machine live, through the symlink — a `git pull` alone is enough.
- `claude/skills/**` reaches a machine only through the plugin's **cached
  copy**, keyed by `version` in `claude/.claude-plugin/plugin.json`.
  `claude plugin update dcltdw@dcltdw` (what `./install.sh` runs) is a no-op
  without a version change.

**Rule: any change to `claude/skills/**` must bump `version` in
`claude/.claude-plugin/plugin.json` in the same commit/PR, or installed
machines keep the stale copy.** `claude/githooks/**` is symlink-delivered
too — `core.hooksPath` points at `$LINK/githooks` — so it does *not* need a
version bump.

Full adopter-facing version of this: `claude/ADOPTING.md`.
Current implementation plan: `docs/superpowers/plans/2026-08-15-pr-skills-plugin.md`.
