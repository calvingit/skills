# Adaptive Workflow Policy

Choose the engineering work needed to resolve the current risk. This is a selection policy for the caller, not a router skill, automatic orchestrator, score calculator or fixed pipeline. Respect an explicitly requested mode and existing contracts.

## Assess three dimensions

| Dimension | Assess from task and repository facts |
| --- | --- |
| Uncertainty | Are required behaviour and expected results settled? Are load-bearing technical decisions known? Distinguish unknown intent from unknown implementation. |
| Blast radius | Which callers, modules, persisted data, public contracts or shared resources can be affected? A small authentication/migration change can have wide impact. |
| Verification difficulty | Can the relevant behaviour be observed reliably in available, permitted resources? Are device, visual, timing or real-provider evidence needed? |

Use qualitative facts, not line count, file count or small/medium/large labels. Assess the dimensions separately; one high-risk dimension can require stronger work even if the other two are low.

## Select only necessary capabilities

| Current fact | Action |
| --- | --- |
| Confirmed local behaviour, limited impact, sufficient existing checks | Direct implementation and proportionate verification for an ordinary change; `quick-implement` for a confirmed single scope requiring its close-out contract. |
| Unsettled behaviour, scope or acceptance choice | `grilling`; persist through `to-spec` only when requirements need sharing/versioning or an existing SPEC needs amendment. |
| A load-bearing technical path needs investigation across sessions | `wayfinding`; ordinary code investigation does not require it. |
| Shared types, interfaces, state/error semantics, ownership, dependency direction, migration or integration decisions | `high-level-design`, independently of ticket count. An HLD's entry conditions still apply. |
| Several claimable delivery slices, real dependencies or scheduling across contexts | `to-tickets` → `loop`. An existing graph stays on this route; do not bypass its lifecycle with quick implementation. |
| No sufficient repeatable method for the required observation, or a stale recipe | Discover existing checks first; use `verification-setup` for necessary recipe/harness work, `implement` for missing repository-test/product capability, within authority. |
| Wide impact or hard-to-observe behaviour | Plan stronger relevant evidence and review. Identify environment/permission limits; extra planning alone does not establish acceptance. |

These conditions combine. A single scope may need HLD; several independent slices may not. Existing sufficient verification methods need no setup. Low risk does not waive project gates, and the selection policy never removes `quick-implement` or Loop's required independent close-out roles. When an explicitly requested route cannot meet its own conditions, explain and resolve that mismatch rather than silently switching modes.

## Reassess on new facts

Keep a brief reason for a consequential routing decision in the current context or existing task record: unresolved fact, affected boundary and selected action suffice. No separate workflow state is required.

Reassess when investigation reveals a shared contract, larger impact or an evidence gap. Return only the affected decision to its owner per [Task Contract](task-contract.md#six-boundaries), and continue unaffected authorized work. Do not regenerate all upstream documents. Planning handoffs do not grant implementation, Git or external publication authority.
