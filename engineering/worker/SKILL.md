---
name: worker
description: "通过统一 loopx 接口执行外部 prompt；Loop 负责 capability 编排，底层 Agent 由 runtime 路由。"
---

# Worker

使用 `loopx` 执行外部传入的 prompt。Worker 不解释任务语义；调用方决定它是实现、验证、审查还是其他工作。

## 入口

```bash
loopx worker run <workspace> --scope src/ --prompt "实现 XXX 需求，修改限于 src/"
loopx worker run <workspace> --provider pi --model glm-5.3 --prompt "审查当前代码并返回问题清单"
loopx worker run <workspace> --provider kimi --scope src/ --prompt "实现 XXX 需求，修改限于 src/"
```

底层 Agent 默认由 `loopx` 自动路由。只有用户明确指定或诊断 provider 时才使用 `--provider` override。
未指定时优先复用当前 Runtime；必要时可由 Runtime 设置 `LOOPX_RUNTIME_PROVIDER`，不需要在任务中指定具体 Agent。

## 规则

- prompt 是唯一的业务输入；implement、verify、review 及其顺序由 Loop 管理，不属于 Worker 公开接口。
- 始终不得修改 graph、`SPEC.md`、`ACCEPTANCE.md`、`HLD.md`、runtime artifact 或 sibling ticket；runtime 做事后检查，不提供进程级写入隔离，也不会自动撤销越界改动。
- 不自动 commit、push、创建分支或调度其他 worker。
- 返回统一 Worker result，包含 outcome、selected provider、model 和原始 provider payload。
- 独立 Worker 要求可完整探测的 Git workspace，默认只读；使用 `--scope <path>` 指定允许写入的范围，多范围重复传入，Runtime 会校验 protected authority、Git 和 scope。
- Loop pipeline 的 receipt contract 由 Loop 内部管理；独立 prompt Worker 返回 prompt result，不要求 ticket schema。
- provider 原始输出只保存到 task-local artifact，不进入 ticket contract。
