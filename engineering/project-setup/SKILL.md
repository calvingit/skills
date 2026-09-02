---
name: project-setup
description: "用于检测并初始化项目工程工作流约定与需求权威入口；变更须用户确认。"
---

# Project Setup

把目标仓库已有的工程工作流、domain docs、可选 issue tracker 与 triage 约定整理为根级 `AGENTS.md` 中的一段稳定配置。它是可选的约定持久化助手，不是其他 engineering Skills 的运行前置条件。

## Resolution contract

engineering Skills 按以下优先级解析项目约定：

1. 用户在当前任务中的明确指定；
2. 当前作用域适用的 `AGENTS.md` 中 `Engineering Skills Profile`；
3. 仓库已有目录、文档和工具所证明的约定；
4. Skill 自身的通用默认行为；
5. 仍有会改变落盘位置或行为的歧义时再询问用户。

没有 Profile、用户取消 setup 或某项保持 `auto` 时，继续动态发现，不得停止其他 Skill。

## Stable settings only

Profile 只记录跨任务稳定的入口和策略：

- task contract 根目录与任务目录命名规则；
- 长期项目上下文；
- 领域术语来源；
- 架构权威入口；
- 需求权威的可访问模式与项目内说明入口；
- ADR 目录或 `auto`；
- 已完成任务契约的归档目录或 `auto`；
- 可选 issue tracker 模式与项目内操作说明入口；
- triage skill 可用或用户明确启用时采用的 label vocabulary。

不要把以下内容变成可配置变量：

- `SPEC.md` 与 `tickets/` 的名称及其契约职责；
- 当前任务目录、当前 task、进度、retry、iteration 或 verification evidence；
- 具体测试命令、Agent/模型选择或 commit/push 权限；
- 临时报告路径。

不预建空 ADR、示例 SPEC 或 tickets/ 占位目录。真正需要产物时由对应 Skill 按项目约定创建。

## Detect before asking

先只读检查：

- 适用的 `AGENTS.md`、README、CONTRIBUTING 和更深层指令；
- 已有 task/spec、project context、glossary、architecture、ADR 和 archive 结构；
- PRD、需求文档或其他 requirement authority 是否位于仓库、已集成外部工具，或只能由用户提供快照；
- Git remote、已有 issue tracker instructions、`.scratch/` 或其他协作约定；
- `triage` skill 是否可用，以及仓库是否已有对应 labels；
- Git 状态，避免覆盖用户现有改动。

把候选值区分为 `confirmed`、`inferred`、`missing` 和 `conflict`。不能仅因某个常见目录存在就把它判定为权威；需要项目文档、实际使用或用户指定支持。

## Ask once

在写入前，一次性展示：

1. 检测结果及依据；
2. 完整推荐 Profile；
3. 将修改的 `AGENTS.md` 和任何明确请求的新长期文档；
4. 以下选择：接受推荐、自定义配置、某项设为 `auto`、取消。

用户在调用 setup 时已经明确给出所有选择时，把这些输入视为本次回答，不重复提问。正常路径只询问一次；只有自定义值无效、与现有约定冲突或会覆盖已有内容时才继续确认。

`auto` 表示不固定该项，消费者继续动态发现；它不表示禁用相关能力。取消表示不修改任何文件。

## Profile format

在根级 `AGENTS.md` 使用以下受控区块；尖括号表示项目自行确认的值，不是默认路径。默认 `requirement_authority.mode: auto`、`requirement_authority.instructions: auto`、`issue_tracker.mode: local`、`issue_tracker.instructions: auto`、`triage.enabled: false`：

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

路径字段必须相对仓库根目录，不能指向用户主目录、全局 Skills 仓库或仓库外位置。不要从上述占位符推导项目目录；`auto` 表示消费者继续动态发现项目现有约定。

`requirement_authority` 与 `issue_tracker` 是正交配置：代码托管或 issue tracker 可位于 GitLab，而 PRD 仍可能位于不可集成的飞书或企业微信。其模式含义如下：

- `repository`：规范需求位于仓库内；`instructions` 指向项目内的读取说明或索引。
- `integrated`：规范需求位于 Agent 可通过项目已配置工具读取的外部系统；`instructions` 指向项目内的访问与优先级说明。
- `external-manual`：规范需求位于 Agent 无法直接访问的外部系统；由用户提供当前任务的确认快照，Agent 不得声称已验证原始来源。
- `auto`：不固定模式，由消费者在每项任务中动态发现；无法确认时不得猜测。

Profile 只保存稳定的模式和项目内说明入口，不保存当前 PRD 内容、临时链接或某次任务的需求快照。`to-spec` 是主要消费者；`grilling` 和 `wayfinding` 只用它判断哪些需求事实必须由用户提供。下游 `to-tickets`、`quick-implement`、`loop` 和 `code-review` 只消费已确认的 SPEC 或 tickets，不直接解释该配置。

`triage.enabled: false` 时省略 `labels`。只有检测到 triage skill 或用户明确启用时才询问 labels，默认使用 `needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。GitHub、GitLab 或 other 模式的具体操作写入 `issue_tracker.instructions` 指向的项目内文档；Profile 只保存稳定入口。

## Write safely

- marker 不存在时新增一个 Profile 章节；完整且唯一时原位更新。
- marker 缺失一端、重复出现或区块与其他项目规则冲突时停止，不猜测覆盖范围。
- 已有 Profile 视为合法的部分配置。保留未知字段和已经确认的值；缺少当前模板中的字段不算错误，只在用户确认后补充或修改对应字段，不得为了匹配模板整体重写 Profile。
- 已配置的路径字段必须存在，除非用户明确选择创建对应长期文档；目录 pattern、策略枚举和 `auto` 不按路径检查。
- 保留 `AGENTS.md` 其他内容、顺序和用户已有改动。
- 重复执行同一配置不得产生第二个区块或无意义 diff。
- 写入后重新读取 Profile，验证路径、marker 唯一性和 Git diff；不自动 commit 或 push。

## Report

汇报采用的推荐/自定义项、保持 `auto` 的项、实际修改、创建的长期文档和未验证内容。不要把静态路径存在描述为所有 Runtime 已成功加载。
