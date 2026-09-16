---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

Spin up a **background agent** to do the research, so you keep working while it reads.

Its job:

1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.
4. **Commit it.** An uncommitted file leaves the tree dirty, and a dirty tree blocks every guarded map write downstream.

## In a repo with an `APP_MAP.json`

The convention is a doc beside the map, named from the question that needed it and cited by that question's id. The pattern is a decisions-chain doc such as `docs/PII_decisions_chain.md`. Open it with a banner saying what it is and what it settled, so the next session reads it instead of re-deriving it.

**Findings are claims about the world outside this repo, not facts about the code.** They never become `openDebt`: a debt entry carries `file:line` evidence and a mechanism, and nothing here has read the repo. Research answers a decision; raising the work that follows is a separate act.
