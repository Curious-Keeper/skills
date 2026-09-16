---
name: code-review
description: 'Review the changes since a fixed point (commit, branch, tag, or merge-base) along three axes: Standards (does the code follow this repo''s documented coding standards?), Spec (does the code match what the originating issue/spec asked for?) and Invariants (did it break something this repo has already been burned by?). Runs each axis in its own parallel sub-agent and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".'
---

Three-axis review of the diff between `HEAD` and a fixed point the user supplies:

- **Standards**: does the code conform to this repo's documented coding standards?
- **Spec**: does the code faithfully implement the originating issue / spec?
- **Invariants**: did it break something this repo has already been burned by? Runs only where the repo documents invariants. In an `APP_MAP.json`, that is the `invariants` section, whose bar is that each entry has already caused a real bug here.

The axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings.

In a repo with a `docs/app-maps/APP_MAP.json`, the map is the spec source: an item id in a commit message (`S#2`, `L#3`, `dec-4`) resolves to an entry in `openDebt`, `plannedWork.backlog` or `decisionsSettled`, and that entry is what the diff is judged against.

## Process

### 1. Pin the fixed point

Whatever the user said is the fixed point (a commit SHA, branch name, tag, `main`, `HEAD~5`, etc.). If they didn't specify one, ask for it.

Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base). Also note the list of commits via `git log <fixed-point>..HEAD --oneline`.

Before going further, confirm the fixed point resolves (`git rev-parse <fixed-point>`) and the diff is non-empty. A bad ref or empty diff should fail here, not inside two parallel sub-agents.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. A map item id in the commit messages, resolved in `docs/app-maps/APP_MAP.json`. Take the whole entry. For `openDebt` that is `summary`, `evidence`, `mechanism` and `fix`, and `fix` states the shape the change was meant to take.
2. `QUEUE.json`, if the work was dispatched: it carries the item's file set and its `mapNote`.
3. A path the user passed as an argument.
4. A spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
5. If nothing is found, ask the user where the spec is. If they say there isn't one, the **Spec** sub-agent will skip and report "no spec available".

### 3. Identify the standards sources

Anything in the repo that documents how code should be written. `CLAUDE.md` and `AGENTS.md` come first, since the project's file and the user's global one both carry standards and the global one is not in the repo. Then `CODING_STANDARDS.md`, `CONTRIBUTING.md`, and any formatter config the repo commits.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below: a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation. Like any standard here, skip anything tooling already enforces.

Each smell reads _what it is_ → _how to fix_; match it against the diff:

- **Mysterious Name**: a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code**: the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy**: a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps**: the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession**: a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches**: the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change**: one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

### 4. Spawn the sub-agents in parallel

**Standards sub-agent prompt** should include:

- The full diff command and commit list.
- The list of standards-source files you found in step 3, **plus the smell baseline from step 3** pasted in full (the sub-agent has no other access to it).
- The brief: "Report, per file/hunk where relevant, (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls: documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Under 400 words."

**Spec sub-agent prompt** should include:

- The diff command and commit list.
- The path or fetched contents of the spec.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong; (d) **stale evidence**. Where the spec cites `file:line`, check the citation still says what it claims, and report it as a finding against the spec rather than against the diff. Quote the spec line for each finding. Under 400 words."

**Invariants sub-agent prompt** should include:

- The diff command and commit list.
- The repo's documented invariants, pasted in full.
- The brief: "For each invariant, say whether you checked it and what you found. Default to reject: say an invariant holds only where you positively confirmed it in the diff, and say plainly which ones the diff gave you no way to check. An invariant with deliberate exclusions is not violated by the excluded case. Under 400 words."

If the spec is missing, skip the Spec sub-agent and note this in the final report. If the repo documents no invariants, skip that sub-agent and say so. An invented invariant list is worse than none.

### 5. Aggregate

Present each report under its own `## Standards`, `## Spec` and `## Invariants` heading, verbatim or lightly cleaned. Do **not** merge or rerank findings, because the axes are deliberately separate (see _Why the axes stay separate_).

End with a one-line summary: total findings per axis, and the worst issue _within each axis_ (if any). Don't pick a single winner across axes: that's the reranking the separation exists to prevent. An axis that did not run reports as **not judged**, which is not the same as passing.

## Why the axes stay separate

A change can pass one axis and fail another:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**
- Code that does exactly what the issue asked, to standard, and references a column dropped four months ago → **Standards pass, Spec pass, Invariants fail.**

Reporting them separately stops one axis from masking another. It is also why a sub-agent that did not return is reported as **not judged** rather than folded into the others: nobody judged that axis, which is not the same as nobody finding anything.
