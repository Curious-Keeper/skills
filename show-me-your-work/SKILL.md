---
name: show-me-your-work
description: "Keep a reviewable decision trail for long-running, unattended, or multi-phase work: one append-only TSV with a row per decision, carrying what was chosen, why, the evidence, and the result. Use when a run is long enough that a human will review it after stepping away, when work is dispatched to builders, or when another skill needs an audit-trail format."
---

# Show me your work

**Keep one canonical log, so a human who stepped away can reconstruct the run without reading the transcript.**

The trail is not a summary. A summary is written at the end, by the agent that already knows how the story turned out, and it smooths over the fork it took wrongly and reverted. A trail is written as it happens and cannot.

This is not `handoff`, which compacts a conversation so the *next agent* can continue. This is for the *human reviewer*, during the run, and the two carry different things: the handoff carries state, this carries decisions and their evidence.

## The format

A single TSV file. One row per decision. Cells stay single-line, and evidence is a pointer rather than prose.

Start from [`references/decision-log-template.tsv`](references/decision-log-template.tsv), which is the header row and nothing else. [`references/example-trail.tsv`](references/example-trail.tsv) shows five rows written in the right voice. Read it to calibrate, and do not copy its rows into a real log. The columns:

- **ts.** ISO 8601 timestamp.
- **phase.** The phase, workstream, or queue item id this belongs to.
- **decision.** What was chosen or done, one line.
- **why.** The reason in plain words. Where a principle drove it, say the thing plainly rather than tagging it.
- **evidence.** A pointer that proves it: a commit SHA, a PR number, a `file:line`, an anchor's exit, or a path to an artifact, trace, or screenshot. Never a paragraph.
- **result.** The outcome: `tests green`, `anchor build failed`, `reverted`, `pixel-diff 0`, `INCONCLUSIVE`, `open`.

Where the project runs the sprint harness, use its own vocabulary in `result` for anything that reached a verdict: `accepted`, `rejected`, `unverified`, `notBuilt`. A reviewer reading the trail and the batch history should not have to translate between two sets of words for the same outcome.

## Logging a row

Write each row the way you would tell a teammate what you did. Plain words, concrete actions. The `unslop` skill applies to log text too, and a row full of "leveraged", "robust", and "comprehensive" is a row that says nothing.

Use the helper:

```
scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>
```

It stamps `ts`, writes the header on first use, strips stray tabs and newlines out of cells, and guards the leading characters a spreadsheet would read as a formula. A plain `printf` append works too, but then those bytes are yours to mind, and any cell built from generated or user-supplied text is where it bites.

Log decisions and checkpoints, not actions. A fork chosen. A unit completed, with its verification result. A pivot or a revert, with what triggered it. A blocker surfaced. An anchor fixed. For a loop, one row per iteration. Skip the trivial and the self-evident: the trail is worthless if a reviewer has to skim 200 rows to find the four that mattered.

## Where it lives

By default the log is a working artifact and stays out of git: `decisions.tsv` in the working directory, or `.audit/<task-slug>.tsv` when several efforts run at once.

Commit it when a reviewer needs the trail to trust the result.

**One exception that is not a judgment call.** Builders and verifiers run in git worktrees, which materialize only tracked files. An uncommitted trail does not exist inside a builder's worktree. So work dispatched through `QUEUE.json` commits its trail as part of the node, or the trail is not there when the reviewer opens the branch. Decide this before dispatch, not after.

## Rules

- One row is one decision or checkpoint.
- **Append-only.** A wrong call gets a new row that supersedes it. Never edit or delete history, because the reverted fork is often the most useful row in the file.
- Prefer evidence produced by a committed script over a hand-made one-off. A reviewer who can rerun the check does not have to trust the row.
- A negative result is a row. An `INCONCLUSIVE` is a row. Neither is a pass, and neither gets quietly dropped on the way to a green summary.

## Audit the trail before you hand it back

At the end of the run, check the log told the truth. Read this run's transcript, locating it the way the `recall` skill describes rather than assuming a path, and never reading another workspace's transcripts to do it.

Walk the log against what actually happened:

- Every row maps to a real action. Cut anything invented or aspirational.
- Each row's evidence resolves, and shows what the row claims it shows.
- A fork, pivot, or abandoned approach that shaped the work but is not logged is a gap. Add it.
- Drop padding.

Fix the log, not the story. Where the work diverged from what a row claims, the row is wrong.

## Cross-model review of the trail

Before handing back, spawn one sub-agent on a different model family from the one that did the work. Self-review does not substitute: the model that made a bad call is the model least able to see it. Take reviewers from `interrogate.reviewers`, then `models.roles.reviewer`, the same way `interrogate` does. Paste the trail and the relevant context into the prompt rather than citing paths, since a reviewer on another vendor's model cannot read this repo.

Build its prompt from [`references/trail-reviewer.md`](references/trail-reviewer.md). It reads the trail and the run, and flags what the user should look at. It does not redo the work.

Every reply for a run that produced a trail ends with an **Attention** section: the reviewing model named on its own line, then one line per flag pointing at a specific row. "No flags" is a valid value, and saying nothing at all is not.

## Composing this skill

Other skills route their audit trail here rather than inventing one. Reference this skill by name and let it own the format. Do not restate the columns.

**Reply:** the path to the trail, the rows a reviewer should start with, and the Attention section.
