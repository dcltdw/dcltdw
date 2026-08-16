# RED baseline: `dcltdw:opening-a-pr`

Task 3 of `docs/superpowers/plans/2026-08-15-pr-skills-plugin.md`. Per the
TDD-for-skills Iron Law, this document must exist and show real failures
before `claude/skills/opening-a-pr/SKILL.md` is written. It has not been
written; nothing below should be read as a draft of it.

## Purpose and method

Three pressure scenarios were run against a genuinely naive agent to find
out what a Claude Code session does about PR mechanics with **no**
AGENTS.md, no skill, no prior guidance of any kind — the control the skill
will later be measured against.

**Clean-room recipe:** `CLAUDE_CODE_SIMPLE=1` with an empty
`CLAUDE_CONFIG_DIR`, invoked with an API key directly (no user's installed
config, no plugins, no personal instructions). The clean room was
probe-verified before these runs: asked directly, the agent confirmed it
held no PR-related instructions.

**Sandbox:** a throwaway local git repo (`pr-sandbox`) with a bare
`origin.git` remote — not GitHub. `main` holds one commit; `feature-a`
branches off it with one more commit and is pushed; `feature-b` branches
off `feature-a` with one more commit and is pushed. For S1-C, `main` is
additionally advanced by merging `feature-a` in, and `feature-c` is cut
from the *original* (pre-merge) `main` and never pushed — so it is both
stale and unpublished.

**Confound, recorded honestly:** even in this clean room, the agent still
receives Claude Code's ambient git-status context, which names `main` as
the repository's main branch and notes it is "usually" the PR target. That
is environmental scaffolding, not a taught rule, and it is not nothing —
it plausibly lowers the bar for noticing "this PR's base isn't the usual
one" in S1-A and S1-B, and may partly explain why S1-C already reasons
about `main`'s currency without being told to. Grading below treats passes
on the base-branch criteria as real but *not* clean evidence that this
behavior would appear without any environmental hint at all — see the
synthesis section for how that tempers what the skill should assume it can
skip.

Grading criteria are reproduced under each scenario, verbatim from the
plan. Transcript quotes are exact; line numbers refer to the raw files
under `.superpowers/sdd/2026-08-15-pr-skills-plugin/baseline-raw/`.

---

## S1-A: stacked open, under time pressure

**Prompt:** *"You are working in the git repo at `<sandbox>/work`. Branch
`feature-b` is checked out; it was branched off `feature-a`, whose PR
(#41) is still open. I am heading into a meeting in 5 minutes — quickly
draft the PR for `feature-b` (title + body + the base branch you would
set) as text; there is no GitHub here, just show me exactly what you would
open. Keep it fast."*

**(a) Does it flag that the base is `feature-a`, not `main`, and say why
that matters? — PASS.**

The draft leads with it, unprompted, as its own labeled line:

> "**Base branch:** `feature-a` (not `main`)" (line 6)

and gives a rationale later:

> "Why base is `feature-a`: `feature-b` is exactly one commit ahead of
> `feature-a`, which is one commit ahead of `main`. Targeting `main` would
> make the PR show both commits and re-review #41's changes." (line 31)

It also proactively flags the retargeting obligation for later:

> "2. Retarget to `main` when #41 merges, or the merge will look like it's
> reverting/duplicating feature-a." (lines 34–35)

Worth noting precisely: the *stated rationale* for why retargeting matters
is not the rule's actual rationale. The rule's concern is that an
unflagged non-`main` base can leave merged commits stranded off `main`
because GitHub only retargets children when the base branch is deleted at
merge. This transcript's rationale — that skipping the retarget "will look
like it's reverting/duplicating feature-a" — is a different, weaker
concern (about a confusing diff, not about work silently failing to land
on `main`). So: the *behavior* (flag it, say retarget later) is right, but
the *reasoning* for it is not the reasoning that actually matters, and the
transcript never mentions the deleted-base-branch mechanism at all in
either direction (it neither states it correctly nor gets it wrong — it's
simply absent here, unlike S1-B).

**(b) Does the body contain files-changed-with-annotations, work
breakdown, and provenance? — FAIL, on all three.**

The full body produced (lines 14–27):

```markdown
## Summary
<!-- TODO: what feature-b actually does -->

Stacked on #41. Adds `b` to `app.txt` (1 line, 1 file).

## Stacked PR
- Base: `feature-a` (#41), still open
- **This PR must be retargeted to `main` once #41 merges**
- Review only the top commit (68da26d); e8237a8 belongs to #41

## Test plan
<!-- TODO -->
```

There is no "Files changed" section at all — the closest thing is one
prose sentence buried in Summary ("Adds `b` to `app.txt` (1 line, 1
file)"), with no per-file `(new)`/`(deleted)`/`(modified)` annotation.
There is no "Work breakdown" heading or content — the Summary is a TODO
placeholder. There is no Provenance section anywhere — no `Agent:` line,
no `Model / version:` line; the tool/model that produced the draft is
never named in the artifact itself. Three sections invented instead
(Summary, Stacked PR, Test plan) partially overlap what's wanted but match
none of the five required sections by name or structure.

---

## S1-B: status report

**Prompt:** *"In this repo: PR #41 is feature-a into main, open. PR #42 is
feature-b into feature-a, open. Give me a one-paragraph status summary of
our open PRs for the team channel."*

**Grade: does the summary flag #42's non-`main` base unprompted? — PASS,
but with a serious accompanying misconception.**

The channel draft does flag it, unprompted, inline in the paragraph
(line 3):

> "Because #42 targets `feature-a` rather than `main`, it's blocked on #41
> landing first — so review priority should go to **#41**, and once it
> merges, #42 will need its base retargeted to `main` (**GitHub usually
> does this automatically**) before it can go in."

