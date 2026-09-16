---
name: laziness-protocol
description: "Bias toward deletion and the smallest change that solves the problem. Use when refactoring, evaluating diff size, or tempted to add an abstraction, a layer, or a new signal threaded through existing types."
disable-model-invocation: true
---

# Laziness Protocol

Aim for the most result with the least code and complexity.

- **Prefer deletion.** When asked to refactor or improve, look for removals before additions.
- **Maintain a flat call hierarchy.** Avoid deep call chains. A **deep module**, a lot of behavior behind a small interface, is not a deep call chain, and nothing here argues against one. If answering a question requires tracing through more than 3 files or layers, flatten it.
- **Consolidate decisions.** Do not repeat the same choice in several places. Put it behind a **single source of truth** and pass the result as a simple flag.
- **Minimize the diff.** Make the smallest change that solves the problem. Fewer lines beat "elegant" boilerplate.
- **Question the threading.** If a task asks you to pass a new signal through types, schemas, pipelines, or similar layers, stop and look for a more direct path.
- **Sweat the small leaks.** Remove tiny pass-throughs, representation leaks, and duplicated choices before they spread. Small leaks compound into permanent coordination costs.

**The test:** If a human developer would find the code exhausting to maintain, it is a bad solution.
