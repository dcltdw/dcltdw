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

## Project board

Work in this repo (and, post-migration, dcltdw/agents) is tracked on the
user-level Project v2 board **"Agent tooling"** (project number 8,
id `PVT_kwHOAAdfes4BgolJ`). Status field id `PVTSSF_lAHOAAdfes4BgolJzhfnY94`;
option ids: Todo `eae12008`, In Progress `44811c68`, Done `702fcf43`,
Won't Do `f196c60a`.
Re-derive if they drift:
`gh project field-list 8 --owner dcltdw --format json`
