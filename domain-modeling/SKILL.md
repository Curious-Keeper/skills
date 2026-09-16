---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a CONTEXT.md, or recording or editing an ADR.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the _active_ discipline: challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely _reading_ `CONTEXT.md` for vocabulary is not this skill: that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## In a repo with an `APP_MAP.json`

The map is already the store for three of the four things this skill writes, and duplicating them there is how a map goes quietly wrong:

| you would write | it already lives in |
|---|---|
| an ADR | `plannedWork.decisionsSettled`, under the id of the question it answers |
| a rule that has already caused a bug here | `invariants` |
| a term that used to mean something else | `evolutionTraps` |
| a term's current meaning | `CONTEXT.md`, **which has no home in the map** |

So in a mapped repo: keep `CONTEXT.md` as the glossary, and settle decisions in the map rather than in `docs/adr/`, where the board shows them and later prose can cite their ids. The three offer-an-ADR tests below are the right tests for whether a settled decision's answer needs a paragraph or a sentence.

Read **`docs/MAP_GUIDE.md`** from the [`sprint-harness`](https://github.com/Curious-Keeper/sprint-harness) kit before writing an invariant or a trap. Use a local checkout if there is one, otherwise fetch it from the repo. The bar for an invariant is that it has already caused a real bug in this repo; a list padded with plausible-sounding rules trains every agent to skim the section.

## File structure

In an unmapped repo, most repos have a single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily: only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account': do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible. Which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up: capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse**: the cost of changing your mind later is meaningful
2. **Surprising without context**: a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).
