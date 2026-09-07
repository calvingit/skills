---
name: code-review
description: "只读审查已完成变更，按 Contract、Change-surface、Exploratory 三层检查验收契约、直接调用链和范围外风险，并输出可验证的完成门结果。"
---

# Code Review

## 目标

审查已完成的代码变更，判断它是否满足当前任务的公开契约，并保留足够的直接调用链上下文来发现只看 diff 行无法发现的回归。Review 只读，不修改代码、Git 状态、`SPEC.md`、`ACCEPTANCE.md`、HLD 或其他外部系统。

Review 有三层，职责不能互换：

```text
Review
├── Contract review       # 决定当前任务能否完成
├── Change-surface review # 覆盖变更及其直接调用链
└── Exploratory review    # 报告范围外高风险，不扩大完成门
```

Contract review 是唯一固定完成门。Exploratory review 发现的问题不能偷偷变成本轮实现要求；验收协议缺口也不能由 review agent 自行补写。

## 输入与范围

开始前必须锁定以下内容：

- `review_mode`、`review_target`、对比基准和既有改动。
- 当前 ticket 的 `R`/`AC`、`SPEC.md` 和存在时的 `ACCEPTANCE.md`。
- 目标仓库的 `AGENTS.md`、项目规范、配置、相关测试和外部边界。
- 变更文件、直接调用方、直接被调用模块、相关公开类型、测试和配置。
- 存在时的任务级 `HLD.md`、适用 D IDs、实现回执、简化回执和验证证据。

需求来源按以下顺序解析：用户明确提供的来源、当前 ticket 或执行图引用的 `SPEC.md`、已配置 issue tracker 的 issue、与分支或任务名匹配的本地 spec。没有需求来源时标记 `no_spec_available`，跳过契约实现判断，不猜测需求。

任务级 HLD 只在用户或调用方提供、或与当前 SPEC 同目录时使用，不能把仓库级架构文档误当成任务级设计。没有 HLD 时标记 `not_applicable`。

## 审查模式

- **branch / commit**：先用 `git rev-parse` 验证基准，再固定 `git diff <fixed-point>...HEAD` 和 `git log <fixed-point>..HEAD --oneline`；基准无效或 diff 为空时停止。
- **working tree**：baseline 固定为 `HEAD`，分别审查 staged、unstaged，并记录未跟踪文件；未读取的 untracked 文件不能计入覆盖范围。
- **explicit path**：只审查用户明确指定的路径，并声明没有完整提交范围的限制。
- **implementation**：使用实现流程提供的 baseline、实际范围、执行回执和验证证据，不重新猜测调用方声明的范围；无法证明覆盖完整范围时返回 `BLOCKER`。

## 执行顺序

1. 锁定模式、基准、范围、既有改动和需求来源。
2. 读取目标仓库规则、`SPEC.md` / `ACCEPTANCE.md`、HLD、配置、测试和直接调用链。
3. 按顺序完成 Contract、Change-surface、Exploratory 三层审查；环境不支持独立 reviewer 时由当前 Agent 分开执行。
4. 每条 finding 引用具体文件、行、分支、`R`/`AC`、验收章节或调用关系，并说明影响、建议和验证方式。
5. 按 [worker.md](references/worker.md)、[review-criteria.md](references/review-criteria.md) 和 [output-contract.md](references/output-contract.md) 聚合结果，不跨层合并或重新排序严重程度。

## Contract review

Contract review 只围绕当前 ticket 的完成门检查：

- 每条 in-scope `R`/`AC` 是否有可观察的通过证据。
- `ACCEPTANCE.md` 的 Public Interface、Observable Behavior、Success Matrix、Failure Matrix 和 Evidence Rules 是否被实现遵守。
- scope、权限、数据安全、错误/取消/超时语义和资源清理约束是否满足。
- 变更是否引入未经授权的公开行为或超出当前 ticket 的必需行为。

协议缺失、矛盾、无法覆盖真实高风险路径或缺少可执行证据时，进入 `acceptance_protocol_gaps`，并回流 `grilling` / `to-spec`，不能补写隐含验收条件。

## Change-surface review

Change-surface review 固定覆盖：

- 变更文件。
- 直接调用方和直接被调用模块。
- 相关公开类型、序列化 / 反序列化和配置。
- 相关测试、artifact 保存和资源生命周期路径。

只报告本次变更引入或扩大的直接链路问题。直接调用链上的正确性、安全、权限、数据损坏、进程泄漏或明显回归问题进入 `blocking_findings`。

HLD 的模块职责、依赖方向、共享类型和错误语义在此作为适用依据，但 HLD 不会单独扩大本次 review scope。

## Exploratory review

Exploratory review 可以查看相邻模块和范围外路径，用于发现高风险问题，但不改变当前 ticket 的 `R`/`AC`、`SPEC.md` 或 `ACCEPTANCE.md`。

范围外问题必须单独分类：

```json
{
  "category": "out_of_scope_risk",
  "severity": "P2",
  "evidence": "具体代码或可达路径证据",
  "recommended_route": "new-ticket"
}
```

普通范围外风险进入 `non_blocking_findings`。如果证据证明问题可达且涉及安全、数据丢失、权限越界、资源泄漏或其他高风险，则同时进入 `blocking_findings`，阻塞当前完成。

## 阻断规则

| 问题 | 当前完成门 |
| --- | --- |
| 违反当前 SPEC、AC 或验收协议 | 阻塞 |
| 安全、数据丢失、权限越界、进程/资源泄漏等高风险可达问题 | 阻塞 |
| 变更直接调用链上的正确性问题 | 阻塞 |
| 相邻但不影响本次行为的风险 | 报告并建议新 ticket |
| 纯风格、重构建议、推测性风险 | 不阻塞 |
| 验收协议缺失或矛盾 | 进入 `acceptance_protocol_gaps`，交回 `grilling` / `to-spec` |

最终完成必须满足：三层 review 均通过、`blocking_findings` 为空、`acceptance_protocol_gaps` 为空、`unverified_scope` 为空，并且所有适用的验证命令成功。

## 协议健康审查

协议健康审查不是每个 ticket 的默认重审，只在以下情况触发：新增公共 CLI、修改错误或取消语义、修改权限或 artifact 规则、发生线上事故，或多个 ticket 反复出现同类遗漏。

触发后独立输出 `protocol_health`，检查：

1. 当前实现是否违反协议。
2. 协议是否覆盖真实高风险路径。
3. 命令、字段、状态和失败语义是否互相矛盾。

协议健康问题只进入 `acceptance_protocol_gaps` 并回流 `grilling` / `to-spec`，review agent 不得直接修改协议。

## 输出与边界

最终输出固定包含：

- `blocking_findings`
- `non_blocking_findings`
- `acceptance_protocol_gaps`
- `unverified_scope`

每条 finding 至少包含 `category`、`severity`、`evidence` 和 `recommended_route`，并保留位置、影响、建议和验证方式。没有发现时仍保留空章节或空数组。

这是只读审查。根因定位转交 `debug`，全仓架构诊断转交 `review-architecture`，测试或构建失败交由 `verify` / `debug` 处理；review 可以提出提交建议，但不能 commit、push、修改分支、修改验收协议或扩大当前 ticket 的完成门。
