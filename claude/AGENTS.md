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

## Model handoffs at phase boundaries
Brainstorming and implementation reward different models, so the boundary
between them is a decision point rather than a seam to slide through.

Roles are the rule; the names below are only today's answer to it:

| phase | model *(mapping current as of 2026-07)* |
|---|---|
| Brainstorming, design, exploring requirements, **writing the plan** | **Fable** |
| **Executing a plan**, implementation, and the verification that follows | **Opus** |

Three events end a turn. When one fires: name the model the next phase wants,
hand over a prompt per [Handing off to another model](#handing-off-to-another-model),
and **stop**. That prompt is the turn's entire deliverable — nothing after it,
no "shall I start?", no offer to carry on.

1. **A plan file exists and execution has not begun.** The moment
   `docs/superpowers/plans/<name>.md` is written, that turn is over.
2. **You are about to propose brainstorming or design on new work.**
3. **Implementation has stopped because the design is wrong.** Not a design
   judgement made in passing — an actual halt.

Nothing else fires this. Fixing review findings, verification, and post-merge
cleanup all belong to the phase already running.

**Anchor these to artifacts, never to how the work feels.** "A plan file was
written" is checkable. "Planning seems finished" is arguable, and anything
arguable gets argued away — which is exactly how the previous version of this
rule failed: a session decided that writing the plan *was* implementation, so
the two were one phase, so no boundary could ever arrive.

**No exemption.** Do this even when you believe the session is already on the
model you would name. You cannot observe which model is running, so that belief
is never load-bearing. Naming the model a phase *wants* is a role question the
table above answers; deciding you are already on it is not, so don't. A
needless handoff costs one sentence — the asymmetry is the whole argument.

**This outranks a skill's closing script.** `superpowers:writing-plans` ends by
offering "Inline Execution — execute tasks in this session"; that offer is a
boundary crossing and this rule refuses it. Put the execution style
(subagent-driven vs inline) *inside* the handoff prompt, for the next session
to act on.

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

## Concurrent agents
Assume other agents — other sessions, subagents, scheduled jobs — may be
working in this repo and on this machine *right now*. Two hazards, two
different remedies; don't let one rule blur them:

- **The working tree is shared state.** Branch switches, staging, and
  stashes collide silently when two agents share a clone. Do feature work
  in an isolated workspace (`superpowers:using-git-worktrees`) **unless**
  the task must mutate machine-global state anchored to the primary
  clone's path — a checkable exception: name that state before claiming
  it. The Commits rule ("confirm you're on the intended branch") is the
  floor here, not the ceiling.
- **A worktree does not isolate the machine.** Global git config,
  `~/.claude/*`, plugin caches, and install scripts are shared no matter
  where your checkout lives. Before mutating any of it: verify its
  current state first, and restore what you disturb. Never run a script
  that repoints global paths from a throwaway checkout (this repo's
  `install.sh` aims `~/.claude/dcltdw` at its own directory — run from a
  worktree, the pointer would outlive the checkout and strand the
  machine's rule imports).

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
- **Verify where the artifact will live, not where you happen to be working.**
  A command that passes in your working tree can prove the wrong thing —
  uncommitted edits, local config, and warm caches all mask failures the next
  person hits. For anything that ships (a branch, a release, a generated file),
  re-run the check in a clean checkout; a throwaway `git worktree` is enough.
- **You cannot observe which model you are running as.** Your system prompt's
  claim about it is not authoritative and a `/model` directive in the transcript
  outranks it, but neither settles the question — so never state the running
  model as fact. Say which one the transcript asked for, and leave it there.
