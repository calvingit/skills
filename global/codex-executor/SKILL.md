---
name: codex-executor
description: Delegate a focused coding task to Codex CLI as a sub-agent.
---

# Codex Executor

## Purpose

Codex CLI is an execution-focused coding sub-agent.

The caller agent owns:
- understanding user intent
- preparing context
- defining acceptance criteria
- evaluating results

Codex owns:
- repository inspection
- implementation
- verification
- reporting changes

## When To Use

Use Codex for tasks requiring:
- repository exploration
- multi-file changes
- terminal execution
- debugging with real code

Do not delegate vague tasks. Every task must define a goal and success criteria.

## Delegation Requirements

Every Codex request should include:

- workspace
- goal
- context
- constraints
- acceptance criteria
- verification commands

## Execution Modes

Use the appropriate execution mode:

- analysis: read-only investigation
- write: authorized code modification
- full: explicitly approved unrestricted access
- resume: continue an existing session

## References

- references/handoff.md - Agent handoff protocol
- references/prompt.md - Prompt patterns
- references/model-selection.md - Model routing policy
- references/verification.md - Completion verification
- references/lifecycle.md - Session lifecycle
- references/cli.md - CLI usage
