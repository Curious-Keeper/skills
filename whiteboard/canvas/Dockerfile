# Excalidraw canvas + MCP server for the `whiteboard` skill.
#
# The published `artificemachine/*` images referenced in the upstream README do
# not exist on Docker Hub, so we build our own and pin the version.
#
# Node 22 rather than the host's Node 26: better-sqlite3 12.6.2 ships prebuilt
# binaries for LTS, and building it from source is the one thing that makes this
# install fragile.

FROM node:22-slim AS build

ARG SENTINEL_VERSION=1.2.1

# better-sqlite3 falls back to a source build when no prebuilt binary matches.
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 make g++ \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app
RUN npm install --omit=dev --no-audit --no-fund \
        "excalidraw-mcp-sentinel@${SENTINEL_VERSION}"

FROM node:22-slim

# curl is the healthcheck; the image has no other runtime dependency.
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/app /opt/app

ENV APP_DIR=/opt/app/node_modules/excalidraw-mcp-sentinel

# 0.0.0.0, not the upstream default of `localhost`, or the published port reaches
# nothing but the container's own loopback.
ENV HOST=0.0.0.0 \
    CANVAS_PORT=3000 \
    EXCALIDRAW_DB_PATH=/data/excalidraw.db

# The node images ship a `node` user at uid/gid 1000. Running as that user means
# a file written into a bind mount is owned by the host user of the same id,
# rather than by root. A fresh named volume inherits this ownership.
RUN mkdir -p /data && chown -R node:node /data
USER node

VOLUME /data
EXPOSE 3000

WORKDIR /opt/app

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://127.0.0.1:3000/health || exit 1

# PID 1 is the canvas only. The MCP server is a second, short-lived process that
# `docker exec -i` starts per agent session (see docker-compose.yml).
CMD ["node", "/opt/app/node_modules/excalidraw-mcp-sentinel/dist/server.js"]
