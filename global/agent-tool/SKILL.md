---
name: agent-tool
description: "用户手动触发的统一 Agent CLI 封装，调用 Claude Code、Codex、Kimi、Pi 或 Grok。"
---

# Agent Tool

当用户明确要求调用某个外部 Agent、指定 provider/model 或启动独立会话时使用。

## 命令

定位 skill 目录 `$SKILL_DIR`，执行：

```bash
python3 $SKILL_DIR/scripts/agent-tool.py providers
python3 $SKILL_DIR/scripts/agent-tool.py doctor
python3 $SKILL_DIR/scripts/agent-tool.py run --provider <claude|codex|kimi|pi|grok> --workspace <path> --prompt "..."
```

可选 `--model`、`--session` 和 `--timeout`。`run` 返回 JSON，包含 `outcome`、provider、model、退出码和原始 stdout/stderr。provider 不可用、超时或非零退出必须如实报告，不能伪装成完成。

## 边界

- 只负责 provider 进程启动、参数归一化、session 传递和原始结果收集。
- 不管理任务编排、项目文件或版本控制状态。
