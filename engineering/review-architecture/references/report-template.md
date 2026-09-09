# Report Template

Write the report where the target repo already puts task / review artifacts. With no stable convention and no user-named path, emit in the current session. Do not invent a project-level directory convention.

```markdown
# Architecture Review — <scope>

## Summary
- Scope: <what this review covers>
- Coverage: <covered areas and what was left out>
- Result: <critical/high/medium/low findings / no findings / needs more evidence>
- Top finding: <ID, theme, severity>
- Next: <codebase-design / grilling / to-spec / high-level-design / simplify / observe>

## Review Basis
- Question: <architecture question this round answers>
- Project authorities: <instructions, architecture docs, ADRs, rules actually found>
- Project controls: <checks that exist and apply; else none>
- External guidance: <official stack basis actually used; else none>

## Architecture Map
- Entrypoints: <main entries>
- Ownership boundaries: <related Module / package / layer>
- Dependency direction: <load-bearing dependencies>
- State / lifecycle owners: <load-bearing state and lifecycle>

## Evidence
| Kind | Source | Observation | Status |
|---|---|---|---|
| code / call path / test / rule / history / command / official guidance | file:symbol / command / source | ... | Observed / Inferred / External guidance / Unknown |

## Findings

### A-001 — <finding> `[Critical | High | Medium | Low | Speculative]`

- Concern: <Boundary / Ownership / Dependency / State / ...>
- Evidence: <current code, relations, tests, rules, or commands>
- Impact: <actual risk, change fan-out, maintenance cost, or verification difficulty>
- Basis: <project rule / current architecture evidence / external guidance / design judgment>
- Recommendation direction: <target architecture outcome, not file-level steps>
- Unknown: <facts still needing a decision or check>
- Counter-evidence / trade-off: <why the current design may be reasonable, or evidence considered but not enough to reject the finding>

## Not Findings
- <issues checked whose evidence does not hold, plus counter-evidence>

## Next Step
- <after the user picks a finding, hand to the matching skill; review-architecture itself does not implement>
```

If the project has lint, a dependency check, an architecture guard, or a baseline, record command, exit status, and a summary as Evidence. Do not require those mechanisms just to fill the template.
