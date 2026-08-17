# Claude Work Migration to `dcltdw/agents` — Design

**Date:** 2026-08-16
**Status:** Approved in-chat (Fable brainstorming session, 2026-08-16); this document is the spec of record for the follow-on plan.
**Relationship to in-flight work:** Strictly sequenced *after* the skills initiative (`docs/superpowers/plans/2026-08-15-pr-skills-plugin.md`, as amended) completes its cutover (Task 11). Changes none of that initiative's deliverables. Planning artifacts (this spec, the plan, tickets, board) may be created before cutover because they are GitHub-side or docs-only and inert machine-wide under the hold-back regime.

## Trigger and root question (context)

On 2026-08-16, after a PR-spam wave (account `emre155`, since blocked at account level), dcltdw set GitHub interaction limits (`collaborators_only`, expiring 2027-02-16) on all 8 public repos. The limits lapse silently; the instinct was "put a reminder in `dcltdw/dcltdw`." Brainstorming concluded the root problem is the repo itself: it is simultaneously the public profile README (job-search surface), a Claude Code plugin marketplace, the plugin, and the canonical cross-project AGENTS.md — four jobs, three release cadences, and one of them machine-load-bearing (the `~/.claude/dcltdw` symlink serves its checkout). Demonstrated hazard, same day: an agent asked to read docs ran `git pull` in the pinned primary clone and briefly made held-back rules live machine-wide (restored within minutes).

## Decisions (provenance)

All decided by dcltdw on 2026-08-16, in-chat:

1. **Split the repo.** `dcltdw/dcltdw` keeps only the profile README. The marketplace, plugin, install tooling, and superpowers docs move to a new repo.
2. **New repo: `dcltdw/agents`, public**, linked from the profile README as portfolio material. (Name availability verified 2026-08-16: 404 on `gh api repos/dcltdw/agents`.) Plugin, marketplace, and symlink names all remain `dcltdw` — no consumer-visible rename.
3. **History preserved.** Moved paths keep their commit history (filtered copy), because the incident-driven evolution of AGENTS.md is part of the repo's value.
4. **Gate: migration executes only after the skills initiative's cutover.** Another agent is executing that initiative from `~/Github/dcltdw-exec` (PR 4, `pre-push-secrets-hook`, in progress as of this writing); the primary clone `~/Github/dcltdw` stays pinned at `6abed3a` until its Task 11 runs.
5. **Tracking: GitHub issues in `dcltdw/dcltdw` plus a new user-level Project v2 board** with statuses Todo / In Progress / Done / Won't Do; board IDs recorded in repo `CLAUDE.md` per ADOPTING.md's convention.
6. **Interaction-limits lapse: recurring calendar reminder, no repo automation.** Alert-to-decide, not auto-renew — the limit decision is worth re-making (it also blocks legitimate strangers, e.g. bunnyforge bug reporters from PyPI). Event text in the appendix; this is a user action outside any repo, ticketed for tracking only.

## Verified facts the design rests on

- **No permanent repo interaction limit exists.** `PUT /repos/{owner}/{repo}/interaction-limits` with `expiry` omitted defaults to **`one_day`** (GitHub REST docs, checked 2026-08-16) — not permanent, contrary to the initial prompt's premise. `six_months` is the ceiling; the lapse problem is unavoidable, only its handling is a choice.
- **Scheduled workflows in public repos auto-disable after 60 days of repo inactivity** (GitHub Actions docs, checked 2026-08-16) — an Actions-based reminder can itself silently die; this plus PAT-lifetime chaining is why repo automation was rejected.
- **Marketplaces are identified by the `name` field in `marketplace.json`**, not the repo location; installed plugins live in a local cache and survive a marketplace repo move. `claude plugin` has a `renames` migration field if a plugin name ever changes (not needed here). (Claude Code docs, researched 2026-08-16.)
- **`install.sh` is already location-independent:** it derives `REPO_DIR` from its own path, re-points the `~/.claude/dcltdw` symlink, and re-registers the marketplace at the new clone path. ADOPTING.md documents re-running it as the moved-clone recovery. The migration therefore requires **no changes to consumers**: `~/.claude/CLAUDE.md`'s import, per-repo `@~/.claude/dcltdw/garmin-release.md` imports, and the post-cutover `core.hooksPath` (`~/.claude/dcltdw/githooks`) all resolve through the symlink.
- **Two-channel delivery stays correct.** Plugins still cannot ship always-loaded instruction text (no memory/rules field in `plugin.json`; no URL/git `@`-imports). ADOPTING.md's exit criteria for retiring the symlink remain valid and move with it.

