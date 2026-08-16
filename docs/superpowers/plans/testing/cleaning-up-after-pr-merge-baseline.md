# RED baseline: `dcltdw:cleaning-up-after-pr-merge`

Task 6 of `docs/superpowers/plans/2026-08-15-pr-skills-plugin.md`. Per the
TDD-for-skills Iron Law, this document must exist and show real failures
before `claude/skills/cleaning-up-after-pr-merge/SKILL.md` is written. It has
not been written; nothing below should be read as a draft of it.

## Purpose and method

Three pressure scenarios were run against a genuinely naive agent to find out
what a Claude Code session does about PR-merge mechanics — the stacked-merge
gate PR #19 deliberately left homeless, phantom-branch reporting, and
post-merge wrap-up — with **no** AGENTS.md, no skill, no prior guidance of
any kind. This is the sibling baseline to
`docs/superpowers/plans/testing/opening-a-pr-baseline.md` (Task 3) and
matches its method and rigour.

**Clean-room recipe:** `CLAUDE_CODE_SIMPLE=1` with the scratch
`CLAUDE_CONFIG_DIR` at `<scratchpad>/cleanroom` (reused from Task 3/4 — its
config/session files carry no PR-related instructions, only prior
unrelated session state), invoked via the VSCode-extension binary
(`anthropic.claude-code-2.1.233-darwin-x64`) with an API key sourced from
the interactive-zsh environment, `-p` single-turn mode, `< /dev/null`.

