---
name: navigator
description: Chart a large effort as owed decisions in a project's APP_MAP.json and settle them one at a time until the work is dispatchable. Use when a chunk of work is too big for one session and the route to it is not visible yet.
disable-model-invocation: true
---

A loose idea has arrived, too big for one agent session, and wrapped in fog: the way from here to the **destination** is not visible yet. Navigating is about finding that way, not charging at the destination. This skill charts the way across two files the project already keeps, then works its **decision tickets**, questions whose resolution is a decision rather than slices of a build, one at a time until the route is clear.

## The destination is a dispatchable backlog

The effort ends where the sprint harness begins. The map is done when every decision is settled and the work that follows exists as `plannedWork.backlog` items (and `openDebt` entries where a session has read the repo) that `extract-queue.mjs` can walk into `QUEUE.json`. Navigator plans; the harness builds.

```
navigator                         sprint-harness
---------                         --------------
decisionsOwed  ---- settle ---->  decisionsSettled   (never dispatchable)
      |
      +--------- raise --------->  plannedWork.backlog  --> extract-queue --> builders
```

An effort may name a different destination in its **Notes**: a spec to hand off, a decision to lock, a migration made in place. Absent that, produce decisions and a backlog, not deliverables. The pull to just do the work is the signal you have reached the edge of the map and it is time to hand off.

## Where the map lives

Two files, and the split is the index/store split:

- **`docs/app-maps/APP_MAP.json`** stores the tickets. A ticket is one entry in `plannedWork.decisionsOwed`, which is `NEVER_DISPATCHABLE`, so a ticket can never reach a builder. The `appmap-board` DECIDE lane is therefore the effort's ticket view for free, and `bin/appmap` is how a human sees it without opening anything.
- **`docs/app-maps/efforts/<slug>.md`** holds the effort itself: destination, notes, the blocking graph, the fog, what was ruled out. Loaded once per session; it is the low-resolution view.

A decision lives in exactly one place, its ticket in the map, so the effort doc never restates one, only gists it and names its id.

