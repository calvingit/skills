# Engineering Skills Profile

## Resolve and load

1. Use the location or setting explicitly named in the current task, subject to applicable project instructions and caller permissions.
2. Read the Profile linked by the applicable `AGENTS.md`; default creation location is `.agents/engineering-profile.md`. Read only the settings or sections needed for this task, then only relevant referenced sources. Do not load all project docs on entry.
3. With no Profile or an item omitted / `auto`, discover the repository's established convention. Ask only when unresolved ambiguity changes behaviour or write location.

Existing embedded Profiles remain readable until an authorised `project-setup` migration. This preserves persisted project settings; do not create new embedded blocks. If embedded and separate versions both exist, check for conflict before relying on the affected settings. An explicit missing or stale path is a configuration gap: report it, inspect actual sources where safe, and identify any alternate method used. Never present discovery as successful use of the configured entry.

Profile paths are relative to the repository root, including when the link is in a nested `AGENTS.md`. A Profile locates sources; it does not override scoped instructions, requirements, permissions, or completion rules. Requirement sources define intent, glossary defines terms, architecture docs record decisions, and code shows current behaviour; conflicts need evidence or the responsible owner's decision rather than one universal precedence chain.

## File format

Use Markdown with a YAML settings block and optional task-relevant prose. Preserve partial configuration; only include confirmed fields. The following is a field reference, not a template to fill with guessed paths:

````markdown
# Engineering Skills Profile

## Settings

```yaml
task_contract:
  root: <repo-relative-task-root>
  directory_pattern: <project-task-directory-pattern>
project_context: <repo-relative-context-file-or-auto>
domain_glossary: <repo-relative-glossary-file-or-auto>
architecture_authorities:
  - <repo-relative-architecture-entry>
verification_instructions: <repo-relative-verification-guide-or-auto>
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

## Verification

| Surface / evidence type | Recipe entry | Prerequisites | Capability and limits |
| --- | --- | --- | --- |
| <relevant surface> | <existing guide or local skill> | <stable environment needs> | <what it can establish; unsupported or unexercised scope> |
````

Omit the Verification table if no meaningful summary is available; never persist its empty skeleton. The summary is navigation, not a second command list, feature map, or run history. Keep actual commands, isolation, cleanup, supported platforms, and operational proof in the referenced methods and run receipts. Distinguish behaviour, conformance to an agreed visual reference, and interaction quality. A method's successful smoke run proves only its exercised path and environment, not all mapped features or current task acceptance.

No parser or new configuration schema is required. Existing keys retain their meaning:

- `task_contract` locates task documents; it does not configure the duties or names of SPEC, HLD, or tickets.
- `project_context`, `domain_glossary`, and `architecture_authorities` locate stable knowledge. Consumers read only relevant entries.
- `verification_instructions` points to one guide, local skill, or multi-surface index. The Verification summary links applicable methods without duplicating their instructions.
- `requirement_authority.mode`: `repository` uses in-repo requirements; `integrated` uses an already-accessible external system; `external-manual` uses the caller's confirmed task snapshot and marks the original source unverified; `auto` discovers per task. `instructions` is an in-repo access/priority entry, not PRD content or a temporary link. Code hosting and requirement authority are independent.
- `issue_tracker` stores a stable mode and in-repo operations entry, not permission to publish. When explicitly configuring it with no other choice, the existing default is `local`; it does not prescribe a directory.
- `triage` is optional and disabled unless enabled by the caller. Omit `labels` when disabled; ask about labels only when triage is available or explicitly requested. Existing label defaults are `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.
- Missing fields are valid. `auto` means discovery, not capability disabled. Do not rewrite a partial Profile to match the field reference.

## Task conventions and boundaries

The shared [Task Contract](../../shared/task-contract.md) is a logical model; `task_contract.root` and `directory_pattern` only locate persisted task documents. A task can stay in the conversation when no persistence or graph is needed.

When the project has confirmed stable task conventions, link their owning sources from relevant Profile prose: where requirements/AC and design are maintained, how derived tickets reference them, and which project evidence/recovery rules apply. Reuse existing instructions and guides; do not add mandatory YAML fields or copy a second ownership/permission table. Universal restrictions and mandatory gates remain directly visible in applicable instructions. Keep per-task scope, actual authorization, current AC, evidence plans and execution results in their task sources, not the Profile.

## AGENTS.md entry

Use the actual Profile path; links in nested instructions must resolve from that file. For root `AGENTS.md`:

```markdown
## Engineering Skills

项目工程配置见 [.agents/engineering-profile.md](.agents/engineering-profile.md)。
涉及任务存放、需求来源、领域术语、架构或验证时，按需读取相关章节，
仅加载当前任务需要的引用资料；普通代码修改无需预先加载全部资料。
```

Keep universally applicable safety and mandatory gates in ordinary project instructions; do not hide them behind optional Profile loading. A link is an instruction to read on demand, not a Runtime auto-include guarantee.

## Migrate and write safely

- Resolve the existing Profile and Git changes before writing. Preserve confirmed values, unknown fields, comments, and related project-specific context. Reuse an existing equivalent separate file rather than introducing another path.
- For an embedded Profile, migrate only a unique complete range between `<!-- engineering-skills-profile:start -->` and `<!-- engineering-skills-profile:end -->`. One-sided or duplicate markers require resolution; never guess the deletion range. If the old section contains other instructions, retain them.
- When authorised, move the settings to the separate file and replace the embedded section with the on-demand entry in the same change. Move related Engineering Context only when authorised and not already maintained elsewhere. Leave no active duplicate.
- If a destination exists, inspect it; do not overwrite or merge conflicting values without resolution. Relocation does not authorise changing field semantics or confirmed policies.
- Validate configured paths within the repo; allow a new long-lived document only when its creation was authorised. `auto`, directory patterns, and policy enums are not paths. Do not redirect entries to global skills or user-home locations.
- Re-read both files, confirm links and preserved settings, and inspect the diff. Identical repeated setup is a no-op.
