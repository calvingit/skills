# Design It Twice

Use this only when the user wants to explore alternative interfaces, or one design is not enough to judge. Read [SKILL.md](SKILL.md) and [DEEPENING.md](DEEPENING.md) first.

Based on "Design It Twice" (Ousterhout) — your first idea is unlikely to be the best. Uses the vocabulary in SKILL.md — **module**, **interface**, **seam**, **adapter**, **leverage**.

## Process

1. Frame the problem space for the user: constraints any candidate must satisfy, dependency categories (see DEEPENING.md), and the seam. A rough code sketch may ground the constraints. The sketch is not a proposal.

2. Compare only candidates with a real trade-off — usually two. Do not pad with directions nobody would ship. Common axes: a smaller interface, a trivial default call path, flexibility when real extension already exists. Ports-and-adapters can be a candidate when there is a remote dependency. It is not mandatory.

3. Parallel sub-agents only when the problem is large enough and current authorisation allows them. Otherwise generate the candidates in this session under the same constraints. The second design must not be a rename of the first.

4. Each candidate must include: Interface (types, methods, params — plus invariants, ordering, error modes), a usage example, what the implementation hides behind the seam, dependency / adapter strategy, and where leverage is high or thin.

5. Present designs sequentially, then compare on **depth**, **locality**, **seam placement**, and migration cost. Recommend one. If pieces from different designs combine well, propose a hybrid. Be opinionated — the user wants a strong read, not a menu.
