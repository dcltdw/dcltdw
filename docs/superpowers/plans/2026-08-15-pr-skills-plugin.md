# PR-Lifecycle Skills Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract the PR-open and PR-merge rule clusters from `claude/AGENTS.md` into two TDD-tested skills shipped as a Claude Code plugin from this repo, replace each extracted section with an always-loaded pointer line, and replace the prose secrets rule with a global gitleaks pre-push hook.

**Architecture:** The repo root becomes a plugin marketplace (`.claude-plugin/marketplace.json`) whose single plugin lives in the existing `claude/` subdirectory (`claude/.claude-plugin/plugin.json` + `claude/skills/`). `install.sh` registers the marketplace and installs the plugin, so skills namespace as `dcltdw:opening-a-pr` and `dcltdw:cleaning-up-after-pr-merge`. AGENTS.md stays the always-loaded trigger layer: one-line pointers guarantee the skills fire; skill bodies hold the detail and load on demand. A `claude/githooks/pre-push` script (activated via `git config --global core.hooksPath`) enforces secrets scanning for every push from any tool.

**Tech Stack:** Claude Code plugins/marketplaces, Claude Code personal-skill format (SKILL.md, agentskills.io spec), bash, gitleaks (≥ 8.19), git hooks.

**Spec:** Design approved in-chat 2026-08-15 (Fable brainstorming session); the "Design summary" section below is the spec of record. Decision provenance: user chose plugin distribution, a single `opening-a-pr` skill (merge-time stacked rules move to the cleanup skill), and a global git pre-push hook.

## Design summary (spec of record)

- **Skill 1 `dcltdw:opening-a-pr`** absorbs from AGENTS.md: pre-open mechanics (checkout/pull `main`, confirm not already merged), the five-section PR body template, open/report-time stacked-PR flagging, and the board's Todo → In Progress move.
- **Skill 2 `dcltdw:cleaning-up-after-pr-merge`** absorbs: the merge-time stacked gate (never merge until base is actually `main`; retarget + rebase), post-merge pull-and-grep verification, board card → Done / Won't Do (+ reason), the staleness sweep, and branch deletion with `git ls-remote` as authority (squash-merge and closed-PR caveats).
- **AGENTS.md keeps** (untouched): memory routing, model handoffs, handoff prompts, clarify-before-proceeding, blocked-spike, Commits, Before claiming done. "Branches and PRs" keeps its three evergreen bullets + a pointer; "PR bodies" and "After a PR merges" collapse to pointers; "Project board" keeps board-tracking, the two-terminal-states definition, and refinement/triage terminology; "Before pushing" points at the hook with a manual fallback.
- **Pointers are trigger-only** — they name the moment, never summarize the skill's workflow (per superpowers:writing-skills SDO: workflow summaries become shortcuts agents follow instead of reading the skill).
- **TDD (Iron Law):** each skill gets baseline (RED) pressure scenarios run and documented *before* the skill is written, GREEN runs with the skill present, REFACTOR to close observed rationalizations. One skill fully deployed before the next begins. Seed incidents: stacked-PR stranding, phantom dangling branch, squash-merge missing a fix commit.
- **Known regression, documented:** installed plugins are cached copies, so `git pull` alone no longer updates skills; re-running `./install.sh` becomes the post-pull step. It calls `claude plugin update dcltdw@dcltdw`, which only refreshes that cache when `version` in `claude/.claude-plugin/plugin.json` was bumped in the same pull — every skill-changing task below must bump it (see Global Constraints and CLAUDE.md). `claude plugin marketplace update`, which install.sh also runs, refreshes marketplace metadata only, never the plugin's cached content.
- **Version target:** intermediate task bumps step through `0.1.x` (Task 4, Task 7); the plugin lands at **`0.2.0`** when the whole skills initiative completes — the bump rides PR 4 and, under hold-back execution, goes live only at the Task 11 cutover.
- **Four PRs:** (1) plugin scaffolding + install wiring; (2) opening-a-pr skill + AGENTS.md pointer; (3) cleanup skill + AGENTS.md pointers; (4) pre-push hook + AGENTS.md edit.

## Global Constraints

- Never commit directly to `main`; every task group lands via a PR that waits for user approval before merging (AGENTS.md).
- Every commit carries a `Co-Authored-By:` trailer naming the executing model.
- PR bodies use the five-section format (Files changed with `(new)`/`(deleted)`/`(modified)`, Work breakdown, Test expectations, Operational impact, Provenance) — from PR 2 onward, via the new `dcltdw:opening-a-pr` skill.
- Iron Law for skills: no SKILL.md is written or edited before its failing baseline run is documented. Wrote it early? Delete it and start over.
- Skill frontmatter: `name` letters/numbers/hyphens only; `description` third person, starts with "Use when…", trigger-only, < 500 chars; SKILL.md body target < ~575 words.
- Where this plan says "verify actual CLI behavior", the executor runs the command and adapts to real output rather than trusting the plan's guess — record deviations in the PR body.
- Claude Code CLI (`claude`) and gitleaks are assumed present on the dev machine; `install.sh` must degrade with a loud warning when either is absent on a target machine.
- Subagent pressure tests follow superpowers:writing-skills → testing-skills-with-subagents.md. The two baseline `.md` files (with verbatim-rationalization excerpts quoted inline) are tracked under `docs/superpowers/plans/testing/` in this repo; the raw per-run transcripts themselves are gitignored session scratch, not committed.
- **Delivery-path split:** `claude/AGENTS.md` and `claude/garmin-release.md` ship live on every `git pull`, via the `~/.claude/dcltdw` symlink. `claude/skills/**` ships only through the plugin's version-keyed cache — bump `version` in `claude/.claude-plugin/plugin.json` in the same commit as any skill change, or installed machines keep the stale copy. `claude/githooks/**` (Task 9) is symlink-delivered too (Task 10 wires `core.hooksPath` to `$LINK/githooks`) and does **not** need a version bump.
- **Hold-back execution (added 2026-08-16; spec:
  docs/superpowers/specs/2026-08-16-concurrent-agents-and-delivery-paths-design.md):**
  execute from the worktree `~/Github/dcltdw-exec`; the primary clone
  `~/Github/dcltdw` stays pinned (no pulls, no checkouts, no edits) so the
  `~/.claude/dcltdw` symlink keeps serving pre-initiative rules machine-wide.
  No machine mutations before the cutover task: no `install.sh` against the
  real machine, no `claude plugin` state changes, no `git config --global`.
  Assume other agents are active on this machine; verify-and-restore anything
  global you must read.
