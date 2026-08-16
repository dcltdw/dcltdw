---
name: cleaning-up-after-pr-merge
description: Use when about to merge a pull request, right after any PR merges, or when deciding whether a local or remote branch is leftover, stale, or safe to delete.
---

# Cleaning Up After a PR Merges

## Overview
A remote-tracking ref is not proof a branch still exists, and "GitHub shows
Merged" is not proof the content reached `main`. Verify both before
reporting on or deleting anything.

## Before merging: the stacked gate
If the PR's base is not `main`, retarget it to `main` before merging —
unconditionally, regardless of the check below. Retargeting only moves
the diff base, not the history, so also check ancestry:
`git merge-base --is-ancestor <parent-tip> main`. Parent branch already
deleted (the default under `deleteBranchOnMerge`)? `<parent-tip>` is
still an ancestor of the child — find it in the PR's original commit
list or `git log <child-branch>`. True (a true merge commit, or an
already-rebased child) — retarget and merge, done. False (squash and
rebase merges both rewrite history — the normal case; a true merge
commit passes) — rebase onto `main` first (`git rebase --onto main
<parent-tip> <child-branch>`), re-diff to confirm only the child's own
changes remain, *then* retarget and merge. `dcltdw:opening-a-pr` covers
this same check (and `deleteBranchOnMerge`) at open/report time; this is
its merge-time enforcement.

## After any merge
Work through all five steps below and report status on each — a blocked
step (missing tool approval, no server access) still needs a stated
answer, not silent omission.
1. `git checkout main && git pull`.
2. **Grep `main` for the actual change** — don't trust the merge summary.
   A squash merge captures the branch as of merge time; a commit pushed
   afterward, or content lost resolving conflicts, won't be there, and a
   stacked child can land off-`main` entirely. Diff the branch against
   `main` to confirm.
3. Move the board card to **Done** — or **Won't Do**, with a one-line reason.
4. Ask what the merge **made stale**: docs describing the old behaviour,
   other open PRs needing a rebase, tickets it silently resolved, live
   config that now differs from `main`.
5. Delete the merged branch — local and remote — per the rules below.

## Branch deletion: ask the server, not the tracking ref
- `git ls-remote --heads origin` (or `git fetch --prune`) is the only
  authority on whether a branch still exists on the remote. Run it before
  reporting *or* deleting anything.
- `git branch -a` lists remote-*tracking* refs, and those go stale: a
  branch someone else deleted on the server keeps appearing until
  something prunes. A stale ref looks identical to a live one — report or
  delete off `git branch -a` alone and you'll hand someone a
  `git push --delete` for a branch the server already dropped.
- `git branch --merged` misses squash-merged branches — their tip commit
  is never an ancestor of `main`, even though their earlier history is.
  Check the PR's actual merge state, not this flag alone.
- A branch whose PR was **closed, not merged**, may still hold commits
  found nowhere else. Confirm the content is landed (or knowingly
  abandoned) before deleting — "closed" is not "safe."

## Rationalizations
| Excuse | Reality |
|---|---|
| "`git branch -a` shows it, so it needs cleanup" | Tracking refs outlive the branch they track. Run `git ls-remote --heads origin` before you report or delete — that's the only thing that has actually checked the server. |
