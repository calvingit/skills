# Codex Prompt Patterns

## Principles

Codex prompts should be goal-oriented, evidence-based, and verification-driven.

Avoid:
- unnecessary role descriptions
- repeating system instructions
- artificial step-by-step chains

Provide:
- goal
- context
- constraints
- acceptance criteria
- verification

---

## Implementation

```text
Work in <workspace>.

Goal:
<desired implementation>

Context:
<existing behavior and relevant files>

Constraints:
- preserve existing architecture
- avoid unrelated refactoring

Acceptance criteria:
- <condition>

Verification:
- run <command>

Report:
- changed files
- implementation summary
- verification result
- remaining risks
```

## Debugging

```text
Investigate the issue in <workspace>.

Problem:
<symptom>

Evidence:
<logs, files, reproduction steps>

Find:
- root cause
- supporting evidence
- minimal fix

Verify:
<commands>
```

## Review

```text
Review <target>.

Focus:
- correctness
- maintainability
- security
- regressions

Report only actionable findings with evidence.
```
