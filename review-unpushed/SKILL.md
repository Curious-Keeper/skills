---
name: review-unpushed
description: "Run the interrogate reviewer roster against the commits that have not reached the remote yet. Use when the user wants unpushed or pre-push work cross-examined, wants a last look before pushing, opening a PR, or letting CI run."
disable-model-invocation: true
---

# Review unpushed

`interrogate` scoped to one changeset: the commits that exist locally and
nowhere else. This is the last point at which a finding costs nothing — before
the push, before CI, before a reviewer's time.

Everything except scope is [`interrogate`](../interrogate/SKILL.md). Read its
steps 2 through 5 and follow them unchanged: the intent paragraph, the
concurrent roster spawn, the synthesis, the lead judgment, the output format.
Build reviewer prompts from its four reference files, pasted into each prompt
rather than cited by path:

- [`reviewer-prompt.md`](../interrogate/references/reviewer-prompt.md)
- [`rubric.md`](../interrogate/references/rubric.md)
- [`code-quality-review.md`](../interrogate/references/code-quality-review.md)
- [`lead-judgment.md`](../interrogate/references/lead-judgment.md)

The roster resolves the same way too: `interrogate.reviewers` in the project's
`.claude/harness.config.json`, falling back to `models.roles.reviewer` — and
reaching a non-Claude reviewer goes through the harness, since the `Agent` tool
spawns Claude models only. Follow interrogate's **How to reach each one** and
**When a reviewer cannot be reached** verbatim: ask
`node .claude/harness-core/models.mjs status --json` for each reviewer's `via`
and `argv`, spawn what resolves, and report what does not rather than filling
the roster with another tier of a vendor you already have.

A pre-push review is where that honesty matters most. "Three reviewers found
nothing" is a reason to push; it should never be able to mean "one vendor in
three costumes found nothing".

The deliverable is a verdict. **Do not auto-apply changes, and do not push.**

## 1. Resolve the base

The base is the commit the unpushed work sits on top of. Take the first of
these that resolves:

1. A `--base <rev>` the user passed.
2. The branch's own tracking ref:
   `git rev-parse --abbrev-ref --symbolic-full-name @{u}`. Where one is set,
   this is the real answer — it names the commit the remote actually has for
   this branch.
3. `<remote>/<mainBranch>` from the harness config, defaulting to `origin` and
   `main`.

"Upstream" here means the branch's tracking ref (`branch.<name>.remote` and
`.merge`), not whether the repo has a remote. A branch that has never been
pushed has no tracking ref even in a repo with a perfectly good `origin`, so
rung 3 is the ordinary case on fresh sprint branches, not a degraded path.
When it fires, every commit on the branch is unpushed, which is exactly the
set to review. Report it as "no tracking ref for <branch>", never as "no
upstream" on its own — the short phrase reads as "no remote" and is wrong.

Rungs 2 and 3 both name a remote-tracking ref, which is only as fresh as the
last fetch. A stale one silently pads the range with commits the remote already
has. Check it without mutating anything:

```sh
git rev-parse <base>
git ls-remote origin refs/heads/<branch-the-base-names>
```

Where they disagree, say so and let the user fetch. Do not run `git fetch`
yourself — this skill reviews, it does not move refs.

Say which rung you landed on when you report. A review against `origin/main`
on a branch that tracks `origin/feat/x` is reviewing work that is
already pushed, and the user needs to see that before reading the findings.

Where the base does not resolve at all — no such ref, a remote never fetched,
a detached HEAD — stop and say so. Do not fall back to reviewing everything.

## 2. Gather the range

```sh
git log  <base>..HEAD  --oneline          # the commits
git diff <base>...HEAD --stat             # the shape
git diff <base>...HEAD                    # the changeset under review
```

Two dots for the log, three for the diff. Three-dot diffs against the
merge-base, so commits that landed on the base after this branch started are
not read as this branch deleting them. Two-dot would hand the reviewers a
changeset the author never wrote, and every model would find the same phantom
findings.

**Refuse an empty range.** No commits between the base and `HEAD` means there
is nothing unpushed. Say that and stop. Spawning the roster against an empty
diff spends three models to learn what `git log` already said.

Where the diff is large, give reviewers the full diff anyway — a partial diff
produces findings about code that the missing hunk already handles. Where it
is genuinely too large for one prompt, say so and ask the user whether to
split by commit or by path, rather than silently truncating.

## 3. Report what is out of scope

This skill reviews **committed work only.** The working tree and the index are
not in the diff, on purpose: uncommitted code is still being written, and a
reviewer cannot tell a half-finished edit from a defect.

That exclusion is invisible to the user unless you state it. Check it:

```sh
git status --short
```

Where anything comes back, list those paths in the output under a
**Not reviewed** heading, before the findings. A file that appears in both the
diff and `git status` is the case that actually misleads — the reviewers read
one version of it and the user is looking at another.

## 4. State the intent

Interrogate's step 2, with better ground to stand on: the commit messages in
the range are the author's own statement of what this work is for. Read them,
read the diff, and write the one-paragraph intent from both.

Where the commits say only what changed and never why — a range of `fix:`
subjects with no body — the intent is genuinely missing. Ask the user rather
than inventing one. Reviewers are told to assume the intent is correct and
challenge only the execution, so a wrong intent paragraph wastes the whole run.

## 5. Run interrogate

Spawn the roster, synthesize, and deliver the lead judgment exactly as
`interrogate` specifies. Add one line above its **Intent** section:

```
Base: <rev> (<upstream | --base | project.mainBranch>)
Commits: <n>   Files: <n>
```

Then, after the **Agreement map**, close with a push recommendation. This is
the one thing interrogate does not have to answer and this skill does:

- **Push.** Nothing in `Act on` blocks it.
- **Fix first.** Name the `Act on` findings that should not reach the remote.

A finding in `Consider` or below never blocks a push by itself. Say which it
is and let the user decide.
