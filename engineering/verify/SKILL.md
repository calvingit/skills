---
name: verify
description: Verify acceptance criteria against observable results in an independent read-only context.
---

# Verify

Verify the current implementation against confirmed acceptance criteria. Check whether it works as required; code and design judgement belong to `code-review`.

1. Read the caller's scope, baseline, requirements, and relevant changes. Do not invent requirements or expand the task.
2. Run the smallest relevant checks using existing tests, builds, lint/type checks, runtime or interface checks. Do not add production code, test-only interfaces, or unnecessary new tests just to verify.
3. Return readable text/Markdown: for each acceptance criterion, explain whether it passed, failed, or could not be checked, with observed evidence. Record actual commands, exit codes, and key output. Identify the ticket/attempt when supplied. No JSON response schema is required.

Reading code and an implementation agent's self-report do not replace execution evidence. Keep failed and unverified checks explicit, including what would allow them to run. Loop decides the next ticket state from these results; verification does not schedule other agents or change the graph.

Do not edit code, requirements, tickets, Git history, or external business state. Put isolated test caches and temporary outputs only in locations the caller permits, normally `.loop/tmp/`. Never claim commands ran when they did not.
