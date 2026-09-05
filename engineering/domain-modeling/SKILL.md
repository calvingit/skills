---
name: domain-modeling
description: "用于统一领域术语，并按需记录长期架构决策。"
---

# Domain Modeling

主动维护目标项目的领域模型：澄清模糊术语、统一命名、发现术语与代码事实的冲突，并在必要时记录长期架构决策。

这不是“读取术语表”。其他 skill 只是消费已有领域文档时，不需要使用本 skill；只有当术语或决策本身需要被改变时才使用。

## Discover authorities

不要假定固定目录或文件名。按以下顺序发现项目权威来源：

1. 用户明确指定的术语表、架构决策或项目文档。
2. 仓库级 Agent 指令、README、CONTRIBUTING、架构文档等声明的位置。
3. 已存在的 glossary、CONTEXT、domain model、ADR/decision record 结构。
4. 当前代码、公开 contract、调用链和测试所证明的事实。

适用 `AGENTS.md` 的 `Engineering Skills Profile` 指定 glossary 或 ADR 入口时优先使用；值为 `auto` 或没有 Profile 时继续按上述顺序发现，不自动运行 setup。

若项目没有术语表或 ADR 约定，不擅自引入固定 `docs/**` 目录。确实需要新增长期文档时，优先沿用仓库已有结构；仍无约定且位置会影响后续使用时，只询问一次写入位置。可采用的默认格式见 [CONTEXT-FORMAT.md](CONTEXT-FORMAT.md) 与 [ADR-FORMAT.md](ADR-FORMAT.md)，但项目已有格式始终优先。

## 何时更新术语表

命中以下情况时，先查代码和现有文档，再更新项目已有的领域词汇来源：

- 用户或 spec 使用的词与现有术语冲突。
- 一个词在会话、代码或文档里承载多个含义。
- 新概念会进入代码命名、接口命名、任务文档或长期 specs。
- `grilling`、`to-spec`、`review-architecture` 或 `code-review` 需要稳定的领域词来描述 Module、Seam 或需求。

不要把实现细节写进领域术语表。文件路径、类名、API path、字段映射、缓存策略和发布步骤应进入 task spec、API 文档、规则文档或 ADR，而不是领域词汇。

通用编程概念（timeout、retry、错误类型、工厂模式等）通常不属于领域词汇。添加前先问：这是当前业务上下文独有的概念，还是通用工程概念？只有前者进入领域模型。

## 词条格式

每个词条写领域含义（“它是什么”），不写实现动作。保持一两句；同概念有多个词时挑一个作主词，其余作为应避免或兼容别名记录。沿用项目已有格式；没有既有格式时可使用：

```markdown
**Visitor** - 会话另一端的服务对象。
_Avoid_: Customer, Buyer, User
```

## 工作流

1. 发现并读取当前项目的领域文档、相关代码、任务文档和历史决策。
2. 若用户用词和现有术语冲突，立即指出冲突，并给出基于当前事实的候选解释。
3. 用具体场景检验术语边界：角色、状态、生命周期、权限、异常路径和跨模块交互。
4. 术语在当前 round 中收敛后立即更新项目已采用的领域词汇来源，不等整个会话结束；没有明确写入位置时不要猜路径。
5. 若代码事实、文档和用户表述冲突，明确列出冲突和证据，不静默选择一边。

## ADR gate

只有同时满足以下三项时，才建议记录长期架构决策：

- **难回滚**：未来改变会有明显迁移成本。
- **没有上下文会意外**：后续维护者很可能会问“为什么这样做”。
- **真实取舍**：存在可行替代方案，且当前选择牺牲了某些东西。

不满足 gate 时，不创建 ADR。临时任务选择属于 task/spec；接口协议属于 API/contract 文档；编码规则属于项目 coding standards。

## ADR 内容

沿用项目已有 ADR/decision record 格式。没有既有格式时保持最小化，至少记录：

```markdown
# <Decision>

<背景、决定和理由；通常 1-3 段即可>
```

只有真正增加价值时再记录 status、considered options、consequences 等信息。价值在于“做了什么决定、为什么”，不在于固定模板。

与 `grilling` 组合时，本 Skill 不拥有 Design Tree、frontier、round 或提问节奏。它只发现需要澄清或记录的领域问题，把问题交给 `grilling` 进入同一 frontier，并在用户确认后负责落盘：默认写入 `grilling` 的会话文档目录；用户要求写入项目时，按 `grilling` 的 Profile 规则确定位置。

## 验证

完成后只运行与本次文档修改相关、且目标仓库已有的轻量验证，例如 Markdown/lint/link check 或 `git diff --check`。不存在对应工具时不创建新的技术栈特定检查。
