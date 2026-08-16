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
  `dcltdw` skills plugin. That plugin ships no skills yet — this is
  scaffolding; `dcltdw:opening-a-pr` and `dcltdw:cleaning-up-after-pr-merge`
  land in later PRs onto this same plugin.

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

> `universal.md` remains as a back-compat symlink to `AGENTS.md`, so any repo
> still importing the old path keeps working. New setups import `AGENTS.md`.

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
