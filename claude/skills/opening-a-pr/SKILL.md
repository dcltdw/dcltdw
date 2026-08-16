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
the flag only protects the reader if the reason behind it is correct.

Branch auto-delete is on for this repo, so GitHub *does* now retarget a
child PR's base automatically once the parent is squash-merged and its
branch deleted. That sounds like the problem is solved — it isn't.
Retargeting changes only which branch the PR diffs against; it does not
rebase the child's commits. A squash merge creates a brand-new commit on
`main`, so the parent's original commits are never its ancestors. After
auto-retarget, the child's diff still shows the parent's already-merged
lines as new additions, and merging it as-is will conflict or duplicate
that work.

Before merging a retargeted child: rebase it onto current `main`
(`git rebase --onto main <old-parent-tip> <child-branch>`), then re-diff
against `main` to confirm only the child's own changes remain. The
merge-time gate itself lives in `dcltdw:cleaning-up-after-pr-merge`; this
skill flags the risk at open- and report-time.

## Rationalizations
| Excuse | Reality |
|---|---|
| "GitHub retargeted it automatically, so it's safe to merge" | Retargeting moves the diff base, not the commit history — the parent's squash commit is never an ancestor of the child's. The diff still duplicates the parent's lines. Rebase onto `main` first. |
| "Flag the non-`main` base so it doesn't look confusing on merge" | Wrong risk. The real one is stranded/duplicated/conflicting work, not a confusing diff — say that, so the flag actually warns. |
| "Body sections are overkill for a small or fast diff" | Files-changed annotations and Provenance cost five lines; reconstructing them afterward costs hours. |
| "Nothing asked who/what produced this, so skip Provenance" | Required unconditionally, not on request — it's the section a fast draft omits by inventing other headings instead. |
