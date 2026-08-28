---
name: domain-modeling
description: "Used when 维护领域术语表或架构决策记录时（触发词：领域建模、术语统一、ubiquitous language、CONTEXT.md、新增 ADR、记录架构决策）。"
---

# Domain Modeling

主动维护多客项目的领域模型：澄清模糊术语、统一命名、发现术语与代码事实的冲突，并在必要时记录长期架构决策。

这不是“读取术语表”。其他 skill 只是引用 `docs/glossary/CONTEXT.md` 时，不需要使用本 skill。只有当术语或决策本身要被改变时才使用。

## Authority

- 领域术语表：`docs/glossary/CONTEXT.md`
- 设计词汇：`docs/skills/design-vocabulary.md`
- 共享项目事实：`docs/skills/skill-context.md`
- ADR 目录：`docs/adr/`（按需创建）

## 何时更新术语表

命中以下情况时，先查代码和现有文档，再更新 `docs/glossary/CONTEXT.md`：

- 用户或 spec 使用的词与现有术语冲突。
- 一个词在会话、代码或文档里承载多个含义。
- 新概念会进入代码命名、接口命名、任务文档或长期 specs。
- `grilling` / `to-spec`、`examine-architecture` 或 `code-review` 需要一个稳定的领域词来命名模块、缝或需求。

不要把实现细节写入术语表。文件路径、类名、API path、字段映射、缓存策略和发布步骤应进入 task spec、API 文档、规则文档或 ADR，而不是 `CONTEXT.md`。

通用编程概念（timeout、retry、错误类型、工厂模式等）不属于术语表，即使项目大量使用--只有本项目领域独有的概念才进。添加前先问：这是本上下文独有的领域概念，还是通用编程概念？只有前者入表。

## 词条格式

每个词条写领域含义（"它是什么"），不写"它做什么"。保持一两句；同概念有多个词时挑一个作主词，其余列 `_Avoid_`：

```markdown
**访客（Visitor）** - 会话另一端的服务对象（买家/客户）。
_Avoid_: 客户、买家、用户
```

分组：术语自然成簇时用 H2 子标题（如 `## 身份与会话`）；单一内聚区域用扁平列表即可。

## 工作流

1. 读取 `docs/glossary/CONTEXT.md`、`docs/skills/skill-context.md`，以及与该术语相关的代码、任务文档或 archived spec。
2. 若用户用词和术语表冲突，立即指出冲突，并给出基于代码事实的候选解释。
3. 用具体场景检验术语边界：角色、状态、生命周期、权限、异常路径和跨模块交互。
4. 术语收敛后，直接更新 `docs/glossary/CONTEXT.md`。每个词条只写领域含义和必要区分，不写实现方案。
5. 若代码事实与用户表述冲突，优先说明冲突，不能静默选择一边。

## ADR gate

只有同时满足以下三项时，才建议创建 ADR：

- **难回滚**：未来改变会有明显迁移成本。
- **没有上下文会意外**：后续维护者会问“为什么这样做”。
- **真实取舍**：存在可行替代方案，且当前选择牺牲了某些东西。

不满足 gate 时，不写 ADR。临时任务选择写入 `docs/tasks/**`；接口协议写入 `docs/api/**`；编码规则写入 `docs/rules/**`。

## ADR 格式

创建 ADR 时使用 `docs/adr/YYYY-MM-DD-<slug>.md`。首次创建前若 `docs/adr/` 不存在则先建目录。保持最小化--多数 ADR 一段话即可，价值在于记录"做了什么决定、为什么"，不在于填满小节：

```markdown
# <Decision>

<1-3 句：背景、决定和理由>
```

仅当真正增加价值时再加可选小节：`## Status`（proposed/accepted/deprecated/superseded by ADR-NNNN，决定被重新审视时有用）、`## Considered Options`（放弃的替代值得记住时）、`## Consequences`（有非显然的下游影响时）。多数 ADR 不需要这些。`## Context` / `## Decision` 可合并成开头那段话。

完成后运行 `git diff --check`；若只改 Markdown 和术语表，不运行 Flutter build。
