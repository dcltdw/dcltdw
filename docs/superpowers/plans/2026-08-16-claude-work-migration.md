# Claude Work Migration to `dcltdw/agents` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the marketplace, plugin, install tooling, and superpowers docs out of the profile repo `dcltdw/dcltdw` into a new public repo `dcltdw/agents` (history preserved), strip the profile repo to its README, re-point the machine, and track it all via issues and a new "Agent tooling" board — executing nothing machine-visible before the in-flight skills initiative's cutover.

**Architecture:** Planning artifacts (this plan, issues, board) are GitHub-side or docs-only and safe pre-cutover. The migration itself is a filtered-history bootstrap of `agents` followed by a strict order: re-point the machine *before* merging the strip PR, so the `~/.claude/dcltdw` symlink never dangles. `install.sh` is already location-independent, so no consumer (imports, marketplace name, `core.hooksPath`) changes.

**Tech Stack:** git, git-filter-repo, gh CLI (incl. Projects v2 GraphQL), markdown. No code.

**Spec:** `docs/superpowers/specs/2026-08-16-claude-work-migration-design.md` — the spec of record; conflicts in this plan resolve against it.

## Global Constraints

- **Pre-cutover rules (binding until Task 5 confirms cutover):** the primary clone `~/Github/dcltdw` stays pinned at `6abed3a` — no pulls, no checkouts, no edits there. `~/Github/dcltdw-exec` belongs to another agent — never touch it. No machine mutations: no `install.sh`, no `claude plugin` state changes, no `git config --global`, no writes under `~/.claude/`. All repo work happens in the worktree `~/Github/dcltdw-migration`.
- **Cutover confirmation is a machine event, not a GitHub event.** Only the user's explicit confirmation plus the Task 5 signals unlock Tasks 6–10.
- Never commit to `main` of `dcltdw/dcltdw` (the sole exception, called out in Task 6, is the initial history push to the brand-new empty `agents` repo). Every PR: base `main` (state it in the body), five-section body format (Files changed with `(new)`/`(deleted)`/`(modified)`, Work breakdown, Test expectations, Operational impact, Provenance), stop for user approval before merging.
- Every pre-cutover PR body states: **merging does not make this live machine-wide** — the primary clone is pinned until cutover.
- Every commit carries `Co-Authored-By:` naming the executing model (state which model the transcript asked for; do not claim to observe it).
- **Scan every diff for secrets before pushing.** If `gitleaks` is installed, run `gitleaks protect --staged`; otherwise review the diff by eye (all diffs in this plan are docs/markdown — nothing should ever resemble a credential).
- No plugin `version` changes anywhere in this initiative. Skills, rules content, and delivery architecture are out of scope — the housing moves, the machinery doesn't.
- The `claude` CLI, if needed read-only, is the VS Code extension binary (`~/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude`, newest version); it is not on PATH.

---

### Task 1: Push the branch and open PR 1 (spec + plan)

**Files:**
- No new edits — commits `3bd1882` (spec) and the plan commit already exist on `claude-work-migration` in `~/Github/dcltdw-migration`.

**Interfaces:**
- Produces: PR 1 (docs-only) open against `dcltdw/dcltdw` `main`; its URL is referenced by Task 2's issue bodies.

- [ ] **Step 1: Verify the branch state**

```bash
cd ~/Github/dcltdw-migration
git log --oneline origin/main..HEAD
```
Expected: exactly two commits — the spec commit and the plan commit, nothing else.

- [ ] **Step 2: Secret-scan and push**

```bash
git diff origin/main..HEAD | grep -iE 'token|secret|key|password|ghp_|github_pat' || echo "no secret-shaped strings"
git push -u origin claude-work-migration
```
Expected: "no secret-shaped strings" (the two files are pure markdown), then a clean push.

- [ ] **Step 3: Open PR 1**

```bash
gh pr create --base main \
  --title "Migration spec + plan: Claude work moves to dcltdw/agents" \
  --body-file <body>
```
Compose `<body>` in the five-section format: Files changed (both docs `(new)`); Work breakdown (spec decisions summary: split approved, `agents` public with history, cutover gate, calendar-not-Actions for interaction limits); Test expectations (none — docs only); Operational impact (**merging changes nothing machine-wide**: primary clone pinned until cutover; execution of Tasks 6–10 additionally gated on user confirmation); Provenance (Agent: Claude Code; Model: per transcript). Base is `main` — say so.

**STOP: wait for user approval before merging. Tasks 2–4 may proceed while PR 1 is open (GitHub-side only, disjoint from repo files).**

---

### Task 2: Create the six tracking issues

**Files:** none (GitHub-side).

