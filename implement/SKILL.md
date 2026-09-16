---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Work to the project's **anchors**, the commands in `.claude/harness.config.json` that decide whether the work stands. Run the narrow ones (typecheck, the single test file you are touching) continuously, and the full set once at the end. Where a seam is worth a test first, write the test first.

Once done, review the work, then commit it to a branch, never to `main` or `master`, and stop before pushing.

## In a repo with an `APP_MAP.json`

The item you are building came out of the map, so the map binds the work:

1. **Read `invariants` and `evolutionTraps` before touching code.** Each invariant has already caused a real bug in this repo, and each trap is something that used to be true and no longer is. Both are cheaper to read than to rediscover.
2. **Verify the item's evidence before changing anything.** An `openDebt` entry cites `file:line`. Confirm the citation still says what it claims; where it does not, report **stale evidence** and stop rather than quietly building against a moved target. Map rot is a finding, not an obstacle.
3. **Stay inside the item's file set.** The paths in the item's evidence are what it claims; `core/scope-gate.sh` enforces it. Where the work genuinely needs a file the item does not name, say so and stop. A builder that reaches outside its set is the collision the graph exists to prevent.
4. **Never hand-edit a generated file.** The map names each one and the command that produces it; run the generator.
5. **Close the item in one edit: add the `shipped` entry AND remove it from `openDebt`.** The second edit is the one that gets skipped, and an item sitting in both places is re-dispatched next batch against work already on main. Record in `how` what the fix taught you, including anything it left open.

Commit the map with the code.
