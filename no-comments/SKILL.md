---
name: no-comments
description: "Delete the comments in scope, fix the code they were covering for, and offer to encode any constraint they claimed."
disable-model-invocation: true
---

# No comments

Spawn Comment Sicko. Act on accepted findings.

Defer to Comment Sicko's fresh perspective.

## Scope

Use the caller's files or diff. Otherwise use the current diff against the base branch, default `main`, including the working tree.

## Steps

### 1. Spawn the sub-agent

Spawn one sub-agent with the brief in [`COMMENT-SICKO.md`](COMMENT-SICKO.md), pasted whole. Pass the scope. Do not restate its rules and do not add your own.

### 2. Audit the report and diff

Reject any of these:

- edits to application code
- deletions outside the scope
- deletions of exception-protected comments
- misstated `MUST KILL` reasons
- flags that treat kept intentional code as guilty

Reshape flags on our-code surprises stay actionable, and their comments stay deleted. A keep survives only with proof it is about something we cannot change. Audit the scoped linter and type-checker suppressions it missed. Suppressions that protect correctness or safety stay actionable `MUST KILL`s. Restore a deletion only against an exact exception with scoped proof.

Before accepting a thin `IMPORTANT` or `do not remove` kill or keep, investigate the named symbol yourself: `git log` and `git blame` on the lines, the ADRs and `CONTEXT.md`, and any `APP_MAP.json` `decisionsSettled` or `invariants`. An ambiguous kill stands. A keep that is refuted or still ambiguous gets deleted.

Revert and rerun one rejected report, naming the failure. Reject a second and stop. Report it open and fail the run.

### 3. Sketch a shape where one is needed

Fix trivial accepted flags directly by deleting a dead path, dropping a parameter, or using the real API. If any fix needs a shape, call the Skill tool for `codebase-design` once for the accepted set and the surrounding code. Stop at the sketch. That skill shapes, step 4 implements.

### 4. Implement the smallest root-cause fix in scope

Remove every named workaround. Fix causes, never symptoms, and never bolt on a symptom guard. If the root cause is out of scope, land the smallest in-scope fix and report the rest open.

Where a fix has to land in a design written without it, call the Skill tool for `redesign-from-first-principles`. It guides intent only. It does not authorize widening the fence or fixing instances outside it.

### 5. Offer to encode the constraints

Constraint comments say `do not remove`, `do not change wording`, or `talk to X before changing`. Leave keeps about things we cannot change. For the rest, offer the cheapest in-scope type, runtime check, test, or CI lint that makes the constraint enforceable, and wait for the user to approve it. A non-interactive run needs that approval from the caller up front.

If approved, encode the constraint and then delete the comment. Otherwise delete the comment, report the constraint open, and sketch the out-of-scope work.

### 6. Report

Report the deletion count, restored comments, reruns, the design sketch, fixes, encoding offers, encodings made, unenforced constraints, and other open work.