**Interfaces:**
- Consumes: PR 1's URL (Task 1).
- Produces: issues #A1–#A6 (record actual numbers); Task 3 adds them to the board; Tasks 6–10 update them.

- [ ] **Step 1: Create the issues**

Run six `gh issue create -R dcltdw/dcltdw --title ... --body ...` commands with exactly these titles and bodies (substitute the real PR 1 URL for `PR1‑URL`):

1. **Title:** `Migration: spec + plan` — **Body:** `Docs-only PR from claude-work-migration: the migration spec (docs/superpowers/specs/2026-08-16-claude-work-migration-design.md) and this plan. PR: PR1-URL. No gate.`
2. **Title:** `Create "Agent tooling" project board; record IDs in CLAUDE.md` — **Body:** `User-level Project v2 board, statuses Todo / In Progress / Done / Won't Do, linked to this repo; IDs recorded in CLAUDE.md per ADOPTING.md convention (small PR). No gate. Spec: see #<issue-1>.`
3. **Title:** `Bootstrap dcltdw/agents: filtered history + README + interaction limit` — **Body:** `Create public repo dcltdw/agents; push history filtered to claude/, .claude-plugin/, install.sh, docs/, CLAUDE.md, .gitignore; add README via the repo's first PR; apply collaborators_only interaction limit. **BLOCKED on skills-initiative cutover** (plugin 0.2.0 installed, core.hooksPath set) **and explicit user go-ahead** — creating a public repo is outward-facing.`
4. **Title:** `Strip dcltdw/dcltdw to profile README; link agents` — **Body:** `Delete the migrated paths, trim .gitignore, add the agents link to README. This PR changes the repo's identity — highlighted for review. **BLOCKED on #<issue-3> and #<issue-5>** (machine must re-point before the old paths disappear from checkouts that pull).`
5. **Title:** `Re-point machine: clone agents, run install.sh, verify` — **Body:** `Clone dcltdw/agents to ~/Github/agents; ./install.sh re-links ~/.claude/dcltdw and re-registers the marketplace path; verify symlink, marketplace path, core.hooksPath resolution, fresh-session AGENTS.md load. Mutates ~/.claude — coordinate with the user like a mini-cutover. **BLOCKED on #<issue-3>.**`
6. **Title:** `Create interaction-limits calendar reminder (user action)` — **Body:** `Recurring event, first ~2027-02-02, every 5 months; paste-ready text in the spec's appendix (docs/superpowers/specs/2026-08-16-claude-work-migration-design.md). Not gated. Close when the user confirms the event exists.`

- [ ] **Step 2: Verify**

```bash
gh issue list -R dcltdw/dcltdw --limit 10
```
Expected: all six issues open with the titles above. Record their numbers for Tasks 3–10.

---

### Task 3: Create the "Agent tooling" board and PR 2 (board IDs in CLAUDE.md)

**Files:**
- Modify: `CLAUDE.md` (append a board-IDs section; on a new branch `board-ids`)

**Interfaces:**
- Consumes: issue numbers (Task 2).
- Produces: board number/ID, Status field ID, four option IDs — recorded in `CLAUDE.md` and used by Tasks 6–10 for status moves.

- [ ] **Step 1: Create and link the board**

```bash
gh project create --owner dcltdw --title "Agent tooling" --format json   # record number + id
gh project link <number> --owner dcltdw --repo dcltdw/dcltdw
```

- [ ] **Step 2: Set the four statuses**

```bash
gh project field-list <number> --owner dcltdw --format json   # record the Status field id (PVTSSF_...)
gh api graphql -f query='
mutation {
  updateProjectV2Field(input: {fieldId: "<status-field-id>", singleSelectOptions: [
    {name: "Todo", color: GRAY, description: ""},
    {name: "In Progress", color: YELLOW, description: ""},
    {name: "Done", color: GREEN, description: ""},
    {name: "Won'"'"'t Do", color: RED, description: "Reviewed and deliberately closed without action"}
  ]}) { projectV2Field { ... on ProjectV2SingleSelectField { id options { id name } } } }
}'
```
Expected: four options returned; record each option id. (Safe to replace options now — no items carry a status yet.)

- [ ] **Step 3: Add the six issues, set statuses**

```bash
for u in <issue-1-url> ... <issue-6-url>; do gh project item-add <number> --owner dcltdw --url "$u"; done
```
Then `gh project item-list <number> --owner dcltdw --format json` to get item ids, and `gh project item-edit --id <item-id> --project-id <project-id> --field-id <status-field-id> --single-select-option-id <todo-id>` for each. Issue 1's item goes to **In Progress** (its PR is open); the rest to **Todo**.