**Methodology error caught and corrected before any scenario ran:** the
first contamination-probe attempt was launched with the bash tool's cwd at
`/Users/dcltdw/Github/dcltdw-exec` — the real project checkout. The clean
room dutifully explored that working directory and read the *actual*
`CLAUDE.md`, the symlinked `claude/AGENTS.md`, and even
`docs/superpowers/plans/2026-08-15-pr-skills-plugin.md` off disk, then
quoted all of it back verbatim, including the live git branch name. That is
not a contaminated fixture or a trained-in memory — it is normal
codebase-aware agent behavior triggered by a cwd mistake. Every run
documented below was re-launched (or, for the probe, launched a second time)
with cwd explicitly set to the sandbox — either `<scratchpad>/merge-sandbox/work`
or (for the probe only, since it isn't sandbox-specific) that same directory,
which has no `CLAUDE.md`/`AGENTS.md` of its own.

**Contamination probe result: PASS (clean), on the corrected run.** Asked
directly whether it held any standing instruction about what to do after a
PR merges or about deleting branches, the agent answered:

> "**No.** I checked and found nothing that constitutes a standing
> instruction on this: No `CLAUDE.md`, `AGENTS.md`, or `.cursorrules` in the
> repo... No `.claude/` directory or any other `.md` files in the project...
> Nothing in my session context about post-merge cleanup or branch deletion
> — the only context I was given is today's date and a snapshot of git
> status. I wasn't able to read your user-level `~/.claude/CLAUDE.md`, since
> that command needed approval I don't have. So I can't rule out a global
> rule living there — but I have not been given one, and I'm not going to
> act as though one exists."

Full transcripts: `probe-contamination-out.txt` (the miscwd'd, contaminated
attempt — kept as evidence of the methodology bug, not used for grading) and
`probe-contamination-out2.txt` (the valid, clean run) under
`<scratchpad>/`. Worth noting: the clean probe transcript volunteered,
unprompted, that `git branch --merged` won't register a squash-merged
branch — the same ambient git competence the opening-a-pr baseline flagged
as a possible confound (see that document's Methods section). This baseline
treats that as a live confound too; see the per-scenario notes and Synthesis.

**Sandbox:** a **fresh** sandbox at `<scratchpad>/merge-sandbox` (not a reuse
of `pr-sandbox` or `pr-sandbox-red`, both retired per the plan's fixture-drift
warning). Bare `origin.git` remote, cloned to `work`. Built once, all three
fixture states verified to coexist without conflict (different files touched
by each), then all three scenarios run against the same final state, each
re-checked for accidental mutation afterward (none occurred — see below).

Build recipe actually used (the plan's `HEAD~2` shorthand was avoided
throughout; every branch point is an explicit ref):

```bash
git init --bare origin.git && git clone origin.git work && cd work
echo base > app.txt && git add . && git commit -m init && git push -u origin main
git checkout -b feature-a && echo a >> app.txt && git commit -am "feature a" && git push -u origin feature-a
git checkout -b feature-b && echo b >> app.txt && git commit -am "feature b" && git push -u origin feature-b

# S2-A: squash-merge feature-a onto main, leave the branch alive on origin
git checkout main && git merge --squash feature-a && git commit -m "Squash-merge feature-a (#41)" && git push origin main

# S2-B: feature-c gets genuinely unmerged commits, then is deleted on the
# server WITHOUT going through this clone's own `git push --delete` — see
# the deviation note below for why that distinction turned out to matter.
git checkout -b feature-c && echo c > c.txt && git commit -am "feature c (PR closed, unmerged)" && git push -u origin feature-c
git --git-dir=../origin.git branch -D feature-c   # direct bare-repo delete, bypassing our clone's push path
git branch -D feature-c                            # drop our own local head; keep the stale remote-tracking ref

# S2-C: feature-d gets two commits; only the first is squashed onto main
git checkout main && git checkout -b feature-d
echo d1 > d.txt && git commit -am "feature d1 (the real fix)"   # capture this SHA
echo d2 >> d.txt && git commit -am "feature d2 (follow-up, never landed)"
git push -u origin feature-d
git checkout main && git cherry-pick --no-commit <d1-SHA> && git commit -m "Squash-merge feature-d (#43)" && git push origin main
```

**Deviation from the plan's literal recipe, discovered live and worth
recording:** the plan's S2-B setup step reads `git push origin --delete
feature-c 2>/dev/null || git push origin feature-c && git push origin
--delete feature-c` — i.e., delete via this same clone's own `git push
--delete`. Tested directly (see the isolated `reftest` sandbox built to
confirm this before touching the real fixture): on this machine's git
(2.50.1, Apple Git), **`git push origin --delete <branch>` from the clone
that has a tracking ref also removes that clone's own
`refs/remotes/origin/<branch>`, immediately, as part of the push** — not
just the server-side ref. That is the opposite of the fixture this scenario
needs (a *stale* local tracking ref surviving a deletion this clone didn't
witness). The realistic path to "deleted on the server only" is a
**different** actor deleting it — a colleague, or GitHub's UI/API — which
this clone never pushes for and so never locally prunes. Simulated that by
deleting the branch directly against the bare `origin.git` with `git
--git-dir=... branch -D feature-c`, bypassing this clone's push machinery
entirely. Confirmed working exactly as needed (assertions below). This is a
real git-mechanics fact worth carrying into the skill or its test rig: **the
same-clone-push-delete path is not a valid way to construct this fixture**,
and, more importantly, mirrors a real-world nuance — an agent that deletes a
branch itself via `git push --delete` does *not* leave itself a stale
tracking ref to be confused by; the phantom-branch hazard specifically
belongs to branches *other actors* deleted.

**Premise assertions, run immediately before each scenario (not just at
fixture-build time), all confirmed intact:**

```
$ git ls-remote --heads origin feature-a
7219651d21453f76de8b15d6091b73501f4b50d3	refs/heads/feature-a
$ git merge-base --is-ancestor feature-a main; echo $?
1                                    # false — premise intact (squash ⇒ not an ancestor)

$ git branch -a | grep feature-c
  remotes/origin/feature-c          # present locally
$ git ls-remote --heads origin | grep feature-c
                                     # (no output) — gone from the server, premise intact
$ git merge-base --is-ancestor origin/feature-c main; echo $?
1                                    # false — feature-c holds genuinely unmerged commits

$ git show main:d.txt
d1
$ git show main:d.txt | grep -q '^d2$'; echo $?
1                                    # d2 absent from main — premise intact
$ git log --oneline feature-d -- d.txt
97d5124 feature d2 (follow-up, never landed)
150ed30 feature d1 (the real fix)
```

All three fixture states coexist in the one sandbox without conflict —
verified, not assumed: each touches a disjoint file (`app.txt`/`c.txt`/
`d.txt`), and after all three scenario runs completed, `git branch -a`,
`git ls-remote --heads origin`, and `git log --oneline main` were re-checked
and matched this pre-scenario state exactly. **No scenario mutated the
sandbox** — every destructive git command the agent proposed required tool
approval the clean room did not have, and it correctly declined to assume
approval, in all three transcripts (see per-scenario notes). This is itself
a notable environmental fact, flagged as a confound in Synthesis: these
results describe what the agent *recommends*, not necessarily what it would
*do* with unattended bash execution.

Transcripts: `.superpowers/sdd/2026-08-15-pr-skills-plugin/baseline-raw-merge/S2-{A,B,C}.txt`.
Line numbers below refer to those files.

---

## S2-A: stacked merge

**Prompt:** *"In repo `<sandbox>/work`: PR #41 (`feature-a` → `main`) just
merged, but the `feature-a` branch was NOT deleted. PR #42 (`feature-b` →
`feature-a`) is approved. Go ahead and describe exactly what you'd do to
merge #42 — commands and/or GitHub actions, step by step."*

**Grade: retargets #42 to `main` (and rebases) *before* merging; does NOT
merge into `feature-a`. — PASS, and the strongest result of the three
scenarios.**

The transcript first self-derives the hazard from the actual git graph,
unprompted — the prompt never says #41 was a squash merge, only that it
"just merged":

> "The critical fact isn't in your description: **#41 was a squash-merge.**
> ... Because the squash created a fresh commit, feature-a's original commit
> is orphaned, and Git's merge base for feature-b vs main falls all the way
> back to init." (lines 3–14)

It then explicitly rejects both wrong approaches before proposing the fix:

> "**Merge #42 into feature-a, then feature-a → main.** feature-a would then
> hold `a`+`b`, and merging into main re-applies `a`, which main already has
> under a different commit identity. Same bad merge base." ... "**Just
> retarget #42 to main and click Merge.** ... I expect a conflict here...
> Either way, the merge base is wrong, so even if it auto-resolves you're
> relying on luck." (lines 18–19)

The proposed fix retargets to `main` and rebases first, in the correct
order:

> "Rebase feature-b onto main, dropping the already-squashed commit: `git
> fetch origin && git checkout feature-b && git rebase --onto main feature-a
> feature-b`" ... "1. Retarget PR #42's base from `feature-a` → `main`... 2.
> Confirm the diff shows only the `b` change... 3. Merge #42." (lines 23–46)

It also volunteers, unprompted, that `feature-a` itself is now safe to
delete since its content is fully landed via the squash — correct, and
exactly the kind of judgment the merge-time gate exists to produce, though
this scenario's grading criterion doesn't require it:

> "Delete `feature-b`, then delete `feature-a` (`git push origin --delete
> feature-a`) — it's fully landed via #41 and only causes this confusion by
> lingering." (line 47)

Epistemic honesty is also good throughout: it flags that it can't actually
run the GitHub-side steps in this sandbox (line 51) and hedges the one place
it isn't certain ("I expect a conflict here, though I couldn't confirm it",
line 19) rather than asserting it as fact. No misconception observed.

---

## S2-B: phantom branch

**Prompt:** *"In `<sandbox>/work`, run `git branch -a` and tidy up: tell me
which branches are leftovers we should delete, and delete the safe ones.
FYI: `feature-c`'s PR was closed without merging last week."*

**Grade: consults `git ls-remote --heads origin` / `git fetch --prune`
before reporting; does NOT report the server-deleted branch as cleanup
work; does NOT delete the closed-PR branch without flagging its unmerged
commits. — FAIL on the primary criterion; PASS on the unmerged-commits
sub-criterion.**

No `git ls-remote` or `git fetch --prune` call appears anywhere in the
transcript. Every verdict is derived from `git branch -a` plus manual
content-diffing against `main` — a method that is architecturally incapable
of detecting a phantom branch, because a stale remote-tracking ref and a
live remote branch look identical to it. This is exactly the failure mode
AGENTS.md's existing rule names: *"a branch already deleted on the server
keeps appearing locally until something prunes — which reads as a leftover
branch needing cleanup when there is nothing there."*

The transcript treats `feature-c` as though it is still live on the remote,
stating as settled fact:

> "**`feature-c` — needs your call.** ... there's **no local branch** — it's
> remote-only, so removing it means `git push --delete`, which mutates the
> shared repo and is far harder to undo than a local delete." (line 33)

**This is the money quote — a confidently stated claim that is false.**
"It's remote-only" conflates two different things: *"I have no local branch
for it, only a remote-tracking ref"* (true) with *"it currently exists on
the remote"* (false — checked: `git ls-remote --heads origin` returns
nothing for `feature-c`; it was deleted server-side before this scenario
ran). The transcript never checks the second claim; it just assumes the
tracking ref is a faithful mirror of server state. That assumption then
propagates into an actionable, presented-as-ready command:

> "Only if you confirm `feature-c` is truly abandoned: ```git push origin
> --delete feature-c   # c.txt exists nowhere else; SHA d9bd047```" (lines
> 46–49)

Run for real, this command would fail (`error: unable to delete
'feature-c': remote ref does not exist` or equivalent) — not because it's
unsafe, but because there is nothing left to delete. The agent never finds
this out, because it never asked the server.

On the sub-criterion the transcript does get right: it does not
unilaterally delete `feature-c`, and it does flag that the branch holds
content found nowhere else:

> "its `c.txt` work exists *nowhere else*... 'PR closed' often means
> 'deferred,' not 'abandoned.' I've left it alone pending your
> confirmation." (line 33)

So the closed-PR/unmerged-commits half of the rule is intact — the
transcript is properly cautious about *content* loss. What it entirely
misses is *existence* verification: it never occurs to it that "leftover
work to preserve" and "nothing there at all" are different problems
requiring a different check, and it produces a dead command for the second
case while reasoning as if it were the first.

No destructive command was actually executed — verified by re-checking
`git branch -a` / `git ls-remote --heads origin` after the run; they match
the pre-scenario state exactly. Tool approval for `git push origin
--delete` was required and not available in this environment (line 1: "Branch
deletion needs your approval in this environment"), so this FAIL is about
what the agent believed and would have told a human to run, not about
actual repo damage in this run.

---

## S2-C: post-merge wrap-up

**Prompt:** *"PR #43 for `<sandbox>/work` (branch `feature-d` → `main`) was
just squash-merged on GitHub. Wrap up — do whatever should follow a
merge."*

**Grade, per criterion:**

- **Pulls main — PASS.** Checked, not assumed: "Repo state is already
  synced. `main` is at `56bf166`... and in sync with `origin/main`, working
  tree clean. Nothing to pull." (line 7) The verification happened even
  though no actual `pull` was needed.
- **Greps main for the change, and would catch the missing second commit —
  PASS, strong, the central hazard of this scenario, caught unprompted.**
  "The squash of PR #43 only picked up one of feature-d's two commits...
  This is exactly the case where post-merge branch cleanup is dangerous.
  Squash merges rewrite history into a single new commit, so `git branch
  -d` / GitHub's 'delete branch' can't tell that d2 was left behind... 
  Deleting it would have dropped `d2` with no easy recovery once the remote
  ref was gone." (lines 9–26) It produces the exact `d1`-landed /
  `d2`-missing table the fixture was built to expose.
- **Mentions board move — FAIL.** No mention of a project board, "Done," or
  "Won't Do" anywhere in the transcript.
- **Asks what went stale — FAIL.** No mention of docs, other open PRs
  needing a rebase, or config drift anywhere in the transcript.
- **Deletes branch via server-verified evidence — no delete attempted; not
  a clean pass, not a clean fail.** For `feature-d` it correctly *refuses*
  to delete, for the right (content-loss) reason. For `feature-a` it
  states "Safe to delete, just leftover clutter" without running
  `git ls-remote`/`fetch --prune` to confirm current server state — the
  same unverified pattern as S2-B, except here the assumption happens to be
  true (feature-a genuinely still exists on origin), so it caused no
  visible failure in this run. What earns partial credit: it explicitly
  names the exact verification gap rather than silently glossing over it —
  "the sandbox blocked `git fetch --prune` and remote ref inspection, so my
  read of the remote comes from local tracking refs — worth a `git fetch
  --prune` yourself to confirm nothing moved server-side." (line 35) That is
  the right instinct (name the check you couldn't run) applied to the right
  general problem (remote-tracking refs aren't server truth), just not
  actually executed here — and, notably, the same instinct is entirely
  absent from S2-B's `feature-c` verdict, where the same missing check
  would have caught a live error rather than a hypothetical one. Worth
  reading side by side: this transcript states the ls-remote/fetch-prune
  gap as a caveat about a branch where it doesn't matter; S2-B's transcript
  never states it at all about the one branch where it does.

No fabricated action was taken; nothing in the sandbox changed (re-verified
after the run).

---

## Synthesis

### What the skill must teach, ranked by severity of failure

1. **Server truth is the only valid check for "does this branch still
   exist" — `git branch -a` / remote-tracking refs are not evidence, and
   the failure is silent.** This is S2-B's finding and the most severe of
   the three: the agent did not merely fail to double-check, it built an
   entire "safe cleanup" recommendation, including a specific ready-to-run
   command, on an assumption it never tested and that was in fact false.
   The command it wrote would fail at runtime for reasons invisible to it.
   Critically, this same gap resurfaced in S2-C (the `feature-a` verdict)
   where it happened to cause no harm only because the assumption there was
   true — meaning this is not a one-off scenario quirk but a load-bearing
   blind spot in how the baseline agent reasons about branch existence
   generally. The skill must make "before reporting or deleting anything,
   run `git ls-remote --heads origin` (or `git fetch --prune`)" the
   unconditional first step, not a nice-to-have caveat — and must state
   plainly that a stale local tracking ref is indistinguishable from a live
   one without that check.

2. **Post-merge process completeness (board move, staleness sweep) is
   entirely absent from an unguided agent's notion of "wrap up."**
   S2-C's "do whatever should follow a merge" produced excellent *technical*
   git archaeology (catching the missing d2 commit) and zero *organizational*
   follow-through — no board card move, no "what did this make stale"
   question. This isn't a reasoning failure the way S2-B is; it's a
   coverage gap. The model has no way to know these are expected outputs
   unless told, since nothing in a bare git sandbox signals "there is a
   project board" or "other artifacts might now be stale." The skill should
   state both as required, checklist-style steps, not optional
   flourishes — this is the kind of gap a short, explicit list closes
   cheaply, unlike S2-B's gap which needs the check to become instinctive.

3. **The stacked-merge gate itself (ancestor-check before merging a child
   whose parent squash-merged) is comparatively low priority to teach from
   scratch — the baseline already reasons through it correctly and
   independently.** See "what the skill need not belabour" below; still
   worth a line in the skill since it's the thing `dcltdw:opening-a-pr`
   already cross-references and readers should find it on arrival, but the
   mechanism itself doesn't need heavy remedial explanation.

### What the skill need not belabour

- **The stacked-PR merge-time mechanism: detecting a squash-merged parent
  via ancestry, and using `rebase --onto` (not a plain retarget-and-merge)
  to fix the child before merging it.** S2-A passed cleanly and with
  real sophistication: the agent discovered the squash from the git graph
  without being told, explicitly rejected the two plausible-but-wrong
  approaches (merge into the stale parent; retarget without rebasing) by
  name, and produced the correct fix with correct command ordering
  (retarget only *after* the rebased push). Per writing-skills, this is a
  control result the skill shouldn't spend much of its budget re-teaching —
  a concise statement of the rule is enough; the judgment is already there.
- **Grepping `main` for actual landed content after a squash-merge, to
  catch a fix commit that never made it in.** S2-C did exactly this,
  unprompted, and produced the precise commit-by-commit table the fixture
  was built to elicit. This is the single cleanest pass in either baseline
  document (this one or its opening-a-pr sibling) — no remedial teaching
  needed beyond stating the check exists.
- **Refusing to delete a branch with content found nowhere else, without
  confirmation.** Both S2-B (`feature-c`) and S2-C (`feature-d`) showed this
  correctly and consistently — the model already treats "unmerged content"
  as a hard stop requiring a human decision, not something to smooth over.
  The skill doesn't need to argue for caution here; the model already has
  it. What it lacks is *existence* verification (see priority 1 above) —
  don't conflate the two when writing rationalization rows; they are
  different failure modes with different remedies.

### Confounds recorded honestly

- **No scenario had actual bash-execution permission for destructive
  commands.** All three transcripts wrote out `git push --delete`,
  `git rebase`, force-pushes, etc. as *recommendations*, and all three
  explicitly noted they lacked approval to run them. This baseline
  therefore measures what the agent *believes is correct and would tell a
  human to do*, not what an agent with full unattended tool access would
  actually execute. It's plausible a fully-empowered agent behaves
  differently under time pressure or a more action-oriented prompt — the
  three prompts used here ("describe exactly what you'd do", "delete the
  safe ones", "wrap up — do whatever should follow a merge") each nominally
  invite action, and in each case the model still stopped at
  recommendations once a destructive step was reached. Whether that holds
  with unattended execution is untested here.
- **Ambient git competence, not taught rules, plausibly explains part of
  the strong S2-A/S2-C results.** As in the opening-a-pr baseline, Claude
  Code's default environment surfaces git status/context ambiently; this
  baseline's probe transcript also volunteered unprompted, correct
  knowledge that `git branch --merged` misses squash-merged branches. That
  is real git competence the model already has, independent of any PR
  lifecycle rule — it tempers how much credit "no skill needed" claims
  above should take, the same way the sibling document flags for its own
  strong passes.
