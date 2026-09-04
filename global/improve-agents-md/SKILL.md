---
name: improve-agents-md
description: Create, audit, or improve repository AGENTS.md files so coding agents receive concise, accurate, portable, and verifiable project instructions. Use when asked to create or optimize AGENTS.md, reduce instruction bloat, fix stale or conflicting agent guidance, document recurring repository rules, or share one instruction source across Codex, Claude Code, GitHub Copilot, and other coding agents.
---

# Improve AGENTS.md

Treat `AGENTS.md` as a compact execution guide for coding agents, not a repository encyclopedia. Preserve proven project rules while removing noise that weakens instruction adherence.

## Operating Mode

- If the user asks to review, audit, or propose changes, inspect and report without editing.
- If the user asks to create, improve, fix, or update the file, apply the smallest justified edits and validate them.
- If removing a rule could change intended behavior and repository evidence does not resolve the ambiguity, ask before removing it.

## Workflow

1. Discover all applicable instruction files from the repository root to the working directory, including `AGENTS.md`, nested `AGENTS.md`, overrides, and tool-specific entrypoints.
2. Inspect the repository evidence that can confirm or contradict the instructions:
   - manifests, lockfiles, task runners, and CI workflows for commands
   - `README`, `CONTRIBUTING`, architecture decisions, policies, and security docs for authoritative references
   - representative source and tests for non-standard conventions
   - generated-file markers, legacy areas, migrations, and recurring failure notes for hazards
3. Classify each instruction as `keep`, `rewrite`, `move`, or `remove`.
4. Detect contradictions, duplicate ownership, stale paths, invalid commands, and rules placed at the wrong scope.
5. Draft or apply a minimal diff. Preserve useful wording unless a rewrite materially improves precision or scope.
6. Validate paths, commands, precedence, and the final file's consistency with repository evidence.
7. Report what changed, what was verified, and what could not be verified.

## Content Standard

Keep an instruction only when it is stable, actionable, relevant to its scope, and likely to prevent wasted work or a real mistake.

Prefer:

- a one-line project identity when it changes how the repository should be approached
- a small routing map for non-obvious workspace or package boundaries, not a copied directory tree
- exact setup, build, test, lint, typecheck, generation, and release commands with necessary preconditions
- the narrowest useful verification command before a full-repository command
- non-standard architecture constraints and canonical example paths
- generated or protected files that must not be edited directly
- safety, data-loss, compatibility, migration, and deployment hazards
- explicit completion requirements that are not already enforced automatically
- links to authoritative repository documents instead of copied explanations

Remove or relocate:

- generic advice such as "write clean code" or "follow best practices"
- rules already guaranteed by repository tooling, or by every targeted Agent runtime after current behavior has been verified
- formatter, linter, compiler, or hook rules that are already enforced and self-explanatory
- exhaustive dependency lists, full directory trees, and codebase facts that a short search reveals reliably
- long code examples that can be replaced with a stable repository path
- duplicated content from `README`, `CONTRIBUTING`, specifications, policies, or architecture docs
- task status, temporary plans, session notes, personal preferences, and other volatile state
- speculative rules added for hypothetical failures that have not occurred
- stale commands, files, names, and historical guidance that no longer applies

Keep absolute language such as `MUST`, `NEVER`, and `ALWAYS` only for safety, data loss, external contracts, or a rule with evidence of repeated violations. Otherwise state the required outcome and scope without inventing exceptions.

## Scope and Portability

Use standard Markdown and plain, direct instructions. Do not add model-specific XML tags such as `<important if="...">` to the shared `AGENTS.md`; other runtimes may treat them as ordinary text.

- Put repository-wide rules in the root `AGENTS.md`.
- Put subtree-specific rules in a nested `AGENTS.md` only after verifying how the repository's target Agent runtimes discover nested files.
- Do not copy root rules into child files. State only the narrower addition or override.
- Keep universally required safety and verification rules at the root; do not hide them in a subtree that some launch locations may not load.
- Use `AGENTS.md` as the shared source of truth. Keep tool-specific wrappers minimal and do not maintain duplicated full copies.
- If changing cross-Agent wiring or precedence, read [references/compatibility.md](references/compatibility.md) and verify current official documentation for every target runtime.

Do not claim universal support merely because a tool supports `AGENTS.md` in one surface. CLI, IDE, cloud Agent, and code-review behavior may differ.

## Classification Test

For every section or rule, answer:

| Test | Decision |
| --- | --- |
| Would removing it plausibly cause a costly or recurring mistake? | Keep or rewrite. |
| Can the Agent reliably discover it from nearby files within a short search? | Usually remove; keep only if it saves recurring exploration or prevents choosing the wrong source. |
| Is another file or tool the authoritative owner? | Link, move, or remove the duplicate. |
| Does it apply only to one subtree or task type? | Narrow its scope after checking runtime discovery behavior. |
| Is it correct for every task in its stated scope? | Narrow or rewrite; do not preserve harmful overreach. |
| Can the stated path, command, or example be verified? | Verify it or mark it unverified; never guess. |

## Default Structure

Use only sections that add value. Do not force empty sections.

```markdown
# Agent Instructions

## Repository
- [One-line identity or non-obvious workspace routing]

## Commands
| Task | Command |
| --- | --- |
| Focused test | `[verified command]` |
| Lint or typecheck | `[verified command]` |

## Working Rules
- [Stable, repository-specific instruction]

## Verification
- [What must be checked before reporting completion]

## References
- Architecture: `[repo-relative path]`
```

## Validation

- Confirm every referenced repository path exists.
- Confirm commands are declared in the authoritative manifest, task runner, or CI configuration.
- Run safe, relevant commands when the environment permits; otherwise report that only static verification was possible.
- Compare root, nested, override, and tool-specific files for contradictions.
- Ensure removed content still has an authoritative owner when it remains necessary.
- Review the final diff for accidental loss of safety rules, commands, or hard-won repository knowledge.
- Record before/after line counts as a signal, not a quality target. Do not optimize for an arbitrary maximum.

## Output

For an audit, return findings ordered by impact, with evidence and proposed minimal changes.

For an edit, report:

- files changed
- important rules kept, moved, rewritten, or removed
- validation performed and its result
- remaining uncertainty or runtime-specific compatibility risks

Do not present a shorter file as automatically better. The goal is less irrelevant context without losing instructions that prevent real failures.
