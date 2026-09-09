# Sync a SPEC / HLD amendment

When tickets already exist and a SPEC or HLD amendment is confirmed, first confirm `loop` has stopped affected new dispatch and has stopped the affected workers and reclaimed their partial receipts. `to-tickets` does not manage subagents itself. Then compare old / new upstream contracts and the current graph:

- Unaffected tickets keep immutable ID, contract, and current evidence.
- An HLD design-only amendment does not change historical acceptance that still satisfies the SPEC. If done behaviour still matches the requirement but not the new design, keep its requirement evidence and create an explicit correction / migration ticket covering the affected Ds. Supersede only when the original delivery contract is replaced as a whole.
- SPEC amendments follow requirement-contract change. The HLD must not be used to quietly change `R` / `AC`.
- An unstarted `open` ticket may be updated in place by reconciliation when the delivery bound is unchanged. When the bound has changed, mark the old ticket `superseded` and create a replacement. `ready` / `blocked` are dynamic projections, not a writable lifecycle.
- An affected `in_progress` ticket must first be stopped by `loop`, with its partial receipt reclaimed. If implemented changes exist, keep the original ticket and evidence, mark it `superseded`, then create a replacement / correction ticket. In-place update is allowed only when nothing has been implemented and the delivery bound is unchanged.
- A `done` ticket stays `done` when its existing contract and implemented behaviour still fully satisfy the current SPEC. Additional behaviour keeps the original ticket and adds an amendment ticket. When original behaviour must change, replace, or reverse, mark the old ticket `superseded` and create a replacement / correction ticket.
- New end-to-end delivery creates a new ticket. Removed requirements that already have implemented behaviour get an explicit removal / correction ticket. Do not merely delete the old ticket or its evidence.

Upstream contract change must not `reopen` a `done` ticket. `done → open` means SPEC and HLD are unchanged and overall delivery review found the original ticket did not satisfy its original contract. A SPEC or HLD amendment must keep still-valid evidence and express the change with amendment / correction / migration / replacement tickets or necessary `superseded`.

Show the user an impact plan and confirm before `reconcile-batch`. The CLI validates all dependencies, lineage, coverage, and current lifecycle, then recomputes readiness. Any dependency pointing at a `superseded` ticket must be deleted, replaced, or rewired so there is no dangling reference or cycle. If an active worker is still writing the same ticket, stop the sync and hand the lifecycle back to `loop`.

`superseded` is terminal and non-active. It is not on the frontier, does not cover current SPEC acceptance, and is not failure. It keeps the original evidence and records the supersession reason plus nullable replacement lineage.

Request shape: `loopx graph reconcile-batch --help`. Use the shared authority and coverage rules in [SKILL.md](../SKILL.md).
