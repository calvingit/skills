# AGENTS.md 兼容性说明

只在创建、移动或合并不同 Agent 运行环境的指令入口时读取本文件。以下内容最后核实于 2026-09-04；发现方式可能变化，执行修改前应重新检查所链接的官方文档。

## 共享格式

- [AGENTS.md 项目](https://github.com/agentsmd/agents.md)将 `AGENTS.md` 定义为开放的仓库指令 Markdown 格式。
- 不同运行环境和使用方式的支持程度并不相同。文件名相同，不代表发现方式、优先级、大小限制或覆盖规则也相同。

## Codex

- [OpenAI：使用 AGENTS.md 提供自定义指令](https://developers.openai.com/codex/agent-configuration/agents-md)
- [OpenAI：Codex 最佳实践](https://developers.openai.com/codex/learn/best-practices)

Codex 依次加载全局指令，以及从仓库根目录到当前工作目录的项目指令。路径越具体，内容在合并后的指令中越靠后。Codex 也支持 `AGENTS.override.md`；修改指令层级前，需从官方文档确认当前限制和优先级。

## Claude Code

- [Anthropic：Claude 如何读取项目说明](https://code.claude.com/docs/en/memory#agentsmd)

Claude Code 使用 `CLAUDE.md` 作为项目指令入口。仓库以 `AGENTS.md` 作为共享依据时，官方文档建议使用只导入 `@AGENTS.md` 的最小 `CLAUDE.md`；没有 Claude 专用补充时也可以使用符号链接。不要维护第二份内容相同的完整文件。

## GitHub Copilot

- [GitHub：添加仓库自定义指令](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions)
- [GitHub：自定义指令支持情况](https://docs.github.com/en/copilot/reference/custom-instructions-support)

GitHub Copilot 的多种 Agent 功能支持 `AGENTS.md`，但 GitHub.com、IDE、CLI、云端 Agent 和代码审查功能之间存在差异。删除 `.github/copilot-instructions.md` 或其他已经生效的入口前，先检查最新支持情况。

## 对内容设计的影响

共享 `AGENTS.md` 应满足：

- 使用标准 Markdown，不依赖特定模型的注意力标签；
- 使用仓库相对路径；
- 不依赖单一运行环境的斜杠命令、工具名或隐藏系统提示词；
- 对必须使用其他文件名的工具，只保留很薄的入口文件；
- 验证项目实际使用的工具和启动目录。

## 方法参考

本 Skill 的筛选与审查方法也参考了以下社区实现。它们只用于设计参考，不能作为运行环境行为的依据：

- [HumanLayer `improve-claude-md`](https://github.com/humanlayer/skills/blob/main/plugins/improve-claude-md/skills/improve-claude-md/SKILL.md)：根据相关性筛选内容，并主动压缩上下文；其中面向特定模型的 XML 写法没有用于共享 `AGENTS.md`。
- [Sentry `agents-md`](https://github.com/getsentry/skills/blob/main/skills/agents-md/SKILL.md)：强调精简指令、准确命令、仓库相对路径和单一共享依据。
- [`agents-md-optimizer`](https://github.com/CaesiumY/agents-md-optimizer)：按可发现性筛选内容，并从现有资料中寻找需要长期记录的易错点。
