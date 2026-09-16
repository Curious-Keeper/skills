---
name: create-verification-skill
description: "Generate a project-local verification skill that drives the app the way a user does, in any language, framework, or platform. Use when a project has no scripted way to prove UI, CLI, or service behavior, or when the user asks for a control skill for this repo."
disable-model-invocation: true
---

# Create a verification skill

Every serious project needs a scripted way to drive the real app and prove behavior: launch it, exercise a feature the way a user would, and capture evidence. This skill generates that as a project-local skill tailored to the repo. You write the generator's output for the next agent, not for a human. It will be read cold, mid-task, by an agent that has never seen the app.

## 1. Interview the repo, not the user

Answer these from the codebase and only ask the user what you cannot observe:

- **Surface.** What does a user actually touch? A web UI, a CLI or TUI, a desktop app, an API, a mobile app, a library? A repo can have several. Pick the primary one and note the rest.
- **Run.** How does the app start locally? Prefer the repo's own documented dev command, from package scripts, a Makefile, or the README quickstart. Note ports, env vars, seed data, auth.
- **Drive.** How can an agent interact with it programmatically? Existing harnesses first: browser-automation specs, expect scripts, PTY helpers, curl-able endpoints, a debug port. Only then pick a generic recipe, such as a browser driver for web and desktop shells, a PTY or terminal-multiplexer harness for CLI and TUI, or plain HTTP for services.
- **Observe.** What evidence can be captured? Screenshots, terminal transcripts, response bodies, logs, exit codes, database state.
- **Isolate.** Can two instances run side by side, on separate ports, data directories, or profiles? If not, say so in the generated skill. Refusing to double-drive a shared instance beats corrupting the user's session.

If the checkout does not build or start as-is, fix that first, or report it precisely, before generating. A skill written against a broken base teaches wrong steps. When an irrelevant missing asset blocks startup, such as a static directory the API never serves or a sample config, the generated skill may create it, clearly marked as verification scaffolding, and remove it in cleanup.

## 2. Generate the skill

**Where it goes.** The generated skill is project-local, so it belongs wherever this project already keeps agent skills. Look for an existing convention and match it: a `skills/` directory at the root, or an agent-specific one the project already commits. If the project keeps none, create `skills/verify-<app>/` and name that choice in your report.

Write `SKILL.md` at that path with YAML frontmatter, `name: verify-<app>` and a `description` naming the app, the surface, and when to reach for it. Without frontmatter the skill never registers. Ground every section in what the interview actually found, and leave no placeholders.

- **Launch.** The exact command that starts the app for verification, and how to tell it is ready: a log line, a port answering, a prompt. Include teardown. For a short-lived CLI or TUI there is no server to keep alive, so launch means build the binary or install dependencies once, then start each drive in its own isolated terminal session.
- **Doctor.** One read-only check that answers whether this instance is worth driving: process up, right version or build, port owned by us, auth valid. An agent runs this first whenever anything looks off.
- **Drive.** The harness recipe with real selectors and commands from this repo, not examples. Prefer stable handles such as ARIA labels, data attributes, prompt strings, and route paths over coordinates and tab order.
- **Evidence.** What to capture for a proof and where it goes. State the proof standards: exercise the real user path, not internal setters or test-only endpoints; capture the action and the resulting state, not just the final screen; verify side effects such as files written, rows inserted, and messages sent alongside what is visible; use mocks only where a production boundary already isolates the external system. When the safe path is a dry-run or test mode, verify what it actually skips by observing files, network, and version-control refs rather than trusting its name. Some dry-runs still touch the network or open a browser.
- **Cleanup.** How to tear down instances the run created. Never kill by process name. Kill what you started. Cleanup removes instances and scratch state, never the evidence: proof artifacts survive the teardown, in a location the skill names.
- **Helpers.** Any script the skill ships is executable and its invocation is shown in the skill body. A helper the reader has to reverse-engineer is not a helper.

## 3. Seed the feature map

Create a `features/` directory beside the generated `SKILL.md`, with a `README.md` index plus one file per user-facing feature you can identify. Aim for the top 3 to 5 to start, drawn from routes, commands, menus, or docs.

Follow the shape in [`references/feature-map-example/`](references/feature-map-example/). Each file answers, from the user's point of view, what the feature is, how to reach it, how to drive it with the harness, and what observable end state proves it works. The four H2s are `Sub-features`, `How to get to it (user POV)`, `Driving it with <harness>`, and `Gotchas`.

The map is the repo's maintained verification source. A proof that drives one convenient entry point is incomplete when the map lists others.

## 4. Prove the generated skill before handing it over

Run its own instructions end to end once: launch, doctor, drive one mapped feature, capture evidence, clean up. One feature is enough, since the map exists so later runs can cover the rest.

After cleanup, confirm the evidence still exists at the named location. A cleanup that eats the proof fails this step. Fix what fails, and run the generated cleanup after every failed iteration too, so broken attempts do not strand processes and ports. A generated skill that was never executed is a draft, not a deliverable.

## 5. Offer the maintenance loop

Point the user at `maintain-verification-skill` for keeping the map honest as the app changes. Suggest a cadence only if they ask.
