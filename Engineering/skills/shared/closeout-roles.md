# Close-out roles

Shared rules for the three independent close-out judgements used by `quick-implement` and `graph-workflow`. Role separation and evidence consumption live here; worker creation, waiting, and context assignment belong to Runtime. Workflow-specific sequencing (receipts, delivery-prepare, correction closeout, broaden triggers) stays in each caller. Initial close-out selects its roles under [Role selection by risk](#role-selection-by-risk) (owner-approved 2026-10-24); the full tier remains the default.

## Role selection by risk

Initial close-out selects its roles from blast-radius facts of the confirmed contract, not from size labels or line counts. Record the selected tier and its basis in the close-out receipt; an omitted role is recorded as not run, never as passed.

- **Full** (default): `simplify` (Review mode), `verify` and `code-review`.
- **Verify-review**: `verify` + `code-review`; omit `simplify` when the change introduces no new abstraction, compatibility path, extension point or shared contract.
- **Verify-only**: `verify` alone, for a single-scope behaviour fix with no public-contract, cross-module, security, permission, data or migration surface and sufficient existing checks.

`verify` is never omitted. A user request, a project gate, or a high-impact fact (shared contract, cross-module impact, security/permission/data/migration surface, wide blast radius) requires the full tier and cannot be reduced. Reduction applies to the caller's initial close-out; after findings, each caller's correction rules apply unchanged. For Graph Workflow final delivery, an independent `code-review` report is additionally mandated by the delivery-state script, so reduction there is limited to `simplify`.

## Simplification

Dispatch a dedicated native sub-agent that loads `simplify` (Call the Skill tool with "simplify", or pass its resolved `SKILL.md`) in Review mode on the implemented / final change set. Consume its report. Record `no_change` when it finds no supported candidate. Apply candidates only when the user explicitly authorized simplification; otherwise report them. This role is separate from verification and review. No conclusion does not mean no simplification was needed.

## Verification

Dispatch a dedicated native `verify` sub-agent, separate from `simplify` and `code-review` (Call the Skill tool with "verify", or pass its resolved `SKILL.md`). Check every applicable confirmed Acceptance Criterion and the project's existing delivery gates for the affected range, including any required standard PR, CI, or full gate. Pass the baseline, pre-existing edits, confirmed requirements and AC, implemented scope, and local check records. Read its per-criterion `PASS`, `FAIL`, or `NOT VERIFIED` report before deciding completion.

Reuse results that are still valid on the current code. Do not re-run a check already covered by the standard gate. Re-run only after a later edit, a failure, or a new risk. When a full test, build, or end-to-end check is unavailable or clearly out of proportion, record why, substitute evidence, unverified scope, and risk.

The `verify` sub-agent follows the task's project verification entry, `verification_instructions` when configured, or existing local verification skills/docs/scripts. Setup is not a prerequisite; use existing checks and report any capability gap. Follow documented isolation, evidence and cleanup rules. Record exit code and key output for every command actually run. A tool succeeding proves only that gate. It does not automatically prove the requirement is complete. Ticket-local AC IDs are not automatically SPEC AC IDs.

## Review

After verification (or after the caller's prescribed order), spawn a dedicated native `code-review` sub-agent, separate from the `simplify` and `verify` sub-agents (Call the Skill tool with "code-review", or pass its resolved `SKILL.md`). Consume its actual Markdown report; a main-agent self-check does not satisfy this gate. Pass baseline, pre-existing edits, SPEC, the solution design (`SOLUTION.md`) when present, the scope actually implemented, the simplification and verification reports, and the actual command records. Pass a separate `ACCEPTANCE.md` when it exists. After required fixes, re-run affected verification and review in separate sub-agents.

Use one reviewer by default. Only for high-impact changes with unresolved, under-evidenced judgements, or an explicit user request for a panel, may the caller dispatch 2–3 independent reviewers on the same scope and synthesize their findings against the evidence.

Use code-review's [report guidance](../code-review/references/output-contract.md) and reference or retain its original report; the receipt does not define another review taxonomy.

## Independence

Missing simplify, verify, or code-review results required by the selected tier, the caller or a project gate leave close-out incomplete. Do not infer a pass from local checks, and do not infer that an omitted role would have passed. Any authorised substitution must preserve its authority, executor, and coverage evidence. A dispatched worker existing is not proof its role judgement ran.
