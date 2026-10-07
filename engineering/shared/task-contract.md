# Task Contract

A contract is the confirmed goal, bounds and completion basis of a task, not a required file or a new state machine. Use it when handing work across skills or contexts; a simple task can keep it in the conversation. Existing SPEC, ACCEPTANCE, HLD, tickets and project instructions retain their own responsibilities.

## Resolve the contract

Establish these five items from confirmed sources before implementation; prose, links and existing sections suffice:

| Item | Question | Existing home |
| --- | --- | --- |
| `goal` | What observable result ends this task? | Confirmed conversation; SPEC Goal when persisted |
| `scope` | Which behaviours and change areas are included or excluded? | Conversation or SPEC Scope / Out of Scope; ticket delivery slice |
| `acceptance` | Which independently decidable criteria define success? | Conversation or SPEC AC; ACCEPTANCE scenarios reference those IDs |
| `decision_boundary` | What may the agent decide, and which changes return to an owner? | Confirmed task constraints; HLD for shared technical decisions |
| `evidence` | Which observations are sufficient, at which surface and with what limits? | Task evidence requirements / ACCEPTANCE; methods in project verification guidance |

Resolve relevant `authority` and `recovery` from existing user/project instructions and Runtime controls. Make them explicit for consequential operations or nontrivial recovery; do not invent permissions or a retry policy to fill a template. Missing optional files are not missing task meaning. Ask only for unresolved information that changes the work or needs a user's decision; ordinary implementation choices remain with the agent.

When a SPEC exists, it is the normative engineering requirement snapshot for downstream work. New chat input that changes that snapshot goes through `to-spec`; do not give a worker a conflicting overlay. A contract assembled from several sources points to their sections rather than copying them. The Profile's `task_contract` setting locates documents; it does not require a contract file or define this model.

## Six boundaries

These boundaries are the workflow-level expression of the cross-skill [engineering kernel](../../docs/ENGINEERING_KERNEL.md); the kernel holds the invariants, this contract keeps their task-level meaning and does not replace them.

| Boundary | Enforced meaning |
| --- | --- |
| Goal | Declare completion only for the confirmed result and current criteria, including required gates. Ticket completion and final delivery are distinct. |
| Scope | Work within the confirmed delivery. Expected change areas are not a sandbox; task scope, role write restrictions and Runtime permissions all still apply. Related necessary changes within authority may be reported; unrelated cleanup requires its own scope. |
| Decision | Choose local implementation details. Return requirement/acceptance changes to `to-spec` (unsettled choices first to `grilling`), shared design changes to `high-level-design`, and graph split/dependency changes to `to-tickets`. |
| Authority | A task, recipe, ticket or tool being available does not grant permission. Carry forward actual user authorization and applicable restrictions; do not ask again for already-authorized work. A downstream role may narrow authority, never expand it. Runtime enforces tools, sandbox and lifecycle. |
| Evidence | Derive expectations from confirmed requirements, then select sufficient observable checks. Keep source, current candidate, executor, environment and coverage distinguishable. A green gate, setup smoke or implementation self-check does not establish unrelated AC or independent verification. |
| Recovery | Correct observed defects against an unchanged contract; resolve environment/permission/dependency gaps before another attempt; return contract conflicts to their owner. For a lost acknowledgement or unknown external write result, establish the outcome before repeating the write. Runtime owns process/session recovery; graph recovery repairs graph transactions only. |

Evidence planning happens before implementation: relate each AC to an observable surface and a sufficient existing method, with its prerequisites and limits. A brief session note or references suffice; no mandatory plan artifact. If a method is missing, identify the gap and route necessary harness/test work within authority. Safe unaffected work can continue, but missing evidence cannot become a completion claim. New evidence plans do not alter AC meaning or waive required independent gates.

## Handoff, inheritance and change

- Pass the bounded work, authoritative source paths/sections and revision or supplied snapshot, relevant constraints, candidate/baseline, existing edits, permitted resources, and required evidence. A worker reads the sources and reports material conflicts before dependent work.
- Tickets derive a delivery slice through the existing `covers`, `referenced_design_decisions`, `constraints` and `delivery_acceptance` fields. Scope and constraints may narrow the upstream task; they cannot change its meaning or grant operations. Do not add a second contract envelope to ticket JSON. Ticket-local AC IDs are a separate namespace from SPEC AC IDs.
- Keep copied excerpts and receipts visibly derived and tied to their source/candidate. On resume or amendment, compare affected meaning and evidence with current sources; an unchanged ID alone does not prove validity. Refresh obsolete handoff notes rather than maintaining another authority.
- Change only the responsible source, then reconcile affected consumers and evidence. Preserve unaffected decisions, historical completion and valid observations. During Loop execution, stop affected writers through Runtime before upstream amendment or graph reconciliation; changing state alone does not stop them.
- `NOT VERIFIED` records insufficient evidence, not a product defect or permission to waive acceptance. Only an explicit authorized change to the applicable contract/gates can change completion conditions; retain its source and limits.

The [ownership matrix](../../docs/engineering-responsibilities.md#事实与产物归属) defines writers and derived records. Workflow selection is governed by [workflow policy](workflow-policy.md), not by requiring every task to create every artifact.
