---
name: project-setup
description: Detect and persist a project's engineering-workflow conventions and requirement-authority entries. Writes need user confirmation.
---

# Project Setup

Turn the target repo's existing engineering workflow, domain docs, optional issue tracker, and triage conventions into a stable block in root `AGENTS.md`. This is an optional convention-persistence helper. It is not a runtime prerequisite for other engineering skills.

## Resolution contract

Engineering skills resolve project convention in this order:

1. What the user named in the current task.
2. `Engineering Skills Profile` in the applicable `AGENTS.md`.
3. Conventions proven by directories, docs, and tools already in the repo.
4. The skill's own generic defaults.
5. Ask the user only when remaining ambiguity would change write location or behaviour.

Missing Profile, cancelled setup, or an item left `auto` means keep discovering dynamically. Other skills must not stop.

## Stable settings only

The Profile records entries and policies that stay stable across tasks:

- Task-contract root and task-directory naming.
- Long-lived project context.
- Domain-vocabulary source.
- Architecture-authority entries.
- Requirement-authority access mode and in-repo instructions entry.
- ADR directory or `auto`.
- Archive directory for finished task contracts, or `auto`.
- Optional issue-tracker mode and in-repo operations entry.
- Label vocabulary when the triage skill is available or the user explicitly enabled it.

Do not turn these into configurable variables:

- The names and contract duties of `SPEC.md`, `HLD.md`, and `tickets/`.
- Current task directory, current task, progress, retry, iteration, or verification evidence.
- Concrete test commands, agent / model choice, or commit / push permission.
- Temporary report paths.

Do not pre-create empty ADRs, sample SPECs, HLDs, or placeholder `tickets/` directories. The owning skill creates a real artifact when it is needed, using project convention.

## Detect before asking

Read-only first:

- Applicable `AGENTS.md`, README, CONTRIBUTING, and deeper instructions.
- Existing task / spec, project context, glossary, architecture, ADR, and archive layout.
- Whether PRDs, requirement docs, or other requirement authority live in the repo, in an already-integrated external tool, or only as user-supplied snapshots.
- Git remote, existing issue-tracker instructions, `.scratch/`, or other collaboration convention.
- Whether a `triage` skill is available, and whether the repo already has matching labels.
- Git status, so existing user edits are not overwritten.

Classify candidates as `confirmed`, `inferred`, `missing`, or `conflict`. A common directory existing is not enough to call it authority. Need project docs, actual use, or an explicit user choice.

## Ask once

Before writing, show in one pass:

1. Detection results and why.
2. The full recommended Profile.
3. Which `AGENTS.md` will change, and any new long-lived docs explicitly requested.
4. Choices: accept the recommendation, customise, leave an item `auto`, or cancel.

If the user already gave every choice when invoking setup, treat those as this round's answers. Do not ask again. The happy path asks once. Keep confirming only when a custom value is invalid, conflicts with existing convention, or would overwrite existing content.

`auto` means do not pin that item; consumers keep discovering dynamically. It does not disable the capability. Cancel means write nothing.

## Profile format

Use this controlled block in root `AGENTS.md`. Angle brackets are values the project confirms, not default paths. Defaults: `requirement_authority.mode: auto`, `requirement_authority.instructions: auto`, `issue_tracker.mode: local`, `issue_tracker.instructions: auto`, `triage.enabled: false`.

````markdown
## Engineering Skills Profile

<!-- engineering-skills-profile:start -->
```yaml
task_contract:
  root: <repo-relative-task-root>
  directory_pattern: <project-task-directory-pattern>
project_context: <repo-relative-context-file-or-auto>
domain_glossary: <repo-relative-glossary-file-or-auto>
architecture_authorities:
  - <repo-relative-architecture-entry>
requirement_authority:
  mode: <repository-or-integrated-or-external-manual-or-auto>
  instructions: <repo-relative-instructions-or-auto>
adr_root: <repo-relative-adr-root-or-auto>
archive_root: <repo-relative-archive-root-or-auto>
issue_tracker:
  mode: <local-or-github-or-gitlab-or-other>
  instructions: <repo-relative-instructions-or-auto>
triage:
  enabled: <true-or-false>
  labels:
    needs_triage: <label>
    needs_info: <label>
    ready_for_agent: <label>
    ready_for_human: <label>
    wontfix: <label>
```
<!-- engineering-skills-profile:end -->
````

Path fields are relative to the repo root. They must not point at a home directory, a global skills repo, or anywhere outside this repo. Do not infer project directories from the placeholders above. `auto` means consumers keep discovering the project's existing convention.

`requirement_authority` and `issue_tracker` are orthogonal. Code hosting or the issue tracker can be GitLab while the PRD still lives in Feishu or WeCom that cannot be integrated.

- `repository`: normative requirements live in the repo; `instructions` points at in-repo read notes or an index.
- `integrated`: normative requirements live in an external system the agent can already reach through project-configured tools; `instructions` points at in-repo access and priority notes.
- `external-manual`: normative requirements live in a system the agent cannot reach; the user supplies a confirmed snapshot for this task; the agent must not claim to have verified the original source.
- `auto`: do not pin a mode; the consumer discovers per task and must not guess when it cannot confirm.

The Profile stores stable modes and in-repo instruction entries. It does not store current PRD content, temporary links, or a one-task requirement snapshot. `to-spec` is the main consumer. `grilling` and `wayfinding` use it only to decide which requirement facts the user must supply. Downstream `high-level-design`, `to-tickets`, `quick-implement`, `loop`, and `code-review` consume confirmed SPEC, applicable HLD, or tickets. They do not interpret this config directly.

Omit `labels` when `triage.enabled: false`. Ask for labels only when a triage skill is detected or the user explicitly enables triage. Defaults: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. GitHub, GitLab, or other operations live in the in-repo doc `issue_tracker.instructions` points at. The Profile stores the stable entry only.

## Write safely

- No marker: add one Profile section. Complete and unique: update in place.
- One-sided marker, duplicates, or a block that conflicts with other project rules: stop. Do not guess overwrite range.
- An existing Profile is valid partial config. Keep unknown fields and already-confirmed values. Missing fields from the current template are not an error. Add or change fields only after the user confirms. Do not rewrite the whole Profile just to match the template.
- Configured path fields must exist unless the user explicitly chose to create that long-lived doc. Directory patterns, policy enums, and `auto` are not checked as paths.
- Keep the rest of `AGENTS.md`, its order, and the user's existing edits.
- Repeating the same config must not produce a second block or a meaningless diff.
- After writing, re-read the Profile and verify paths, unique markers, and the Git diff. Do not commit or push.

## Report

Report recommended vs custom items, items left `auto`, what actually changed, long-lived docs created, and what was not verified. Do not describe a static path existing as every runtime having loaded it.
