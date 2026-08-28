---
name: codex-reviewer
description: 需要使用无头 Codex CLI 进行代码分析、审查、实现、验证或继续已有会话时使用。
---

# 无头 Codex CLI

使用 `codex exec` 在脚本、CI 或其他自动化流程中运行 Codex，不打开交互式 TUI。任务提示词由调用者提供；本 skill 不预设业务提示词、模型或推理力度。

## 基本调用

```bash
codex exec "<调用者提供的任务提示词>"
```

`codex exec` 默认使用只读 sandbox。需要修改工作区时显式选择最小权限：

```bash
codex exec --sandbox workspace-write "<调用者提供的任务提示词>"
```

只有受控环境确实需要时才使用 `--sandbox danger-full-access`。不要在新脚本中使用已废弃的 `--full-auto` 兼容参数。

## 输出与管道

- 普通模式将进度写入 `stderr`，最终 Agent 消息写入 `stdout`，可直接管道给其他命令。
- 需要机器读取每个事件时使用 `--json`，其 `stdout` 为 JSONL。
- 只需要最终消息时使用 `-o <path>` 或 `--output-last-message <path>` 保存。
- 不需要保存会话 rollout 文件时可使用 `--ephemeral`。

示例（提示词仍由调用者传入）：

```bash
codex exec --json "<调用者提供的任务提示词>" | jq
codex exec -o result.md "<调用者提供的任务提示词>"
```

## 继续会话

调用者提供新的提示词，继续最近一次会话：

```bash
codex exec resume --last "<调用者提供的后续提示词>"
```

也可以用会话 ID 替代 `--last`。`resume` 会沿用原会话配置，不要无依据地重新指定模型或权限。

## 运行边界

- 在受信任的 Git 仓库中运行；非仓库目录只有确认环境安全时才加 `--skip-git-repo-check`。
- 自动化中只授予完成任务所需的最小 sandbox 权限。
- 凭证通过安全环境注入，不写入提示词、脚本、日志或仓库；不要把 `~/.codex/auth.json` 提交或分享。
- 由调用者决定是否需要联网、结构化输出、验证命令和停止条件，并把这些要求写进传入的提示词。

## 故障处理

命令失败时先保留退出码和错误摘要；参数不兼容时运行 `codex --help` 或 `codex exec --help` 获取当前 CLI 的参数，不猜测版本行为。不要自动重试相同失败命令。

## 官方文档

- [Non-interactive mode](https://developers.openai.com/codex/noninteractive/)
- [Codex CLI reference](https://developers.openai.com/codex/cli/reference/)
