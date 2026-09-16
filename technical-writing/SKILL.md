---
name: technical-writing
description: "Layered standard for prose a human reads: Diátaxis for what kind of document this is, Google developer style for voice, Simplified Technical English for instructions, and Global English for syntax. Use when writing or reviewing docs, READMEs, RFCs, ADRs, release notes, PR descriptions, or commit messages."
---

# Technical writing

**Four layers, applied in order.** Each one answers a question the next one cannot.

1. **Diátaxis** decides what kind of document this is, and therefore what belongs in it.
2. **Google developer style** decides the voice and the sentence.
3. **Simplified Technical English** decides how an instruction is written.
4. **Global English** decides the syntax, so a non-native reader and a machine translator both parse it once.

This is not `unslop`, which strips AI tells from any prose and runs last, over whatever this produces. It is not `writing-for-agents`, which is for documents an *agent* consumes, where the levers are different because the reader takes a process rather than absorbing an idea. This skill is for prose a **human** reads.

## Layer 1: Diátaxis decides the kind

Four kinds. Each serves a different reader in a different state, and mixing two in one document is the most common way technical writing fails.

| Kind | The reader is | Gives them | Fails when |
|---|---|---|---|
| **Tutorial** | learning by doing | a guaranteed-success first path | it explains, or offers choices |
| **How-to** | working, with a goal | the steps for one real task | it teaches, or covers every case |
| **Reference** | looking something up | complete, dry description | it advises, or tells a story |
| **Explanation** | trying to understand | context and the why | it instructs |

Name the kind before the first sentence. Where a document needs two kinds, that is two documents and a link between them, not two halves.

The failure modes are specific. A tutorial that stops to explain loses the reader who wanted to get something running. A reference that advises cannot be scanned, because advice has to be read to be skipped. An explanation with steps in it will be followed instead of understood.

Two kinds already have a format in this repo, and the `domain-modeling` skill owns both. An architectural decision is explanation and follows its `ADR-FORMAT.md`. A subsystem's vocabulary is reference and follows its `CONTEXT-FORMAT.md`. Call the Skill tool for `domain-modeling` and use those rather than inventing a shape.

## Layer 2: Google developer style decides the voice

- **Second person, present tense, active voice.** "Run the migration", not "the migration should be run" and not "we will now run".
- **Describe what the reader does, not what the product lets them do.** "Set `retries` to 3", not "the API allows you to configure retries".
- **Cut the difficulty adverbs.** No "simply", "just", "easy", "obviously", "of course". They are only ever right when the reader already succeeded, and insulting when they did not.
- **Sentence case for every heading.** Headings state the reader's task or question, not a noun category. "Configure the queue" beats "Queue configuration".
- **Code voice for anything literal.** File names, flags, values, types, commands. Never for a concept, and never for emphasis.
- **Descriptive link text.** The link says where it goes. Never "here", "this", or a bare URL.
- **Serial comma.** Every list, every time.
- **One idea per sentence.** A sentence with two clauses joined by "and" is usually two sentences, and splitting it usually shortens it.
- **Define on first use, then stop.** Expand an abbreviation once, then use it. Do not re-explain a term the reader has already met.

## Layer 3: Simplified Technical English decides the instruction

Instructions are the part readers follow under pressure, so they get the tightest rules.

- **One action per step.** Two actions is two steps, even when they are one keystroke apart.
- **Imperative mood, verb first.** "Open the config file." Not "the config file should now be opened" and not "you will want to open".
- **Condition before action, in the same sentence.** "If the build fails, clear the cache." The reader must not execute half a step before learning it did not apply to them.
- **Cap the length.** Roughly 20 words for an instruction, 25 for a descriptive sentence. Over that, the step is doing two things.
- **One topic per paragraph.** A paragraph that needs two topic sentences is two paragraphs.
- **One meaning per word.** Pick one verb for each action and keep it. Do not alternate "remove", "delete", and "drop" for the same operation, and never use "run" for both executing a command and operating a service.
- **Say what happens next.** A step whose result is invisible needs the expected outcome attached, or the reader cannot tell whether it worked.
- **Warnings before the step, never after.** A caution below the instruction is read after the damage.

## Layer 4: Global English decides the syntax

Written for a reader whose first language is not English, and for a machine translating it. Both break on the same constructions.

- **Keep subject, verb, and object together.** Do not separate them with a clause.
- **Do not drop "that" or "which".** "The file the script writes" is ambiguous; "the file that the script writes" is not.
- **No ambiguous pronouns.** Where "it", "this", or "they" could attach to two nouns, repeat the noun. This is the single highest-yield edit in most technical prose.
- **At most two nouns in a row.** "Queue configuration validation failure handler" is not a phrase. Unpack it with prepositions.
- **Avoid phrasal verbs where a single verb exists.** "Submit", not "send in". "Cancel", not "call off".
- **No idioms, no metaphors, no humour that depends on a culture.** "Out of the box" and "low-hanging fruit" do not translate and do not need to.
- **Avoid strings of -ing words.** "Using the running config, starting the service" parses three ways.
- **Positive over negative, and never two negatives.** "Wait until the build finishes" beats "do not proceed unless the build is not still running".

## Common documents

- **Commit messages.** Conventional Commits, imperative subject under 72 characters, no trailing period. The body says why, not what, because the diff already says what. Wrap at 72.
- **PR descriptions.** A briefing, not a changelog. What changed, why now, how a reviewer verifies it, what you deliberately left out. Where the repo runs the sprint harness, name the anchors that passed rather than asserting it works.
- **READMEs.** What this is, in one sentence a stranger understands. Then how to run it. Then where to go next. A README that opens with architecture is an explanation wearing a README's name.
- **Release notes.** Reader-facing change first, mechanism second, and only where the mechanism changes what they do.
- **Issues and debt entries.** Symptom, the evidence that shows it, and the mechanism if known. In a repo with a `docs/app-maps/APP_MAP.json`, an `openDebt` entry's `evidence` is reference-kind writing and carries a real `file:line`, not a description of one.

## Reviewing rather than writing

When the task is reviewing someone else's prose, report against the layers in order and stop at the first one that is wrong. A document in the wrong Diátaxis kind cannot be fixed by sentence edits, and copy-editing it first wastes the pass. Say which layer failed, quote one example, and name the kind it should be.

## Finish

Run the result through the `unslop` skill last. This skill decides the structure and the sentence; `unslop` removes what makes it read as machine-written. Doing it in the other order re-introduces what you just cut.
