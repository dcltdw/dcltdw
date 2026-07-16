# Universal collaboration rules

Canonical cross-project rules for working with Claude on any of dcltdw's repos.
Imported into a repo via `@~/Github/dcltdw/claude/universal.md`. Domain- and
project-specific rules live alongside the import in each repo's CLAUDE.md and
supplement (or override) these.

## Where a remembered rule belongs
When asked to remember something, decide its scope *before* saving it:
- A **cross-project** rule (applies to any of dcltdw's repos) belongs here in
  `universal.md`. When a "remember this" request looks cross-project, say so and
  **ask whether it should go here** rather than into project-local memory.
- A **repo-specific** rule belongs in that repo's `CLAUDE.md`.
- Only **project state or personal context** belongs in private per-project memory.

Defaulting a universal rule into one project's memory is how the same lesson gets
re-learned from scratch in every other repo.

## Clarify before proceeding
Before acting on any request — *including* an explicit "please proceed with X" —
if you have a genuine clarifying question about X, or a substantive
countersuggestion or concern, raise it and **wait** for a response before
proceeding. Do not perform agreement, and do not suppress a concern to seem
agreeable.

The flip side: do not manufacture questions when something is genuinely clear.
Proceeding without asking signals you genuinely had none — not that you skipped
the check.

## Branches and PRs
- Never commit directly to `main`. Always work on a branch.
- Open a PR and **wait for approval** before merging — don't merge your own work
  unprompted.
- Prefer **many small, single-purpose PRs** over one large one. Size each ticket
  to one reviewable PR.
- **Before opening a PR, `git checkout main && git pull` first** — so you branch
  off current `main` and confirm the work isn't already merged.

## PR bodies
Include these sections:
- **Files changed** — annotate each entry `(new)` / `(deleted)` / (modified).
- **Work breakdown** — what changed and why.
- **Test expectations** — only when failures are expected.
- **Operational impact** — deploy / reinstall / migration notes (omit if none).
- **Provenance** — `Agent:` (tool / harness) and `Model / version:` that
  produced the PR.

## Project board
- Track work on the project board; move status **Todo → In Progress** (PR opens)
  **→ Done** (PR merges).
- Two terminal states: **Done** (work happened) and **Won't Do** (reviewed and
  deliberately closed without action — always record a one-line reason). Add a
  "Won't Do" status if the board lacks one.
- Say **refinement** or **triage** for backlog work — never "grooming" (outdated).

## After a PR merges
- `git checkout main && git pull`.
- **Confirm `main` actually contains the change** — grep for it. "The PR shows
  merged" is a weaker claim: a squash-merge can land from a state *before* a
  later fix commit, leaving `main` silently missing it.
- Move the board card to **Done** (or **Won't Do** + reason).
- Ask what the merge **made stale** — docs describing the old behaviour, tickets
  it silently resolved, open PRs needing a rebase, live config that now differs
  from `main`.
- Delete the merged branch, local and remote. Note that `git branch --merged`
  does **not** list a squash-merged branch (it shares no commits with `main`), so
  rely on the PR's merge state, not that command.

## Commits
- Stamp each commit with the current AI model in a `Co-Authored-By:` trailer.

## Before pushing
- **Scan the diff for secrets** (keys, tokens, credentials) before every push.

## Before claiming done
- **Verify, don't assert.** Run the actual build/test/command and confirm the
  output before saying something works. Report what was verified vs. assumed; if
  a step was skipped or failed, say so.
- **Re-derive facts from the source, not from earlier prose.** A number carried
  over from a prior summary is not verified — re-check it against the tool
  (`gh run list`, the file, the API). And a check you have not watched *fail* is
  not yet evidence that it can.
