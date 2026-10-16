# Agent Skills

个人 Agent Skills 集合。以 Engineering 工作流为主（调研 → 需求 → 设计 → 实现 → 验证 → 审查），并包含后端生产实践、文档处理和工作会话/工具能力。可用于 Claude Code、Codex 等 Coding Agent，不绑定单一框架或 Runtime。

> 本 README 是仓库入口，各插件的 skill 说明在插件目录的 README 里。维护前先读[维护规则](#maintenance-rules维护规则)：Engineering Skills 处于收敛期，优先修正已有职责与入口，勿轻易新增全局工程 Skill。

## Getting Started（安装）

### 插件安装

仓库按分类拆成四个插件，都在市场 `calvingit` 里，按需装。每个插件的 skill 列表和用法见各自的 README：

| 插件 | 内容 |
| --- | --- |
| [`zstack-engineering`](./Engineering/README.md) | 工程工作流：需求、设计、拆票、实现、调试、评审、验证 |
| [`zstack-backend`](./Backend/README.md) | 后端：API 契约、事件驱动、Java、MySQL/MongoDB/Redis |
| [`zstack-documents`](./Documents/README.md) | 文档：同步、中文术语、去 AI 腔、网页转 Markdown |
| [`zstack-work`](./Work/README.md) | 日常工作：讲解、交接、提示词优化、搜索、教学 |

各工具的装法（以 `zstack-engineering` 为例，其他插件换个名字）：

| 工具 | 安装 |
| --- | --- |
| Claude Code | `/plugin marketplace add calvingit/skills`，再 `/plugin install zstack-engineering@calvingit` |
| Codex | `codex plugin marketplace add calvingit/skills`，再 `codex plugin add zstack-engineering@calvingit` |
| ZCode | 设置 → 插件 → 创建 → 添加插件市场，填 `calvingit/skills`，再在 个人 分段安装 |

更新、本地调试和发版说明见 [INSTALL.md](./INSTALL.md)。原来的 `zstack` 插件已经删除，装过的话先卸载它再装新插件。

### 外部引用的插件

市场里还挂了一个外部插件 `supply-chain-risk-auditor`，来自 [trailofbits/skills](https://github.com/trailofbits/skills/tree/5c99c03fb8a9ea568432ecbcba5d86e9f4ac2bf0/plugins/supply-chain-risk-auditor)，用来审计 npm、PyPI、Go 依赖的供应链风险。它的许可证是 CC BY-SA 4.0，所以没有复制进本仓库，市场条目只是指向原仓库，并固定在提交 `5c99c03`。要跟进上游，改各个 `marketplace.json` 里的提交号即可。

```bash
claude plugin install supply-chain-risk-auditor@calvingit
```

运行它需要 uv 和 Python 3.11 以上，最好也装上 `gh`。

另外三个前端相关的外部插件，同样只是引用、固定在某个提交：

| 插件 | 来源 | 许可证 |
| --- | --- | --- |
| `react-best-practices` | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills/tree/063bee94c3f4df8453406c830b0a7df0f2860278/skills/react-best-practices)，提交 `063bee9` | MIT（仓库没有 LICENSE 文件，只在 README 和 SKILL.md 里声明） |
| `vue-best-practices` | [vuejs-ai/skills](https://github.com/vuejs-ai/skills/tree/c9d355ff23f654309dd02006be671859df0a134c/skills/vue-best-practices)，提交 `c9d355f` | MIT |
| `web-quality-skills` | [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills/tree/afa8da942115f2961fdbfa80807ea0b232ff6c00)，提交 `afa8da9`，含性能、Core Web Vitals、可访问性、SEO 等 6 个 skill | MIT |

React 和 Vue 两个上游只有裸的 skill 目录、没有插件清单，所以条目把插件根指向上游的 `skills/` 目录，再用 `strict: false` 和 `skills` 字段只挑出其中一个 skill。Claude Code 和 Codex 已实测各加载 1 个 skill。

### 手动安装

把本仓库里需要的 Skill 目录放到所用 Agent 的 Skills 搜索路径；每个 Skill 是一个含 `SKILL.md` 的独立文件夹。

常见做法：

1. 克隆或加为子模块到本机，例如 `~/skills/calvingit-skills`。
2. 按需把 Skill 目录链接到 Agent 的 skills 根目录（文件夹名保持不变），例如：
   - Claude Code / 兼容实现：`~/.claude/skills/<skill-name> -> <repo>/<category>/skills/<skill-name>`
   - 项目内：`.agents/skills/<skill-name>`，或工具文档指定的路径
3. 不要把整库当成单个 Skill 安装。`scripts/` 和根目录的说明文件只用于维护本仓库，不是 Skill。
4. 带 `scripts/` 的 Skill（如 `agent-tool`、`url-to-markdown`、`graph-workflow`）需要本机有对应依赖（多为 Python 3 / Bash）；缺依赖时按该 Skill 正文说明处理。
5. 若曾从 `global/` 安装 Skill，需按新路径重装：`context-audit` 与 `agent-tool` 现位于 `Engineering/`，其余原 `global/` Skill 现位于 `Work/`。

## 目录

| 目录 | 内容 |
| --- | --- |
| [`Engineering/`](./Engineering/) | 插件 zstack-engineering；`docs/` 下是 Graph Workflow 与 Runtime 说明和图示 |
| [`Backend/`](./Backend/) | 插件 zstack-backend |
| [`Documents/`](./Documents/) | 插件 zstack-documents |
| [`Work/`](./Work/) | 插件 zstack-work |
| [`scripts/`](./scripts/) | 仓库检查脚本 |
| [INSTALL.md](./INSTALL.md)、[RELEASING.md](./RELEASING.md) | 安装、更新与发版 |

每个插件目录的结构相同：`.claude-plugin/plugin.json`、`README.md`、`skills/<skill>/SKILL.md`。许可见根目录 [`LICENSE`](./LICENSE)；第三方来源见 [`ATTRIBUTIONS.md`](./ATTRIBUTIONS.md)。

## Maintenance Rules（维护规则）

完整治理规则见 [Maintenance](./Engineering/skills/shared/maintenance.md)。要点：

- 收敛期：暂停新增全局工程 Skill，只有真实任务证明现有职责无法承接时才提出新增；新增的 Skill 须原子、独立、不绑定 Runtime。
- 不新增 Runtime 抽象、通用编排层，也不添加 CI（`.github/workflows`）。
- 文档用自然的中文，避免 AI 腔和翻译腔。
- 维护某个 Skill 时只读相关文档，普通修改不要求预读全部 Skills 或建立完整 SPEC / tickets。
- 提交前运行 `python3 scripts/check_repo.py`（链接、Skill 元数据，并调用 `Engineering/skills/shared/check.py` 跑状态脚本测试）和 `git diff --check`；改动插件清单时运行 `claude plugin validate .`。这些检查不能代替 Skill 行为、GUI 或 Runtime 验证，较大流程改动按维护规则做行为演练。
