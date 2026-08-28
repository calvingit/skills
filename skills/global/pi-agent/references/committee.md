# Committee

Use two or more independent Pi sessions when multiple model perspectives materially improve a difficult review or plan.

## First round

- Give every member exactly the same dossier.
- Give each member a separate member directory and JSONL session.
- Do not include the primary agent's findings in the first-round dossier.
- Default to serial execution. Start the next member only after the previous Pi process exits.
- Use parallel host execution only when the selected providers and accounts are confirmed to have no applicable concurrency or requests-per-minute limit.

Parallel mode means multiple independent foreground shell/PTTY calls managed by the host agent. It does not require a daemon or orchestration server.

## Synthesis

Preserve each member result and error separately, then report:

- `completed`: every member produced a valid report and session;
- `partial`: at least one succeeded and at least one failed;
- `failed`: no member produced a usable result.

The primary agent verifies claims and groups them as:

- `agreed`;
- `main-only`;
- `pi-only`;
- `unresolved`.

Model votes are not evidence. Correlated agreement can still repeat the same unsupported assumption.

When challenging a finding, resume only the exact session of the member that produced it. Do not broadcast the primary agent's rebuttal to unrelated members unless a new independent round is explicitly requested.
