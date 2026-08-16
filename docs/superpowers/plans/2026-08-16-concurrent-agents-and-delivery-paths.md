# Concurrent-Agents Rule & Delivery-Paths Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the "Concurrent agents" isolation rule to AGENTS.md (PR A), document the symlink/plugin delivery-path split with its exit criteria and retire `universal.md` (PR B), and amend the in-flight skills plan to the hold-back/cutover execution regime — all without any change reaching other running agents before the user-chosen cutover.

**Architecture:** Two small main-based PRs executed from a persistent git worktree while the primary clone stays pinned at post-#16 `main`. The `~/.claude/dcltdw` symlink serves the pinned clone's checkout, so upstream merges stay dormant machine-wide until the cutover runbook (added to the in-flight plan as its final task) pulls the clone and runs `install.sh` once.

**Tech Stack:** git worktrees, markdown, gh CLI. No code.

**Spec:** `docs/superpowers/specs/2026-08-16-concurrent-agents-and-delivery-paths-design.md` — the spec of record; conflicts in this plan resolve against it. It contains the exact AGENTS.md rule text and all decision provenance.

## Global Constraints

- **Hold-back regime (from the spec, binding on every task):** the primary clone `~/Github/dcltdw` stays checked out at `main` and is pulled exactly once (Task 0, post-#16). After that: no pulls, no branch checkouts, no edits in the primary clone until cutover. All work happens in the worktree `~/Github/dcltdw-exec`.
- **No machine mutations:** do not run `install.sh` against the real machine; no `claude plugin install/update/marketplace` state changes; no `git config --global`; no writes under `~/.claude/`. The `claude` CLI (VSCode extension binary at `~/.vscode/extensions/anthropic.claude-code-2.1.233-darwin-x64/resources/native-binary/claude`, or any newer version-stamped sibling) is for **read-only** verification only.
- PR #16 must be MERGED before Task 0 proceeds; verify, don't assume.
- Never commit to `main`. Both PRs base `main` (say so in each body); each stops for user approval before merging. They touch disjoint files and may merge in either order.
- Every commit carries `Co-Authored-By:` naming the executing model.
- PR bodies use the five-section AGENTS.md format (Files changed with `(new)`/`(deleted)`/`(modified)`, Work breakdown, Test expectations, Operational impact, Provenance) — the `dcltdw:opening-a-pr` skill is not live yet; the prose section on `main` still applies.
- No plugin `version` bump in either PR: AGENTS.md, ADOPTING.md, spec and plan files are symlink-delivered or repo-local; nothing here ships through the cache.
- Both PR bodies must state: **merging does not make this live** — changes reach the machine at cutover (see the in-flight plan's cutover task), because the primary clone is pinned.

---

### Task 0: Verify gate, pin the primary clone, create the worktree

**Files:**
- No repo file changes (operational setup only, plus one append to the in-flight plan's untracked ledger).

**Interfaces:**
- Produces: pinned primary clone at post-#16 `main`; worktree `~/Github/dcltdw-exec` on branch `agents-concurrent-rule`; hold notice in the old ledger.

- [ ] **Step 1: Verify PR #16 is merged**

```bash
cd ~/Github/dcltdw && gh pr view 16 --json state --jq .state
```
Expected: `MERGED`. If `OPEN`: **stop** — this plan is blocked on the user merging #16. Do not proceed.

- [ ] **Step 2: Pin the primary clone (the one permitted pull)**

```bash
cd ~/Github/dcltdw
git status --short          # expect: clean or untracked-only (.superpowers/, docs/ spec+plan, .DS_Store)
git checkout main && git pull
git log --oneline -1        # record: this is the pin commit
git worktree list           # expect: only the primary clone so far
```
Post-#16 `main` is behaviorally inert machine-wide (no AGENTS.md changes, no skills), so this pull is safe. From here on the primary clone is read-only until cutover.

- [ ] **Step 3: Create the execution worktree**

```bash
cd ~/Github/dcltdw
git worktree add ../dcltdw-exec -b agents-concurrent-rule main
cd ~/Github/dcltdw-exec && git branch --show-current   # expect: agents-concurrent-rule
```

- [ ] **Step 4: Copy the spec and this plan into the worktree**

Both files are untracked in the primary clone (`docs/superpowers/specs/2026-08-16-concurrent-agents-and-delivery-paths-design.md` and `docs/superpowers/plans/2026-08-16-concurrent-agents-and-delivery-paths.md`). Copy them to the same relative paths in `~/Github/dcltdw-exec` (create directories as needed). Leave the originals in place — the primary clone is not to be edited, and untracked files don't affect its pin.

**Note (added post-review, 2026-08-16):** "Leave the originals in place" created a hazard — once these paths are tracked here and merge to `main`, the primary clone's Task 11 Step 1b `git pull` refuses to overwrite the still-untracked local copies, even though they're byte-identical to the incoming tracked files. The controller subsequently removed both untracked copies from the primary clone by ruling (nothing was lost — they matched what's committed here byte-for-byte); Task 11 Step 1a (added by Task 2 Step 9) now also defends against this recurring.

- [ ] **Step 5: Append a hold notice to the in-flight plan's ledger**

Append to `~/Github/dcltdw/.superpowers/sdd/2026-08-15-pr-skills-plugin/progress.md` (untracked scratch — writing it does not violate the pin):

```markdown
## HOLD (2026-08-16, concurrent-agents initiative)

Do NOT resume Task 3 until PRs A and B of
docs/superpowers/plans/2026-08-16-concurrent-agents-and-delivery-paths.md merge.
Execution then follows the AMENDED 2026-08-15 plan: work from the worktree
~/Github/dcltdw-exec, primary clone stays pinned, machine mutations defer to
the new cutover task. Move this ledger directory into the worktree
(mv .superpowers/sdd/2026-08-15-pr-skills-plugin ~/Github/dcltdw-exec/.superpowers/sdd/)
when resuming.
```

- [ ] **Step 6: Commit the spec and plan (worktree)**

```bash
cd ~/Github/dcltdw-exec
git add docs/superpowers/specs/2026-08-16-concurrent-agents-and-delivery-paths-design.md \
        docs/superpowers/plans/2026-08-16-concurrent-agents-and-delivery-paths.md
git commit -m "docs: concurrent-agents + delivery-paths design and plan"
```

---

### Task 1: PR A — the "Concurrent agents" section in AGENTS.md

**Files:**
- Modify: `claude/AGENTS.md` (insert one section; no other lines change)

**Interfaces:**
- Consumes: exact rule text from the spec's Item A section.
- Produces: branch `agents-concurrent-rule` pushed; PR A open, base `main`.

- [ ] **Step 1: Insert the section**

In `~/Github/dcltdw-exec/claude/AGENTS.md`, insert the following between the end of the "## Before deferring as \"blocked\"" section and the "## Branches and PRs" heading — copied **verbatim from the spec** (the spec is authoritative if this plan and it ever differ):

```markdown
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
```

- [ ] **Step 2: Verify the edit is insertion-only and well-placed**

```bash
cd ~/Github/dcltdw-exec
git diff --stat claude/AGENTS.md            # expect: exactly one file, insertions only, 0 deletions
grep -n '^## ' claude/AGENTS.md             # expect "Concurrent agents" between "Before deferring" and "Branches and PRs"
git diff claude/AGENTS.md | grep -c '^-[^-]' # expect: 0 (no removed lines)
```

- [ ] **Step 3: Commit**

```bash
git add claude/AGENTS.md
git commit -m "agents: assume concurrent agents; isolate worktree work, verify-and-restore machine state"
```

- [ ] **Step 4: Push and open PR A**

```bash
git push -u origin agents-concurrent-rule
gh pr create --base main --title "AGENTS.md: concurrent-agent isolation rule" --body-file <body>
```
Body: five-section format. Base is `main` — say so. Operational impact must state the hold-back fact: the rule merges now but goes live machine-wide only at the skills initiative's cutover, because the primary clone is pinned; sessions executing the amended skills plan get the rule via that plan's Global Constraints in the meantime. **STOP: wait for user approval. Do not merge.** Task 2 may proceed while PR A awaits review (disjoint files).

---

### Task 2: PR B — delivery-paths docs, universal.md retirement, in-flight plan amendments

**Files:**
- Modify: `claude/ADOPTING.md` (add "Delivery paths" section; remove the universal.md back-compat note)
- Delete: `claude/universal.md` (symlink)
- Modify: `docs/superpowers/plans/2026-08-15-pr-skills-plugin.md` (hold-back amendments + new cutover task)
- Modify: `.gitignore` (track `.superpowers/` scratch)

**Interfaces:**
- Consumes: spec Item B and hold-back sections.
- Produces: branch `delivery-paths-docs` pushed; PR B open, base `main`.

- [ ] **Step 1: Branch off main (worktree)**

```bash
cd ~/Github/dcltdw-exec
# Not `git checkout main`: main is already checked out in the primary clone,
# so a linked worktree's checkout of the same branch fails outright
# (`fatal: 'main' is already used by worktree at ...`, reproduced on git
# 2.50.1) — and the obvious recovery, checking out main in the primary
# clone, is a direct pin violation. Fetch and branch from origin/main
# instead; never check out main locally in this worktree.
git fetch origin
git checkout -b delivery-paths-docs origin/main
```
(If PR A has merged by now this picks up its commit; if not, branching from pre-A main is equally fine — the files are disjoint.)

- [ ] **Step 2: Add the "Delivery paths" section to `claude/ADOPTING.md`**

Insert after the Install section, immediately after the existing post-pull/version-bump paragraphs (`claude/ADOPTING.md:30–46`):

```markdown
## Delivery paths

This directory ships through two complementary channels — neither replaces
the other:

- **The `~/.claude/dcltdw` symlink** (created by `install.sh`) carries
  everything that must be *live on pull*: the always-loaded `AGENTS.md`
  import, per-repo opt-in imports (`garmin-release.md`), and — once the
  pre-push hook lands — `githooks/`, which `core.hooksPath` points into.
- **The `dcltdw` plugin cache** carries `skills/` only, gated by `version`
  bumps in `.claude-plugin/plugin.json`.

Plugin-only delivery is not currently possible (verified against Claude
Code 2.1.233, 2026-08): plugins cannot contribute always-loaded
instruction text, cannot serve per-repo conditional content or
version-stable import paths, and their cache path is version-stamped and
therefore unusable as a `core.hooksPath` target. **Revisit retiring the
symlink when Claude Code ships all three:** (1) always-loaded plugin
instruction text; (2) per-repo conditional plugin content or a
version-stable import path into an installed plugin; (3) a version-stable
path suitable for `core.hooksPath` (or plugin-managed git hooks). Any one
of them landing is worth a fresh look; all three are needed to retire the
symlink outright.
```

- [ ] **Step 3: Retire `universal.md`**

```bash
cd ~/Github/dcltdw-exec
git rm claude/universal.md
```
Then delete the back-compat blockquote from `claude/ADOPTING.md` (the `> universal.md remains as a back-compat symlink…` note). Do **not** touch `install.sh`'s legacy-import migration — it stays as the safety net, per the spec.

- [ ] **Step 4: Track `.superpowers/` in the tracked `.gitignore`**

The tracked `.gitignore` currently contains only `.DS_Store`; the SDD scratch
tree is excluded only by `.superpowers/sdd/.gitignore`, which contains a bare
`*` — itself disposable scratch that self-ignores. Recreate the scratch tree
without that inner file present (e.g. a fresh clone, or after it's deleted)
and a `git add -A` would commit the whole ledger. Add to the tracked
`.gitignore`:

```
.superpowers/
```

- [ ] **Step 5: Amend the in-flight plan — Global Constraints**

In `docs/superpowers/plans/2026-08-15-pr-skills-plugin.md`, append to the Global Constraints list:

```markdown
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
```

- [ ] **Step 6: Amend the in-flight plan — defer the live trigger checks**

Locate Task 4 Step 5 and Task 7 Step 5 (the live trigger checks; the fix-wave text requires a `version` bump, `./install.sh`, a cache presence check, and a fresh-session skill-invocation test). In **each**, keep the version-bump requirement (the bump still rides the skill's commit) and replace the install/cache/fresh-session portion with:

```markdown
**DEFERRED to the Cutover task (hold-back regime):** pre-cutover, the
marketplace builds from the pinned primary clone, which does not contain
this skill — running `install.sh` or `plugin update` here would both fail
to deliver it and violate the no-machine-mutations constraint. GREEN
verification for this task is by injection (previous steps). Add this
skill's fresh-session trigger check, verbatim, to the Cutover task's
checklist instead.
```

Apply the same deferral to Task 8 Step 2 and Task 5 Step 4 (the fresh-session AGENTS.md pointer checks): the pointer edits are symlink-delivered but the pinned clone won't contain them until cutover, so those checks also move to the Cutover checklist.

- [ ] **Step 7: Amend the in-flight plan — replace stale AGENTS.md line-number references in Task 5**

Task 5 of `docs/superpowers/plans/2026-08-15-pr-skills-plugin.md` addresses
`claude/AGENTS.md` by line number in three places. Those numbers were
correct at `6abed3a`, but PR A's insertion shifts everything after it —
"lines 89–108" now spans exactly the new `## Concurrent agents` section,
start to end. An executor who trusts the literal numbers would delete the
rule PR A adds and leave "Branches and PRs" untouched. Replace all three
with heading anchors so they can't drift again this way; preserve each
bullet's surrounding meaning, only the addressing changes:

- **Files block:** ``- Modify: `claude/AGENTS.md` ("Branches and PRs"
  lines 89–108, "PR bodies" lines 110–117, "Project board" lines 119–125)``
  → ``- Modify: `claude/AGENTS.md` (the "## Branches and PRs" section, the
  "## PR bodies" section, the "## Project board" section)``
- **Step 1:** `Replace the whole section (currently lines 89–108) with:` →
  `Replace the whole "## Branches and PRs" section with:`
- **Step 2:** `- [ ] **Step 2: Delete the "PR bodies" section entirely**
  (lines 110–117; the template now lives in the skill).` → `- [ ] **Step 2:
  Delete the "## PR bodies" section entirely** (the template now lives in
  the skill).`

- [ ] **Step 8: Amend the in-flight plan — sandbox Task 10's install.sh testing**

In Task 10 Step 2 (idempotency test of `install.sh` with the hookPath step), replace the bare `./install.sh` runs with sandboxed runs and add the isolation note:

```markdown
Run sandboxed — never against the real machine (hold-back regime).
`install.sh` honors `CLAUDE_CONFIG_DIR`, and `git config --global` writes
to `$HOME/.gitconfig`, so a scratch HOME isolates everything:

    SBOX=$(mktemp -d) && mkdir -p "$SBOX/home"
    HOME="$SBOX/home" CLAUDE_CONFIG_DIR="$SBOX/home/.claude" ./install.sh
    HOME="$SBOX/home" CLAUDE_CONFIG_DIR="$SBOX/home/.claude" ./install.sh   # idempotency
    HOME="$SBOX/home" git config --global --get core.hooksPath   # expect: $SBOX/home/.claude/dcltdw/githooks (or unset-warning path)

Verify actual behavior and adapt: the `claude` CLI inside the sandbox will
take the warning branch (not on PATH) unless you prepend a fakebin shim;
both branches are acceptable evidence here — what matters is that
`core.hooksPath` lands in the sandbox's `.gitconfig`, not the real one.
Confirm afterward that the real `git config --global --get core.hooksPath`
is unchanged.
```

- [ ] **Step 9: Amend the in-flight plan — add the Cutover task**

Append after Task 10, before the Self-review section:

```markdown
---

### Task 11: Cutover (user-gated; the single go-live moment)

**Precondition:** PRs 1–4 all merged; the user has paused or finished other
active agents on this machine and explicitly said to cut over. Do not start
this task on your own initiative.

**Files:** none in this repo (machine state only).

- [ ] **Step 1a:** `cd ~/Github/dcltdw && git status --porcelain` — check
  for untracked files at paths this branch now tracks (e.g. stale copies of
  the spec/plan carried over from Task 0 Step 4's original "leave the
  originals in place" instruction — since walked back, see that step's
  note). `git pull` refuses to overwrite an untracked file even when it is
  byte-identical to the incoming tracked version, so remove any such stale
  copies before pulling (confirm first that each one matches what's about
  to be pulled, or that it was already removed).
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
  AGENTS.md pointer is live).
- [ ] **Step 6:** Run one real pre-push hook check: in a scratch repo with
  a fake-secret commit, confirm the push is blocked by the *global* hook
  (no repo-local hooksPath override this time).
- [ ] **Step 7:** Tell the user cutover is complete; they resume the
  paused agents. Running sessions pick up new rules at their next
  clear/compaction; pushes go through the hook immediately.
```

Also update the plan's version-bump note in the Design summary if needed so Task 11's "0.2.0" claim is consistent with the user's decision recorded there (PR 4 bumps to 0.2.0; intermediate task bumps step through 0.1.x).

- [ ] **Step 10: Self-check the amended plan**

```bash
cd ~/Github/dcltdw-exec
grep -n "DEFERRED to the Cutover" docs/superpowers/plans/2026-08-15-pr-skills-plugin.md | wc -l   # expect: 4
grep -n "### Task 11: Cutover" docs/superpowers/plans/2026-08-15-pr-skills-plugin.md              # expect: present, after Task 10
grep -n "Hold-back execution" docs/superpowers/plans/2026-08-15-pr-skills-plugin.md               # expect: in Global Constraints
grep -n 'lines 89\|lines 110\|lines 119' docs/superpowers/plans/2026-08-15-pr-skills-plugin.md    # expect: no output (Step 7's heading-anchor replacement)
```
Read the amended Task 4/5/7/8 steps once end-to-end: each must still make sense as a sequence (bump kept, injection GREEN kept, deferral note in place).

- [ ] **Step 11: Commit, push, open PR B**

```bash
git add claude/ADOPTING.md .gitignore docs/superpowers/plans/2026-08-15-pr-skills-plugin.md
git commit -m "docs: delivery-path split + exit criteria; retire universal.md; hold-back amendments to skills plan"
git push -u origin delivery-paths-docs
gh pr create --base main --title "Delivery paths: document the split, retire universal.md, hold-back cutover" --body-file <body>
```
(`git rm claude/universal.md` in Step 3 already staged the deletion — no separate `git add -u` needed.)
Body: five-section format; base `main` — say so; `claude/universal.md` listed as `(deleted)`; `.gitignore` listed as `(modified)`. Operational impact: nothing goes live at merge (pinned clone); universal.md removal is safe (zero imports verified 2026-08-16, and `install.sh`'s legacy migration remains); the in-flight plan's executors must follow the amended Global Constraints. **STOP: wait for user approval on both PRs.**

---

## After both PRs merge (post-merge routine, per AGENTS.md on main)

For each PR: confirm `main` contains the change (grep, from the **worktree** — `git -C ~/Github/dcltdw-exec fetch && git -C ~/Github/dcltdw-exec log origin/main --oneline -5`; do NOT pull the primary clone), delete the merged branch local+remote (verify with `git ls-remote --heads origin`), and note what went stale: the in-flight plan's ledger already carries the hold notice from Task 0 Step 5 pointing resumers at the amended regime.

## Self-review notes (done at plan time)

- **Spec coverage:** Item A → Task 1; Item B → Task 2 Steps 2–3; hold-back/cutover → Task 0 + Task 2 Steps 5, 6, 8, 9; sequencing (post-#16, pre-plan-PR-2, either merge order) → Task 0 Step 1 + Task 2 Step 1. AGENTS.md line-drift fix (post-review) → Task 2 Step 7; `.gitignore` scratch fix (post-review) → Task 2 Step 4. Decision provenance (rule strength, universal.md, 0.2.0) lives in the spec.
- **Pin integrity:** the only primary-clone operations are Task 0 Step 2 (the one pull) and Step 5 (append to untracked scratch). Everything else is worktree-only. Post-merge routine explicitly avoids pulling the primary clone.
- **No placeholders:** all inserted texts are verbatim in this plan; the two `<body>` references are composed by the executor from the constraints given (content requirements enumerated in each step).
- **Consistency:** branch names `agents-concurrent-rule` / `delivery-paths-docs` used identically in Tasks 0–2; deferral count (4) matches the enumerated steps (Tasks 4, 5, 7, 8).
