---
name: interrogate
description: "Spawn one reviewer per configured model to adversarially review a changeset from independent angles, then synthesize a lead verdict. Use when the user wants a multi-model or adversarial review, wants a change stress-tested or torn apart, or wants blind spots found."
disable-model-invocation: true
---

# Interrogate

Spawn one reviewer per configured model to adversarially review code changes. Each model gets the same prompt and rubric. The adversarial signal comes from model diversity, not assigned personas.

The deliverable is a synthesized verdict. **Do not auto-apply changes.**

This is not `code-review`. That skill runs three axes (standards, spec, invariants) as sub-agents of one model and reports them side by side. This one runs one prompt across many models and decides between them. Reach for `code-review` to check a change against a documented bar, and for this to find what a single model cannot see.

## Reviewer roster

The roster is an `interrogate.reviewers` array in the project's harness config, one entry per reviewer, each naming a model. Read it from the config the project already keeps, such as `.claude/harness.config.json`.

If `interrogate.reviewers` is absent or empty, fall back to `models.roles.reviewer`. A string means one reviewer. An array means one reviewer per model; assign Reviewer A/B/C/D labels in order. With neither field configured, use the defaults below.

One reviewer per entry. Extend or shrink the Reviewer A/B/C/D labels to the configured count.

| Reviewer | Default family and tier | Example slug |
|---|---|---|
| Reviewer A | Claude, highest reasoning tier | `claude-opus-5` |
| Reviewer B | GPT, highest reasoning tier | `gpt-5.6` |
| Reviewer C | Grok, fast tier | `grok-4.6-fast` |
| Reviewer D | Claude, second family member | `claude-fable-5` |

Slugs rot faster than anything else here, so the configured roster wins over this table, and the table is examples rather than a contract. Where the configured value is `inherit-parent` or `auto`, pin no model at all rather than treating the alias as a broken slug.

### How to reach each one

Your own agent runtime probably spawns only its own vendor's models. Claude Code's `Agent` tool takes `sonnet | opus | haiku | fable` and nothing else, so a roster naming GPT or Grok cannot be spawned that way and a skill that tries will quietly review with one vendor. Ask the harness instead:

```sh
node .claude/harness-core/models.mjs status --json
```

Each entry in `reviewers` carries a `via` and, where one exists, an `argv`:

| `via` | What it means | How to spawn |
|---|---|---|
| `host` | your own runtime spawns it natively | the `Agent` tool, pinned to that model |
| `runner` | a command on this machine drives it | run `argv`, piping the prompt on **stdin**, then verify what ran |
| `apiKey` | only the provider key is present | you have no dispatcher; treat as unreachable unless you can call the API |
| `unreachable` | nothing here can reach it | do not spawn; report it |

Pipe the filled prompt on stdin rather than passing it as an argument — a diff will exceed `ARG_MAX`:

```sh
printf '%s' "$PROMPT" | <argv from the status output>
```

The `argv` already carries the runner's read-only flags. A reviewer must never edit files, so do not add write or force flags to it. Build the `argv` only from that output — never hand-write a runner invocation, because the flags that make a runner read-only and the flag that actually selects the model both live in the catalog.

### Check what actually ran

**Asking a runner for a model is not the same as getting one.** `pi --provider xai` is accepted, silently ignored, and answers from `openai-codex/gpt-5.5`. A roster can therefore claim three vendors, run two, and say nothing — which is worse than a short roster, because it is invisible in the verdict.

Where a reviewer's entry carries a `reports` block, read the model back out of the runner's own output and compare it against what you asked for:

```js
ranAs(stdout, reports)   // -> { provider, model, cost } | null
```

- **Mismatch** — report that reviewer as the vendor that *actually* answered, not the one you requested, and treat the requested vendor as unreachable. Do not silently accept the substitute; it is the collapse this check exists to catch.
- **`null` with a `reports` block** — the run did not report. Say so rather than assuming it went where you asked.
- **No `reports` block** — that runner cannot be verified. Name it as an unverified reviewer in the roster line, because a blind spot you have not named reads as a confirmed vendor.

`ranAs` also returns `cost`, which is worth reporting per reviewer when it is available.

### When a reviewer cannot be reached

Spawn the ones that resolve and **report the rest as unreachable.** Do not fill the gap with another tier of a vendor you already have.

That is not the same as slug rot, and the two must not share a remedy. A rotted slug is one renamed model inside a vendor you can still reach: read the valid slugs out of the error, take the closest equivalent in the same family, spawn it, and open a separate PR to fix the configured value. Substitution preserves the intent there.

