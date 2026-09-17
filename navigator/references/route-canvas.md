# The route canvas

The Route table records blocking as a `blocked by` column, which means the shape
of an effort — what is takeable now, what is waiting, and how much of it needs a
human — is spread across a column of ids nobody can hold in their head. The board
does not close this gap and is not meant to: its DECIDE lane lists every open
ticket, blocked or not.

This draws the Route table as a graph.

**Read [`../../whiteboard/canvas/PROTOCOL.md`](../../whiteboard/canvas/PROTOCOL.md)
first.** Read before you write, red is theirs, snapshot first, recolour rather
than redraw. This file adds only what is specific to a route.

## What the graph shows

One node per ticket. One edge per blocking relation, drawn from the blocker to
the ticket it blocks, so the arrows run in the direction work becomes possible.

Two channels, and they answer different questions.

**Colour is state** — can this be worked?

| state | colour | in the Route table |
|---|---|---|
| frontier | `#1971c2` blue | open, unblocked, unclaimed |
| claimed | `#f08c00` amber | open, unblocked, `claimed` is set |
| blocked | `#868e96` grey | open, some blocker still open |
| settled | `#2f9e44` green | in `decisionsSettled` |
| theirs | `#e03131` red | **never write it** |

**Shape is who it needs** — can this run without you?

| type | mode | shape |
|---|---|---|
| `designing` | HITL | rectangle |
| `prototype` | HITL | rectangle |
| `research` | AFK | ellipse |
| `task` | either | diamond |

Draw every HITL node with a `strokeWidth` of 4 and every AFK node with 2. That
one difference is the most useful thing on the canvas: **the heavy nodes are the
ones that need the user in the room, and everything reachable only through them
is time they cannot be away.** Say that in the legend, in those words.

The width is for their eye, not yours: `describe_scene` does not report it. Shape
is the channel you read back, which is why type is doubled into both. Never encode
something in width alone.

Put the fog on too, as a dashed grey region titled **Not yet specified**, with one
node per patch. It is the honest edge of the map, and leaving it off makes the
route look more finished than it is.

## Rebuilding it each session

The Route table is the truth about nodes, edges and state. The canvas is the truth
about annotations. Reconcile, never regenerate:

1. If the canvas is empty, `import_scene` from
   `docs/app-maps/efforts/<slug>.excalidraw` where one exists.
2. `describe_scene`. Harvest every red element and every id you did not create —
   those are the user's and they survive this session untouched.
3. Compare the ticket nodes against the Route table. `update_element` the stroke
   of any node whose state changed; `batch_create_elements` for tickets added
   since the last session.
4. Never `clear_canvas` a route. A ticket ruled out of scope is recoloured grey
   and struck, not deleted — navigator keeps its id for the same reason
   `decisionsSettled` does, and the graph should show the route actually walked.

## What their marks mean here

Annotations on a route are proposals about the map, so each one maps to a step
navigator already owns. **The canvas never writes the map.** Read the mark, say
what you read, and make the change through the step that owns it.

| what they drew | what to propose |
|---|---|
| red note on a ticket | a steer, or the answer itself — confirm, then settle it at step 4 |
| an arrow between two tickets | a blocking edge the Route table is missing. Add the row, re-derive the frontier |
| a box with no ticket | a decision the chart missed. Ticket it if the question is sharp, else add a fog patch |
| a node crossed out in red | rule it out of scope: settle it `resolved`, plus a line under **Out of scope** |
| a ring around several nodes | they are one ticket, or one session. Ask which — the two have different consequences |

A node deleted outright is the one signal to slow down on. Deleting is not how a
ticket leaves a route: propose the out-of-scope move and let them confirm, then
redraw the node struck rather than gone.

## Where it is saved

```
export_scene    filePath: docs/app-maps/efforts/<slug>.excalidraw
```

Beside the effort doc, and committed with it — navigator commits the map and the
effort doc together, and the graph is a third view of the same state. A route
canvas that only exists in a container is a route nobody else can see.