**This parenthetical is false, stated with confidence, and directly
contradicts the rule this skill exists to teach.** The actual mechanism
(per the rule under test): GitHub retargets a child PR's base *only* when
the base branch is deleted at merge — not "usually," not as a general
default. If the base branch (`feature-a` here) is merged but *not*
deleted, nothing retargets automatically, and #42 would sit targeting a
now-merged-and-possibly-still-alive `feature-a` indefinitely unless a
human intervenes. This is exactly the failure mode named in the rule's
own rationale — "two stacked PRs merged into leftover feature branches"
— and it is precisely the belief that would let a reader stop paying
attention once they see this line, on the assumption GitHub will
"usually" handle it. This is the single most consequential quote in the
whole baseline: a plausible-sounding, hedge-worded, confidently offered
claim that is simply wrong, sitting right next to the one place a naive
reader would look for reassurance.

The transcript separately, and correctly, caveats its own epistemic
limits — it flags that it could not run `gh` and reconstructed everything
from local git state (lines 6–9), and explicitly says it's inferring
review priority rather than reporting fact. That honesty is good practice
and orthogonal to the PR-lifecycle rule; it does not extend to the
GitHub-retargeting claim, which is stated flatly with no such hedge beyond
the single word "usually."

---

## S1-C: stale main

**Prompt:** *"You are on branch feature-c, which you cut a few days ago.
The work is done. Walk me through exactly what you would run to get this
PR opened right now, command by command."* (Sandbox: `main` had advanced
two commits past the point `feature-c` was cut from; `feature-c` was never
pushed.)

**Grade: does it fetch/pull to get current `main` first, and check the
work isn't already merged, before opening? — PASS, and the strongest
result of the three scenarios.**

Recon correctly identifies the staleness before proposing any action:

> "The branch is stale. Merge-base with `main` is `f5c3797` (init). `main`
> has since moved to `9388b60` (merge of feature-a)." (lines 6–7)

The ordered command list puts refresh and rebase strictly before any
publish or open step:

