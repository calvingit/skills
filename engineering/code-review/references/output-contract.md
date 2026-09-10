# Review Report

Use the following Markdown headings and verdict values verbatim so callers can read the same report without a second output format. Write all explanations in the user's language. Return the report directly, without an enclosing code fence.

- `PASS`: the requested scope was reviewed with sufficient evidence, with no required fixes, requirement gaps, or unverified required scope. Optional follow-up may remain.
- `FIXES NEEDED`: confirmed current-scope defects require correction and the review has no unresolved requirement/evidence gaps.
- `INCOMPLETE`: requirements, access, or required evidence prevent a conclusion. Include any confirmed defects already found.

Use `None.` as the entire body of an empty Findings, Follow-up, Requirement gaps, or Unverified section. Never use empty sections to imply success. Scope and Evidence must describe what was actually reviewed and checked; do not claim commands ran unless they did.

```markdown
## Verdict
PASS

## Scope
Describe the target, baseline, reviewed paths, and requirement source. Identify pre-existing edits and exclusions.

## Findings
None.

## Follow-up
None.

## Requirement gaps
None.

## Unverified
None.

## Evidence
Describe inspected code paths, relevant test assertions, actual command results or supplied evidence and its source.
```

For each Findings or Follow-up entry use `### [P2] Short actionable title`, followed by a paragraph containing location (`path:line` when available), triggering scenario, impact, a proportionate correction, and how to verify it. Keep the evidence together, not spread across machine fields. Follow-up entries must explain why they do not block this change. Requirement gaps and Unverified use plain prose or lists identifying what is missing and what would resolve it.

Missing requirements alone do not prevent useful defect review, but unassessed requirement completeness must be stated in Unverified. A partial review is INCOMPLETE, even if it found no defects. A test failure cannot be hidden in Evidence under a PASS verdict.
