# Adaptive Workflow Policy

Choose the engineering work needed to resolve the current risk. This is a selection policy for the caller, not a router skill, automatic orchestrator, score calculator or fixed pipeline. Respect an explicitly requested mode and existing contracts.

## Routing and ownership

**Caller owns routing. Callee owns execution. Contract owners resolve changes.**

| Responsibility | Owner |
| --- | --- |
| Recommend the execution route | Upstream caller, from current requirements and repository facts |
| Final human route choice | User |
| Execute the selected scope | Invoked execution skill |
| Requirement / acceptance changes | `to-spec`; unresolved choices first to `grilling` |
| Shared technical design changes | `solution-design` |
| Delivery split and dependencies | `to-tickets` |

Respect an explicitly selected route; the callee may report a better fit and its reasons, but must not switch execution workflows because of preference, size or delivery-unit count. It still checks contracts, authority and necessary prerequisites, returning missing requirements or shared design to their owner. An existing graph or active writers cannot be bypassed: resolve ownership and apply existing lifecycle / stop-write protections before affected writes. Route choice changes neither requirements, authority nor completion standards.

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
| Shared types, interfaces, state/error semantics, ownership, dependency direction, migration or integration decisions | `solution-design`, independently of ticket count. Its entry conditions for a recorded technical solution still apply. |
| Several separately deliverable units, real delivery dependencies or scheduling across contexts | Recommend `to-tickets` → `graph-workflow`, even if all units fit one session. An existing graph stays on this route; do not bypass its lifecycle with quick implementation. |
| No sufficient repeatable method for the required observation, or a stale recipe | Discover existing checks first; use `verification-setup` for necessary recipe/harness work, `ticket-implement` for missing repository-test/product capability, within authority. |
| Wide impact or hard-to-observe behaviour | Plan stronger relevant evidence and review. Identify environment/permission limits; extra planning alone does not establish acceptance. |

Recommend `quick-implement` when one complete delivery scope needs no separately managed units, graph-managed dependencies or cross-context scheduling and can reliably finish in the current context. Verification difficulty and blast radius strengthen evidence and review; they do not alone require tickets.

These conditions combine. A single scope may need a technical solution; several independent slices may not. Existing sufficient verification methods need no setup. Low risk does not waive project gates, and the selection policy never removes `quick-implement` or Graph Workflow's required independent close-out roles. Pause affected operations for actual contract, authority or execution-prerequisite conflicts; route preference alone does not block an explicit Quick choice.

## Reassess on new facts

Keep a brief reason for a consequential routing decision in the current context or existing task record: unresolved fact, affected boundary and selected action suffice. No separate workflow state is required.

Reassess when investigation reveals a shared contract, larger impact or an evidence gap. Return only the affected decision to its owner per [Task Contract](task-contract.md#six-boundaries), and continue unaffected authorized work. Do not regenerate all upstream documents. Planning handoffs do not grant implementation, Git or external publication authority.
