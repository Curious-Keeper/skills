---
name: scope
description: Break a planned item, plan, spec, or the current conversation into dispatchable openDebt entries in the project's APP_MAP.json, each carrying the file:line evidence the queue extractor and the builder both read. Use when work is agreed but not yet buildable, or when a plannedWork.backlog item needs scoping.
disable-model-invocation: true
---

`plannedWork` is defined as *wanted, not yet dispatchable. These need scoping first*. This skill is that step: it takes an item nobody can build yet and produces `openDebt` entries a builder can be handed.

```
navigator / architecture review  -->  plannedWork.backlog  -->  scope  -->  openDebt
                                          (agreed)                        (dispatchable)
                                                                              |
                                                            extract-queue --> QUEUE.json --> builders
```

This is the phase **after** a map exists. Before one does, work is sized for feedback rather than for parallelism. Call the Skill tool for `tracer` instead, which slices vertically and builds serially until there is enough system to map.

The whole job is one transition, and its bar is a single question, taken from `openDebt`'s own `$comment`: **can a builder open the cited file and see the thing?** Where the answer is no, the item is not scoped yet, whatever else you know about it.

Read **`docs/MAP_GUIDE.md`** from the [`sprint-harness`](https://github.com/Curious-Keeper/sprint-harness) kit before writing an entry. Use a local checkout if there is one, otherwise fetch it from the repo. It is the writing standard for all four fields, and this skill does not restate it. Write no entry from memory of it.

## Why this may write facts

`codemod.py` may never write a `mechanism` and `intake.py` may never promote into `openDebt`, both for the same reason: nothing in them has read the repo. This skill has. That license is the entire content of the step. You are converting a claim into a finding by going and looking, and it is spent the moment you write an entry you did not verify. An unverified `evidence` line is worse than no entry: the builder checks the citation before changing anything, and a wrong one turns into a `staleEvidence` report and a wasted node.

## 1. Read the source

Work from what the user points at: a `plannedWork.backlog` item by its `n`, an effort doc under `docs/app-maps/efforts/`, a spec path, or the conversation. Take the whole thing. A backlog item's `ref` names the decision it came from, and that decision's answer in `decisionsSettled` usually carries the constraint the fix has to preserve.

Then read the map: `invariants`, `evolutionTraps`, `acceptedRisks`, and the open `openDebt`. An entry that duplicates live debt, restates an accepted ceiling, or targets something that no longer exists is the common way this step wastes a batch.

## 2. Go and look

For each piece of work, open the code and find where it actually lives. Two rules decide the file set, and both come from real failures:

- **Cite where a thing is BUILT, not only where it is declared.** For anything that adds a field to a model or a case to a rule, grep for where the thing is *constructed* and cite that file too. A builder handed only the declaration site cannot construct the field, and correctly cuts the feature rather than touching a file it was not given, which reads as a failure and is not one.
- **Name only the files you intend to EDIT.** `citedFiles` scrapes path-shaped tokens out of the whole entry and unions them into its file set, so a path mentioned in passing manufactures a collision edge and serialises work that could have run in parallel. Describe comparisons and cross-references without paths.

Companion files are granted automatically and should not be cited: a `pairedArtifacts` counterpart, and anything in the extractor's `COMPANIONS` table. Citing a test file that does not exist yet only produces an unresolved-citation warning.

## 3. Draft the entries

The unit is one `openDebt` entry with its four fields, at a severity (`high`, `medium`, `low`).

**Size by file set, not by layer.** This is where a tracer-bullet instinct goes wrong here: a slice cutting cleanly through schema, API and UI touches enough files to collide with nearly everything, and the collision graph serialises the batch it was meant to parallelise. Size each entry so its file set is the smallest one that leaves the repo working, and let the graph decide what runs beside what.

**Do not declare blocking edges.** The dependency graph is *derived*. `citedFiles` builds it and `plan-batch.mjs` partitions from it. Hand-written "blocked by" lines duplicate that graph and will eventually disagree with it. Where two entries genuinely must land in order for a reason no file set expresses, say so in `fix` and expect them in separate batches.

**An item that cannot be built yet does not become debt.** Leave it in `plannedWork.backlog` with `scope: "held"` and a note saying who held it and what releases it. The extractor refuses a `held` item with no note. A refusal decided by evidence belongs beside the evidence, not in a batch note.

## 4. Wide refactors: expand-contract

A **wide refactor** is one mechanical change, such as renaming a column or retyping a shared symbol, whose blast radius fans across the codebase, so a single edit breaks thousands of call sites and no entry can land green. It also breaks everything downstream of the file set: `scope-gate.sh` refuses the diff, the collision graph makes every entry collide with every other, and worktree isolation stops paying.

Sequence it instead of slicing it:

1. **Expand.** One entry that adds the new form beside the old, breaking nothing.
2. **Migrate.** One entry per batch of call sites, sized by directory or package so each file set is disjoint and each lands green on its own, since the old form still exists. Disjoint file sets are what lets these run in parallel; that is the whole reason to batch by directory.
3. **Contract.** One entry deleting the old form once no caller remains.

Order is carried by the file sets: expand touches the definition, contract touches it again, so the graph serialises them against every migrate batch on its own. Where a migrate batch genuinely cannot stay green alone, say so in `fix` and take the batches on a shared integration branch, with green promised only at the end.

## 5. Quiz the user

Present the draft as a numbered list before writing anything. Per entry: **summary**, **severity**, **the file set** (this is the part that decides parallelism, so it is the part worth reading), and **what it delivers**.

Ask three questions:

- Does the granularity feel right? Anything to merge or split?
- Is any file in a file set there by accident? A stray path is invisible in a diff and is the one thing here that can damage a sprint.
- Anything that should be `held` rather than dispatched?

Iterate until the user approves. Write nothing before they do.

## 6. Write the map

1. **Append each entry** under its severity in `openDebt`, with an id in the map's own naming. Read the stems already there (`S#7` → `S#8`), and check the result against **every id in the map**, not just that section's. The extractor exits 1 on a duplicate wherever its twin lives.
2. **Remove the source backlog item in the same edit.** `plannedWork.backlog` is walked, so a scoped item left in place is dispatched twice: once as vague scope and once as the debt it became. This is the edit that gets skipped.
3. **Stamp `openDebt.verifiedOn`** with today's date. You verified these citations today, and that is what the field records.
4. **Commit the map.** Worktrees materialize only tracked files, so an uncommitted map is invisible to every builder. Branch first; never commit to `main`.

## 7. Verify the partition

Scoping is done when the machinery agrees:

```
bin/appmap drift                     # exit 1 on a structural error
node <extractor> && cat QUEUE.json   # the entries became queue items
```

Read the partition, not just the count. Every new entry should appear with a real `scope` rather than `unscoped`. An `unscoped` item is refused at dispatch and means a citation did not resolve. Two entries you expected to run in parallel landing in the same batch means their file sets overlap: go back and find the shared path, because it is usually a passing mention rather than a real edit.
