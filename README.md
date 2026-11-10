# Agent Skills

个人 Agent Skills 集合。包含后端生产实践、文档处理和工作会话/工具能力。可用于 Claude Code、Codex 等 Coding Agent，不绑定单一框架或 Runtime。

> 工程工作流 Skill（需求、设计、拆票、实现、验证、审查）已废弃，请改用 [cstack](https://github.com/calvingit/cstack)。本 README 是仓库入口，各插件的 skill 说明在插件目录的 README 里。维护前先读[维护规则](#maintenance-rules维护规则)。

## Getting Started（安装）

### 插件安装

仓库按分类拆成三个插件，都在市场 `calvingit` 里，按需装。每个插件的 skill 列表和用法见各自的 README：

| 插件 | 内容 |
| --- | --- |
| [`zstack-backend`](./Backend/README.md) | 后端：API 契约、事件驱动、Java、MySQL/MongoDB/Redis |
| [`zstack-documents`](./Documents/README.md) | 文档：同步、中文术语、去 AI 腔、网页转 Markdown |
| [`zstack-work`](./Work/README.md) | 日常工作：讲解、交接、提示词优化、搜索、教学、上下文审查、AGENTS.md 优化、文档查询、外部 Agent CLI |

各工具的装法（以 `zstack-work` 为例，其他插件换个名字）：

| 工具 | 安装 |
| --- | --- |
| Claude Code | `/plugin marketplace add calvingit/skills`，再 `/plugin install zstack-work@calvingit` |
| Codex | `codex plugin marketplace add calvingit/skills`，再 `codex plugin add zstack-work@calvingit` |
| ZCode | 设置 → 插件 → 创建 → 添加插件市场，填 `calvingit/skills`，再在 个人 分段安装 |

更新、本地调试和发版说明见 [INSTALL.md](./INSTALL.md)。原来的 `zstack` 插件已经删除，装过的话先卸载它再装新插件。原先的 `zstack-engineering` 也已删除，工程工作流请改用 [cstack](https://github.com/calvingit/cstack)。

### 外部引用的插件

市场里还挂了一个外部插件 `supply-chain-risk-auditor`，来自 [trailofbits/skills](https://github.com/trailofbits/skills/tree/5c99c03fb8a9ea568432ecbcba5d86e9f4ac2bf0/plugins/supply-chain-risk-auditor)，用来审计 npm、PyPI、Go 依赖的供应链风险。它的许可证是 CC BY-SA 4.0，所以没有复制进本仓库，市场条目只是指向原仓库，并固定在提交 `5c99c03`。要跟进上游，改各个 `marketplace.json` 里的提交号即可。

```bash
claude plugin install supply-chain-risk-auditor@calvingit
```

运行它需要 uv 和 Python 3.11 以上，最好也装上 `gh`。

审计相关的 `security-audit`（Cloudflare）同样只引用、不复制，固定在提交 `c1c8a8c`，MIT：

```bash
claude plugin install security-audit@calvingit
```

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
4. 带 `scripts/` 的 Skill（如 `agent-tool`、`url-to-markdown`）需要本机有对应依赖（多为 Python 3 / Bash）；缺依赖时按该 Skill 正文说明处理。
5. 若曾从 `global/` 或 `Engineering/` 安装 Skill，需按新路径重装：`context-audit`、`improve-agents-md`、`find-docs` 与 `agent-tool` 现位于 `Work/`。原先的工程工作流 Skill 已迁至 [cstack](https://github.com/calvingit/cstack)。

## 目录

| 目录 | 内容 |
| --- | --- |
| [`Backend/`](./Backend/) | 插件 zstack-backend |
| [`Documents/`](./Documents/) | 插件 zstack-documents |
| [`Work/`](./Work/) | 插件 zstack-work |
| [`scripts/`](./scripts/) | 仓库检查脚本 |
| [INSTALL.md](./INSTALL.md)、[RELEASING.md](./RELEASING.md) | 安装、更新与发版 |

每个插件目录的结构相同：`.claude-plugin/plugin.json`、`README.md`、`skills/<skill>/SKILL.md`。许可见根目录 [`LICENSE`](./LICENSE)；第三方来源见 [`ATTRIBUTIONS.md`](./ATTRIBUTIONS.md)。

## Maintenance Rules（维护规则）

约束如何治理这套 Skills：什么时候新增、合并或删除，改动后如何验证。单个 Skill 怎么用见各自的说明。

### 新增 Skill

只有真实任务证明现有职责无法承接某项能力时，才提出新增方案。不新增通用编排层、Runtime 抽象或 CI（不添加 `.github/workflows`），优先修正已有职责、项目配置和工具入口。新增的 Skill 须满足：

- 原子、独立：有自己的判断目标和停止点，单独安装也能使用，不依赖另一个 Skill 的内部细节。
- 通用：不绑定语言、框架或 Agent Runtime；项目实现细节、领域术语、ADR、Git 规则和测试约定由目标仓库维护。
- 不是项目知识：项目本地的验证入口属于项目，不等于增加全局 Skill。

### 合并、精简与删除

- 判断目标和停止点不同的 Skill 保留，不因检查同一份代码或测试就合并。
- 通过组合复用规则，不复制另一 Skill 的执行细节；各 Skill 不复制完整的流程路由表，只保留本 Skill 的硬性停止条件。
- 精简时不能静默删掉已确认的能力，例如自动记录 decisions、术语对齐和 ADR。
- 新增限制必须对应明确需求或已观察到的问题；通用常识、重复要求、分类教学和假设性防护不进入正文。
- 重复出现且可确定性判断的问题，先考虑用 script、schema、lint、test 或 metadata 约束，不继续往 SKILL.md 叠加提示词；只有需要上下文判断或跨 Runtime 解释的规则才写成文字。不要为了一次偶发输出引入新工具。
- 优先修正有问题的局部，不因一次输出不理想就重写整体流程，也不以行数作为质量指标。

维护某个 Skill 时只读相关文档，普通修改不要求预读全部 Skills。

### 上游适配

源自上游的 Skill 以上游原版为基础，只添加确有需要的适配；自行设计的 Skill 不强行套用上游结构。改动前先核对原文，保留核心机制、关键术语和交互节奏，记录来源与适配理由。适配集中在项目约定、文档位置、必要的技能组合和 Runtime 能力差异。

### 文字约定

文档用自然的中文，避免 AI 腔、翻译腔和模板化表达（可用 `unslop` 检查）；SKILL.md 正文沿用各自现有语言。

### 验证

| 改动 | 方法 | 能证明什么 |
| --- | --- | --- |
| 任何文档或 Skill | `python3 scripts/check_repo.py`（本地链接与锚点、SKILL.md frontmatter、`agents/openai.yaml` 基本格式）和 `git diff --check`；改动插件清单时运行 `claude plugin validate .` | 只证明格式和引用有效，不证明路由、约束强度或 Runtime 加载 |
| 较大的流程改动 | 在隔离目录用当前候选 Skill 演练受影响的真实场景，检查实际决定、文件和观察 | 只覆盖演练过的场景 |
| 后端 Skill | 用受影响的后端场景做隔离演练 | 文本演练不等于真实数据库测试 |

按改动风险选择，不必每次跑全部。演练时记录候选（`HEAD` 加未提交改动）、实际命令、退出码、关键输出和覆盖缺口；只给执行者原始请求和输入，不附期望答案；验收用独立上下文。缺少前提（如 Python 3.10+、Git）时报告，不静默安装。

审阅文档不能证明 Runtime 生命周期、真实项目 GUI 质量或长期 token / 耗时改善；声称效果改善前，用相同任务、模型和上下文比较关键遗漏、无效追问、用户纠正和阅读负担。

### Retro 与实验

- 会话级系统性问题收集真实证据，只观察、诊断并路由给现有负责方；没有正式 retro Skill，也不自动进入交付流程。
- 流程调整须有真实证据并经评审。
