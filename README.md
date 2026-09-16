# skills

Agent skills for the Sprint Harness Toolchain.

A skill is a Markdown file describing a procedure precisely enough that an
agent can follow it without improvising. These are the procedures used to plan,
scope, build, review and hand off work across a set of projects that keep an
`APP_MAP.json` — a machine-readable record of what a codebase is, what it owes,
and what has already gone wrong in it.

Some skills stand alone and will work in any repo. Others read that map or the
project's harness config, and are only fully useful alongside
[`sprint-harness`](https://github.com/Curious-Keeper/sprint-harness).
`manifest.json` records exactly which is which.

## Install

Claude Code discovers skills in `~/.claude/skills`:

```sh
git clone https://github.com/Curious-Keeper/skills.git ~/git_projects/skills
ln -s ~/git_projects/skills ~/.claude/skills
```

Invoke one by name: `/interrogate`, `/scope`, `/review-unpushed`. A skill marked
`disable-model-invocation: true` runs only when you ask for it and is never
picked up on its own — which is the right default for anything that spends real
money or rewrites real files.

Each skill also ships an `agents/openai.yaml`, so the same procedure can be
loaded by a non-Claude runtime rather than being locked to one vendor.

## What is here

`M` marks a skill listed in `manifest.json` as coupled to the harness. `U`
marks one that only runs when you invoke it.

| | Skill | What it does |
|---|---|---|
|`MU`| `blast-radius` | Find what a change could break beyond the diff |
|`M` | `code-review` | Review changes since a fixed point: standards, spec, invariants |
|    | `codebase-design` | Vocabulary for designing deep modules |
|` U`| `create-verification-skill` | Generate a project-local skill that drives the app like a user |
|    | `designing` | Interview the user relentlessly about a plan or decision |
|`M` | `domain-modeling` | Build and sharpen a project's domain model |
|` U`| `handoff` | Compact a conversation into a handoff document |
|`M` | `how` | Explain how a subsystem actually works |
|`MU`| `implement` | Implement work from a spec or tickets |
|` U`| `improve-codebase-architecture` | Find deepening opportunities and grill through them |
|`MU`| `interrogate` | One reviewer per configured model, adversarially, then a lead verdict |
|` U`| `laziness-protocol` | Bias toward deletion and the smallest change that works |
|` U`| `maintain-verification-skill` | Keep a verification skill and feature map honest |
|`MU`| `navigator` | Chart a large effort as owed decisions, settle them one at a time |
|`MU`| `no-comments` | Delete comments, fix the code they were covering for |
|    | `prototype` | Build a throwaway prototype to answer a design question |
|`MU`| `recall` | Reconstruct working context from history and live state |
|` U`| `redesign-from-first-principles` | Integrate a requirement as if it had always been there |
|    | `research` | Investigate against primary sources, capture findings as Markdown |
|`MU`| `review-unpushed` | Interrogate the commits that have not reached the remote |
|`MU`| `scope` | Break work into dispatchable entries in the map |
|`M` | `show-me-your-work` | An append-only decision trail for long unattended runs |
|`M` | `technical-writing` | Diátaxis, Google developer style, Simplified Technical English |
|`MU`| `tracer` | Turn a plan into ordered vertical slices |
|    | `unslop` | Cut AI tells from writing |
|` U`| `whiteboard` | A relentless interview that leaves ADRs and a glossary behind |
|    | `writing-for-agents` | Writing documents that agents read |

## manifest.json

The manifest is the reviewable index of how these skills touch the toolchain:
for each one, which harness config keys it reads, which `APP_MAP.json` sections
it reads, and which it writes. It exists so that changing a map section or a
config key does not mean grepping 27 files to find out what breaks.

Keep it current. A skill that starts reading a config field or writing a map
section without updating its row is the failure the file is there to prevent.
`manifest.schema.json` validates the shape. Run `python3 check_manifest.py`
to check that the README's `M` markers, `manifest.json`, the harness config
schema, and the map skeleton still agree.

## Shared contract

This repository is one part of the Sprint Harness Toolchain. The shared
cross-repo contract lives in
[`../sprint-harness/docs/TOOLCHAIN.md`](../sprint-harness/docs/TOOLCHAIN.md).
Use the glossary in [`../sprint-harness/CONTEXT.md`](../sprint-harness/CONTEXT.md)
when naming shared concepts. Read both files before changing map sections,
harness config keys, skill coupling, or shared vocabulary.

Use this checklist for cross-repo changes:

- If a skill starts reading or writing a map section, update `manifest.json` in
  the same change.
- If a skill starts reading a harness config key, update `manifest.json` in the
  same change.
- If the map shape changes, update affected skills after the
  `sprint-harness` skeleton and `appmap-board` loader are updated.
- If shared vocabulary changes, update `../sprint-harness/CONTEXT.md` first.

## Attribution

Several skills here began as work published by other people. Some were
rewritten almost entirely; **others remain close to the original**.
Their notices are reproduced in full in [NOTICE](NOTICE) rather than merely
thanked here. Without others' hard work and research, shared growth would
not be possible.

**[mattpocock/skills](https://github.com/mattpocock/skills)** — (c) 2026 Matt
Pocock, MIT:

`codebase-design` · `code-review` · `designing` · `domain-modeling` ·
`handoff` · `implement` · `improve-codebase-architecture` · `prototype` ·
`research` · `tracer` · `whiteboard` · `writing-for-agents`

`designing` and `whiteboard` are both descendants of his `grill-me`.

**[pstack](https://github.com/cursor/plugins/tree/main/pstack)**, by Lauren Tan
— (c) 2026 Lauren Tan, MIT:

`blast-radius` · `create-verification-skill` · `how` · `interrogate` ·
`laziness-protocol` · `maintain-verification-skill` · `no-comments` · `recall` ·
`redesign-from-first-principles` · `review-unpushed` · `show-me-your-work` ·
`technical-writing` · `unslop`

`laziness-protocol` and `redesign-from-first-principles` correspond to the
upstream `principle-` skills of those names. `review-unpushed` is a variant of
`interrogate` that reuses its reference files, so it descends from pstack too.
`research` carries pstack ideas as well, while sharing a name with Matt
Pocock's; treat both as upstream for it.

**Written for this repo:** `navigator` and `scope`.

This repo is a modified, harness-coupled derivative of two other people's work,
not an original collection with a few borrowings.

Where a skill was modified, the modification is usually coupling the original
procedure to `APP_MAP.json` and the harness config, which neither upstream has
any notion of. `interrogate` is the clearest case: the multi-model adversarial
review is Lauren Tan's idea, while the configured reviewer roster, the
reachability layer and the cross-vendor substitution rules are not. That is a
statement about what changed, not a claim to have invented what came before.
Neither author has reviewed or endorsed this repository.

Ideas from named sources are credited where they are used — for example
`codebase-design/DESIGN-IT-TWICE.md` cites "Design It Twice" from John
Ousterhout's *A Philosophy of Software Design*.

I am human, and I make mistakes, miss things, and will also happily
give credit where credit is due. If I have misidentified, or misattributed
any of this, please let me know and I will update accordingly.

## Licence

MIT. See [LICENSE](LICENSE), and [NOTICE](NOTICE) for upstream copyrights
that portions of this work carry forward.
