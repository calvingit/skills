---
name: visual-pr
description: Only use when the user explicitly invokes visual-pr. Draft a short pull request description with a visual change outline for the user to review; never edit the PR.
---

# Visual PR

Draft a description that tells a reviewer why the change exists and what shape the implementation takes. Work read-only: do not commit, push, create or edit a PR, or change Git state. The user decides whether and where the text goes.

## Establish scope

Use the PR, branch or commit range the user names. Otherwise use the current branch: `gh pr view --json url,number,title,baseRefName,headRefName` when a PR exists, or the commits since the merge base with the default branch when it does not. If neither yields relevant changes, ask which change to describe. Missing `gh` or no remote only limits metadata; describe from the local diff.

## Gather context

Read the complete diff and enough surrounding code to understand behaviour and ownership. Read the ticket, spec or plan only when the user or the branch points to one. Do not invent motivation the sources do not support; mark it as an assumption instead.

## Write the description

Use this structure and nothing more:

````markdown
{Optional links line: ticket, spec, plan or related PRs. Omit when there are none.}

## Why the change

{Exactly one sentence: the problem this solves and what becomes possible after it ships.}

## Special things to note

- {1-3 reviewer warnings: migrations, compatibility, deliberate omissions, surprising decisions. Write "None." when there are none.}

## Change outline

{short lead-in}

```diff
{a focused view}
```
````

For the change outline, pick the smallest set of views that explains this change, and order them so the story is easiest to follow:

- SQL tables and endpoint request/response contracts, with pseudocode for the business logic
- key data structures or types
- a shallow file tree showing changed responsibilities
- UI component trees with the hooks, state and package boundaries that matter
- call trees, control flow or data flow

Use `diff` for a focused change to an existing shape; show the full target shape in a language block or `text` when it is new or clearer without diff notation. Omit views that did not change. This is a structural view, not prose and not a file-by-file changelog.

Write as one person talking to another: plain, short, no jargon.

## Hand back

Reply with the description in one fenced `markdown` block the user can copy, then one line naming the PR or range it covers and any assumptions. Write it to a file only when the user asks, at the path they give. Never run `gh pr edit`, `gh pr create` or anything else that publishes it.

If the user wants a fuller visual explanation of the change beyond the PR body, tell them to run `show-me`; do not start it yourself.