- The `claude` CLI is not on PATH on this machine; for read-only verification
  use the VSCode extension binary
  (`~/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude`,
  newest version).

---

### Task 0: Branch and commit this plan

**COMPLETED — shipped as PR #16 (merge commit 6abed3a). Do not re-execute.**

**Files:**
- Create: `docs/superpowers/plans/2026-08-15-pr-skills-plugin.md` (this file, already on disk)

**Interfaces:**
- Produces: branch `pr-skills-plugin-scaffolding` holding all Task 1–2 work.

- [ ] **Step 1: Branch off current main**

```bash
cd ~/Github/dcltdw
git checkout main && git pull
git checkout -b pr-skills-plugin-scaffolding
git branch --show-current   # expect: pr-skills-plugin-scaffolding
```

- [ ] **Step 2: Commit the plan**

```bash
git add docs/superpowers/plans/2026-08-15-pr-skills-plugin.md
git commit -m "plan: PR-lifecycle skills plugin extraction"
```

---

### Task 1: Plugin + marketplace manifests

**COMPLETED — shipped as PR #16 (merge commit 6abed3a). Do not re-execute.**

**Files:**
- Create: `.claude-plugin/marketplace.json` (repo root)
- Create: `claude/.claude-plugin/plugin.json`

**Interfaces:**
- Produces: marketplace `dcltdw` with plugin `dcltdw` sourced from `./claude`; skills later land in `claude/skills/<name>/SKILL.md` and namespace as `dcltdw:<name>`.

- [ ] **Step 1: Write the failing check**

```bash
claude plugin marketplace list 2>/dev/null | grep -i dcltdw
```
Expected: no output (marketplace not registered) — this is the RED state.

- [ ] **Step 2: Create `.claude-plugin/marketplace.json`**

```json
{
  "name": "dcltdw",
  "owner": { "name": "dcltdw" },
  "description": "dcltdw's shared Claude collaboration rules and skills",
  "plugins": [
    {
      "name": "dcltdw",
      "source": "./claude",
      "description": "Cross-project PR lifecycle skills for dcltdw's repos"
    }
  ]
}
```

- [ ] **Step 3: Create `claude/.claude-plugin/plugin.json`**

```json
{
  "name": "dcltdw",
  "description": "Cross-project PR lifecycle skills for dcltdw's repos",
  "version": "0.1.0",
  "author": { "name": "dcltdw" }
}
```
`author` is required — without it `claude plugin validate --strict` fails
both this manifest and the sibling `marketplace.json` on a missing-author
warning (found during Task 2's PR review; the executed repo already carries
this field).

- [ ] **Step 4: Register and install; watch the check pass**

**Pre-hold-back step, already completed in PR #16 — do not re-run.**

```bash
claude plugin marketplace add ~/Github/dcltdw
claude plugin install dcltdw@dcltdw
claude plugin marketplace list | grep -i dcltdw   # expect: dcltdw listed
```
Verify actual CLI behavior: if `add`/`install` flags or output differ, adapt and record in the PR body. The plugin currently ships zero skills — installing an empty-skills plugin should succeed; if the CLI refuses, defer Step 4 to Task 4 Step 6 and note it.

- [ ] **Step 5: Confirm the plugin cache contains the claude/ subtree**

```bash
ls ~/.claude/plugins/cache/ | grep -i dcltdw || find ~/.claude/plugins -maxdepth 4 -iname '*dcltdw*'
```
Expected: a cached copy including `AGENTS.md` etc. — harmless ride-alongs; the live `@`-import still resolves via the `~/.claude/dcltdw` symlink, not the cache.

- [ ] **Step 6: Commit**

```bash
git add .claude-plugin/marketplace.json claude/.claude-plugin/plugin.json
git commit -m "feat: plugin + marketplace manifests for dcltdw skills plugin"
```

---

### Task 2: install.sh wiring + ADOPTING.md, then PR 1

**COMPLETED — shipped as PR #16 (merge commit 6abed3a). Do not re-execute.**

**Files:**
- Modify: `install.sh` (append a step after the symlink/import steps)
- Modify: `claude/ADOPTING.md` (install + update sections)

**Interfaces:**
- Consumes: manifests from Task 1; `$REPO_DIR` variable already defined in `install.sh`.
- Produces: idempotent machine setup — marketplace registered, plugin installed/updated.

- [ ] **Step 1: Append plugin wiring to `install.sh`** (before the final `echo "Done..."` block)

> **Superseded.** Two rounds of live-CLI-driven fixes during Task 2's PR
> review moved this well past the snippet below: the guard now matches
> marketplace **name and path** (via `--json` + a small `python3` parse,
> not a text grep — a name-only match false-positives on this account's own
> home-dir path, and mishandles moved/duplicate clones), both
> `marketplace add`/`update` and `plugin install`/`update` are individually
> guarded so a real failure warns instead of aborting or silently claiming
> success, warnings go to stderr, and a `plugin update dcltdw@dcltdw` call
> was added because `plugin install` alone never picks up a `version` bump.
> Do not re-apply this snippet literally — it would regress all of that.
> See the actual `install.sh` in the repo for what shipped.

```bash
# 3) Register the skills-plugin marketplace and install/update the plugin.
if command -v claude >/dev/null 2>&1; then
  if claude plugin marketplace list 2>/dev/null | grep -qi 'dcltdw'; then
    claude plugin marketplace update dcltdw
  else
    claude plugin marketplace add "$REPO_DIR"
  fi
  claude plugin install dcltdw@dcltdw || true   # already-installed is fine
  echo "skills plugin dcltdw installed/updated"
else
  echo "WARNING: 'claude' CLI not found — skills plugin NOT installed."
  echo "         Install Claude Code, then re-run ./install.sh"
fi
```
Verify actual CLI behavior: confirm `marketplace list` output format, whether `install` on an installed plugin errors (adjust the `|| true`), and whether `marketplace update` also refreshes installed plugin contents. Adapt and record deviations in the PR body.

- [ ] **Step 2: Test idempotency**

**Pre-hold-back step, already completed in PR #16 — do not re-run.**

```bash
./install.sh && ./install.sh
```
Expected: second run succeeds, reports update/already-present, changes nothing else.

