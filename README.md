# Agent Skills

个人 Agent skills 集合。

## 目录

- `global/`：来自全局 `~/.agents/skills`，提供工具、文档、委托和通用工作流。
- `engineering/`：通用工程 Coding 流程，不绑定具体框架、项目目录、业务组件或 Agent Runtime。

## Global Skills

| Skill | 用途 |
| --- | --- |
| [`claude-coder`](./global/claude-coder/SKILL.md) | 将明确的编码、修复、重构或测试任务委托给 Claude Code。 |
| [`codex-executor`](./global/codex-executor/SKILL.md) | 将边界清晰的编码任务委托给 Codex CLI 子智能体执行。 |
| [`find-docs`](./global/find-docs/SKILL.md) | 查询开发技术、库、SDK 和 CLI 的最新文档。 |
| [`fuck-my-shit-mountain`](./global/fuck-my-shit-mountain/SKILL.md) | 对项目进行证据驱动的全面工程审计。 |
| [`handoff`](./global/handoff/SKILL.md) | 将当前任务整理为可供下一次会话接续的交接文档。 |
| [`humanizer-zh`](./global/humanizer-zh/SKILL.md) | 清理中文文本中的 AI 味、翻译腔和模板化表达。 |
| [`kimi-worker`](./global/kimi-worker/SKILL.md) | 将明确的编码任务委托给 Kimi CLI。 |
| [`pi-agent`](./global/pi-agent/SKILL.md) | 使用 Pi CLI 获取第二意见、委员会审查或执行受限实现。 |
| [`prompt-optimizer`](./global/prompt-optimizer/SKILL.md) | 优化任务提示词的目标、上下文、边界、输出和验证条件。 |
| [`resolving-merge-conflicts`](./global/resolving-merge-conflicts/SKILL.md) | 调查并解决 Git merge/rebase 冲突。 |
| [`tavily-best-practices`](./global/tavily-best-practices/SKILL.md) | 设计 Tavily 搜索、提取、爬取和研究集成。 |
| [`tavily-cli`](./global/tavily-cli/SKILL.md) | 通过 Tavily CLI 进行网页搜索、提取、爬取和研究。 |
| [`tavily-crawl`](./global/tavily-crawl/SKILL.md) | 批量爬取网站并提取多个页面内容。 |
| [`tavily-dynamic-search`](./global/tavily-dynamic-search/SKILL.md) | 编程式筛选网页搜索结果，减少无关上下文。 |
| [`tavily-extract`](./global/tavily-extract/SKILL.md) | 从指定 URL 提取干净的 Markdown 或文本。 |
| [`tavily-map`](./global/tavily-map/SKILL.md) | 发现网站 URL 结构，不提取页面正文。 |
| [`tavily-research`](./global/tavily-research/SKILL.md) | 基于多来源开展带引用的深度研究。 |
| [`tavily-search`](./global/tavily-search/SKILL.md) | 获取面向 Agent 优化的网页搜索结果。 |
| [`teach`](./global/teach/SKILL.md) | 在工作区内组织连续的主题学习、参考资料和学习记录。 |
| [`url-to-markdown`](./global/url-to-markdown/SKILL.md) | 将公开网页转换为本地 Markdown 文件。 |

## Engineering Skills

Engineering skills 不是完整的软件开发框架，也不会接管项目流程。它们把可以跨语言、跨框架复用的软件工程方法拆成独立、可组合的 Agent Skills。

### 设计原则

- **通用优先**：不绑定语言、框架、目录结构、业务组件或 Agent Runtime。
- **项目规则外置**：coding standards、架构约束、领域术语、ADR、Git 规则和测试约定属于目标仓库，而不是 Skill。
- **单一职责**：每个 Skill 解决一种明确的工程问题，避免把完整生命周期塞进一个巨型 prompt。
- **可组合**：workflow 可以调用 engineering discipline，但不复制其规则；每类规则只保留一个 owner。
- **证据驱动**：代码事实、spec、测试、运行结果和 review evidence 优先于模型自报。
- **渐进式上下文**：只读取当前任务需要的项目上下文，不假定固定 `docs/**` 路径，也不预加载整套项目知识。
- **可选项目配置**：`project-setup` 可以把已确认的稳定入口写入项目 `AGENTS.md`；未配置的项目继续动态发现，不以 setup 作为使用前置条件。
- **Runtime 能力优先**：Agent Runtime 已经提供可靠的 goal、task persistence、pause/resume、session recovery 等能力时，优先复用 Runtime 原生能力，不在 Skill 层重复实现生命周期控制。

使用时按以下优先级发现项目上下文：

