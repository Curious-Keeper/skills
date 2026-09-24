# Sharing a canvas with a human

The rules for any skill that draws on the live Excalidraw canvas. `whiteboard`
draws a design tree on it and `navigator` draws a route graph, but both share one
canvas with a person who is drawing at the same time, and these are the rules that
keep them from deleting each other's work.

Setup and operation of the container are in [`README.md`](README.md).

## Before you draw, read

**Read the canvas before every write. No exceptions.** The user edits the same
canvas you do, and sync is last-write-wins, so a write that has not read first
can silently delete their work.

```
describe_scene      structured text: every element, its id, position, colours
```

You know the ids you created. Everything else in that output is the user's. Four
signals, each meaning something different:

| what you see | what it means |
|---|---|
| an element with a red stroke | an annotation — read it against whatever it overlaps or points at |
| an id you did not create | they drew a missing piece themselves |
| one of your elements moved | they regrouped it; the new neighbours are the point |
| one of your elements gone | they rejected it |

A deletion is an answer. Do not redraw it.

## Are they still drawing?

The canvas pushes browser edits to the server on a 3-second debounce, so a read
taken seconds after the user's last stroke can be stale. Before a write that
depends on what you just read, call `describe_scene` twice about four seconds
apart. If the two differ, they are still working: say so and wait, rather than
writing into a moving canvas.

## Back up before you write

```
export_scene    filePath: <somewhere outside the repo>
```

This is the undo, and it is the only one that works. Take one before any batch
write.

### Three tools are broken in sentinel 1.2.1. Do not trust them.

The server requires `?confirm=true` on its delete route. Three MCP tools call
that route without it, and none of them checks the response, so the delete
fails with a 400 that is thrown away and the tool reports success anyway.

| tool | what it does instead | verified |
|---|---|---|
| `clear_canvas` | clears nothing; errors on the confirm step | yes |
| `restore_snapshot` | re-adds the snapshot, removes nothing, reports success | yes — held at 9 while reporting 6 restored |
| `import_scene` | appends to the canvas rather than replacing it | by inspection, same call site |

So: **`restore_snapshot` is not an undo.** It re-adds what was in the snapshot
and leaves everything else in place. **`import_scene` is safe only into an empty
canvas.** To repair a bad write, delete the offending ids with `delete_element`,
which does work, and rebuild from an `export_scene` file.

To genuinely clear a canvas, go around the MCP server to the REST API, and get
a real answer from the user first — this deletes their work as well as yours:

```sh
curl -X DELETE -H "x-tenant-id: <id>" \
     "http://127.0.0.1:3000/api/elements/clear?confirm=true"
```

Each workspace is its own tenant, so clearing "the canvas" may mean clearing
several. `list_tenants` shows them; the count in `/health` covers only the
active one.

## Red is theirs

**Never draw in red.** `#e03131` and its neighbours are reserved for the user, and
that reservation is the whole annotation convention: it needs no zones, no
legend, and no tablet. They select, click the red swatch, and type or drag.

Everything you draw uses the rest of the palette. Each skill states what its own
colours mean, and puts a small legend on the canvas so the user does not have to
remember the coding.

## Recolour, never redraw

When a thing changes state, `update_element` its stroke. Rebuilding the drawing
each round destroys the user's annotations and moves everything out from under
their cursor. Create elements only for what is genuinely new.

## Drawing that comes out right

- `batch_create_elements` for a first layout. **Shapes before arrows**, or the
  arrows bind to nothing.
- `create_element`'s `label` argument produces a `Title` / `Description` pair
  rather than the text passed to it. Place text elements explicitly instead.
- `export_scene` takes **`filePath`**, not `filename`. The other spelling returns
  the scene and writes nothing.
- `import_scene` restores an exported file, which is how a later session picks up
  where this one stopped.
- `describe_scene` reports each element's type, position and stroke **colour**,
  but not its stroke width, opacity or fill. Reach for `query_elements` when you
  need a full element back. Encode meaning in shape and colour, which survive the
  cheap read; treat width and fill as reinforcement for the human eye.

## The canvas is an input surface, not a source of truth

Nothing is settled because it is on the canvas. A canvas is where a question gets
asked and answered quickly, in a form the user can point at; the answer is
durable only once it reaches the file that owns it — an ADR, `CONTEXT.md`, the
map, an effort doc.

So never treat a box as a decision, and never let the canvas write to the map.
When the user's drawing implies a change, say what you read from it and make the
change through the step that owns it.

## When there is no canvas

The `whiteboard` MCP server may not be configured, or the container may be down.
Both are normal. Say so in one line and carry on text-only: every skill that uses
the canvas worked without one first, and still does. Do not stop to fix Docker
unless the user asks.

`get_canvas_screenshot` and `export_to_image` additionally need the canvas open in
a browser tab and return 503 otherwise. Treat them as a supplement;
`describe_scene` is the leg to rely on, and it works headless.

A write reporting `Canvas sync not confirmed (no_clients_in_scope)` succeeded and
reached the database. It just had no browser to push to.
