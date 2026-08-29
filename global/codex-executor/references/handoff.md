# Codex Agent Handoff Protocol

## Overview

Codex should be treated as an execution agent.

The caller agent owns:
- task understanding
- context selection
- final judgment

Codex owns:
- repository inspection
- code modification
- verification
- implementation report

## Task Contract

Every delegation should provide:

```yaml
task:
  type: analysis | implementation | debugging | review
workspace:
  path: absolute path
goal:
  description
context:
  facts
constraints:
  rules
acceptance:
  checks
verification:
  commands
```

## Completion

Codex should report:

```text
Implemented:
Verified:
Not verified:
Blocked:
```

Do not report success without validation attempts.
