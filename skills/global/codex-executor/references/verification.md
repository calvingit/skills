# Verification Strategy

Codex completion is not equivalent to task success.

A completed task requires evidence.

## Verification Layers

## 1. Diff Verification

Check:
- changed files
- unexpected modifications
- unrelated refactoring

## 2. Static Verification

Examples:
- lint
- type checking
- formatting checks

## 3. Runtime Verification

Examples:
- unit tests
- integration tests
- build commands
- smoke tests

## 4. Behavioral Verification

Confirm:
- original issue is fixed
- expected behavior works
- regressions are unlikely

## Agent Rules

Ask Codex to report:

```text
Implemented:

Verified:

Not verified:

Blocked:
```

If verification cannot run, the limitation must be explicitly reported.

Do not treat assumptions as validation.
