# Simplification Investigation

Use this for review mode, repository-wide scope, or modify mode when dynamic loading, external consumers, or persistence compatibility is unresolved.

## Evidence ladder

Do not treat a smell or static search hit as deletion authority. Advance by evidence strength:

1. **Smell**: complexity, duplication, or over-abstraction appears to exist.
2. **Static lead**: search, lint, compiler, or analyzer shows little or no use.
3. **Consumer map**: in-repo hits are classified, and relevant callers/callees have been read.
4. **Contract proof**: dynamic loading, external use, persistence, compatibility, ownership, and the current design reason are confirmed or explicitly unknown.
5. **Behavior proof**: there is a decisive check that would catch an incorrect deletion, and a recovery path if it fails.

High-confidence modify mode usually needs a consumer map, contract proof, and behavior proof.

## Consumer classification

Classify hits; do not only count references:

- **Runtime**: production code, real entrypoints, runtime config, migrations, loaders, deployment, or other actual execution paths.
- **Support-only**: tests, purely explanatory docs, snapshots, examples confirmed as samples only, generated expectations.
- **Uncertain**: public exports, fixtures, plugin registrations, reflection, lazy imports, string dispatch, manifests, generated code, or interfaces that may be used by an external package.

Do not promote a candidate to high-confidence deletion while a dynamic or external consumer remains unresolved.

## Coverage

Focused: fully trace ownership and contract for the requested subsystem, symbol, state machine, dependency, or suspected duplication. Do not expand on your own.

Broad: map coverage by responsibility first, then rank candidates. Consider the repository's relevant entrypoints, runtime control, public APIs / config, state / lifecycle, persistence / compatibility, plugins / DI / reflection / codegen, background workers, packages / adapters / tests / docs. Record unchecked areas as uncovered.

Do not stop a repository-wide review at the first deletable point.

## History as evidence

When a design, compatibility path, or unexplained abstraction has history, use git history, blame, PRs, issues, ADRs, RFCs, or comments to answer:

- Which failure, requirement, or future plan introduced it?
- Does that condition still hold?
- Which artifact or owner still maintains the decision?
- What becomes expensive or unrecoverable after deletion?

"Unchanged for a long time" or "no search hits" are discovery leads only.

## Review output

Review mode does not modify code. Report coverage, proven and ranked candidates, important rejected or unresolved candidates, and the specific missing fact for each uncertain item.

Rank by confidence, benefit, blast radius, reversibility, and validation strength. Do not rank by lines deleted or candidate count.
