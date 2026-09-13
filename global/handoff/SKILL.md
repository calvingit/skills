---
name: handoff
description: Write a handoff for another agent to continue this conversation.
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS - not the current workspace.

Capture the current goal and scope, completed work and actual verification, remaining work, confirmed decisions, existing authorisation and limits, blockers, and the next actionable step. Identify the workspace and relevant existing changes. Separate observed results from assumptions; include only what is needed to resume, and return the saved file's absolute path.

Include a "suggested skills" section naming the exact skills the next agent should invoke.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
