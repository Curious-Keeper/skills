---
name: how
description: "Explain how a subsystem actually works: its runtime flow, the mental model a maintainer needs, and which module owns what. Use when the user asks how something works, wants a walkthrough before changing code, or asks a placement question such as where something should live, which package owns it, or whether it is at the right layer."
---

# How

**Explain how a part of this codebase works, grounded in a path you actually traced.** The deliverable is a mental model a maintainer can hold, not a tour of file names.

Naming the files is not grounding. A walkthrough that lists `auth/session.ts` and `auth/middleware.ts` and asserts that one calls the other reads exactly the same whether or not it is true. Trace one real path end to end and cite it.

This is not `recall`, which rebuilds what *you* were recently doing. It is not `research`, which reads primary sources outside the repo. It is not `code-review`, which judges a diff against a bar. This skill answers what the code in front of you does, and where a new piece of it belongs.

## The three questions

Classify the question before you start, because each one ends somewhere different.

- **Flow.** What happens when X occurs? Ends in a traced path: entry point, each hop, the state each hop reads and writes, where it terminates.
- **Mental model.** How should I think about this subsystem? Ends in the handful of concepts and invariants that make the rest of the code predictable, plus the places the model leaks.
- **Placement.** Where should this live, which module owns it, is this the right layer? Ends in a named owner and the seam that justifies it.

For a placement question, call the Skill tool for `codebase-design` first and answer in its vocabulary. "Where should this live" is a question about depth and seams, and answering it in ad-hoc words is how a module ends up shallow.

## 1. Scope the question

Pin what the user is asking about and which of the three questions it is. Say the classification back in one line, because a flow answer to a placement question is a wasted run.

Pin the boundary too. "How does auth work" is unanswerable; "how does a request get from the edge to an authenticated user object" is a path. Narrow it yourself and state the narrowing.

## 2. Ground from what the repo already documents

Read the cheap sources before spending a single sub-agent:

- In a repo with a `docs/app-maps/APP_MAP.json`, its `architecture` section, its `invariants.items`, and its `evolutionTraps.items` for the area. An invariant is a rule that has already caused a real bug here, and a trap is something that used to be true. Both are load-bearing for a mental model and neither is visible in the code.
- `CONTEXT.md` files and ADRs for the vocabulary the codebase actually uses. Use those terms; do not coin new ones.
- The project's anchors in `.claude/harness.config.json`. The commands the project trusts tell you which behaviour it considers worth guarding.

Where these contradict the code, the code wins and the contradiction is a finding. Say so.

## 3. Fan out explorers

Spawn read-only sub-agents in parallel, one per slice of the question, on a fast model. Slice by hop for a flow question, by module for a mental model, by candidate owner for a placement question.

Build each prompt from [`references/explorer-prompt.md`](references/explorer-prompt.md). Paste the grounding from step 2 into it rather than citing the paths: an explorer on another vendor's model cannot read this repo. Take reviewers from `interrogate.reviewers`, then `models.roles.reviewer`, the same way `interrogate` does. With neither field configured, use whatever the host defaults to.

Every explorer returns citations or says it found nothing. A search that finds nothing is a real answer and you need it, because it is what separates "nothing else calls this" from "I did not look."

For one or two slices, skip the fan-out and read directly. The raw file contents stay in the sub-agents; the main thread takes their findings.

## 4. Trace one real path

Do this yourself, in the main thread, after the explorers return. Pick the single most representative path and walk it hop by hop, opening each file. At every hop record the `file:line`, what it does, and the state it reads or writes.

Two rules bind this step:

- **Never invent a caller, a function, or an API.** If you cannot find the next hop, the trace stops there and you say where it stopped.
- **Follow what a symbol search misses.** The trace is only worth having where grep stops: a string key, a route table, dependency injection, an event name, a database column, a wire format, a feature flag, a generated file, or another language reading the same bytes.

Where the trace contradicts an explorer, trust the trace and note the correction.

## 5. Explain it

Build the answer from [`references/explainer-prompt.md`](references/explainer-prompt.md) and write it through the `unslop` skill.

Lead with the model, not the tour. A reader who stops after the first paragraph should still come away with the one idea that makes the rest predictable.

## Output contract

- **The model.** What a reader who stops here needs to predict the rest: the concepts and invariants, nothing else.
- **The path.** The traced hops in order, each with a real `file:line` and what it does. For a placement question, the candidate owners with the seam each one implies.
- **Where the model leaks.** The special cases, the hop that is not where you would expect it, the thing the names lie about.
- **Unknowns.** What you could not establish, and where the trace stopped. Never pad this into certainty.
- **The answer.** One paragraph answering the question as asked. For a placement question, name one owner and say why.

Anything the repo should have told you but did not is worth writing down. A missing invariant belongs in `invariants.items`, a stale assumption in `evolutionTraps.items`, and a term the code uses but nothing defines belongs in a `CONTEXT.md` via `domain-modeling`. Offer the edit; do not make it as a side effect of answering a question.

**Reply:** the answer, to the contract above.
