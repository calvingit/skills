# 工程验收协议

本仓库将验收作为按任务复杂度选择的契约：`grilling` 收敛行为与边界，`to-spec` 需要持久化时记录 `SPEC.md`，独立 `ACCEPTANCE.md` 只在有明确复用或协议需求时创建，`to-tickets` 将协作任务映射为可执行工作，`loop` 消费已有 ticket 契约。Review 与 verify 只报告缺口，不自行发明验收条件。

## 任务产物

任务至少有已确认的目标和 Acceptance Criteria；只有需要独立版本、跨 ticket 复用场景或复杂 CLI/权限矩阵时才创建 `ACCEPTANCE.md`。它可以包含机器可读区块，但这不是默认要求。任务明确启用机器可读协议时再声明格式、场景和命令；普通任务不需要这些字段。

`ACCEPTANCE.md` 使用以下最小章节：`Public Interface`、`Observable Behavior`、`Acceptance Criteria / Scenarios`、`Failure and Environment Notes`、`Evidence Rules`、`Unverified Coverage` 和 `Change History`。CLI 自动执行确有需要时，才额外增加机器可读字段和验证命令。

独立协议建议使用以下章节名称：

```markdown
## Public Interface
## Observable Behavior
## Acceptance Criteria / Scenarios
## Failure and Environment Notes
## Evidence Rules
## Unverified Coverage
## Change History
```

独立协议中的场景应引用相关 `R`/`AC`，说明预期结果，并提供可复核证据。成功、失败、取消、超时、权限和环境路径按任务风险明确写出。`HLD.md` 负责共享技术约束；ticket 负责执行，不负责验收语义。

## 证据

验证证据由 verify 记录实际命令、退出码、摘要和未验证范围；Loop 不重复执行命令。Provider 原始输出只保留在任务本地，不能作为公开 CLI 输出。

## 完成门

loopx 工具自身的标准检查从仓库根目录执行：

```bash
python3 tools/loopx/scripts/check.py all
```

缺少任务已声明的必需产物、ticket/receipt 结构无效、必要证据缺失或边界违反，属于阻塞项。普通任务不因没有独立协议、场景映射或机器可读命令而阻塞。真实 provider 和生产副作用除非单独执行验证，否则必须明确标记为未验证。

正式版 schema 尚未发布，不提供旧 graph 迁移路径；任务变更直接使用当前契约重新创建 graph。任务完成由实际验证证据和适用审查决定。

无 graph 的任务由 `quick-implement` 执行项目已有验证并按风险审查；不要求 Loop 专有产物。
