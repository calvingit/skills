---
name: agent-tool
description: "用户手动触发的统一 Agent CLI 封装，调用 Claude Code、Codex、Kimi、Pi 或 Grok，并观察外部 CLI 进程。"
---

# Agent Tool

当用户明确要求调用某个外部 Agent、指定 provider/model 或启动独立会话时使用。

## 命令

定位 skill 目录 `$SKILL_DIR`，执行：

```bash
python3 $SKILL_DIR/scripts/agent-tool.py clis
python3 $SKILL_DIR/scripts/agent-tool.py doctor
python3 $SKILL_DIR/scripts/agent-tool.py models --cli pi --provider dianxiaomi
python3 $SKILL_DIR/scripts/agent-tool.py run --cli pi --provider dianxiaomi --model kimi-k3 --workspace <path> --prompt "..."
python3 $SKILL_DIR/scripts/agent-tool.py run --cli <claude|codex|kimi|pi|grok> --prompt "..." --events
```

`--cli` 指本地 Agent 命令，`--provider` 指模型供应商，`--model` 指精确模型名称。执行前会通过 CLI 的模型列表校验显式指定的 provider/model；当前支持 Pi、Kimi 和 Grok 的模型发现。另有可选参数 `--session`、`--timeout`、`--idle-timeout`、`--heartbeat-interval` 和 `--events`。

- `--idle-timeout` 是无活动超时，默认 600 秒。从启动开始计时，每次实际读到 provider 的 stdout 或 stderr 字节，都重新计时；连续 600 秒没有输出则终止进程。这是静默容忍策略，不代表已经判定模型卡死。
- 总运行时间默认不限；只有显式设置 `--timeout`，才按指定秒数限制总执行时间。输出不会延长这个上限。
- `--heartbeat-interval` 默认 30 秒，只控制封装脚本的观察事件频率。脚本自产心跳不会重置无活动计时，也不会重置总执行预算。

例如，第 599 秒收到 provider 输出，无活动截止时间延到第 1199 秒；期间只有封装脚本的心跳时，截止时间不变。当前没有统一的 provider 主动探测接口，因此只以实际输出字节续期。

默认 `run` 在 CLI 结束后返回一份 JSON，包含 `outcome`、cli、provider、model、退出码、原始 stdout/stderr 和进程观察摘要。`--events` 显式启用实时 NDJSON：先输出启动、CLI 输出和心跳事件，最后输出同样的结果 JSON，便于调用方在长任务期间确认进程仍可观察。心跳的 `process-observation` 语义只证明进程状态和传输活动，不证明模型正在有效推进；没有输出不能判定卡死。

CLI-specific 的运行中消息注入不属于统一契约。脚本不向所有 CLI 假设存在通用 ping/pong，也不把 `--session` 误解为当前进程内的双向通道。需要恢复或继续会话时，由调用方按 CLI 的实际能力重新调用。

无活动超时或显式设置的总执行预算耗尽时，会先停止 CLI 进程组并保留部分 stdout/stderr，结果标记为 `interrupted`，原因分别为 `provider idle timeout` 和 `provider timeout`；非零退出标记为 `failed`。不因为一次观察间隔没有输出而提前终止，也不启动重叠 CLI。

## 边界

- 只负责 CLI 进程启动、参数归一化、模型选择校验、session 传递、进程观察和原始结果收集。
- 心跳只记录进程级事实，不管理 ticket、`.loop/`、项目文件、版本控制、重试编排或验收结论。
- 不管理任务编排、项目文件或版本控制状态。
