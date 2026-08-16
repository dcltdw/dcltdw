---
name: opening-a-pr
description: Use when opening a pull request, writing or revising a PR body, or presenting or reporting a PR's status or merge state — including any PR whose base branch is not main.
---

# Opening a PR

## Overview
The PR's reader — human or agent — must understand and safely merge it
without your session transcript: a body that says what changed and who
produced it, and an accurate account of any non-`main` base.

## Before opening
1. `git checkout main && git pull` (or fetch + rebase onto `origin/main`) —
   branch off *current* `main`; confirm the work isn't already merged.
2. Move the board card **Todo → In Progress** (if the repo has a board).

## PR body — five required sections, every time
Use these headings, in this order, even for a "quick" or "small" PR — under
time pressure this is what gets dropped first:
- **Files changed** — every file, annotated `(new)` / `(deleted)` / `(modified)`.
- **Work breakdown** — what changed and why, not just what.
- **Test expectations** — only when failures are expected; omit otherwise.
- **Operational impact** — deploy / reinstall / migration notes; omit if none.
- **Provenance** — `Agent:` (tool/harness) and `Model / version:`.

Provenance especially: nothing in the request ever asks for it, so it's the
section a fast draft skips by inventing other headings instead.

## Stacked PRs (base ≠ main)
Flag a non-`main` base every time you open, present, or report on the PR —
the flag only protects the reader if the reason behind it is checked, not
assumed.

Check, don't assume: `gh repo view --json deleteBranchOnMerge` tells you
whether this repo auto-deletes branches on merge. If so, GitHub retargets
a child PR's base automatically once the parent merges — sounds solved,
usually isn't: retargeting changes only which branch the PR diffs
against, never the child's commit history.

So check ancestry instead of guessing whether that gap matters:
`git merge-base --is-ancestor <parent-tip> main`. True (a true merge, or
an already-rebased child) — nothing to do. False (typical after a squash
merge — a brand-new commit, never an ancestor of the original branch) —
the child's diff still duplicates the parent's lines and will conflict.

If false: rebase the child onto current `main` (`git rebase --onto main
<parent-tip> <child-branch>`), then re-diff against `main` to confirm only
the child's own changes remain. Parent branch already deleted?
`<parent-tip>` is still an ancestor of the child — find it in the PR's
original commit list or `git log <child-branch>`. The merge-time gate
itself lives in `dcltdw:cleaning-up-after-pr-merge`; this skill flags the
risk at open- and report-time.

## Rationalizations
| Excuse | Reality |
|---|---|
| "Auto-delete/retargeting means it's safe to merge" | Retargeting moves the diff base, not the history. Check ancestry first — a squash-merged parent fails it, so its lines still show as new. |
| "Flag the non-`main` base so it doesn't look confusing on merge" | Wrong risk. If ancestry fails, the real risk is stranded/duplicated/conflicting work — say that, so the flag actually warns. |
