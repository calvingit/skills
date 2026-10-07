# Deepening

How to deepen a cluster of shallow modules safely, given its dependencies. Assumes the vocabulary in [SKILL.md](SKILL.md) — **module**, **interface**, **seam**, **adapter**.

## Dependency categories

When assessing a candidate for deepening, classify its dependencies. The category determines how the deepened module is tested across its seam.

### 1. In-process

Pure computation, in-memory state, no I/O. These modules can usually be deepened directly by merging them and testing through the new interface. No adapter is needed.

### 2. Local-substitutable

Dependencies that have local test stand-ins (PGLite for Postgres, in-memory filesystem). They can be deepened if the stand-in exists. The deepened module is tested with the stand-in running in the test suite. The seam is internal; no port is needed at the module's external interface.

### 3. Remote but owned (Ports & Adapters)

Your own services across a network boundary (microservices, internal APIs). Define a **port** (interface) at the seam. The deep module owns the logic; a transport **adapter** implements the port and is injected through it. Tests use an in-memory adapter. Production uses an HTTP/gRPC/queue adapter.

Recommendation shape: *"Define a port at the seam, implement an HTTP adapter for production and an in-memory adapter for testing, so the logic sits in one deep module even though it's deployed across a network."*

### 4. True external (Mock)

Third-party services (Stripe, Twilio, etc.) you don't control. The deepened module depends on a stable port; a concrete adapter for the external service is injected through that port, and tests provide a mock adapter.

## Seam discipline

- **Adapter count is a lead, not a verdict.** One adapter means a hypothetical seam — worth questioning whether a second adapter is justified (typically production + test). But a single-adapter seam is not automatically mere indirection: it may hide necessary complexity or isolate a real external boundary. Judge by what changes the seam separates, not by the count.
- **Internal seams vs external seams.** A deep module can have internal seams (private to its implementation, used by its own tests) as well as the external seam at its interface. Don't expose internal seams through the interface just because tests use them.

## Testing strategy: replace, don't layer

- Old unit tests on shallow modules are **not** automatically waste once tests at the deepened module's interface exist. Decide per test by comparing: behaviour coverage (inputs and outcomes), failure modes exercised, unique protection (what regression only this test would catch — internal invariants, faster feedback on private seams), and feedback cost. Keep, merge into the interface tests, or delete only after this comparison — never delete solely because the interface got deeper.
- Write new tests at the deepened module's interface. The **interface is the test surface**.
- Tests assert on observable outcomes through the interface, not internal state.
- Tests should survive internal refactors — they describe behaviour, not implementation. A test that must change when only the implementation changes (behaviour intact) is a lead that it asserts past the interface; when the contract itself changes, updating the test is legitimate — check what actually changed before judging.