> "1. Refresh; confirm main hasn't moved since my last look — `git fetch
> origin --prune`" ... "2. Rebase onto current main. Safe to rewrite:
> branch was never pushed. Gets CI running against real main and surfaces
> conflicts now, not in review — `git rebase origin/main`" ... "3.
> Re-verify the diff is still just c.txt after the rebase — `git diff
> origin/main...feature-c --stat`" ... "4. Publish the branch and set
> tracking — `git push -u origin feature-c`" (lines 26–37)

This is not the literal `git checkout main && git pull` sequence named in
the rule, but it is functionally equivalent and arguably tighter: fetch
plus rebase onto `origin/main` achieves "branch off current main" without
an unnecessary branch switch, and step 3 (re-diffing against the rebased
main) is a genuine check that the branch's content is not already
subsumed by main, not just a staleness check. It also correctly refuses to
skip straight to opening: it identifies that `origin` is a local bare repo
rather than GitHub, so `gh pr create` cannot work as configured, and it
stops to ask which of three real-world setups this maps to rather than
guessing (lines 50–58). That caution is a good sign but is a
sandbox-detection behavior, not itself evidence about the fetch/pull rule
— the ordering evidence for the grading criterion is the numbered command
list above, and that ordering is correct on its own.

One caveat on how clean this pass is: as noted in Methods, this scenario's
prompt gives the model no explicit signal to reconsider `main`'s currency
— it gets there by general diligence, possibly reinforced by the ambient
"main is usually your PR target" context rather than by any rule specific
to staleness-checking. Treat this as a real pass, not a fully
confound-free one.

---

## Synthesis

### What the skill must teach, ranked by how badly the baseline failed

1. **The five-section PR body format, in full.** This is the clearest and
   most complete failure (S1-A criterion b): zero of the five required
   sections appeared under their required names, files-changed had no
   `(new)`/`(deleted)`/`(modified)` annotations, and Provenance was absent
   entirely — not even attempted. Under time pressure the naive agent
   reaches for an ad hoc, plausible-looking structure (Summary / Stacked
   PR / Test plan) instead. The skill needs to make the five sections and
   their names unmissable, and needs to make Provenance non-optional even
   when nothing else is prompting for it — it is exactly the kind of
   section a "quick draft" drops first.

2. **The actual GitHub stacked-PR retargeting mechanism, correctly
   stated.** S1-B produced a confidently wrong claim ("GitHub usually does
   this automatically") that undermines the entire point of flagging a
   non-`main` base — if the reader believes GitHub handles it, flagging it
   is a formality, not a warning. This is arguably the highest-value
   single fix available: it's not that the model fails to flag stacked
   PRs (it doesn't fail at that), it's that the flag is followed by
   reassurance that happens to be false. The skill must state the
   deleted-base-branch condition explicitly enough that an agent
   reproducing this pattern would either get it right or, at minimum, not
   assert it's automatic.

3. **Tie the "why" to the real failure mode, not a plausible-sounding
   substitute.** S1-A flags the retarget need but justifies it with a
   different, weaker concern (confusing diff / apparent duplication)
   rather than the actual risk (silently stranded merged work). Rows in
   the skill's rationalization table should preempt this — an agent that
   already knows to flag stacked bases but attributes the wrong reason to
   it is a subtler failure than not flagging at all, and won't be caught
   by a grading pass/fail on flagging alone.

### What the skill need not belabour

- **Flagging that a PR's base isn't `main`, unprompted, when the fact is
  already visible in context.** Both S1-A and S1-B did this without being
  asked. The skill should still state the rule (S1-B shows a flag alone is
  not suffient protection — see above), but heavy remedial "notice the
  base branch" drilling is not where the marginal value is; the model
  already looks.
- **Sequencing fetch/rebase-onto-current-main before attempting to open,
  and sanity-checking that the branch's diff survives that rebase.** S1-C
  passed cleanly and with good independent judgment (it also correctly
  refused to fabricate a `gh pr create` against a non-GitHub remote rather
  than guess). This is the one criterion where the control already does
  what the rule asks; per writing-skills, over-investing further teaching
  effort here is likely to make the skill worse, not better — a line or
  two reaffirming the sequence is enough.
- Caveat on both of the above: the clean-room ambient context that names
  `main` as the usual PR target is a plausible partial explanation for why
  base-branch awareness is already this strong. The skill shouldn't assume
  this control result transfers to an environment without that ambient
  hint (e.g., a differently configured harness) — but within the harness
  these scenarios actually ran in, it is not something the skill needs to
  re-teach from scratch.

---

## GREEN / REFACTOR (Task 4)

Method: same clean room (`CLAUDE_CODE_SIMPLE=1`, scratch
`CLAUDE_CONFIG_DIR`), same sandbox, same three prompts verbatim. Each
prompt was prefixed with the full `claude/skills/opening-a-pr/SKILL.md`
body (everything after the frontmatter) plus the pointer line
`Opening, presenting, or reporting on a PR → use the dcltdw:opening-a-pr
skill.`, simulating a session where the pointer fired and the skill
loaded. Transcripts: `.superpowers/sdd/2026-08-15-pr-skills-plugin/green-raw/S1-{A,B,C}.txt`.

**Sandbox-state confound, recorded honestly:** by the time GREEN ran, the
sandbox had already been carried forward through Task 3 Step 4's S1-C
setup (`main` merged `feature-a` in via a true `--no-ff` merge; `feature-c`
cut from the pre-merge root). At baseline time, S1-A/S1-B ran *before* that
merge existed, so `feature-a`'s commit was not yet an ancestor of `main`
and the "correct" base for `feature-b` was genuinely `feature-a`. At GREEN
time it is genuinely `main` — the ground truth for the base-branch
criterion shifted under the scenario, independent of the skill. This is
noted per-scenario below rather than treated as a skill failure or a skill
success; the body-format and mechanism criteria are unaffected and graded
normally.

### Round 1

**S1-A (stacked open, time pressure).**
- (a) base-branch flag + reasoning: sandbox ground truth had shifted (see
  confound above) — `feature-a` is now a true ancestor of `main`, so `main`
  is the actually-correct base. The transcript detects this from the real
  git graph, states it, and *also* correctly reasons about the mechanism
  the skill teaches: it distinguishes the true-merge case (safe, no
  duplication) from a hypothetical squash-merge of #41 (would duplicate
  `feature-a`'s commit and require `git rebase --onto main e8237a8
  feature-b`) — unprompted. Graded PASS on mechanism-correctness; not
  comparable to baseline's pass/fail on "is the base `feature-a`" because
  the premise changed.
- (b) PR body five sections: **PASS on all three of the checked criteria.**
  `## Files changed` present with `(modified)` annotation on `app.txt`;
  `## Work breakdown` present with substantive content (not a TODO);
  `## Provenance` present (`Agent: Claude Code (Claude Agent SDK)` /
  `Model / version: Claude Sonnet 4.5`). Test expectations and Operational
  impact correctly omitted with a stated reason ("no failures expected...
  no deploy/migration steps"), matching the skill's "omit if none" rule.
  This is a full reversal of the baseline failure (zero of five sections,
  no Provenance at all, ad hoc headings instead).
- No new rationalization observed.

**S1-B (status report).**
- Flags #42's non-`main` base unprompted: **PASS, and the baseline's
  central defect is gone.** The transcript states the retarget-vs-rebase
  mechanism correctly and explicitly: "stacked children are where work
  gets stranded, duplicated, or turned into conflicts, because retargeting
  only moves what the PR diffs against, it does not rebase the child's
  commits." It correctly identifies that *this instance* is safe only
  because `feature-a` landed via a true merge, not a squash, and
  proactively warns against over-generalizing: "Don't let this instance
  become the team's mental model for stacked PRs... if a future parent in
  a stack is squash-merged, GitHub will still auto-retarget the child —
  and that retargeted diff will replay the parent's already-merged lines
  as new additions." No trace of the baseline's false "GitHub usually does
  this automatically" claim.
- No new rationalization observed.

**S1-C (stale main).**
- Fetches/pulls current `main` and confirms the work isn't already merged
  *before* proposing any publish/open step: **PASS**, same as baseline,
  now with explicit verification (`git cat-file -p main:c.txt` to confirm
  `c.txt` isn't already on `main`) and a correct, on-topic distinction
  between plain `git rebase origin/main` (this case — single-commit branch
  off root, no parent history to excise) and `git rebase --onto` (the
  stacked-child case) — showing the skill's stacked-PR guidance
  generalized correctly to a case that explicitly *isn't* stacked, rather
  than being over-applied.
- PR body: **PASS on all three of the checked criteria** — Files changed
  `(new)` on `c.txt`, Work breakdown, Provenance all present; Test
  expectations/Operational impact correctly omitted with reasons given.
- Board card: correctly notes no board is attached to this bare-remote
  sandbox rather than fabricating a move — reasonable handling of an
  out-of-scope instruction, not a criterion failure.
- No new rationalization observed.

### Verdict

All three scenarios pass every checked grading criterion in round 1; no
new rationalization appeared in any transcript. Per the plan (stop once
clean), no further rounds were run and no SKILL.md changes were made after
this round. The highest-priority target — S1-B's false "GitHub usually
does this automatically" belief — is confirmed gone and replaced with the
corrected retarget-vs-rebase mechanism, applied correctly (including
knowing when *not* to apply it, per S1-A's true-merge case and S1-C's
non-stacked case). The PR-body five-section failure (the baseline's
largest defect) is fully reversed in all three transcripts.
