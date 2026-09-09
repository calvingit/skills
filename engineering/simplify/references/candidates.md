# Simplification Candidates

Look for maintenance obligations, not line count. These categories generate candidates; they are not deletion proof.

## Common candidates

- **Interfaces or extension points with no production callers**: an export, hook, event, option, protocol field, command, or extension point has no current production consumer.
- **Multiple representations of the same fact**: several states, caches, summaries, formats, or event families express the same fact and must stay in sync.
- **Extensibility without a current product path**: a strategy, fallback, flag, adapter, or abstraction exists for a future that no current product path owns.
- **Pure forwarding layers**: a wrapper, service, package, or route only forwards behavior and does not reduce coupling or establish a real boundary.
- **Duplicated state machines**: several flags, promises, queues, sentinels, controllers, or callbacks describe the same lifecycle transition.
- **Rebuilt local primitives**: custom parsing, retry, diff, matching, or scheduling could be owned by existing project, platform, or dependency capability with less net maintenance.
- **Interfaces kept alive by support use**: tests, fixtures, snapshots, examples, or docs are the main reason a production-unused interface still exists.
- **Residue of removed features**: the feature is gone or abandoned, but schema, config, compatibility logic, tests, docs, or design records still keep its shape.
- **Production architecture introduced for tests**: a production interface, dependency injection, hook, callback, debug state, or extension point exists mainly to make tests easier to control or observe, not because production needs that variability or boundary.
- **One-off verification scaffolding**: helpers, adapters, fallbacks, probes, compatibility paths, or instrumentation added for a one-off check, experiment, migration, or AI self-check remain on the production path after the task ended.

Visual similarity or duplicated code is only a lead. Separate implementations may still own failure isolation, ownership, compatibility, or a boundary.

Production architecture that exists primarily to support tests is a strong candidate when no real production variability or boundary requires it. Tests, fixtures, examples, or documentation alone do not justify keeping a production interface.

## AI-generated accidental complexity

Long-running AI coding especially accumulates these obligations:

- Injecting many dependencies, clocks, parsers, loggers, retry policies, or callbacks into business functions so they can be mocked.
- interface → implementation → adapter → service → repository relays where each layer only forwards.
- Exposing production APIs such as `retryCount`, `isInitialized`, `pendingOperations`, or lifecycle callbacks so tests can observe internals.
- Repeating validation, copies, fallbacks, rollbacks, and defensive guards on trusted internal handoffs.
- Adding factories, registries, strategies, or plugin seams for later extension when the current product path has one real implementation.
- Keeping probes, feature flags, temporary adapters, compatibility branches, fixtures, or test/docs-only packages after the experiment, migration, or check is done.

The question is not whether AI wrote it. The question is whether the capability has a current production responsibility. Heavy test usage does not by itself prove a production contract is valuable.

## Net benefit

A candidate is real simplification only when the long-term maintenance it removes exceeds any new migration, wrapper, dependency, sync, or compatibility cost.

Do not reduce line count by:

- moving complexity into callers;
- adding a sync layer that maintains two representations;
- replacing small, stable local logic with a new dependency;
- deleting something that still has real consumers or an explicit current design decision;
- deleting an interface because tests are its main users without proving production behavior can still be validated.
