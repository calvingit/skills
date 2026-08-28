# Agent Skills

个人 Agent skills 集合。

## 目录

- `skills/global/`：来自全局 `~/.agents/skills`，提供工具、文档、委托和通用工作流。
- `skills/engineering/`：跨 **Flutter、Web、后端** 等技术栈的通用工程流程，不绑定具体框架、项目目录或业务组件。

## Global Skills

| Skill | 用途 |
| --- | --- |
| [`claude-coder`](./skills/global/claude-coder/SKILL.md) | 将明确的编码、修复、重构或测试任务委托给 Claude Code。 |
| [`codex-reviewer`](./skills/global/codex-reviewer/SKILL.md) | 使用 Codex CLI 执行代码分析、重构或自动编辑。 |
| [`find-docs`](./skills/global/find-docs/SKILL.md) | 查询开发技术、库、SDK 和 CLI 的最新文档。 |
| [`fuck-my-shit-mountain`](./skills/global/fuck-my-shit-mountain/SKILL.md) | 对项目进行证据驱动的全面工程审计。 |
| [`handoff`](./skills/global/handoff/SKILL.md) | 将当前任务整理为可供下一次会话接续的交接文档。 |
| [`humanizer-zh`](./skills/global/humanizer-zh/SKILL.md) | 清理中文文本中的 AI 味、翻译腔和模板化表达。 |
| [`kimi-worker`](./skills/global/kimi-worker/SKILL.md) | 将明确的编码任务委托给 Kimi CLI。 |
| [`pi-agent`](./skills/global/pi-agent/SKILL.md) | 使用 Pi CLI 获取第二意见、委员会审查或执行受限实现。 |
| [`prompt-optimizer`](./skills/global/prompt-optimizer/SKILL.md) | 优化任务提示词的目标、上下文、边界、输出和验证条件。 |
| [`resolving-merge-conflicts`](./skills/global/resolving-merge-conflicts/SKILL.md) | 调查并解决 Git merge/rebase 冲突。 |
| [`tavily-best-practices`](./skills/global/tavily-best-practices/SKILL.md) | 设计 Tavily 搜索、提取、爬取和研究集成。 |
| [`tavily-cli`](./skills/global/tavily-cli/SKILL.md) | 通过 Tavily CLI 进行网页搜索、提取、爬取和研究。 |
| [`tavily-crawl`](./skills/global/tavily-crawl/SKILL.md) | 批量爬取网站并提取多个页面内容。 |
| [`tavily-dynamic-search`](./skills/global/tavily-dynamic-search/SKILL.md) | 编程式筛选网页搜索结果，减少无关上下文。 |
| [`tavily-extract`](./skills/global/tavily-extract/SKILL.md) | 从指定 URL 提取干净的 Markdown 或文本。 |
| [`tavily-map`](./skills/global/tavily-map/SKILL.md) | 发现网站 URL 结构，不提取页面正文。 |
| [`tavily-research`](./skills/global/tavily-research/SKILL.md) | 基于多来源开展带引用的深度研究。 |
| [`tavily-search`](./skills/global/tavily-search/SKILL.md) | 获取面向 Agent 优化的网页搜索结果。 |
| [`teach`](./skills/global/teach/SKILL.md) | 在工作区内组织连续的主题学习、参考资料和学习记录。 |
| [`url-to-markdown`](./skills/global/url-to-markdown/SKILL.md) | 将公开网页转换为本地 Markdown 文件。 |

## Engineering Skills

| Skill | 用途 |
| --- | --- |
| [`code-review`](./skills/engineering/code-review/SKILL.md) | 分别从规范和需求两个轴审查代码 diff 或任务文档。 |
| [`debug`](./skills/engineering/debug/SKILL.md) | 基于复现证据定位并修复 bug、性能回归和不稳定行为。 |
| [`domain-modeling`](./skills/engineering/domain-modeling/SKILL.md) | 统一领域术语，维护领域模型和架构决策记录。 |
| [`examine-architecture`](./skills/engineering/examine-architecture/SKILL.md) | 调查模块边界、依赖、ownership、接口和测试面，输出治理候选。 |
| [`grilling`](./skills/engineering/grilling/SKILL.md) | 通过问题澄清需求、边界、风险和设计决策，不写代码。 |
| [`implement`](./skills/engineering/implement/SKILL.md) | 按已确认的 `SPEC.md` 与 `PLAN.md` 实现、验证和审查任务。 |
| [`loop`](./skills/engineering/loop/SKILL.md) | 按轮次自动推进实现、简化、验证和审查，直到任务收尾。 |
| [`simplify`](./skills/engineering/simplify/SKILL.md) | 在行为不变前提下删除冗余抽象、测试专用接口和偶然复杂度。 |
| [`to-spec`](./skills/engineering/to-spec/SKILL.md) | 将已收敛需求落盘为可追踪的 `SPEC.md` 与 `PLAN.md`。 |
| [`wayfinding`](./skills/engineering/wayfinding/SKILL.md) | 对不确定技术领域进行跨会话探索，维护地图和决策记录。 |

## 使用

按需将目标 skill 目录复制到 Agent 客户端的 skills 目录；skill 内的脚本、参考文档和模板随目录一起使用。
