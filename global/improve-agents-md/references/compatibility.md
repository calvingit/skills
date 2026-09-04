# AGENTS.md compatibility notes

Use this reference only when creating, moving, or consolidating instruction entrypoints across Agent runtimes. These notes were last verified on 2026-09-04; re-check the linked official documentation because discovery behavior can change.

## Shared format

- The [AGENTS.md project](https://github.com/agentsmd/agents.md) defines `AGENTS.md` as an open Markdown format for repository instructions.
- Support is runtime- and surface-specific. A shared filename does not imply identical discovery, precedence, size limits, or override behavior.

## Codex

- [OpenAI: Custom instructions with AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md)
- [OpenAI: Codex best practices](https://developers.openai.com/codex/learn/best-practices)

Codex loads global guidance and then project guidance from the repository root toward the current working directory. More specific files appear later in the combined instructions. Codex also supports `AGENTS.override.md`; confirm current limits and precedence in the official documentation before changing a hierarchy.

## Claude Code

- [Anthropic: How Claude remembers your project](https://code.claude.com/docs/en/memory#agentsmd)

Claude Code uses `CLAUDE.md` as its project instruction entrypoint. When a repository uses `AGENTS.md` as the shared source, the official documentation recommends a minimal `CLAUDE.md` that imports `@AGENTS.md`, or a symlink when no Claude-specific additions are needed. Do not maintain a second full copy.

## GitHub Copilot

- [GitHub: Adding repository custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions)
- [GitHub: Custom instructions support matrix](https://docs.github.com/en/copilot/reference/custom-instructions-support)

GitHub Copilot supports `AGENTS.md` on several Agent surfaces, but support differs across GitHub.com, IDEs, CLI, cloud Agent, and code review. Check the current support matrix before deleting `.github/copilot-instructions.md` or another working entrypoint.

## Design consequence

Keep the shared `AGENTS.md` portable:

- standard Markdown rather than model-specific attention tags
- repository-relative paths
- no dependence on one runtime's slash commands, tool names, or hidden system prompt
- small wrappers for runtimes that require another filename
- explicit verification of the actual tools and launch directories used by the project

## Method references

The Skill's filtering and audit approach also compares the following community implementations. Treat them as design input, not runtime specifications:

- [HumanLayer `improve-claude-md`](https://github.com/humanlayer/skills/blob/main/plugins/improve-claude-md/skills/improve-claude-md/SKILL.md): conditional relevance and aggressive context reduction; its model-specific XML technique is intentionally not applied to shared `AGENTS.md` files.
- [Sentry `agents-md`](https://github.com/getsentry/skills/blob/main/skills/agents-md/SKILL.md): concise instructions, exact commands, repository-relative paths, and one shared source.
- [`agents-md-optimizer`](https://github.com/CaesiumY/agents-md-optimizer): discoverability filtering and source-based gotcha discovery.