## Target architecture

**Moves to `dcltdw/agents`** (with history):

- `claude/` — AGENTS.md, ADOPTING.md, garmin-release.md, `skills/`, `.claude-plugin/plugin.json`, and `githooks/` once PR 4 lands
- `.claude-plugin/marketplace.json`
- `install.sh`
- `docs/` (the superpowers specs and plans, including this one)
- `CLAUDE.md` (the delivery-paths repo instructions)
- `.gitignore` (copied — see below)

**Stays in `dcltdw/dcltdw`:** `README.md`, plus a `.gitignore` — that file is *copied* to `agents` by the filter and also retained by the strip PR, which trims it to what the profile repo still needs (`.DS_Store`; drop `.superpowers/` once the scratch tree is gone). The profile repo's git history retains the moved files' past — accepted; history preservation in `agents` is about the new repo standing alone.

**Unaffected:** `.superpowers/` scratch (untracked, machine-local, belongs to the in-flight execution), the plugin cache, all other repos' imports.

**New content in `agents`:** a README describing the repo (what it is, how to adopt — pointing at `claude/ADOPTING.md`); written as part of the migration, not before.

## Migration mechanics

1. **Create `dcltdw/agents`** (public, empty — no auto-generated files).
2. **Filtered history copy:** in a throwaway clone of `dcltdw/dcltdw` (never the pinned clone or either worktree), run `git filter-repo` keeping exactly the moved paths above; push the result as `agents`' `main`. `git filter-repo` is not stock git — `brew install git-filter-repo` (or accept the alternative of a plain copy at the cost of decision 3).
3. **Strip `dcltdw/dcltdw`:** branch + PR deleting the moved paths and adding the profile-README link to `agents`. This PR is highlighted as the repo's identity change.
4. **Re-point each machine:** clone `agents`, run `./install.sh` from it (re-links `~/.claude/dcltdw`, re-registers the marketplace path; plugin cache already current post-cutover). Verify: symlink target, `claude plugin marketplace list` path, `core.hooksPath` still resolving, a fresh session loading AGENTS.md. Then the old `~/Github/dcltdw` clone is just the profile repo (or is re-cloned slim); the `dcltdw-exec` and `dcltdw-migration` worktrees are removed once their branches are merged and cleanup is done.
5. **New repo hygiene:** optionally apply the current interaction limit to `agents` so it matches the other public repos until the 2027-02 decision (`gh api -X PUT repos/dcltdw/agents/interaction-limits -f limit=collaborators_only -f expiry=six_months`); add `agents` to the calendar event's repo list (already included in the appendix).

**Ordering matters in step 4:** cutover (their initiative) runs `install.sh` from the *old* clone first and sets `core.hooksPath` through the symlink; the migration's re-run from the *new* clone re-points the same symlink, so the hook path stays valid throughout. No window where imports dangle, because `ln -sfn` is atomic.

## Concurrency and gating

