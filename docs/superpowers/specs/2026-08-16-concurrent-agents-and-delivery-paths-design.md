# Concurrent-Agent Isolation & Delivery-Path Architecture — Design

**Date:** 2026-08-16
**Status:** Approved in-chat (Fable brainstorming session, 2026-08-16); this document is the spec of record for the follow-on plan.
**Relationship to in-flight work:** Amends the sequencing and execution regime of `docs/superpowers/plans/2026-08-15-pr-skills-plugin.md` (PR #16 open; PRs 2–4 pending). Does not change that plan's deliverables.

## Decisions (provenance)

All decided by dcltdw on 2026-08-16, in-chat:

1. **Isolation rule strength:** isolate by default — feature work in a worktree unless the task must mutate machine-global state anchored to the primary clone's path (a named, checkable exception). Not judgment-based; not exceptionless.
2. **`universal.md` back-compat symlink:** retire in this initiative. Verified: zero imports remain on this machine (all repos use `@~/.claude/dcltdw/AGENTS.md`; the per-repo files are in git, so other machines' clones match). `install.sh`'s legacy-import migration stays as the safety net.
3. **Hold-back execution with a single cutover:** work on this and the in-flight initiative must not reach other running agents (e.g. bunnyforge) until a user-chosen moment, when other agents pause and the infrastructure updates under them.
4. *(Prior, 2026-08-16:)* plugin version lands at **0.2.0** when the whole skills initiative completes — the bump rides PR 4 and therefore goes live at cutover.

## Item A — "Concurrent agents" section in AGENTS.md

New always-loaded section in `claude/AGENTS.md`, placed after "Before deferring as 'blocked'" and before "Branches and PRs". Exact text:

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

Settled points:

- **Prose, not a skill.** This is spontaneous discipline that must fire unprompted; a plugin cannot load instruction text into every session (verified 2026-08-16 against Claude Code 2.1.233 docs: no plugin-level CLAUDE.md, no `instructions` field; skill *descriptions* always load, bodies do not).
- The existing Commits bullet ("confirm you're on the intended branch") **stays in place** — it is moment-anchored to "before committing"; the new section references it.
- **No subagent TDD for this prose** (considered, rejected as YAGNI): this repo's rules iterate from real incidents via PR review — that is the mechanism working, not a gap. The superpowers pressure-testing methodology applies to the skills initiative, not to AGENTS.md prose.

## Item B — delivery paths: document, retire, define the exit

**Verdict (verified, not assumed):** plugin-only delivery is not currently achievable; the `~/.claude/dcltdw` symlink is load-bearing for three capabilities:

1. **Always-loaded instruction text** — AGENTS.md's machine-global import is the trigger layer the entire skills plan depends on. Plugins expose skill descriptions always, bodies on demand; nothing always-loads. *(Verified via doc-cited research, Claude Code 2.1.233, 2026-08-16.)*
2. **Per-repo opt-in imports** — `Understated` and `Flightdeck` actively import `@~/.claude/dcltdw/garmin-release.md`. Plugins are all-or-nothing per scope, with no version-stable import path into the cache. *(Verified by grep across all repos on this machine.)*
3. **A stable `core.hooksPath` target** for the PR-4 git pre-push hook. The plugin cache path is version-stamped (`~/.claude/plugins/cache/dcltdw/dcltdw/<version>/`) and version bumps are now mandatory for skill changes, so a cache path would break on every skill release. Plugin `hooks/` are Claude Code lifecycle hooks, not git hooks. *(Cache keying verified live with probe files, 2026-08-16.)*

Design:

- **`claude/ADOPTING.md` gains a "Delivery paths" section** — the authoritative statement that the symlink and the plugin are complementary, not redundant:
  - symlink carries: always-loaded prose (AGENTS.md), per-repo opt-in imports (garmin-release.md), and — from PR 4 — `claude/githooks/**`;
  - plugin cache carries: `claude/skills/**`, gated by `version` bumps.
  - The repo-root `CLAUDE.md` already states the contributor-facing split and points here; it needs no change beyond what PR #16 shipped.
- **Same section records the exit criteria** for revisiting (so the decision is revisited, not re-litigated). Plugin-only becomes possible when Claude Code ships **any** of the missing capabilities, and all three are needed to retire the symlink outright:
  1. plugins can contribute always-loaded instruction text;
  2. per-repo conditional plugin content, or a version-stable import path into an installed plugin;
  3. a version-stable filesystem path suitable as a `core.hooksPath` target (or plugin-managed git hooks).
- **`universal.md` retires:** delete the `claude/universal.md → AGENTS.md` symlink; remove the back-compat note from ADOPTING.md. `install.sh`'s migration of the legacy machine-global import stays.

## Hold-back execution and the cutover (amends the in-flight plan)

**Problem.** Work here is not isolated by default. Three channels reach other agents:

| Channel | Reaches | When |
|---|---|---|
| AGENTS.md via `~/.claude/dcltdw` symlink | every new, cleared, or **compacted** session, machine-wide | the moment the change exists in the primary clone's checkout — including unmerged branch states checked out there, and any `git pull` after a merge |
| Plugin cache | new sessions only | only on explicit `version` bump + `plugin update`; additive, and skills are inert without their AGENTS.md pointers |
| `core.hooksPath` (PR 4) | every `git push` from every repo, **including running sessions** | the moment `install.sh` sets it — git reads config per invocation |

Compaction is the reason "already running" is not protection: a long-lived session that compacts re-reads CLAUDE.md imports and silently picks up whatever is on disk.

**Mechanism.** The symlink serves the primary clone's *checkout*, not GitHub — so "merged upstream" and "live on this machine" can be decoupled:

- **Pin the primary clone** (`~/Github/dcltdw`): checked out at `main`, pulled once after PR #16 merges (post-#16 main is behaviorally inert machine-wide: no AGENTS.md changes, no skills), then **never pulled and no branches checked out in it** until cutover.
- **Execute everything in a persistent worktree** (e.g. `~/Github/dcltdw-exec`): branches, commits, PRs, subagent testing. The in-flight plan's SDD ledger (untracked scratch under `.superpowers/sdd/`) moves into the worktree.
- **Defer every machine mutation to cutover:** no `install.sh` against the real machine, no plugin installs/updates, no `core.hooksPath`. Task 10's install.sh testing runs fully sandboxed via `HOME=<scratch> CLAUDE_CONFIG_DIR=<scratch>` (the script already honors `CLAUDE_CONFIG_DIR`; `git config --global` writes to `$HOME/.gitconfig`, so a scratch HOME isolates both). Task 9's hook tests already use repo-local `core.hooksPath` in scratch repos.
- **TDD cost, accepted:** the in-flight plan's live trigger checks (Tasks 4/7 Step 5, Task 8 Step 2 — fresh session discovers the skill via the real plugin) cannot run pre-cutover, because the marketplace builds from the pinned clone. GREEN-by-injection is unaffected. The trigger checks move to a **post-cutover verification pass** — same checks, run when the infrastructure is actually live.
- **Cutover runbook** (one moment, user-chosen): pause/finish other agents → `git pull` the primary clone → `brew install gitleaks` → `./install.sh` (installs the 0.2.0 plugin, sets `core.hooksPath`) → run the deferred trigger checks → resume agents. Running sessions get new push behavior immediately and new rules at next clear/compaction.

**Resolved contradiction:** under hold-back, the Item A rule itself is not machine-live while PRs 2–4 execute. Its requirements reach those executors anyway, because they are written into the in-flight plan's Global Constraints and carried in every dispatch — the live AGENTS.md route is for everything *else* on the machine, from cutover onward.

## Sequencing and PR shape

Two small single-purpose PRs from this initiative, plus amendments to the in-flight plan:

- **PR A** — the AGENTS.md "Concurrent agents" section (Item A). Branches off post-#16 `main`, executed from the worktree.
- **PR B** — ADOPTING.md "Delivery paths" section + exit criteria + `universal.md` symlink removal (Item B), **plus** the hold-back amendments to `docs/superpowers/plans/2026-08-15-pr-skills-plugin.md`: execution-locus (worktree, pinned primary clone), sandboxed install.sh testing for Task 10, trigger checks re-homed to a new cutover task, and the cutover runbook itself.
- **Order:** PR A and PR B merge after PR #16 and **before plan-PR 2 opens** (so Tasks 5/8 branch from a main that already contains the new AGENTS.md section — no merge conflicts to manage). Both go *live* at cutover, per hold-back.
- Neither PR bumps the plugin `version`: AGENTS.md, ADOPTING.md, and plan files are symlink-delivered or repo-local; nothing here ships through the cache.

## Out of scope

- No changes to the in-flight plan's deliverables (skills content, hook script, install.sh behavior).
- No AGENTS.md edits while PR #16 is unmerged.
- The cutover pattern is initiative-specific process; it is recorded in the plan and ADOPTING.md, not as a universal AGENTS.md rule.
