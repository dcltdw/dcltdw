# Universal collaboration rules

Canonical cross-project rules for working with Claude on any of dcltdw's repos.
Imported into a repo via `@~/Github/dcltdw/claude/universal.md`. Domain- and
project-specific rules live alongside the import in each repo's CLAUDE.md and
supplement (or override) these.

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

## PR bodies
Include these sections:
- **Files changed** — annotate each entry `(new)` / `(deleted)` / (modified).
- **Work breakdown** — what changed and why.
- **Test expectations** — only when failures are expected.
- **Operational impact** — deploy / reinstall / migration notes (omit if none).

## Project board
- Track work on the project board; move status **Todo → In Progress** (PR opens)
  **→ Done** (PR merges).

## Commits
- Stamp each commit with the current AI model in a `Co-Authored-By:` trailer.

## Before pushing
- **Scan the diff for secrets** (keys, tokens, credentials) before every push.

## Before claiming done
- **Verify, don't assert.** Run the actual build/test/command and confirm the
  output before saying something works. Report what was verified vs. assumed; if
  a step was skipped or failed, say so.
