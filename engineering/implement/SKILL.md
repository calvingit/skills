---
name: implement
description: "Implement one ticket's delivery behaviour within its agreed write scope."
---

# Implement

Use the ticket, requirements, baseline, and write scope supplied by the caller. Implement the simplest correct design, including necessary simplification of complexity this change creates or makes obsolete. Remove unnecessary compatibility, fallback, indirection, duplication, and temporary scaffolding introduced by this change; preserve old behaviour only for a confirmed requirement.

Do not expand into unrelated cleanup. Do not edit SPEC, ACCEPTANCE, HLD, tickets, or Git history, or schedule sibling tasks. Report a requirement or scope conflict rather than resolving it through unauthorised edits.

Return a concise text/Markdown account of the changes, simplification, and unresolved issues, identifying the ticket and attempt when supplied. No capability schema or JSON envelope is required. Do not fabricate verification evidence or fill in commands another agent has not run; verification belongs to `verify`.