An unreachable *vendor* is the opposite. This skill's entire premise is that the adversarial signal comes from model diversity, so replacing GPT and Grok with two more Claude tiers keeps the roster's shape while deleting the only thing it was for — and the run then looks like a three-vendor interrogation at a glance. State it plainly instead:

```
Reviewers: 2 of 3
  A  claude-opus-5   host
  B  gpt-5.6         runner (cursor-agent -> gpt-5.2)
  C  grok-4.6-fast   UNREACHABLE (xai)

Consensus below is 2-model across 2 vendors. Weight it accordingly.
```

Where only one vendor is reachable, say so above the verdict and say that this was not a cross-vendor run. Reachable means "something here can drive it", never "the provider is up" — a runner that exists can still fail at spawn time, and that is another degradation to report rather than a reason to substitute.

## 1. Determine scope

Identify what to review from context:

- If the user points at specific files or a diff, use that.
- If on a feature branch, diff against the base branch (`git diff main...HEAD`, or the branch the project actually merges into) for the full changeset.
- If the user's message references recent work, gather the relevant files.

Package the diff or file contents plus any surrounding context files the reviewers need to understand the code.

## 2. State the intent

Before spawning reviewers, state the intent explicitly. Derive it from the user's message, the commit messages, the PR description where one exists, and the code itself.

Write one clear paragraph. If you are unsure about the intent, ask the user before proceeding. Reviewers are told to assume the intent is correct and challenge only the execution, so a wrong intent paragraph wastes the whole run.

## 3. Spawn reviewers

Launch every reviewer in a single message so they run concurrently — `host` reviewers as `Agent` calls, `runner` reviewers as their `argv` with the prompt on stdin, all in that one message. Mixing the two mechanisms is normal; serialising them is not, since a roster of three costs three times the wall clock for nothing.

Each reviewer is read-only, never edits files, and is pinned to its own model from the roster. A reviewer that shares a model with another reviewer adds cost and no signal, which is the one thing this skill exists to avoid.

Build each prompt from [`references/reviewer-prompt.md`](references/reviewer-prompt.md), filling in:

1. The stated intent.
2. The diff or file contents.
3. The review rubric from [`references/rubric.md`](references/rubric.md).
4. The code-quality lens from [`references/code-quality-review.md`](references/code-quality-review.md).
5. The project context the reviewers cannot see, into `{PROJECT_CONTEXT}`: the repo's documented coding standards, and in a repo with an `APP_MAP.json`, its `invariants` and the `evolutionTraps` for the area. Each invariant has already caused a real bug here, and each trap is something that used to be true. A reviewer meeting the code cold cannot know either, and both are one paste. Leave the slot empty where the project documents none.

The same filled template goes to every reviewer, so every model applies the same rubric, the same code-quality lens, and the same project context. Paste the reference contents into the prompt rather than citing their paths: a reviewer on another vendor's model cannot read this repo.

## 4. Synthesize

As results come back, build a unified picture:

1. **Parse all findings** from the reviewers.
2. **Identify consensus.** Findings raised by two or more models independently are the highest signal.
3. **Identify lone-model findings.** Still worth reading, but weight accordingly.
4. **Deduplicate.** Different models may describe the same issue differently. Merge these and note which models raised it.
5. **Note disagreements.** Where one model flags something and another explicitly says the opposite, that is useful context for the verdict.

## 5. Lead judgment

You are the lead reviewer, a pragmatic senior engineer, not a neutral aggregator.

Read [`references/lead-judgment.md`](references/lead-judgment.md) for the full framework.

Categorize every finding into one of these buckets:

- **Act on.** Real issues affecting correctness, security, or maintainability given the actual goals. These would block a real PR.
- **Consider.** Legitimate points, but you are not sure they outweigh the cost of addressing them right now. Worth the user's attention.
- **Noted.** Technically valid but not actionable. Context-dependent, premature optimization, or low-impact given the current stage.
- **Dismissed.** Wrong, nitpicky, or missing context. Give a brief explanation why.

For each finding, include which models raised it, its category, and a one-line rationale for the categorization.

## Output format

Present the verdict in this structure:

### Intent
> The stated intent paragraph from step 2.

### Reviewers
One bullet per reviewer: label, model name, number of findings.

### Act on
Findings that should be addressed. For each: description, which models raised it, why it matters.

### Consider
Findings worth thinking about. For each: description, which models raised it, the tradeoff involved.

### Noted
Valid but low-priority. Brief list.

### Dismissed
Rejected findings with brief rationale.

### Agreement map
Where the models agreed, where they diverged, and what the pattern of agreement and disagreement tells us.
