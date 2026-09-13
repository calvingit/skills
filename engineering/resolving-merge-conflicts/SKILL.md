---
name: resolving-merge-conflicts
description: Resolve an in-progress Git merge or rebase conflict.
---

# Resolve Merge Conflicts

1. Inspect the merge/rebase state, Git history, index, conflicting paths, and existing user edits. Establish the merge's intended result and the user's authorisation. Do not start a different merge or rebase.
2. Read both changes and their original intent through commits and available PRs or requirements. Resolve only the affected conflicts, preserving both intents where compatible. Do not invent new behaviour. If incompatible intent needs a user decision, leave the operation in progress and report the exact choice; do not force a resolution or abort without authorisation.
3. Run the project's relevant checks and inspect the resulting diff. Fix regressions caused by the resolution within the agreed scope. Keep unrelated user changes intact.
4. Stage only the resolved changes when authorised to finish the operation. Inspect the full index before committing or continuing: unrelated staged changes must not enter the merge commit or replayed commit. Do not unstage the user's work automatically; report a scope conflict if it prevents continuation.
5. Commit or continue the merge/rebase only when the request authorises completing it. A request to resolve conflicts alone does not grant commit permission. If continuation reveals more conflicts, apply the same boundaries to each step. Never push unless separately authorised.

Report resolved paths, checks, unresolved choices, and the actual Git state: files resolved, staged, committed, or rebase still in progress. Do not equate edited conflict markers with a completed merge.
