# 工作流状态脚本

原 `tools/loopx` 已拆入 skill，不再需要安装全局 CLI。脚本仅处理执行图、状态和交付快照；决策由 Skill 所在的 Agent 作出，Agent 调度由当前 Runtime 提供。

| 目录 | 职责 |
| --- | --- |
| `engineering/to-tickets/scripts/` | 创建、校验及按上游变更协调执行图 |
| `engineering/loop/scripts/` | 查询可执行任务、记录 attempt、状态流转和最终交付快照 |
| `engineering/shared/` | 唯一 ticket schema、图校验、文件锁、事务与恢复 |

使用 Python 3.10+，当前文件锁实现支持 macOS/Linux。没有第三方 Python 包、Codex 或 Claude Code 依赖；最终代码快照检查需要 Git。安装或复制相关 skill 时须保留兄弟目录 `shared/`，仅复制单个 SKILL.md 不足以运行脚本。脚本通过自身位置加载共享代码，调用时不要求当前目录位于 Skills 仓库。

从本仓库根目录调用的例子：

```bash
python3 engineering/to-tickets/scripts/create-graph create-batch /path/to/task --input /path/to/request.json
python3 engineering/to-tickets/scripts/validate-graph /path/to/task
python3 engineering/loop/scripts/frontier /path/to/task
python3 engineering/loop/scripts/record-attempt start /path/to/task T001 --input /path/to/start.json
python3 engineering/loop/scripts/update-status complete /path/to/task T001 --input /path/to/complete.json
```

输入定义见 [建图与协调](../engineering/to-tickets/references/script-inputs.md)、[执行状态](../engineering/loop/references/script-inputs.md)。原 `graph create-batch/reconcile-batch` 对应 `create-graph`；原 `frontier` 对应 `frontier`；原 `graph start/retry` 对应 `record-attempt`；其余状态和最终交付记录使用 `update-status`。

`.loop/` 仍位于任务目录，与 `SPEC.md`、`tickets/` 同级。现有图锁和临时事务目录也按任务隔离。脚本不建立项目级共享运行状态。

## 验证

```bash
python3 engineering/shared/check.py
```

检查图依赖、状态流转、需求修订、证据、事务恢复以及脱离仓库目录的脚本调用。不会模拟或承诺原生 Runtime 的后台持续运行能力。