- [ ] **Step 4: Branch and record IDs in CLAUDE.md**

```bash
cd ~/Github/dcltdw-migration && git fetch origin && git checkout -b board-ids origin/main
```
(Branching from `origin/main` regardless of PR 1's merge state — disjoint files.) Append to `CLAUDE.md`:

```markdown
## Project board

Work in this repo (and, post-migration, dcltdw/agents) is tracked on the
user-level Project v2 board **"Agent tooling"** (project number <number>,
id `<project-id>`). Status field id `<status-field-id>`; option ids:
Todo `<id>`, In Progress `<id>`, Done `<id>`, Won't Do `<id>`.
Re-derive if they drift:
`gh project field-list <number> --owner dcltdw --format json`
```

- [ ] **Step 5: Commit, push, open PR 2**

```bash
git add CLAUDE.md
git commit -m "docs: record Agent tooling board IDs in CLAUDE.md

Co-Authored-By: <executing model>"
git push -u origin board-ids
gh pr create --base main --title "CLAUDE.md: Agent tooling board IDs" --body-file <body>
```
Five-section body; base `main`; Operational impact: inert machine-wide (pinned clone); the section migrates to `agents` with `CLAUDE.md` later — intended. **STOP: wait for approval. Move issue 2 to In Progress.**

---

### Task 4: Hand the user the calendar event text (issue 6)

**Files:** none.

- [ ] **Step 1:** Present the spec's appendix (title, first occurrence 2027-02-02, 5-month recurrence, full body text) to the user verbatim and ask them to create the event in their calendar of choice. This is not gated on anything — it can happen today.
- [ ] **Step 2:** When the user confirms the event exists, close issue 6 with comment `Event created by user on <date>` and move it to **Done** on the board. If the user declines or defers, leave the issue open in Todo — do not nag; it fires again naturally when they review the board.

---

### Task 5: GATE — cutover confirmation (unlocks Tasks 6–10)

**Files:** none.

- [ ] **Step 1: Ask the user** whether the skills initiative's cutover (Task 11 of `docs/superpowers/plans/2026-08-15-pr-skills-plugin.md`) has run. **Do not proceed on inference.**
- [ ] **Step 2: Verify the machine signals** (read-only):

```bash
ls ~/.claude/plugins/cache/dcltdw/dcltdw/        # expect: a 0.2.0 directory
git config --global --get core.hooksPath          # expect: ~/.claude/dcltdw/githooks (expanded)
git -C ~/Github/dcltdw log --oneline -1           # expect: at or past the four skills-initiative PRs (no longer 6abed3a)
```
All three must hold **and** the user must have said go (creating a public repo in Task 6 is outward-facing). If anything fails: stop, report which signal is missing, and wait. From here on, the pre-cutover Global Constraints (pin, no machine mutations) are lifted — the concurrent-agents AGENTS.md rule is now live and worktree discipline still applies.

---

### Task 6: Bootstrap `dcltdw/agents` with filtered history (issue 3, part 1)

**Files:** none in existing repos (new repo only).

**Interfaces:**
- Produces: `dcltdw/agents` `main` = filtered history of the six paths; consumed by Tasks 7–9.

- [ ] **Step 1: Install git-filter-repo if absent**

```bash
command -v git-filter-repo || brew install git-filter-repo
```

- [ ] **Step 2: Fresh clone and filter** (filter-repo refuses non-fresh clones; never run this against `~/Github/dcltdw` or the worktrees)

```bash
SCRATCH=$(mktemp -d)
git clone https://github.com/dcltdw/dcltdw.git "$SCRATCH/agents"
cd "$SCRATCH/agents"
git rev-list --count HEAD -- claude .claude-plugin install.sh docs CLAUDE.md .gitignore   # record N
git filter-repo --path claude --path .claude-plugin --path install.sh --path docs --path CLAUDE.md --path .gitignore
git log --oneline | wc -l    # expect: N (filter-repo keeps exactly the commits touching kept paths)
ls                            # expect: claude/ install.sh docs/ CLAUDE.md (+ hidden .claude-plugin, .gitignore); NO README.md
```

- [ ] **Step 3: Create the repo and push (the sanctioned direct-to-main push)**

```bash
gh repo create dcltdw/agents --public --description "Rules, skills, and install tooling for dcltdw's AI coding agents (AGENTS.md + Claude Code plugin)"
git remote add origin https://github.com/dcltdw/agents.git   # filter-repo strips remotes
git push -u origin main
```
This pushes reviewed history (every commit already went through a PR in `dcltdw/dcltdw`); it is a repo bootstrap, not new work — the "never commit to main" rule's stated exception.

- [ ] **Step 4: Apply the interaction limit and verify**

```bash
gh api -X PUT repos/dcltdw/agents/interaction-limits -f limit=collaborators_only -f expiry=six_months
gh api repos/dcltdw/agents/interaction-limits --jq '.limit + " until " + .expires_at'
gh repo view dcltdw/agents --json defaultBranchRef --jq .defaultBranchRef.name   # expect: main
```
Expected: `collaborators_only until <timestamp ~6 months out>`. Note: this expiry is ~2027-02-*later* than the others (set today vs. 2026-08-16) — the calendar event covers all repos regardless. Update issue 3 with progress; move it to **In Progress** on the board.

---

### Task 7: `agents` README via its first PR (issue 3, part 2)

**Files:**
- Create: `README.md` in a fresh clone of `dcltdw/agents` (branch `readme`)

- [ ] **Step 1: Clone to the permanent location and branch**

```bash
git clone https://github.com/dcltdw/agents.git ~/Github/agents
cd ~/Github/agents && git checkout -b readme
```

- [ ] **Step 2: Write `README.md`** with exactly this content (adjust the date to the actual bootstrap date):

```markdown
# agents

The rules, skills, and install tooling my AI coding agents work under,
across all of my repos.

- **[claude/AGENTS.md](claude/AGENTS.md)** — canonical cross-project
  collaboration rules (vendor-neutral [AGENTS.md](https://agents.md/)
  format), imported machine-globally into every project.
- **[claude/skills/](claude/skills/)** — PR-lifecycle skills, shipped as
  the `dcltdw` Claude Code plugin (marketplace manifest in
  [.claude-plugin/](.claude-plugin/)).
- **[install.sh](install.sh)** — one-command machine setup. Start at
  **[claude/ADOPTING.md](claude/ADOPTING.md)** for how the two delivery
  paths (live symlink vs. versioned plugin cache) fit together.

Extracted with history from [dcltdw/dcltdw](https://github.com/dcltdw/dcltdw)
on 2026-08-16; that repo is now just my profile README.
```

- [ ] **Step 3: Commit, push, open the PR**

```bash
git add README.md
git commit -m "docs: repo README

Co-Authored-By: <executing model>"
git push -u origin readme
gh pr create --repo dcltdw/agents --base main --title "README" --body-file <body>
```
Five-section body (Files changed: `README.md (new)`; no test expectations; no operational impact). **STOP: wait for approval; merge; run the AGENTS.md post-merge routine** (pull main, confirm content, delete branch local+remote via `git ls-remote --heads origin`).

---

### Task 8: Re-point the machine (issue 5)

**Files:** none in git (machine state: `~/.claude/dcltdw` symlink, marketplace registration).

- [ ] **Step 1: Coordinate.** Confirm with the user that no other agent is mid-flight on this machine (this step re-points the symlink every session's imports resolve through; `ln -sfn` is atomic, but the mini-cutover courtesy applies).
- [ ] **Step 2: Run install.sh from the new clone**

```bash
cd ~/Github/agents && git checkout main && git pull && ./install.sh
```
Expected output lines: `linked /Users/dcltdw/.claude/dcltdw -> /Users/dcltdw/Github/agents/claude`; `global import already present`; marketplace re-pointed/updated; plugin update reporting already-current (no `version` change is involved).

- [ ] **Step 3: Verify all four consumers**

```bash
readlink ~/.claude/dcltdw                                   # expect: /Users/dcltdw/Github/agents/claude
"$(ls -d ~/.vscode/extensions/anthropic.claude-code-* | sort -V | tail -1)/resources/native-binary/claude" plugin marketplace list --json | python3 -c 'import json,sys; [print(m["name"], m["path"]) for m in json.load(sys.stdin)]'
                                                            # expect: dcltdw /Users/dcltdw/Github/agents
git config --global --get core.hooksPath                    # expect: ~/.claude/dcltdw/githooks (unchanged, resolves through new symlink)
ls ~/.claude/dcltdw/githooks/ ~/.claude/dcltdw/AGENTS.md    # expect: hook files + AGENTS.md present via new target
```
- [ ] **Step 4:** Start a fresh Claude session in any repo and confirm the AGENTS.md rules load (ask it to quote a rule heading). Close issue 5 (**Done** on the board) with the verification output.

---

### Task 9: Strip `dcltdw/dcltdw` to the profile README (issue 4)

**Files:**
- Delete: `claude/` (all), `.claude-plugin/marketplace.json`, `install.sh`, `docs/` (all), `CLAUDE.md`
- Modify: `README.md` (add the `agents` link), `.gitignore` (trim to `.DS_Store`)

**Interfaces:**
- Consumes: Task 8 verified (the machine no longer reads this repo's `claude/`).

- [ ] **Step 1: Branch** — post-cutover the pin is lifted; still use the worktree:

```bash
cd ~/Github/dcltdw-migration && git fetch origin && git checkout -b strip-to-profile origin/main
```

- [ ] **Step 2: Delete and trim**

```bash
git rm -r claude .claude-plugin install.sh docs CLAUDE.md
printf '.DS_Store\n' > .gitignore && git add .gitignore
```
(`.superpowers/` scratch, if any remains here, is untracked and unaffected; dropping its ignore line is fine once the strip merges — but if `git status` shows a local `.superpowers/`, keep the `.superpowers/` line in `.gitignore` instead.)

- [ ] **Step 3: Add the README link** — in `README.md`, insert as the **first** bullet under `**Fun stuff I'm developing/maintaining**`:

```markdown
- **[agents](https://github.com/dcltdw/agents)** — the AGENTS.md rules,
  Claude Code skills plugin, and install tooling my AI coding agents work
  under across these repos.
```

- [ ] **Step 4: Verify the end state**

```bash
git ls-files | sort    # expect exactly: .gitignore, README.md
git diff --cached --stat | tail -1
```

- [ ] **Step 5: Commit, push, open PR 3**

```bash
git commit -m "Strip repo to profile README; Claude work now lives in dcltdw/agents

Co-Authored-By: <executing model>"
git push -u origin strip-to-profile
gh pr create --base main --title "Strip to profile README: Claude work moved to dcltdw/agents" --body-file <body>
```
Five-section body; base `main`; every deleted path listed `(deleted)`; Operational impact: **this PR changes the repo's identity** — after merge, machines must never run this repo's (now absent) `install.sh`; the machine was re-pointed in issue 5 *before* this merges. **STOP: wait for approval. Move issue 4 to In Progress.**

---

### Task 10: Post-merge cleanup and staleness sweep

**Files:** none in repos; memory file `~/.claude/projects/-Users-dcltdw/memory/claude-work-moves-to-agents-repo.md`.

- [ ] **Step 1: Per merged PR (1, 2, 3):** run the AGENTS.md post-merge routine — `git checkout main && git pull` (primary clone; the pin is long lifted), grep `main` for the change, delete branches local + remote, verifying against `git ls-remote --heads origin` (not `git branch -a`).
- [ ] **Step 2: Board + issues:** issues 1–5 to **Done** (issue 6 per Task 4's outcome); one-line closing comment each linking the delivering PR/repo.
- [ ] **Step 3: Worktree cleanup:**

```bash
cd ~/Github/dcltdw && git worktree remove ../dcltdw-migration && git worktree prune && git worktree list
```
Expected: `dcltdw-migration` gone. Leave `dcltdw-exec` alone unless the skills initiative's own cleanup already removed it.
- [ ] **Step 4: Staleness sweep** — check and report: the profile repo's git history still shows old `claude/` paths (fine, by design); any docs elsewhere referencing `github.com/dcltdw/dcltdw` as the rules' home (grep the other repos' CLAUDE.md files for `dcltdw/dcltdw`); `~/Github/dcltdw` is now a README-only checkout (optionally re-clone slim — user's call).
- [ ] **Step 5: Update memory** — edit the memory file `claude-work-moves-to-agents-repo.md`: status from "approved, gated" to "completed <date>"; keep the interaction-limits calendar facts (still live until 2027-02). Update its `MEMORY.md` index line to say the migration is done and `agents` is the home of the Claude work.

---

## Self-review notes (done at plan time)

- **Spec coverage:** Decisions 1–3 → Tasks 6–9; decision 4 (gate) → Task 5 + Global Constraints; decision 5 (tickets/board) → Tasks 2–3; decision 6 (calendar) → Task 4. Migration mechanics steps 1–5 → Tasks 6, 9, 8, 6-Step-4 respectively; ordering fix (re-point before strip) encoded as issue 4 blocked on issue 5 and Task 8 < Task 9. Verified facts → Global Constraints + Task 6/8 checks.
- **No placeholders:** every `<...>` token is data captured by an earlier step in the same or a prior task (issue numbers, board/field/option ids, PR URLs, executing model), never undecided content. README and issue texts are verbatim.
- **Consistency:** branch names `claude-work-migration` / `board-ids` / `readme` / `strip-to-profile`; paths `~/Github/dcltdw-migration`, `~/Github/agents`; board "Agent tooling"; kept-path list identical in Task 6 Step 2 and Task 9 Step 2 (six paths).
