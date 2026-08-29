# Codex Executor

A portable skill for using Codex CLI as a coding execution sub-agent.

## Purpose

Codex Executor defines how other AI agents delegate software engineering tasks to Codex CLI.

Supported workflows:

- code analysis
- implementation
- debugging
- refactoring
- testing
- code review

## Architecture

```text
User
 |
 v
Orchestrator Agent
 |
 v
Codex Executor
 |
 v
Codex CLI
 |
 v
Repository
```

## Usage

### Direct Codex CLI

```bash
codex exec --sandbox workspace-write --full-auto "Implement the requested change and run tests"
```

### Through wrapper

```bash
scripts/codex-run.sh write "Implement the requested change and run tests"
```

JSON mode for Agent integration:

```bash
scripts/codex-run.sh write --json "Implement the requested change"
```

## Agent Integration

### Claude Code

Example delegation:

```text
Use codex-executor skill.

Task:
Implement refresh token support.

Workspace:
/path/to/project

Constraints:
- preserve existing API
- run tests

Acceptance:
- authentication flow works
```

### PI / OpenCode

Pass a structured handoff:

```yaml
task:
  type: implementation
workspace:
  path: /path/to/project
goal: Implement refresh token support
constraints:
  - preserve existing API
acceptance:
  - authentication tests pass
verification:
  - npm test
```

### Custom Agents

Use the same handoff contract defined in:

```text
references/handoff.md
```

## Design Principles

- Codex is an execution agent, not the final authority.
- Context should be explicitly handed off.
- Completion requires verification evidence.
- Failed sessions should resume before restarting.

## Structure

```
.
├── SKILL.md
├── VERSION
├── CHANGELOG.md
├── references
│   ├── cli.md
│   ├── handoff.md
│   ├── lifecycle.md
│   ├── model-selection.md
│   ├── prompt.md
│   └── verification.md
└── scripts
    └── codex-run.sh
```