- **Precondition for executing tickets 3–5 (below):** the user confirms cutover is complete. Checkable signals: plugin `dcltdw` installed at 0.2.0 (cache dir `~/.claude/plugins/cache/dcltdw/dcltdw/0.2.0/` exists), `git config --global core.hooksPath` → `~/.claude/dcltdw/githooks`, all four skills-initiative PRs on `main`. Do not infer completion from PR merge state alone — cutover is a machine event, not a GitHub event.
- **Until then:** no pulls or checkouts in `~/Github/dcltdw`; no writes in `~/Github/dcltdw-exec` (another agent's workspace); no `install.sh`, no `claude plugin` state changes, no `~/.claude/*` writes. Planning work happens in the dedicated worktree `~/Github/dcltdw-migration` (branch `claude-work-migration`, from `origin/main`; created without touching the pinned checkout, per the repo's established sibling-worktree convention).
- **Docs-only PRs merging to `main` are inert machine-wide** (pinned clone doesn't pull them) and additive for the executing agent (disjoint paths from PR 4's `claude/githooks/**` + `install.sh` changes — *note:* PR 4 touches `install.sh`; the migration moves it but does not modify it, and the move happens post-cutover from a fresh clone of post-PR-4 `main`, so there is no textual conflict, only sequencing).
- Every PR body states its base and that merging does not go live before cutover.

## Tickets and board

GitHub issues in `dcltdw/dcltdw`, one per PR-sized unit, each carrying its gate explicitly:

1. **Migration spec + plan** (this spec, plus the plan file) — docs-only PR from `claude-work-migration`. No gate.
2. **Create the project board; record IDs in repo `CLAUDE.md`** — board creation is GitHub-side; the `CLAUDE.md` edit rides a small PR. No gate. (The `CLAUDE.md` board-IDs section migrates to `agents` with the file; acceptable duplication of motion, small cost.)
3. **Create `dcltdw/agents` and push filtered history; write its README** — blocked on cutover confirmation.
4. **Strip `dcltdw/dcltdw` to profile README + link** — blocked on 3.
5. **Re-point machine(s): clone `agents`, run `install.sh`, verify** — blocked on 3; coordinated with the user like a mini-cutover (it mutates `~/.claude`).
6. **Calendar event for interaction limits** — user action from the appendix text; ticket exists for tracking only, closable the day the event is created.

Board: user-level GitHub Project v2 (v2 boards belong to users/orgs, linked to the repo), named **"Agent tooling"**, statuses Todo / In Progress / Done / Won't Do, so it can keep serving `agents`-repo work after the migration. Issues 1–6 land in Todo; status moves per AGENTS.md (In Progress at PR open, Done at merge, Won't Do with a one-line reason).

## Out of scope

- No changes to skills content, plugin version, AGENTS.md rules, or the two-channel delivery architecture — the housing moves; the machinery doesn't.
- No interaction-limits automation (rejected with reasons above; revisit only if GitHub ships expiry notifications or unbounded limits).
- No changes to the in-flight skills plan; if its executor needs anything from this initiative, the answer is "after cutover."
- Board IDs for other repos' boards; only the new "Agent tooling" board is in scope.

## Appendix: calendar event (paste-ready)

**Title:** GitHub interaction limits — decide before they lapse
**First occurrence:** 2027-02-02 (expiry is 2027-02-16). **Repeat:** every 5 months.
**Body:**

> Interaction limits (`collaborators_only`) were set 2026-08-16 on all public repos after a PR-spam wave (emre155, blocked at account level). They lapse silently on ~2027-02-16; GitHub sends no notification. Max duration is six months; a "permanent" API limit does not exist (omitted `expiry` defaults to `one_day`).
>
> **Decide, don't just renew:** if the spam threat has passed, let them lapse — `collaborators_only` also blocks legitimate strangers (bunnyforge is on PyPI and wants bug reports). Record the decision here.
>
> Check current state:
> `gh api repos/dcltdw/REPO/interaction-limits`
>
> Renew (edit the repo list if public repos have changed):
> `for r in annotated-maps annotated-maps-sp bunnyforge bunnyforge-visibility-preview dcltdw Flightdeck gtfs-demo Understated agents; do gh api -X PUT repos/dcltdw/$r/interaction-limits -f limit=collaborators_only -f expiry=six_months; done`
>
> Private repos are deliberately excluded (access is already invite-only). If renewing, the next lapse is six months out and this event will fire again before it.
