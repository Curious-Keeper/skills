---
name: whiteboard
description: A relentless interview to sharpen a plan or design, held over a live Excalidraw canvas you can draw on, which also creates docs (ADRs and glossary) as we go.
disable-model-invocation: true
---

# Whiteboard

An interview you can draw on. The canvas is where the design tree becomes
visible; the durable output is still ADRs and a glossary.

Three skills, one session:

| | owns |
|---|---|
| `whiteboard` | the canvas: what is drawn, and reading back what the user drew |
| `designing` | the interview: the design tree, the frontier, the rounds |
| `domain-modeling` | the record: ADRs and `CONTEXT.md` |

Call the Skill tool for `designing` and `domain-modeling` at the start. They run
unchanged. This skill adds a surface to them, and takes no decisions of its own.

**Read [`canvas/PROTOCOL.md`](canvas/PROTOCOL.md) before drawing anything.** It
holds the rules for sharing a canvas with someone who is drawing on it too: read
before you write, red is theirs, snapshot first, recolour rather than redraw. They
are not optional and they are not repeated here.

**The canvas is optional.** Where the `whiteboard` MCP server is not configured or
its container is down, say so in one line and run the interview text-only. That is
what this skill was before it could draw, and nothing below is load-bearing for it.

## What the colours mean

| state | colour | meaning |
|---|---|---|
| settled | `#2f9e44` green | decided, and written into an ADR |
| open | `#1971c2` blue | on the frontier, asked this round |
| blocked | `#868e96` grey | waiting on a decision above it |
| theirs | `#e03131` red | **never write it** |

## Drawing the design tree

`designing` produces a tree of decisions worked in rounds, where the frontier is
every decision whose prerequisites are settled. That tree is the thing to draw.

- One node per decision. Number it to match the `Q1`, `Q2` of the round, so an
  answer in chat and an answer on the canvas mean the same thing.
- An edge from each decision to the decisions that hang off it.
- Colour by state.
- When a decision settles, recolour it. Do not rebuild the tree.

Draw the round's questions, then ask them in chat as `designing` specifies. The
canvas does not replace the written round; it gives the user somewhere to answer
that is faster than prose.

## Reading their answers

Everything in the protocol's four-signal table applies, and here is what each one
settles:

| signal | what it means for the tree |
|---|---|
| red note on a node | the answer, or a constraint on it — restate it and confirm |
| a box they drew | a decision the tree was missing; add it and re-derive the frontier |
| a node moved beside another | the two are one decision, or the order is wrong |
| a node deleted | the question does not apply. Do not re-ask it |

An answer given on the canvas is an answer. Carry it into the round as though
they had typed it.

## Ending the session

The canvas is scratch, so it ends as a file rather than as a live service:

```
export_scene    filePath: docs/app-maps/efforts/<slug>.excalidraw
```

That path sits beside the effort doc `navigator` keeps, so a later session picks
up both together.

Then the real outputs, through `domain-modeling`: an ADR per decision settled,
and the terms the session argued about in `CONTEXT.md`. A session that ends with
only a drawing has produced nothing.

## Where this goes next

`whiteboard` is the unmapped conversation. When the effort is bigger than one
session and the project keeps an `APP_MAP.json`, `navigator` charts it as decision
tickets and draws the route graph on this same canvas — see
[`../navigator/references/route-canvas.md`](../navigator/references/route-canvas.md).
