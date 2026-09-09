# Architecture Review Lenses

These lenses raise and test architecture findings. They are not a fixed architecture template, a mandatory checklist, or a stack taxonomy. Use only what is directly relevant to current scope and evidence.

| Lens | Core question | Typical evidence |
|---|---|---|
| Boundary / Ownership | Do change, state, knowledge, and side effects concentrate in the Module that actually owns the behaviour? | Caller spread, change history, state write points, lifecycle |
| Interface / Depth | Are the facts a caller must know nearly as complex as the Implementation? | Params, invariants, call order, error modes, pass-through methods |
| Seam / Adapter | Does the Seam sit at a real variation point, and does the Adapter represent a real replacement or external bound? | Multiple implementations, transport/storage differences, test stand-ins, leaked details |
| Dependency Direction | Do direction, cycles, or cross-module knowledge amplify change? | import/call graph, build deps, init order, reverse calls |
| State / Lifecycle | Do state owner and lifecycle match the use? | Global mutable state, concurrent access, create/dispose, recovery |
| Data / Control Flow | Do data, errors, and side effects leak across a boundary or get re-interpreted in several places? | Transform chains, error mapping, branches, retry, cache, event fan-out |
| Testability | Can tests verify behaviour through the same Interface production callers use? | Reaching past internals, brittle mocks, test-only entry points |
| Standards Conformance | Does the current design violate a declared project architecture constraint, or official stack rules that apply to this scene? | ADRs, project rules, architecture guards, official docs |
| Evolution Cost | Does an ordinary requirement have to cross too many owners, keep several facts in sync, or edit unrelated areas? | Frequent co-change, repeated wiring, parallel state, cross-layer feature edits |

## Deep-read method

1. Start from a user action, public entry, or upstream caller, and trace to the final side effect or persistence.
2. Mark Module ownership, Interface, dependency direction, and state ownership along the path.
3. Read tests, config, rules, and necessary history that bear on the hypothesis. Don't scan unrelated directories.
4. Distinguish project policy from design judgement: a rule hit proves non-compliance, but you still explain actual impact.
5. When citing stack best practice, prefer current official material, and mark hard constraint vs guidance.
6. Look for counter-evidence. If the current structure protects real compatibility, failure isolation, lifecycle ownership, or a replacement boundary, record Not Finding or lower severity.

## Finding gate

A candidate enters Findings only with:

- Locatable current evidence.
- A named architecture concern.
- Actual impact, risk, or ongoing maintenance friction.
- A recommendation direction that is not file-level implementation steps.

Style taste, directory preference, a static smell, or an unconfirmed "best practice" cannot be a finding on its own.
