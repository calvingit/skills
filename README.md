# Agent Skills

个人 Agent skills 集合。

## 目录

- `skills/global/`：来自全局 `~/.agents/skills`，提供工具、文档、委托和通用工作流。
- `skills/engineering/`：跨 **Flutter、Web、后端** 等技术栈的通用工程流程，不绑定具体框架、项目目录或业务组件。

## Global Skills

| Skill | 用途 |
| --- | --- |
| `claude-coder` | 将明确的编码、修复、重构或测试任务委托给 Claude Code。 |
| `codex-reviewer` | 使用 Codex CLI 执行代码分析、重构或自动编辑。 |
| `find-docs` | 查询开发技术、库、SDK 和 CLI 的最新文档。 |
| `fuck-my-shit-mountain` | 对项目进行证据驱动的全面工程审计。 |
| `handoff` | 将当前任务整理为可供下一次会话接续的交接文档。 |
| `humanizer-zh` | 清理中文文本中的 AI 味、翻译腔和模板化表达。 |
| `kimi-worker` | 将明确的编码任务委托给 Kimi CLI。 |
| `pi-agent` | 使用 Pi CLI 获取第二意见、委员会审查或执行受限实现。 |
| `prompt-optimizer` | 优化任务提示词的目标、上下文、边界、输出和验证条件。 |
| `resolving-merge-conflicts` | 调查并解决 Git merge/rebase 冲突。 |
| `tavily-best-practices` | 设计 Tavily 搜索、提取、爬取和研究集成。 |
| `tavily-cli` | 通过 Tavily CLI 进行网页搜索、提取、爬取和研究。 |
| `tavily-crawl` | 批量爬取网站并提取多个页面内容。 |
| `tavily-dynamic-search` | 编程式筛选网页搜索结果，减少无关上下文。 |
| `tavily-extract` | 从指定 URL 提取干净的 Markdown 或文本。 |
| `tavily-map` | 发现网站 URL 结构，不提取页面正文。 |
| `tavily-research` | 基于多来源开展带引用的深度研究。 |
| `tavily-search` | 获取面向 Agent 优化的网页搜索结果。 |
| `teach` | 在工作区内组织连续的主题学习、参考资料和学习记录。 |
| `url-to-markdown` | 将公开网页转换为本地 Markdown 文件。 |

## Engineering Skills

| Skill | 用途 |
| --- | --- |
| `code-review` | 分别从规范和需求两个轴审查代码 diff 或任务文档。 |
| `debug` | 基于复现证据定位并修复 bug、性能回归和不稳定行为。 |
| `domain-modeling` | 统一领域术语，维护领域模型和架构决策记录。 |
| `examine-architecture` | 调查模块边界、依赖、ownership、接口和测试面，输出治理候选。 |
| `grilling` | 通过问题澄清需求、边界、风险和设计决策，不写代码。 |
| `implement` | 按已确认的 `SPEC.md` 与 `PLAN.md` 实现、验证和审查任务。 |
| `loop` | 按轮次自动推进实现、简化、验证和审查，直到任务收尾。 |
| `simplify` | 在行为不变前提下删除冗余抽象、测试专用接口和偶然复杂度。 |
| `to-spec` | 将已收敛需求落盘为可追踪的 `SPEC.md` 与 `PLAN.md`。 |
| `wayfinding` | 对不确定技术领域进行跨会话探索，维护地图和决策记录。 |

## 使用

按需将目标 skill 目录复制到 Agent 客户端的 skills 目录；skill 内的脚本、参考文档和模板随目录一起使用。
