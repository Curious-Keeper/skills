---
name: tracer
description: Turn a plan, whiteboard session, or prototype into an ordered set of vertical slices, each cutting narrow but complete through every layer so there is something to touch after each one. Use before a codebase is big enough to map, when work is agreed but there is nothing running yet.
disable-model-invocation: true
---

Build in **tracer bullets**: narrow vertical slices that cut through every layer at once, integrated early, each one leaving something you can actually touch. The alternative is a layer at a time, stacked, which leaves nothing to react to until the last layer lands, and by then every assumption underneath it has hardened unexamined.

```
        ┌─────────┐ ┌─────────┐ ┌─────────┐
  UI    │         │ │         │ │         │
  API   │ slice 1 │ │ slice 2 │ │ slice 3 │
  data  │         │ │         │ │         │
        └─────────┘ └─────────┘ └─────────┘
          touch it    touch it    touch it
```

This is the phase **before a map exists.** There is no `APP_MAP.json`, no queue, no fan-out. You are building serially with the user in the loop, and the constraint being optimised is how fast they get to react. Slice for feedback latency, not for parallelism.

## Not the same unit as a map entry

Where a map exists, work is sized by **file set**, because the queue extractor derives a collision graph from cited paths and serialises anything that overlaps. A vertical slice touches every layer and so collides with nearly everything, correct here and wrong there. The two units serve different constraints and do not convert into each other:

| | tracer slice | `openDebt` entry |
|---|---|---|
| optimises | feedback latency | wall-clock across builders |
| shape | vertical, all layers | whatever the smallest working file set is |
| ordering | **declared**, you state the edges | **derived**, the collision graph does |
| built | serially, you react between | in parallel, one gate at the end |

Declared edges are right here precisely because there is no graph to derive them from yet.

## 1. Read the source

Work from the plan, the whiteboard output, the prototype, or the conversation. If a `prototype` branch settled something, take the verdict rather than the code.

If decisions are still open, stop and call the Skill tool for `designing` first. Slicing an undecided plan produces slices that get thrown away, and the throwing-away looks like progress.

## 2. Prefactor first

*Make the change easy, then make the easy change.* Where existing code makes a slice awkward, the prefactor is its own slice and it goes first. Keep it strictly mechanical. A prefactor that changes behaviour is two slices pretending to be one.

## 3. Draft the slices

<vertical-slice-rules>

- Each slice cuts a **narrow but complete** path through every layer it needs: data, logic, interface, tests. Narrow is the load-bearing word: one case, one field, one route, end to end.
- A finished slice is **demoable or verifiable on its own.** If you cannot show it or run it, it is a layer wearing a slice's name.
- Each slice fits **one fresh context window.**
- Each slice names the slices that must land before it. A slice with no blockers can start now.

</vertical-slice-rules>

**Slice one is the walking skeleton**: the thinnest possible path that touches every layer and works. It is allowed to be embarrassing. Its job is to prove the layers connect and to give the user something to point at, not to be good.

**Order by what you learn, not by what is easy.** The slice that would invalidate the most of the plan if it went badly goes early. A slice that only confirms what you already believe can wait, however tempting it is to start there.

## 4. Wide changes: expand-contract

A change whose blast radius fans across everything, such as renaming a shared symbol or retyping a core model, cannot be a slice, because no narrow path through it leaves the system working. Sequence it instead: **expand** (add the new form beside the old, breaking nothing), **migrate** (call sites in batches), **contract** (delete the old form once nothing references it). Each step is its own slice, each stays green.

## 5. Quiz the user

Present the sequence as a numbered list before building anything. Per slice: **title**, **blocked by**, **what it delivers end to end**, and **what you will be able to touch when it lands**. That last one is the whole point, so if you cannot write it, the slice is horizontal.

Ask:

- Does the granularity feel right? Anything to merge or split?
- Is slice one thin enough? It is almost always still too fat.
- Which slice would hurt most if it went badly? Should it move earlier?

Iterate until approved.

## 6. Build one, then stop

Build the first unblocked slice. Call the Skill tool for `implement`, or build it directly.

Then **stop and show it.** Not a summary. The running thing, or the exact command that runs it. The reaction is the deliverable of the phase, and a session that builds three slices before surfacing has spent the feedback it was buying.

Record what the slice taught you as you go, in whatever the project uses for notes. Two kinds are worth more than the rest, because they are what the first map will be built from:

- **What turned out not to be true.** A shape you assumed, an API that does not work that way. These become `evolutionTraps` the moment the map exists.
- **What bit, and why it was surprising.** These become the first `invariants`, and the bar there is that it has already caused a real bug here, which, by the time you have hit it, it has.

## 7. Know when to stop slicing

Slices are throwaway **as a unit**: they do not become map entries. What survives is the code and what you learned building it.

The exit condition is the harness's own candidacy test, in **`docs/PORTING.md`** in the [`sprint-harness`](https://github.com/Curious-Keeper/sprint-harness) kit. Stop slicing and write the map when all three are yes:

1. There are **≥8 remaining items with few edges between them.** While the work is five things all touching the same module, slicing serially is still the faster path.
2. **A command can tell you the code is broken.** Without an anchor, everything downstream degrades to models agreeing with each other.
3. **A human will actually gate.** The harness converts one gate per item into one gate per batch; it does not remove the gate.

Then hand off: prompts `00` and `01` build `docs/SURFACE.md` and the first `APP_MAP.json`, mining `evolutionTraps` out of the git history you have just created. From there `navigator` charts what is still undecided, `scope` makes work dispatchable, and the sprint runs it in parallel.

You cannot map a codebase that does not exist yet. The map is retrospective by construction. That is why this phase comes first, and why its output is a running system rather than a document.
