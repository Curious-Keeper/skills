---
name: blast-radius
description: "Find what a change could break somewhere else, beyond the diff, and prove the one fact it is safe because of by running real code instead of writing it up. Use when the user asks what a change could break, wants the blast radius of a change assessed, or has a small-looking diff they do not trust yet."
disable-model-invocation: true
---

# Blast radius

**Find what a change breaks somewhere else, before it ships.** The answer is only worth having if the fact it rests on was proven by running code.

Listing the callers is not the job. Any agent can grep those in a second. The job is the breakage grep will not show you.

This is not `code-review`, which judges a diff against the repo's documented standards, spec, and invariants. It is not `interrogate`, which throws several models at the diff itself. Both look *at* the change. This one looks at everything the change reaches.

## Do not trust your own writeup

A blast-radius writeup that sounds right is worthless. It reads as convincing whether or not it is true, and the more fluent it is the more expensive the mistake. So the deliverable is not the writeup. It is the one or two facts the whole thing depends on, proven.

### How sure are you

For each fact the change's safety depends on, get it as far down this ladder as is cheap, and say where it stopped.

1. **You said so.** Worthless on its own.
2. **You pointed at the line.** A real `file:line`, in this repo or in the dependency's own source.
3. **You showed the bad case cannot happen.** You walked the failure step by step and it does not reach.
4. **You ran it.** A script or test that calls the real code and fails loud if you are wrong.
5. **You reproduced it in the running app.**

Rung 4 is usually one small script that imports the same version of the library the app ships and calls the exact function you are worried about. That is minutes of work, so the bar is rung 4 unless you can say concretely why it is expensive here.

Any safety fact you cannot get to rung 4, label **unproven** and leave labelled. Do not write it up as settled.

## 1. Read the change

The diff, the symbols it adds, changes, and deletes, and what the code now does differently. Include the part the diff does not spell out: the behaviour that moved without the line moving, the default that changed, the call that is now reached on a path it was not reached on before.

Where the change has a spec, read it. In a repo with a `docs/app-maps/APP_MAP.json`, an item id in the commit messages resolves to an `openDebt` or `plannedWork.backlog` entry, and that entry's `fix` states the shape the change was meant to take. A diff that reaches further than its `fix` described is itself a finding.

## 2. Load what this repo has already been burned by

Read `invariants.items` and `evolutionTraps.items` from the map for the area the change touches. Every invariant is a rule that has already caused a real bug here, and every trap is something that used to be true. This is the cheapest blast-radius signal in the repo and it is one read.

For each invariant that the change could plausibly reach, that is a candidate risk, and its `enforcedBy` tells you whether anything would catch it. An invariant whose `enforcedBy` is prose rather than a command is the one to worry about.

## 3. Find the one fact it is safe because of

Most changes that look risky are safe because of a single fact. "This call only drops cache entries that are already dead, and does nothing else." "This field is written in one place and that place runs before any reader exists."

Find that fact and name it. If it holds, most of the risky cases clear at once. Spend your time here rather than on a long list of maybes, because a long list of maybes is what this skill exists to avoid producing.

## 4. Look where grep stops

A symbol search covers the easy half. Work the other half deliberately:

- **The dependency's real source.** Read it, at the version the lockfile pins, plus any local patch. What the docs say and what the shipped code does are different objects.
- **When things run.** Microtask versus macrotask, mount versus effect versus teardown, transaction boundaries, retries, what happens on the second call.
- **Data that crosses a wall.** The JSON an API returns, a database column, a cache key, a queue payload, a wire format, a generated file, another language reading the same bytes.
- **Indirection a search cannot follow.** A string key, a route table, dependency injection, an event name, a feature flag, reflection.
- **Three hops downstream.** The caller's caller's caller, where the change alters something the immediate caller does not care about but a distant one does.

## 5. Be honest about each risk

Give every risk a real chance of happening and a real cost if it does. Keep the ones you confirmed. List what you checked and cleared separately, because "I looked and it is fine" is information and deleting it means the next person looks again.

Cite a real `file:line` for every risk. A search that finds nothing is still an answer, so report it as one. Never invent a caller or an API.

## 6. Prove it

Write the script or test that runs the real code, run it, and paste what happened. Not what you expect to happen.

Where the risk is durable rather than specific to this diff, the proof should not be a one-off. The project's anchors in `.claude/harness.config.json` are the commands it trusts, and a proof worth keeping belongs there as a new anchor, or as an `enforcedBy` command on an invariant. Propose that; do not add it as a side effect of answering the question.

If the change is wide enough that one reading will miss something, run the diff through `interrogate` as well and fold its consensus findings in here. Different models catch different real bugs.

## 7. Feed what you learned back to the map

A risk you confirmed and fixed is a bug this repo has now been burned by, which is the bar for `invariants.items`. Offer the entry, shaped as the map wants it: `rule`, `failureMode`, and `enforcedBy` naming the command from step 6 that catches it.

An assumption you found to be stale belongs in `evolutionTraps.items`. A risk you confirmed but chose not to fix belongs in `openDebt` with its `evidence` and `mechanism`, not in a paragraph of chat that scrolls away.

Offer these as edits and let the user take them. Do not write to the map as a side effect.

## Output contract

- **What it does.** What changed, including the part that is not obvious from the diff.
- **The one fact it is safe because of.** State it, say which rung of the ladder you got it to, and show the proof. If you could not prove it, write **unproven** and leave it there.
- **Risks.** Only the real ones. Each names how it breaks, a real `file:line`, how likely, how bad, and how to check. Paste the proof for the ones that matter.
- **Cleared.** What you checked and why it is fine, including the searches that found nothing.
- **Before you merge.** The cheapest test or repro that catches the real bug, including the script you wrote.
- **Map edits offered.** Any invariant, trap, anchor, or debt entry step 7 turned up, ready for the user to accept.

Write it through the `unslop` skill, cite real code, and strip anything private before it leaves the repo.

**Reply:** the writeup above, with the one safety fact either proven or marked unproven.
