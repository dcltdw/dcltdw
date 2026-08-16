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
  imports don't depend on *where* you cloned the repo;
- ensures your machine-global `~/.claude/CLAUDE.md` imports the universal rules:

      @~/.claude/dcltdw/AGENTS.md

  (migrating the old `@~/Github/dcltdw/claude/universal.md` import if it finds it).

The script also registers this clone as the `dcltdw` plugin marketplace and
installs the `dcltdw` skills plugin (`dcltdw:opening-a-pr`,
`dcltdw:cleaning-up-after-pr-merge`).

After a `git pull`, the symlinked rule files (`AGENTS.md`, `garmin-release.md`)
are already current — but the **skills plugin is a cached copy** and is not.
Re-run `./install.sh` after pulling (it runs `claude plugin marketplace update`);
or enable auto-update for the `dcltdw` marketplace in `/plugin` → Marketplaces.

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
