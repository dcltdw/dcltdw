# Adopting dcltdw's shared Claude rules

The canonical shared rules live in this directory: **[`AGENTS.md`](AGENTS.md)**
— cross-project collaboration rules, in the vendor-neutral
[AGENTS.md](https://agents.md/) format — and
[`garmin-release.md`](garmin-release.md) (the Garmin release process).

## Install (once per machine)

From a clone of this repo:

    ./install.sh

The script is idempotent and does three things:

- symlinks this `claude/` directory to the stable path `~/.claude/dcltdw`, so
  imports don't depend on *where* you cloned the repo — re-run `./install.sh`
  if you move the clone; both the symlink and the plugin marketplace
  registration re-point at the new location;
- ensures your machine-global `~/.claude/CLAUDE.md` imports the universal rules:

      @~/.claude/dcltdw/AGENTS.md

  (migrating the old `@~/Github/dcltdw/claude/universal.md` import if it finds it);
- registers this clone as the `dcltdw` plugin marketplace and installs the
  `dcltdw` skills plugin — home to this repo's PR-lifecycle skills:
  `dcltdw:opening-a-pr`, with `dcltdw:cleaning-up-after-pr-merge` rounding
  out the pair on the same plugin.

**Two delivery paths, and they behave differently — this is the single most
confusing thing about this setup.** `AGENTS.md` and `garmin-release.md` reach
a machine through the `~/.claude/dcltdw` symlink: a `git pull` alone is
enough, nothing to re-run. `claude/skills/**` instead reaches a machine only
through the plugin's **cached copy**, keyed by the `version` field in
`claude/.claude-plugin/plugin.json`. Re-run `./install.sh` after pulling — it
calls `claude plugin update dcltdw@dcltdw`, which refreshes that cache, but
**only if `version` changed** in the pull you just took. Without a bump it
reports "already at the latest version" and the stale copy survives.
(`claude plugin marketplace update`, which install.sh also runs, refreshes
marketplace metadata only — never the plugin's cached content by itself.)

**Standing rule for every future change to `claude/skills/**`:** bump
`version` in `claude/.claude-plugin/plugin.json` in the same change, or
installed machines never see it. Edits to `AGENTS.md`, `garmin-release.md`,
or this file do **not** need a bump — they ship live through the symlink, not
the cache.

## Delivery paths

This directory ships through two complementary channels — neither replaces
the other:

- **The `~/.claude/dcltdw` symlink** (created by `install.sh`) carries
  everything that must be *live on pull*: the always-loaded `AGENTS.md`
  import, per-repo opt-in imports (`garmin-release.md`), and — once the
  pre-push hook lands — `githooks/`, which `core.hooksPath` points into.
- **The `dcltdw` plugin cache** delivers `skills/` — and only `skills/` —
  gated by `version` bumps in `.claude-plugin/plugin.json`. (The cached
  copy is actually a full snapshot of `claude/`, so files like
  `AGENTS.md` ride along in it too; those ride-alongs are inert, since
  the live `@`-import resolves through the symlink, not the cache.)

Plugin-only delivery is not currently possible (verified against Claude
Code 2.1.233, 2026-08): plugins cannot contribute always-loaded
instruction text, cannot serve per-repo conditional content or
version-stable import paths, and their cache path is version-stamped and
therefore unusable as a `core.hooksPath` target. **Revisit retiring the
symlink when Claude Code ships all three:** (1) always-loaded plugin
instruction text; (2) per-repo conditional plugin content or a
version-stable import path into an installed plugin; (3) a version-stable
path suitable for `core.hooksPath` (or plugin-managed git hooks). Any one
of them landing is worth a fresh look; all three are needed to retire the
symlink outright.

## Per-repo wiring

**Board IDs are project-specific.** The universal rules say to track work on a
project board (Todo → In Progress → Done → Won't Do) but can't hold IDs. If a
repo uses a board, record its IDs in that repo's own `CLAUDE.md` — board URL/id,
the Status field id, the option ids, and the `gh api graphql` query to re-derive
them if they drift.

**Garmin repos.** Add to the repo's own `CLAUDE.md`:

    @~/.claude/dcltdw/garmin-release.md

Then add a short project supplement below the import with this repo's specifics
(signing-key path + how it's verified, target device list / primary test device,
where the store copy lives, release quirks). See the "Project supplement"
section of `garmin-release.md`.

If the repo previously pointed at another "master" conventions doc, remove that
pointer — these `@import`s are the single source of truth now.

## Delivering a repo's CLAUDE.md change

Per the universal rules: branch and open a PR for approval. (`~/.claude/CLAUDE.md`
is user config, not a repo — `install.sh` edits it directly.)

## How resolution works

`@import`s resolve against the local filesystem, so a new import takes effect
once the referenced file exists at the resolved path — which, after
`install.sh`, is the stable `~/.claude/dcltdw/` symlink.