Read **`docs/MAP_GUIDE.md`** from the [`sprint-harness`](https://github.com/Curious-Keeper/sprint-harness) kit before writing anything into a map. Use a local checkout if there is one, otherwise fetch it from the repo. It is the writing standard, and it is where the rules for `openDebt` evidence and `plannedWork` prose live.

### The effort doc

```markdown
# <effort name>

charted YYYY-MM-DD · map `docs/app-maps/APP_MAP.json`

## Destination

<what reaching the end of this effort looks like. One or two lines; every session
orients to it before choosing a ticket.>

## Notes

<domain; skills every session should call; standing preferences for this effort;
a different destination, if this effort overrides the default>

## Route

<!-- the blocking graph. A ticket is UNBLOCKED when every ticket blocking it is
     settled. The FRONTIER is the open, unblocked, unclaimed rows. -->

| ticket | title | type | blocked by | claimed |
|---|---|---|---|---|
| dec-4 | Where session state lives | designing | none | none |
| dec-5 | Whether Okta supports the SCIM shape we need | research | dec-4 | brian |

## Decisions so far

<!-- the index: one line per settled ticket, enough to judge relevance. The answer
     itself is in decisionsSettled, under the same id. -->

- **dec-3** Sessions are server-side, keyed by an opaque cookie.

## Not yet specified

<!-- fog: in-scope, not yet sharp enough to ticket. Graduates as the frontier advances. -->

## Out of scope

<!-- ruled beyond the destination; never graduates -->
```

The Route table is the only place blocking is recorded. `decisionsOwed` has no dependency field, and inventing one would change the skeleton and the board's rendering. The cost is real and worth naming: the board's DECIDE lane shows every open ticket, blocked or not, so the board tells you what is owed and the Route table tells you what is takeable.

### The ticket

One entry in `plannedWork.decisionsOwed.items`, in the shape the maps already use:

```json
{
  "id": "dec-4",
  "decision": "Where session state lives. <the question, stated so a reader who has not been on the calls can answer it>",
  "ref": "efforts/sso-launch.md"
}
```

- **The id comes from the map's own naming.** Read the stems already in `decisionsOwed`, so a map naming its decisions `L#3` gets `L#4` and not a stray `dec-1`. Check the result against **every id in the map**, not just this section's. The extractor exits 1 on a duplicate wherever its twin lives.
- **`ref` names the effort doc**, so a ticket read cold on the board leads back to the route.
- **The answer is not in the body.** It is written on settlement, into `decisionsSettled`.
- **Size each ticket to one session.** A question that needs two sessions is two tickets or a patch of fog.

### Refer by name

Lead with the ticket's title in everything a human reads: narration, the Decisions-so-far index, the Route table. A wall of `dec-4, dec-5, dec-6` is illegible. The id rides alongside the name, never in place of it, because the id is what `board._link` resolves and what later prose cites.

## Ticket types

Every ticket is either **HITL**, worked *with* a human who speaks for themselves, or **AFK**, driven by the agent alone. A HITL ticket resolves only through that live exchange; standing in for the human's side of it breaks the type.

| type | mode | how it resolves |
|---|---|---|
| `designing` | HITL | Conversation. **The default.** Call the Skill tool twice, for `designing` and `domain-modeling`. |
| `research` | AFK | A fact the decision waits on, living outside the working directory. Call the Skill tool for `research`. |
| `prototype` | HITL | A cheap, rough, concrete artifact to react to. Call the Skill tool for `prototype`. Use when "how should it look" or "how should it behave" is the question. |
| `task` | either | Manual work that must happen before a decision *can* be made: provisioning access, signing up so an API can be judged, moving data so its shape can be seen. Nothing to decide. The discussion is blocked until it is done. |

`task` is the one type that *does* rather than decides, and it earns its place by unblocking a decision, not by delivering the destination. Drive it alone where you can; otherwise hand the human a precise checklist. Its answer records what was done and any facts later tickets depend on: where credentials landed, new URLs, row counts.

## Fog of war

The map is *deliberately* incomplete: chart only what you can see. Beyond the live tickets lies the **fog**, the decisions you can tell are coming but cannot yet pin down, because they hang on questions still open. Settling a ticket clears the fog ahead of it, graduating whatever is now specifiable into fresh tickets, one at a time, until the route is clear.

**Not yet specified** is where that dim view is written down. The test is whether you can state the question precisely *now*, not whether you can answer it now.

- **Ticket** when the question is already sharp, even if it is blocked.
- **Not yet specified** when you cannot yet phrase it that sharply. One patch may graduate into several tickets, or none; leave it coarser than a ticket rather than pre-slicing the fog.

**Not yet specified** excludes what is already settled, already a live ticket, or out of scope.

## Out of scope

Fog gathers only *toward* the destination. Work past the destination is **out of scope**: scope, not sharpness, lands it there. It never graduates, and it returns only if the destination is redrawn, and then as a fresh effort.

When a ticket already in `decisionsOwed` turns out to sit past the destination, **settle it with `state: blocked-external` is wrong**. That state means real, unanswered and waiting on an outside party. Instead move it to `decisionsSettled` with `state: resolved` and an answer that says it was ruled out of this effort and why, and leave one line under **Out of scope** naming its id. It stays out of **Decisions so far**, which records the route actually walked; a scope boundary is not a step on it.

Settled entries keep their ids for the same reason `decisionsSettled` exists at all: prose elsewhere cites them, and `board._link` resolves those mentions.

## Chart the map

The user invokes with a loose idea, in a project that already has an `APP_MAP.json`.

1. **Read the map first.** `invariants`, `evolutionTraps`, `coverageGaps`, `acceptedRisks`, and the open `decisionsOwed`. A ticket that re-asks what the map already answers is the most common way this wastes a session. Run `bin/appmap` or read the JSON; both are fine.
2. **Name the destination.** Call the Skill tool twice, for `designing` and `domain-modeling`. The destination fixes the scope, so it is settled first. State plainly what handing off to the harness will look like for this effort.
3. **Map the frontier.** Design again, **breadth-first** this time: fan across the whole space rather than deep on one thread, surfacing the open decisions and the first steps takeable now. **If this surfaces no fog**, meaning the route is already clear and the whole journey fits one session, you do not need an effort doc. Stop and ask the user how they want to proceed.
4. **Write `docs/app-maps/efforts/<slug>.md`**: Destination and Notes filled in, Route empty, Decisions-so-far empty, the fog sketched into **Not yet specified**.
5. **Append the tickets** you can specify now to `plannedWork.decisionsOwed`, then fill in the Route table's blocking column in a second pass. Ids have to exist before they can reference each other. Wiring sorts the tickets into the frontier and the blocked; everything you cannot yet specify stays in the fog.
6. **Commit both files in one commit.** The map must be committed: worktrees materialize only tracked files, `preflight.sh` checks it, and the board keeps saying the map is uncommitted until it is. Never commit to `main`. Branch first.
7. **Fire the research tickets.** For each `research` ticket you just created, call the Skill tool for `research` so they resolve in parallel while you stop.
8. Stop. Charting is one session's work; it settles nothing by hand.

## Work through the map

The user invokes with an effort slug. A ticket is **optional**: without one, you pick the next decision, not the user.

1. **Load the effort doc**, which is the low-resolution view, and the open `decisionsOwed` entries it names. Not every ticket body.
2. **Choose the ticket.** If the user named one, use it. Otherwise take the first frontier row in the Route table. **Claim it** by writing the claim into the Route table's `claimed` column and committing, before any work, so a concurrent session skips it.
3. **Resolve it.** Zoom as needed: read any settled ticket's answer in `decisionsSettled`, any `openDebt` entry, any doc the map cites. Call the Skill tool for whichever skills the ticket's type and the effort's `## Notes` name. In doubt, call `designing` and `domain-modeling`.
4. **Settle it.** Move the entry from `decisionsOwed` to `decisionsSettled`, **keeping its id**, with `state: resolved` and the answer written into its text. `bin/appmap`'s `a` key does exactly this move and shows the diff before it writes; either path is fine, and both must leave the entry gone from `decisionsOwed`. An answered question left there inflates the pending count and hides the one real decision.
5. **Raise the work the answer unlocks**, as its own visible act. Settling changes nothing about what gets built: `decisionsOwed`, `decisionsSettled`, `externalState.*` and `shipped` are all `NEVER_DISPATCHABLE`. Work reaches a sprint only as a fresh `plannedWork.backlog` item carrying the decision's id as `ref`, with a fresh `n` and never the decision's own id, because the extractor exits 1 on a queue item bearing a never-dispatchable id and carries `ref` as an inert `mapNote` instead.
6. **Update the effort doc**: one gist line under Decisions so far, the Route row struck, new tickets created and wired, and every fog patch the answer made specifiable graduated into a ticket and **cleared from Not yet specified** so it lives in exactly one place. If the answer reveals a ticket sits past the destination, rule it out of scope. If it invalidates other tickets, settle or delete them.
7. **Commit map and effort doc together**, and say so. Then stop: **one ticket per session**, research excepted.

## Guards you inherit

Every one of these is a scar in `sprint-harness/docs/SCARS.md` or a fence in `appmap-board`. They bind navigator the same way they bind the board:

- **A backlog item's prose becomes a file set.** `citedFiles` scrapes path-shaped tokens out of a `plannedWork.backlog` item's text and unions them into what it claims, so a path mentioned in passing manufactures a false collision edge and serialises two unrelated items. Before raising a backlog item, list every path-shaped token in the text you are about to write and remove the ones you do not intend to edit. `writeback.cited_paths` does this for the human at the board; do it by hand here.
- **`decisionsOwed` prose is inert**, because it is never walked. Say what you mean there, paths and all.
- **Debt needs a repo read.** An `openDebt` entry carries `file:line` evidence and a mechanism. Raise one only from a session that has actually verified the citation says what it claims, and follow MAP_GUIDE for the four fields. A decision's answer alone never justifies one.
- **Intake is claims, not facts.** `docs/app-maps/INTAKE.md` holds what came off calls and mail; nothing in it has read the repo. It is a fine source for charting a destination and for fog. Promoting one into a ticket is `bin/appmap`'s `p`, and its targets are exactly `decisionsOwed`, `externalState.open` and `plannedWork.backlog`.
- **Waiting on an outside party is `externalState.open`, not a ticket.** A question no amount of reasoning here settles is not a decision anybody owes; it is external state, and the board resolves it into `confirmedDone` when the answer comes back.
- **Closing is two edits and the second gets skipped.** Whatever you settle, move it; whatever you ship, move it out of `openDebt`. Do the move in the same edit, before the context is gone.

## When the project has no map yet

Navigator is the **mapped** effort: it assumes an `APP_MAP.json`, because a ticket has nowhere to live without one. The **unmapped** effort is `designing`. Call the Skill tool for it and work the design tree in rounds, with no effort doc and no tickets. Say which one you are in before charting anything.

Where the unmapped effort's destination turns out to *be* a working system, call the Skill tool for `tracer`: it orders the work into vertical slices, builds them one at a time, and stops when there is enough system to map. The route from there is already charted. **`templates/prompts/README.md`** in the [`sprint-harness`](https://github.com/Curious-Keeper/sprint-harness) kit picks the track, and prompts `00` and `01` build the map. Navigator picks up after that.

Inside a mapped effort, `designing` stays the interview primitive this skill calls at steps 2, 3 and 5. One skill, two roles, and the difference is whether there is a map to write tickets into.
