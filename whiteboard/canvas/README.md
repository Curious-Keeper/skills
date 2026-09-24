# The whiteboard canvas

A live Excalidraw canvas the agent draws on and you draw on, in one container.

```
docker compose up -d --build     # start
xdg-open http://localhost:3000   # open the canvas
docker compose down              # stop (the drawing survives, in the volume)
```

The container carries `restart: unless-stopped`, so it comes back whenever you
start the Docker daemon — and stays down if you stopped it deliberately. It
never starts the daemon itself.

## What is inside

[`excalidraw-mcp-sentinel`](https://github.com/artificemachine/excalidraw-mcp-sentinel),
a hardened fork of [`yctimlin/mcp_excalidraw`](https://github.com/yctimlin/mcp_excalidraw)
that adds SQLite persistence, per-workspace tenants and a test suite. Pinned in
the `Dockerfile` by `SENTINEL_VERSION`.

We build the image rather than pulling one: the `artificemachine/*` images its
README documents were never published to Docker Hub.

One container, two roles:

| role | process | reached by |
|---|---|---|
| canvas + database | PID 1, `dist/server.js` | your browser, on `127.0.0.1:3000` |
| MCP server | `docker exec -i`, `dist/index.js` | the agent, over stdio |

They are one process tree, so they share one database and one filesystem, and the
canvas outlives any single agent session. The MCP half starts its own canvas
server, finds the port taken, and attaches to the running one.

## Wiring an agent to it

The MCP server is declared per project. In `sprint-harness/.mcp.json`:

```json
{
  "mcpServers": {
    "whiteboard": {
      "command": "docker",
      "args": [
        "exec", "-i",
        "-w", "${WHITEBOARD_WORKSPACE:-${PWD}}",
        "-e", "EXCALIDRAW_EXPORT_DIR=${WHITEBOARD_WORKSPACE:-${PWD}}",
        "whiteboard-canvas",
        "node", "/opt/app/node_modules/excalidraw-mcp-sentinel/dist/index.js"
      ]
    }
  }
}
```

To use it from another repo, copy that file there and add the repo to the bind
mounts in `docker-compose.yml`.

## Two settings that are load-bearing

**The bind mount uses the same path inside the container as outside.** A path
then means the same thing to you, to the agent and to `export_scene`, so a
`.excalidraw` file saves where you expect. Add one line per repo:

```yaml
volumes:
  - /home/you/git_projects/your-repo:/home/you/git_projects/your-repo
```

**The container runs as uid 1000.** The `node` images ship a `node` user at
uid/gid 1000, which is the ordinary first-user id on Linux. Run as root instead
and every exported file lands owned by root. If your uid is not 1000, change
`user:` in `docker-compose.yml` to match `id -u`.

## Each repo gets its own canvas

The server derives a tenant from the workspace root the MCP client reports, so
two projects do not share a drawing. `list_tenants` and `switch_tenant` move
between them; the canvas UI has a workspace dropdown for the same thing.

## Security

The canvas publishes on `127.0.0.1:3000` only, and runs with authentication off.
That is fine for a loopback-only service and keeps a shared secret out of a
committed file. Set `EXCALIDRAW_API_KEY` before exposing the port anywhere else —
the browser UI picks the key up automatically, and every `/api/*` route then
requires it.

## When it misbehaves

```
docker compose ps                     # is it up and healthy?
docker compose logs -f canvas         # what it thinks is wrong
curl -fsS http://127.0.0.1:3000/health
```

`{"status":"healthy", ...}` also reports `websocket_clients`. Zero means no
browser tab is open — which is why `get_canvas_screenshot` and `export_to_image`
return 503. `describe_scene` works regardless.

A write that reports `Canvas sync not confirmed (no_clients_in_scope)` succeeded
and reached the database; it just had no browser to push to.
