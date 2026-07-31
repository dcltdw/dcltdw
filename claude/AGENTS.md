# Universal collaboration rules

Canonical cross-project rules for working with Claude on any of dcltdw's repos.
Imported machine-globally via `@~/.claude/dcltdw/AGENTS.md` (see [ADOPTING.md](ADOPTING.md)). Domain- and
project-specific rules live alongside the import in each repo's CLAUDE.md and
supplement (or override) these.

## Where a remembered rule belongs
When asked to remember something, decide its scope *before* saving it:
- A **cross-project** rule (applies to any of dcltdw's repos) belongs here in
  `AGENTS.md`. When a "remember this" request looks cross-project, say so and
  **ask whether it should go here** rather than into project-local memory.
- A **repo-specific** rule belongs in that repo's `CLAUDE.md`.
- Only **project state or personal context** belongs in private per-project memory.

Defaulting a universal rule into one project's memory is how the same lesson gets
re-learned from scratch in every other repo.

## Switching models at phase boundaries
Brainstorming and implementation reward different models, so the boundary between
them is a decision point rather than a seam to slide through. When work crosses
one, **stop before starting the new phase**: name the model you recommend and why,
hand over a prompt per [Handing off to another model](#handing-off-to-another-model),
and let the human choose. Don't start the new phase and mention the switch
afterwards — by then it has been done on the model you were going to replace.

Roles are the rule; the names below are only today's answer to it:

| phase | model *(mapping current as of 2026-07)* |
|---|---|
| Brainstorming, design, exploring requirements | **Fable** |
| Implementation, and the verification that follows it | **Opus** |

This fires on phase *entry*, not on every mode change inside one. Starting a
brainstorm for a new piece of work, or starting implementation of a design that
has been agreed, are boundaries. A design judgement made mid-implementation,
fixing review findings, and post-merge cleanup all belong to the phase already
running — no pause.

Say nothing and carry on when the session is already on the model you would
name. The rule exists to stop a phase running on the wrong model, not to
announce agreement with the current one.

**Hold that exemption to a high bar, because you are a poor judge of which
model is running.** A `/model` directive anywhere in this session's transcript
is authoritative; your system prompt's claim about which model you are is not,
and loses to it. If the two disagree — or you simply cannot tell — you are
**not** "already on the model you would name": pause and hand over. The
asymmetry is the argument. Announcing a switch that turns out to be unnecessary
costs one sentence; staying silent on the wrong model costs the rule its whole
purpose (this happened: a session set to Opus by `/model` read its system
prompt as Fable, took the exemption, and ran a brainstorm on Opus — the exact
outcome the rule exists to prevent).

## Handing off to another model
When the immediate next step you recommend is switching models — "switch to X and
do Y" as the action to take *now*, not a switch mentioned as a later step — hand
over a **ready-to-paste, self-contained prompt** for the new model. Write it to
stand on its own in a fresh session: include the context, goal, constraints, and
any file or ticket paths it needs, rather than assuming it inherits the current
conversation.

## Clarify before proceeding
Before acting on any request — *including* an explicit "please proceed with X" —
if you have a genuine clarifying question about X, or a substantive
countersuggestion or concern, raise it and **wait** for a response before
proceeding. Do not perform agreement, and do not suppress a concern to seem
agreeable.

The flip side: do not manufacture questions when something is genuinely clear.
Proceeding without asking signals you genuinely had none — not that you skipped
the check.

## Before deferring as "blocked"
Before deferring work as blocked — on an upstream dependency, a missing
capability, an unknown — do a cheap, time-boxed **spike** to confirm it is
actually blocked. A deferral resting on a stale assumption wastes the analysis
and just defers again; a few minutes checking the real state (current package
versions, the actual API, a quick probe) often flips "blocked" into "actually a
small change." Record the finding on the ticket either way.

## Branches and PRs
- Never commit directly to `main`. Always work on a branch.
- Open a PR and **wait for approval** before merging — don't merge your own work
  unprompted.
- Prefer **many small, single-purpose PRs** over one large one. Size each ticket
  to one reviewable PR.
- **Before opening a PR, `git checkout main && git pull` first** — so you branch
  off current `main` and confirm the work isn't already merged.
- **Highlight any PR whose base is not `main`** — every time you open one,
  present one for review, or report its merge state. Merging a stacked PR
  lands its commits on the base *branch*, and GitHub only retargets child
  PRs when the base branch is deleted at merge — so an unflagged non-`main`
  base can leave "merged" work stranded off `main` (this happened: two
  stacked PRs merged into leftover feature branches). After any stacked-PR
  merge, verify the content actually reached `main`, not just that GitHub
  says "Merged".
- **Never merge a stacked PR until its base has actually become `main`.** If the
  parent merged without its branch being deleted, retarget the child to `main`
  (and rebase) *before* merging it — otherwise the child merges into the stale
  base branch, not `main`, and strands even though GitHub says "Merged".

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
- **Ask the server which branches exist; `git branch -a` doesn't know.** It lists
  remote-*tracking* refs, so a branch already deleted on the server keeps
  appearing locally until something prunes — which reads as a leftover branch
  needing cleanup when there is nothing there (this happened: a closed PR's
  branch was reported as dangling, and flagged to the human as work to tidy,
  weeks after the server had dropped it). `git ls-remote --heads origin` answers
  authoritatively; `git fetch --prune` clears the stale refs. Check before
  reporting a branch as leftover, and before deleting one — a branch whose PR
  was **closed rather than merged** still holds unmerged commits.

## Commits
- Stamp each commit with the current AI model in a `Co-Authored-By:` trailer.
- **Confirm you're on the intended branch before committing** (`git branch
  --show-current` costs nothing). A stray commit on the wrong feature branch —
  another task's, or one you meant to base fresh off `main` — is easy to make
  and fiddly to unpick.

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