1. 用户明确要求和当前任务约束。
2. 仓库级 Agent 指令与项目文档。
3. 已存在的 coding standards、架构文档、ADR、领域词汇、测试与构建配置。
4. 当前代码、调用链和可运行验证所证明的事实。

项目使用 `project-setup` 后，各 Skill 按“当前用户指定、适用 `AGENTS.md` Profile、仓库已有结构、通用默认行为、仍有歧义时询问”的顺序解析约定。Profile 只保存稳定入口和策略，不保存运行进度或具体任务状态。

### Skill 类型

| 类型 | Skill | 职责 |
| --- | --- | --- |
| Project Setup | `project-setup` | 检测现有项目结构，一次性建议并持久化可选的 Engineering Skills Profile。 |
| Workflow | `grilling`, `to-spec`, `implement`, `wayfinding` | 组织需求澄清、规格化、实现或长期探索阶段。 |
| Engineering Discipline | `tdd`, `codebase-design`, `domain-modeling`, `code-review`, `debug`, `simplify`, `review-architecture` | 提供可复用的软件工程判断与实践。 |
| Execution Protocol | `loop` | 提供 Runtime-neutral 的 progress、evidence、iteration / retry 和 no-progress 规则；仅在 Runtime 缺少 long-running task 能力时承担最小执行控制。 |

几个关键边界：

```text
implement knows WHEN to test
tdd knows HOW to test

review-architecture judges WHETHER the current architecture is sound
codebase-design reasons about HOW the target boundary should look
simplify asks WHETHER a concept, state, contract or abstraction needs to exist at all

Runtime Goal owns lifecycle / pause / resume
loop defines WHAT counts as progress in each iteration
implement decides HOW to implement
```

### Skills 一览

| Skill | 用途 |
| --- | --- |
| [`project-setup`](./engineering/project-setup/SKILL.md) | 检测并初始化项目级 Engineering Skills 工作流约定；支持推荐、自定义、自动发现或取消。 |
| [`code-review`](./engineering/code-review/SKILL.md) | 分别从规范和需求两个轴审查代码 diff 或任务文档。 |
| [`codebase-design`](./engineering/codebase-design/SKILL.md) | 设计和评估 Module、Interface、Seam、Adapter 与依赖边界。 |
| [`debug`](./engineering/debug/SKILL.md) | 基于复现证据定位并修复 bug、性能回归和不稳定行为。 |
| [`domain-modeling`](./engineering/domain-modeling/SKILL.md) | 统一领域术语，并在满足条件时记录长期架构决策。 |
| [`review-architecture`](./engineering/review-architecture/SKILL.md) | 评审现有架构是否合理、是否符合项目约束与相关技术栈最佳实践，并输出有证据支撑的 findings。 |
| [`grilling`](./engineering/grilling/SKILL.md) | 通过问题澄清需求、边界、风险和设计决策，不写代码。 |
| [`implement`](./engineering/implement/SKILL.md) | 按已确认的需求契约实现、验证和审查任务。 |
| [`loop`](./engineering/loop/SKILL.md) | Runtime-neutral Loop Engineering protocol；定义 progress invariant、evidence、iteration / retry 和 no-progress gate，不替代已有 Runtime Goal。 |
| [`simplify`](./engineering/simplify/SKILL.md) | 在行为不变前提下删除没有当前生产 ownership 的偶然复杂度，包括 AI coding 沉积的 test-induced architecture、verification scaffolding 和推测性抽象。 |
| [`tdd`](./engineering/tdd/SKILL.md) | 使用 red-green 的 vertical-slice 循环，通过公开 Seam 验证行为。 |
| [`to-spec`](./engineering/to-spec/SKILL.md) | 将已收敛需求落盘为可追踪的 `SPEC.md` 与 `PLAN.md`。 |
| [`wayfinding`](./engineering/wayfinding/SKILL.md) | 对不确定技术领域进行跨会话探索，维护地图和决策记录。 |

### 如何选择 Engineering Skill

