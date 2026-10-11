# Close-out roles

Shared rules for the three independent close-out judgements used by `quick-implement` and `loop`. Role separation and evidence consumption live here; worker creation, waiting, and context assignment belong to Runtime. Workflow-specific sequencing (receipts, delivery-prepare, correction closeout, broaden triggers) stays in each caller.

Whether to select roles by risk instead of running all three is a separate behaviour decision; both callers currently require all three on initial closeout.

## Simplification

Dispatch a dedicated native sub-agent that loads `simplify` (Call the Skill tool with "simplify", or pass its resolved `SKILL.md`) in Review mode on the implemented / final change set. Consume its report. Record `no_change` when it finds no supported candidate. Apply candidates only when the user explicitly authorized simplification; otherwise report them. This role is separate from verification and review. No conclusion does not mean no simplification was needed.

## Verification

Dispatch a dedicated native `verify` sub-agent, separate from `simplify` and `code-review` (Call the Skill tool with "verify", or pass its resolved `SKILL.md`). Check every applicable confirmed Acceptance Criterion and the project's existing delivery gates for the affected range, including any required standard PR, CI, or full gate. Pass the baseline, pre-existing edits, confirmed requirements and AC, implemented scope, and local check records. Read its per-criterion `PASS`, `FAIL`, or `NOT VERIFIED` report before deciding completion.

Reuse results that are still valid on the current code. Do not re-run a check already covered by the standard gate. Re-run only after a later edit, a failure, or a new risk. When a full test, build, or end-to-end check is unavailable or clearly out of proportion, record why, substitute evidence, unverified scope, and risk.

The `verify` sub-agent follows the task's project verification entry, `verification_instructions` when configured, or existing local verification skills/docs/scripts. Setup is not a prerequisite; use existing checks and report any capability gap. Follow documented isolation, evidence and cleanup rules. Record exit code and key output for every command actually run. A tool succeeding proves only that gate. It does not automatically prove the requirement is complete. Ticket-local AC IDs are not automatically SPEC AC IDs.

## Review

After verification (or after the caller's prescribed order), spawn a dedicated native `code-review` sub-agent, separate from the `simplify` and `verify` sub-agents (Call the Skill tool with "code-review", or pass its resolved `SKILL.md`). Consume its actual Markdown report; a main-agent self-check does not satisfy this gate. Pass baseline, pre-existing edits, SPEC, HLD when present, the scope actually implemented, the simplification and verification reports, and the actual command records. Pass a separate `ACCEPTANCE.md` when it exists. After required fixes, re-run affected verification and review in separate sub-agents.

Use one reviewer by default. Only for high-impact changes with unresolved, under-evidenced judgements, or an explicit user request for a panel, may the caller dispatch 2–3 independent reviewers on the same scope and synthesize their findings against the evidence.

Use code-review's [report guidance](../code-review/references/output-contract.md) and reference or retain its original report; the receipt does not define another review taxonomy.

## Independence

Missing required simplify, verify, or code-review results leave close-out incomplete. Do not infer a pass from local checks. Any authorised substitution must preserve its authority, executor, and coverage evidence. A dispatched worker existing is not proof its role judgement ran.
