# Explainer

The trace is done. This is how the answer gets written. It applies whether you write it yourself or hand it to a sub-agent.

## Lead with the model, not the tour

A file-by-file walkthrough makes the reader assemble the model themselves, and most readers stop before they finish. State the organising idea first, then show the path that proves it.

The test: if the reader stops after the first paragraph, do they still hold the one idea that makes the rest of this subsystem predictable? If not, the first paragraph is wrong.

## Say the shape, then the exceptions

Give the rule that covers most cases, then the cases it does not cover. Do not average the two into a hedge that describes neither. "Every write goes through the queue, except the migration path, which writes directly and is the reason the idempotency key exists" is a model. "Writes generally go through the queue" is not.

## Use the codebase's own words

Take terms from `CONTEXT.md`, the ADRs, and the type names. Do not coin a new word for a thing that already has one, and do not substitute a generic word ("service", "handler", "layer") for a specific one the code uses. Where the code's own name is actively misleading, say so once and then keep using it, because that is the name the reader will grep for.

## Keep the citations attached

Every hop carries its `file:line`. A reader who disbelieves you needs to be able to check in one click, and a reader six months from now needs to find the code after it moves.

## Do not upgrade uncertainty

Three things stay distinct and must not collapse into each other:

- What you read in the code.
- What you inferred from it.
- What you could not establish.

Mark the second as inference. State the third plainly and keep it in the output. A confident answer with a silent gap is worse than an honest one with a hole in it, because it costs the reader the debugging session that finds the hole.

## Diagrams

Draw one only where the shape is the point: a cycle, a fan-out, a state machine, an ordering constraint. A diagram of a straight line is worse than the line written as a list of hops. Keep it in text, and label every edge with what crosses it.

## Length

Long enough to hold the model, short enough to be read. Cut the tour before you cut the exceptions. If it is too long, the fix is fewer hops at higher altitude, not smaller words.

Write the final text through the `unslop` skill.
