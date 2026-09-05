# Execution Graph Module

`execution-graph` owns the shared JSON ticket graph contract and its CLI implementation. It is an internal shared Module, not a user-routed workflow Skill.

Consumers:

- `to-tickets` creates and reconciles confirmed delivery graphs.
- `loop` queries the graph and applies normal execution lifecycle transitions.
- ticket workers consume the receipt schema but never mutate the graph.

The public CLI is `scripts/ticket_graph.py`; its schemas live in `schemas/`, and its black-box CLI tests live in `tests/`. The Module owns ticket identity, schema validation, graph invariants, transaction/recovery and migration. It does not own ticket decomposition, workspace evidence judgment or worker dispatch.

Loop uses the CLI for graph queries and mutations. It may reuse the Module's read-only contract validators for receipt and identity checks, but never writes the graph through internal store or lifecycle APIs.