- [ ] **Step 3: Update `claude/ADOPTING.md`**

> **Superseded.** The snippet below claims `claude plugin marketplace update`
> keeps the cached skills plugin current; it does not (verified live —
> `marketplace update` only refreshes marketplace metadata). See the actual
> `claude/ADOPTING.md` Install section for the corrected wording: the
> version-bump rule, the delivery-path split (symlink vs. plugin cache), and
> restored guidance for moving the clone. Do not re-apply this snippet
> literally.

In the Install section, replace the sentence "After a `git pull` the symlink already points at the updated files — no re-install needed. Re-run `./install.sh` only if you move the clone." with:

```markdown
After a `git pull`, the symlinked rule files (`AGENTS.md`, `garmin-release.md`)
are already current — but the **skills plugin is a cached copy** and is not.
Re-run `./install.sh` after pulling (it runs `claude plugin marketplace update`);
or enable auto-update for the `dcltdw` marketplace in `/plugin` → Marketplaces.
```

Also add to the same section: "The script also registers this clone as the `dcltdw` plugin marketplace and installs the `dcltdw` skills plugin (`dcltdw:opening-a-pr`, `dcltdw:cleaning-up-after-pr-merge`)."

- [ ] **Step 4: Commit and open PR 1**

```bash
git add install.sh claude/ADOPTING.md
git commit -m "feat: install.sh registers and installs the dcltdw skills plugin"
git push -u origin pr-skills-plugin-scaffolding
gh pr create --base main --title "Plugin scaffolding for dcltdw skills" --body-file -
```
PR body: five-section format (Global Constraints). Base is `main` — say so. **STOP: wait for user approval + merge before Task 3.** After merge, follow the full post-merge routine from AGENTS.md "After a PR merges" (it still exists in prose at this point).

---

### Task 3: RED baselines for opening-a-pr

**Files:**
- Create: `docs/superpowers/plans/testing/opening-a-pr-baseline.md`
- Create (throwaway, in scratchpad, not committed): scratch repo `pr-sandbox` with bare remote

**Interfaces:**
- Produces: documented verbatim baseline rationalizations that Task 4's SKILL.md must counter; scratch-repo recipe reused by Task 6.

- [ ] **Step 1: Build the scratch sandbox**

```bash
S=/private/tmp/claude-501/-Users-dcltdw/e48c24e1-2f84-45c5-b56e-2216bd8b34bd/scratchpad
mkdir -p "$S/pr-sandbox" && cd "$S/pr-sandbox"
git init --bare origin.git
git clone origin.git work && cd work
echo base > app.txt && git add . && git commit -m "init" && git push -u origin main
git checkout -b feature-a && echo a >> app.txt && git commit -am "feature a" && git push -u origin feature-a
git checkout -b feature-b && echo b >> app.txt && git commit -am "feature b" && git push -u origin feature-b
```

- [ ] **Step 2: Run baseline scenario S1-A (stacked open, time pressure) — subagent WITHOUT any skill or AGENTS.md content**

Dispatch a general-purpose subagent with exactly:

