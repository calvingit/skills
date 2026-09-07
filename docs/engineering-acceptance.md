# 工程验收协议

本仓库将验收作为跨阶段契约：`grilling` 收敛行为与边界，`to-spec` 记录 `SPEC.md` 与 `ACCEPTANCE.md`，`to-tickets` 将需求映射为可执行场景，`loop` 消费该契约。Review 与 verify 只报告缺口，不自行发明验收条件。

## 任务产物

每个任务目录都包含带版本的 `SPEC.md` 与 `ACCEPTANCE.md`：

```yaml
protocol_version: 1
spec_snapshot: <version, date, or content fingerprint>
status: draft | confirmed | superseded
owner: to-spec
verification_owner: loop
```

`ACCEPTANCE.md` 使用以下章节：公共接口（Public Interface）、可观察行为（Observable Behavior）、成功矩阵（Success Matrix）、失败矩阵（Failure Matrix）、证据规则（Evidence Rules）、验证命令（Verification Commands）、环境前置条件（Environment Prerequisites）、未验证覆盖范围（Unverified Coverage）和变更历史（Change History）。

以下章节名称具有规范性：

```markdown
## Public Interface
## Observable Behavior
## Success Matrix
## Failure Matrix
## Evidence Rules
## Verification Commands
## Environment Prerequisites
## Unverified Coverage
## Change History
```

每个场景至少引用一个 `R` 和一个 `AC`，说明预期结果，并提供可执行证据。当前所有 `R` 与 `AC` 都必须被场景覆盖。成功、失败、取消、超时、权限和环境路径必须明确写出。`HLD.md` 负责共享技术约束；ticket 负责执行，不负责验收语义。

## 证据

验证证据记录 `source`、`command`、`exit_code`、`environment`、`expected_source`（`ACCEPTANCE.md` 中的章节）和 `unverified_reason`。Provider 原始输出只保留在任务本地，不能作为公开 CLI 输出。

## 完成门

从仓库根目录执行以下标准检查：

```bash
python3 tools/loopx/scripts/check.py all
```

缺少产物、协议版本过期、ID 未覆盖、缺少预期结果或所需命令不可执行，均属于阻塞项。真实 provider 和生产副作用除非单独执行验证，否则必须明确标记为未验证。
