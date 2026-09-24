---
name: implement
description: "Implement one ticket's delivery behaviour within its agreed write scope."
---

# Implement

Use the ticket, requirements, baseline, and write scope supplied by the caller. Implement the simplest correct design, including necessary simplification of complexity this change creates or makes obsolete. Remove unnecessary compatibility, fallback, indirection, duplication, and temporary scaffolding introduced by this change; preserve old behaviour only for a confirmed requirement.

Do not expand into unrelated cleanup. Do not edit SPEC, ACCEPTANCE, HLD, tickets, or Git history, or schedule sibling tasks. Report a requirement or scope conflict rather than resolving it through unauthorised edits.

Use the project verification entry (`verification_instructions` when configured, otherwise existing local skills/docs/scripts) to select necessary development tests and local acceptance checks. Report their actual commands, results, and coverage. Missing guidance does not block use of existing checks; report capability gaps to the caller without treating setup as a prerequisite. These checks may support ticket-local completion; final independent verification belongs to `verify`.

Return a concise text/Markdown account of the changes, simplification, checks, and unresolved issues, identifying the ticket and attempt when supplied. No capability schema or JSON envelope is required. Do not fabricate verification evidence or fill in commands another agent has not run.