| 场景 | 推荐 Skill |
| --- | --- |
| 希望一次性统一任务目录、项目上下文、术语、ADR 或归档入口 | `project-setup`（可选） |
| 需求、边界或设计决策还没有收敛 | `grilling` |
| 目标已经明确，但关键技术路径仍处于 Fog of war | `wayfinding` |
| 需求已经收敛，需要生成正式任务契约 | `to-spec` |
| 路径明确，预计一次执行可以可靠完成 | `implement` |
| 路径明确，需要多轮自主推进，且 Runtime 已有 Goal / long-running task | 优先 Runtime Goal；需要统一工程迭代规则时参考 `loop` |
| 路径明确，需要多轮自主推进，但 Runtime 没有可靠 Goal / resume 能力 | `loop` |
| 已确认存在 bug，需要建立反馈循环并定位根因 | `debug` |
| 需要判断目标 Module、Interface、Seam、Adapter 或 dependency boundary 应如何设计 | `codebase-design` |
| 需要评审当前架构是否合理、是否符合项目约束或相关技术栈最佳实践 | `review-architecture` |
| 需要 test-first / red-green 实现行为 | `tdd` |
| 需要在行为不变前提下收缩当前 diff 或执行长期代码库 entropy reclamation | `simplify` |
| 代码或任务文档已经完成，需要检查规范与需求符合度 | `code-review` |

可以进一步简化为：

```text
需求不清楚                  → grilling
路径不清楚                  → wayfinding
需求已收敛要落盘            → to-spec
路径清楚且单次可完成         → implement
需要多轮，Runtime 有 Goal    → Runtime Goal + loop protocol（按需）
需要多轮，Runtime 无 Goal    → loop
根因不清楚                  → debug
当前架构是否合理            → review-architecture
目标架构边界怎么设计         → codebase-design
哪些维护义务其实不需要存在    → simplify
```

`loop` 不是 Goal 的替代品，也不是普通重试器。大部分现代 Coding Agent 已经能持久化目标、暂停并恢复任务，这些生命周期能力应该由 Runtime 自己管理。`loop` 主要补充跨 Runtime 可复用的工程执行语义：每轮必须产生新的 evidence 或有效状态变化，区分 engineering iteration 与 retry，并在 no-progress 时停止。

### Runtime Goal 与 Loop 的关系

推荐分层：

```text
Runtime Goal / Task
    │  lifecycle / persistence / pause / resume / recovery
    ▼
Loop Engineering protocol
    │  evidence / progress invariant / iteration / no-progress
    ▼
Engineering Skills
    ├── implement
    ├── tdd
    ├── debug
    ├── simplify
    └── code-review
```

如果外层 Goal 已经负责 continue/stop/checkpoint，不要再创建一个具有相同职责的 nested loop。此时 `loop` 只是执行协议，不是第二个 orchestrator。

### 典型组合

这些只是常见组合，不是强制生命周期。简单任务可以直接使用单个 Skill。

#### 普通 Feature

```text
grilling
   ↓
to-spec
   ↓
implement
   ├── tdd
   ├── simplify
   └── code-review
```

#### 大型且初始路径不清晰的任务

如果 Runtime 提供 Goal：

```text
wayfinding
    ↓
grilling
    ↓
to-spec
    ↓
Runtime Goal
    ↓
loop protocol
    ↓
implement
   ├── tdd
   ├── simplify
   └── code-review
```

如果 Runtime 没有可靠的 Goal / resume：

```text
wayfinding
    ↓
grilling
    ↓
to-spec
    ↓
loop
  └── implement
       ├── tdd
       ├── simplify
       └── code-review
```

#### Bug 修复

```text
debug
  ↓
reproduction
  ↓
root cause
  ↓
regression test
  ↓
fix
  ↓
simplify
```

#### 架构治理

```text
review-architecture
        ↓
      finding
        ↓
codebase-design
        ↓
grilling / to-spec
        ↓
implement
```

#### 长期 AI Coding 熵回收

```text
长期 Agent-driven development
        ↓
simplify Survey
        ↓
识别 support-only / test-induced / speculative obligations
        ↓
证明 runtime consumer、contract 与 behavior
        ↓
simplify Change
        ↓
删除完整维护义务并验证
```

这个流程针对“为了验证 AI 写得对不对而逐渐进入生产代码”的 abstraction、injection point、wrapper、hook、debug state、compatibility path 和实验残留。重点不是识别 AI 作者，而是判断这些维护义务是否仍有真实生产 ownership。

### 不需要 Skill 的情况

Skill 是工程方法，不是每个任务都必须经过的仪式。以下情况通常直接处理即可：

- 明确的一行或局部修改；
- 简单配置调整；
- 明确且低风险的机械性修改；
- 只需要查询事实或阅读代码；
- 已经有明确反馈循环，不需要额外工程流程的任务。

只有当 Skill 能明显降低不确定性、错误率或长期维护成本时再使用。

## 使用

按需将目标 Skill 目录复制到 Agent 客户端的 skills 目录；Skill 内的脚本、参考文档和模板随目录一起使用。README 负责说明 **What / Why / When / How they compose**，具体执行规则以各自 `SKILL.md` 为准。
