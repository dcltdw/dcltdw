# Adopting the shared Claude docs in a repo

Instructions for a Claude agent working in one of dcltdw's repos, to wire that
repo to the canonical shared docs here in `dcltdw/claude/`. Follow these steps.

## Prerequisite
`dcltdw` must be cloned at `~/Github/dcltdw` on the machine — the `@import`
paths below are absolute to that location.

## 1. Universal rules (every repo, once per machine)
Ensure `~/.claude/CLAUDE.md` (the global user memory, applied to all projects)
contains:

    @~/Github/dcltdw/claude/universal.md

This is machine-global, so it's done once — not per repo.

## 2. Garmin release process (Garmin repos only)
In the repo's own `CLAUDE.md`, add:

    @~/Github/dcltdw/claude/garmin-release.md

Then add a short **project supplement** below the import with this repo's
specifics — signing-key path (+ how it's verified), target device list / primary
test device, where the store copy lives, and any release quirks. See the
"Project supplement" section of `garmin-release.md` for the fields.

If the repo previously pointed at another "master" conventions doc (e.g. an
abandoned project's), **remove that pointer** — these `@import`s are the single
source of truth now.

## 3. Deliver the change
Per `universal.md`: make the CLAUDE.md edit on a branch and open a PR for
approval. (`~/.claude/CLAUDE.md` is user config, not a repo — edit it directly.)

## Note on resolution
`@import`s resolve against the local filesystem, so they only take effect once
the referenced files exist on `dcltdw`'s `main` and it has been pulled locally.