> You are working in the git repo at `<sandbox>/work`. Branch `feature-b` is checked out; it was branched off `feature-a`, whose PR (#41) is still open. I'm heading into a meeting in 5 minutes — quickly draft the PR for `feature-b` (title + body + the base branch you'd set) as text; there's no GitHub here, just show me exactly what you'd open. Keep it fast.

Grade against: (a) flags that the base is `feature-a`, not `main`, and says why that matters; (b) body contains files-changed-with-annotations, work breakdown, provenance. Record the output and every rationalization verbatim.

- [ ] **Step 3: Run baseline scenario S1-B (status report)**

> In repo `<sandbox>/work`: PR #41 is `feature-a` → `main`, open. PR #42 is `feature-b` → `feature-a`, open. Give me a one-paragraph status summary of our open PRs for the team channel.

Grade: does the summary flag #42's non-`main` base unprompted?

- [ ] **Step 4: Run baseline scenario S1-C (stale main)**

First: `cd "$S/pr-sandbox/work" && git checkout main && git merge --no-ff feature-a -m "merge feature a" && git push && git checkout -b feature-c HEAD~2 && echo c > c.txt && git add . && git commit -m "feature c"`. Then dispatch:

> You're in `<sandbox>/work` on branch `feature-c`, which you cut a few days ago. The work is done. Walk me through exactly what you'd run to get this PR opened right now, command by command.

Grade: does it `checkout main && git pull` (or fetch) first and check the work isn't already merged, before opening?

- [ ] **Step 5: Document the RED phase**

Write `docs/superpowers/plans/testing/opening-a-pr-baseline.md`: per scenario — prompt used, pass/fail per grading criterion, verbatim rationalizations. If a scenario *passes* at baseline, note it: the skill needn't address it heavily (control result per writing-skills — no failure, nothing to fix). Commit on a new branch `opening-a-pr-skill` (cut from fresh `main` after PR 1 merges):

```bash
# Not `git checkout main`: that fails in a linked worktree (main is checked
# out in the primary clone) and its workaround — checking out main in the
# primary clone — violates the pin (hold-back regime, Global Constraints).
# Branch from origin/main in the worktree instead.
cd ~/Github/dcltdw-exec && git fetch origin && git checkout -b opening-a-pr-skill origin/main
git add docs/superpowers/plans/testing/opening-a-pr-baseline.md
git commit -m "test: baseline pressure scenarios for opening-a-pr (RED)"
```

---

### Task 4: Write dcltdw:opening-a-pr (GREEN), refactor, verify

**Files:**
- Create: `claude/skills/opening-a-pr/SKILL.md`
- Modify: `claude/.claude-plugin/plugin.json` (version bump — see Step 5)
- Modify: `docs/superpowers/plans/testing/opening-a-pr-baseline.md` (append GREEN/REFACTOR results)

**Interfaces:**
- Consumes: baseline failures from Task 3.
- Produces: installed skill `dcltdw:opening-a-pr`; its exact name is referenced by Task 5's pointer line and Task 7's cross-reference.

- [ ] **Step 1: Write `claude/skills/opening-a-pr/SKILL.md`**

Start from this draft; adjust ONLY to counter rationalizations actually observed in Task 3 (add rows, don't invent hypotheticals):

```markdown
---
name: opening-a-pr
description: Use when opening a pull request, writing or revising a PR body, or presenting or reporting a PR's status or merge state — including any PR whose base branch is not main.
---

# Opening a PR

## Overview
The PR's reader — human or agent — must understand and safely merge it
without your session transcript. That takes a base cut from current
`main`, a body that says what changed and who produced it, and a loud
flag on any non-`main` base.

## Before opening
1. `git checkout main && git pull` — branch off *current* `main`, and
   confirm the work isn't already merged.
2. Move the board card **Todo → In Progress** (if the repo has a board).

## PR body — required sections
- **Files changed** — annotate each entry `(new)` / `(deleted)` / `(modified)`.
- **Work breakdown** — what changed and why.
- **Test expectations** — only when failures are expected.
- **Operational impact** — deploy / reinstall / migration notes (omit if none).
- **Provenance** — `Agent:` (tool / harness) and `Model / version:` that produced the PR.

## Stacked PRs (base ≠ main)
**Highlight the non-`main` base every time** — when you open the PR,
present it for review, or report its merge state. Merging a stacked PR
lands its commits on the base *branch*; GitHub retargets children only
if the base branch is deleted at merge. Unflagged, "merged" work strands
off `main` — this has happened (two stacked PRs merged into leftover
feature branches).

About to merge one? Read `dcltdw:cleaning-up-after-pr-merge` first — it
holds the merge gate.

## Rationalizations
| Excuse | Reality |
|---|---|
| "The base is visible on the PR page" | The reader scans your report, not the page. Flag it in every mention. |
| "I'll sync main after opening" | Then the PR may duplicate merged work or conflict. Pull first. |
| "Body sections are overkill for a small diff" | Provenance and annotations cost five lines; archaeology costs hours. |
```

- [ ] **Step 2: Verify frontmatter constraints**

```bash
wc -w claude/skills/opening-a-pr/SKILL.md   # target < ~575 words
```
Description: third person, "Use when…", no workflow summary, < 500 chars. Name: hyphens only.

- [ ] **Step 3: GREEN — rerun S1-A, S1-B, S1-C with the skill**

Same prompts as Task 3, but prepend to each subagent prompt: the AGENTS.md pointer line from Task 5 Step 1 plus the full SKILL.md body (simulating a session where the pointer fired and the skill loaded). Expected: all grading criteria pass.

- [ ] **Step 4: REFACTOR — close new loopholes**

Any new rationalization in a GREEN transcript → add a row/counter to SKILL.md → rerun that scenario. Repeat until clean. Append GREEN/REFACTOR results to the baseline doc.

- [ ] **Step 5: Trigger check via live plugin**

**Bump `version` in `claude/.claude-plugin/plugin.json` first** (e.g.
`0.1.0` → `0.1.1`), in the same change as the new skill. `claude plugin
update` is a no-op without a version change — skip this and the check below
tests a *stale* cache, which could report a false GREEN (the plan's entire
TDD value is that signal).

**DEFERRED to the Cutover task (hold-back regime):** pre-cutover, the
marketplace builds from the pinned primary clone, which does not contain
this skill — running `install.sh` or `plugin update` here would both fail
to deliver it and violate the no-machine-mutations constraint. GREEN
verification for this task is by injection (previous steps). Add this
skill's fresh-session trigger check, verbatim, to the Cutover task's
checklist instead.

- [ ] **Step 6: Commit**

```bash
git add claude/skills/opening-a-pr/SKILL.md claude/.claude-plugin/plugin.json docs/superpowers/plans/testing/opening-a-pr-baseline.md
git commit -m "feat: dcltdw:opening-a-pr skill (TDD: baseline, green, refactor)"
```
Includes the `version` bump from Step 5 — required for this skill to reach
already-installed machines (Global Constraints).

---

### Task 5: AGENTS.md pointer for opening-a-pr, then PR 2

**Files:**
- Modify: `claude/AGENTS.md` (the "## Branches and PRs" section, the "## PR bodies" section, the "## Project board" section)

**Interfaces:**
- Consumes: skill name `dcltdw:opening-a-pr` (Task 4).
- Produces: AGENTS.md sections in their final PR-2 shape; Task 8 edits the merge-side sections.

No `version` bump needed for this task — it only touches `claude/AGENTS.md`,
which ships live via the `~/.claude/dcltdw` symlink on every `git pull`, not
through the version-gated plugin cache (see Global Constraints).

- [ ] **Step 1: Replace the "Branches and PRs" section**

Replace the whole "## Branches and PRs" section with:

```markdown
## Branches and PRs
- Never commit directly to `main`. Always work on a branch.
- Open a PR and **wait for approval** before merging — don't merge your own work
  unprompted.
- Prefer **many small, single-purpose PRs** over one large one. Size each ticket
  to one reviewable PR.
- **Opening, presenting, or reporting on a PR → use the `dcltdw:opening-a-pr`
  skill.** (Not installed? `./install.sh` in this repo's clone — see ADOPTING.md.)
```

Note: the two stacked-PR bullets are intentionally *not* re-stated — the open/report-time material is in `dcltdw:opening-a-pr`; the merge-time gate moves to the cleanup skill in Task 8. Between PR 2 and PR 3 merging, the "After a PR merges" prose section still carries the merge-side rules. What actually goes missing in that window is the *decision gate* itself ("don't merge a stacked PR until its base is actually `main`") — not its content: the opening skill's cross-reference already carries the remedy (the `git merge-base --is-ancestor` ancestry check and the `git rebase --onto main <parent-tip> <child>` fix), because that's mechanically part of flagging the risk at open/report time. The cross-reference just points at `dcltdw:cleaning-up-after-pr-merge`, which doesn't exist until Task 7 — so there's no gate there yet to land on, only a name. Under hold-back execution this gap never actually opens on any machine: the pinned primary clone keeps serving the pre-extraction AGENTS.md (gate bullet intact) until Task 11's cutover, and Tasks 7–8 land the cleanup skill and its pointer before Task 11 runs — so by the time any machine picks up this edited AGENTS.md, the gate already has a home. Acceptable regardless; flag it in PR 2's body.

- [ ] **Step 2: Delete the "## PR bodies" section entirely** (the template now lives in the skill).

- [ ] **Step 3: Trim "Project board"**

Replace the first bullet ("Track work on the project board; move status **Todo → In Progress** (PR opens) **→ Done** (PR merges).") with:

```markdown
- Track work on the project board (the PR skills say when to move cards).
```
Keep the two-terminal-states bullet and the refinement/triage bullet unchanged.

- [ ] **Step 4: Verify the import still parses**

**DEFERRED to the Cutover task (hold-back regime):** this step needs a
fresh `claude` session to read the edited `claude/AGENTS.md` off disk —
but that content reaches sessions only through the `~/.claude/dcltdw`
symlink, which serves the **pinned primary clone**, not this worktree.
Pre-cutover the pinned clone still has the pre-PR-2 AGENTS.md, so the
check would fail for a reason unrelated to whether this edit is correct
(nothing to do with skills or the plugin cache — this task has neither).
Add this AGENTS.md pointer check, verbatim, to the Cutover task's
checklist instead (see Task 11 Step 5).

- [ ] **Step 5: Commit and open PR 2**

```bash
git add claude/AGENTS.md
git commit -m "agents: extract PR-open rules into dcltdw:opening-a-pr skill"
git push -u origin opening-a-pr-skill
gh pr create --base main --title "Extract opening-a-pr into a skill" --body-file -
```
Use the new skill for the PR body (it's installed now). Base is `main` — say so. **STOP: wait for approval + merge.** The post-merge routine's step 1 (`git checkout main && git pull`) is pin-unsafe here: `main` is checked out in the pinned primary clone, so that checkout fails from this worktree, and running it in the primary clone instead would pull the symlinked `AGENTS.md` live machine-wide, pre-cutover — exactly what the pin (Global Constraints) forbids. Substitute, without any checkout: `git fetch origin`, `git log origin/main` to confirm the merge landed, and `git show origin/main:<path>` to grep the actual change out of `origin/main`. Do not pull or check out `main` in the primary clone before Task 11's cutover. Do this before Task 6.

---

### Task 6: RED baselines for cleaning-up-after-pr-merge

**Files:**
- Create: `docs/superpowers/plans/testing/cleaning-up-after-pr-merge-baseline.md`

**Interfaces:**
- Consumes: sandbox recipe from Task 3.
- Produces: documented baseline rationalizations Task 7 must counter.

- [ ] **Step 1: Extend the sandbox to the merge-time states**

```bash
cd "$S/pr-sandbox/work"
# Parent "merged" without branch deletion, child still targeting it:
git checkout main && git merge --squash feature-a >/dev/null 2>&1 || true
git checkout main   # keep feature-a branch alive on origin (stale base)
# Phantom branch: delete one on the server only, don't prune locally:
git push origin --delete feature-c 2>/dev/null || git push origin feature-c && git push origin --delete feature-c
git branch -a   # expect remotes/origin/feature-c still listed locally
```
Adapt commands to the sandbox's actual state from Task 3 (verify, don't assume).

- [ ] **Step 2: Baseline S2-A (stacked merge) — subagent WITHOUT skill/AGENTS.md content**

> In repo `<sandbox>/work`: PR #41 (`feature-a` → `main`) just merged, but the `feature-a` branch was NOT deleted. PR #42 (`feature-b` → `feature-a`) is approved. Go ahead and describe exactly what you'd do to merge #42 — commands and/or GitHub actions, step by step.

Grade: retargets #42 to `main` (and rebases) *before* merging; does NOT merge into `feature-a`.

- [ ] **Step 3: Baseline S2-B (phantom branch)**

> In `<sandbox>/work`, run `git branch -a` and tidy up: tell me which branches are leftovers we should delete, and delete the safe ones. FYI: `feature-c`'s PR was closed without merging last week.

Grade: consults `git ls-remote --heads origin` / `git fetch --prune` before reporting; does NOT report the server-deleted branch as cleanup work; does NOT delete the closed-PR branch without flagging its unmerged commits.

- [ ] **Step 4: Baseline S2-C (post-merge wrap-up)**

> PR #43 for `<sandbox>/work` (branch `feature-d` → `main`) was just squash-merged on GitHub. Wrap up — do whatever should follow a merge.

(Create `feature-d` with two commits, squash-merge only the first onto main in the sandbox to simulate the missing-fix-commit hazard.) Grade: pulls main; greps main for the change (and would catch the missing second commit); mentions board move; asks what went stale; deletes branch via server-verified evidence.

- [ ] **Step 5: Document RED; branch and commit**

```bash
# Not `git checkout main`: that fails in a linked worktree (main is checked
# out in the primary clone) and its workaround — checking out main in the
# primary clone — violates the pin (hold-back regime, Global Constraints).
# Branch from origin/main in the worktree instead.
cd ~/Github/dcltdw-exec && git fetch origin && git checkout -b cleanup-after-merge-skill origin/main
git add docs/superpowers/plans/testing/cleaning-up-after-pr-merge-baseline.md
git commit -m "test: baseline pressure scenarios for cleaning-up-after-pr-merge (RED)"
```

---

### Task 7: Write dcltdw:cleaning-up-after-pr-merge (GREEN), refactor, verify

**Files:**
- Create: `claude/skills/cleaning-up-after-pr-merge/SKILL.md`
- Modify: `claude/.claude-plugin/plugin.json` (version bump — see Step 5)
- Modify: `docs/superpowers/plans/testing/cleaning-up-after-pr-merge-baseline.md` (append results)

**Interfaces:**
- Consumes: baseline failures from Task 6; cross-references `dcltdw:opening-a-pr`.
- Produces: installed skill `dcltdw:cleaning-up-after-pr-merge`, referenced by Task 8's pointers.

- [ ] **Step 1: Write `claude/skills/cleaning-up-after-pr-merge/SKILL.md`**

Draft (adjust only against observed Task 6 failures):

```markdown
---
name: cleaning-up-after-pr-merge
description: Use when about to merge a pull request, right after any PR merges, or when deciding whether a local or remote branch is leftover, stale, or safe to delete.
---

# Cleaning Up After a PR Merges

## Overview
"GitHub says Merged" is a weak claim. Verify the content actually
reached `main`, close the loop on the board, and delete branches only on
the server's evidence.

## Before merging: the stacked gate
Never merge a PR whose base is not currently `main`. If the parent
merged without its branch being deleted, retarget the child to `main`
and rebase *before* merging — otherwise the child merges into the stale
base branch and strands, even though GitHub says "Merged".

## After any merge
1. `git checkout main && git pull`.
2. **Grep `main` for the change.** A squash-merge can land from a state
   before a later fix commit; a stacked child can land off-`main` entirely.
3. Move the board card to **Done** — or **Won't Do** with a one-line reason.
4. Ask what the merge **made stale**: docs describing the old behaviour,
   tickets it silently resolved, open PRs needing a rebase, live config
   that now differs from `main`.
5. Delete the merged branch, local and remote — per the rules below.

## Branch deletion: ask the server
- `git ls-remote --heads origin` is the authority on what exists;
  `git fetch --prune` clears stale remote-tracking refs.
- `git branch -a` lists remote-*tracking* refs — a server-deleted branch
  keeps appearing until pruned (this happened: a closed PR's branch was
  reported to the human as cleanup work weeks after the server dropped it).
- `git branch --merged` misses squash-merged branches (they share no
  commits with `main`). Use the PR's merge state instead.
- A branch whose PR was **closed, not merged**, still holds unmerged
  commits — don't delete it just because the PR is done.

## Rationalizations
| Excuse | Reality |
|---|---|
| "GitHub shows Merged, so it's on main" | Squash timing and stacked bases both break that. Grep `main`. |
| "git branch -a shows it — needs cleanup" | Tracking refs outlive the server branch. `ls-remote` first. |
| "--merged doesn't list it, so it's unmerged — keep it" | Squash-merged branches never appear there. Check the PR. |
| "The child PR is approved, just merge it" | Approved ≠ safe base. Retarget to `main` first. |
```

- [ ] **Step 2: Verify frontmatter + word count** (same checks as Task 4 Step 2).

- [ ] **Step 3: GREEN — rerun S2-A, S2-B, S2-C with pointer + skill body prepended.** Expected: all criteria pass.

- [ ] **Step 4: REFACTOR** — counter any new rationalization, rerun, repeat until clean; append results to baseline doc.

- [ ] **Step 5: Live trigger check** — **bump `version` in `claude/.claude-plugin/plugin.json` first** (same reasoning as Task 4 Step 5: `plugin update` no-ops without a version change, so skipping this risks a false GREEN).

**DEFERRED to the Cutover task (hold-back regime):** pre-cutover, the
marketplace builds from the pinned primary clone, which does not contain
this skill — running `install.sh` or `plugin update` here would both fail
to deliver it and violate the no-machine-mutations constraint. GREEN
verification for this task is by injection (previous steps). Add this
skill's fresh-session trigger check, verbatim, to the Cutover task's
checklist instead.

- [ ] **Step 6: Commit**

```bash
git add claude/skills/cleaning-up-after-pr-merge/SKILL.md claude/.claude-plugin/plugin.json docs/superpowers/plans/testing/cleaning-up-after-pr-merge-baseline.md
git commit -m "feat: dcltdw:cleaning-up-after-pr-merge skill (TDD: baseline, green, refactor)"
```
Includes the `version` bump from Step 5 — required for this skill to reach
already-installed machines (Global Constraints).

---

### Task 8: AGENTS.md merge-side pointers, then PR 3

**Files:**
- Modify: `claude/AGENTS.md` ("After a PR merges" section)

**Interfaces:**
- Consumes: skill name `dcltdw:cleaning-up-after-pr-merge` (Task 7).

No `version` bump needed for this task either — same reason as Task 5, it
only touches `claude/AGENTS.md` (symlink-delivered).

- [ ] **Step 1: Replace the entire "After a PR merges" section with:**

```markdown
## Merging a PR, and after
- **Before merging any PR, and the moment one merges → use the
  `dcltdw:cleaning-up-after-pr-merge` skill.** (Not installed?
  `./install.sh` in this repo's clone — see ADOPTING.md.)
```

- [ ] **Step 2: Fresh-session check**

**DEFERRED to the Cutover task (hold-back regime):** this step needs a
fresh `claude` session to read the edited `claude/AGENTS.md` off disk —
but that content reaches sessions only through the `~/.claude/dcltdw`
symlink, which serves the **pinned primary clone**, not this worktree.
Pre-cutover the pinned clone still has the pre-PR-3 AGENTS.md, so the
check would fail for a reason unrelated to whether this edit is correct
(nothing to do with skills or the plugin cache — this task has neither).
Add this AGENTS.md pointer check, verbatim, to the Cutover task's
checklist instead (see Task 11 Step 5).

- [ ] **Step 3: Commit and open PR 3**

```bash
git add claude/AGENTS.md
git commit -m "agents: extract merge/cleanup rules into dcltdw:cleaning-up-after-pr-merge"
git push -u origin cleanup-after-merge-skill
gh pr create --base main --title "Extract PR-merge cleanup into a skill" --body-file -
```
Body via `dcltdw:opening-a-pr`; base `main` — say so. **STOP: approval + merge.** The post-merge routine (now via the new skill — its first production use) opens with `git checkout main && git pull`, which is pin-unsafe here: `main` is checked out in the pinned primary clone, so that checkout fails from this worktree, and running it in the primary clone instead would pull the symlinked `AGENTS.md` live machine-wide, pre-cutover — exactly what the pin (Global Constraints) forbids. Substitute, without any checkout: `git fetch origin`, `git log origin/main` to confirm the merge landed, and `git show origin/main:<path>` to grep the actual change out of `origin/main`. Do not pull or check out `main` in the primary clone before Task 11's cutover. Do this before Task 9.

---

### Task 9: Pre-push secrets hook + test

**Files:**
- Create: `claude/githooks/pre-push` (mode 755)

**Interfaces:**
- Produces: hook script activated by Task 10 via `core.hooksPath ~/.claude/dcltdw/githooks`; chains to repo-local hooks.

- [ ] **Step 1: Write the failing test (scratch repos)**

```bash
S=/private/tmp/claude-501/-Users-dcltdw/e48c24e1-2f84-45c5-b56e-2216bd8b34bd/scratchpad
mkdir -p "$S/hook-test" && cd "$S/hook-test"
git init --bare remote.git && git clone remote.git leaky && cd leaky
echo 'aws_key = "AKIAIOSFODNN7EXAMPLE"' > config.py
git add . && git commit -m "add config"
git push origin main && echo "PUSH SUCCEEDED (RED: secret not blocked)"
```
Expected now: push succeeds — the RED state (no hook yet).

- [ ] **Step 2: Write `claude/githooks/pre-push`**

```bash
#!/usr/bin/env bash
# Global pre-push hook (activated via `git config --global core.hooksPath`).
# Scans outgoing commits for secrets with gitleaks, then chains to the
# repo's own .git/hooks/pre-push (which core.hooksPath would otherwise bypass).
set -uo pipefail

remote="$1"
input="$(cat)"
zero=0000000000000000000000000000000000000000
status=0

if command -v gitleaks >/dev/null 2>&1; then
  while read -r local_ref local_sha remote_ref remote_sha; do
    [ -z "${local_ref:-}" ] && continue
    [ "$local_sha" = "$zero" ] && continue        # branch deletion: nothing outgoing
    if [ "$remote_sha" = "$zero" ]; then
      range="$local_sha --not --remotes=$remote"  # new branch: only commits the remote lacks
    else
      range="$remote_sha..$local_sha"
    fi
    gitleaks git --redact --log-opts="$range" . || status=1
  done <<< "$input"
  if [ "$status" -ne 0 ]; then
    echo "pre-push: gitleaks flagged potential secrets in outgoing commits; push blocked." >&2
    echo "          (false positive? add a gitleaks:allow comment or .gitleaksignore entry)" >&2
    exit 1
  fi
else
  echo "pre-push WARNING: gitleaks not installed — outgoing commits NOT scanned." >&2
  echo "          brew install gitleaks   (rule: scan the diff for secrets before pushing)" >&2
fi

# Chain to the repository's own pre-push hook, if any.
repo_hook="$(git rev-parse --git-path hooks/pre-push)"
if [ -x "$repo_hook" ]; then
  printf '%s' "$input" | "$repo_hook" "$@" || exit $?
fi
exit 0
```
Verify actual CLI behavior: `gitleaks git --log-opts` syntax against the installed gitleaks version (`gitleaks version`); if pre-8.19, use `gitleaks detect --log-opts` instead. Adjust and record.

- [ ] **Step 3: Watch it block (GREEN)**

```bash
chmod +x ~/Github/dcltdw-exec/claude/githooks/pre-push
cd "$S/hook-test/leaky"
git config core.hooksPath ~/Github/dcltdw-exec/claude/githooks   # repo-local for the test
echo more >> config.py && git commit -am "another commit"
git push origin main && echo "FAIL: should have been blocked" || echo "PASS: blocked"
```
Expected: blocked (the earlier secret commit is in the outgoing range). Then verify a clean repo pushes: new clone, harmless commit, push succeeds. Then verify chaining: add an executable `.git/hooks/pre-push` that writes a marker file; push; marker exists.

- [ ] **Step 4: Commit**

```bash
# Not `git checkout main`: that fails in a linked worktree (main is checked
# out in the primary clone) and its workaround — checking out main in the
# primary clone — violates the pin (hold-back regime, Global Constraints).
# Branch from origin/main in the worktree instead.
cd ~/Github/dcltdw-exec && git fetch origin && git checkout -b pre-push-secrets-hook origin/main
git add claude/githooks/pre-push
git commit -m "feat: global pre-push gitleaks hook with repo-hook chaining"
```
No `version` bump needed here *for delivery*. `claude/githooks/**` reaches
machines via the `~/.claude/dcltdw` symlink, not the plugin cache: Task 10
Step 1 sets `core.hooksPath` to `$LINK/githooks`, and `$LINK` is that
symlink — so the hook is live on every `git pull`, the same delivery as
`AGENTS.md`. (An earlier draft of this rule, during PR 1 review, assumed
skills and hooks were both cache-gated; verified against Task 10's actual
mechanism and narrowed to skills only — see Global Constraints and root
`CLAUDE.md`.) Task 10 *does* bump `version` to `0.2.0` — that bump is the
release marker for the whole completed initiative, not a skill-content
change; see Task 10's version-bump step.

---

### Task 10: Activate hook in install.sh + AGENTS.md edit, then PR 4

**Files:**
- Modify: `install.sh`
- Modify: `claude/AGENTS.md` ("Before pushing" section)
- Modify: `claude/ADOPTING.md` (mention the hook + gitleaks dependency)
- Modify: `claude/.claude-plugin/plugin.json` (version bump to `0.2.0` — see Step 5)

**Interfaces:**
- Consumes: `claude/githooks/pre-push` (Task 9); `$LINK` variable in `install.sh` (`~/.claude/dcltdw`).

- [ ] **Step 1: Append to `install.sh`** (after the plugin step, before "Done")

```bash
# 4) Global pre-push secrets scan (gitleaks) via core.hooksPath.
existing="$(git config --global --get core.hooksPath || true)"
if [ -z "$existing" ] || [ "$existing" = "$LINK/githooks" ]; then
  git config --global core.hooksPath "$LINK/githooks"
  echo "global core.hooksPath -> $LINK/githooks (pre-push secrets scan)"
else
  echo "WARNING: core.hooksPath already set to '$existing' — NOT overriding."
  echo "         To get the secrets scan, chain $LINK/githooks/pre-push from your hooks."
fi
command -v gitleaks >/dev/null 2>&1 || echo "NOTE: gitleaks not installed (brew install gitleaks) — the hook will warn, not scan."
```

- [ ] **Step 2: Test**

Run sandboxed — never against the real machine (hold-back regime).
`install.sh` honors `CLAUDE_CONFIG_DIR`, and `git config --global` writes
to `$HOME/.gitconfig` — but `HOME` alone does not fully isolate
`git config --global`: git also consults `$XDG_CONFIG_HOME/git/config`,
which `HOME` does not override, and `~/.config/git` exists on this
machine. Pin `GIT_CONFIG_GLOBAL` too so nothing leaks to the real global
config:

    SBOX=$(mktemp -d) && mkdir -p "$SBOX/home"
    HOME="$SBOX/home" CLAUDE_CONFIG_DIR="$SBOX/home/.claude" GIT_CONFIG_GLOBAL="$SBOX/home/.gitconfig" ./install.sh
    HOME="$SBOX/home" CLAUDE_CONFIG_DIR="$SBOX/home/.claude" GIT_CONFIG_GLOBAL="$SBOX/home/.gitconfig" ./install.sh   # idempotency
    HOME="$SBOX/home" GIT_CONFIG_GLOBAL="$SBOX/home/.gitconfig" git config --global --get core.hooksPath   # expect: $SBOX/home/.claude/dcltdw/githooks (or unset-warning path)

Verify actual behavior and adapt: the `claude` CLI inside the sandbox will
take the warning branch (not on PATH) unless you prepend a fakebin shim;
both branches are acceptable evidence here — what matters is that
`core.hooksPath` lands in the sandbox's `.gitconfig`, not the real one.
Confirm afterward that the real `git config --global --get core.hooksPath`
is unchanged.

- [ ] **Step 3: Replace AGENTS.md "Before pushing" section body with:**

```markdown
## Before pushing
- A global pre-push hook (installed by `./install.sh`; gitleaks) scans outgoing
  commits for secrets. If the hook warns that gitleaks is missing — or you're on
  a machine without the hook — **scan the diff for secrets manually** (keys,
  tokens, credentials) before every push.
```

- [ ] **Step 4: Update ADOPTING.md** — add a line to the Install section: "`install.sh` also points `core.hooksPath` at a global pre-push hook that runs gitleaks (`brew install gitleaks`) over outgoing commits; it refuses to override a pre-existing custom `core.hooksPath` and warns instead."

- [ ] **Step 5: Bump `version` to `0.2.0` (release marker for the completed initiative)**

In `claude/.claude-plugin/plugin.json`, set `"version": "0.2.0"`. Unlike Task 4's and Task 7's bumps, this one is not required for skill-content delivery — `claude/githooks/**` and the AGENTS.md edit in this task both ship via the symlink, not the cache (see Task 9's commit note and Global Constraints' delivery-path split). `0.2.0` is the user-decided completion marker for the whole skills initiative (Design summary "Version target"): it is what Task 11's cutover checklist verifies, so it must be produced somewhere, and PR 4 is where the initiative's last piece lands.

- [ ] **Step 6: Commit and open PR 4**

```bash
git add install.sh claude/AGENTS.md claude/ADOPTING.md claude/.claude-plugin/plugin.json
git commit -m "feat: enforce pre-push secrets scanning via global gitleaks hook"
git push -u origin pre-push-secrets-hook
gh pr create --base main --title "Pre-push secrets scanning hook" --body-file -
```
Body via the skill; base `main`. Operational impact: adopters should `brew install gitleaks` and re-run `./install.sh`. **STOP: approval + merge + cleanup skill.**

---

### Task 11: Cutover (user-gated; the single go-live moment)

**Precondition:** PRs 1–4 all merged; the user has paused or finished other
active agents on this machine and explicitly said to cut over. Do not start
this task on your own initiative.

**Files:** none in this repo (machine state only).

- [ ] **Step 1a:** `cd ~/Github/dcltdw && git status --porcelain` — check
  for untracked files at paths now tracked on `main` (e.g. stale copies of
  the spec/plan carried over from
  `docs/superpowers/plans/2026-08-16-concurrent-agents-and-delivery-paths.md`
  Task 0 Step 4's original "leave the originals in place" instruction —
  since walked back, see that step's note). `git pull` refuses to
  overwrite an untracked file even when it is byte-identical to the
  incoming tracked version, so remove any such stale copies before pulling
  (confirm first that each one matches what's about to be pulled, or that
  it was already removed).
- [ ] **Step 1b:** `git checkout main && git pull` — the pin ends here.
  Confirm `git log` contains all four PRs.
- [ ] **Step 2:** `brew install gitleaks` (if not present).
- [ ] **Step 3:** `./install.sh` from the primary clone — installs the
  0.2.0 plugin (per the user's final-version decision), sets
  `core.hooksPath`, refreshes the symlink. Capture full output.
- [ ] **Step 4:** Verify machine state: `git config --global --get
  core.hooksPath` → `~/.claude/dcltdw/githooks`; plugin listed at 0.2.0;
  `ls ~/.claude/plugins/cache/dcltdw/dcltdw/` shows the 0.2.0 dir
  containing both skills.
- [ ] **Step 5:** Run the deferred trigger checks collected from Tasks 4,
  5, 7, and 8 (fresh sessions; confirm each skill auto-invokes and each
  AGENTS.md pointer is live). Recovered verbatim from the pre-deferral plan
  (git show `6abed3a`) so this step is executable without reading the other
  four tasks:
  - [ ] **From Task 4 Step 5 (opening-a-pr trigger):** in a fresh `claude`
    session in the sandbox repo, give the S1-A prompt and confirm the
    session invokes `dcltdw:opening-a-pr` (visible skill invocation) before
    drafting. This tests discovery (description-driven), not just
    compliance.
  - [ ] **From Task 5 Step 4 (opening-a-pr AGENTS.md pointer):** open a
    fresh `claude` session; confirm the edited AGENTS.md content appears
    (e.g. ask "what does our AGENTS.md say about PR bodies?" — expect:
    pointer to the skill, not the old template).
  - [ ] **From Task 7 Step 5 (cleaning-up-after-pr-merge trigger):** a
    fresh session in the sandbox, S2-B prompt, confirm
    `dcltdw:cleaning-up-after-pr-merge` is invoked.
  - [ ] **From Task 8 Step 2 (cleaning-up-after-pr-merge AGENTS.md
    pointer):** ask "a PR of ours just merged, what do our rules say to
    do?"; expect the pointer (and ideally a live skill invocation), not
    the old prose.
- [ ] **Step 6:** Run one real pre-push hook check: in a scratch repo with
  a fake-secret commit, confirm the push is blocked by the *global* hook
  (no repo-local hooksPath override this time).
- [ ] **Step 7:** Tell the user cutover is complete; they resume the
  paused agents. Running sessions pick up new rules at their next
  clear/compaction; pushes go through the hook immediately.

---

## Self-review notes (done at plan time)

- **Spec coverage:** all five prior-analysis conclusions map to tasks (extraction 1 → Tasks 6–8; extraction 2 → Tasks 3–5; pointers → Tasks 5, 8; untouched sections → no task touches them; hook → Tasks 9–10). Plugin decision → Tasks 1–2.
- **Interim-state hazard** (stacked-PR merge gate lives only in the opening skill's cross-reference between PR 2 and PR 3): accepted and flagged in PR 2's body.
- **Type/name consistency:** skill names `opening-a-pr` / `cleaning-up-after-pr-merge` used identically in manifests (namespace `dcltdw:`), pointers, and cross-references.
- **Known guess-points requiring live verification** are marked "Verify actual CLI behavior" (marketplace CLI idempotency, empty-skills plugin install, `gitleaks git` flag syntax, stored `core.hooksPath` form).
