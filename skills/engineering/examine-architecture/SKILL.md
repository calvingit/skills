---
name: examine-architecture
description: "Used when 用户明确要求架构诊断时（触发词：架构审视、架构诊断、模块边界、架构债）。对任意技术栈的代码库调查 Module 的 Depth、ownership、Seam、依赖与 test surface，输出有证据支撑的治理候选；不实现修复。"
---

# Examine Architecture

## Goal

对任意技术栈的代码库执行只读架构调查，发现少量有当前证据支撑、值得继续治理的候选。关注理解成本、变更扩散、职责归属、依赖关系和 test surface，而不是套用固定架构风格。

使用 `Module`、`Interface`、`Implementation`、`Depth`、`Seam`、`Adapter`、`Leverage`、`Locality` 作为 canonical terms。先读取 [`docs/skills/design-vocabulary.md`](../../../docs/skills/design-vocabulary.md) 作为词汇来源。

## Boundaries

- 不修改源码、测试、配置、规则、baseline 或历史报告。
- 不把旧报告、命名约定、静态检查或架构文档当成当前事实；用当前代码和当前命令验证。
- 不把普通 bug 自动升级为架构问题；只有证据表明问题来自 ownership、Seam、依赖、状态生命周期或 test surface 时才纳入。
- 不为了凑数量扩大扫描范围，也不把个人风格偏好写成 finding。
- 候选阶段只描述证据、摩擦、期望结果、约束和未知，不设计具体 Interface，不给出文件级实现配方。

## Workflow

### 1. Scope before scanning

先写清本轮要回答的架构问题和成功条件。

- 用户指定 Module、子系统、文件或痛点时，以该范围及其直接调用和依赖为主。
- 用户未指定范围且仓库有 Git 历史时，从近期反复改动的路径寻找 hot spots，再选择少量区域调查。
- 没有可用历史时，从仓库说明、顶层结构、主要入口和测试布局建立最小地图。
- 范围仍过大时，先说明本轮选取的区域和未覆盖部分，不假装完成全仓库审计。

调查深度跟随范围分级，不强制同一套流程：用户指定了窄范围（单一 Module、文件或明确痛点）且问题已具体时，走轻量调查——跳过 hot spot 发现和无关的项目检查发现，直接进入 deep-read，报告可只含成立的 finding 与证据；范围大或问题未成形时才执行完整流程的每一步。无论哪种分级，finding gate 和 evidence 区分（Observed / Inferred / Unknown）不放松。

### 2. Discover project context

按实际存在情况读取，而不是假定固定路径：

- 仓库级 Agent 指令、README、架构文档、ADRs 和领域词汇；
- 构建清单、依赖声明、入口、Module 边界和测试配置；
- 与当前范围有关的 lint、依赖检查、架构守卫或 baseline。

项目自带检查只是一类 evidence。仅在与当前问题相关、只读且可运行时执行；记录命令、退出状态和必要输出。不存在此类工具不是 blocker，不创建替代规则或 baseline。

### 3. Survey candidates

先记录 candidate hypothesis，不立即给 refactor 方案。候选可来自：

1. 用户指出的架构摩擦；
2. 理解一个概念需要来回跳转的 hot spot；
3. 反复改动、反复回归或难以通过公开 Interface 测试的区域；
4. 依赖、状态、数据或副作用跨 Seam 泄漏的位置；
5. 当前代码证实的项目规则或工具违规。

按需使用 [`references/classification-guide.md`](references/classification-guide.md) 的 investigation lenses。它们不是必须逐项满足的规则，也不是技术栈分类表。

### 4. Deep-read the strongest candidates

对少量高价值候选追踪完整关系：目标 Module、代表性调用方、下游依赖、composition/configuration 入口、相关测试，以及必要的数据流或控制流。读取数量由证明或否定 hypothesis 所需证据决定，不设置固定文件配额。

每个结论区分：

- **Observed**：当前文件、symbol、调用关系、测试或命令直接证明；
- **Inferred**：由多项 Observed evidence 推导，明确说明推理；
- **Unknown**：缺少信息，不能假设成立。

只在判断 Module 形状时使用 [`references/deletion-test.md`](references/deletion-test.md)。Deletion Test 不是所有架构问题的 gate：一个 deep Module 仍可能位于错误的 Seam、拥有错误的状态或制造错误的依赖方向。

### 5. Rank without over-specifying

根据 evidence strength、实际摩擦、变更频率和影响范围，将候选标为：

- `Strong`：证据充分，问题正在产生明确成本；
- `Worth exploring`：方向可信，但仍有关键未知；
- `Speculative`：只有弱信号，保留观察而不建议立项。

优先级不是 finding 数量竞赛。没有成立的候选时，输出 no finding，并记录已排除的 hypothesis。

### 6. Write the report and stop

使用 [`references/report-template.md`](references/report-template.md) 生成 Markdown 报告。写入按 `to-spec` skill 任务目录规则确定的稳定位置（无现成任务目录时先创建），文件名使用 `architecture-exam-<timestamp>.md`；不要写入操作系统临时目录，跨会话把报告路径和 candidate ID 交给后续流程时依赖该路径可读。报告是调查工作产物，不进入 living spec；只有用户明确要求归档时才移动到长期位置。

重新读取报告，确认每个 finding 都有 evidence、friction、desired outcome、unknowns 或 non-goals。报告完成后停止并让用户选择候选，不在本 Skill 内开始实现。

选中的候选需要收敛决策或生成任务文档时，将报告路径和 candidate ID 交给 `to-spec` skill（必要时先经 `grilling` 收敛）。Interface 或 Seam 形状的设计在 specification / 实现阶段按 `docs/skills/design-vocabulary.md` 的原则收敛，不要在候选调查阶段提前完成该设计。

## Done when

- 已说明调查范围、成功条件和未覆盖部分。
- 已动态发现当前项目的 authority 和可用检查，没有假定技术栈或固定路径。
- 每个 finding 都由当前代码、关系、测试或命令 evidence 支撑，并区分 Observed、Inferred 和 Unknown。
- Deletion Test 只用于 Module shape，没有掩盖 ownership、Seam 或依赖问题。
- 报告没有实现配方，已写入稳定任务目录并重新读取。
- 已给出 top candidate、no finding 或继续调查的明确结论，并停止在用户选择之前。
