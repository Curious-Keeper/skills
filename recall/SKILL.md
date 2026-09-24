---
name: recall
description: "Reconstruct recent working context from your own chat history, live state, and the shared record of user reports, prior fixes, and incidents, then hand back a tight current-state brief. Use when the user asks to be caught up, asks what they have been working on or where they left off, or before starting or resuming work on a named topic."
disable-model-invocation: true
---

# Recall

**Before you start or resume work, you rebuild the user's recent working context and hand back a tight capsule of where things stand now and what to do next.**

Keep it tight and on-topic. Read only what the in-scope threads need, then stop.

Your context lives in two records. Your own chat history holds what you did and decided. The shared record holds everything that happened around the same code under other names: the symptoms users keep reporting, the fixes that shipped and got reverted, the errors still firing in prod. A feature with a long bug tail keeps most of its story in that second record, so do not reconstruct it from your transcripts alone.

## Finding the transcripts

Transcripts live in the agent host's per-project state directory: one file per chat, one JSON object per line, one line per message.

Locate that directory rather than assuming a layout. The common shape is a per-host dotfile directory holding `projects/<slug>/`, where `<slug>` is the workspace path with each `/` turned into `-`. Hosts disagree on the leading separator, some dropping it and some keeping it as a leading `-`, so glob for the slug instead of constructing the path. Confirm you have the right directory by checking a file's modification time against work you remember.

## 1. Classify, then route

Recall loads working context across recent chats before you act. These are different tasks:

- Resuming one specific prior chat that the user names.
- Compacting the current conversation for another agent, which is `handoff`.
- Turning a recurring habit into a durable skill, which is `writing-for-agents`.
- Writing a human-readable summary of your work for a person to read.

If the user already gave you a full state capsule, with paths, branch, and the change, use it and skip the mining.

## 2. Lock the scope before searching

Pin the window, since "recent" is a real range and defaults to the last 7 days. Pin the topic if one is named. Pin the workspace, defaulting to the active one, and never read another project's transcripts without being asked.

State the scope back. Never quietly turn "all" into "recent N".

## 3. Fan out across your chat history

Spawn parallel sub-agents on a fast, cheap model, each taking a slice of the corpus. Tell every sub-agent to:

- Order candidates by real modification time (`ls -t`), never by file name.
- Grep the topic first, then read only the matching chats, and only their relevant regions.
- Skip the current chat and obvious noise, meaning sub-agent, eval, and test chats.

Each returns the same schema, one block per chat: topic, the user's goal, decisions, open threads, struggles and corrections, and artifacts such as PRs, tickets, and branches. Every block cites its chat id.

For one or two chats, skip the fan-out and search directly. The raw transcripts stay in the sub-agents. The main thread gets only their findings.

## 4. Sweep the shared record

Do this whenever the topic names a feature, file, subsystem, area, or bug. It is the default, not a judgment call, and "my work on X" does not exempt it.

Run the sweep in parallel with the chat-history mining, one investigator per source:

- **Source control.** `git log` and `git blame` on the paths, plus merged, closed, and reverted pull requests touching them.
- **Issue tracker.** Open and recently closed issues naming the feature, and the ones that keep getting reopened.
- **Chat and issue channels.** Where the symptom gets reported in the user's own words.
- **Long-form docs.** ADRs, `CONTEXT.md`, and in a repo with an `APP_MAP.json`, its `decisionsSettled`, `invariants`, and `evolutionTraps`.
- **Error tracking.** What is still firing, at what rate, since which release.

Steer every investigator to the same question: what is the current state, what has been tried and did not hold, and what are users still reporting. That is a different question from why the code was built this way.

A null result is a finding, so report it. A source you cannot reach is skipped and said out loud, never silently dropped.

Skip this whole step only for pure activity recall with no named target, such as "what did I do this week", where your own history and live state are the entire answer.

## 5. Verify against live state

Take the PRs, branches, and tickets the mining and the sweep surfaced, and check them with `git`, and with the forge's CLI where the project has one. A branch that is merged, abandoned, or three weeks stale changes the brief.

When the answer hinges on what an agent actually did, meaning the tools it ran, the files it read, and the errors it hit, read the full transcript rather than a trimmed local copy.

## 6. Write the brief

Group by thread. Stay on the named topic.

## Output contract

Lead with the capsule, then the thread status, then the problems, then the next move. Deeper detail goes below or gets cut.

- **Capsule.** Readable at a glance. What this work is and where it stands overall.
- **Threads.** One line each, prefixed with exactly one status tag: `[merged #N]`, `[open PR #N]`, `[in flight <branch>]`, `[verified, uncommitted]`, `[reverted #N]`, or `[planned, not started]`. A thread with no tag is not done yet, so tag it.
- **Problems.** The recurring ones. Include the symptoms users keep reporting and any fix that shipped and was reverted, so the next attempt starts where the last one failed.
- **Next move.** The single most useful next action, concrete.

An adjacent feature or ticket stays out unless it blocks this one. When the capsule and thread lines outgrow a screen, cut detail before you cut threads.

Write the brief through the `unslop` skill. Cite chat findings by chat id and shared-record findings by their source, meaning a PR number, ticket id, chat permalink, or error-tracker issue. Sanitize private context before any public output.

**Reply:** the brief, to the contract above.
